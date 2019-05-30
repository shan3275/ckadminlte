#!/usr/bin/python
#coding:utf-8

import socket
import sys
import time
import thread
import time
import struct
import inits
import globalvar as gl
import libdb as libdb
import libredis as libredis

global logger
global CONF

TaskList=list()

def getUserTaskList(user):
    """
    获取未提交任务的详情列表
    :param user:
    :return:
    """
    task_list=list()
    crack = libredis.LibRedis(user)
    task_num = crack.setCard(CONF['redis']['task'])
    if task_num == 0:
        logger.info('user:%d, task_num:%d', user,task_num)
        return task_list
    task_set = crack.setSmembers(CONF['redis']['task'])
    for task in task_set:
        logger.info(task)
        task_dict = crack.hashGetAll(task)
        if task_dict != None:
            logger.info(task_dict)
            if task_dict['submit'] == '1':
                continue
            logger.info('task 没有被提交，故添加到队列中')
            task_list.append(task_dict)
        else:
            logger.error('异常，在redis中找不到表项')

    return task_list

def strToTimestamp(str):
    """
    将字符串时间转换为时间戳
    :param str:  "2016-05-05 20:28:00"
    :return:
    """
    # 转换成时间数组
    timeArray = time.strptime(str, "%Y-%m-%d %H:%M:%S")
    # 转换成时间戳
    timestamp = int(time.mktime(timeArray))
    return timestamp

def bubble_sort(lists):
    """
    冒泡排序,将任务按照时间进行排序，时间靠前，排在后面
    :param lists:
    :return:
    """
    count = len(lists)
    for i in range(0, count):
        timestamp_i = strToTimestamp(lists[i]['begin_time'])
        for j in range(i + 1, count):
            timestamp_j = strToTimestamp(lists[j]['begin_time'])
            if timestamp_i < timestamp_j:
                lists[i], lists[j] = lists[j], lists[i]
    return lists

def loop_th():
    """
    轮询任务，对任务进行排序
    :return:
    """
    #将每个DB的任务取出，获取任务详情
    task_list = list()
    for user in range(0,16):
        user_task_list = getUserTaskList(user)
        task_list = task_list + user_task_list

    logger.info(task_list)

    #未执行任务进行排序
    task_sorted_list = bubble_sort(task_list)
    logger.info(task_sorted_list)
    global TaskList
    if cmp(task_sorted_list,TaskList) != 0:
        logger.info('同步任务队列')
        TaskList = task_sorted_list
        logger.info(TaskList)
    else:
        logger.info('任务队列不需要同步')


def getOneTask():
    ou = dict(error=0,msg='ok',data=dict())

    #任务存储在DB15中，故获取
    crack = libredis.LibRedis(15)
    if crack.zCard(CONF['redis']['begintask']) == 0:
        ou['error'] = 1
        ou['msg']   = 'no task'
        return ou

    #对比时间，如果时间不在范围内，不能提交
    timestamp = int(time.time())
    if crack.zCount(CONF['redis']['begintask'],timestamp-3600*5, timestamp) == 0:
        ou['error'] = 1
        ou['msg']   = 'no task'
        return ou

    if crack.zCount(CONF['redis']['endtask'],timestamp, timestamp+3600*5) == 0:
        ou['error'] = 1
        ou['msg']   = 'no task'
        return ou

    task_list_begin = crack.zRangeByScore(CONF['redis']['begintask'], timestamp-3600, timestamp)
    task_list_end   = crack.zRangeByScore(CONF['redis']['endtask'],   timestamp,      timestamp+3600)
    task_list       = list(set(task_list_begin).intersection(set(task_list_end)))
    if  len(task_list) == 0:
        ou['error'] = 1
        ou['msg']   = 'no task'
        return ou

    for task in task_list:
        task_dict = crack.hashGetAll(task)
        if task_dict == None:
            logger.error('异常，在redis中找不到表项')
            ou['error'] = 1
            ou['msg'] = 'no task'
            return ou
        #logger.info(task_dict)
        effective = int(task_dict['effective'])
        if effective == 0:
            task_dict = None
            continue
        req = int(task_dict['req'])
        user_num = int(task_dict['user_num'])
        if req >= user_num:
            task_dict = None
            continue
        else:
            time_gap = int(task_dict['time_gap'])
            gap_num  = int(task_dict['gap_num'])
            begin_timestamp = int(task_dict['begin_timestamp'])
            index = (timestamp - begin_timestamp) / time_gap
            gap_num_max = user_num / gap_num * (index+1)
            logger.debug('time_gap:%d,gap_num:%d,index:%d,gap_num_max:%d,req:%d', time_gap,gap_num,index,gap_num_max,req)
            if req >= gap_num_max:
                task_dict = None
                continue
            else:
                break

    if task_dict != None :
        logger.info('当前task 满足时间条件，可以提交')
        ou['error'] = 0
        ou['msg']   = 'ok'
        ou['data']  = task_dict
    else:
        logger.info('当前task 不满足时间条件，不可以提交')
        logger.info('当前task 放回队列')
        TaskList.append(task)
        ou['error'] = 1
        ou['msg']   = 'no task'
    return ou

def updateTaskStatus(task):
    crack = libredis.LibRedis(15)
    task_id = task['task_id']
    crack.hashincr(task_id,'req')

def now():
    return time.strftime("%m-%d %H:%M:%S", time.localtime())

def gstat_clear(userId):
    stat = dict()
    stat['pos'] = 0
    stat['asigned'] = 0
    stat['req'] = 0
    stat['rereq'] = 0
    stat['none'] = 0
    stat['reset_ts'] = now()
    crack = libredis.LibRedis(userId)
    crack.hashMSet('g_stat', stat)

def reset_records(userId):
    CNT = 0
    gstat_clear(userId)
    crack = libredis.LibRedis(userId)
    while crack.setCard(CONF['redis']['user']) > 0:
        ip = crack.setSpop(CONF['redis']['user'])
        if ip != None:
            lens = crack.hashHlen(ip)
            if lens == 0:
                continue
            record = crack.hashGetAll(ip)
            CNT += 1
            rv = crack.hashDel(ip, *record.keys())
            logger.info('reset user(%s) hash rv(%d)', ip,rv)

    #将cknnsetconst 复制一份，作为获取ck时的中间变量。
    if CONF['random'] == True:
        rv = crack.setSunionstore(CONF['redis']['live'], CONF['redis']['const'])
        if rv == 0:
            logger.info('copy ck nickname set fail')
    else:
        num = crack.delete(CONF['redis']['live'])
        logger.info('redis delete(%d) live list num=%d', userId, num)

        const = crack.listLRange(CONF['redis']['const'],0,-1)
        if len(const) == 0:
            logger.error('redist const list is null')
            logger.info("%d records reset.", CNT)
            return CNT
        rv = crack.listRPush(CONF['redis']['live'], *const)
        if rv <= 0:
            logger.error('write ck nickname to redis(%d) live list fail!!',userId)
        else:
            logger.info('write ck nickname to redis(%d) live list success, %d', userId,rv)

    logger.info("%d records reset." ,CNT)
    return CNT

def resetTaskCK():
    ou = dict(error=0,msg='ok',data=dict())

    #任务存储在DB15中，故获取
    crack = libredis.LibRedis(15)
    if crack.zCard(CONF['redis']['begintask']) == 0:
        ou['error'] = 1
        ou['msg']   = 'no task'
        return ou

    #对比时间，如果时间不在范围内，不能提交
    timestamp = int(time.time())
    if crack.zCount(CONF['redis']['begintask'],timestamp-60*3, timestamp+60*3) == 0:
        ou['error'] = 1
        ou['msg']   = 'no task'
        return ou

    task_list = crack.zRangeByScore(CONF['redis']['begintask'], timestamp-60*3, timestamp+60*3)
    if  len(task_list) == 0:
        ou['error'] = 1
        ou['msg']   = 'no task'
        return ou

    for task in task_list:
        task_dict = crack.hashGetAll(task)
        if task_dict == None:
            logger.error('异常，在redis中找不到表项')
            ou['error'] = 1
            ou['msg'] = 'no task'
            return ou
        #logger.info(task_dict)
        effective = int(task_dict['effective'])
        if effective == 0:
            continue
        reset_done = int(task_dict['reset_done'])
        if reset_done == 1:
            continue

        ## effective == 1 and reset_done == 0, 下面继续执行，准备复位ck
        begin_timestamp = int(task_dict['begin_timestamp'])
        if begin_timestamp >= timestamp - 120 and begin_timestamp <= timestamp + 120:
            ##自动重置ck
            userId = int(task_dict['user_id'])
            stat = libredis.LibRedis(userId).hashGetAll('g_stat')
            asigned = int(stat['asigned'])
            total   = int(stat['total'])
            request_num = int(task_dict['user_num'])
            logger.info('asigned:%d,total:%d,request_num:%d', asigned, total, request_num)
            task_id = task_dict['task_id']
            if (total-asigned) < (request_num*0.7):
                reset_records(userId)
                ##更新标志位
            else:
                logger.info('%s no need to reset ck',task_id)
            crack.hashset(task_id, 'reset_done', 1)
            logger.info('%s set reset_done to 1', task_id)


def writeTasktoDB(task):
    """
    将task写入数据库
    :param task: 任务字典
    :return:
    """
    key = "user_id, task_id, effective, reset_done, submit_time, begin_timestamp,total_time,"\
          "last_time_from,last_time_to,time_gap,gap_num,user_num,req,ck_req,"\
          "ck_url,room_url,content"
    value = "'%s', '%s', '%s', '%s', '%s', '%s', '%s',"\
            "'%s', '%s', '%s', '%s', '%s', '%s', '%s',"\
            "'%s', '%s', '%s'" \
            % (task['user_id'],       task['task_id'],        task['effective'],    task['reset_done'], \
               task['submit_time'],   task['begin_timestamp'],task['total_time'],                       \
               task['last_time_from'],task['last_time_to'],   task['time_gap'],     task['gap_num'],    \
               task['user_num'],      task['req'],            task['ck_req'],                           \
               task['ck_url'],        task['room_url'],       task['content'])
    logger.debug('key:%s, value:%s', key, value)
    rv = libdb.LibDB().insert_db(key, value, CONF['database']['tasktb'])

def moveTaskFromRedistoDB():
    """
    将redis中的超过24小时的任务移动到mysql中
    :return:
    """
    #任务存储在DB15中，故获取
    start = 0
    end   = int(time.time()-3600*24)

    crack = libredis.LibRedis(15)
    task_num = crack.zCount(CONF['redis']['begintask'], start, end)
    logger.info('task_num=%d', task_num)
    if task_num == 0:
        logger.info('24小时之前任务数量为空')
        return

    tasks = crack.zRangeByScore(CONF['redis']['begintask'], start, end)
    if len(tasks) == 0:
        logger.info('24小时之前任务列表为空')
        return

    ##删除任务从集合中
    begin_task_num = crack.zRmRangeByScore(CONF['redis']['begintask'], start, end)
    logger.info('删除任务从集合，begin_task_num=%d', begin_task_num)
    if task_num != begin_task_num:
        logger.error('task_num != begin_task_num,异常，需要关注')

    end_task_num = crack.zRmRangeByScore(CONF['redis']['endtask'], start, end)
    logger.info('删除任务从集合，end_task_num=%d', end_task_num)
    if task_num != end_task_num:
        logger.error('task_num != end_task_num,异常，需要关注')

    ##将任务从redis复制到数据库中
    for task in tasks:
        task_dict = crack.hashGetAll(task)
        if task_dict == None:
            logger.error('异常，在redis中找不到表项')
            continue
        ##将表项写入Db中
        rv = writeTasktoDB(task_dict)
        if rv == False:
            logger.error('write task to DB Fail!')
        rv = crack.hashDel(task, *task_dict.keys())
        logger.info('clear task(%s) rv(%d)', task, rv)



logger = gl.get_logger()
CONF = gl.get_conf()
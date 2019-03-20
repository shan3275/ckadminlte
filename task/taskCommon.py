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
        logger.info(task_dict)
        req = int(task_dict['req'])
        user_num = int(task_dict['user_num'])
        if req >= user_num:
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

logger = gl.get_logger()
CONF = gl.get_conf()
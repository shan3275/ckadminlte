#!/usr/bin/python
#-*- coding: UTF-8 -*-
# FileName : libcommon.py
# Author   : Shan
# DateTime : 2019/3/13
# SoftWare : PyCharm
import os,json
from werkzeug.utils import secure_filename
import libdb as libdb
import libredis as libredis
import chardet
import urllib
import time,datetime
import globalvar as gl

global logger
global CONF

def now():
    return time.strftime("%m-%d %H:%M:%S", time.localtime())

def cookieWriteToDB(nickname, pwd, cookie, grp):
    key = "nickname, password, grp, regdate, lastdate, colddate, cookie"
    value = "'%s', '%s', '%s', '%d', '%d', '%d', '%s'" % (nickname, pwd, grp, \
                                                    int(time.time()), int(time.time()), \
                                                    int(time.time()), cookie)
    logger.debug('key:%s, value:%s', key, value)
    rv = libdb.LibDB().insert_db(key, value, CONF['database']['table'])
    return rv

def updateFailWriteToDB(nickname, update_fail):
    if update_fail == 'update_fail':
        setval = "update_fail=update_fail+1"
    else:
        return False
    condition = "nickname='%s'" %(nickname)
    logger.debug('setval:%s, condition:%s', setval, condition)
    rv = libdb.LibDB().update_db(setval, condition, CONF['database']['table'])
    return rv

def cookieUpdateToDB(nickname, pwd, cookie):
    setval = "password='%s',lastdate='%d',cookie='%s',update_fail=0" %(pwd, int(time.time()), cookie)
    condition = "nickname='%s'" %(nickname)
    logger.debug('setval:%s, condition:%s', setval, condition)
    rv = libdb.LibDB().update_db(setval, condition, CONF['database']['table'])
    return rv

def updateColdDateToDB(nickname,timestamp):
    """
    设置冷却时间
    :param nickname: 用户名
    :param timestamp: 时间戳，10位
    :return:
    """
    setval = "colddate=%d" %(timestamp)
    condition = "nickname='%s'" %(nickname)
    logger.debug('setval:%s, condition:%s', setval, condition)
    rv = libdb.LibDB().update_db(setval, condition, CONF['database']['table'])
    return rv

def cookie_csv_parse_for_db(line):
    row = line.split(',')
    if len(row) < 3:
        return None

    if row[0] == "" or row[0] == "名称":
        return None

    # 名称,密码,Cookies
    record  = {}
    record['nickname']    = row[0]
    record['password']    = row[1]
    record['cookie']      = row[2]
    return record

def cookie_load_for_db(path):
    FILE = open(path, 'rb')
    records =[]
    seq = 0
    for line in FILE:
        if '\xef\xbb\xbf' in line:
            logger.info('用replace替换掉\\xef\\xbb\\xb')
            line = line.replace('\xef\xbb\xbf', '')  # 用replace替换掉'\xef\xbb\xbf'
        line = line.strip('\n')
        cdet = chardet.detect(line)
        if cdet['encoding'] == None:
            logger.info(cdet)
            continue
        if cdet['encoding'].lower().find("utf-8") == 0 :
            u8str = line
        else:
            u8str = line.decode('GBK').encode("utf8")
        record = cookie_csv_parse_for_db(u8str)
        if record == None:
            continue

        record['seq'] = seq
        records.append(record)
        seq += 1
    logger.debug("%d cookies loaded from %s!" ,len(records), path)
    return records

def writeFileToDB(file, group='G0'):
    """
    将cooikes csv文件写入数据库
    :param file: cookie文件描述符
    :return:   ou  ：字典，包含信息
               ou['data']['num']  :成功数量
               ou['msg']            :信息
               ou['error']           : 0 ok
                                      : 1 写数据库失败
    """
    ou = dict(error=0, data=dict(), msg='ok')
    basepath = os.path.dirname(__file__)  # 当前文件所在路径
    upload_path = os.path.join(basepath, 'uploads', secure_filename(file.filename))  # 注意：没有的文件夹一定要先创建，不然会提示没有该路径
    file.save(upload_path)

    # 读取文件
    logger.debug("upload_path: %s", upload_path)
    records = cookie_load_for_db(upload_path)
    logger.debug(records)
    ou['data']['num'] = len(records)

    #写入数据库
    for record in records:
        sql = libdb.LibDB().query_one('nickname', record['nickname'], CONF['database']['table'])
        if sql == False:
            ou['error'] = 1
            ou['msg']   = '读数据库失败'
            continue
        if sql == None:
            rv = cookieWriteToDB(record['nickname'], record['password'], record['cookie'], group)
            if rv != True:
                ou['error'] = 1
                ou['msg']   = '写数据库失败'
                continue
        else:
            rv = cookieUpdateToDB(record['nickname'], record['password'], record['cookie'])
            if rv != True:
                ou['error'] = 1
                ou['msg']   = '更新数据库失败'
                continue
    return ou

def cookie_append(records):
    rcs = list()
    for record in records:
        t = dict()
        t['id']       = record[0]
        t['seq']      = records[0]
        t['nickname'] = record[2]
        t['password'] = record[3]
        t['regtime']  = datetime.datetime.fromtimestamp(record[4])
        t['uptime']   = datetime.datetime.fromtimestamp(record[5])
        t['cookie']   = record[9]
        rcs.append(t)

    return rcs

def takeOutCksFromDB(cks_num):
    #先取出DB中表项数目
    condition = 'lastdate>%d' %(int(time.time()-3600*24*6))
    count = libdb.LibDB().query_count_by_condition(condition, CONF['database']['table'])
    if count != False:
        total = count[0]
    else:
        total = 0
    logger.debug(type(cks_num))
    cks_num = int(cks_num)
    if total >= cks_num:
        take_num = cks_num
    else:
        take_num = total

    logger.debug('准备从数据库取出cookies数量：%d', take_num)
    records = libdb.LibDB().query_num_by_condition(take_num,condition, CONF['database']['table'])
    return records

def takeOutCksByIndexFromDB(index, num):
    """
    按照索引从DB中取出cookies
    :param index:
    :param num:
    :return:
    """
    key = 'id'
    info = libdb.LibDB().min_key(key, CONF['database']['table'])
    if info != False:
        min = info[0]
    else:
        return False

    info = libdb.LibDB().max_key(key, CONF['database']['table'])
    if info != False:
        max = info[0]
    else:
        return False

    begin_id = min + index
    if begin_id > max:
        return False

    begin_end = begin_id + num - 1
    condition = key + ' between %d and %d' %(begin_id, begin_end)
    logger.info(condition)
    records = libdb.LibDB().query_by_condition(condition, CONF['database']['table'])
    if records == False:
        return False
    return records

def takeOutCksByTimeStampRange(timestampBegin, timestampEnd):
    """
    :param timeStampStart:
    :param timeStampEnd:
    :return:
    """
    condition = 'lastdate >= %d and lastdate <= %d and update_fail <= 5' % (timestampBegin, timestampEnd)
    logger.info(condition)
    records = libdb.LibDB().query_by_condition(condition, CONF['database']['table'])
    if records == False:
        return False
    return records



def writeRecordsToRedis(records, userId):

    if records == None or len(records) == 0:
        return

    # 写入数据库
    if len(records) ==0:
        return
    crack = libredis.LibRedis(userId)
    for record in records:
        # cookie写入redis
        rv = crack.hashMSet(record['nickname'], record)
        if rv != True:
            logger.info('write to redis fail %s', record)
        ##写入集合和写入列表二选一
        if CONF['random'] == True:
            # ck名称集合，写入redis，集合为无序集合
            rv = crack.setAdd(CONF['redis']['const'], record['nickname'])
            if rv != True:
                logger.info('repeat,write ck nickanme set to redis fail')
        else:
            #ck名称列表，写入redis，列表元素可以重复
            rv = crack.listLPush(CONF['redis']['const'], record['nickname'])
            if rv <= 0:
                logger.error('write ck nickname to redis const list fail!!')

    if CONF['random'] != True:
        logger.info('write ck nickname to redis const list success')


    # 将cknnsetconst 复制一份，作为获取ck时的中间变量。
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
        rv = crack.listRPush(CONF['redis']['live'], *const)
        if rv <= 0:
            logger.error('write ck nickname to redis(%d) live list fail!!',userId)
        else:
            logger.info('write ck nickname to redis(%d) live list success, %d', userId,rv)

    # 更新g_stat total  变量
    if CONF['random'] == True:
        Digit = crack.setCard(CONF['redis']['const'])
    else:
        Digit = crack.listLLen(CONF['redis']['const'])
    crack.hashSet('g_stat', 'total', Digit)
    logger.info('更新 redis g_stat total success!')

def takeOutCksFromDBToRedis(index, num, userId):
    records = takeOutCksByIndexFromDB(index, num)
    if records == False:
        return False

    #logger.info(records)
    rcs = list()
    seq = 0
    timestr = time.strftime('%Y%m%d%H%M%S')
    for record in records:
        t = dict()
        t['id']       = record[0]
        t['seq']      = seq
        seqstr = "%06d" % seq
        t['nickname'] = record[2] + timestr + seqstr
        t['password'] = record[3]
        t['regtime']  = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(record[4])))
        t['uptime']   = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(record[5])))
        t['cookie']   = record[9]
        rcs.append(t)
        #logger.info(t)

    writeRecordsToRedis(rcs, userId)

    return True

def cookie_csv_parse_for_redis(line):
    row = line.split(',')
    if len(row) < 3:
        return None

    if row[0] == "" or row[0] == "ID":
        return None

    # 名称,密码,Cookies
    record  = {}
    record['id']          = row[0]
    record['nickname']    = row[1]
    record['password']    = row[2]
    record['cookie']      = row[7]
    record['uptime']      = row[8]
    record['regtime']     = row[9]
    return record

def cookie_txt_parse_for_redis(line):
    if line == '':
        return None
    aa = line.split('acf_nickname=')
    if len(aa) == 1:
        nickname = 'nickname'
    else:
        bb = aa[1].split(';', 1)
        cc = bb[0].encode('utf8')
        nickname = urllib.unquote(cc)
    # 名称,密码,Cookies
    record  = {}
    record['id']          = 0
    record['nickname']    = nickname
    record['password']    = 'password'
    record['cookie']      = line
    return record

def cookie_load_for_redis(path):
    FILE = open(path, 'r')
    records =[]
    seq = 0
    timestr = time.strftime('%Y%m%d%H%M%S')
    for line in FILE:
        if '\xef\xbb\xbf' in line:
            logger.info('用replace替换掉\\xef\\xbb\\xb')
            line = line.replace('\xef\xbb\xbf', '')  # 用replace替换掉'\xef\xbb\xbf'
        line = line.strip('\n')
        cdet = chardet.detect(line)
        if cdet['encoding'].lower().find("utf-8") == 0 :
            u8str = line
        else:
            u8str = line.decode('GBK').encode("utf8")
        #record = cookie_csv_parse_for_redis(u8str)
        record = cookie_txt_parse_for_redis(u8str)
        if record == None:
            continue

        record['seq'] = seq
        seqstr = "%06d" % seq
        record['nickname'] = record['nickname'] + timestr + seqstr
        records.append(record)
        seq += 1
    logger.debug("%d cookies loaded from %s!" ,len(records), path)
    return records




def writeFileToRedis(file,userId):
    """
    将cooikes csv文件写入数据库
    :param file: cookie文件描述符
    :return:   ou  ：字典，包含信息
               ou['data']['num']  :成功数量
               ou['msg']                :信息
               ou['error']              : 0 ok
                                        : 1 写数据库失败
    """
    basepath = os.path.dirname(__file__)  # 当前文件所在路径
    upload_path = os.path.join(basepath, 'uploads', secure_filename(file.filename))  # 注意：没有的文件夹一定要先创建，不然会提示没有该路径
    file.save(upload_path)

    # 读取文件
    logger.debug("upload_path: %s", upload_path)
    records = cookie_load_for_redis(upload_path)
    logger.debug('cookie num:%d', len(records))

    writeRecordsToRedis(records, userId)
    return True

def fetch_record_from_redis(ip, userId):
    crack = libredis.LibRedis(userId)
    if CONF['random'] == True:
        num = crack.setCard(CONF['redis']['live'])
        if num == 0:
            logger.info('cookie has used over, fecth record fail,userid:%d',userId)
            return None

        nickname = crack.setSpop(CONF['redis']['live'])
        if nickname == None:
            logger.error('fetch record get nickname null!!')
            return None
    else:
        num = crack.listLLen(CONF['redis']['live'])
        if num == 0:
            logger.info('cookie has used over, fecth record fail,userid:%d', userId)
            return None

        nickname = crack.listLPop(CONF['redis']['live'])
        if nickname == None:
            logger.error('fetch record get nickname null!!')
            return None

    user = dict(nickname=nickname,loc='',fts=now(),cnt=1)
    rv   = crack.hashMSet(ip,user)
    if rv != True:
        logger.error('write user record fail!!')

    #ck名称集合，写入redis
    rv = crack.setAdd(CONF['redis']['user'], ip)
    if rv != True:
        logger.info('write ck nickanme set to redis fail')

    #获取cookie
    record = crack.hashGetAll(nickname)
    if record == None:
        logger.error('cookie record not existed nickname:%s', nickname)
        return None

    return record

def get_record_from_redis(ip,userId):
    crack = libredis.LibRedis(userId)
    len = crack.hashHlen(ip)
    if len == 0:
        return None
    record = crack.hashGetAll(ip)
    if record.has_key('nickname') ==False:
        return None
    nickname = record['nickname']
    len = crack.hashHlen(nickname)
    if len == 0:
        return None
    record = crack.hashGetAll(nickname)
    logger.info(record)
    return record

def gstat_clear(userId):
    stat = dict()
    stat['total_renqi'] = 0
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
            return CNT
        rv = crack.listRPush(CONF['redis']['live'], *const)
        if rv <= 0:
            logger.error('write ck nickname to redis(%d) live list fail!!',userId)
        else:
            logger.info('write ck nickname to redis(%d) live list success, %d', userId,rv)

    logger.info("%d records reset." ,CNT)

    freeUserCK(userId)
    return CNT

def clear_records(userId):
    #reset 用户记录
    reset_records(userId)
    #清空ck
    CNT = 0
    crack = libredis.LibRedis(userId)
    ##使用随机方式，索引存储在无序集合中
    if CONF['random'] == True:
        while crack.setCard(CONF['redis']['const']) > 0:
            nickname = crack.setSpop(CONF['redis']['const'])
            if nickname != None:
                record = crack.hashGetAll(nickname)
                if record == None:
                    continue
                CNT += 1
                rv = crack.hashDel(nickname, *record.keys())
                logger.info('clear nickname(%s) cookie hash rv(%d)', nickname, rv)

        while crack.setCard(CONF['redis']['live']) > 0:
            nickname = crack.setSpop(CONF['redis']['live'])
            if nickname != None:
                logger.info('del redis live set: nickname(%s)', nickname)

        #更新g_stat total  变量
        Digit = crack.setCard(CONF['redis']['const'])
    ##使用顺序模式，索引存储在列表中
    else:
        while crack.listLLen(CONF['redis']['const']) > 0:
            nickname = crack.listLPop(CONF['redis']['const'])
            if nickname != None:
                record = crack.hashGetAll(nickname)
                if record == None:
                    continue
                CNT += 1
                rv = crack.hashDel(nickname, *record.keys())
                logger.info('clear nickname(%s) cookie hash rv(%d)', nickname, rv)

        num = crack.delete(CONF['redis']['live'])
        logger.info('redis delete(%d) live list num=%d', userId, num)

        #更新g_stat total  变量
        Digit = crack.listLLen(CONF['redis']['const'])

    crack.hashSet('g_stat', 'total', Digit)
    logger.info("%d cookie records clean.", CNT)

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

def writeTaskToRedis(userId, room_url, ck_url, begin_time, total_time, \
                     user_num, last_time_from, last_time_to, time_gap, gap_num):
    """
    将用户的任务写入Redis
    :param userId:
    :param room_url:
    :param ck_url:
    :param begin_time:
    :param total_time:
    :param user_num:
    :param last_time_from:
    :param last_time_to:
    :return:
    """
    #处理参数
    task =dict()
    task['submit_time'] = now()
    task['room_url'] = room_url
    #task['ck_url']   = ck_url
    task['begin_time'] = begin_time.replace('T', ' ')
    task['total_time'] = total_time
    task['user_num']   = user_num
    task['req']        = 0
    task['ck_req']     = 0
    task['last_time_from'] = last_time_from
    task['last_time_to']   = last_time_to
    task['time_gap']       = time_gap
    task['gap_num']        = gap_num
    task['user_id']        = userId
    task['effective']      = 1  #有效标志
    task['reset_done']     = 0  #重置ck
    #content= '<t a="%d|20" flash="1" isBoot="1" ckul=%s s=%s><p a="%d,%d|0|0|5" /></t>' \
    #         %( (int(total_time)) * 60, ck_url, room_url,(int(last_time_from)) * 60, (int(last_time_to)) * 60)
    #task['content'] = content

    task_timestamp = strToTimestamp(task['begin_time'])
    task['begin_timestamp'] = task_timestamp

    #获取任务数量
    #将任务存储在DB15中统一管理
    crack = libredis.LibRedis(15)
    Digit = crack.zCard(CONF['redis']['begintask'])
    taskID = 'user%02d%04d' %(userId, Digit)
    task['task_id'] = taskID
    task['ck_url'] = ck_url+'&id='+taskID
    content= '<t a="%d|20" flash="1" isBoot="0" ckul=%s s=%s><p a="%d,%d|0|0|5" /></t>' \
             %( (int(total_time)) * 60, task['ck_url'], room_url,(int(last_time_from)) * 60, (int(last_time_to)) * 60)
    task['content'] = content
    logger.info(task)

    # task写入redis
    rv = crack.hashMSet(taskID, task)
    if rv != True:
        logger.info('write to redis fail %s', taskID)
        return False
    # task名称以开始时间作为score集合，写入redis
    a=dict()
    a[taskID] = task_timestamp
    num = crack.zAdd(CONF['redis']['begintask'], a)
    if num != 1:
        logger.info('write task id zset to redis fail')
        return False

    # task名称以结束时间作为score集合，写入redis
    a=dict()
    a[taskID] = task_timestamp + (int(total_time)) * 60
    num = crack.zAdd(CONF['redis']['endtask'], a)
    if num != 1:
        logger.info('write task id zset to redis fail')
        return False
    return True

def delTaskFromRedis(userId,task_id):
    """
    根据任务ID删除任务（更新删除标志位）
    :param userId:
    :param task_id:
    :return:
    """
    crack = libredis.LibRedis(15)
    rv = crack.hashExists(task_id,'effective')
    if rv == False:
        logger.info('Task:%s, not exist!!', task_id)
        return False
    logger.info('Task:%s, exist!')
    crack.hashSet(task_id,'effective', 0)
    logger.info('Task:%s, del success!')
    return True

def getUserTaskList(userId):
    tasks_list = list()

    #任务存储在DB15中，故获取
    crack = libredis.LibRedis(15)
    task_num = crack.zCard(CONF['redis']['begintask'])
    if task_num == 0:
        return tasks_list

    tasks = crack.zRange(CONF['redis']['begintask'], 0, task_num-1)
    for task in tasks:
        task_dict = crack.hashGetAll(task)
        if task_dict == None:
            logger.error('异常，在redis中找不到表项')
            continue
        if (int(task_dict['user_id'])) == (int(userId)):
            if (int(task_dict['effective'])) == 1:
                task_dict['status'] = 'Validated'
            else:
                task_dict['status'] = 'Cancelled'
            tasks_list.append(task_dict)
    tasks_list.reverse()
    return tasks_list

def parseOrder(record):
    order = dict()
    order['id'] = record[0]
    order['status'] = record[1]
    order['name'] = record[2]
    order['custom'] = record[3]
    order['platform'] = record[4]  
    order['room_id'] = record[5]
    order['order_type'] = record[6]
    order['renqi'] = record[7]
    order['income'] = record[8]
    order['ctime'] = record[9]
    order['sdate'] = record[10]
    order['edate'] = record[11]
    order['note'] = record[12]

    return order

def room_url(platform, room_id):
    room_url = ""
    if platform == "douyu":
        room_url = "https://www.douyu.com/%s" %(room_id)
    elif platform == "huya":
        room_url = "https://www.huya.com/%s" %(room_id)
    elif platform == "egame":
        room_url = "https://egame.qq.com/%s" %(room_id)
    else:
        room_url = "https://www.douyu.com/%s" %(room_id)

    return room_url

def getOrderList():
    order_list = list()

    records = libdb.LibDB().query('ordtb')

    for record in records :
        order = parseOrder(record)
        order_list.append(order)

    return order_list

def getOrder(order_id):
    record = libdb.LibDB().query_by_id(order_id, 'ordtb')

    logger.debug("order_id=%s, record=%s" %(order_id, record))
    if record != False and record != None:
        order = parseOrder(record)
        return order
    else:
        return None

def getTaskList():
    tasks_list = list()

    #任务存储在DB15中，故获取
    crack = libredis.LibRedis(15)
    task_num = crack.zCard(CONF['redis']['begintask'])
    if task_num == 0:
        return tasks_list

    tasks = crack.zRange(CONF['redis']['begintask'], 0, task_num-1)
    for task in tasks:
        task_dict = crack.hashGetAll(task)
        if task_dict == None:
            logger.error('异常，在redis中找不到表项')
            continue
        if (int(task_dict['effective'])) == 1:
            task_dict['status'] = 'Validated'
        else:
            task_dict['status'] = 'Cancelled'
        tasks_list.append(task_dict)
    tasks_list.reverse()
    return tasks_list

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
    logger.info('begin_task_num=%d', begin_task_num)
    if task_num != begin_task_num:
        logger.error('task_num != begin_task_num,异常，需要关注')

    end_task_num = crack.zRmRangeByScore(CONF['redis']['endtask'], start, end)
    logger.info('end_task_num=%d', end_task_num)
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



def updateTaskCKReq(taskID):
    if taskID != None:
        crack = libredis.LibRedis(15)
        crack.hashincr(taskID,'ck_req')
    else:
        logger.error('taskID is null, can not update task ck_req number!!!')


def dateRangeToTimeStamp(date_range):
    """
    02/20/2019 - 03/21/2019
    :param date_range:
    :return:
    """
    date = date_range.split(' - ')
    date_from = date[0]
    date_to   = date[1]
    logger.info('date_from: %s', date_from)
    logger.info('date_to  : %s', date_to)
    month_from = date_from.split('/')[0]
    day_from   = date_from.split('/')[1]
    year_from  = date_from.split('/')[2]
    month_to   = date_to.split('/')[0]
    day_to     = date_to.split('/')[1]
    year_to    = date_to.split('/')[2]
    start_str = '%s-%s-%s 00:00:00' %(year_from, month_from, day_from)
    end_str   = '%s-%s-%s 23:59:59' %(year_to,   month_to,   day_to)
    logger.info('start_str: %s, end_str: %s', start_str, end_str)

    timestamp_start = strToTimestamp(start_str)
    timestamp_end   = strToTimestamp(end_str)
    logger.info('timestamp_start:%d', timestamp_start)
    logger.info('timestamp_end  :%d', timestamp_end)

    return timestamp_start,timestamp_end

def dateRangeToFileName(date_range):
    """
    02/20/2019 - 03/21/2019
    :param date_range:
    :return:  字符串 0220-0321.txt
    """
    date = date_range.split(' - ')
    date_from = date[0]
    date_to   = date[1]
    logger.info('date_from: %s', date_from)
    logger.info('date_to  : %s', date_to)
    month_from = date_from.split('/')[0]
    day_from   = date_from.split('/')[1]

    month_to   = date_to.split('/')[0]
    day_to     = date_to.split('/')[1]

    file_str = '%s%s-%s%s.txt' %(month_from, day_from, month_to, day_to)
    logger.info('file name: %s', file_str)

    return file_str

def SaveAccountToFile(line,file):
    """
    功能：写行内容到文件中
    :param line: 账号内容
    :return: 无
    """
    if file == '':
        logger.error('输出账号文件为空')
        return
    #str = file.split('.')
    #fileName = str[0] + time.strftime('%Y-%m-%d') +'.'+ str[1]
    fileName = file
    logger.info('SaveAccountToFile: %s', fileName)
    f = open(fileName, 'a+')
    f.writelines(line + '\n')
    f.close()
    logger.debug('账号写入文件：%s',line)

def getFileFromDBByDateRange(date_range):
    """
    根据日期范围从数据库选择用户名和密码，保存成文件
    :param date_range:
    :return:
    """
    timestampBegin, timestampEnd = dateRangeToTimeStamp(date_range)
    #写文件
    file = dateRangeToFileName(date_range)
    open(file, "w+").close()

    records = takeOutCksByTimeStampRange(timestampBegin, timestampEnd)
    if records == False:
        return file

    #logger.info(records)
    rcs = list()
    for record in records:
        t = dict()
        t['nickname'] = record[2]
        t['password'] = record[3]
        t['regtime']  = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(record[4])))
        t['uptime']   = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(record[5])))
        rcs.append(t)
        #logger.info(t)

    for r in rcs:
        r_str = '%s----%s' %(r['nickname'], r['password'])
        SaveAccountToFile(r_str.encode("utf-8"), file)

    return file

def getFileFromDBByIndex(index_begin, index_to):
    """
    根据日期范围从数据库选择用户名和密码，保存成文件
    :param date_range:
    :return:
    """
    #写文件
    file = '%d-%d.txt' %(index_begin, index_to)
    open(file, "w+").close()

    records = takeOutCksByIndexFromDB(index_begin,index_to-index_begin+1)
    if records == False:
        return file

    #logger.info(records)
    rcs = list()
    for record in records:
        t = dict()
        t['nickname'] = record[2]
        t['password'] = record[3]
        t['regtime']  = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(record[4])))
        t['uptime']   = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(record[5])))
        rcs.append(t)
        #logger.info(t)

    for r in rcs:
        r_str = '%s----%s' %(r['nickname'], r['password'])
        SaveAccountToFile(r_str.encode("utf-8"), file)

    return file

'''
add some function by ben 2019-05-22
'''
def takeIdleCK():
    records = libdb.LibDB().query_by_condition("uid=0", CONF['database']['table'])

    if records == False:
        return None

    return records
    #select sum(Value) from table1 where Name = 'AAA'

def allocUserCK(ckid, uid):
    return libdb.LibDB().update_db("uid=%d" %(uid), "id=%s" %(ckid), CONF['database']['table'])

def freeUserCK(uid):
    return libdb.LibDB().update_db("uid=0", "uid=%d" %(uid), CONF['database']['table'])

def getUserCookieList(userId):
   
    cookie_list = list()
    #任务存储在DB15中，故获取

    crack = libredis.LibRedis(userId)

    record_num = crack.listLLen(CONF['redis']['live'])

    #logger.debug('!!!!!getUserCookieList: record_num=%d\n' %(record_num))
    if record_num == 0:
        return cookie_list

    key_list = crack.listLRange(CONF['redis']['live'], 0, record_num-1)

    #logger.debug('!!!!!getUserCookieList: record_list=%s' %(record_list))
    for key in key_list:
        cookie = crack.hashGetAll(key)
        #logger.debug('!!!!!getUserCookieList: cookie=%s' %(cookie))

        cookie_list.append(cookie)

    return cookie_list

def getUserStat(userId):
     stat = libredis.LibRedis(userId).hashGetAll('g_stat')
     return stat

def total_renqi_get(userId):
    stat = libredis.LibRedis(userId).hashGetAll('g_stat')
    return float(stat['total_renqi'])

def renqi_to_cookies(userId, renqi):
    cookies = getUserCookieList(userId)

    cur_ck = 0
    cur_renqi = 0
    logger.debug("renqi_to_cookies: userId=%d, renqi=%d, len(cookies)=%d" %(userId, renqi, len(cookies)))
    for cookie in cookies:
        cur_renqi += float(cookie['radio'])
        cur_ck += 1
        if cur_renqi > renqi:
            break;

    return cur_ck

def add_renqi(total, userId):
    """
    根据人气需求，将cookie导入到redis缓存
    :param total:  需求的人气数量
    :param userId: 用户id
    :return:
    """

    alloced = 0

    crack = libredis.LibRedis(userId)

    records = takeIdleCK()

    if records == None:
        return alloced

    rcs = list()
    for record in records:
        t = dict()
        t['id'] = record[0]
        t['seq'] = record[0]
        t['nickname'] = record[2]
        t['password'] = record[3]
        t['grp'] = record[4]
        t['radio'] = record[5]
        t['regtime']  = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(record[6])))
        t['uptime']   = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(record[7])))
        
        t['cookie']   = record[11]

        alloced += t['radio']

        rcs.append(t)
        logger.info(t)

        allocUserCK(t['id'], userId)
        crack.hashincrfloat('g_stat', 'total_renqi', t['radio'])
        if alloced >= total:
            break

    logger.debug("alloced=%d, len(rcs)=%d" %(alloced, len(rcs)))
    writeRecordsToRedis(rcs, userId)

    return alloced

def renqi_alloc(userId, req_renqi):
    alloced = -1
    total_renqi = total_renqi_get(userId)
    balance = req_renqi - total_renqi

    if balance > 0:
        alloced = add_renqi(balance, userId)

    logger.debug("renqi_alloc: total_renqi=%d, req_renqi=%d, balance=%d" %(total_renqi, req_renqi, balance))
    return alloced

logger = gl.get_logger()
CONF   = gl.get_conf()
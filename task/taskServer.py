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
import taskCommon as taskCommon

global logger
global CONF

def assemblPayload(msgid, task):
    """
    组装payload
    :param msgid:
    :param task:
    :return:
    """
    tid      = 0x117834
    parallel = 0
    mid      = 1
    total_time = (int(task['total_time'])) * 60
    ckul       = task['ck_url']
    room_url   = task['room_url']
    last_time_from = (int(task['last_time_from'])) * 60
    last_time_to   = (int(task['last_time_to']  )) * 60
    content= '<t a="%d|20" flash="1" isBoot="1" ckul=%s s=%s><p a="%d,%d|0|0|5" /></t>' \
             %(total_time, ckul, room_url,last_time_from, last_time_to)
    length = len(content)
    fmt = '!BIBH%dsI' %(length)
    logger.info('assemblPayload fmt: %s', fmt)
    data = struct.pack(fmt, msgid, tid, parallel, length,content, mid)
    logger.info(data)
    return data

def processDeal(msgid,pid,uid):
    ou = dict(error=0,msg='ok',data=dict())
    if pid != 5:
        ou['error'] = 1
        ou['msg']   = 'product id error!'
        return ou

    #获取一个任务
    ou1 = taskCommon.getOneTask()
    if ou1['error'] != 0:
        #没有任务
        logger.info('没有获取到任务，当前没有任务')
        data = struct.pack("!BI", msgid, 0)
        ou['error'] = 0
        ou['msg']   = 'ok'
        ou['data']['payload'] = data
        ou['data']['has_task'] = 0
    else:
        #获取到了任务
        logger.info('获取到了任务')
        payload = assemblPayload(msgid,ou1['data'])
        ou['error'] = 0
        ou['msg']   = 'ok'
        ou['data']['payload']  = payload
        ou['data']['has_task'] = 1  #重要标志
        ou['data']['task']     = ou1['data']
    return ou

def decode_data(data):
    pad = struct.unpack("B", '\x33') * len(data)
    fmt = "B" * len(data)
    bytes = struct.unpack(fmt, data)
    bytes = [bytes[i] ^ pad[i] for i in xrange(len(bytes))]
    bytes = struct.pack(fmt, *bytes)
    return bytes

def task_th():
    HOST = CONF['host']
    PORT = CONF['port']
    BUFSIZ = 1024
    tcpSerSock = socket.socket()
    tcpSerSock.bind(('' ,PORT))
    tcpSerSock.listen(5)
    while True:
        cs, address = tcpSerSock.accept()
        logger.info('got connected from %s', address)
        recvData = cs.recv(BUFSIZ)
        logger.info('recvData len:%d', len(recvData))
        if len(recvData) != 29:
            continue
        data = decode_data(recvData)
        msgid, pid, uid = struct.unpack('!BI24s', data)
        logger.info('msgid:%d',msgid)
        logger.info('pid: %d'    ,pid)
        logger.info('uid: %s', uid)
        ou = processDeal(msgid,pid,uid)
        if ou['error'] == 0:
            sendData = decode_data(ou['data']['payload'])
            cs.send(sendData)
            logger.info('已经回复了服务器')
            #同步状态到user redis db中
            if ou['data']['has_task'] == 1:
                logger.info('任务已经提交给了服务器')
                logger.info('本地更新任务状态')
                if taskCommon.updateTaskStatus(ou['data']['task']) == True:
                    logger.info('本地更新任务状态 成功')
                else:
                    logger.error('本地更新任务状态 失败!!!')
            else:
                logger.info('没有任务提交给服务器')
                logger.info('本地无需更新任务状态')
        else:
            logger.error('process deal error %s', ou['msg'])
        cs.close()

if __name__ == '__main__':
    logger = gl.get_logger()
    CONF = gl.get_conf()
    thread.start_new_thread(task_th, ())
    time.sleep(10)
    while True:
        taskCommon.loop_th()
        time.sleep(120)





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
from twisted.internet import reactor, protocol

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
    content  = task['content']
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
        ou['data']['has_task'] = 0
    else:
        #获取到了任务
        logger.info('获取到了任务')
        data = assemblPayload(msgid,ou1['data'])
        ou['data']['has_task'] = 1  #重要标志
        ou['data']['task']     = ou1['data']
    ou['error'] = 0
    ou['msg'] = 'ok'
    ou['data']['payload'] = decode_data(data)
    return ou

def decode_data(data):
    pad = struct.unpack("B", '\x33') * len(data)
    fmt = "B" * len(data)
    bytes = struct.unpack(fmt, data)
    bytes = [bytes[i] ^ pad[i] for i in xrange(len(bytes))]
    bytes = struct.pack(fmt, *bytes)
    return bytes

def task_th(recvData):
    ou = dict(error=0, msg='ok', data=dict())
    logger.info('recvData len:%d', len(recvData))
    if len(recvData) != 29:
        ou['error'] = 1
        ou['msg']   = 'rcv data error!'
        return ou
    data = decode_data(recvData)
    msgid, pid, uid = struct.unpack('!BI24s', data)
    logger.info('msgid:%d', msgid)
    logger.info('pid: %d', pid)
    logger.info('uid: %s', uid)
    ou = processDeal(msgid, pid, uid)
    return ou

class Echo(protocol.Protocol):
    """This is just about the simplest possible protocol"""
    def dataReceived(self, data):
        "As soon as any data is received, write it back."
        ip, port = self.transport.client
        logger.info('got connected from %s, %d', ip, port)
        ou = task_th(data)
        if ou['error'] == 0:
            self.transport.write(ou['data']['payload'])
            #同步状态到user redis db中
            if ou['data']['has_task'] == 1:
                logger.info('任务已经提交给了服务器')
                logger.info('本地更新任务状态')
                taskCommon.updateTaskStatus(ou['data']['task'])
            else:
                logger.info('没有任务提交给服务器')
                logger.info('本地无需更新任务状态')
        else:
            logger.error('process deal error %s', ou['msg'])

if __name__ == '__main__':
    logger = gl.get_logger()
    CONF = gl.get_conf()
    """This runs the protocol on port 8000"""
    factory = protocol.ServerFactory()
    factory.protocol = Echo
    reactor.listenTCP(CONF['port'], factory)
    reactor.run()
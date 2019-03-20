#!/usr/bin/python
#coding:utf-8

import socket
import sys
import time
import struct
import inits
import globalvar as gl

global logger
global CONF


def encode_data(data):
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
    UID = 'bdc5e03cf80abee9e0103d44'
    client = socket.socket()
    client.connect((HOST, PORT))
    data = struct.pack("!BI24s", 6, 5, UID)
    for i in data:
        sys.stdout.write('%#x' % ord(i))
    print ''
    data  = encode_data(data)
    for i in data:
        sys.stdout.write('%#x' % ord(i))
    print ''
    client.send(data)
    recvData = client.recv(BUFSIZ)
    data = encode_data(recvData)
    for i in data:
        sys.stdout.write('%#x' % ord(i))
    print ''
    print 'data len:%d' %(len(data))
    if len(data) > 10:
        fmt = '!BIBH%dsI' %(len(data)-12)
        msgid, tid, parallel,length,content,mid = struct.unpack(fmt, data)
        print 'msgid   : ' , msgid
        print 'tid     : ' , tid
        print 'parallel: ' , parallel
        print 'length  : ' , length
        print 'content : ' , content
    else:
        msgid,tid =  struct.unpack('!BI', data)
        print 'msgid   : ' , msgid
        print 'tid     : ' , tid
    client.close()
    time.sleep(0)

if __name__ == '__main__':
    logger = gl.get_logger()
    CONF = gl.get_conf()
    for i in range(0,6):
        task_th()

#!/usr/bin/env python
# -*- coding:utf-8 -*-
#Filename:taskClientV2.py

import socket
import struct
from cmd import Cmd
import platform,os
import sys,time
import random,string
import requests
import threading
import threadpool
import inits
import globalvar as gl

global logger
global CONF

rip = lambda: '.'.join([str(int(''.join([str(random.randint(0, 2)), str(random.randint(0, 5)), str(random.randint(0, 5))]))) for _ in range(4)])

def SaveAccountToFile(line,file):
    """
    功能：写行内容到文件中
    :param line: 账号内容
    :return: 无
    """
    if file == '':
        logger.error('输出账号文件为空')
        return
    str = file.split('.')
    fileName = str[0] + time.strftime('%Y-%m-%d') +'.'+ str[1]
    logger.info('SaveAccountToFile: %s', fileName)
    f = open(fileName, 'a+')
    f.writelines(line + '\n')
    f.close()
    logger.info('账号写入文件：%s',line)


def autoGetCK(num):
    success = 0
    index    = 0
    fail    = 0
    while index < num:
        index = index + 1
        ip = rip()
        url = "http://127.0.0.1:8200/useradmin/cookie"
        payload = dict(ip=rip(),debug='1',user=0)
        r = requests.get(url, params=payload)
        logger.debug('链接: ' + str(r.url))
        ##判断http post返回值
        if r.status_code != requests.codes.ok:
            logger.error('get 失败,r.status_code=%d', r.status_code)
            fail = fail + 1
            continue
        success = success + 1
        logger.debug('get 成功, r.status_code=%d', r.status_code)
        responsed = r.text
        logger.debug('返回内容：%s', responsed)
        SaveAccountToFile(responsed, 'ck.txt')

    return success

def encode_data(data):
    pad = struct.unpack("B", '\x33') * len(data)
    fmt = "B" * len(data)
    bytes = struct.unpack(fmt, data)
    bytes = [bytes[i] ^ pad[i] for i in xrange(len(bytes))]
    bytes = struct.pack(fmt, *bytes)
    return bytes

def getCKUrl(content):
    """
    解析出ckurl链接
    :param content:
    :return:
    """
    str = content.split(' ')[4]
    url= str.split('=', 1)[1]
    logger.info(url)
    return url

L1 = threading.Lock()
L2 = threading.Lock()
L3 = threading.Lock()
def getCK(url):
    """
    根据url请求ck
    :param url:
    :return:
    """
    global Success
    global Fail
    payload = dict(ip=rip(), debug='1')
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
                    'Connection': 'close'}
    r = requests.get(url, params=payload,headers=headers)
    logger.debug('链接: ' + str(r.url))
    ##判断http post返回值
    if r.status_code != requests.codes.ok:
        logger.error('get 失败,r.status_code=%d', r.status_code)
        #L1.acquire()
        Fail = Fail +1
        #L1.release()
        return
    Success = Success + 1
    #logger.debug('get 成功, r.status_code=%d', r.status_code)
    responsed = r.text
    #logger.debug('返回内容：%s', responsed)
    L2.acquire()
    SaveAccountToFile(responsed, 'ck.txt')
    L2.release()

def task_th(id):
    global Success
    global Fail
    global None_Task
    HOST = CONF['host']
    PORT = CONF['port']
    BUFSIZ = 1024
    #UID = 'bdc5e03cf80abee9e0103d44'
    UID = ''.join(random.sample(string.ascii_letters + string.digits, 24))
    client = socket.socket()
    client.connect((HOST, PORT))
    data = struct.pack("!BI24s", 6, 5, UID)
    data  = encode_data(data)
    client.send(data)
    recvData = client.recv(BUFSIZ)
    data = encode_data(recvData)
    if len(data) > 10:
        Success = Success + 1
        fmt = '!BIBH%dsI' %(len(data)-12)
        msgid, tid, parallel,length,content,mid = struct.unpack(fmt, data)
        #print 'msgid   : ' , msgid
        #print 'tid     : ' , tid
        #print 'parallel: ' , parallel
        #print 'length  : ' , length
        #print 'content : ' , content
        logger.info('msgid: %s', msgid)
        logger.info('tid: %s', tid)
        logger.info('parallel: %s', parallel)
        logger.info('length: %s', length)
        logger.info('content: %s', content)
        url = getCKUrl(content)
        logger.info(url)
        #getCK(url)
    else:
        msgid,tid =  struct.unpack('!BI', data)
        #print 'msgid   : ' , msgid
        #print 'tid     : ' , tid
        None_Task =  None_Task +1
    client.close()

def DisplayLoginInfo(num):
    """
    实时显示获取cookie数量
    :return:
    """
    global Success
    global Fail
    global None_Task
    while True:
        num_str = '%d' % (num)
        success_str = '%d' % (Success)
        fail_str = '%d' % (Fail)
        none_str = '%d' % (None_Task)
        result_str = 'Needs: ' + num_str + ' Success: ' + success_str + ' Fail: ' + fail_str + ' None: ' + none_str
        sys.stdout.write("\r{0}".format(result_str))
        sys.stdout.flush()
        if num == (Success+Fail+None_Task):
            print('\n')
            logger.info('DisplayLoginInfo exit')
            break
        time.sleep(2)

def autoGetTask(num=2000):
    index = 0
    global Success
    global Fail
    global None_Task
    Success = 0
    Fail    = 0
    None_Task = 0
    t = threading.Thread(target=DisplayLoginInfo, args=(num, ) )
    t.start()
    pool = threadpool.ThreadPool(CONF['ThreadNum'])
    #while True:
    acc_list = list()
    for i in range(0, num):
        acc_list.append(i)
    logger.info(acc_list)
    requests = threadpool.makeRequests(task_th, acc_list)
    [pool.putRequest(req) for req in requests]
    pool.wait()

class Cli(Cmd):
    u"""help
    这是doc
     """
    prompt = 'douYu>'
    intro = 'Welcome!'

    def __init(self):
        Cmd.__init__(self)

    def preloop(self):
        print "Welcom into Douyu cookie Test Cmd"

    def postloop(self):
        print 'Bye!'
        if platform.system() == 'Darwin':
            print "退出程序"
        else:
            print  'Exit Program'
    def do_exit(self, arg):
        return True  # 返回True，直接输入exit命令将会退出
    def help_exit(self):
        print '退出命令行'

    def do_ck(self,arg):
        num = int(arg)
        cnt = autoGetCK(num)
        if cnt == num:
            print('Test scucess!')
        else:
            print('Test fail, need %d, success %d', num, cnt)

    def help_ck(self):
        print 'cookie 请求测试程序,请输入请求个数'

    def do_task(self,arg):
        autoGetTask()
    def help_task(self):
        print 'task 请求测试程序,请求任务并获取ck'

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf8')
    logger = gl.get_logger()
    CONF = gl.get_conf()
    cli = Cli()
    cli.cmdloop()
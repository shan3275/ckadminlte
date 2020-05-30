#!/usr/bin/python
#-*- coding: UTF-8 -*-
# FileName : testCmd.py
# Author   : Shan
# DateTime : 2020/5/22
# SoftWare : Visual Studio Code

import socket
import struct
from cmd import Cmd
import platform,os
import sys,time
import random
import requests
import threading
import threadpool
import libdb    as libdb
import libredis as libredis
import libcm     as libcm
import inits
import globalvar as gl

global logger
global CONF

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

L1 = threading.Lock()
L2 = threading.Lock()
def upip_th(ip):
    '''
    更新ip区域信息，写入数据库
    '''
    global Success
    global Fail
    global errFile

    areaid = libcm.getIPAreaID(ip)
    if areaid == False:
        Fail += 1
        L1.acquire()
        SaveAccountToFile(ip,errFile)
        L1.release()
    else:
        Success +=1
        L2.acquire()
        SaveAccountToFile(ip,'success.txt')
        L2.release()

def DisplayProcessInfo(num):
    """
    实时显示获取ip 区域位置数量
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
        if num == (Success+Fail):
            print('\n')
            logger.info('DisplayProcessInfo exit')
            break
        time.sleep(2)
    print('\n')

def createLocalIpWareHouse(ipFile, outFile):
    '''
    查询输入文件中的IP区域信息，更新到本地的ip库中
    Args:
        ipFile:   ip输入文件
        outFile:  保存处理失败的IP
    Return None
    '''
    iptb = list()
    f = open(ipFile, "r")
    for line in f:
        line = line.strip('\r\n')
        iptb.append(line)
    f.close()
    logger.info(iptb)

    num = len(iptb)
    logger.info('ip list len: %d', num)

    global Success
    global Fail
    global None_Task
    global errFile
    Success = 0
    Fail    = 0
    None_Task = 0
    errFile = outFile

    t = threading.Thread(target=DisplayProcessInfo, args=(num, ) )
    t.start()

    pool = threadpool.ThreadPool(CONF['ThreadNum'])
    requests = threadpool.makeRequests(upip_th, iptb)
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

    ##打印配置文件新
    def do_conf(self,line):
        print(CONF)
    def help_conf(self):
        print '打印配置文件信息'

    def do_upip(self,line):
        if line == '':
            print 'ipFile outFile'
            return
        arg = line.split()

        ipFile  = arg[0]
        outFile = arg[1]
        createLocalIpWareHouse(ipFile, outFile)

    def help_upip(self):
        print '查询IP归属地并记录入库，输入参数：ipFile  outFile'

    def do_mvarea(self,arg):
        total = libcm.queryAreaCount()
        print 'DB 中表项数量:  %d' %(total)
        num   = libcm.getAreaFromDBandWriteToRedis()
        print '写入Reis表项数量: %d' %(num)
    
    def help_mvarea(self):
        print '将mysql中area表项数据移动到redis中'

    def do_mvip(self,arg):
        total = libcm.queryIPCount()
        print 'DB 中表项数量:  %d' %(total)
        num = libcm.getIptbFromDBandWriteRedis()
        print '写入Reis表项数量: %d' %(num)
    
    def help_mvip(self):
        print '将mysql中ip表项数据移动到redis中'

    def do_ipcode(self, arg):
        total = libcm.queryIPCount()
        print 'DB 中表项数量:  %d' %(total)
        num = libcm.updateIptbPostcode()
        print 'DB 中更新成功数量: %d'  %(num)

    def help_ipcode(self):
        print 'mysql中iptb表项增加了postcode字段，需要查询area更新字段值'

    def do_comip(self,arg):
        libcm.compareIpDB()
    
    def help_comip(self):
        print '比较线上获取的ip和本地ip库是否一致'

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf8')
    logger = gl.get_logger()
    CONF = gl.get_conf()
    cli = Cli()
    cli.cmdloop()

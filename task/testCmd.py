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
from datetime import datetime
import libdb    as libdb
import libredis as libredis
import taskCommon     as taskCommon
import inits
import globalvar as gl

global logger
global CONF

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

    def do_taskstat(self,arg):
        if arg == '':
            print '输入时间，例如：2020-06-09 20:28:00'
            return
        #转换成时间数组
        timeArray = time.strptime(arg, "%Y-%m-%d %H:%M:%S")
        print timeArray
        timestamp = time.mktime(timeArray)
        taskCommon.colectTaskStatByHour(timestamp)

    def help_taskstat(self):
        print '将任务统计写入数据库表项中，输入参数：2020-06-09 20:28:00'

    def do_creqtaskstat(self,arg):
        if arg == '':
            print '输入时间，例如：2020-06-09 20:28:00'
            return
        #转换成时间数组
        timeArray = time.strptime(arg, "%Y-%m-%d %H:%M:%S")
        print timeArray
        timestamp = time.mktime(timeArray)
        taskCommon.collectClientRequestTaskStatsByHour(timestamp)

    def help_creqtaskstat(self):
        print '将请求统计写入数据库表项中，输入参数：2020-06-09 20:28:00'

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf8')
    logger = gl.get_logger()
    CONF = gl.get_conf()
    cli = Cli()
    cli.cmdloop()

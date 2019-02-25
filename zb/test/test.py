#!/usr/bin/env python
# -*- coding:utf-8 -*-
#Filename:app.py

from cmd import Cmd
import platform,os
import sys,time
import random
import requests
import logging
from logging import handlers
global logger

def log_init(log_app_name, file_name):
    logger = logging.getLogger(log_app_name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    ch = logging.handlers.TimedRotatingFileHandler(
                    filename=file_name,
                    when='midnight',
                    backupCount=3
                    )
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)

    #控制台输出
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    #logger.addHandler(sh)

    return logger
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
        url = "http://192.168.100.133:8889/admin/cookie"
        payload = dict(ip=rip(),debug='1')
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

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf8')
    logger = log_init('Test', 'TT.txt')
    cli = Cli()
    cli.cmdloop()
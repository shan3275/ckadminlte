#!/usr/bin/python
#coding:utf-8
import datetime
import time
import inits
import globalvar as gl
import libredis as libredis
import taskCommon as taskCommon
from apscheduler.schedulers.background import BackgroundScheduler

global logger
global CONF

def ckRsetTask():
    taskCommon.resetTaskCK()

def moveTaskTask():
    taskCommon.moveTaskFromRedistoDB()

if __name__ == '__main__':
    logger = gl.get_logger()
    CONF = gl.get_conf()
    # 创建后台执行的 schedulers
    scheduler = BackgroundScheduler()
    # 添加调度任务
    # 调度方法为 timedTask，触发器选择 interval(间隔性)，间隔时长为 50 秒
    scheduler.add_job(ckRsetTask, 'interval', seconds=50)
    # 启动调度任务

    # 定时每天 04:55:00秒执行任务
    #scheduler.add_job(moveTaskTask, 'cron', day_of_week='0-6', hour=04, minute=45, second=0)
    scheduler.start()

    while True:
        print(time.time())
        time.sleep(50)
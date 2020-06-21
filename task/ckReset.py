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

def collectTaskStatsTask():
    '''
    客户端请求ck的统计，http链接的统计
    '''
    lasthour = int(time.time()) - 3600
    taskCommon.colectTaskStatByHour(lasthour)

def collectClientRequestTaskStatsTask():
    '''
    客户端过来请求任务的统计,tcp链接的统计
    '''
    lasthour = int(time.time()) - 3600
    taskCommon.collectClientRequestTaskStatsByHour(lasthour)

if __name__ == '__main__':
    logger = gl.get_logger()
    CONF = gl.get_conf()
    # 创建后台执行的 schedulers
    scheduler = BackgroundScheduler()
    # 添加调度任务
    # 调度方法为 timedTask，触发器选择 interval(间隔性)，间隔时长为 50 秒
    scheduler.add_job(ckRsetTask, 'interval', seconds=50)
    # 启动调度任务
    #统计房间的投放情况
    #scheduler.add_job(collectTaskStatsTask, 'interval', seconds=120)
    scheduler.add_job(collectTaskStatsTask, 'cron', minute='40', hour='*/1')

    #统计任务的请求情况
    scheduler.add_job(collectClientRequestTaskStatsTask, 'cron', minute='1', hour='*/1')
    # 定时每天 04:55:00秒执行任务，将任务从缓存移动到db中
    scheduler.add_job(moveTaskTask, 'cron', day_of_week='0-6', hour=04, minute=55, second=0)
    scheduler.start()

    while True:
        print(time.time())
        time.sleep(50)
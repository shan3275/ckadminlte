#!/usr/bin/python
#-*- coding: UTF-8 -*-
# FileName : useradmin.py
# Author   : Shan
# DateTime : 2019/1/9
# SoftWare : PyCharm
from flask import Blueprint, abort,Flask, request, jsonify, render_template, redirect,url_for, send_file, send_from_directory
import flask_admin as admin
import os,json
import chardet
import time
import datetime
import urlparse
from urllib import urlencode
import random
import globalvar as gl
import libdb    as libdb
import libredis as libredis
import libcommon as libcommon

global logger
global CONF

def now():
    return time.strftime("%m-%d %H:%M:%S", time.localtime())
DEF_PORT = 8888
CUR_PORT = DEF_PORT
DEF_FILE = "def.txt"
g_stat = {"cycle":1, "pos":0,'take_out_cks':0,"total_renqi":0, "total":0, "asigned":0, "req":0, "rereq":0, "none":0, "boot_ts": now(), "reset_ts":now()}
g_records = []
g_cnt = {}


def gstat_init():
    """
    g_stat 变量初始化，在redis中
    :return:
    """
    for i in range(0, 16):
        crack = libredis.LibRedis(i)
        rv = crack.hashExists('g_stat', 'total')
        if rv == True:
            logger.info('g_stat exist in db%d redis, init exit', i)
            continue

        logger.info('g_stat no exist in db%d, now init', i)
        #不存在，故初始化
        rv = crack.hashMSet('g_stat', g_stat)
        if rv != True:
            logger.error('g_stat write redis in db%d fail', i)
            return False
        logger.info("g_stat write redis db%d success!", i)

    return True

def save_records(path):
    file = open(path, "w")
    CNT = 0
    for record in g_records:
        file.write(record['cookie'] + "\n")
        CNT += 1
    file.close()
    print "%d records save to %s" %(CNT, path)

def def_file_get():
    path = "download/"+"def_%d.txt" %(CUR_PORT)
    return path

def cookie_append(records):
    global g_records, g_stat
    for record in records:
        t = dict()
        t['idx']      = len(g_records)
        t['id']       = record[0]
        t['nickname'] = record[2]
        t['password'] = record[3]
        t['regdate']  = datetime.datetime.fromtimestamp(record[4])
        t['lastdate'] = datetime.datetime.fromtimestamp(record[5])
        t['colddate'] = datetime.datetime.fromtimestamp(record[6])
        t['ip']   = record[7]
        t['usednum']  = record[8]
        t['cookie']   = record[9]
        t['cts']      = now()
        t['ftc']      = ''
        t['loc']      = ''
        t['cnt']      = 0
        #logger.debug('cts: %s', t['cts'])
        g_records.append(t)
        g_stat['take_out_cks'] += 1

def urlAddPara(url, params):
    """
    给url增加参数，拼装新的链接
    :param url: 带参数，或者不带
    :param params: 字典形式 {'lang':'en','tag':'python'}
    :return:
    """
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)

    url_parts[4] = urlencode(query)

    return urlparse.urlunparse(url_parts)

class UserHomeView(admin.AdminIndexView):
    @admin.expose('/')
    def index(self):
        userIdStr = request.args.get('user')
        if userIdStr != None:
            userId = int(userIdStr)
        else:
            refer = request.referrer
            if refer == None:
                userId = 0
            else:
                para_str = urlparse.urlsplit(refer).query
                param = urlparse.parse_qs(para_str)
                logger.info(param)
                if param.has_key('user'):
                    para_dict = dict(user=param['user'][0])
                else:
                    para_dict = dict(user='0')
                logger.info(para_dict)
                url = urlAddPara(request.url, para_dict)
                return redirect(url)
        # 获取表项数量
        stat = libredis.LibRedis(userId).hashGetAll('g_stat')
        tasks = libcommon.getUserTaskList(userId)
        return self.render('useradmin/index.html',  g_stat=stat,user=userId, task_records=tasks)


    @admin.expose('/useradmin1')
    def useradmin1(self):
        userIdStr = request.args.get('user')
        if userIdStr != None:
            userId = int(userIdStr)
        else:
            refer = request.referrer
            if refer == None:
                userId = 0
            else:
                para_str = urlparse.urlsplit(refer).query
                param = urlparse.parse_qs(para_str)
                logger.info(param)
                if param.has_key('user'):
                    para_dict = dict(user=param['user'][0])
                else:
                    para_dict = dict(user='0')
                logger.info(para_dict)
                url = urlAddPara(request.url, para_dict)
                return redirect(url)
        # 获取表项数量
        stat = libredis.LibRedis(userId).hashGetAll('g_stat')
        tasks = libcommon.getUserTaskList(userId)
        return self.render('useradmin.html',  g_stat=stat,user=userId, task_records=tasks)

    @admin.expose('/upload',methods=('GET', 'POST'))
    def upload(self):
        """
        测试命令：curl -F "file=@/Users/liudeshan/work/studycase/script/flask/zb/2.csv" -X  "POST" http://localhost:8888/strapi/upload
        :return:
        """
        logger.debug('request.method:%s', request.method)
        logger.debug('request.files:%s', request.files['file'])
        userIdStr = request.args.get('user')
        if userIdStr != None:
            userId = int(userIdStr)
        else:
            # default 0
            userId = 0
        logger.debug('upload user=%d', userId)
        if request.method == 'POST':
            # 保存文件
            ou = libcommon.writeFileToRedis(request.files['file'], userId)
            if ou == True:
                return redirect(url_for('useradmin.index', user=userId))
            else:
                return json.dumps(ou)
        else:
            return redirect(url_for('useradmin.index', user=userId))

    @admin.expose('/take_cks_by_id',methods=('GET', 'POST'))
    def take_cks_by_id(self):
        global g_stat
        if request.method == 'POST':
            ck_id_from = request.form.get('ck_index')
            ck_num = request.form.get('ck_num')
            userIdStr = request.args.get('user')
            if userIdStr != None:
                userId = int(userIdStr)
            else:
                # default 0
                userId = 0
            logger.debug('ck_id_from: %s, ck_num: %s', ck_id_from, ck_num)
            libcommon.takeOutCksFromDBToRedis(int(ck_id_from), int(ck_num), userId)
        return redirect(url_for('useradmin.index', user=userId))

    @admin.expose('/take_out_cks', methods=['POST', 'GET'])
    def take_out_cks(self):
        global g_stat
        if request.method == 'POST':
            userIdStr = request.args.get('user')
            if userIdStr != None:
                userId = int(userIdStr)
            else:
                # default 0
                userId = 0
            cks_num = request.form.get('ck_num')
            # 读取cookie从数据库
            records = libcommon.takeOutCksFromDB(cks_num)
            if records != False and records != None:
                cookie_append(records)
        return redirect(url_for('useradmin.index', user=userId))

    @admin.expose('/act_reset', methods=['POST', 'GET'])
    def act_reset(self):
        userIdStr = request.args.get('user')
        if userIdStr != None:
            userId = int(userIdStr)
        else:
            # default 0
            userId = 0
        CNT = libcommon.reset_records(userId)
        return redirect(url_for('useradmin.index', user=userId))

    @admin.expose('/act_clear', methods=['POST', 'GET'])
    def act_clear(self):
        userIdStr = request.args.get('user')
        if userIdStr != None:
            userId = int(userIdStr)
        else:
            # default 0
            userId = 0
        CNT = libcommon.clear_records(userId)
        return redirect(url_for('useradmin.index', user=userId))

    # @admin.expose('/act_save', methods=['POST', 'GET'])
    def act_save(self):
        file = def_file_get()
        CNT = save_records(file)
        return redirect(url_for('useradmin2.admin'))

    # @admin.expose("/act_download", methods=['POST', 'GET'])
    def download(self):
        # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
        directory = os.getcwd()  # 假设在当前目录
        file = def_file_get()
        return send_from_directory(directory, file, as_attachment=True)

    @admin.expose('/cookie', methods=['GET'])
    def cookie(self):
        ##调试模式传递IP
        debug = request.args.get('debug')
        if debug != None:
            ip = request.args.get('ip')
            if ip == None:
                ip = '127.0.0.1'
        else:
            ##nginx 反向代理，获取真实IP
            if request.headers.has_key('X-Forwarded-For') == True:
                real_ip = request.headers['X-Forwarded-For']
                if real_ip != None:
                    if len(real_ip.split(',')) > 1:
                        ip = real_ip.split(",")[1]
                    else:
                        ip = real_ip
            else:
                ##未使用nginx反向代理，获取真实IP
                ip = request.remote_addr

        userIdStr = request.args.get('user')
        if userIdStr != None:
            userId = int(userIdStr)
        else:
            # default 0
            userId = 0
        taskID = request.args.get('id')
        crack = libredis.LibRedis(userId)
        crack.hashincr('g_stat', 'req')
        record = libcommon.get_record_from_redis(ip, userId)
        if record == None:
            record = libcommon.fetch_record_from_redis(ip, userId)
        else:
            crack.hashincr('g_stat', 'rereq')

        if record == None :
            cookie = "None"
            crack.hashincr('g_stat', 'none')
        else:
            if record.has_key('cookie'):
                cookie = record['cookie']
                crack.hashincr('g_stat', 'asigned')
            else:
                cookie = "None"
                crack.hashincr('g_stat', 'none')

        rep = {'ip': ip, 'cookie': cookie}

        libcommon.updateTaskCKReq(taskID)

        # logger.debug(rep)
        return jsonify(rep)

    @admin.expose('/submit_task', methods=['POST', 'GET'])
    def submit_task(self):
        global g_stat
        if request.method == 'POST':
            room_url = request.form.get('room_url')
            ck_url = request.form.get('ck_url')
            begin_time = request.form.get('begin_time')
            total_time = request.form.get('total_time')
            user_num = request.form.get('user_num')
            last_time_from = request.form.get('last_time_from')
            last_time_to = request.form.get('last_time_to')
            time_gap = request.form.get('time_gap')
            gap_num = request.form.get('gap_num')
            userIdStr = request.args.get('user')
            if userIdStr != None:
                userId = int(userIdStr)
            else:
                # default 0
                userId = 0
            logger.debug('room_url: %s, ck_url: %s', room_url, ck_url)
            logger.debug('begin_time: %s, total_time:%s', begin_time, total_time)
            logger.debug('user_num: %s', user_num)
            logger.debug('last_time_from:%s, last_time_to:%s', last_time_from, last_time_to)
            logger.debug('time_gap:%s, gap_num:%s', time_gap, gap_num)
            libcommon.writeTaskToRedis(userId, room_url, ck_url, begin_time, total_time, \
                                       user_num, last_time_from, last_time_to, time_gap, gap_num)
        return redirect(url_for('useradmin.index', user=userId))

    @admin.expose('/del_task', methods=['POST', 'GET'])
    def del_task(self):
        global g_stat
        if request.method == 'POST':
            task_id = request.form.get('task_id')
            userIdStr = request.args.get('user')
            if userIdStr != None:
                userId = int(userIdStr)
            else:
                # default 0
                userId = 0
            logger.debug('Task_id: %s', task_id)
            libcommon.delTaskFromRedis(userId, task_id)
        return redirect(url_for('useradmin.index', user=userId))

    @admin.expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        # render your view here
        return "Hello World"

# Create custom admin view
class UserTaskView(admin.BaseView):
    @admin.expose('/')
    def index(self):
        userIdStr = request.args.get('user')
        if userIdStr != None:
            userId = int(userIdStr)
        else:
            refer = request.referrer
            if refer == None:
                userId = 0
            else:
                para_str = urlparse.urlsplit(refer).query
                param = urlparse.parse_qs(para_str)
                logger.info(param)
                if param.has_key('user'):
                    para_dict = dict(user=param['user'][0])
                else:
                    para_dict = dict(user='0')
                logger.info(para_dict)
                url = urlAddPara(request.url, para_dict)
                return redirect(url)

        tasks = libcommon.getUserTaskList(userId)
        if not tasks:
            task = dict()
            task['room_url'] = 'https://www.douyu.com/657158'
            task['total_time'] = '30'
            task['user_num'] = '10000'
            task['last_time_from'] = 23
            task['last_time_to'] = 25
            task['time_gap'] = 6
            task['gap_num'] = 100
            task['task_id'] = 'user100001'
        else:
            task = tasks[0]
        return self.render('useradmin/usertask.html',task_records=task, user=userId)

    @admin.expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        # render your view here
        return "Hello"

userAdmin_bp = admin.Admin(name="用户控制台",index_view=UserHomeView(url='/useradmin',endpoint='useradmin'), template_mode='bootstrap3')
userAdmin_bp.add_view(UserTaskView(name='Task',endpoint='usertask'))

logger = gl.get_logger()
CONF   = gl.get_conf()
if gstat_init() != True:
    print('gstat init fail, exit!')
    os._exit(0)
#!/usr/bin/python
#-*- coding: UTF-8 -*-
# FileName : stradmin.py
# Author   : Shan
# DateTime : 2019/1/9
# SoftWare : PyCharm
from flask import Blueprint, abort,Flask, request, jsonify, render_template, redirect,url_for, send_file, send_from_directory
import flask_admin as admin
import os,json
from werkzeug.utils import secure_filename
import chardet
import time
import datetime
import urllib
import random
import globalvar as gl
import libdb as libdb
import libcommon as libcommon

global logger
global CONF

def now():
    return time.strftime("%m-%d %H:%M:%S", time.localtime())
g_stat = {"cycle":1, "pos":0,'could_use':0, "total":0, "asigned":0, "req":0, "rereq":0, "none":0, "boot_ts": now(), "reset_ts":now()}
g_records = []
g_cnt = {}


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

def TakeOutCksFromDB(cks_num):
    #先取出DB中表项数目
    condition = 'lastdate>%d' %(int(time.time()-3600*24*6))
    count = libdb.LibDB().query_count_by_condition(condition, CONF['database']['table'])
    if count != False:
        total = count[0]
    else:
        total = 0
    logger.debug(type(cks_num))
    cks_num = int(cks_num)
    if total >= cks_num:
        take_num = cks_num
    else:
        take_num = total

    logger.debug('准备从数据库取出cookies数量：%d', take_num)
    records = libdb.LibDB().query_num_by_condition(take_num,condition, CONF['database']['table'])
    return records

class MyHomeView(admin.AdminIndexView):
    @admin.expose('/')
    def index(self):
        global g_stat
        # 获取表项数量
        count = libdb.LibDB().query_count(CONF['database']['table'])
        if count != False:
            Digit = count[0]
        else:
            Digit = '0'
        g_stat['total'] = Digit
        timestamp = int(time.time() - 3600 * 24 * 6)
        conditions = 'lastdate >= %d' % (timestamp)
        count = libdb.LibDB().query_count_by_condition(conditions, CONF['database']['table'])
        if count != False:
            Digit = count[0]
        else:
            Digit = '0'
        g_stat['could_use'] = Digit
        return self.render('admin/index.html',  g_stat=g_stat)

    @admin.expose('/download', methods=['POST'])
    def download(self):
        # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
        directory = os.getcwd()  # 假设在当前目录
        if request.method == 'POST':
            # 按照日期下载文件
            date_range = request.form.get('date_range')
            if date_range != None:
                logger.info('date_range: %s', date_range)
                file = libcommon.getFileFromDBByDateRange(date_range)
                return send_from_directory(directory, file, as_attachment=True)

            # 按照id下载文件
            ck_id_from = request.form.get('ck_from')
            ck_id_to = request.form.get('ck_to')
            if ck_id_from == None or ck_id_to == None:
                return 'para error'
            logger.debug('ck_id_from: %s, ck_id_to: %s', ck_id_from, ck_id_to)
            file = libcommon.getFileFromDBByIndex(int(ck_id_from), int(ck_id_to))
            return send_from_directory(directory, file, as_attachment=True)
        else:
            # return redirect(url_for('stradmin.admin'))
            return redirect(url_for('admin.index'))

    @admin.expose('/upload', methods=['POST', 'GET'])
    def upload(self):
        """
        测试命令：curl -F "file=@/Users/liudeshan/work/studycase/script/flask/zb/2.csv" -X  "POST" http://localhost:8888//upload
        :return:
        """
        logger.debug('request.method:%s', request.method)
        logger.debug('request.files:%s', request.files['file'])
        if request.method == 'POST':
            # 保存文件
            ou = libcommon.writeFileToDB(request.files['file'])
            if ou['error'] == 0:
                return redirect(url_for('admin.index'))
            else:
                return json.dumps(ou)
        else:
            return redirect(url_for('admin.index'))

    #@admin.expose('/act_clear', methods=['POST', 'GET'])
    def act_clear(self):
        libdb.LibDB().del_db(' ', CONF['database']['table'])
        return redirect(url_for('admin.index'))

    #@admin.expose('/take_out_cks', methods=['POST', 'GET'])
    def take_out_cks(self):
        global g_stat
        if request.method == 'POST':
            cks_num = request.form.get('ck_num')
            # 读取cookie从数据库
            records = TakeOutCksFromDB(cks_num)
            if records != False and records != None:
                cookie_append(records)
        return redirect(url_for('stradmin.admin'))

    #@admin.expose('/take_cks_by_type', methods=['POST', 'GET'])
    def take_cks_by_type(self):
        global g_stat
        if request.method == 'POST':
            cks_type = request.form.get('take_ck_type')
            logger.debug('cks_type: %s', cks_type)
        return redirect(url_for('stradmin.admin'))

    #@admin.expose('/take_cks_by_id', methods=['POST', 'GET'])
    def take_cks_by_id(self):
        global g_stat
        if request.method == 'POST':
            ck_id_from = request.form.get('ck_id_min')
            ck_id_to = request.form.get('ck_id_max')
            logger.debug('ck_id_from: %s, ck_id_max: %s', ck_id_from, ck_id_to)
        return redirect(url_for('stradmin.admin'))

    @admin.expose('/admin1/', methods=['POST', 'GET'])
    def admin1(self):
        global g_stat
        # 获取表项数量
        count = libdb.LibDB().query_count(CONF['database']['table'])
        if count != False:
            Digit = count[0]
        else:
            Digit = '0'
        g_stat['total'] = Digit
        timestamp = int(time.time() - 3600 * 24 * 6)
        conditions = 'lastdate >= %d' % (timestamp)
        count = libdb.LibDB().query_count_by_condition(conditions, CONF['database']['table'])
        if count != False:
            Digit = count[0]
        else:
            Digit = '0'
        g_stat['could_use'] = Digit
        tasks = libcommon.getTaskList()
        return self.render("console.html", g_stat=g_stat, task_records=tasks)

# Create custom admin view
class AdminTaskView(admin.BaseView):
    @admin.expose('/')
    def index(self):
        tasks = libcommon.getTaskList()
        return self.render('admin/admintask.html',  task_records=tasks)

    @admin.expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        # render your view here
        return "Hello"

admin_bp = admin.Admin(name="CK控制台",index_view=MyHomeView(url='/admin',endpoint='admin'),template_mode='bootstrap3')
admin_bp.add_view(AdminTaskView(name='Task',endpoint='task'))

logger = gl.get_logger()
CONF   = gl.get_conf()
#!/usr/bin/python
#-*- coding: UTF-8 -*-
# FileName : stradmin.py
# Author   : Shan
# DateTime : 2019/1/9
# SoftWare : PyCharm
from flask import Blueprint, abort,Flask, request, jsonify, render_template, redirect,url_for, send_file, send_from_directory
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
g_stat = {"cycle":1, "pos":0,'take_out_cks':0, "total":0, "asigned":0, "req":0, "rereq":0, "none":0, "boot_ts": now(), "reset_ts":now()}
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

stradmin_bp = Blueprint('stradmin', __name__, template_folder='templates/html',static_folder="templates/html",static_url_path="")
@stradmin_bp.route('/act_clear', methods=['POST', 'GET'])
def act_clear():
    libdb.LibDB().del_db(' ', CONF['database']['table'])
    return redirect(url_for('stradmin.admin'))

@stradmin_bp.route('/take_out_cks', methods=['POST', 'GET'])
def take_out_cks():
    global g_stat
    if request.method == 'POST':
        cks_num  = request.form.get('ck_num')
        #读取cookie从数据库
        records = TakeOutCksFromDB(cks_num)
        if records != False and records != None:
            cookie_append(records)
    return redirect(url_for('stradmin.admin'))

@stradmin_bp.route('/take_cks_by_type', methods=['POST', 'GET'])
def take_cks_by_type():
    global g_stat
    if request.method == 'POST':
        cks_type  = request.form.get('take_ck_type')
        logger.debug('cks_type: %s',cks_type)
    return redirect(url_for('stradmin.admin'))

@stradmin_bp.route('/take_cks_by_id', methods=['POST', 'GET'])
def take_cks_by_id():
    global g_stat
    if request.method == 'POST':
        ck_id_from  = request.form.get('ck_id_min')
        ck_id_to    = request.form.get('ck_id_max')
        logger.debug('ck_id_from: %s, ck_id_max: %s',ck_id_from,ck_id_to)
    return redirect(url_for('stradmin.admin'))

@stradmin_bp.route('/download', methods=['POST'])
def download():
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    directory = os.getcwd()  # 假设在当前目录
    if request.method == 'POST':
        date_range = request.form.get('date_range')
        if date_range == None:
            return 'param error!!'
        logger.info('date_range: %s', date_range)
        file = libcommon.getFileFromDBByDateRange(date_range)
        return send_from_directory(directory, file, as_attachment=True)
    else:
        return redirect(url_for('stradmin.admin'))


@stradmin_bp.route('/', methods=['POST', 'GET'])
def admin():
    global g_stat
    #获取表项数量
    count = libdb.LibDB().query_count(CONF['database']['table'])
    if count != False:
        Digit = count[0]
    else:
        Digit = '0'
    g_stat['total'] = Digit
    tasks = libcommon.getTaskList()
    return render_template("console.html",  g_stat=g_stat,task_records=tasks)

logger = gl.get_logger()
CONF   = gl.get_conf()
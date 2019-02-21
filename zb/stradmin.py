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

global logger
global CONF

def now():
    return time.strftime("%m-%d %H:%M:%S", time.localtime())
DEF_PORT = 8888
CUR_PORT = DEF_PORT
DEF_FILE = "def.txt"
g_stat = {"cycle":1, "pos":0,'take_out_cks':0, "total":0, "asigned":0, "req":0, "rereq":0, "none":0, "boot_ts": now(), "reset_ts":now()}
g_records = []
g_cnt = {}

g_dy_room_id = "3326206"
g_dy_room_cnzz = "https://s19.cnzz.com/z_stat.php?id=1274369776&web_id=1274369776"

def save_records(path):
    file = open(path, "w")
    CNT = 0
    for record in g_records:
        file.write(record['cookie'] + "\n")
        CNT += 1
    file.close()
    print "%d records save to %s" %(CNT, path)

def gstat_clear():
    g_stat['pos'] = 0
    g_stat['asigned'] = 0
    g_stat['req'] = 0
    g_stat['rereq'] = 0
    g_stat['none'] = 0
    g_stat['reset_ts'] = now()

def clear_records():
    global g_records, g_stat
    CNT = 0
    g_records = []
    # g_stat = {"cycle":1, "total":0, "asigned":0, "req":0, "rereq":0, "boot_ts": now(), "reset_ts":""
    g_stat['take_out_cks'] = 0
    gstat_clear()
    logger.debug("all records clean!!.")

def def_file_get():
    path = "download/"+"def_%d.txt" %(CUR_PORT)
    return path

def ip_loc(ip):
    if ip == "127.0.0.1":
        return "内网IP"
    url = "http://ip.taobao.com/service/getIpInfo.php?ip="
    data = urllib.urlopen(url + ip).read()
    try:
        datadict=json.loads(data)
        for oneinfo in datadict:
            if "code" == oneinfo:
                if datadict[oneinfo] == 0:
                    return datadict["data"]["country"] + datadict["data"]["region"] + datadict["data"]["city"] + datadict["data"]["isp"]
    except:
        return "Fail"

def update_loc():
    global g_records
    for records in g_records:
        if records['ip'] != "":
            if records['loc'] == "" or records['loc'] == "Fail":
                records['loc'] = ip_loc(records['ip'])

def reset_records():
    global g_records, g_stat
    CNT = 0
    for record in g_records:
        if record['ip'] != "":
            record['ip']  = ""
            record['loc']  = ""
            record['fts']  = ""
            #record['cts'] = now()
            CNT += 1
    gstat_clear()
    print "%d records reset." %(CNT)
    return CNT

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

def cookie_del_by_date(dstr):
    global g_records, g_stat
    tcnt = 0
    dcnt = 0
    for i in range(len(g_records) - 1, -1, -1):

        record = g_records[i]

        cts  = record['cts']
        pos = cts.find(dstr)

        if  pos >= 0:
            g_records.remove(record)
            g_stat['take_out_cks'] -= 1
            dcnt += 1

        tcnt += 1
    print "%d recoreds deleted in %d, dstr=%s" %(dcnt, tcnt, dstr)
    return dcnt


stradmin_bp = Blueprint('stradmin', __name__, template_folder='templates/html',static_folder="templates/html",static_url_path="")


@stradmin_bp.route('/act_loc', methods=['POST', 'GET'])
def act_loc():
    update_loc()
    return redirect(url_for('stradmin.admin'))

@stradmin_bp.route('/act_random', methods=['POST', 'GET'])
def act_random():
    random.shuffle(g_records)
    return redirect(url_for('stradmin.admin'))

@stradmin_bp.route('/act_del', methods=['POST', 'GET'])
def act_del():
    dstr = request.form['date']

    cookie_del_by_date(dstr)

    return redirect(url_for('stradmin.admin'))

@stradmin_bp.route('/act_clear', methods=['POST', 'GET'])
def act_clear():
    CNT = clear_records()

    return redirect(url_for('stradmin.admin'))

@stradmin_bp.route('/act_reset', methods=['POST', 'GET'])
def act_reset():
    CNT = reset_records()

    return redirect(url_for('stradmin.admin'))

@stradmin_bp.route('/act_save', methods=['POST', 'GET'])
def act_save():
    file = def_file_get()
    CNT = save_records(file)

    return redirect(url_for('stradmin.admin'))

@stradmin_bp.route("/act_download", methods=['POST', 'GET'])
def download():
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    directory = os.getcwd()  # 假设在当前目录
    file = def_file_get()
    return send_from_directory(directory, file, as_attachment=True)

@stradmin_bp.route('/set_room_cnzz', methods=['POST', 'GET'])
def set_room_cnzz():
    global g_dy_room_cnzz
    if request.method == 'POST':
        room_cnzz = request.form['room_cnzz']
        g_dy_room_cnzz = room_cnzz
    return redirect(url_for('stradmin.admin'))

@stradmin_bp.route('/set_room_id', methods=['POST', 'GET'])
def set_room_id():
    global g_dy_room_id
    if request.method == 'POST':
        room_id = request.form.get('room_id')
        g_dy_room_id = room_id
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

@stradmin_bp.route('/', methods=['POST', 'GET'])
def admin():
    global g_records, g_stat, g_cnt
    tarry  = []
    darry = []
    #获取表项数量
    count = libdb.LibDB().query_count(CONF['database']['table'])
    if count != False:
        Digit = count[0]
    else:
        Digit = '0'
    g_stat['total'] = Digit
    st = datetime.datetime.now() + datetime.timedelta(minutes=-120)
    for i in range(0, 121):
        sn = st + datetime.timedelta(minutes=i)
        ts = sn.strftime("%H:%M")
        tarry.append(ts)
        if g_cnt.has_key(ts):
            darry.append(g_cnt[ts])
        else:
            darry.append(0)
    return render_template("index.html",  g_stat=g_stat)
    #return render_template("console.html", g_records=g_records, g_stat=g_stat, tarry=tarry, darry=darry)

@stradmin_bp.route('/room', methods=['POST', 'GET'])
def room():

    global g_dy_room_id
    global g_dy_room_cnzz

    return render_template("jump.html", g_dy_room_id=g_dy_room_id, g_dy_room_cnzz=g_dy_room_cnzz)


def get_min():
    str = time.strftime("%H:%M", time.localtime())
    return str
def g_cnt_inc(m):
    global g_cnt

    if g_cnt.has_key(m):
        g_cnt[m] = g_cnt[m] + 1
    else:
        g_cnt[m] = 1

    #print "g_cnt: ", g_cnt

def fetch_record(ip):
    global g_records, g_stat
    if g_stat['pos'] < g_stat['take_out_cks']:
        g_records[g_stat['pos']]['ip'] = ip
        g_records[g_stat['pos']]['loc'] = ""
        g_records[g_stat['pos']]['fts'] = now()
        g_records[g_stat['pos']]['cnt'] +=1
        record = g_records[g_stat['pos']]
        g_stat['pos'] +=1
        return record

    return None

def get_record(ip):
    global g_records;
    for record in g_records:
        #logger.debug("record['ip']:%s, ip:%s", record['ip'], ip)
        if record['ip'] == ip:
            return record

    return None

@stradmin_bp.route('/cookie',methods=['GET'])
def cookie():
    m = get_min()
    g_cnt_inc(m)
    ip = request.remote_addr
    g_stat['req'] += 1
    record = get_record(ip)
    if record == None:
        record = fetch_record(ip)
    else:
        g_stat['rereq'] += 1

    if record == None:
        cookie = "None"
        g_stat['none'] += 1
    else:
        cookie = record['cookie']
        g_stat['asigned'] += 1

    rep = {'ip':ip, 'cookie': cookie}
    #logger.debug(rep)
    return jsonify(rep)


logger = gl.get_logger()
CONF   = gl.get_conf()
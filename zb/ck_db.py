#!/usr/bin/env python
# -*- coding:utf-8 -*-
#

import sys
import re
import os
import time
import datetime
import logging
import json
import socket

from flask import Flask, request, jsonify, render_template, redirect,url_for, send_file, send_from_directory
from flask_request_params import bind_request_params
import urllib
import random
import chardet
import pymysql
import base64

from werkzeug.utils import secure_filename
from collections import OrderedDict


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def now():
    str = time.strftime("%m-%d %H:%M:%S", time.localtime()) 
    return str

def get_min():
    str = time.strftime("%H:%M", time.localtime()) 
    return str

DEF_PORT = 9240 
CUR_PORT = DEF_PORT
DEF_FILE = "def.txt"
g_stat = {"cycle":1, "pos":0, "total":0, "asigned":0, "req":0, "rereq":0, "none":0, "boot_ts": now(), "reset_ts":now()}
g_records = []
g_cnt = {}

g_sql_ck_if = ""
g_dy_room_id = "3326206"

app = Flask(__name__, template_folder="",static_folder="",static_url_path="")

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
#app.config['DEBUG'] = True

@app.route('/')
def index():
    return 'Hello'

def def_file_get():
    path = "def_%d.csv" %(CUR_PORT) 
    return path

def  ip_loc(ip):
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

def g_cnt_inc(m):
    global g_cnt
    
    if g_cnt.has_key(m):
        g_cnt[m] = g_cnt[m] + 1
    else:
        g_cnt[m] = 1

    #print "g_cnt: ", g_cnt

def fetch_record(ip):
    global g_records, g_stat

    '''
    for record in g_records:
        #print "ip %s record[\'ip\'] %s" %(ip, record['ip'])
        if record['ip'] == "":
            record['ip'] = ip
            #record['loc'] = ip_loc(ip)
            record['loc'] = ""
            record['fts'] = now()
            record['cnt'] = 0
            #g_stat['asigned'] += 1
            return record
    '''

    #print "g_stat[pos]=%d g_stat[total]=%d" %(g_stat['pos'], g_stat['total'])

    if g_stat['pos'] < g_stat['total']:
        record = g_records[g_stat['pos']]
        record['ip'] = ip
        record['loc'] = ""
        record['fts'] = now()
        record['cnt'] = 0
        g_stat['pos'] += 1
        return record

    return None

def cycle_set(cycle):
    global g_records, g_stat
    g_stat['cycle'] = cycle



def get_record(ip):
    global g_records;

    for record in g_records:
        if record['ip'] == ip:
            return record

    return None



def save_records(path):
    file = open(path, "w")
    CNT = 0
    file.write("ID,名称,密码,属性,等级,绑定状态,有效状态,Cookies,更新时间,注册时间\n")
    for record in g_records:
        rec_id = str(record['id'])
        file.write(rec_id + ",") 
        file.write(record['nn'] + ",") 
        file.write(record['pwd'] + ",") 
        file.write(record['attr'] + ",") 
        rec_level = str(record['level'])
        file.write(rec_level + ",") 
        file.write(record['bind'] + ",") 
        file.write(record['vaild'] + ",") 
        file.write(record['cookie'] + ",") 
        file.write(record['update_time'] + ",") 
        file.write(record['signup_time'] + "\n") 
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
    g_stat['total'] = 0
    gstat_clear()

    print "all records clean!!."

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
            g_stat['total'] -= 1
            dcnt += 1

        #print "tcnt(%d) dcnt(%d) POS(%d)  cts(%s)  dstr(%s)" %(tcnt, dcnt, pos, cts, dstr)
        
        tcnt += 1
    print "%d recoreds deleted in %d, dstr=%s" %(dcnt, tcnt, dstr)
    return dcnt

@app.route('/reset',methods=['GET'])
def reset():
    CNT = reset_records()

    ip = request.remote_addr

    rep = {'ip':ip, 'CNT': CNT}

    #print "rep: ", rep

    return jsonify(rep)

#g_stat = {"cycle":1, "total":0, "asigned":0, "req":0, "rereq":0, "none":0, "boot_ts": now(), "reset_ts":now()}
@app.route('/cookie',methods=['GET'])
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
        record['cnt'] += 1
        g_stat['asigned'] += 1
        
    rep = {'ip':ip, 'cookie': cookie}

    #print "rep: ", rep

    return jsonify(rep)


def connect_ck_db():
    return pymysql.connect(host='127.0.0.1',
                           port=3306,
                           user='root',
                           password='STR@1q2w3e',
                           database='DYDB',
                           charset='utf8')
                           

def sql_append(rec, key, type,  fileds):
    try:
        value = rec[key]
        if type == 'i':
            append = {'key':'%s, ' % key,    'value':"%s, " % value}
        else:
            append = {'key':'%s, ' % key,    'value':"'%s', " % value}
    except:
        append = {'key':'', 'value':''}

    fileds['key'] += append['key']
    fileds['value'] += append['value']
    return fileds

def mysql_insert_rec(tab_name, rec):

    cong = connect_ck_db()
    curg = cong.cursor()
    fileds = {'key': '', 'value': ''}

    fileds = sql_append(rec, 'nn', 'c', fileds)
    fileds = sql_append(rec, 'pwd', 'c', fileds)
    fileds = sql_append(rec, 'attr', 'c', fileds)
    fileds = sql_append(rec, 'level', 'i', fileds)
    fileds = sql_append(rec, 'bind', 'c', fileds)
    fileds = sql_append(rec, 'vaild', 'c', fileds)
    fileds = sql_append(rec, 'cookie', 'c', fileds)
    fileds = sql_append(rec, 'signup_date', 'c', fileds)
    fileds = sql_append(rec, 'signup_time', 'c', fileds)
    fileds = sql_append(rec, 'update_date', 'c', fileds)
    fileds = sql_append(rec, 'update_time', 'c', fileds)


    fileds['key'] = fileds['key'][0:len(fileds['key']) - 2]
    fileds['value'] = fileds['value'][0:len(fileds['value']) - 2]

    sql_str = 'INSERT INTO `%s` ( %s ) VALUES( %s );' % (
        tab_name, fileds['key'], fileds['value'])

    try:
     	curg.execute(sql_str)
     	cong.commit();
    except:
        logging.exception('Insert operation error')
        raise
    finally:
        curg.close()
        cong.close()

    return 0


def mysql_update_rec(tab_name, setval, sql_if):

    cong = connect_ck_db()
    curg = cong.cursor()

    sql_str = 'UPDATE %s set %s %s;' %(tab_name, setval, sql_if)

    try:
     	curg.execute(sql_str)
     	cong.commit();
    except:
        logging.exception('Insert operation error')
        raise
    finally:
        curg.close()
        cong.close()

    return 0


def mysql_del_rec(tab_name, sql_if):
    cong = connect_ck_db()
    curg = cong.cursor()
    
    sql_str = 'DELETE FROM %s %s;' %(tab_name, sql_if)

    try:
     	curg.execute(sql_str)
     	cong.commit();
    except:
        logging.exception('Delete operation error')
        raise
    finally:
        curg.close()
        cong.close()

    return 0
    

def mysql_query_rec(tab_name, option):
    cong = connect_ck_db()
    curg = cong.cursor()
	
    sql_str = 'SELECT * FROM  %s %s;' %(tab_name, option)
    print "%s" %(sql_str)
    try:
     	curg.execute(sql_str)
        sql_rows = curg.fetchall()
       # print "%d" %(len(sql_rows))
       # print "%d" %(len(sql_rows[0]))
    except:
        logging.exception('query operation error')
        raise
    finally:
        curg.close()
        cong.close()
        return sql_rows

def cookie_append(records):
    global g_records, g_stat

    g_stat['total'] = 0
    for record in records:
        record['idx'] = len(g_records)
        g_records.append(record)
        g_stat['total'] += 1

def cookie_csv_parse(line):
    row = line.split(',')

    if len(row) < 8:
        return None

    if row[0] == "" or row[0] == "ID":
        return None

    # ID,名称,密码,属性,等级,绑定状态,有效状态,Cookies
    record  = {}
    record['nn']     = row[1].replace(' ', '')
    record['pwd']    = row[2].replace(' ', '')
    record['attr']   = row[3].replace(' ', '')
    record['level']  = row[4].replace(' ', '')
    record['bind']   = row[5].replace(' ', '')
    record['vaild']  = row[6].replace(' ', '')
    record['cookie'] = row[7].replace(' ', '')
    record['update_date'] = row[8].replace(' ', '')
    record['update_time'] = row[9].replace(' ', '')
    record['signup_date'] = row[10].replace(' ', '')
    record['signup_time'] = row[11].replace(' ', '')

    return record


def read_sql_data(tab_name, sql_if):
    sql_records =[]
    ck_rows = mysql_query_rec(tab_name, sql_if)
    for idx in range(len(ck_rows)):
        rcd = {}
        rcd['id']     = ck_rows[idx][0]
        rcd['nn']     = ck_rows[idx][1]
        rcd['pwd']    = ck_rows[idx][2]
        rcd['attr']   = ck_rows[idx][3]
        rcd['level']  = ck_rows[idx][4]
        rcd['bind']   = ck_rows[idx][5]
        rcd['vaild']  = ck_rows[idx][6]
        rcd['cookie'] = ck_rows[idx][7]
        rcd['signup_date'] = ck_rows[idx][8]
        rcd['signup_time'] = ck_rows[idx][9]
        rcd['update_date'] = ck_rows[idx][10]
        rcd['update_time'] = ck_rows[idx][11]
                
        rcd['seq'] = idx
        rcd['cnt'] = 0
        rcd['ip']  = ""
        rcd['cts'] = now()
        rcd['fts'] = ""

        sql_records.append(rcd)
    return sql_records




def cookie_load(path):
    FILE = open(path, 'rb')
    records =[]
    sql_records =[]

    # print "%d entires in g_records" %(len(g_records))

    mysql_del_rec("cktb", "")
    seq = 0
    for line in FILE:
        line = line.strip('\n')
        cdet = chardet.detect(line)
        #print 'cdet: ', cdet
        if cdet['encoding'].lower().find("utf-8") == 0 :
            u8str = line
            #print "u8str: ", u8str
        else:
            u8str = line.decode('GBK').encode("utf8")
            #print "line: ", line

        record = cookie_csv_parse(u8str)

        if record == None:
            continue

        mysql_insert_rec("cktb", record)
   
        record['seq'] = seq
        record['cnt'] = 0
        record['ip']  = ""
        record['cts'] = now()
        record['fts'] = ""

        records.append(record)
        seq += 1
     
  
    print "%d cookies loaded from %s!" %(len(records), path)

    return sql_records

@app.route('/act_del', methods=['POST', 'GET'])
def act_del():
    dstr = request.form['date']

    cookie_del_by_date(dstr)

    return redirect(url_for('console'))

@app.route('/act_cycle', methods=['POST', 'GET'])
def act_cycle():
    cycstr = request.form['cycle']

    cycle = int(cycstr)

    cycle_set(cycle)

    return redirect(url_for('console'))

@app.route('/act_clear', methods=['POST', 'GET'])
def act_clear():
    CNT = clear_records()

    return redirect(url_for('console'))

@app.route('/act_reset', methods=['POST', 'GET'])
def act_reset():
    CNT = reset_records()

    return redirect(url_for('console'))

@app.route('/act_save', methods=['POST', 'GET'])
def act_save():
    file = def_file_get()
    CNT = save_records(file)

    return redirect(url_for('account'))

@app.route("/act_download", methods=['POST', 'GET'])
def download():
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    directory = os.getcwd()  # 假设在当前目录

    file = def_file_get()
    return send_from_directory(directory, file, as_attachment=True)

@app.route('/act_upload', methods=['POST', 'GET'])
def act_upload():
    if request.method == 'POST':
        f = request.files['file']
        basepath = os.path.dirname(__file__)  # 当前文件所在路径
        upload_path = os.path.join(basepath, 'uploads',secure_filename(f.filename))  #注意：没有的文件夹一定要先创建，不然会提示没有该路径
        f.save(upload_path)
        print "upload_path: ", upload_path
        records = cookie_load(upload_path)
        cookie_append(records)
        return redirect(url_for('account'))

@app.route('/act_loc', methods=['POST', 'GET'])
def act_loc():
    update_loc()

    return redirect(url_for('console'))

@app.route('/console', methods=['POST', 'GET'])
def console():

    global g_records, g_stat, g_cnt

    #print "%d entires in g_records" %(len(g_records))
    #update_loc()

    tarry  = []
    darry = []


    st = datetime.datetime.now() + datetime.timedelta(minutes=-120)

    for i in range(0, 121):
        sn = st + datetime.timedelta(minutes=i)
        ts = sn.strftime("%H:%M")
        tarry.append(ts)

        if g_cnt.has_key(ts):
            darry.append(g_cnt[ts])
        else:
            darry.append(0)

    sql_records= read_sql_data("cktb", g_sql_ck_if)
    cookie_append(sql_records)
    return render_template("ck_db.html", g_records=g_records, g_stat=g_stat, tarry=tarry, darry=darry)




@app.route('/act_random', methods=['POST', 'GET'])
def act_random():
    random.shuffle(g_records)
    return redirect(url_for('console'))


@app.route('/room', methods=['POST', 'GET'])
def room():

    global g_dy_room_id

    return render_template("jump.html", g_dy_room_id=g_dy_room_id)



@app.route('/set_room_id', methods=['POST', 'GET'])
def set_room_id():

    global g_dy_room_id

    if request.method == 'POST':
        room_id = request.form.get('room_id')
        g_dy_room_id = room_id

    return redirect(url_for('account'))
    


@app.route('/act_select_rec', methods=['POST', 'GET'])
def act_select_rec():

    global g_sql_ck_if

    if request.method == 'POST':
        nickname = request.form.get('nickname')
        if (nickname == ""):
            return redirect(url_for('account'))
        sql_if = "where nn='%s'" %(nickname)
        g_sql_ck_if = sql_if
        return redirect(url_for('account'))



        

@app.route('/act_select_sql', methods=['POST', 'GET'])
def act_select_sql():

    global g_sql_ck_if

    if request.method == 'POST':
        #print "%s." %(request.form.get('level_min'))
        #print "%s." %(request.form.get('level_max'))
        #print "%s." %(request.form.get('attr'))
        #print "%s." %(request.form.get('valid'))
        
        level_min = request.form.get('level_min')
        level_max = request.form.get('level_max')
        ck_attr = request.form.get('attr')
        ck_valid = request.form.get('valid')

        if (ck_attr is None) and (ck_valid is None) and (level_min == "") and (level_max == ""):
            return redirect(url_for('account'))
        if level_min > level_max:
            return redirect(url_for('account'))
          
        if (ck_attr is None) and (ck_valid is None) and (level_min < level_max):
            sql_if = "where level between %s and %s" %(level_min, level_max)
        elif (ck_attr is None) and (ck_valid is None) and (level_min == level_max):
            sql_if = "where level=%s" %(level_min)
        elif (level_min == "") and (ck_valid is None):
            sql_if = "where attr='%s'" %(ck_attr)
        elif (level_min == "") and (ck_attr is None):
            sql_if = "where vaild='%s'" %(ck_valid)
        elif level_min == "":
            sql_if = "where attr='%s' and vaild='%s'" %(ck_attr, ck_valid)
        elif (ck_valid is None) and (level_min < level_max):
            sql_if = "where level between %s and %s and attr='%s'" %(level_min, level_max, ck_attr)
        elif (ck_attr is None) and (level_min < level_max):
            sql_if = "where level between %s and %s and vaild='%s'" %(level_min, level_max, ck_valid)
        elif (ck_valid is None) and (level_min == level_max):
            sql_if = "where level=%s and attr='%s'" %(level_min, ck_attr)
        elif (ck_attr is None) and (level_min == level_max):
            sql_if = "where level=%s and vaild='%s'" %(level_min, ck_valid)
        elif (level_min < level_max):
            sql_if = "where level between %s and %s and attr='%s' and vaild='%s'" %(level_min, level_max, ck_attr, ck_valid)
        elif (level_min == level_max):
            sql_if = "where level=%s and attr='%s' and vaild='%s'" %(level_min, ck_attr, ck_valid)
        else:
            return redirect(url_for('account'))
        
        print "%s" %(sql_if)

        g_sql_ck_if = sql_if
    return redirect(url_for('account'))

@app.route('/act_cancel_filter', methods=['POST', 'GET'])
def act_cancel_filter():

    global g_sql_ck_if

    g_sql_ck_if = ""
    return redirect(url_for('account'))

@app.route('/insert_dy', methods=['POST','GET'])
def insert_dy():
    
    if request.method == 'GET':
        #print "%s." %(request.form.get('valid'))
        
        rcd = {}
        rcd['nn']     = request.args.get('nn')
        rcd['pwd']    = request.args.get('pwd')
        rcd['cookie'] = base64.b64decode(request.args.get('ck'))
        rcd['signup_date'] = datetime.datetime.now().strftime('%Y-%m-%d')
        rcd['signup_time'] = datetime.datetime.now().strftime('%H:%M:%S')
        sql_if = "where nn='%s'" %(rcd['nn'])
        ck_rows = mysql_query_rec("cktb", sql_if)
        #print "re is %d" %(len(ck_rows))
        if len(ck_rows) == 0:
            mysql_insert_rec("cktb", rcd)
        else:
            return "fail"
        return "Success"
        
@app.route('/update_dy', methods=['POST','GET'])
def update_dy():
    
    if request.method == 'GET':
        #print "%s." %(request.form.get('valid'))
        
        rcd = {}
        nn     = request.args.get('nn')
        cookie = base64.b64decode(request.args.get('ck'))
        up_date = datetime.datetime.now().strftime('%Y-%m-%d')
        up_time = datetime.datetime.now().strftime('%H:%M:%S')
        sql_if = "where nn='%s'" %(nn)
        ck_rows = mysql_query_rec("cktb", sql_if)
        #print "re is %d" %(len(ck_rows))
        if len(ck_rows) == 1:
            setval = "cookie='%s',update_date='%s',update_time='%s'" %(cookie, up_date, up_time)
            mysql_update_rec("cktb", setval, sql_if)
        else:
            return "fail"
        return "Suceess"


@app.route('/query_dy', methods=['POST','GET'])
def query_dy():
    
    if request.method == 'GET':
        #print "%s." %(request.form.get('valid'))
        
        query_date = request.args.get('date')
        sql_if = "where signup_date='%s'" %(query_date)
        sql_if_limit = "where signup_date='%s' limit 1" %(query_date)
        ck_rows = mysql_query_rec("cktb", sql_if)
        ck_row = mysql_query_rec("cktb", sql_if_limit)
        if len(ck_row) != 1:
            return "fail"
        nn = ck_row[0][1]
        pwd = ck_row[0][2]
        re_sum = len(ck_rows)
        #print "%s" %(nn) 
        rep = {'total':re_sum, 'username':nn, 'pwd':pwd}

        return jsonify(rep)


@app.route('/account', methods=['POST', 'GET'])
def account():

    global g_records, g_stat, g_cnt, g_sql_ck_if

    g_records = []
    sql_records= read_sql_data("cktb", g_sql_ck_if)
    cookie_append(sql_records)
    return render_template("ck_db.html", g_records=g_records, g_stat=g_stat)



if __name__ == '__main__':

    #path = DEF_FILE

    #global CUR_PORT

    if len(sys.argv) > 1:
        CUR_PORT = sys.argv[1]

    #records = cookie_load(path)
    #cookie_append(records)
    app.run(host='0.0.0.0', port=CUR_PORT)

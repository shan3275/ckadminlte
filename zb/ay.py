#!/usr/bin/env python
# -*- coding:utf-8 -*-
#

import sys
import re
import os
import time

from flask import Flask, request, jsonify, render_template, redirect,url_for
import urllib
import random

from werkzeug.utils import secure_filename

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def now():
    str = time.strftime("%m-%d %H:%M:%S", time.localtime()) 
    return str

g_stat = {"cycle":1, "total":0, "asigned":0, "req":0, "rereq":0, "boot_ts": now(), "clear_ts":""}
g_records = []

app = Flask(__name__, template_folder="",static_folder="",static_url_path="")

@app.route('/')
def index():
    return 'Hello'

def fetch_record(ip):
    global g_records, g_stat

    for record in g_records:
        print "ip %s record[\'ip\'] %s" %(ip, record['ip'])
        if record['ip'] == "":
            record['ip'] = ip
            record['fts'] = now()
            g_stat['asigned'] += 1
            return record

    return None

def cycle_set(cycle):
    global g_records, g_stat
    g_stat['cycle'] = cycle

def get_record(ip):
    global g_records, g_stat

    for record in g_records:
        if record['ip'] == ip:
            g_stat['rereq'] += 1
            g_stat['req'] += 1
            return record

    record = None

    if g_stat['req'] % g_stat['cycle'] == 0:
        record = fetch_record(ip)

    g_stat['req'] += 1
    return record

def clear_records():
    global g_records, g_stat
    cnt = 0
    for record in g_records:
        if record['ip'] != "":
            record['ip']  = ""
            record['fts']  = ""
            #record['cts'] = now()
        
            cnt += 1

    g_stat['asigned'] = 0
    g_stat['req'] = 0
    g_stat['clear_ts'] = now()
    return cnt

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

@app.route('/clear',methods=['GET'])
def clear():
    cnt = clear_records()

    ip = request.remote_addr

    rep = {'ip':ip, 'cnt': cnt}

    print "rep: ", rep

    return jsonify(rep)


@app.route('/cookie',methods=['GET'])
def cookie():
    ip = request.remote_addr
    print "ip, ", ip
    record = get_record(ip)
    if record == None:
        cookie = "None"
    else:
        cookie = record['cookie']

    rep = {'ip':ip, 'cookie': cookie}

    print "rep: ", rep

    return jsonify(rep)

def cookie_append(records):
    global g_records, g_stat

    for record in records:
        record['idx'] = len(g_records)
        g_records.append(record)
        g_stat['total'] += 1

def cookie_load(path):
    FILE = open(path, 'rb')
    records =[]

    print "%d entires in g_records" %(len(g_records))

    idx = 0
    for line in FILE:
        cookie = line.strip('\n')
        nnv  =re.findall('acf_nickname=(.*); acf_own_room',cookie)
        uidv =re.findall('acf_uid=(.*); acf_username',cookie)

        if len(nnv) <= 0 or len(uidv) <= 0:
            continue

        nn  = urllib.unquote(nnv[0])
        uid = uidv[0]
        
        nn = nn.decode('utf-8').encode('utf-8')
   
        record = {'idx':0, 'ip':"", 'cookie':cookie, 'uid':uid, 'nn':nn, 'cts': now(), 'fts':""}
        records.append(record)
        idx += 1

    random.shuffle(records)

    #for record in g_records:
    #   print "uid %d cookie: %s" %(record['uid'], record['cookie'])
    
    print "%d cookies loaded!" %(len(records))

    return records

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
    cnt = clear_records()

    return redirect(url_for('console'))


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
        return redirect(url_for('console'))

@app.route('/room', methods=['POST', 'GET'])
def console():

    global g_records, g_stat

    return render_template("jump.html", g_records=g_records, g_stat=g_stat)


if __name__ == '__main__':
    records = cookie_load(sys.argv[1])
    cookie_append(records)
    app.run(host='0.0.0.0', port=7777)

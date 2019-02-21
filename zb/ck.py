#!/usr/bin/env python
# -*- coding:utf-8 -*-
#

import sys
import re
import os
import time

from flask import Flask, request, jsonify, render_template, redirect,url_for, send_file, send_from_directory
import urllib
import random

from werkzeug.utils import secure_filename

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def now():
    str = time.strftime("%m-%d %H:%M:%S", time.localtime()) 
    return str
DEF_FILE = "def.txt"
g_stat = {"cycle":1, "total":0, "asigned":0, "req":0, "rereq":0, "boot_ts": now(), "reset_ts":now()}
g_records = []

g_room_id = "657158"

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

def save_records(path):
    file = open(path, "w")
    CNT = 0
    for record in g_records:
        file.write(record['cookie'] + "\n") 
        CNT += 1

    file.close()

    print "%d records save to %s" %(CNT, path)


def clear_records():
    global g_records, g_stat
    CNT = 0
    g_records = []
   
    # g_stat = {"cycle":1, "total":0, "asigned":0, "req":0, "rereq":0, "boot_ts": now(), "reset_ts":""
    g_stat['total'] = 0
    g_stat['asigned'] = 0
    g_stat['req'] = 0
    g_stat['rereq'] = 0
    g_stat['reset_ts'] = now()

    print "all records clean!!."

def reset_records():
    global g_records, g_stat
    CNT = 0
    for record in g_records:
        if record['ip'] != "":
            record['ip']  = ""
            record['fts']  = ""
            #record['cts'] = now()
        
            CNT += 1

    g_stat['asigned'] = 0
    g_stat['req'] = 0
    g_stat['reset_ts'] = now()

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

    # print "%d entires in g_records" %(len(g_records))

    idx = 0
    for line in FILE:
        cookie = line.strip('\n')
        if cookie == "":
            continue

        nnv  = re.findall('acf_nickname=(.*); acf_own_room',cookie)
        uidv = re.findall('acf_uid=(.*); acf_username',cookie)

        #print "%d: nnv %s uidv %s" %(idx, nnv, uidv)
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
    
    print "%d cookies loaded from %s!" %(len(records), path)

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
    CNT = clear_records()

    return redirect(url_for('console'))

@app.route('/act_reset', methods=['POST', 'GET'])
def act_reset():
    CNT = reset_records()

    return redirect(url_for('console'))

@app.route('/act_save', methods=['POST', 'GET'])
def act_save():
    CNT = save_records(DEF_FILE)

    return redirect(url_for('console'))

@app.route('/act_random', methods=['POST', 'GET'])
def act_random():
    random.shuffle(g_records)
    return redirect(url_for('console'))

@app.route("/act_download", methods=['POST', 'GET'])
def download():
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    directory = os.getcwd()  # 假设在当前目录
    return send_from_directory(directory, DEF_FILE, as_attachment=True)

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

@app.route('/console', methods=['POST', 'GET'])
def console():

    global g_records, g_stat

    print "%d entires in g_records" %(len(g_records))

    return render_template("console.html", g_records=g_records, g_stat=g_stat)

@app.route('/room', methods=['POST', 'GET'])
def room():

    global g_room_id

    return render_template("rid.html", g_room_id=g_room_id)

@app.route('/data', methods=['POST', 'GET'])
def data():

    return render_template("data.html", g_records=g_records, g_stat=g_stat)

if __name__ == '__main__':

    path = DEF_FILE

    if len(sys.argv) > 1:
        path = sys.argv[1]

    records = cookie_load(path)
    cookie_append(records)
    app.run(host='0.0.0.0', port=9999)

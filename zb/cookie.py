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
import urllib
import random
import chardet

from werkzeug.utils import secure_filename

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def now():
    str = time.strftime("%m-%d %H:%M:%S", time.localtime()) 
    return str

def get_min():
    str = time.strftime("%H:%M", time.localtime()) 
    return str

DEF_PORT = 8000
CUR_PORT = DEF_PORT
DEF_FILE = "def.txt"
g_stat = {"cycle":1, "pos":0, "total":0, "asigned":0, "req":0, "rereq":0, "none":0, "boot_ts": now(), "reset_ts":now()}
g_records = []
g_cnt = {}

g_dy_room_id = "3326206"
g_dy_room_cnzz = "https://s19.cnzz.com/z_stat.php?id=1274369776&web_id=1274369776"

app = Flask(__name__, template_folder="",static_folder="",static_url_path="")

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
#app.config['DEBUG'] = True

@app.route('/')
def index():
    return 'Hello'

def def_file_get():
    path = "def_%d.txt" %(CUR_PORT) 
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

def cookie_append(records):
    global g_records, g_stat

    for record in records:
        record['idx'] = len(g_records)
        g_records.append(record)
        g_stat['total'] += 1

def cookie_csv_parse(line):
    row = line.split(',')

    #print "row(%d): %s" %(len(row), row)
    if len(row) < 8:
        return None

    if row[0] == "" or row[0] == "ID":
        return None

    # ID,名称,密码,属性,等级,绑定状态,有效状态,Cookies
    record  = {}
    record['id']     = row[0]
    record['nn']     = row[1]
    record['pwd']    = row[2]
    record['attr']   = row[3]
    record['level']  = row[4]
    record['bind']   = row[5]
    record['vaild']  = row[6]
    record['cookie'] = row[7]

    return record

def cookie_load(path):
    FILE = open(path, 'rb')
    records =[]

    # print "%d entires in g_records" %(len(g_records))

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

        #nnv  = re.findall('acf_nickname=(.*); acf_own_room',cookie)
        #uidv = re.findall('acf_uid=(.*); acf_username',cookie)

        #print "%d: nnv %s uidv %s" %(idx, nnv, uidv)
        #if len(nnv) <= 0 or len(uidv) <= 0:
        #    continue

        #nn  = urllib.unquote(nnv[0])
        #uid = uidv[0]
        
        #nn = nn.decode('utf-8').encode('utf-8')
   
        record['seq'] = seq
        record['cnt'] = 0
        record['ip']  = ""
        record['cts'] = now()
        record['fts'] = ""

        records.append(record)
        seq += 1

    #random.shuffle(records)

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
    file = def_file_get()
    CNT = save_records(file)

    return redirect(url_for('console'))

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
        return redirect(url_for('console'))

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

    return render_template("console.html", g_records=g_records, g_stat=g_stat, tarry=tarry, darry=darry)


@app.route('/room', methods=['POST', 'GET'])
def room():

    global g_dy_room_id
    global g_dy_room_cnzz

    return render_template("jump.html", g_dy_room_id=g_dy_room_id, g_dy_room_cnzz=g_dy_room_cnzz)



@app.route('/set_room_id', methods=['POST', 'GET'])
def set_room_id():

    global g_dy_room_id

    if request.method == 'POST':
        room_id = request.form.get('room_id')
        g_dy_room_id = room_id

    return redirect(url_for('console'))


@app.route('/set_room_cnzz', methods=['POST', 'GET'])
def set_room_cnzz():

    global g_dy_room_cnzz

    if request.method == 'POST':
        room_cnzz = request.form['room_cnzz']
        g_dy_room_cnzz = room_cnzz

    return redirect(url_for('console'))


@app.route('/data', methods=['POST', 'GET'])
def data():

    return render_template("data.html", g_records=g_records, g_stat=g_stat)

@app.route('/speed')
def speed():

    global g_cnt

    tarry  = []
    darry = []


    st = datetime.datetime.now() + datetime.timedelta(minutes=-60)

    for i in range(0, 61):
        sn = st + datetime.timedelta(minutes=i)
        ts = sn.strftime("%H:%M")
        tarry.append(ts)

        if g_cnt.has_key(ts):
            darry.append(g_cnt[ts])
        else:
            darry.append(0)

    return render_template('chart.html', tarry=tarry, darry=darry)

@app.route('/act_random', methods=['POST', 'GET'])
def act_random():
    random.shuffle(g_records)
    return redirect(url_for('console'))

if __name__ == '__main__':

    #path = DEF_FILE

    #global CUR_PORT

    if len(sys.argv) > 1:
        CUR_PORT = sys.argv[1]

    #records = cookie_load(path)
    #cookie_append(records)
    app.run(host='0.0.0.0', port=CUR_PORT)

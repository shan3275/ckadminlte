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

from werkzeug.utils import secure_filename


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

CUR_PORT = 2280


def now():
    str = time.strftime("%m-%d %H:%M:%S", time.localtime()) 
    return str

def get_min():
    str = time.strftime("%H:%M", time.localtime()) 
    return str

app = Flask(__name__, template_folder="",static_folder="",static_url_path="")

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
#app.config['DEBUG'] = True

@app.route('/')
def index():
    return 'Hello'

def GenuniueNum(length):
    numOfNum = random.randint(1,length-1)
    numOfLetter = length - numOfNum
    slcNum = [random.choice(string.digits) for i in range(numOfNum)]
    slcLetter = [random.choice(string.ascii_letters) for i in range(numOfLetter)]
    slcChar = slcNum + slcLetter
    random.shuffle(slcChar)
    rearStr = ''.join([i for i in slcChar])
    nowTime=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    uniqueNum=str(nowTime)+str(rearStr);
    return uniqueNum



@app.route('/code/registerJDPhone',methods=['GET'])
def registerJDPhone():
    if request.method == 'GET':
        status = -1
        msg = "fail"
        phoneNO = request.args.get("phone")
        if (phoneNO.isdigit() == true) and (len(str(phoneNO)) == 11):
            status = 0;
            msg = "success"
        orderid = Genordid(4)

        rep = {'orderid':orderid, 'msg':msg, 'status':status}
        return jsonify(rep)



@app.route('/code/commitCode',methods=['GET'])
def commitCode():
    if request.method == 'GET':
        msg = "error"
        Code = request.args.get("code")
        if Code.isdigit() == true:
            msg = "ok"
        return msg
        
         




if __name__ == '__main__':

    #path = DEF_FILE

    #global CUR_PORT

    if len(sys.argv) > 1:
        CUR_PORT = sys.argv[1]

    app.run(host='0.0.0.0', port=CUR_PORT)

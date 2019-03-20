#!/usr/bin/env python
# -*- coding:utf-8 -*-
#Filename:app.py

import sys
import re
import os
import time,datetime
import logging
import json
import socket

from flask import Flask, request, jsonify, render_template, redirect,url_for, send_file, send_from_directory,session,escape

import urllib
import random,hashlib
import chardet

from werkzeug.utils import secure_filename
from werkzeug.contrib.fixers import ProxyFix
import inits
import globalvar as gl
from strapi     import strapi_bp
from useradmin  import useradmin_bp
from stradmin   import stradmin_bp
from charts     import charts_bp
from forms      import forms_bp
from examples   import examples_bp
from layout     import layout_bp
from mailbox    import mailbox_bp
from tables     import tables_bp
from ui         import ui_bp
import libdb as libdb
global logger
global CONF

DEF_PORT = 8888
CUR_PORT = DEF_PORT

#app = Flask(__name__, template_folder="templates/html",static_folder="templates/html",static_url_path="")
app = Flask(__name__)
app.register_blueprint(strapi_bp,   url_prefix='/strapi')
app.register_blueprint(useradmin_bp, url_prefix='/useradmin')
app.register_blueprint(stradmin_bp, url_prefix='/admin')
#app.register_blueprint(charts_bp, url_prefix='/charts')
#app.register_blueprint(forms_bp, url_prefix='/forms')
#app.register_blueprint(examples_bp, url_prefix='/examples')
#app.register_blueprint(layout_bp, url_prefix='/layout')
#app.register_blueprint(mailbox_bp, url_prefix='/mailbox')
#app.register_blueprint(tables_bp, url_prefix='/tables')
#app.register_blueprint(ui_bp, url_prefix='/ui')

# set the secret key.  keep this really secret:
app.secret_key = '\xe5\xcc\xc5\xd9+\xfbC\xc6\xdbD\x1af\xe0\xa6*\xeb$\xa7\xe4\xf6p~\x01\xaf'
def now():
    return time.strftime("%m-%d %H:%M:%S", time.localtime())
g_stat = {"cycle":1, "pos":0,'take_out_cks':0, "total":0, "asigned":0, "req":0, "rereq":0, "none":0, "boot_ts": now(), "reset_ts":now()}
g_records = []
g_cnt = {}
@app.route('/')
def index():
    return "Hello World"


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    logger = gl.get_logger()
    CONF = gl.get_conf()
    CUR_PORT = CONF['port']
    if len(sys.argv) > 1:
        CUR_PORT = sys.argv[1]
    #app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run(debug=True,host='0.0.0.0', port=CUR_PORT)
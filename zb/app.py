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
import flask_admin as admin
from flask_admin import helpers as admin_helpers
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
import urllib
import random,hashlib
import chardet

from werkzeug.utils import secure_filename
from werkzeug.contrib.fixers import ProxyFix
import inits
import globalvar as gl
from strapi     import strapi_bp
from useradmin  import userAdmin_bp
from stradmin   import admin_bp
from stradmin   import admin_db_bp
from stradmin   import user_datastore


import libdb as libdb
global logger
global CONF

DEF_PORT = 8888
CUR_PORT = DEF_PORT

#app = Flask(__name__, template_folder="templates/html",static_folder="templates/html",static_url_path="")
app = Flask(__name__)
app.config.from_pyfile('config.py')
app.register_blueprint(strapi_bp,   url_prefix='/strapi')  #api接口

#配置界面主题，可选参数：Cerulean  Cosmo  Cyborg Darkly Flatly Journal
# Lumen Paper Readable Sandstone Simplex Slate Spacelab Superhero United Yeti
app.config['FLASK_ADMIN_SWATCH'] = 'yeti'


admin_db_bp.init_app(app)
security = Security(app, user_datastore)

admin_bp.init_app(app)
userAdmin_bp.init_app(app)



""""""
# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin_bp.base_template,
        admin_view=admin_bp.index_view,
        h=admin_helpers,
        get_url=url_for
    )

# set the secret key.  keep this really secret:
app.secret_key = '\xe5\xcc\xc5\xd9+\xfbC\xc6\xdbD\x1af\xe0\xa6*\xeb$\xa7\xe4\xf6p~\x01\xaf'
def now():
    return time.strftime("%m-%d %H:%M:%S", time.localtime())
g_stat = {"cycle":1, "pos":0,'take_out_cks':0, "total":0, "asigned":0, "req":0, "rereq":0, "none":0, "boot_ts": now(), "reset_ts":now()}
g_records = []
g_cnt = {}
@app.route('/')
def index():
    return "hello world"

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
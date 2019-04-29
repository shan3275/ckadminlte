#!/usr/bin/python
#-*- coding: UTF-8 -*-
# FileName : stradmin.py
# Author   : Shan
# DateTime : 2019/1/9
# SoftWare : PyCharm
from flask import Blueprint, abort,Flask, request, jsonify, render_template, redirect,url_for, send_file, send_from_directory
import flask_admin as admin
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla.form import AdminModelConverter
from flask_admin.contrib.sqla.form import InlineModelConverter
from flask_admin import helpers as admin_helpers
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
from flask_security.utils import encrypt_password
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
        return self.render('stradmin/index.html',  g_stat=g_stat)

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

admin_bp = admin.Admin(name="CK控制台",base_template='my_master.html',index_view=MyHomeView(url='/admin',endpoint='admin'),template_mode='bootstrap3')
#admin_bp = admin.Admin(name="CK控制台",base_template='my_master.html', template_mode='bootstrap3',url='/admin',endpoint='admin')


# Create custom admin view
class AdminTaskView(admin.BaseView):
    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                current_user.has_role('superuser')
        )

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

    @admin.expose('/')
    def index(self):
        tasks = libcommon.getTaskList()
        return self.render('stradmin/task.html',  task_records=tasks)

    @admin.expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        # render your view here
        return "Hello"

admin_bp.add_view(AdminTaskView(name='Task',endpoint='task'))

admin_db_bp = SQLAlchemy()
db = admin_db_bp
# Create models
class Cktb(db.Model):
    __tablename__='cktb'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer)
    nickname = db.Column(db.String(20),unique=True)
    password = db.Column(db.String(32))
    regdate = db.Column(db.Integer)
    cookie   = db.Column(db.Text)

    def __str__(self):
        return "{}, {}".format(self.nickname, self.password)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())


class MyModelConverter(AdminModelConverter):
    pass


class MyInlineModelConverter(InlineModelConverter):
    def post_process(self, form_class, info):
        #form_class.regdate  = wtf.StringField('regdate') + 10000
        form_class.regdate  =  10000
        return form_class
class CkAdmin(sqla.ModelView):
    #can_create = False
    #can_export = True
    #form_args = dict(regdate=((int)(time.time())))
    column_formatters = dict(regdate=lambda v, c, m, p:datetime.datetime.fromtimestamp(m.regdate))
    model_form_converter = MyModelConverter
    inline_model_form_converter = MyInlineModelConverter
    action_disallowed_list = ['delete', ]
    can_view_details = True
    column_display_pk = True
    column_list = [
        'id',
        'uid',
        'nickname',
        'password',
        'regdate',
        'cookie',
    ]
    column_default_sort = [('nickname', False), ('password', False)]  # sort on multiple columns

    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                current_user.has_role('superuser')
        )

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

admin_bp.add_view(CkAdmin(Cktb, db.session,name='CK', endpoint='ck'))


# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)

# Create customized model view class
class MyModelView(sqla.ModelView):
    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                current_user.has_role('superuser')
        )

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

# Add model views
admin_bp.add_view(MyModelView(Role, db.session))
admin_bp.add_view(MyModelView(User, db.session))


logger = gl.get_logger()
CONF   = gl.get_conf()
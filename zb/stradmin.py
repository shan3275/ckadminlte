#!/usr/bin/python
#-*- coding: UTF-8 -*-
# FileName : stradmin.py
# Author   : Shan
# DateTime : 2019/1/9
# SoftWare : PyCharm
from flask import Blueprint, abort,Flask, request, jsonify, render_template, redirect,url_for, send_file, send_from_directory
import flask_admin as admin
from flask_admin.actions import action
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
import time

global logger
global CONF

g_stat = {"cycle":1, "pos":0,'could_use':0, "total":0, "asigned":0, "req":0, "rereq":0, "none":0, "boot_ts": libcommon.now(), "reset_ts":libcommon.now()}
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
        t['cts']      = libcommon.now()
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
#admin_bp = admin.Admin(name="CK控制台",index_view=MyHomeView(url='/admin',endpoint='admin'),template_mode='bootstrap3')


# Create custom admin view
class AdminTaskView(admin.BaseView):
    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                (current_user.has_role('superuser') or current_user.has_role('user'))
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
        return self.render('admin/task.html',  task_records=tasks)

    @admin.expose('/del_task')
    def del_task(self):
        taskIdStr = request.args.get('task_id')
        userIdStr = request.args.get('user')
        if userIdStr != None:
            userId = int(userIdStr)
        else:
            # default 0
            userId = 0
        logger.debug('taskIdStr: %s', taskIdStr)
        if taskIdStr != None:
            libcommon.delTaskFromRedis(userId, taskIdStr)

        return redirect(url_for('task.index'))

#admin_bp.add_view(AdminTaskView(name='任务列表',endpoint='task'))
admin_bp.add_view(AdminTaskView(name='任务列表',endpoint='task',category='任务'))

admin_db_bp = SQLAlchemy()
db = admin_db_bp

# Create models
class Tasktb(db.Model):
    __tablename__='task'
    id              = db.Column(db.Integer, primary_key=True)
    task_id         = db.Column(db.String(32))
    effective       = db.Column(db.Integer)
    user_id         = db.Column(db.Integer)
    reset_done      = db.Column(db.Integer)
    submit_time     = db.Column(db.String(32))
    begin_timestamp = db.Column(db.Integer)
    total_time      = db.Column(db.Integer)
    last_time_from  = db.Column(db.Integer)
    last_time_to    = db.Column(db.Integer)
    time_gap        = db.Column(db.Integer)
    gap_num         = db.Column(db.Integer)
    user_num        = db.Column(db.Integer)
    req             = db.Column(db.Integer)
    ck_req          = db.Column(db.Integer)
    ck_url          = db.Column(db.String(128))
    room_url        = db.Column(db.String(128))

    def __str__(self):
        return "{}, {}".format(self.nickname, self.password)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())


class AdminDbTaskView(sqla.ModelView):
    can_create = False
    action_disallowed_list = ['delete', ]
    #form_args = dict(regdate=((int)(time.time())))
    column_formatters = dict(begin_timestamp=lambda v, c, m, p:datetime.datetime.fromtimestamp(m.begin_timestamp))
    can_view_details = True
    column_display_pk = True
    column_list = [
        'id',
        'task_id',
        'effective',
        'user_id',
        'reset_done',
        'submit_time',
        'begin_timestamp',
        'total_time',
        'last_time_from',
        'last_time_to',
        'time_gap',
        'gap_num',
        'user_num',
        'req',
        'ck_req',
        'ck_url',
        'room_url',
    ]

    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                (current_user.has_role('superuser') or current_user.has_role('user'))
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

admin_bp.add_view(AdminDbTaskView(Tasktb, db.session, name='固化任务',endpoint='db-task',category='任务'))

# BufferView
class BufferView(admin.BaseView):
    @admin.expose('/',  methods=['POST', 'GET'])
    def index(self):
        if request.method == 'POST':
            userIdStr = request.form.get('user_id')
        else:
            userIdStr = request.args.get('user')

        if userIdStr != None:
            userId = int(userIdStr)
        else:
            # default 0
            userId = 0

        # 获取表项数量
       
        stat = libcommon.getUserStat(userId)
        cookies = libcommon.getUserCookieList(userId)
        total_renqi = libcommon.total_renqi_get(userId)
        return self.render('/admin/buffer.html',  g_stat=stat,user=userId, cookie_records=cookies, total_renqi=total_renqi)

    @admin.expose('/buffer_clear', methods=['POST', 'GET'])
    def buffer_clear(self):
        userIdStr = request.args.get('user')
        if userIdStr != None:
            userId = int(userIdStr)
        else:
            # default 0
            userId = 0
        CNT = libcommon.clear_records(userId)
        return redirect(url_for('redis-cookies.index', user=userId))
    
    @admin.expose('/alloc_renqi',methods=('GET', 'POST'))
    def alloc_renqi(self):
        global g_stat
        if request.method == 'POST':
            renqi_req = request.form.get('renqi_req')
            userIdStr = request.args.get('user')
            if userIdStr != None:
                userId = int(userIdStr)
            else:
                # default 0
                userId = 0
            logger.debug('alloc_cookie renqi_req: %s',  renqi_req)
            
            total = float(renqi_req)
            alloced = libcommon.renqi_alloc(userId, total)

        return redirect(url_for('redis-cookies.index', user=userId))
      
    @admin.expose('/move/', methods=('GET', 'POST'))
    def move_view(self):
        # render your view here
        libcommon.moveTaskFromRedistoDB()
        return "move success!"
      
admin_bp.add_view(BufferView(name='缓存Cookie',endpoint='redis-cookies',category='Cookies'))



# Create models
class Cookie(db.Model):
    __tablename__='cktb'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer)
    nickname = db.Column(db.String(20),unique=True)
    grp = db.Column(db.String(20),unique=True)
    password = db.Column(db.String(32))
    regdate = db.Column(db.Integer)
    cookie   = db.Column(db.Text)

    def __str__(self):
        return "{}, {}".format(self.nickname, self.password)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())

class CookieAdmin(sqla.ModelView):
    #can_create = False
    #can_export = True
    #form_args = dict(regdate=((int)(time.time())))
    column_formatters = dict(regdate=lambda v, c, m, p:datetime.datetime.fromtimestamp(m.regdate))
    action_disallowed_list = ['delete', ]
    can_view_details = True
    column_display_pk = True
    
    column_list = [
        'id',
        'uid',
        'nickname',
        'password',
        'grp',
        'regdate',
        'cookie',
    ]
    column_filters = ('grp',) 
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

admin_bp.add_view(CookieAdmin(Cookie, db.session,name='固化Cookie', endpoint='db-cookies',category='Cookies'))

#supplier models

class Supplier(db.Model):
    __tablename__='suptb'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20),unique=True)
    ctime = db.Column(db.TIMESTAMP(True))
    note   = db.Column(db.Text)

    def __str__(self):
        return "{}, {}".format(self.name)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())


class SupplierModelConverter(AdminModelConverter):
    pass

class SupplierAdmin(sqla.ModelView):
    list_template = 'admin/supplier.html'
    model_form_converter = SupplierModelConverter
    action_disallowed_list = ['delete', ]
    can_view_details = True
    column_display_pk = True
    can_export = True
    column_list = [
        'id',
        'name',
        'ctime',
        'note',
    ]
    column_default_sort = [('id', False)]  # sort by field id
admin_bp.add_view(SupplierAdmin(Supplier,  db.session,name='Cookie供应商', endpoint='Supplier', category='Cookies'))

#Group models
from wtforms import IntegerField, FloatField, StringField, SelectField, DateField, DateTimeField, FileField, TextAreaField, form, Form
from wtforms.ext.sqlalchemy.fields import QuerySelectField

class Group(db.Model):
    __tablename__='grptb'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20),unique=True)
    supplier = db.Column(db.String(20))
    utime   = db.Column(db.TIMESTAMP(True))
    ttime   = db.Column(db.TIMESTAMP(True))
    ctime = db.Column(db.TIMESTAMP(True))
    number  = db.Column(db.Integer)
    active   = db.Column(db.Integer)
    rratio = db.Column(db.Float)
    cratio = db.Column(db.Float)
    rrenqi = db.Column(db.Integer)
    crenqi = db.Column(db.Integer)
    note   = db.Column(db.Text)

    def __str__(self):
        return "{}, {}".format(self.name)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())


class GroupModelConverter(AdminModelConverter):
    pass

class GroupForm(Form):
    def sup_query_factory():
        return [r.name for r in db.session.query(Supplier).all()]

    def sup_get_pk(obj):
        return obj

    name = StringField('名称')

    supplier = QuerySelectField('渠道', query_factory=sup_query_factory, get_pk=sup_get_pk)

    csv = FileField('CSV 文件')
    note = TextAreaField('备注')

    number = IntegerField('数量', default=0)
    rratio = FloatField('原始系数', default=1.0)
    rrenqi = IntegerField('原始人气', default=0)
    
    #ctime =DateTimeField(now())
    def validate_csv(form, field):

        logger.info("form.name.data: %s", form.name.data)
        logger.info("field.data: %s", field.data)
        logger.info("form.csv.data: %s", form.csv.data)

        if field.data:
            file = field.data
            if form.name.data:
                grp = form.name.data
                ou = libcommon.writeFileToDB(file, grp)
                
                if ou['error'] == 0:
                    form.number.data = ou['data']['num']
                    return True
                
        return False

    def validate_rrenqi(form, field):
        if form.number.data and form.rratio.data:
            field.data = form.number.data * form.rratio.data
            return True
        else:
            return False

    


class GroupAdmin(sqla.ModelView):

    form = GroupForm
    list_template = 'admin/group.html'
    model_form_converter = GroupModelConverter
    action_disallowed_list = ['delete', ]
    can_view_details = True
    column_display_pk = True
    can_export = True
    column_list = [
        'id',
        'name',
        'supplier',
        'active',
        'cratio',
        'crenqi',
        'number',
        'rratio',
        'rrenqi',
        'utime',
        'ttime',
        'ctime',
        'note',
    ]
    #column_default_sort = [('nickname', False), ('password', False)]  # sort on multiple columns
    column_default_sort = [('id', False)]  # sort by field id
admin_bp.add_view(GroupAdmin(Group,  db.session,name='Cookie组', endpoint='Group', category='Cookies'))

# Custom
class Custom(db.Model):
    __tablename__='custb'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20),unique=True)
    ctime = db.Column(db.TIMESTAMP(True))
    note   = db.Column(db.Text)

    def __str__(self):
        return "{}, {}".format(self.name)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())


class CustomModelConverter(AdminModelConverter):
    pass

class CustomAdmin(sqla.ModelView):
    model_form_converter = CustomModelConverter
    action_disallowed_list = ['delete', ]
    can_view_details = True
    column_display_pk = True
    can_export = True
    column_list = [
        'id',
        'name',
        'ctime',
        'note',
    ]
    column_default_sort = [('id', False)]  # sort by field id
admin_bp.add_view(CustomAdmin(Custom,  db.session,name='客户', endpoint='Custom',category='需求'))

# Orders

class OrderForm(Form):
    def custom_query_factory():
        return [r.name for r in db.session.query(Custom).all()]

    def custom_get_pk(obj):
        return obj

    name = StringField('名称')

    custom = QuerySelectField('客户', query_factory=custom_query_factory, get_pk=custom_get_pk)

    platform_choices   = [('douyu', u'斗鱼'), ('huya', u'虎牙'), ('qie', u'企鹅')]
    platform = SelectField(label=u'平台', choices=platform_choices)

    type_choices   = [('renqi', u'人气'), ('huya', u'排名')]
    order_type = SelectField(label=u'类型', choices=type_choices)

    room_id = IntegerField('房间号', default=0)
    renqi      = IntegerField('人气', default=0)
    income   = IntegerField('收入', default=0) 
    sdate      = DateField('开始日期')
    edate      = DateField('结束日期')
    note       = TextAreaField('备注')

class Orders(db.Model):
    __tablename__='ordtb'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    custom = db.Column(db.String(255))
    platform = db.Column(db.String(255))
    room_id = db.Column(db.String(255))
    order_type =  db.Column(db.String(255))
    renqi  = db.Column(db.Integer)
    income  = db.Column(db.Integer)
    ctime = db.Column(db.TIMESTAMP(True))
    sdate = db.Column(db.Date())
    edate = db.Column(db.Date())
    note = db.Column(db.Text)

    def __str__(self):
        return self.id

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())


class OrderAdmin(sqla.ModelView):

    form = OrderForm
    list_template = 'admin/orders.html'
    can_view_details = True
    column_display_pk = True
    edit_modal=True
    column_searchable_list=['custom', 'platform', 'room_id', 'order_type', 'renqi']
    column_list = [
        'id',
        'name',
        'custom',
        'platform',
        'room_id',
        'order_type',
        'renqi',
        'income',
        'ctime',
        'sdate',
        'edate',
        'note',
    ]

    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                (current_user.has_role('superuser') or current_user.has_role('user'))
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

admin_bp.add_view(OrderAdmin(Orders, db.session,name='需求列表',endpoint='Orders',category='需求'))

# Create custom admin view
class CreateTaskView(admin.BaseView):
    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                (current_user.has_role('superuser') or current_user.has_role('user'))
        )

    @admin.expose('/')
    def index(self):
        order_id = request.args.get('order_id')

        logger.debug('order_id: %s', order_id)

        if order_id == None:
            order_id = 1

        order = libcommon.getOrder(order_id)

        if order == None:
            return redirect(url_for('Orders.index_view'))
            #return self.render('admin/orders.html',order=order)
        else:
            return self.render('admin/createtask.html',order=order)

    @admin.expose('/submit_task', methods=['POST', 'GET'])
    def submit_task(self):
        global g_stat
        if request.method == 'POST':
            
            order_id = request.form.get('order_id')
            begin_time = request.form.get('begin_time')
            task_time = request.form.get('task_time')
            total_time = request.form.get('total_time')

            
            renqi_num = request.form.get('renqi_num')
            last_time_from = request.form.get('last_time_from')
            last_time_to = request.form.get('last_time_to')
            time_gap = request.form.get('time_gap')
            gap_num = request.form.get('gap_num')
            userId = request.form.get('user_id')


            logger.debug('begin_time: %s, total_time:%s' %(begin_time, total_time))
            logger.debug('renqi_num: %s' %(renqi_num))
            logger.debug('last_time_from:%s, last_time_to:%s' %(last_time_from, last_time_to))
            logger.debug('time_gap:%s, gap_num:%s' %(time_gap, gap_num))

            begin_time_s = begin_time.replace('T', ' ')
            begin_timestamp = libcommon.strToTimestamp(begin_time_s)

            room_url = request.form.get('room_url')
            ck_url = request.form.get('ck_url')

            order = libcommon.getOrder(order_id)
            room_url = libcommon.room_url(order['platform'], order['room_id'])
            ck_url = "http://127.0.0.1:8200/useradmin/cookie?user=%s" %(userId)

            logger.debug('room_url: %s, ck_url: %s' %(room_url, ck_url))

            req_renqi = int(renqi_num)

            userId = int(userId)
            alloced = libcommon.renqi_alloc(userId, req_renqi)

            ck_num = libcommon.renqi_to_cookies(userId, req_renqi)
            
            logger.debug(' req_renqi %d, alloced %d, ck_num %d' %(req_renqi, alloced, ck_num))
            

            task_min = int(task_time)
            total_min = int(total_time)
            cur_min = 0
            while cur_min < task_min:
                cur_timestamp = begin_timestamp + (cur_min * 60)
                cur_time_s =  time.localtime(cur_timestamp)
                cur_time_f = time.strftime("%Y-%m-%dT%H:%M:%S",cur_time_s)
                libcommon.writeTaskToRedis(userId, room_url, ck_url, cur_time_f, total_time, \
                                       ck_num, last_time_from, last_time_to, time_gap, gap_num)
                cur_min += total_min

                logger.debug('task_min:%d, cur_min:%d, cur_time_s=%s' %(task_min, cur_min, cur_time_s))
        return redirect(url_for('task.index'))

    

admin_bp.add_view(CreateTaskView(name='创建任务',endpoint='createtask',category='任务' ))

# Role
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

# User
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
#from redis import Redis
#from flask_admin.contrib import rediscli
#admin_bp.add_view(rediscli.RedisCli(Redis()))


logger = gl.get_logger()
CONF   = gl.get_conf()
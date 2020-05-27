#!/usr/bin/python
#-*- coding: UTF-8 -*-
# FileName : libcm.py
# Author   : Shan
# DateTime : 2020/5/21
# SoftWare : Visual Studio Code
import requests,json,sys,os
from requests import exceptions 
from urllib import urlencode
from werkzeug.utils import secure_filename
import libdb as libdb
import libredis as libredis
import chardet
import urllib
import time,datetime
import globalvar as gl

global logger
global CONF

def getIPAreaOnline(ip):
    '''
    通过第三方接口查询ip归属地
    Args:
        ip:    请求的IP
    Return:
        area:    false 为失败,否则为dict(state='',province='',city='',postcode='',phonecode='')
    '''
    params = urlencode({'ip':ip,'datatype':'jsonp'})
    url = 'http://api.ip138.com/query/?'+params
    payload = dict(token="dd333cd32f6e51e2893577cc9ee1a681")
    try:
        r = requests.get(url,params=payload)
    except exceptions.Timeout as e:
        logger.error('请求超时：'+str(e.message))
        return False
    except exceptions.HTTPError as e:
        logger.error('http请求错误:'+str(e.message))
        return False
    except exceptions.ConnectionError as e:
        logger.error('http连接错误:'+str(e.message))
        return False
    else:
        #logger.debug('接码平台链接: %s', r.url)
        ##判断http get返回值
        if r.status_code != requests.codes.ok:
            logger.error('get 失败,r.status_code=%d', r.status_code)
            return False

        logger.info(r.text)
        responsed = r.json()
        if responsed.has_key('ret') == False:
            return False
        elif responsed['ret'] == 'ok':
            area = dict(state=responsed['data'][0],
                        province = responsed['data'][1],
                        city     = responsed['data'][2],
                        postcode = responsed['data'][4],
                        phonecode= responsed['data'][5])
            return area;

def writeIPandAreaIDtoDB(ip, areaID):
    '''
    将ip地址和区域id信息写入数据库表项
    Args:
        ip:       IP地址
        areaID:   区域ID
    Return:
        true or false
    '''
    key = "addr, areaid"
    value = "'%s', '%s' " %(ip, areaID)
    logger.debug('key:%s, value:%s', key, value)
    rv = libdb.LibDB().insert_db(key, value, CONF['database']['iptb'])
    return rv


def writeAreaToDB(area):
    """
    将区域信息写入表项area，不是IP地址信息
    :param area: dict(state='',province='',city='',postcode='',phonecode='')
    :return: true or false
    """
    key = "province, city, postcode, phonecode"
    value = "'%s', '%s', '%s', '%s'" \
            %(area['province'], area['city'], area['postcode'],area['phonecode'])
    logger.debug('key:%s, value:%s', key, value)
    rv = libdb.LibDB().insert_db(key, value, CONF['database']['area'])
    return rv

def getAreaIDFromDB(postcode):
    '''
    通过邮编查询区域ID
    Args:
        postcode: 邮政编码
    Return:
        areaId:  false or None or 成功值
    '''
    sql = libdb.LibDB().query_one('postcode', postcode, CONF['database']['area'])
    if  sql == False : #查询失败
        logger.error('get AreaID 读数据库失败')
        return False
    elif sql == None:   #查询成功，但是为空
        logger.info('area 记录为空, not found 邮编：%s',  postcode)
        return None
    else: #查询成功
        logger.info(sql);
        areaID = sql[0]
        return areaID


def getIPAreaOnlineAndWrToDB(ip):
    '''
    获取区域信息，并写入数据库
    Args:
        ip:    请求的IP
    Return:
        areaId: false 为失败，否则为数值ID
    '''
    #获取区域信息
    area = getIPAreaOnline(ip)
    if area == False:
        return False 
    #根据邮政编码查询区域ID
    postcode = area['postcode']
    areaID = getAreaIDFromDB(postcode)
    if  areaID == False : #查询失败
        logger.error('get AreaID 读数据库失败')
        return False
    elif areaID == None:   #查询成功，但是为空
        logger.info('area 记录为空, %s-%s-%s', area['state'], area['province'], area['city'])
        #区域记录为空，故需要写入数据库表项中
        if writeAreaToDB(area) == False:
            logger.error('将区域信息写入数据库失败')
            return False
        #再次查询
        areaID = getAreaIDFromDB(postcode)
        if  areaID == False : #查询失败
            logger.error('再次 get AreaID 读数据库失败')
            return False
        elif areaID == None:
            logger.error('正常逻辑不会执行到这里，除非闹鬼了')
            return False  
    
    #将IP和区域ID写入数据库iptb表项中
    rv = writeIPandAreaIDtoDB(ip, areaID)
    if rv == False:
        logger.error('将IP和区域ID写入数据库iptb表项中 失败')

    return areaID
    

def getIPAreaID(ip):
    '''
    查询ip的区域id，如果查询不到自动通过api获取，获取成功之后插入数据库中
    Args:
        ip:    请求的IP
    Return:
        areaID:    false 为失败,否则为数值
    '''
    #首先查询本地ip库
    sql = libdb.LibDB().query_one('addr', ip, CONF['database']['iptb'])
    if  sql == False : #查询失败
        logger.error('getIPAreaID 读数据库失败')
        return False
    elif sql == None:   #查询成功，但是为空
        logger.info('ip 记录为空, %s', ip)
        #线上查询，并写入数据库
        areaID = getIPAreaOnlineAndWrToDB(ip)
    else: #查询成功
        areaID = sql[2]
        logger.info(sql);
    
    return areaID


def getCKByIP(ip):
    '''
        通过查询ip，获取一条ck记录
    Args:
        ip:  IP地址
    Return:
        record: ck记录表项 or None or False(运行出错)
    '''
    sql = libdb.LibDB().query_one('lastip', ip, CONF['database']['cktb'])
    if  sql == False : #查询失败
        logger.error('get ck by lastip 读数据库失败')
        return False
    elif sql :   #查询成功
        logger.info(sql);
        timestamp = int(time.time())
        setval = "colddate=%d" %(timestamp+CONF['ckcoldtime'])
        condition = "id=%d" %(sql[0])
        logger.debug('setval:%s, condition:%s', setval, condition)
        rv =  libdb.LibDB().update_db(setval, condition, CONF['database']['cktb'])
        if rv == False:
            logger.error('更新ck表冷却时间失败')
            return False
        return sql   #成功
    return None

def getCKByID(ip,areaId):
    '''
        通过查询区域ID，获取一条ck记录
    Args:
        ip:  IP地址
        areaId:   区域Id索引
    Return:
        record: ck记录表项 or None or False(运行出错)
    '''
    #查询命中区域ID，且冷却时间最小，但是必须小于当前时间
    key = 'colddate'
    condition = "areaid=%d" %(areaId)
    info = libdb.LibDB().min_key_of_condition(key, CONF['database']['cktb'], condition)
    if info == False:
        logger.error('查询区域ID中最小值失败')
        return False
    logger.info(type(info))
    logger.info(info)
    if  info:
        min = info[0]
        if min == None:
            return None
    else:
        return None
    logger.info(min)

    #根据最小值和区域ID再查询一次，有点蛋疼
    timestamp = int(time.time())
    conditon = 'areaid=%d and colddate=%s' % (areaId, min)
    sql = libdb.LibDB().query_one_by_condition(conditon, CONF['database']['cktb'])
    if sql == False: #查询失败
        logger.error('get ck by %s 读数据库失败', condition)
        return False
    elif sql == None: 
        logger.error('闹鬼了才会执行到这里')
    logger.info(sql)
    if sql == None:
        return False
    
    colddate = sql[8]
    index    = sql[0]
    logger.info('冷却时间：%d',colddate)
    if colddate <= timestamp: #冷却时间已经过了，可以使用
        setval = "colddate=%d,lastip='%s'" %(timestamp+CONF['ckcoldtime'], ip)
        condition = "id=%d" %(index)
        logger.debug('setval:%s, condition:%s', setval, condition)
        rv =  libdb.LibDB().update_db(setval, condition, CONF['database']['cktb'])
        if rv == False:
            logger.error('更新ck表冷却时间及IP失败')
            return False
        return sql #成功
    return None


def getCKByNoneIP(ip,areaId):
    '''
        通过查询ip为空的记录，获取一条ck记录
    Args:
        ip:  IP地址
        areaId:   区域Id索引
    Return:
        record: ck记录表项 or None or False(运行出错)
    '''
    sql = libdb.LibDB().query_one('lastip', '', CONF['database']['cktb'])
    if  sql == False : #查询失败
        logger.error('get ck by lastip 读数据库失败')
        return False
    elif sql :   #查询成功
        logger.info(sql);
        timestamp = int(time.time())
        setval = "colddate=%d,lastip='%s',areaid=%d" %(timestamp+CONF['ckcoldtime'],ip,areaId)
        condition = "id=%d" %(sql[0])
        logger.debug('setval:%s, condition:%s', setval, condition)
        rv =  libdb.LibDB().update_db(setval, condition, CONF['database']['cktb'])
        if rv == False:
            logger.error('更新ck表冷却时间失败')
            return False
        return sql   #成功
    return None

def getCKByIDandIP(ip, areaId):
    '''
    获取一条ck记录
    Args:
        ip:  IP地址
        areaId:   区域Id索引
    Return:
        record: ck记录表项 or None
    '''
    #查询IP
    record = getCKByIP(ip)
    if record == False:
        return None
    elif record != None:
        return record
    
    #查询成功,但是为空
    logger.info('ck 查询 ip 记录为空, %s', ip)
    #查询区域ID
    record = getCKByID(ip,areaId)
    if record == False:
        return None
    elif record != None:
        return record
    
    #查询成功，但是为空，下面查找ip为空表项，也就是未使用的记录
    record = getCKByNoneIP(ip,areaId)
    if record == False:
        return None
    elif record != None:
        return record
    
    return None


def getCKFromDB(ip,userId):
    '''
    从mysql数据库中获取一条cookie
    Args:
        ip :    请求的IP
        userId: 用户ID，暂不使用 
    '''
    areaId = getIPAreaID(ip);
    if areaId == False:
        return None

    #根据区域ID查询ck记录    
    record = getCKByIDandIP(ip, areaId)
    logger.info(record)
    return record

logger = gl.get_logger()
CONF   = gl.get_conf()
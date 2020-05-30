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
import ipdb
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

def _writeIPandAreaIDtoRedis(ip, area):
    '''
    将ip地址和区域id信息写入数据库表项
    Args:
        ip:         IP地址
        area:  dist(province='',city='', postcode='', id='')
    Return:
        true or false
    '''
    logger.info(ip)
    info = dict()
    name                    = ip
    info['id']              = 0
    info['addr']            = ip
    info['areaid']          = area['id']
    info['postcode']        = area['postcode']
    info['submission_date'] = _now()
    if libredis.LibRedis(CONF['redis']['ipdb']).hashMSet(name, info):
        logger.info('插入到redis成功')
        return True
    else:
        logger.error('插入到redis失败')
        return False 

def _writeAreaToRedis(area):
    """
    将区域信息写入表项area，不是IP地址信息
    :param area: dict(state='',province='',city='',postcode='',phonecode='')
    :return: true or false
    """
    name = area['postcode']
    if libredis.LibRedis(CONF['redis']['areadb']).hashMSet(name, area):  
        return True
    else:
        return False

def _getAreaIDFromRedis(postcode):
    '''
    通过邮编查询区域ID
    Args:
        postcode: 邮政编码
    Return:
        areaId:  false or None or dict(id='',postcode='')
    '''
    crack = libredis.LibRedis(CONF['redis']['areadb'])
    len = crack.hashHlen(postcode)
    if len == 0:
        logger.info('postcode 记录为空, %s', postcode)
        return False
    record = crack.hashGetAll(postcode)
    if record.has_key('postcode') ==False:
        return False
    return record

def _getIPAreaOnlineAndWrToRedis(ip):
    '''
    获取区域信息，并写入数据库
    Args:
        ip:    请求的IP
    Return:
        postcode: false 为失败，否则为字符串
    '''
    #获取区域信息
    area = getIPAreaOnline(ip)
    if area == False:
        return False 
    #根据邮政编码查询区域ID
    postcode = area['postcode']
    area = _getAreaIDFromRedis(postcode)
    if  area == False : 
        logger.info('area 记录为空, %s-%s-%s', area['state'], area['province'], area['city'])
        #区域记录为空，故需要写入数据库表项中
        if _writeAreaToRedis(area) == False:
            logger.error('将区域信息写入数据库失败')
            return False
        
    #将IP和区域ID写入数据库iptb表项中
    rv = _writeIPandAreaIDtoRedis(ip, area)
    if rv == False:
        logger.error('将IP和区域ID写入数据库iptb表项中 失败')

    return area['postcode']
    
def _getIPAreaID(ip):
    '''
    查询ip的区域id，如果查询不到自动通过api获取，获取成功之后插入数据库中
    Args:
        ip:    请求的IP
    Return:
        postCode:    false 为失败,否则为邮编
    '''
    #首先查询本地ip库
    crack = libredis.LibRedis(CONF['redis']['ipdb'])
    len = crack.hashHlen(ip)
    if len == 0:
        logger.info('ip 记录为空, %s', ip)
        #线上查询，并写入数据库
        postCode = _getIPAreaOnlineAndWrToRedis(ip)
        return postCode
    
    #redis中存在
    record = crack.hashGetAll(ip)
    if record.has_key('postcode') ==False:
        logger.error('异常，iptb中 postcode被删除')
        return False
    postCode = record['postcode']

    return postCode

def _getCKByIP(ip):
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
        record  =dict()
        record['cookie'] = sql[11]
        return record  #成功
    return None

def _getCKByPostCode(ip, postCode):
    '''
    获取一条ck记录,从mysql中
    Args:
        ip:         IP地址
        postCode:   邮编信息
    Return:
        record: ck记录表项 or None or False
    '''
    if ip == '' or postCode == '':
        logger.error('ip(%s) or postCode(%s) null', ip, postCode)
        return None
    timestamp = int(time.time())
    #condition = "postcode='%s' and colddate<%d limit 1" %(postCode, timestamp)
    condition = "postcode='%s' order by colddate asc limit 10" %(postCode)
    sql = libdb.LibDB().query_one_by_condition(condition, CONF['database']['cktb'])
    if  sql == False : #查询失败
        logger.error('get ck by lastip 读数据库失败')
        return False
    elif sql :   #查询成功
        logger.info(sql);
        colddate = sql[8]
        logger.info('冷却时间：%d',colddate)
        if colddate <= timestamp: #冷却时间已经过了，可以使用
            setval = "colddate=%d,lastip='%s',postcode='%s'" %(timestamp+CONF['ckcoldtime'], ip, postCode)
            condition = "id=%d" %(sql[0])
            logger.debug('setval:%s, condition:%s', setval, condition)
            rv =  libdb.LibDB().update_db(setval, condition, CONF['database']['cktb'])
            if rv == False:
                logger.error('更新ck表冷却时间失败')
                return False
            record  =dict()
            record['cookie'] = sql[11]
            return record  #成功
    
    return None    


def _getOneCKFromRedisAndWriteToDB(ip,postCode):
    '''
    从Redis中获取一条ck，添加ip、冷却时间、邮编，插入mysql
    Args:
        ip:         IP地址
        postCode:   邮编信息
    Return:
        record: ck记录表项 or None or False    
    '''
    #获取redis中ck 键值
    crack = libredis.LibRedis(CONF['redis']['cktbdb'])
    if CONF['random'] == True:
        num = crack.setCard(CONF['redis']['live'])
        if num == 0:
            logger.info('cookie has used over, fecth record fail')
            return None

        nickname = crack.setSpop(CONF['redis']['live'])
        if nickname == None:
            logger.error('fetch record get nickname null!!')
            return None
    else:
        num = crack.listLLen(CONF['redis']['live'])
        if num == 0:
            logger.info('cookie has used over, fecth record fail')
            return None

        nickname = crack.listLPop(CONF['redis']['live'])
        if nickname == None:
            logger.error('fetch record get nickname null!!')
            return None

    #获取cookie
    record = crack.hashGetAll(nickname)
    if record == None:
        logger.error('cookie record not existed nickname:%s', nickname)
        return None
    
    if record.has_key('nickname') == False:
        logger.info(nickname)
        logger.error('redis ck record no exist nickname, error!')
        logger.info(record)
        return None
    ##插入ck到mysql中
    #写入数据库
    sql = libdb.LibDB().query_one('nickname', record['nickname'], CONF['database']['table'])
    if sql == False:
        logger.error('查询 ck失败')
        return None
    if sql == None:
        timestamp = int(time.time())
        key = "nickname, password, grp, regdate, lastdate, colddate, cookie, lastip, postcode"
        value = "'%s', '%s', '%s', '%d', '%d', '%d', '%s', '%s', '%s'" \
                        %(record['nickname'], record['password'], 'G0', \
                          timestamp, timestamp,timestamp+CONF['ckcoldtime'], \
                          record['cookie'], ip, postCode)
        logger.debug('key:%s, value:%s', key, value)
        rv = libdb.LibDB().insert_db(key, value, CONF['database']['cktb'])
        if rv != True:
            logger.error('CK 插入mysql失败')
            return None
    else:
        logger.error('redis 和 mysql 中同时存在记录，请关注')
        return None
    
    #删除redis中已经去除的ck
    if crack.delete(nickname) :
        logger.info('从redis中删除一条ck成功')

    return record     

def getOneCK(ip,userId):
    '''
    从mysql数据库或者redis获取一条cookie
    Args:
        ip :    请求的IP
        userId: 用户ID，暂不使用 
    '''
    # 1.首先查询mysql中是否存在该ip的记录
    record = _getCKByIP(ip)
    if record == False:
        return None
    elif record != None:
        return record
     
    # 2.没有记录，则获取IP归属地
    postCode = _getIPAreaID(ip)
    if postCode == False :
        return None
    
    if postCode == '':
        logger.error('postCode is null')
        return None
      
    
    # 3.根据邮编查询ck记录
    record = _getCKByPostCode(ip, postCode)
    if record == False:
        return None
    elif record != None:
        return record

    # 4. 从redis中取出一条空记录（redis中存放的都是空记录）
    record = _getOneCKFromRedisAndWriteToDB(ip,postCode)
    logger.info(record)
    return record

def _now():
    return time.strftime("%m-%d %H:%M:%S", time.localtime())

def _queryCount(table):
    '''
    查询数据库中table的表项数量
    return：
        total: 表项数量
    '''
    count = libdb.LibDB().query_count(table)
    if count != False:
        total = count[0]
    else:
        total = 0
    return total
  

def queryAreaCount():
    return _queryCount(CONF['database']['area'])

def getAreaFromDBandWriteToRedis():
    '''
    从mysql 数据库中读取area表项，写入redis中
    存放到redis 中的表项数据格式：
    key：dict（）
    postcode: {id='',province='',city='',postcode='',areacode='',submission_date=''}
    Args:
        None
    return:
        num: 插入成功数量
    '''
    num = 0
    #使用分页查询
    page_size = 100
    total = queryAreaCount()
    if total == 0:
        return num
    
    page  = total / page_size
    page1 = total % page_size
    if page1 != 0:
        page = page + 1
    
    for p in range(0, page):
        limit_param = ' limit ' + str(p * page_size) + ',' + str(page_size)
        sql = 'select * from ' + CONF['database']['area'] + limit_param
        areaRows = libdb.LibDB().query_all_by_condition(sql)
        for area in areaRows:
            logger.info(area)
            info = dict()
            name                    = area[4]
            info['id']              = area[0]
            info['province']        = area[1]
            info['city']            = area[2]
            info['postcode']        = area[4]
            info['phonecode']       = area[5]
            info['submission_date'] = _now()
            if libredis.LibRedis(CONF['redis']['areadb']).hashMSet(name, info):
                logger.info('插入到redis成功')
                num +=1
            else:
                logger.error('插入到redis失败')    

    return num

def queryIPCount():
    return _queryCount(CONF['database']['iptb'])    

def queryIPCountByCondition(condition):
    '''
    查询数据库中table的表项数量
    return：
        total: 表项数量
    '''
    count = libdb.LibDB().query_count_by_condition(condition, CONF['database']['iptb'])
    if count != False:
        total = count[0]
    else:
        total = 0
    return total 

def getIptbFromDBandWriteRedis():
    '''
    从mysql 数据库中读取ip表项，写入redis中
    存放到redis 中的表项数据格式：
    key：dict（）
    ip: {id='',addr='',areaid='',postcode=''}
    Args:
        None
    return:
        num: 插入成功数量
    '''
    num = 0
    #使用分页查询
    page_size = 1000
    condition = " postcode!='0' "
    total = queryIPCountByCondition(condition)    
    if total == 0:
        return num
    
    page  = total / page_size
    page1 = total % page_size
    if page1 != 0:
        page = page + 1
    
    for p in range(0, page):
        limit_param = ' limit ' + str(p * page_size) + ',' + str(page_size)
        sql = 'select * from ' + CONF['database']['iptb'] +' where ' + condition + limit_param
        ipRows = libdb.LibDB().query_all_by_condition(sql)
        for ip in ipRows:
            logger.info(ip)
            info = dict()
            name                    = ip[1]
            info['id']              = ip[0]
            info['addr']            = ip[1]
            info['areaid']          = ip[2]
            info['postcode']        = ip[4]
            info['submission_date'] = _now()
            if libredis.LibRedis(CONF['redis']['ipdb']).hashMSet(name, info):
                logger.info('插入到redis成功')
                num +=1
            else:
                logger.error('插入到redis失败')
    
    return num

def updateIptbPostcode():
    '''
    mysql 中iptb新增了postcode字段，需要将postcode字段从area表中更新过来。
    读iptb表项中的areaid,然后查询area表项，获取postcode填入iptb中。
    后续以postcode作为地区标识码
    return:
        num: 更新成功数量
    '''
    num = 0
    #使用分页查询
    page_size = 1000
    condition = " postcode='0' "
    total = queryIPCountByCondition(condition)
    if total == 0:
        return num
    
    page  = total / page_size
    page1 = total % page_size
    if page1 != 0:
        page = page + 1
    
    for p in range(0, page):
        limit_param = ' limit ' + str(p * page_size) + ',' + str(page_size)
        sql = 'select * from ' + CONF['database']['iptb'] +' where ' + condition + limit_param
        ipRows = libdb.LibDB().query_all_by_condition(sql)
        for ip in ipRows:
            logger.info(ip)
            id      = ip[0]
            areaid  = ip[2]
            #查询 areaid 对应的postcode
            area = libdb.LibDB().query_by_id(areaid, CONF['database']['area'])
            if area == False or area == None:
                continue
            postcode = area[4]
            #更新进入表项
            setval = "postcode='%s'" %(postcode)
            condition = "id=%s" %(id)
            logger.debug('setval:%s, condition:%s', setval, condition)
            if libdb.LibDB().update_db(setval, condition, CONF['database']['iptb']) :
                num += 1
    
    return num

def _saveAccountToFile(line,file):
    """
    功能：写行内容到文件中
    :param line: 账号内容
    :return: 无
    """
    if file == '':
        logger.error('输出账号文件为空')
        return
    str = file.split('.')
    fileName = str[0] + time.strftime('%Y-%m-%d') +'.'+ str[1]
    logger.info('SaveAccountToFile: %s', fileName)
    f = open(fileName, 'a+')
    f.writelines(line + '\n')
    f.close()
    logger.info('账号写入文件：%s',line)

def compareIpDB():
    '''
    将数据库中通过付费api接口获取的ip区域记录和ipip.net的离线数据库进行对比，结果写入一个文件
    '''
    db = ipdb.City(CONF['ipdb'])
    num = 0
    #使用分页查询
    page_size = 1000
    condition = " postcode!='0' "
    total = queryIPCountByCondition(condition)
    if total == 0:
        return num
    
    page  = total / page_size
    page1 = total % page_size
    if page1 != 0:
        page = page + 1
    
    for p in range(0, page):
        limit_param = ' limit ' + str(p * page_size) + ',' + str(page_size)
        sql = 'select * from ' + CONF['database']['iptb'] +' where ' + condition + limit_param
        ipRows = libdb.LibDB().query_all_by_condition(sql)
        for ip in ipRows:
            logger.info(ip)
            id      = ip[0]
            areaid  = ip[2]
            addr    = ip[1]
            #查询 areaid 对应的postcode
            area = libdb.LibDB().query_by_id(areaid, CONF['database']['area'])
            if area == False or area == None:
                continue
            postcode = area[4]
            province = area[1]
            city     = area[2]
            localArea = db.find_map(addr, "CN")
            if city == localArea['city_name']:
                line = '%s %s %s %s %s 匹配' %(addr, province,city, localArea['region_name'], localArea['city_name'])
            else:
                line = '%s %s %s %s %s 错配' %(addr, province,city, localArea['region_name'], localArea['city_name'])
            _saveAccountToFile(line,'ip.txt')
            num +=1
    return num

logger = gl.get_logger()
CONF   = gl.get_conf()

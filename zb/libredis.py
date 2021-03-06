#!/usr/bin/python
#-*- coding: UTF-8 -*-
# FileName : libredis.py
# Author   : Shan
# DateTime : 2019/1/23
# SoftWare : PyCharm

from redis import StrictRedis
import time
import inits
import globalvar as gl

global CONF
global logger

class LibRedis():
    def __init__(self,user=0):
        db = user % 16
        self.redis = StrictRedis(host=CONF['redis']['host'], port=CONF['redis']['port'], db=db)
        #self.redis = StrictRedis(host=CONF['redis']['host'], port=CONF['redis']['port'], db=CONF['redis']['db'])

    def strSet(self, key, value):
        """
        设置字符串的键值对
        :param key:
        :param value:
        :return: True or False
        """
        rv = self.redis.set(key,value)
        logger.debug('strSet:%s',rv)
        if rv == 1:
            return True
        else:
            return False

    def strGet(self,key):
        """
        获取字符串键值对
        :param key:
        :return: None 或者键值
        """
        rv = self.redis.get(key)
        logger.debug(rv)
        return rv

    def hashMSet(self,name, map):
        """
        设置字典
        :param name: 字典名称，唯一
        :param map:  字典，dic = {"zcx": "111111", "zcx1": "2222222"}
        :return: True or False
        """
        rv = self.redis.hmset(name,map)
        logger.info("write dict to redis, rv(%s)", rv)
        if rv == 1:
            return True
        else:
            return False

    def hashSet(self, name, key, value):
        """
        设置字典,其中键值
        :param name: 字典名称，唯一
        :param key: 键
        :param value : 值
        :return: True or False
        """
        rv = self.redis.hset(name,key,value)
        if rv == 1:
            return True
        else:
            return False

    def hashGet(self,name,key):
        """
        获取字典name中键为key的值
        :param name:
        :param key:
        :return: None or 键值
        """
        rv = self.redis.hget(name,key)
        logger.info(rv)
        return rv

    def hashGetAll(self,name):
        """
        根据字典的name,获取内容，
        :param name:
        :return: dict or None
        """
        rv = self.redis.hgetall(name)
        return rv

    def hashExists(self,name,key):
        """
        查找字典是否存在某个key
        :param name:
        :param key:
        :return: true or False
        """
        rv = self.redis.hexists(name,key)
        logger.info(rv)
        if rv == 1:
            return True
        else:
            return False

    def hashDel(self,name,*keys):
        """
        删除字典中的一个或多个键
        :param name: 字典名称
        :param key: 字典键，单个键或者多个键。
        :return: 删除数量，没有为0
        """
        rv = self.redis.hdel(name,*keys)
        logger.info(" hashDel return: %d",rv)
        return rv

    def hashincr(self,name,key,amount=1):
        """
        hash 表中键值自加1或者指定数字
        :param name:
        :param key:
        :param amount:
        :return: 键值自加后的结果
        """
        rv = self.redis.hincrby(name,key,amount)
        return rv

    def hashHlen(self,name):
        """
        获取哈希表字段的数量
        :param name:
        :return: 数字，0或者其他数字
        """
        return self.redis.hlen(name)


    def setAdd(self,name,value):
        """
        在集合中增加一个元素
        :param name:
        :param value:
        :return: True or False
        """
        rv = self.redis.sadd(name,value)
        logger.info(rv)
        if rv > 0:
            return True
        else:
            return False

    def setCard(self,name):
        """
        获取集合的成员数
        :param name:
        :return: 数字
        """
        num = self.redis.scard(name)
        logger.info("setCard return(%d)", num)
        return num

    def setSmembers(self,name):
        """
        获取所有的元素
        :param name:
        :return: None or string
        """
        rv = self.redis.smembers(name)
        logger.info(rv)
        return rv

    def setSpop(self,name):
        """
        移除并返回集合中的一个随机元素
        :param name:
        :return:
        """
        rv = self.redis.spop(name)
        logger.info(rv)
        return rv

    def setSunionstore(self,dst,source):
        """
        将source复制到dst
        :param dst:
        :param source:
        :return: the number of keys in the new set.
        """
        rv = self.redis.sunionstore(dst,source,'temp')
        logger.info(rv)
        return rv

logger = gl.get_logger()
CONF   = gl.get_conf()

"""
if __name__ == '__main__':
    crack = LibRedis()
    rv = crack.strSet('name', 'Hello World')
    print(crack.strGet('name'))
    test = dict(name='cooper', family='Liu')
    rv = crack.hashMSet('my', test)
    print(rv)
    test = crack.hasGetAll('my')
    print(test)
    crack.hashSet('my', 'sex', 'mail')
    test = crack.hasGetAll('my')
    print(test)
    crack.hashSet('my', 'sex', 'femeal')
    test = crack.hasGetAll('my')
    print(test)

    rv = crack.setAdd('redis', 'cooper')
    print(rv)
    print(crack.setCard('redis'))
    print(crack.setSmembers('redis'))
    rv = crack.setAdd('redis', 'family')
    print(rv)
    print(crack.setCard('redis'))
    print(crack.setSmembers('redis'))
    crack.setSunionstore('dst', 'cknnsetconst')
"""
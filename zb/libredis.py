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

class LibRedis(db=0):
    def __init__(self):
        self.redis = StrictRedis(host=CONF['redis']['host'], port=CONF['redis']['port'], db=db, password=CONF['redis']['password'])

    def strSet(self, key, value):
        rv = self.redis.set(key,value)
        logger.debug('strSet:%s',rv)
        return rv

    def strGet(self,key):
        """
        :param key:
        :return: None 或者键值
        """
        rv = self.redis.get(key)
        logger.debug(rv)
        return rv

logger = gl.get_logger()
CONF   = gl.get_conf()
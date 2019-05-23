#!/usr/bin/python
#-*- coding: UTF-8 -*-
# FileName : libdb.py
# Author   : Shan
# DateTime : 2019/1/9
# SoftWare : PyCharm

import pymysql
import time
import inits
import globalvar as gl

global CONF
global logger

class LibDB():
    def __init__(self):
        self.cong = pymysql.connect(host='127.0.0.1',
                                    port=3306,
                                    user='root',
                                    password=CONF['database']['passwd'],
                                    database=CONF['database']['db'],
                                    charset='utf8')
        self.curg = self.cong.cursor()

    def __del__(self):
        self.curg.close()
        self.cong.close()

    def query_count(self,db_table):
        sql = "select count(*) from %s" % (db_table)
        logger.info("%s",sql)
        try:
            self.curg.execute(sql)
            sql_rows = self.curg.fetchone()
            logger.debug('query_count: %s', sql_rows)
        except:
            logger.exception('Insert operation error')
            return False

        return sql_rows

    def query_count_by_condition(self,condition, db_table):
        sql = "select count(*) from %s where %s" % (db_table, condition)
        logger.info("%s",sql)
        try:
            self.curg.execute(sql)
            sql_rows = self.curg.fetchone()
            logger.debug('query_count: %s', sql_rows)
        except:
            logger.exception('Insert operation error')
            return False

        return sql_rows

    def query_num(self, num, db_table):
        sql = "select * from %s limit %d" % (db_table, num)
        logger.info("%s",sql)
        try:
            self.curg.execute(sql)
            sql_rows = self.curg.fetchall()
        except:
            logger.exception('Insert operation error')
            return False
        logger.debug(sql_rows)

        return sql_rows

    def query_num_by_condition(self, num,condition, db_table):
        sql = "select * from %s  where %s limit %d" % (db_table, condition, num)
        logger.info("%s",sql)
        try:
            self.curg.execute(sql)
            sql_rows = self.curg.fetchall()
        except:
            logger.exception('Insert operation error')
            return False
        logger.debug(sql_rows)

        return sql_rows

    def query(self,  db_table):
        sql = "select * from %s" % (db_table)
        logger.info("%s",sql)
        try:
            self.curg.execute(sql)
            sql_rows = self.curg.fetchall()
        except:
            logger.exception('Insert operation error')
            return False

        return sql_rows

    def query_all(self, key, value, db_table):
        sql = "select * from %s where %s='%s'" % (db_table, key, value)
        logger.info("%s",sql)
        try:
            self.curg.execute(sql)
            sql_rows = self.curg.fetchall()
        except:
            logger.exception('Insert operation error')
            return False

        return sql_rows

    def query_all_by_condition(self, sql):
        logger.info("%s",sql)
        try:
            self.curg.execute(sql)
            sql_rows = self.curg.fetchall()
        except:
            logger.exception('Insert operation error')
            return False

        return sql_rows

    def query_by_condition(self, condition, db_table):
        sql = "select * from %s where %s" % (db_table, condition)
        logger.info("%s",sql)
        try:
            self.curg.execute(sql)
            sql_rows = self.curg.fetchall()
        except:
            logger.exception('Insert operation error')
            return False

        return sql_rows

    def query_by_id(self, id_str, db_table):
        sql = "select * from %s where id=%s" %(db_table, id_str)
        logger.info("%s",sql)
        try:
            self.curg.execute(sql)
            info = self.curg.fetchone()
        except:
            logger.exception('Insert operation error')
            return False
        return info

    def query_one(self, key, value, db_table):
        sql = "select * from %s where %s='%s'" %(db_table, key, value)
        logger.info("%s",sql)
        try:
            self.curg.execute(sql)
            info = self.curg.fetchone()
        except:
            logger.exception('Insert operation error')
            return False
        return info

    def query_one_by_condition(self, condition, db_table):
        sql = "select * from %s where %s order by rand()" %(db_table, condition)
        logger.info("%s",sql)
        try:
            self.curg.execute(sql)
            info = self.curg.fetchone()
        except:
            logger.exception('Insert operation error')
            return False
        logger.debug(type(info))
        return info


    def insert_db(self, key, value, db_table):
        """
        插入一条表项
        :param key: nickname, password, regdate, lastdate, colddate, cookie
        :param value:'用户52769467', 'HFhz9tbH', 1546943718, 1546943718, 1546943718, 'cookie'
        :param db_table:
        :return:
        """
        sql = 'INSERT INTO `%s` ( %s ) VALUES( %s );' %(db_table, key, value)
        try:
            self.curg.execute(sql)
            self.cong.commit()
        except:
            logger.exception('Insert operation error')
            return False

        logger.info('写入一条cookie进入数据库')
        return True

    def update_db(self, setval, condition,db_table):
        """
        更新表项
        :param setval: 更新值，例如：cookie='22222'
        :param condition: 更新的索引，例如：nickname='用户123456'
        :param db_table: 表项名称
        :return:
        """
        sql = "UPDATE %s set %s where %s;" % (db_table, setval, condition)
        logger.debug(sql)
        try:
            self.curg.execute(sql)
            self.cong.commit()
        except:
            logger.exception('Update operation error')
            return False

        logger.info('更新一条cookie进入数据库')
        return True

    def del_db(self,condition,db_table):
        sql = 'DELETE FROM %s %s;' % (db_table, condition)
        try:
            self.curg.execute(sql)
            self.cong.commit()
        except:
            logger.exception('Insert operation error')
            return False

        logger.info('删除一条表项成功')
        return True

    def check_acc(self,db_table,username,password):
        sql = "SELECT * from %s where username='%s' and password='%s'" %(db_table,username,password)
        logger.info("%s",sql)
        try:
            self.curg.execute(sql)
            info = self.curg.fetchone()
        except:
            logger.exception('Check_acc operation error')
            return False
        logger.info(info)
        return info

    def min_key(self, key, db_table):
        sql = "select min(%s) from %s" %(key, db_table)
        logger.info("%s",sql)
        try:
            self.curg.execute(sql)
            info = self.curg.fetchone()
        except:
            logger.exception('Insert operation error')
            return False
        return info

    def max_key(self, key, db_table):
        sql = "select max(%s) from %s" %(key, db_table)
        logger.info("%s",sql)
        try:
            self.curg.execute(sql)
            info = self.curg.fetchone()
        except:
            logger.exception('Insert operation error')
            return False
        return info

    def min_key_of_condition(self, key, db_table, condition):
        sql = "select min(%s) from %s where %s" %(key, db_table, condition)
        logger.info("%s",sql)
        try:
            self.curg.execute(sql)
            info = self.curg.fetchone()
        except:
            logger.exception('Insert operation error')
            return False
        return info

    def max_key_condition(self, key, db_table, condition):
        sql = "select max(%s) from %s where %s" %(key, db_table, condition)
        logger.info("%s",sql)
        try:
            self.curg.execute(sql)
            info = self.curg.fetchone()
        except:
            logger.exception('Insert operation error')
            return False
        return info
        

logger = gl.get_logger()
CONF   = gl.get_conf()
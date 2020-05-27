#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
import httplib2
from urllib.parse import urlencode #python3
#from urllib import urlencode #python2

params = urlencode({'ip':'27.18.150.201','datatype':'jsonp'})
url = 'http://api.ip138.com/query/?'+params
headers = {"token":"dd333cd32f6e51e2893577cc9ee1a681"}#token为示例
http = httplib2.Http()
response, content = http.request(url,'GET',headers=headers)
print(content.decode("utf-8"))
'''

import requests,json,sys
from urllib import urlencode

def getAreaInfo(ip):
        """
        功能：从第三方接口获取ip的地址信息
        输入参数：
                ip： IP地址
        返回值： 
                none
        """
        ou = dict(error=0, data=dict(), msg='ok')
        params = urlencode({'ip':ip,'datatype':'jsonp'})
        url = 'http://api.ip138.com/query/?'+params
        payload = dict(token="dd333cd32f6e51e2893577cc9ee1a681")
        print(url)
        r = requests.get(url,params=payload)
        print(r)
        #logger.debug('接码平台链接: %s', r.url)
        ##判断http post返回值
        if r.status_code != requests.codes.ok:
            #logger.error('get 失败,r.status_code=%d', r.status_code)
            ou['error'] = '1'
            ou['msg']   = 'HTTP GET 失败'
            return ou
        #logger.debug('get 成功, r.status_code=%d', r.status_code)

        responsed = r.json()
        print(responsed)
        print(responsed['data'])
        return ou

getAreaInfo('27.18.150.201')




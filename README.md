# ckadminlte

##douyu cookie 管理后台 V3 版本
V3版本：

1.cookie可以直接存储在数据库mysql中；

2.可以自动更新cookie；

3.可以自动添加cookie；

4.多用户功能,支持多用户，通过url参数区分，最多16个用户。 

user0： 

	http://192.168.100.133:8889/useradmin?user=0 
	http://192.168.100.133:8889/useradmin/cookie?user=0

user1: 
 
	http://192.168.100.133:8889/useradmin?user=1 
	http://192.168.100.133:8889/useradmin/cookie?user=1

user15:

	http://192.168.100.133:8889/useradmin?user=15 
	http://192.168.100.133:8889/useradmin/cookie?user=15

5.用户的cookie可以直接存储在redis db中；

6.支持提交任务，任务提交在用户页面；

7.总控制台
	
	http://192.168.100.133:8889/admin

8.总控制台增加用户登录管理功能

启动命令：
	
	cd zb
	gunicorn -c gunicorn.py app:app &
##任务分发模块：

1.使用tcp方式；

2.支持并发模式；

3.用户端直接请求任务，然后从管理后台获取cookie

启动命令：

	python taskServerV2.py &
	
##用户ck自动重置模块：

1.使用定时器模式；

2.在任务开始前两分钟内重置将要使用的cookie

启动命令：
	python ckReset.py &

--------------------------------------------------------------------
V1版本特征及问题：

1.直接使用flask调试模式；

2.cookie上传直接存储在内存中；

3.并发情况下响应非常慢,大量报错，错误如下：
	self._sock.sendall(view[write_offset:write_offset+buffer_size])error: [Errno 32] Broken pipe

关于这个错误的网上说明：

	https://github.com/hanc00l/wooyun_public/issues/13

官方的说明：

	http://flask.pocoo.org/docs/1.0/deploying/wsgi-standalone/

解决方案,前端使用WSGI容器，命令如下：

	gunicorn -w 2 -b :8100  cookie:app  &

但是使用这个方案，gunicorn就会启用多个flask进程去处理请求，cookie在内存中无法共享。

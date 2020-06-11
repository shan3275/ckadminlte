# ckadminlte
##douyu cookie 管理后台 V4 版本

V4版本：

1. 未使用cookie存放在redis中；
2. 已经使用cookie存放在mysql中，表项记录使用的ip及地域信息，地域信息的获取支持通过在线api获取或者通过本地IP库获取；
3. 增加任务统计，按照房间以小时段进行统计，写入mysql；
4. 提交任务之间在后台中执行，无需再分端口进行；
5. 增加ck分组功能。上传ck时，默认分组是G0，新的分组建议修改为G1，G2，以此类推；缓存中ck，会进行分组，DB中ck也会进行分组；客户端请求ck，默认请求G0分组ck。如果需求请求其他分组，在提交任务的时候，请求ck链接中带上分组参数，参数为grp=Gx，例如：
http://127.0.0.1:8000/useradmin/cookie?user=0&id=user001591086071000&grp=G1

--------------------------------------------------------------------
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

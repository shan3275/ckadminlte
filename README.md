# ckadminlte

douyu cookie 管理后台 V2 版本
V2版本：
1.cookie直接存储在redis数据库中
2.前端使用gunicorn
3.启动命令：gunicorn -w 2 -b :8889 -t 300 app:app
4.一个用户需要起一个端口，多用户启动多个实体。 在配置文件yaml.conf中绑定redis的不同db,以实现区分

--------------------------------------------------------------------------------
V3版本：
1.cookie可以直接存储在数据库mysql中；
2.可以自动更新cookie；
3.可以自动添加cookie；
未实现功能：
1.多用户功能
---------------------------------------------------------------------------------
V1版本特征及问题：
1.直接使用flask调试模式；
2.cookie上传直接存储在内存中；
3.并发情况下响应非常慢,大量报错，错误如下：
    self._sock.sendall(view[write_offset:write_offset+buffer_size])
error: [Errno 32] Broken pipe
关于这个错误的网上说明：https://github.com/hanc00l/wooyun_public/issues/13
官方的说明：http://flask.pocoo.org/docs/1.0/deploying/wsgi-standalone/
解决方案,前端使用WSGI容器，命令如下：
gunicorn -w 2 -b :8100  cookie:app  &
但是使用这个方案，gunicorn就会启用多个flask进程去处理请求，cookie在内存中无法共享。

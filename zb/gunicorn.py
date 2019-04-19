import multiprocessing

bind = ":8200"
workers = multiprocessing.cpu_count() * 2 + 1
timeout = 300
worker_class = 'gevent'
loglevel = 'info'
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'
accesslog = "gunicorn_access.log"
errorlog =  "gunicorn_error.log"
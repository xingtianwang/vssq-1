#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: gun.py.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 16/10/10
# *************************************************************************
import gevent.monkey
import multiprocessing

gevent.monkey.patch_all()

bind = '0.0.0.0:9103'
# restart workers when code change, only use in development
#reload = True

preload_app = True

# debug when development and error when production
loglevel = 'error'
logfile = 'log/debug.log'
accesslog = 'log/access.log'
access_log_format = '%(h)s %(t)s %(U)s %(q)s'
errorlog = 'log/error.log'
# process name
proc_name = 'vssq-server'

pidfile = 'log/gunicorn.pid'
# set process daemon, not use in default
# daemon = True
timeout = 60

# number of processes
workers = multiprocessing.cpu_count() * 2 + 1
# number of threads of per process
threads = multiprocessing.cpu_count() * 2
worker_class = 'gevent'

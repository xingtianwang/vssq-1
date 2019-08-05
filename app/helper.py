#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: helper.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 16/9/27
# *************************************************************************
import json
import logging
import os
import re
import threading
from datetime import datetime
from threading import Thread

import gevent
from flask import render_template, current_app, request
from flask_mail import Message
from gevent.pool import Pool
from crontab import CronTab

from . import mail, db
from .auth.models import AdminLog


def send_mail(to, subject, template, attachments=None, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + subject,
                  recipients=to, sender=app.config['MAIL_SENDER'])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    if attachments is not None:
        for attachment in attachments:
            file_name = os.path.basename(attachment)
            with app.open_resource(attachment) as fp:
                msg.attach(file_name, content_type='text/plain', data=fp.read())

    def send_mail_async(message):
        with app.app_context():
            mail.send(message)

    thr = Thread(target=send_mail_async, args=[msg])
    thr.start()


def add_admin_log(user, actions, client_ip, results):
    log = AdminLog()
    log.username = user
    log.actions = actions
    log.client_ip = client_ip
    log.results = results
    db.session.add(log)
    db.session.commit()


def check_phone_num(phone_num):
    if len(phone_num) == 11 and phone_num.isdigit():
        return True
    else:
        return False


def check_imei(imei):
    if len(imei) < 14 or len(imei) > 17:
        return False
    else:
        return True


def allowed_file(filename):
    """检查文件的后缀名是否符合规范
    @param ：文件名
    @return: 文件归属于那种平台，IOS, Android或者都不属于返回'Wrong'

    """
    return '.' in filename and filename.rsplit('.', 1)[1] in set(['apk', 'json', 'jar'])


# log  debug level = 0
def print_log(action, function, branch, api_version, imei=None, data=None):
    if current_app.config['LOG_FLAG'] <= 0:
        log_msg = 'DEBUG ' + action + ' ' + function + '@' + branch + '@api_' + \
              api_version
        if imei is not None:
            log_msg += '-' + imei + '-'
        if data is not None:
            log_msg += '-' + data + '-'
        log_msg += '@' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' END'
        print(log_msg)


# log info level = 1
def print_info(action, function, branch, api_version, imei=None, data=None):
    if current_app.config['LOG_FLAG'] <= 1:
        log_msg = 'INFO ' + action + ' ' + function + '@' + branch + '@api_' + \
              api_version
        if imei is not None:
            log_msg += '-' + imei + '-'
        if data is not None:
            log_msg += '-' + data + '-'
        log_msg += '@' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' END'
        print(log_msg)


# log warn level = 2
def print_warn(action, function, branch, api_version, imei=None, data=None):
    if current_app.config['LOG_FLAG'] <= 2:
        log_msg = 'WARN ' + action + ' ' + function + '@' + branch + '@api_' + \
              api_version
        if imei is not None:
            log_msg += '-' + imei + '-'
        if data is not None:
            log_msg += '-' + data + '-'
        log_msg += '@' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' END'
        print(log_msg)


# log error level = 3
def print_error(action, function, branch, api_version, imei=None, data=None):
    if current_app.config['LOG_FLAG'] <= 3:
        log_msg = 'ERROR ' + action + ' ' + function + '@' + branch + '@api_' + \
              api_version
        if imei is not None:
            log_msg += '-' + imei + '-'
        if data is not None:
            log_msg += '-' + data + '-'
        log_msg += '@' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' END'
        print(log_msg)


def check_file_version(file_dir, file_version):
    f = open(file_dir)
    res = json.loads(f.read())
    f.close()
    for item in res:
        if 'version' in item and item['version'] == file_version:
            return True
    return False


# class Scheduler(object):
#
#     def __init__(self, function, sleep_time=60):
#         self._function = function
#         self._sleep_time = sleep_time
#         self._timer = None
#
#     def start(self):
#         if self._timer is None:
#             self._timer = Timer(2, self._run)
#             self._timer.start()
#         else:
#             Exception('timer already running')
#
#     def _run(self):
#         self._function()
#         self._timer = Timer(self._sleep_time, self._run)
#         self._timer.start()
#
#     def stop(self):
#         if self._timer is not None:
#             self._timer.cancel()
#             self._timer = None


class Interval(object):
    def __init__(self,zt):
        self.is_seconds = False
        if isinstance(zt,int):
            self.per = int(zt)
            self.is_seconds = True
        else:
            self.per = CronTab(zt)
        self.started = True

    def next(self):
        if self.is_seconds:
            return self.per
        return self.per.next()


class Task(object):
    def __init__(self, name, action, timer, *args, **kwargs):
        self.name = name
        self.action = action
        self.timer = timer
        self.args = args
        self.kwargs = kwargs


class Scheduler(object):
    """
    Time-based scheduler
    """
    def __init__(self, logger_name='greenlock.task'):
        self.logger_name = logger_name
        self.tasks = []
        self.active = {}  # action task name registry
        self.waiting = {}  # action task name registry
        self.running = True

    def schedule(self, name, timer, func, *args, **kwargs):
        self.tasks.append(Task(name, func, timer, *args, **kwargs))
        self.active[name] = []  # list of greenlets
        self.waiting[name] = []

    def unschedule(self, task_name):
        for greenlet in self.waiting[task_name]:
            try:
                gevent.kill(greenlet)
            except BaseException:
                pass

    def stop_task(self, task_name):
        for greenlet in self.active[task_name]:
            try:
                gevent.kill(greenlet)
                self.active[task_name] = []
            except BaseException:
                pass

    def _remove_dead_greenlet(self, task_name):
        for greenlet in self.active[task_name]:
            try:
                # Allows active greenlet continue to run
                if greenlet.dead:
                    self.active[task_name].remove(greenlet)
            except BaseException:
                pass

    def run(self, task):
        self._remove_dead_greenlet(task.name)
        greenlet_ = gevent.spawn(task.action, *task.args, **task.kwargs)
        self.active[task.name].append(greenlet_)
        try:
            greenlet_later = gevent.spawn_later(task.timer.next(), self.run, task)
            self.waiting[task.name].append(greenlet_later)
            return greenlet_, greenlet_later
        except StopIteration:
            pass
        except Exception:
            pass
        return greenlet_, None

    def run_tasks(self):
        pool = Pool(len(self.tasks))
        for task in self.tasks:
            pool.spawn(self.run, task)
        return pool

    def daemon(self,flag=False):
        if flag:
            self.run_forever
        else:
            my_thread = threading.Thread(target=self.run_forever)
            my_thread.start()

    def run_forever(self):
        try:
            task_pool = self.run_tasks()
            while self.running:
                gevent.sleep(seconds=0.1)
            task_pool.join(timeout=30)
            task_pool.kill()
        except KeyboardInterrupt:
            task_pool.closed = True
            task_pool.kill()
            logging.getLogger(self.logger_name).info('Time scheduler quits')

    def stop(self):
        self.running = False


def transform_num(phone_num):
    """ 使用手机号后10位，生成10位邀请码 """
    phone = list(phone_num[1:])
    a = 1
    b = 2
    c = 3
    d = 4
    phone[0] = str((int(phone[0]) + a) % 10)
    phone[3] = str((int(phone[3]) + b) % 10)
    phone[6] = str((int(phone[6]) + c) % 10)
    phone[9] = str((int(phone[9]) + d) % 10)
    share_code = ''.join(phone)
    return share_code


def paging(result_data):
    cur_page = request.args.get('cur_page', type=int)
    if not cur_page:
        cur_page = 1

    cur_page = int(cur_page)
    page_size = request.args.get('page_size', current_app.config['RECORDS_PER_PAGE'])

    if not page_size:
        page_size = current_app.config['RECORDS_PER_PAGE']
    page_size = int(page_size)

    if result_data % page_size == 0:
        page_num = result_data / page_size
    else:
        page_num = result_data / page_size + 1
    page_num = int(page_num)
    total = result_data
    start_idx = page_size * (cur_page - 1)
    end_idx = page_size * cur_page
    if end_idx > total:
        end_idx = total

    return start_idx, end_idx, cur_page, page_num, page_size, total

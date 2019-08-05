#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: utils.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 2016/11/17
# *************************************************************************
import datetime
import hashlib
import os
import random
import string
from json import dumps

import requests
from flask import Response
from flask import current_app
from flask import json
from sqlalchemy import func

from app import db, celery, cache, redis, cache_simple
from app.helper import check_imei, print_error, print_info
from app.manage.models import BlackList, WhiteImeiList
from .errors import ErrorCode
from .models import UserInfo, DeviceInfo, ActivateMembers, AppVersion, AppList, AvatarVersion, ChannelVersion, \
    BusinessType, \
    BiReport, BiMonthReport, BiReportProtocol


def validate_client(imei, app_version, function):
    if not check_imei(imei):
        print_error(action='Response', function=function, branch='IMEI_INVALID', api_version='v1.0', imei=imei)
        return {'head': ErrorCode.IMEI_INVALID}

    if app_version not in get_valid_channel_version_name() and app_version not in get_valid_avatar_version_name() \
            and imei not in get_white_imei_list():
        print_error(action='Response', function=function, branch='APP_INVALID', api_version='v1.0', imei=imei)
        return {'head': ErrorCode.APP_INVALID}

    if imei in get_back_imei_list():
        print_info(action='Response', function=function, branch='BLACK_IMEI', api_version='v1.0', imei=imei)
        return {'head': ErrorCode.BLACK_IMEI}

    return "valid"


def validate_client_no_imei(imei, app_version, function):
    if app_version not in get_valid_channel_version_name() and app_version not in get_valid_avatar_version_name() \
            and imei not in get_white_imei_list():
        print_error(action='Response', function=function, branch='APP_INVALID', api_version='v1.0', imei=imei)
        return {'head': ErrorCode.APP_INVALID}

    if imei in get_back_imei_list():
        print_info(action='Response', function=function, branch='BLACK_IMEI', api_version='v1.0', imei=imei)
        return {'head': ErrorCode.BLACK_IMEI}

    return "valid"


def validate_app_exception(imei, app_version, function):
    if app_version not in get_app_version_list() and app_version not in get_valid_avatar_version_name() \
            and imei not in get_white_imei_list():
        print_error(action='Response', function=function, branch='EXCEPTION_APP_INVALID', api_version='v1.0',
                    imei=imei)
        return {'head': ErrorCode.EXCEPTION_APP_INVALID}

    return "valid"


def gen_order_num():
    return datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S') + \
           ''.join(random.sample(string.ascii_letters + string.digits, 18))


def gen_vip_order_num():
    return 'vip' + datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S') + \
           ''.join(random.sample(string.ascii_letters + string.digits, 15))


def gen_avatar_vip_order_num():
    return 'ava' + datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S') + \
           ''.join(random.sample(string.ascii_letters + string.digits, 15))

def gen_free_vip_order_num():
    return 'free' + datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S') + \
           ''.join(random.sample(string.ascii_letters + string.digits, 15))


def gen_business_vip_order_num():
    return 'Buss' + datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S') + \
           ''.join(random.sample(string.ascii_letters + string.digits, 14))


def gen_key_order_num():
    return 'key' + datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S') + \
           ''.join(random.sample(string.ascii_letters + string.digits, 15))


def create_key():
    st = 'abcdefghijkelmnopqrstuvwxyzABCDEFGHIJKELMNOPQRSTUVWXYZ0123456789'
    key = 'VSSQ' + ''.join(random.sample(st, 12))
    return key


def gen_notice():
    return 'n' + datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S') + \
           ''.join(random.sample(string.ascii_letters + string.digits, 15))


def report_toutiao(imei):
    from app.api_1_0.models import TouTiaoAdsClickInfo
    md = hashlib.md5()
    md.update(bytes(imei, 'utf-8'))
    imei_md5 = md.hexdigest()
    toutiaoads = TouTiaoAdsClickInfo.query.filter_by(imei=imei_md5, status=0).all()
    for toutiaoad in toutiaoads:
        r = requests.get(url=toutiaoad.callback_url)
        toutiaoad.status = 1
        toutiaoad.last_seen = datetime.datetime.now()
        db.session.add(toutiaoad)
    db.session.commit()


def add_month(src_datetime, months):
    if not src_datetime or not months or months > 12:
        return None
    src_year = src_datetime.year
    month = (src_datetime.month + months)
    year = src_year + month // 13
    new_month = month % 12 if month != 12 else month
    if month == 24:
        new_month = 12
    day = src_datetime.day

    month_list = [1, 3, 5, 7, 8, 10, 12]
    if src_datetime.month in month_list and day == 31 and new_month not in month_list:
        day = 30

    # 闰年
    if year % 400 == 0 or (year % 100 != 0 and year % 4 == 0):
        if new_month == 2 and day >= 29:
            day = 29
    elif new_month == 2 and day >= 29:
        day = 28
    return datetime.datetime(year=year, month=new_month, day=day, hour=src_datetime.hour,
                             minute=src_datetime.minute, second=src_datetime.second)


@celery.task()
def add_all_vip(ware_id, channel):
    members = UserInfo.query.join(DeviceInfo, UserInfo.imei == DeviceInfo.imei). \
        filter(DeviceInfo.status == 1, DeviceInfo.market == channel).all()
    db.session.close()
    with db.session.no_autoflush:
        for member in members:
            act_member = ActivateMembers()
            act_member.godin_id = member.godin_id
            act_member.ware_id = ware_id
            act_member.channel = channel
            db.session.add(act_member)
        try:
            db.session.commit()
        except Exception as ee:
            print(ee)
            db.session.rollback()
    return True


@cache_simple.cached(timeout=60, key_prefix='get_black_imei_list')
def get_back_imei_list():
    return [x.imei for x in BlackList.query.all()]


@cache.cached(timeout=3600, key_prefix='get_valid_app_version_name')
def get_valid_app_version_name():
    return [version_name[0] for version_name in
            db.session.query(AppVersion.version_name.distinct()).filter(AppVersion.is_released == True)]


@cache.cached(timeout=3600, key_prefix='get_valid_channel_version_name')
def get_valid_channel_version_name():
    return [version_name[0] for version_name in
            db.session.query(ChannelVersion.version_name.distinct()).filter(ChannelVersion.is_released == True)]


@cache.cached(timeout=3600, key_prefix='get_valid_avatar_version_name')
def get_valid_avatar_version_name():
    return [version_name[0] for version_name in
            db.session.query(AvatarVersion.version_name.distinct()).filter(AvatarVersion.status == 2)]


@cache_simple.cached(timeout=60, key_prefix='get_white_imei_list')
def get_white_imei_list():
    return [x.imei for x in WhiteImeiList.query.all()]


@cache.cached(timeout=518400, key_prefix='get_app_version_list')
def get_app_version_list():
    ret = []
    new_channel_list = [(value[0], value[1]) for value in db.session.query(
        ChannelVersion.app_type, func.max(ChannelVersion.version_code)).filter(
        ChannelVersion.is_released == True).group_by(ChannelVersion.app_type)]

    for value in new_channel_list:
        ret += [version_name[0] for version_name in db.session.query(ChannelVersion.version_name).filter(
            ChannelVersion.app_type == value[0], ChannelVersion.version_code == value[1])]

    return ret


@cache.cached(timeout=3600, key_prefix='get_app_list')
def get_app_list():
    return [x.package_name for x in AppList.query.all()]


def get_lock(key, timeout=10, user_wait_timeout=15):
    import time
    _lock, lock_key = 0, "%s_dynamic_lock" % key

    wait_timestamp = int(time.time()) + user_wait_timeout
    while _lock != 1:
        timestamp = int(time.time() + timeout)

        # 延时11秒
        _lock = redis.setnx(lock_key, timestamp)
        # 如果持有锁，当前时间大于过期时间，说明已经超时了
        if _lock == 1:
            redis.expire(lock_key, int(time.time()) + timeout)

            return 'success', lock_key

        lock_key_time = redis.get(lock_key)

        if lock_key_time:
            if int(time.time()) > int(lock_key_time):
                new_time = redis.getset(lock_key, int(time.time()) + timeout)
                if not new_time or lock_key_time == new_time:
                    redis.expire(lock_key, int(time.time()) + timeout)
                    return 'success', lock_key
            else:
                if int(time.time()) > wait_timestamp:
                    return 'timeout', lock_key
                time.sleep(0.1)

        else:
            if int(time.time()) > wait_timestamp:
                return 'timeout', lock_key

            time.sleep(0.3)


def release(lock_key):
    if redis.get(lock_key):
        redis.delete(lock_key)


def get_response(data):
    response = Response(json.dumps(data), mimetype='application/json')
    response.headers.add_header('Accept-Encoding', 'gzip, deflate')
    return response


@cache.cached(timeout=60 * 60 * 12, key_prefix='feature_file')
def feature_file():
    app_query = ChannelVersion.query.filter_by(app_type=99)
    version_info = app_query.order_by(ChannelVersion.version_code.desc())

    res = dict()
    for version in version_info:
        value = res.get(version.version_name, 'no')
        if value != 'no':
            res[version.version_name].append(version)
        else:
            data_list = list()
            data_list.append(version)
            res[version.version_name] = data_list
    # for key, value in res.items():
    #     print(key)
    #     for val in value:
    #         print(val.app_dir)
    return res


def get_imei(imei_list):
    imei_list = list(set(imei_list))
    imei = [imei for imei in imei_list if len(imei) <= 15 and len(imei) >= 14]
    return imei[0:4]


@cache.cached(timeout=60 * 60 * 12, key_prefix='get_app_version')
def get_app_version():
    ver_query = ChannelVersion.query.filter_by(app_type=8). \
        order_by(ChannelVersion.version_code.desc())
    ver_query = ver_query.filter_by(is_released=True)

    app_version = ver_query.first()
    return app_version


@cache.cached(timeout=60 * 60 * 12, key_prefix='get_app_version_white')
def get_app_version_white():
    ver_query = ChannelVersion.query.filter_by(app_type=8). \
        order_by(ChannelVersion.version_code.desc())

    app_version = ver_query.first()
    return app_version


@cache.cached(timeout=60 * 60 * 12, key_prefix='get_business_type')
def get_business_type():
    type_info = BusinessType.query.all()
    res = dict()
    for info in type_info:
        res[info.number] = info.name

    return res


def is_Chinese(word):
    # 判断是否含有中文
    for ch in str(word):
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


@celery.task()
def read_report_d(target_date):
    # 通过celery异步不能传递格式化时间对象
    new_date = datetime.datetime.strptime(target_date, '%Y%m%d').date()

    name = os.path.join(os.getcwd(), current_app.config['STATISTICS_TAG'], 'bi', target_date, 'report_d.json')
    if os.path.exists(name):
        print('read_report_d file exist '+target_date)
    else:
        print('read_report_d file not exist')
        return True

    if BiReport.query.filter_by(record_time=target_date).limit(1).first() is not None:
        print('read_report_d already exist')
        return True

    dbreports = BiReportProtocol.query.filter_by(status=1).all()
    for re in dbreports:
        cache.set(str(re.we_id), '1', timeout=60 * 10)
        redis.lpush("BiReportProtocol", str(re.we_id))

    bi_default = BiReport()
    with open(os.path.join(os.getcwd(), current_app.config['STATISTICS_TAG'], 'bi',
                           target_date, 'report_d.json'), 'r') as file:
        data = file.readlines()
        for report in data:
            try:
                report = json.loads(report)

                if report['we_id'] != 'default':
                    data = cache.get(report['we_id'])
                    if data:
                        bi_report = BiReport()
                        bi_report.record_time = report['record_time']
                        bi_report.we_id = report['we_id']
                        bi_report.rank_index = report['rank_index']
                        bi_report.latent_consumer_index = report['latent_consumer_index']
                        bi_report.activite_consumer_index = report['activite_consumer_index']
                        bi_report.extend_work_heat = report['extend_work_heat']
                        bi_report.sale_work_heat = report['sale_work_heat']
                        bi_report.income_index = report['income_index']
                        bi_report.pay_index = report['pay_index']
                        bi_report.v_webusiness_index = report['v_webusiness_index']
                        db.session.add(bi_report)
                        db.session.commit()
                        cache.set(str(report['we_id']), '2', timeout=60 * 10)
                else:
                    bi_default.record_time = report['record_time']
                    bi_default.we_id = report['we_id']
                    bi_default.rank_index = report['rank_index']
                    bi_default.latent_consumer_index = report['latent_consumer_index']
                    bi_default.activite_consumer_index = report['activite_consumer_index']
                    bi_default.extend_work_heat = report['extend_work_heat']
                    bi_default.sale_work_heat = report['sale_work_heat']
                    bi_default.income_index = report['income_index']
                    bi_default.pay_index = report['pay_index']
                    bi_default.v_webusiness_index = report['v_webusiness_index']

            except Exception as e:
                print('read_report_d: ', e)

        all_data = redis.lrange('BiReportProtocol', 0, -1)

        for key in all_data:
            data = cache.get(key.decode())
            if data == '1':
                bi_report = BiReport()
                bi_report.record_time = bi_default.record_time
                bi_report.we_id = key.decode()
                bi_report.rank_index = bi_default.rank_index
                bi_report.latent_consumer_index = bi_default.latent_consumer_index
                bi_report.activite_consumer_index = bi_default.activite_consumer_index
                bi_report.extend_work_heat = bi_default.extend_work_heat
                bi_report.sale_work_heat = bi_default.sale_work_heat
                bi_report.income_index = bi_default.income_index
                bi_report.pay_index = bi_default.pay_index
                bi_report.v_webusiness_index = bi_default.v_webusiness_index
                db.session.add(bi_report)
                db.session.commit()

            cache.delete(key.decode())
        redis.delete('BiReportProtocol')
    print('read_report_d finish')

    return True


@celery.task()
def read_report_m(target_date):
    # 通过celery异步不能传递格式化时间对象
    new_date = datetime.datetime.strptime(target_date, '%Y%m%d').date()
    year = new_date.year
    month = new_date.month

    name = os.path.join(os.getcwd(), current_app.config['STATISTICS_TAG'], 'bi', target_date, 'report_m.json')
    if os.path.exists(name):
        print('read_report_m file exist')
    else:
        print('read_report_m file not exist')

    if BiMonthReport.query.filter_by(year=year, month=month).first() is not None:
        print('read_report_m already exist')
        return True

    with open(os.path.join(os.getcwd(), current_app.config['STATISTICS_TAG'], 'bi',
                           target_date, 'report_m.json'), 'r') as file:
        data = file.readlines()
        for report in data:
            try:
                report = json.loads(report)
                bi_report = BiMonthReport()
                bi_report.year = int(report['year'])
                bi_report.month = int(report['month'])
                bi_report.year_month = int(str(report['year']) + str(report['month']))
                bi_report.we_id = report['we_id']
                bi_report.rank_index = report['rank_index']
                bi_report.latent_consumer_index = report['latent_consumer_index']
                bi_report.activite_consumer_index = report['activite_consumer_index']
                bi_report.extend_work_heat = report['extend_work_heat']
                bi_report.sale_work_heat = report['sale_work_heat']
                bi_report.income_index = report['income_index']
                bi_report.pay_index = report['pay_index']
                bi_report.v_webusiness_index = report['v_webusiness_index']
                db.session.add(bi_report)
            except Exception as e:
                print('read_report_m: ', e)
        db.session.commit()

    print('read_report_m finish')
    return True


def log_print(event, args, time, ip):
    redis.rpush('invite_share_log', dumps({'event': event, 'args': args, 'time': time, 'ip': ip}))


def deal_float(value):
    # 保留两位小数
    value = float(value)
    return float("%.2f" % value)


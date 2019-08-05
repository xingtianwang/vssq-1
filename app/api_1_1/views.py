#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: views.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 2016/11/17
# *************************************************************************
import base64
import binascii
import datetime
import hashlib
import os
import random
import time
from json import dumps

from ffmpy import FFmpeg
from werkzeug.utils import secure_filename

from app.api_1_0.apktool.conversion_apk import format_apk
from flask import current_app, request
from flask import g
from flask import json
from flask_restful import Resource, reqparse

from app import cache, db, http_auth, redis, cache_simple
from app.api_1_0.ThreadQueue import QueueThread
from app.api_1_0.cash_cat import CashCat
from app.api_1_0.errors import ErrorCode
from app.api_1_0.models import GodinAccount, DeviceInfo, UserInfo, \
    BindRecord, FeedBack, AppVersion, AppList, ExceptionLog, Activity, \
    OpenScreenAds, OpenScreenAdsStatistics, BannerAds, OpenScreenSimulateData, OpenScreenSimulatedUser, VipMembers, \
    MemberWare, MemberWareOrder, \
    CommunicationGroup, InteractiveAds, InteractiveAdsStatistics, \
    BannerRefreshUser, BannerRefreshData, BannerConfig, OpenConfig, InteractiveConfig, ServiceProtocol, VipType, \
    AdsIcon, AvatarVersion, WeAvatar, ActivateMembers, UserKeyRecord, Key, KeyOrder, \
    ChannelVersion, ImeiVip, KeyRecord, KeyChannel, SignData, SignRecord, NoticeRecord, SysNotice, AppVersionCheck, \
    BusinessWare, BusinessMembers, BusinessWareOrder, BusinessType, BusinessPoolOne, DataLock, FriendHistory, OnePool, \
    BusinessRecommend, BusinessGiveStatistics, BusinessSecondPoolOne, VSZL_Customer_Service, VSZL_Service, \
    Free_Experience_Days, UserGeneralize, FunctionHotDot, UploadVoice
from app.api_1_0.sms import SmsWwtl
from app.api_1_0.utils import gen_vip_order_num, validate_client_no_imei, get_response, get_app_version, \
    read_report_d, read_report_m, gen_free_vip_order_num
from app.api_1_0.utils import get_white_imei_list, gen_key_order_num, create_key, gen_avatar_vip_order_num, \
    feature_file, get_imei, get_app_version_white, gen_business_vip_order_num
from app.api_1_0.utils import validate_client, validate_app_exception
from app.helper import check_phone_num, transform_num, print_error, print_info, print_warn, print_log, check_imei
from app.manage.helper import key_is_divide
from app.manage.models import KeyValue, FunctionVideo
from app.weixin_pay.new_weixin_pay import AvatarWexinPay
from app.weixin_pay.weixin_pay import WexinPay

g_api_version = 'v1.1'
queue = QueueThread()


# 登录发送短信接口
class GetAuthSmsApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('phone_num', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('msg_type', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        super(GetAuthSmsApi, self).__init__()

    def post(self):
        """
        1.获取前端传来的参数数据
        2.校验手机号长度和是否为数值
        3.校验imei(唯一设备标识）, app_version(应用版本号） 校验通过返回‘valid’
        4.判断redis获取该手机对应的短信验证码
          1.为空
          2.不为空
        """
        # 日志
        # print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        # 获取前端传来的参数数据
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        phone_num = json_req['phone_num']
        msg_type = json_req['msg_type']
        # 校验手机号长度和是否为数值
        if not check_phone_num(phone_num):
            # print_error(action='Response', function=self.__class__.__name__, branch='PHONE_NUM_INVALID',
            #             api_version=g_api_version, imei=json_req['imei'])
            return get_response({'head': ErrorCode.PHONE_NUM_INVALID})
        # 校验imei(唯一设备标识）, app_version(应用版本号） 校验通过返回‘valid’
        msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
                              function=self.__class__.__name__)
        if msg != 'valid':
            return get_response(msg)
        # 从redis获取该手机对应的短信验证码
        rv = cache.get(phone_num + '_' + msg_type)
        # 如果为空
        if rv is None:
            # 生成6位短信验证码
            rv = ''.join(random.sample('0123456789', 6))
            # 将短信验证码存入redis
            cache.set(phone_num + '_' + msg_type, rv, timeout=60 * 2)
            # 调用第三方工具发送短信验证码
            SmsWwtl().send_template_sms(to=phone_num, content=[rv], template_id=4)
            # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS',
            #            api_version=g_api_version, imei=json_req['imei'])
            return get_response({'head': ErrorCode.SUCCESS})
        # 如果非空
        else:
            # return sms already sent
            # print_warn(action='Response', function=self.__class__.__name__, branch='SMS_SENT',
            #            api_version=g_api_version, imei=json_req['imei'])
            return get_response({'head': ErrorCode.SMS_SENT})


# 注册接口
class RegisterApi(Resource):
    """
    1.获取前端传来的参数数据
    2.校验手机号长度和是否为数值
    3.校验imei(唯一设备标识）, app_version(应用版本号） 校验通过返回‘valid’
    4.从redis获取该手机对应的短信验证码
      1.为空
      2.若从redis取出的手机验证码和前端传来的手机验证码相等
        1.删除redis中的手机验证码
        2.生成设备对象 从存储设备信息
        3.生成用户分享码
        4.添加国鼎账号

      2.不为空

    """
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('phone_num', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('msg_type', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('smsverifycode', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('os_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('device_factory', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('device_model', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('market', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('password', type=str, required=True, help='param missing', location='json')
        super(RegisterApi, self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()
        # 校验手机号长度和是否为数值
        if not check_phone_num(json_req['phone_num']):
            return get_response({'head': ErrorCode.PHONE_NUM_INVALID})
        # 校验imei(唯一设备标识）, app_version(应用版本号） 校验通过返回‘valid’
        msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
                              function=self.__class__.__name__)
        if msg != 'valid':
            return get_response(msg)
        # 从redis获取该手机对应的短信验证码
        rv = cache.get(json_req['phone_num'] + '_' + str(json_req['msg_type']))
        if rv is None:
            return get_response({'head': ErrorCode.SMS_EXPIRED})
        # 校验从redis取出的手机验证码和前端传来的手机验证码是否相等
        elif rv == json_req['smsverifycode']:
            # 如果相等删除redis中的手机验证码
            cache.delete(json_req['phone_num'] + '_' + str(json_req['msg_type']))
            # 查询该手机号的国鼎账号
            godin_account = GodinAccount.query.filter_by(phone_num=json_req['phone_num']).limit(1).first()

            # new device, imei not exists
            # 设备信息 with_lock ?
            new_device_info = DeviceInfo().query.filter_by(imei=json_req['imei']).limit(
                1).first()
            # 设备信息表是否有该手机信息
            # 如果没有
            if new_device_info is None:
                # 生成该手机设备信息对象
                new_device_info = DeviceInfo()
                # 存入渠道信息
                new_device_info.market = json_req['market']
            else:
                new_device_info.ping()  # ？
            new_device_info.from_json(json_req)
            new_device_info.status = True

            # create share_code
            flag = True
            # 通过手机号生成分享码
            share_code = transform_num(json_req['phone_num'])
            # 分享码在微商神器中未使用，所以只是赋值，可以重复
            # while flag:
            #     user_code = UserInfo.query.filter_by(share_code=share_code).limit(1).first()
            #     if user_code is not None:
            #         if json_req['phone_num'] == user_code.godin_account.phone_num:
            #             flag = False
            #     else:
            #         flag = False
            # add a new user
            # 如果不存在该国鼎账号
            if godin_account is None:
                # 新用户分成操作
                key_is_divide(db, json_req['phone_num'], json_req['imei'], True)

                godin_account = GodinAccount(json_req['phone_num'])
                user_info = UserInfo(godin_id=godin_account.godin_id, imei=json_req['imei'])
                user_info.godin_id = godin_account.godin_id
                user_info.godin_account = godin_account
                user_info.password = json_req['password']
                user_info.share_code = share_code

                # 创建会员信息
                vip_member = VipMembers()
                vip_member.godin_id = godin_account.godin_id
                vip_member.channel = json_req['market']
                # 通过key查询到key_record_id 找到该批次赠送的会员时间vip_time
                user_key_record = UserKeyRecord.query.filter_by(imei=json_req['imei'], status=1).limit(1).first()
                if user_key_record is not None:
                    key = Key.query.filter_by(id=user_key_record.key_id).limit(1).first()
                    if key is not None:
                        key_record = KeyRecord.query.filter_by(id=key.key_record_id).limit(1).first()
                        if key_record is not None:

                            if key.give_activate_status == 0:
                                vip_ad_time = 0
                                vip_gold_ad_time = 0
                                vip_member.grade = 0
                                freegod = None
                                freevip = None
                                if key_record.vip_gold_ad_time:
                                    vip_member.grade = 1
                                    vip_gold_ad_time = key_record.vip_gold_ad_time
                                    # 赠送黄金会员
                                    freegod = MemberWareOrder()
                                    freegod.ware_id = 'freegod'
                                    freegod.order_number = gen_free_vip_order_num()
                                    freegod.buyer_godin_id = user_info.godin_id
                                    freegod.pay_type = 2
                                    freegod.ware_price = 0
                                    freegod.discount_price = 0
                                    freegod.discount = 0
                                    freegod.status = 1
                                    freegod.ac_source = 0
                                    freegod.pay_time = datetime.datetime.now()
                                    freegod.start_time = user_key_record.activate_time
                                    freegod.end_time = user_key_record.activate_time + datetime.timedelta(days=vip_gold_ad_time)
                                    freegod.category = 1
                                    freegod.key_record_id = key.key_record_id
                                    freegod.buy_grade = 0

                                if key_record.vip_ad_time:
                                    vip_member.grade = 2
                                    vip_ad_time = key_record.vip_ad_time
                                    # 赠送铂金会员
                                    freevip = MemberWareOrder()
                                    freevip.ware_id = 'freevip'
                                    freevip.order_number = gen_free_vip_order_num()
                                    freevip.buyer_godin_id = user_info.godin_id
                                    freevip.pay_type = 2
                                    freevip.ware_price = 0
                                    freevip.discount_price = 0
                                    freevip.discount = 0
                                    freevip.status = 1
                                    freevip.ac_source = 0
                                    freevip.pay_time = datetime.datetime.now()
                                    freevip.start_time = user_key_record.activate_time
                                    freevip.end_time = user_key_record.activate_time + datetime.timedelta(days=vip_ad_time)
                                    freevip.category = 1
                                    freevip.key_record_id = key.key_record_id
                                    freevip.buy_grade = 1

                                vip_member.valid_time = user_key_record.activate_time + datetime.timedelta(days=vip_ad_time)
                                vip_member.gold_valid_time = user_key_record.activate_time+ datetime.timedelta(
                                    days=vip_gold_ad_time)
                                key.give_activate_status = 1
                                db.session.add(key)
                                db.session.add(vip_member)
                                db.session.commit()
                                if freegod:
                                    db.session.add(freegod)
                                if freevip:
                                    db.session.add(freevip)
            else:
                # 老用户购买新 key 分成操作
                key_is_divide(db, json_req['phone_num'], json_req['imei'], False)

                user_info = godin_account.user_info
                if not user_info.verify_password(password=json_req['password']):
                    user_info.password = json_req['password']

                user_key_record = UserKeyRecord.query.filter_by(imei=json_req['imei'], status=1).order_by(UserKeyRecord.activate_time.desc()).limit(1).first()
                if user_key_record is not None:
                    key = Key.query.filter_by(id=user_key_record.key_id).limit(1).first()
                    if key is not None:
                        key_record = KeyRecord.query.filter_by(id=key.key_record_id).limit(1).first()
                        if key_record is not None:
                            if key.give_activate_status == 0:

                                # 获取该账号的会员, 并修改会员信息
                                vip_member = VipMembers.query.filter_by(godin_id=godin_account.godin_id).limit(1).first()

                                vip_ad_time = 0
                                vip_gold_ad_time = 0
                                if key_record.vip_gold_ad_time:
                                    vip_gold_ad_time = key_record.vip_gold_ad_time
                                if key_record.vip_ad_time:
                                    vip_ad_time = key_record.vip_ad_time
                                gold_give_time = user_key_record.activate_time + datetime.timedelta(days=vip_gold_ad_time)
                                plat_give_time = user_key_record.activate_time + datetime.timedelta(days=vip_ad_time)
                                #
                                if vip_member is None:
                                    vip_member = VipMembers()
                                    vip_member.godin_id = godin_account.godin_id
                                    vip_member.channel = json_req['market']
                                    vip_member.category = 1
                                    if vip_gold_ad_time > 0:
                                        vip_member.gold_valid_time = gold_give_time
                                        vip_member.grade = 1
                                    if vip_ad_time > 0:
                                        vip_member.valid_time = plat_give_time
                                        vip_member.grade = 2

                                freegod = None
                                freevip = None
                                # 赠送黄金会员
                                if vip_gold_ad_time > 0:
                                    if vip_member.gold_valid_time is not None:
                                        if vip_member.gold_valid_time < gold_give_time:
                                            if vip_member.grade == 0:
                                                vip_member.grade = 1
                                            vip_member.gold_valid_time = gold_give_time
                                    else:
                                        if vip_member.grade == 0:
                                            vip_member.grade = 1
                                        vip_member.gold_valid_time = gold_give_time

                                    # 赠送黄金会员
                                    freegod = MemberWareOrder()
                                    freegod.ware_id = 'freegod'
                                    freegod.order_number = gen_free_vip_order_num()
                                    freegod.buyer_godin_id = user_info.godin_id
                                    freegod.pay_type = 2
                                    freegod.ware_price = 0
                                    freegod.discount_price = 0
                                    freegod.discount = 0
                                    freegod.status = 1
                                    freegod.ac_source = 0
                                    freegod.pay_time = datetime.datetime.now()
                                    freegod.start_time = user_key_record.activate_time
                                    freegod.end_time = gold_give_time
                                    freegod.category = 1
                                    freegod.key_record_id = key.key_record_id
                                    freegod.buy_grade = 0
                                    # 当存在订单时，需要判断订单的时间和赠送的时间，取最大的值
                                    mwo = db.session.query(MemberWareOrder).filter(MemberWareOrder.buyer_godin_id == user_info.godin_id,\
                                                                                   MemberWareOrder.buy_grade == 0,\
                                                                                   MemberWareOrder.status == 1,\
                                                                                   MemberWareOrder.ware_id != 'freevip',\
                                                                                   MemberWareOrder.ware_id != 'freegod').\
                                        order_by(MemberWareOrder.end_time.desc()).limit(1).first()
                                    if mwo:
                                        if mwo.end_time > freegod.end_time:
                                            freegod.end_time = mwo.end_time
                                            vip_member.gold_valid_time = mwo.end_time

                                # 赠送铂金会员
                                if vip_ad_time > 0:
                                    if vip_member.valid_time is not None:
                                        if vip_member.valid_time < plat_give_time:
                                            vip_member.grade = 2
                                            vip_member.valid_time = plat_give_time
                                    else:
                                        vip_member.grade = 2
                                        vip_member.valid_time = plat_give_time

                                    # 赠送铂金会员
                                    freevip = MemberWareOrder()
                                    freevip.ware_id = 'freevip'
                                    freevip.order_number = gen_free_vip_order_num()
                                    freevip.buyer_godin_id = user_info.godin_id
                                    freevip.pay_type = 2
                                    freevip.ware_price = 0
                                    freevip.discount_price = 0
                                    freevip.discount = 0
                                    freevip.status = 1
                                    freevip.ac_source = 0
                                    freevip.pay_time = datetime.datetime.now()
                                    freevip.start_time = user_key_record.activate_time
                                    freevip.end_time = plat_give_time
                                    freevip.category = 1
                                    freevip.key_record_id = key.key_record_id
                                    freevip.buy_grade = 1
                                    # 当存在订单时，需要判断订单的时间和赠送的时间，取最大的值
                                    mwo = db.session.query(MemberWareOrder).filter(MemberWareOrder.buyer_godin_id == user_info.godin_id,\
                                                                                   MemberWareOrder.buy_grade == 1,\
                                                                                   MemberWareOrder.status == 1,\
                                                                                   MemberWareOrder.ware_id != 'freevip',
                                                                                   MemberWareOrder.ware_id != 'freegod').\
                                        order_by(MemberWareOrder.end_time.desc()).limit(1).first()
                                    if mwo is not None:
                                        if mwo.end_time > freevip.end_time:
                                            freevip.end_time = mwo.end_time
                                            vip_member.valid_time = mwo.end_time

                                db.session.add(vip_member)
                                key.give_activate_status = 1
                                db.session.add(key)
                                db.session.commit()
                                if freegod:
                                    db.session.add(freegod)
                                if freevip:
                                    db.session.add(freevip)

            user_count = UserInfo.query.filter_by(imei=user_info.imei).count()
            user_info.device_info = new_device_info
            # update imei
            if user_info.imei != json_req['imei']:
                old_dev = DeviceInfo.query.filter_by(imei=user_info.imei).limit(1).first()
                if old_dev is not None and user_count < 2:
                    old_dev.status = False
                user_info.imei = json_req['imei']
            # add or update bind info
            bind_record = BindRecord().query.filter_by(godin_id=user_info.godin_id, imei=user_info.imei).limit(
                1).first()
            if bind_record is None:
                bind_record = BindRecord()
                bind_record.godin_id = user_info.godin_id
                bind_record.imei = user_info.imei
                db.session.add(bind_record)
            else:
                bind_record.ping()

            try:
                db.session.add(user_info)
                db.session.commit()
                return get_response({'head': ErrorCode.SUCCESS, 'body': user_info.to_json()})
            except Exception as e:
                db.session.rollback()
                print_error(action='Response', function=self.__class__.__name__, branch='INTERNAL_ERROR',
                            api_version=g_api_version, imei=json_req['imei'], data=e)
                return get_response({'head': ErrorCode.INTERNAL_ERROR})
        else:
            return get_response({'head': ErrorCode.SMS_INVALID})


# 更新设备信息
class UploadMobileInfoApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('os_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('device_factory', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('device_model', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('market', type=str, required=True, help='param missing', location='json')
        super(UploadMobileInfoApi, self).__init__()

    def post(self):
        # print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
                              function=self.__class__.__name__)
        if msg != 'valid':
            return get_response(msg)

        # from flask import request
        # ip = request.headers.get('X-Forwarded-For')
        # print('mobile: ', ip, json_req['imei'])
        device_info = DeviceInfo.query.filter_by(imei=json_req['imei']).limit(1).first()
        # new device
        if device_info is None:
            device_info = DeviceInfo()
            device_info.market = json_req['market']
        else:
            device_info.ping()
        device_info.from_json(json_req)
        try:
            db.session.add(device_info)
            db.session.commit()
            # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS',
            #            api_version=g_api_version, imei=json_req['imei'])
            return get_response({'head': ErrorCode.SUCCESS})
        except Exception as e:
            # print_error(action='Response', function=self.__class__.__name__, branch='INTERNAL_ERROR',
            #             api_version=g_api_version, imei=json_req['imei'], data=e)
            db.session.rollback()
            return get_response({'head': ErrorCode.INTERNAL_ERROR})


# 用户反馈信息
class FeedBackApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('godin_id', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('os_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('device_factory', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('device_model', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('user_contact', type=str, location='json')
        self.req_parse.add_argument('content', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('attach', type=str, required=True, help='param missing', location='json')
        super(FeedBackApi, self).__init__()

    def post(self):

        json_req = self.req_parse.parse_args()

        # 校验imei, app_version 校验通过返回‘valid’
        msg = validate_client_no_imei(imei=json_req['imei'], app_version=json_req['app_version'],
                                      function=self.__class__.__name__)
        if msg != 'valid':
            return get_response(msg)
        fb = FeedBack()
        fb.from_json(json_req)
        g_account = GodinAccount.query.filter_by(godin_id=json_req['godin_id']).first()
        fb.phone_num = g_account.phone_num

        attach = eval(json_req['attach'])
        if attach["photo"]:
            unix_time = int(time.time())
            new_name = str(unix_time) + '.' + attach['suffix']  # 修改上传的文件名

            photo_data = base64.decodebytes(bytes(attach['photo'].replace(' ', '+'), 'utf-8'))
            if photo_data is None:
                return {'head': ErrorCode.PHOTO_FORMAT_INVALID}
            basedir = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
            screen_dir = os.path.join(basedir, current_app.config['PHOTO_TAG'], 'appeal_image')
            if not os.path.exists(screen_dir):
                os.makedirs(screen_dir)
            photo = open(
                os.path.join(basedir, current_app.config['PHOTO_TAG'], 'appeal_image', new_name), 'wb')
            photo.write(photo_data)
            photo.close()

            fb.picture = os.path.join(current_app.config['PHOTO_TAG'], 'appeal_image', new_name)
            db.session.add(fb)

        device_info = DeviceInfo.query.filter_by(imei=json_req['imei']).limit(1).first()
        try:
            if device_info is not None:
                device_info.ping()
                db.session.add(device_info)
            db.session.add(fb)
            db.session.commit()
            return get_response({'head': ErrorCode.SUCCESS})
        except Exception as e:
            print_error(action='Response', function=self.__class__.__name__, branch='INTERNAL_ERROR',
                        api_version=g_api_version, imei=json_req['imei'], data=e)
            db.session.rollback()
            return get_response({'head': ErrorCode.INTERNAL_ERROR})


# 设置用户个人信息
class SetUserInfoApi(Resource):
    decorators = [http_auth.login_required]

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('godin_id', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('nick_name', type=str, location='json')
        self.req_parse.add_argument('photo', type=str, required=False, location='json')
        super(SetUserInfoApi, self).__init__()

    def post(self):
        # print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        # msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
        #                       function=self.__class__.__name__)
        # if msg != 'valid':
        #     return get_response(msg)

        user_info = UserInfo.query.filter_by(godin_id=json_req['godin_id']).limit(1).first()
        if user_info is None:
            print_warn(action='Response', function=self.__class__.__name__, branch='USER_NOT_EXIST',
                       api_version=g_api_version, imei=json_req['imei'])
            return get_response({'head': ErrorCode.USER_NOT_EXIST})
        if json_req['nick_name'] is not None:
            user_info.nick_name = json_req['nick_name']
        if json_req['photo'] is not None:
            try:
                user_photo_data = base64.decodebytes(bytes(json_req['photo'].replace(' ', '+'), 'utf-8'))
                if user_photo_data is None:
                    return get_response({'head': ErrorCode.PHOTO_FORMAT_INVALID})
                md = hashlib.md5()
                md.update(bytes(json_req['photo'], 'utf-8'))
                user_info.photo_md5 = md.hexdigest()
                user_info.photo_url = os.path.join(current_app.config['PHOTO_TAG'], json_req['godin_id'] + '.jpg')
                user_photo = open(os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'],
                                               json_req['godin_id'] + '.jpg'), 'wb')
                user_photo.write(user_photo_data)
                user_photo.close()
            except binascii.Error:
                print_error(action='Response', function=self.__class__.__name__, branch='PHOTO_FORMAT_INVALID',
                            api_version=g_api_version, imei=json_req['imei'])
                return get_response({'head': ErrorCode.PHOTO_FORMAT_INVALID})
        device_info = DeviceInfo.query.filter_by(imei=json_req['imei']).with_for_update().limit(1).first()
        try:
            if device_info is not None:
                device_info.ping()
                db.session.add(device_info)
            db.session.add(user_info)
            db.session.commit()
            # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS', api_version=g_api_version,
            #            imei=json_req['imei'])
            return get_response({'head': ErrorCode.SUCCESS})
        except Exception as e:
            print_error(action='Response', function=self.__class__.__name__, branch='INTERNAL_ERROR',
                        api_version=g_api_version, imei=json_req['imei'], data=e)
            db.session.rollback()
            return get_response({'head': ErrorCode.INTERNAL_ERROR})


class UploadExceptionLogApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('md5_value', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('os_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('device_model', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('package_name', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('content', type=str, required=True, help='param missing', location='json')
        super(UploadExceptionLogApi, self).__init__()

    def post(self):
        #print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        #print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #          api_version=g_api_version, data=str(json_req))
        # msg = validate_client_no_imei(imei=json_req['imei'], app_version=json_req['app_version'],
        #                               function=self.__class__.__name__)
        # if msg != 'valid':
        #     return get_response(msg)
        msg = validate_app_exception(imei=json_req['imei'], app_version=json_req['app_version'],
                                     function=self.__class__.__name__)
        if msg != 'valid':
            return get_response(msg)

        exception_log = ExceptionLog.query.with_lockmode("update"). \
            filter_by(md5_value=json_req['md5_value'], app_version=json_req['app_version']).limit(1).first()
        if exception_log is None:
            exception_log = ExceptionLog()
            exception_log.error_count = 1
            exception_log.imei = json_req['imei']
            exception_log.md5_value = json_req['md5_value']
            exception_log.app_version = json_req['app_version']
            exception_log.log_link = os.path.join(current_app.config['EXCEPTION_TAG'], json_req['md5_value'] + '.log')
            err_log = open(os.path.join(os.getcwd(), current_app.config['EXCEPTION_TAG'],
                                        json_req['md5_value'] + '.log'), 'wb')
            err_log.write(bytes(json_req['content'], 'utf-8'))
            err_log.close()

        else:
            exception_log.error_count += 1
        exception_log.imei = json_req['imei']
        exception_log.os_version = json_req['os_version']
        exception_log.device_model = json_req['device_model']
        exception_log.package_name = json_req['package_name']

        try:
            db.session.add(exception_log)
            db.session.commit()
            #print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS',
            #           api_version=g_api_version, imei=json_req['imei'])
            return get_response({'head': ErrorCode.SUCCESS})
        except Exception as e:
            print_info(action='Response', function=self.__class__.__name__, branch='INTERNAL_ERROR',
                       api_version=g_api_version, imei=json_req['imei'], data=e)
            db.session.rollback()
            return get_response({'head': ErrorCode.INTERNAL_ERROR})

# 获取token
class GetAuthTokenApi(Resource):
    decorators = [http_auth.login_required]

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('phone_num', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        super(GetAuthTokenApi, self).__init__()

    def post(self):
        # print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        phone_num = json_req['phone_num']
        if not check_phone_num(phone_num):
            # print_error(action='Response', function=self.__class__.__name__, branch='PHONE_NUM_INVALID',
            #             api_version=g_api_version, imei=json_req['imei'])
            return get_response({'head': ErrorCode.PHONE_NUM_INVALID})
        msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
                              function=self.__class__.__name__)
        if msg != 'valid':
            return get_response(msg)
        # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS',
        #            api_version=g_api_version, imei=json_req['imei'])
        return get_response({'head': ErrorCode.SUCCESS, 'body': {
            'current_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'token': g.current_user.generate_auth_token(
                expiration=current_app.config['TOKEN_EXPIRED_TIME']).decode('utf-8'),
            'expiration': str(current_app.config['TOKEN_EXPIRED_TIME'])}})


class GetActivityApi(Resource):
    # decorators = [http_auth.login_required]

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing')
        self.req_parse.add_argument('godin_id', type=str, required=True, help='param missing')
        super(GetActivityApi, self).__init__()

    def get(self):
        # print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        msg = validate_client_no_imei(imei=json_req['imei'], app_version=json_req['app_version'],
                                      function=self.__class__.__name__)
        if msg != 'valid':
            return get_response(msg)

        user = UserInfo.query.filter_by(godin_id=json_req['godin_id']).limit(1).first()
        if user is None:
            # print_warn(action='Response', function=self.__class__.__name__, branch='USER_NOT_EXIST',
            #            api_version=g_api_version, imei=json_req['imei'])
            return get_response({'head': ErrorCode.USER_NOT_EXIST})

        res = []
        base_ser = current_app.config['FILE_SERVER']
        current_time = datetime.datetime.now().date()
        activity_info = Activity.query.filter(Activity.status == 1, Activity.start_time < current_time,
                                              Activity.end_time > current_time).all()
        for item in activity_info:
            icon = ''
            share_icon = ''
            if len(item.icon) > 4:
                icon = base_ser + item.icon
            if len(item.share_icon) > 4:
                share_icon = base_ser + item.share_icon

            res.append({'activity_id': item.id, 'name': item.name, 'number': item.number, 'icon': icon,
                        'link': item.link, 'content': item.content, 'share_title': item.share_title,
                        'share_description': item.share_description, 'share_icon': share_icon,
                        'share_link': item.share_link})

        # print_info(action='Response', function=self.__class__.__name__, branch="success", api_version=g_api_version,
        #            imei=json_req['imei'])
        if not res:
            return get_response({"head": ErrorCode.SUCCESS})
        else:
            return get_response({"head": ErrorCode.SUCCESS, "body": res})


class ActivityFuncApi(Resource):
    # decorators = [http_auth.login_required]

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('godin_id', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('activity_id', type=int, required=True, help='param missing', location='json')
        self.req_parse.add_argument('number', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('event', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('attach', type=str, required=True, help='param missing', location='json')
        super(ActivityFuncApi, self).__init__()

    def post(self):
        # print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        imei, app_version, godin_id, activity_id, number, event, attach_value = [
            json_req[k] for k in ['imei', 'app_version', 'godin_id', 'activity_id', 'number', 'event', 'attach']]
        msg = validate_client(imei=imei, app_version=app_version, function=self.__class__.__name__)
        if msg != 'valid':
            return get_response(msg)
        user = UserInfo.query.filter_by(godin_id=godin_id).limit(1).first()
        if user is None:
            # print_warn(action='Response', function=self.__class__.__name__, branch='USER_NOT_EXIST',
            #            api_version=g_api_version, imei=imei)
            return get_response({'head': ErrorCode.USER_NOT_EXIST})
        activity = Activity.query.filter_by(id=activity_id).limit(1).first()
        if activity is None:
            # print_warn(action='Response', function=self.__class__.__name__, branch='ACTIVITY_NOT_EXIST',
            #            api_version=g_api_version)
            return get_response({'head': ErrorCode.ACTIVITY_NOT_EXIST})

        flag_status = 0
        # 事件100004 签到领会员
        if event == '100004':
            if number == '000003':
                sign_data = SignData.query.filter_by(activity_id=activity_id, sign_godin_id=godin_id,
                                                     number=number).limit(1).first()
                if sign_data is None:
                    current_time = datetime.datetime.now()
                    sign_data = SignData()
                    sign_data.activity_id = activity_id
                    sign_data.number = number
                    sign_data.sign_godin_id = godin_id
                    sign_data.sign_count = 1
                    sign_data.phone = user.godin_account.phone_num
                    sign_data.last_sign_time = current_time.date()
                    sign_data.update_time = current_time
                    db.session.add(sign_data)
                else:
                    current_time = datetime.datetime.now()
                    last_sign_time = sign_data.last_sign_time

                    if last_sign_time + datetime.timedelta(days=1) == current_time.date() \
                            and sign_data.sign_count != activity.award_period:
                        sign_data.sign_count += 1
                        sign_data.last_sign_time = current_time.date()
                        sign_data.update_time = current_time
                        db.session.add(sign_data)
                        if sign_data.sign_count == activity.award_period:
                            sign_record = SignRecord()
                            sign_record.activity_id = activity_id
                            sign_record.sign_godin_id = godin_id
                            sign_record.sign_time = current_time.date()
                            sign_record.phone = user.godin_account.phone_num
                            sign_record.reward = activity.reward
                            sign_record.create_time = current_time
                            db.session.add(sign_record)
                            sign_data.total_count += 1
                            # sign_data.sign_count = 0
                            db.session.add(sign_data)

                            v_type = VipType.query.filter_by(days=activity.reward).limit(1).first()
                            if v_type is not None:
                                ware = MemberWare.query.filter_by(category=v_type.number).limit(1).first()
                                if ware is not None:
                                    ware_id = ware.id
                                    activate = ActivateMembers()
                                    activate.godin_id = godin_id
                                    activate.channel = 'moren'
                                    activate.ware_id = ware_id
                                    activate.vip_type = 1
                                    db.session.add(activate)
                                    flag_status = 1
                    else:
                        if last_sign_time != current_time.date():
                            sign_data.sign_count = 1
                            sign_data.last_sign_time = current_time.date()
                            sign_data.update_time = current_time
                            db.session.add(sign_data)
                try:
                    db.session.commit()
                    # print_info(action='Response', function=self.__class__.__name__, branch="success",
                    #            api_version=g_api_version, imei=imei)
                    return get_response({"head": ErrorCode.SUCCESS, 'status': flag_status})
                except Exception as e:
                    db.session.rollback()
                    print_error(action='Response', function=self.__class__.__name__,
                                branch='INTERNAL_ERROR', api_version=g_api_version, imei=imei, data=e)
                    return get_response({'head': ErrorCode.INTERNAL_ERROR})

        # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS', api_version=g_api_version,
        #            imei=imei)
        return get_response({'head': ErrorCode.SUCCESS, 'status': flag_status})


class GetBanneradsStatisticsApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('ad_info', type=list, required=True, help='param missing', location='json')

        super(GetBanneradsStatisticsApi, self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()

        if not check_imei(json_req['imei']):
            return get_response("valid")

        for info in json_req['ad_info']:
            if 'ad_id' not in info or 'type' not in info:
                return get_response({'head': ErrorCode.JSON_FORMAT_INVALID}), 400
            if info['type'] >= 2:
                continue

            value = str({"ad_id": info['ad_id'], "operation": info['type'], "imei": json_req['imei'],
                         "record_time": datetime.date.today()})
            redis.lpush("BannerAdsStatistics", value)

        return {'head': ErrorCode.SUCCESS, 'body': {'status': 0}}


class GetOpenScreenAdsStatisticsApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('ad_info', type=list, required=True, help='param missing', location='json')

        super(GetOpenScreenAdsStatisticsApi, self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()

        if not check_imei(json_req['imei']):
            return get_response("valid")

        for info in json_req['ad_info']:
            if 'ad_id' not in info or 'type' not in info:
                return {'head': ErrorCode.JSON_FORMAT_INVALID}, 400

            if info['type'] >= 3:
                continue

            key = str({"ad_id": info['ad_id'], "operation": info['type'], "imei": json_req['imei'],
                       "record_time": datetime.date.today()})
            redis.incr(key, 1)
            redis.sadd("GetOpenScreenAdsStatistics", key)

        return {'head': ErrorCode.SUCCESS, 'body': {'status': 0}}


class UploadStatisticsApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('statistics', type=str, required=True, help='param missing', location='json')
        super(UploadStatisticsApi, self).__init__()

    def post(self):
        # print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        # json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        # msg = validate_client_no_imei(imei=json_req['imei'], app_version=json_req['app_version'],
        #                               function=self.__class__.__name__)
        # if msg != 'valid':
        #     return get_response(msg)

        # server = current_app.config['SERVER']
        """
        try:
            ret,  lock_key = get_lock(server + '_lock', 50, 80)
            if ret == 'timeout':
                print_info(action='Response', function='UploadStatisticsApi', branch='RELOAD_LATER', api_version='v1.0',
                          imei=json_req['imei'])
                return get_response({'head': ErrorCode.RELOAD_LATER})
        except Exception as e:
            print('UploadStatistics', e)
            print_info(action='Response', function='UploadStatisticsApi', branch='RELOAD_LATER-1', api_version='v1.0',
                      imei=json_req['imei'])
            return get_response({'head': ErrorCode.RELOAD_LATER})
        """
        # try:
        #     now_date = datetime.datetime.now().strftime('%Y%m%d')
        #     statistics_dir = os.path.join(os.getcwd(), current_app.config['STATISTICS_TAG'], now_date)
        #     if not os.path.exists(statistics_dir):
        #         os.mkdir(statistics_dir)
        #     now_hour = datetime.datetime.now().strftime('%H')
        #     file_name = os.path.join(statistics_dir, server + '-' + now_date + now_hour + '.txt')
        #     if os.path.exists(file_name):
        #         fp = open(file_name, 'a', encoding='utf8')
        #     else:
        #         fp = open(file_name, 'w', encoding='utf8')
        #     fp.write(json_req['statistics'] + '\n')
        #     fp.close()
        #     # release(lock_key)
        # except Exception as e:
        #     # release(lock_key)
        #     print_error(action='Response', function=self.__class__.__name__, branch='RELOAD_LATER-2',
        #                 api_version=g_api_version, imei=json_req['imei'], data=e)

        return get_response({'head': ErrorCode.SUCCESS})


class GetUserVipStatusApi(Resource):

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('godin_id', type=str, required=True, help='param missing', location='json')
        super(GetUserVipStatusApi,self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()
        act_member = ActivateMembers.query.filter_by(godin_id=json_req['godin_id'], status=0).limit(1).first()
        activate = 0
        if act_member:
            activate = 1
        vip_member = VipMembers.query.filter_by(godin_id=json_req['godin_id']).limit(1).first()
        if vip_member is None:
            return get_response({'head': ErrorCode.USER_NOT_VIP, 'body': {'activate': activate, "grade": 0}})
        body = {}
        if vip_member.valid_time and vip_member.valid_time > datetime.datetime.now():
            # 如果铂金会员有效接着判断黄金会员是否有效
            if vip_member.gold_valid_time and vip_member.gold_valid_time > datetime.datetime.now():
                if vip_member.grade != 2:
                    vip_member.grade = 2
                    db.session.add(vip_member)
                    db.session.commit()
                body = {
                    'activate': activate,
                    "grade": 2,
                    'remain_days': (vip_member.valid_time - datetime.datetime.today()).days,
                    'valid_time': vip_member.valid_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'second_remain_day': (vip_member.gold_valid_time - datetime.datetime.today()).days,
                    'second_valid_time': vip_member.gold_valid_time.strftime('%Y-%m-%d %H:%M:%S'),
                }
            else:
                if vip_member.grade != 2:
                    vip_member.grade = 2
                    db.session.add(vip_member)
                    db.session.commit()
                body = {
                    'activate': activate,
                    "grade": 2,
                    'remain_days': (vip_member.valid_time - datetime.datetime.today()).days,
                    'valid_time': vip_member.valid_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'second_remain_day': -1,
                    'second_valid_time': "",
                }

        elif vip_member.gold_valid_time and vip_member.gold_valid_time > datetime.datetime.now():

            if vip_member.grade != 1:
                vip_member.grade = 1
                db.session.add(vip_member)
                db.session.commit()

            # 铂金会员无效黄金会员有效
            body = {
                'activate': activate,
                "grade": 1,
                'remain_days': (vip_member.gold_valid_time - datetime.datetime.today()).days,
                'valid_time': vip_member.gold_valid_time.strftime('%Y-%m-%d %H:%M:%S'),
                'second_remain_day': -1,
                'second_valid_time': "",
            }
        else:
            # 没有会员
            if vip_member.status == 1 or vip_member.grade != 0:
                vip_member.status = 0
                vip_member.grade = 0
                db.session.add(vip_member)
                db.session.commit()
            return get_response({'head': ErrorCode.USER_NOT_VIP, 'body': {'activate': activate, "grade": 0}})

        return get_response({'head': ErrorCode.SUCCESS, 'body': body})


class GetChannelVipWareApi(Resource):

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('channel', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('godin_id', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('status', type=str, required=True, help='param missing', location='json')
        super(GetChannelVipWareApi,self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()
        msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
                              function=self.__class__.__name__)
        if msg != 'valid':
            return get_response(msg)

        ware_list = []
        ware_cate = []
        type_dict = {}
        vip_type = VipType.query
        for vip in vip_type:
            type_dict[vip.number] = vip.days
        wares = MemberWare.query.filter(MemberWare.channel.in_([json_req['channel'], 'moren']),
                                        MemberWare.gold_or_platinum == int(json_req['status'])).filter_by(status=1)
        # 判断当前用户的等级
        grade = 0
        vip_member = VipMembers.query.filter_by(godin_id=json_req['godin_id']).limit(1).first()
        # if vip_member is not None and vip_member.valid_time and vip_member.valid_time > datetime.datetime.now():
        #     grade = int(vip_member.grade)

        # 验证vip类型
        if vip_member:
            gradechange = False  # 是否grade需要改变
            if vip_member.grade == 2:
                if vip_member.valid_time and vip_member.valid_time > datetime.datetime.now():
                    pass
                else:
                    vip_member.grade = 1
                    gradechange = True

            if vip_member.grade == 1:
                if vip_member.gold_valid_time and vip_member.gold_valid_time > datetime.datetime.now():
                    pass
                else:
                    vip_member.grade = 0
                    gradechange = True

            # 修改grade字段
            if gradechange:
                db.session.add(vip_member)
                db.session.commit()
            grade = int(vip_member.grade)

        if json_req['channel'] != 'moren':
            for ware in wares:
                # 根据用户等级确定商品折扣
                try:
                    if grade == 0:
                        discount = float(ware.common_discount)
                    elif grade == 1:
                        discount = float(ware.gold_discount)
                    else:
                        discount = float(ware.discount)
                except TypeError:
                    return get_response({'head': ErrorCode.SUCCESS, 'body': {'ware_list': ""}})

                if ware.channel == json_req['channel']:
                    if ware.picture != '':
                        picture = current_app.config['FILE_SERVER'] + ware.picture
                    else:
                        picture = ''

                    cell = {
                        'id': ware.id,
                        'name': ware.name,
                        'category': ware.category,
                        'days': type_dict[ware.category],
                        'price': ware.price,
                        'discount': discount,
                        'discount_price': float(ware.price * discount),
                        'priority': ware.priority,
                        'description': ware.description,
                        'channel': ware.channel,
                        'picture': picture
                    }
                    ware_list.append(cell)
                    ware_cate.append(ware.category)

        for ware in wares:
            # 根据用户等级确定商品折扣
            try:
                if grade == 0:
                    discount = float(ware.common_discount)
                elif grade == 1:
                    discount = float(ware.gold_discount)
                else:
                    discount = float(ware.discount)
            except TypeError:
                return get_response({'head': ErrorCode.SUCCESS, 'body': {'ware_list': ""}})

            if ware.channel == 'moren':
                if ware.category not in ware_cate:
                    if ware.picture != '':
                        picture = current_app.config['FILE_SERVER'] + ware.picture
                    else:
                        picture = ''
                    cell = {
                        'id': ware.id,
                        'name': ware.name,
                        'category': ware.category,
                        'days': type_dict[ware.category],
                        'price': ware.price,
                        'discount': discount,
                        'discount_price': float(ware.price * discount),
                        'priority': ware.priority,
                        'description': ware.description,
                        'channel': ware.channel,
                        'picture': picture
                    }
                    ware_list.append(cell)
        return get_response({'head': ErrorCode.SUCCESS, 'body': {'ware_list': ware_list}})


class GetUserVipOrderApi(Resource):
    decorators = [http_auth.login_required]

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('godin_id', type=str, required=True, help='param missing', location='json')
        super(GetUserVipOrderApi, self).__init__()

    def post(self):
        # print_info(action='Recevie', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        # msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
        #                       function=self.__class__.__name__)
        # if msg != 'valid':
        #     return get_response(msg)
        ware_order = []
        type_dict = {}
        vip_type = VipType.query
        for vip in vip_type:
            type_dict[vip.number] = vip.name
        for order in MemberWareOrder.query.filter(MemberWareOrder.buyer_godin_id==json_req['godin_id'],
                                                     MemberWareOrder.status==1,
                                                     MemberWareOrder.ware_id!='freegod',
                                                     MemberWareOrder.ware_id!='freevip'):
            category = 0
            type_name = '其它'
            ware_info = MemberWare.query.filter_by(id=order.ware_id).limit(1).first()
            if ware_info is not None:
                category = ware_info.category
                if category in type_dict:
                    type_name = type_dict[category]
            ware_order.append(order.to_json(ware_info.gold_or_platinum, type_name))
        # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS',
        #            api_version=g_api_version, imei=json_req['imei'])
        return get_response({'head': ErrorCode.SUCCESS, 'body': {'ware_order': ware_order}})


class BuyVipWareApi(Resource):
    decorators = [http_auth.login_required]

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('godin_id', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('ware_id', type=str, required=True, help='param missing', location='json')
        super(BuyVipWareApi, self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()

        ware_info = MemberWare.query.filter_by(id=json_req['ware_id']).limit(1).first()
        if ware_info is None:
            return get_response({'head': ErrorCode.WARE_NOT_EXIST})

        vip_member = VipMembers.query.filter_by(godin_id=json_req['godin_id']).limit(1).first()

        # 判断当前用户的状态
        grade = 0
        if vip_member is None:
            vip_member = VipMembers()
            vip_member.godin_id = json_req['godin_id']
            vip_member.category = 0
            vip_member.status = 0
            vip_member.grade = 0
            vip_member.cur_pay_cate = ware_info.category

            user = UserInfo.query.filter_by(godin_id=json_req['godin_id']).limit(1).first()

            if user is not None:
                vip_member.channel = user.device_info.market
            db.session.add(vip_member)
            db.session.commit()
        else:
            gradechange = False  # 是否grade需要改变

            if vip_member.grade is None:
                vip_member.grade = 2
                gradechange = True
            elif vip_member.grade == 3:
                vip_member.grade = 2
                gradechange = True

            if vip_member.grade == 2:
                if vip_member.valid_time and vip_member.valid_time > datetime.datetime.now():
                    pass
                else:
                    vip_member.grade = 1
                    gradechange = True

            if vip_member.grade == 1:
                if vip_member.gold_valid_time and vip_member.gold_valid_time > datetime.datetime.now():
                    pass
                else:
                    vip_member.grade = 0
                    gradechange = True

            # 修改grade字段
            if gradechange:
                db.session.add(vip_member)
                db.session.commit()
            grade = int(vip_member.grade)

        ware_order = MemberWareOrder.query.filter_by(buyer_godin_id=json_req['godin_id'], ac_source=0,
                                                     ware_id=json_req['ware_id'], status=0, category=0).limit(1).first()

        # 用户没有未支付的订单
        if ware_order is None:
            ware_order = MemberWareOrder()
            old_order = MemberWareOrder.query.filter_by(buyer_godin_id=json_req['godin_id'], status=1, buy_grade=ware_info.gold_or_platinum). \
                order_by(MemberWareOrder.pay_time.desc()).limit(1).first()
            if old_order is not None:
                # 最后一个付款订单结束的时间的下一秒
                if old_order.end_time < datetime.datetime.now():
                    ware_order.start_time = datetime.datetime.now()
                else:
                    ware_order.start_time = old_order.end_time + datetime.timedelta(seconds=1)
            else:
                ware_order.start_time = datetime.datetime.now()
            ware_order.order_number = gen_vip_order_num()
            ware_order.buyer_godin_id = json_req['godin_id']
            ware_order.ware_id = json_req['ware_id']
            ware_order.ware_price = ware_info.price
            # ware_order.discount = ware_info.discount
            ware_order.ac_source = 0
            # ware_order.discount_price = ware_info.price * ware_info.discount
            # discount_price = ware_info.price * ware_info.discount
            # 客户下单时会将小数位截掉，在截掉小数位的整数上进行加1 确保客户付的钱一定是富裕的
            # if isinstance(discount_price, float):
            #     discount_price = int(str(discount_price).split('.')[0]) + 1
            # ware_order.discount_price = discount_price

            # 获取key_record_id
            user_key_record = UserKeyRecord.query.filter_by(imei=json_req['imei'], status=1). \
                order_by(UserKeyRecord.activate_time.desc()).limit(1).first()
            if user_key_record is not None:
                key = Key.query.filter_by(id=user_key_record.key_id).limit(1).first()
                if key is not None:
                    ware_order.key_record_id = key.key_record_id
            # ware_order.end_time = add_month(ware_order.start_time, added_month)
            vip_type = VipType.query.filter_by(number=ware_info.category).limit(1).first()
            if vip_type is not None:
                ware_order.end_time = ware_order.start_time + datetime.timedelta(days=vip_type.days)
            ware_order.category = 0
            # status 0 表示订单未支付
            ware_order.status = 0
            # 确认用户的购买类型
            if grade == 0:
                ware_order.discount = ware_info.common_discount
                discount_price = ware_info.price * ware_info.common_discount
                if ware_info.gold_or_platinum == 0:
                    ware_order.buy_type = "普通升黄金"
                    ware_order.buy_grade = 0
                else:
                    ware_order.buy_type = "普通升铂金"
                    ware_order.buy_grade = 1
            elif grade == 1:
                ware_order.discount = ware_info.gold_discount
                discount_price = ware_info.price * ware_info.gold_discount
                if ware_info.gold_or_platinum == 0:
                    ware_order.buy_type = "黄金续费黄金"
                    ware_order.buy_grade = 0
                else:
                    ware_order.buy_type = "黄金升铂金"
                    ware_order.buy_grade = 1
            else:
                ware_order.discount = ware_info.discount
                discount_price = ware_info.price * ware_info.discount
                ware_order.buy_type = "铂金续费铂金"
                ware_order.buy_grade = 1
            if isinstance(discount_price, float):
                discount_price = int(str(discount_price).split('.')[0]) + 1
            ware_order.discount_price = discount_price

            try:
                db.session.add(ware_order)
                db.session.commit()
            except Exception as e:
                print_error(action='Response', function=self.__class__.__name__, branch='INTERNAL_ERROR',
                            api_version=g_api_version, imei=json_req['imei'], data=e)
                db.session.rollback()
                return get_response({'head': ErrorCode.INTERNAL_ERROR})
        elif ware_order.ware_price != ware_info.price or ware_order.discount != ware_info.discount or \
                (ware_order.create_time + datetime.timedelta(minutes=15) < datetime.datetime.now()):
            db.session.delete(ware_order)
            db.session.commit()
            return get_response({'head': ErrorCode.ORDER_EXPIRED})
        try:
            today = datetime.datetime.today()
            expire_time = today + datetime.timedelta(minutes=30)
            res = WexinPay().unified_order(out_trade_no=ware_order.order_number,
                                           total_fee=ware_order.discount_price,
                                           time_start=today.strftime('%Y%m%d%H%M%S'),
                                           time_expire=expire_time.strftime('%Y%m%d%H%M%S'),
                                           body=ware_info.name, trade_type='APP')

            res['order_number'] = ware_order.order_number
            res['price'] = ware_order.discount_price
            return get_response({'head': ErrorCode.SUCCESS, 'body': res})
        except Exception as e:
            db.session.delete(ware_order)
            db.session.commit()
            print_error(action='Response', function=self.__class__.__name__, branch='ORDER_INVALID',
                        api_version=g_api_version, imei=json_req['imei'], data=e)
            return get_response({'head': ErrorCode.ORDER_INVALID})


class NewBuyVipWareApi(Resource):
    decorators = [http_auth.login_required]

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('godin_id', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('ware_id', type=str, required=True, help='param missing', location='json')
        super(NewBuyVipWareApi, self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()
        msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
                              function=self.__class__.__name__)
        if msg != 'valid':
            return get_response(msg)
        ware_info = MemberWare.query.filter_by(id=json_req['ware_id']).limit(1).first()
        if ware_info is None:
            return get_response({'head': ErrorCode.WARE_NOT_EXIST})

        vip_member = VipMembers.query.filter_by(godin_id=json_req['godin_id']).limit(1).first()
        # 判断当前用户的状态
        grade = 0
        if vip_member is None:
            vip_member = VipMembers()
            vip_member.godin_id = json_req['godin_id']
            vip_member.category = 0
            vip_member.status = 0
            vip_member.grade = 0
            vip_member.cur_pay_cate = ware_info.category

            user = UserInfo.query.filter_by(godin_id=json_req['godin_id']).limit(1).first()

            if user is not None:
                vip_member.channel = user.device_info.market
            db.session.add(vip_member)
            db.session.commit()

        else:
            gradechange = False  # 是否grade需要改变

            if vip_member.grade is None:
                vip_member.grade = 2
                gradechange = True
            elif vip_member.grade == 3:
                vip_member.grade = 2
                gradechange = True

            if vip_member.grade == 2:
                if vip_member.valid_time and vip_member.valid_time > datetime.datetime.now():
                    pass
                else:
                    vip_member.grade = 1
                    gradechange = True

            if vip_member.grade == 1:
                if vip_member.gold_valid_time and vip_member.gold_valid_time > datetime.datetime.now():
                    pass
                else:
                    vip_member.grade = 0
                    gradechange = True

            # 修改grade字段
            if gradechange:
                db.session.add(vip_member)
                db.session.commit()
            grade = int(vip_member.grade)

        ware_order = MemberWareOrder.query.filter_by(buyer_godin_id=json_req['godin_id'], ac_source=1,
                                                     ware_id=json_req['ware_id'], status=0, category=0).limit(1).first()

        # 用户没有未支付的订单
        if ware_order is None:

            ware_order = MemberWareOrder()
            old_order = MemberWareOrder.query.filter_by(buyer_godin_id=json_req['godin_id'], status=1). \
                order_by(MemberWareOrder.pay_time.desc()).limit(1).first()
            if old_order is not None:
                # 最后一个付款订单结束的时间的下一秒
                if old_order.end_time < datetime.datetime.now():
                    ware_order.start_time = datetime.datetime.now()
                else:
                    ware_order.start_time = old_order.end_time + datetime.timedelta(seconds=1)
            else:
                ware_order.start_time = datetime.datetime.now()
            ware_order.order_number = gen_avatar_vip_order_num()
            ware_order.buyer_godin_id = json_req['godin_id']
            ware_order.ware_id = json_req['ware_id']
            ware_order.ware_price = ware_info.price
            ware_order.ac_source = 1

            # 获取key_record_id
            user_key_record = UserKeyRecord.query.filter_by(imei=json_req['imei'], status=1). \
                order_by(UserKeyRecord.activate_time.desc()).limit(1).first()
            if user_key_record is not None:
                key = Key.query.filter_by(id=user_key_record.key_id).limit(1).first()
                if key is not None:
                    ware_order.key_record_id = key.key_record_id
            # ware_order.end_time = add_month(ware_order.start_time, added_month)
            vip_type = VipType.query.filter_by(number=ware_info.category).limit(1).first()
            if vip_type is not None:
                ware_order.end_time = ware_order.start_time + datetime.timedelta(days=vip_type.days)
            ware_order.category = 0
            # status 0 表示订单未支付
            ware_order.status = 0

            # 确认用户的购买类型
            if grade == 0:
                ware_order.discount = ware_info.common_discount
                discount_price = ware_info.price * ware_info.common_discount
                if ware_info.gold_or_platinum == 0:
                    ware_order.buy_type = "普通升黄金"
                    ware_order.buy_grade = 0
                else:
                    ware_order.buy_type = "普通升铂金"
                    ware_order.buy_grade = 1
            elif grade == 1:
                ware_order.discount = ware_info.gold_discount
                discount_price = ware_info.price * ware_info.gold_discount
                if ware_info.gold_or_platinum == 0:
                    ware_order.buy_type = "黄金续费黄金"
                    ware_order.buy_grade = 0
                else:
                    ware_order.buy_type = "黄金升铂金"
                    ware_order.buy_grade = 1
            else:
                ware_order.discount = ware_info.discount
                discount_price = ware_info.price * ware_info.discount
                ware_order.buy_type = "铂金续费铂金"
                ware_order.buy_grade = 1
            if isinstance(discount_price, float):
                discount_price = int(str(discount_price).split('.')[0]) + 1
            ware_order.discount_price = discount_price

            try:
                db.session.add(ware_order)
                db.session.commit()
            except Exception as e:
                print_error(action='Response', function=self.__class__.__name__, branch='INTERNAL_ERROR',
                            api_version=g_api_version, imei=json_req['imei'], data=e)
                db.session.rollback()
                return get_response({'head': ErrorCode.INTERNAL_ERROR})
        elif ware_order.ware_price != ware_info.price or ware_order.discount != ware_info.discount or \
                (ware_order.create_time + datetime.timedelta(minutes=15) < datetime.datetime.now()):
            db.session.delete(ware_order)
            db.session.commit()
            return get_response({'head': ErrorCode.ORDER_EXPIRED})
        try:
            today = datetime.datetime.today()
            expire_time = today + datetime.timedelta(minutes=30)
            res = AvatarWexinPay().unified_order(out_trade_no=ware_order.order_number,
                                                 total_fee=ware_order.discount_price,
                                                 time_start=today.strftime('%Y%m%d%H%M%S'),
                                                 time_expire=expire_time.strftime('%Y%m%d%H%M%S'),
                                                 body=ware_info.name, trade_type='APP')
            res['order_number'] = ware_order.order_number
            res['price'] = ware_order.discount_price
            return get_response({'head': ErrorCode.SUCCESS, 'body': res})
        except Exception as e:
            db.session.delete(ware_order)
            db.session.commit()
            print_error(action='Response', function=self.__class__.__name__, branch='ORDER_INVALID',
                        api_version=g_api_version, imei=json_req['imei'], data=e)
            return get_response({'head': ErrorCode.ORDER_INVALID})


class GetVipOrdersStatusApi(Resource):
    decorators = [http_auth.login_required]

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('godin_id', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('order_nums', type=list, required=True, help='param missing', location='json')
        super(GetVipOrdersStatusApi, self).__init__()

    def post(self):
        # print_info(action='Recevie', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        # msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
        #                       function=self.__class__.__name__)
        # if msg != 'valid':
        #     return get_response(msg)
        res = []
        for order_num in json_req['order_nums']:
            order = MemberWareOrder.query.filter_by(buyer_godin_id=json_req['godin_id'], order_number=order_num).limit(1).first()
            if order is not None:
                res.append({'order_num': order_num, 'status': order.status})
        # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS', api_version=g_api_version,
        #            imei=json_req['imei'])
        return get_response({'head': ErrorCode.SUCCESS, 'body': res})


class ActivateVipMemberApi(Resource):
    decorators = [http_auth.login_required]

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('godin_id', type=str, required=True, help='param missing', location='json')
        super(ActivateVipMemberApi, self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()
        msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
                              function=self.__class__.__name__)
        if msg != 'valid':
            return get_response(msg)

        category = 0
        channel = ''
        vip_member = VipMembers.query.filter_by(godin_id=json_req['godin_id']).limit(1).first()
        if vip_member is None:
            member = VipMembers()
            member.godin_id = json_req['godin_id']
            member.category = 2
            member.cur_pay_cate = category
            member.status = 0
            member.channel = ''
            db.session.add(member)
            db.session.commit()

        act_member = ActivateMembers.query.filter_by(godin_id=json_req['godin_id'], status=0)
        i = 0
        for act in act_member:
            ware = MemberWare.query.filter_by(id=act.ware_id).limit(1).first()
            if ware is None:
                return get_response({'head': ErrorCode.WARE_NOT_EXIST})
            order = MemberWareOrder()
            old_order = MemberWareOrder.query.filter_by(buyer_godin_id=json_req['godin_id'], status=1,
                                                        buy_grade=ware.gold_or_platinum).order_by(
                                                        MemberWareOrder.pay_time.desc()).limit(1).first()
            if old_order is not None:
                if old_order.end_time < datetime.datetime.now():
                    order.start_time = datetime.datetime.now()
                else:
                    order.start_time = old_order.end_time + datetime.timedelta(seconds=1)
            else:
                order.start_time = datetime.datetime.now()

            vip_type = VipType.query.filter_by(number=ware.category).limit(1).first()
            if vip_type is not None:
                order.end_time = order.start_time + datetime.timedelta(days=vip_type.days)
            order.status = 1
            order.pay_time = datetime.datetime.now() + datetime.timedelta(minutes=i)
            order.order_number = gen_vip_order_num()
            order.buyer_godin_id = json_req['godin_id']
            order.ware_id = act.ware_id
            order.ware_price = ware.price
            order.discount = ware.common_discount
            order.discount_price = ware.price * ware.common_discount
            order.pay_type = 2
            order.status = 1
            order.category = 2
            if act.vip_type == 1:
                order.category = 1

            act.status = 1
            act.modify_time = datetime.datetime.now()
            db.session.add(act)
            category = ware.category
            channel = act.channel
            i += 1

            vip_member = VipMembers.query.filter_by(godin_id=json_req['godin_id']).limit(1).first()
            if ware.gold_or_platinum == 0:
                vip_member.gold_valid_time = order.end_time
                order.buy_grade = 0
            else:
                vip_member.valid_time = order.end_time
            vip_member.cur_pay_cate = category
            if not vip_member.first_pay_time:
                vip_member.category = 2
                if act.vip_type == 1:
                    vip_member.category = 1
            if vip_member.grade != 2:
                vip_member.grade = ware.gold_or_platinum + 1
            vip_member.status = 1
            vip_member.channel = channel
            db.session.add(order)
            db.session.add(vip_member)
            db.session.commit()
        return get_response({'head': ErrorCode.SUCCESS})


class VipServiceProtocolApi(Resource):
    decorators = [http_auth.login_required]

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        super(VipServiceProtocolApi, self).__init__()

    def post(self):
        # print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
                              function=self.__class__.__name__)
        if msg != 'valid':
            return get_response(msg)
        protocol = ServiceProtocol.query.filter_by(category=0).limit(1).first()
        if protocol is None:
            # print_warn(action='Response', function=self.__class__.__name__, branch='USER_NOT_VIP',
            #            api_version=g_api_version, imei=json_req['imei'])
            return get_response({'head': ErrorCode.VIP_NOT_PROTOCOL})
        else:
            # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS',
            #            api_version=g_api_version, imei=json_req['imei'])
            return get_response({'head': ErrorCode.SUCCESS, 'body': {'content': protocol.content}})


class GetCommunicationGroupApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        super(GetCommunicationGroupApi, self).__init__()

    def post(self):
        # print_info(action='Recevie', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        # msg = validate_client_no_imei(imei=json_req['imei'], app_version=json_req['app_version'],
        #                               function=self.__class__.__name__)
        # if msg != 'valid':
        #     return get_response(msg)
        group_info = CommunicationGroup.query.all()
        if group_info is not None and len(group_info) > 0:
            data = []
            for info in group_info:
                data.append({'type': info.type, 'group_number': info.group_number, 'group_key': info.group_key})
                # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS',
                #            api_version=g_api_version, imei=json_req['imei'])
            return get_response({'head': ErrorCode.SUCCESS, 'body': {'group_info': data}})

        return get_response({'head': ErrorCode.SUCCESS})


class OpenScreenAdsDataApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('ad_id', type=int, required=True, help='param missing', location='json')
        self.req_parse.add_argument('type', type=int, required=True, help='param missing', location='json')
        super(OpenScreenAdsDataApi, self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()

        if not check_imei(json_req['imei']):
            return get_response("valid")

        value = str({"ad_id": json_req['ad_id'], "operation": json_req['type'], "imei": json_req['imei'],
                     "record_time": datetime.date.today()})
        redis.lpush("OpenScreenAdsData", value)

        return {'head': ErrorCode.SUCCESS, 'body': {'status': 0}}



class GetInteractiveAdsApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('channel', type=str, required=True, help='param missing', location='json')
        super(GetInteractiveAdsApi, self).__init__()

    def post(self):
        # print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        # msg = validate_client_no_imei(imei=json_req['imei'], app_version=json_req['app_version'],
        #                               function=self.__class__.__name__)
        # if msg != 'valid':
        #     return get_response(msg)

        if not check_imei(json_req['imei']):
            return get_response("valid")

        key = "GetInteractiveAdsApi_" + json_req['app_version'] + "_" + json_req['channel'] + datetime.datetime.now().strftime('%Y-%m-%d-%H')
        isRelease = False
        if json_req['imei'] not in get_white_imei_list():
            isRelease = True
            c_data = cache.get(key)
            if c_data:
                return c_data

        version = 0
        ver_query = AppVersion.query.filter_by(app_type=4)
        if isRelease:
            ver_query = ver_query.filter_by(is_released=True)
        version_info = ver_query.order_by(AppVersion.id.desc()).limit(1).first()
        if version_info is not None:
            if version_info.version_name == json_req['app_version']:
                version = 1

        refresh_count = 0
        current_time = datetime.datetime.now()
        r_time = str(current_time.year) + '-' + str(current_time.month) + '-' + str(current_time.day) + " "
        refresh_time = r_time + '00:00~' + r_time + '00:00'

        res = []

        ads_info = InteractiveAds.query.join(InteractiveConfig, InteractiveConfig.ad_id == InteractiveAds.id) \
            .filter(InteractiveAds.status == 1, InteractiveConfig.status == 1, InteractiveConfig.channel ==
                    json_req['channel'], InteractiveConfig.version == version).all()

        for info in ads_info:
            icon = ''
            if info.icon != '':
                icon = current_app.config['FILE_SERVER'] + info.icon

            res.append({'ad_id': info.id, 'name': info.name, 'position': info.position, 'source': info.source,
                        'refresh_time': refresh_time, 'refresh_count': refresh_count,
                        'third_link': info.third_link, 'icon': icon})

        if not res:
            c_data = get_response({"head": ErrorCode.SUCCESS})
            if isRelease:
                cache.set(key, c_data, timeout=60*5)
            return c_data
        else:
            c_data = get_response({"head": ErrorCode.SUCCESS, "body": res})
            if isRelease:
                cache.set(key, c_data, timeout=60*5)
            return c_data

class InteractiveAdsStatisticsApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('ad_info', type=list, required=True, help='param missing', location='json')

        super(InteractiveAdsStatisticsApi, self).__init__()

    def post(self):
        # print_info(action='Recevie', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        # msg = validate_client_no_imei(imei=json_req['imei'], app_version=json_req['app_version'],
        #                               function=self.__class__.__name__)
        # if msg != 'valid':
        #     return get_response(msg)

        if not check_imei(json_req['imei']):
            return get_response("valid")

        ad_id = []
        for info in json_req['ad_info']:
            if 'ad_id' not in info or 'type' not in info:
                # print_error(action='Response', function=self.__class__.__name__, branch='JSON_FORMAT_INVALID',
                #             api_version=g_api_version, imei=json_req['imei'])
                return get_response({'head': ErrorCode.JSON_FORMAT_INVALID}), 400
            ad_id.append(info['ad_id'])
        ad_id = set(ad_id)
        infos = InteractiveAds.query.filter(InteractiveAds.id.in_(ad_id)).all()
        if len(infos) <= 0:
            # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS0',
            #            api_version=g_api_version, imei=json_req['imei'])
            return get_response({'head': ErrorCode.SUCCESS, 'body': {'status': 1}})

        for info in infos:
            for ad in json_req['ad_info']:
                temp_type = -1
                if ad['ad_id'] == info.id:
                    temp_type = ad['type']

                if temp_type == -1 or temp_type >= 2:
                    continue

                interactive_ads = InteractiveAdsStatistics.query.filter_by(ad_id=info.id, operation=temp_type,
                                                                           imei=json_req['imei'],
                                                                           record_time=datetime.date.today()
                                                                           ).order_by(InteractiveAdsStatistics.id.desc()).limit(1).first()
                if interactive_ads is None:
                    interactive_ads = InteractiveAdsStatistics()
                    interactive_ads.ad_id = info.id
                    interactive_ads.imei = json_req['imei']
                    interactive_ads.operation = temp_type
                    interactive_ads.count = 1
                    interactive_ads.record_time = datetime.date.today()
                    db.session.add(interactive_ads)
                else:
                    interactive_ads.count += 1
                    db.session.add(interactive_ads)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print_error(action='Response', function=self.__class__.__name__, branch='INTERNAL_ERROR',
                        api_version=g_api_version, imei=json_req['imei'], data=e)
            return get_response({'head': ErrorCode.INTERNAL_ERROR})
        # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS', api_version=g_api_version,
        #            imei=json_req['imei'])
        if len(ad_id) != len(infos):
            return get_response({'head': ErrorCode.SUCCESS, 'body': {'status': 1}})
        else:
            return get_response({'head': ErrorCode.SUCCESS, 'body': {'status': 0}})


class GetLinkApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('ad_id', type=str, required=True, help='param missing', location='json')
        super(GetLinkApi, self).__init__()

    def post(self):
        #print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        #print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #          api_version=g_api_version, data=str(json_req))

        if not check_imei(json_req['imei']):
            return get_response("valid")

        msg = validate_client_no_imei(imei=json_req['imei'], app_version=json_req['app_version'],
                                      function=self.__class__.__name__)
        if msg != 'valid':
            return get_response(msg)

        icon_link = ''
        ads_info = InteractiveAds.query.filter_by(id=json_req['ad_id'])
        for info in ads_info:
            if len(info.third_link) > 4:
                cash_info = CashCat()
                data = {
                    'appUid': json_req['imei'],
                    'appType': 'app'
                }
                icon_link = cash_info.get_url(info.third_link, **data)

        # print_info(action='Response', function=self.__class__.__name__, branch="success", api_version=g_api_version,
        #            imei=json_req['imei'])

        return get_response({"head": ErrorCode.SUCCESS, "body": {'icon_link': icon_link}})


class SpecificadsStatisticsApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('number', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('type', type=int, required=True, help='param missing', location='json')
        super(SpecificadsStatisticsApi, self).__init__()

    def post(self):
        # print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        # msg = validate_client_no_imei(imei=json_req['imei'], app_version=json_req['app_version'],
        #                               function=self.__class__.__name__)
        # if msg != 'valid':
        #     return get_response(msg)

        if not check_imei(json_req['imei']):
            return get_response("valid")

        info = OpenScreenAds.query.filter_by(number=json_req['number']).limit(1).first()
        if info is None:
            # print_warn(action='Receive', function=self.__class__.__name__, branch='OPEN_SCREEN_ADS_NOT_EXIST',
            #            api_version=g_api_version)
            return get_response({'head': ErrorCode.OPEN_SCREEN_ADS_NOT_EXIST})

        ads_info = OpenScreenAdsStatistics.query.filter_by(
            ad_id=info.id, imei=json_req['imei'], operation=json_req['type'],
            record_time=datetime.date.today()).limit(1).first()

        if ads_info is not None:
            ads_info.count += 1
            db.session.add(ads_info)
        else:
            ads_info = OpenScreenAdsStatistics()
            ads_info.imei = json_req['imei']
            ads_info.ad_id = info.id
            ads_info.operation = json_req['type']
            ads_info.record_time = datetime.date.today()
            ads_info.count = 1
            db.session.add(ads_info)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print_error(action='Response', function=self.__class__.__name__, branch='INTERNAL_ERROR',
                        api_version=g_api_version, imei=json_req['imei'], data=e)

            return get_response({'head': ErrorCode.INTERNAL_ERROR})

        # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS', api_version=g_api_version,
        #            imei=json_req['imei'])

        return get_response({'head': ErrorCode.SUCCESS})


class GetBanneradsApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('channel', type=str, required=True, help='param missing', location='json')
        super(GetBanneradsApi, self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()

        # msg = validate_client_no_imei(imei=json_req['imei'], app_version=json_req['app_version'],
        #                               function=self.__class__.__name__)
        # if msg != 'valid':
        #     return get_response(msg)
        # version 0 历史版本, 1 最新版本

        if not check_imei(json_req['imei']):
            return get_response("valid")

        version = 0
        ver_query = AppVersion.query.filter_by(app_type=4)
        if json_req['imei'] not in get_white_imei_list():
            ver_query = ver_query.filter_by(is_released=True)
        version_info = ver_query.order_by(AppVersion.id.desc()).limit(1).first()
        if version_info is not None:
            if version_info.version_name == json_req['app_version']:
                version = 1

        infos = BannerAds.query.join(
            BannerConfig, BannerConfig.ad_id == BannerAds.id).filter(
            BannerAds.status == 1, BannerConfig.status == 1,
            BannerConfig.channel == json_req['channel'], BannerConfig.version == version)

        data = []
        flag = 0
        current_time = datetime.datetime.now()
        r_time = str(current_time.year) + '-' + str(current_time.month) + '-' + str(current_time.day) + " "
        for bannerad in infos:
            current_time = int(datetime.datetime.now().strftime('%H%M'))
            temp_type = -1
            refresh_count = 0
            refresh_time = r_time + '00:00~' + r_time + '00:00'
            icon = ''
            if bannerad.icon != '':
                icon = current_app.config['FILE_SERVER'] + bannerad.icon

            # 上午时间 08:00~12:00
            if not current_time <= 800 and current_time < 1300:
                temp_type = 0
                refresh_time = r_time + '08:00~' + r_time + '13:00'
            # 下午时间 12:00~18:00
            elif not current_time <= 1300 and current_time < 1800:
                temp_type = 1
                refresh_time = r_time + '12:00~' + r_time + '18:00'
            # 晚上时间 18:00~23:59
            elif not current_time <= 1800 and current_time < 2359:
                temp_type = 2
                refresh_time = r_time + '18:00~' + r_time + '23:59'

            if bannerad.refresh_status == 1:
                refresh_user_info = BannerRefreshUser.query.filter_by(
                    ad_id=bannerad.id, record_time=datetime.date.today(), imei=json_req['imei'], type=temp_type).limit(1).first()
                if refresh_user_info is None:
                    refresh_info = BannerRefreshData.query.filter_by(ad_id=bannerad.id, type=temp_type,
                                                                     record_time=datetime.date.today()).limit(1).first()
                    if refresh_info is not None and refresh_info.control_number > refresh_info.actual_number:
                        # 取余数
                        remainder = refresh_info.control_times % refresh_info.control_number
                        # 取整数
                        integer = int(refresh_info.control_times / refresh_info.control_number)

                        refresh_user_info = BannerRefreshUser()
                        refresh_user_info.ad_id = bannerad.id
                        refresh_user_info.record_time = datetime.date.today()
                        refresh_user_info.imei = json_req['imei']
                        refresh_user_info.type = temp_type
                        if remainder > 0 and remainder > refresh_info.actual_number:
                            refresh_count = integer + 1
                            refresh_user_info.count = refresh_count
                        else:
                            refresh_user_info.count = 1
                            refresh_count = 1
                        refresh_info.actual_number += 1

                        db.session.add(refresh_user_info)
                        db.session.add(refresh_info)
                        flag = 1

            data.append({'ad_id': bannerad.id, 'name': bannerad.name, 'position': bannerad.position,
                         'source': bannerad.source, 'display_number': bannerad.display_number,
                         'carousel': bannerad.carousel, 'carousel_interval': bannerad.carousel_interval, 'icon': icon,
                         'icon_dest_link': bannerad.icon_dest_link,
                         'ad_number': bannerad.number,
                         'refresh_time': refresh_time,
                         'refresh_count': refresh_count,
                         'start_time': bannerad.start_time.strftime('%Y-%m-%d %H: %M: %S'),
                         'end_time': bannerad.end_time.strftime('%Y-%m-%d %H: %M: %S')})

        if flag == 1:
            try:
                db.session.commit()
            except Exception as e:
                print_error(action='Response', function=self.__class__.__name__, branch='INTERNAL_ERROR',
                            api_version=g_api_version, imei=json_req['imei'], data=e)
                return get_response({'head': ErrorCode.INTERNAL_ERROR})

        #print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS', api_version=g_api_version,
        #           imei=json_req['imei'])
        return get_response({'head': ErrorCode.SUCCESS, 'body': data})


class GetOpenAdsApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('channel', type=str, required=True, help='param missing', location='json')
        super(GetOpenAdsApi, self).__init__()

    def post(self):
        # print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        # msg = validate_client_no_imei(imei=json_req['imei'], app_version=json_req['app_version'],
        #                               function=self.__class__.__name__)
        # if msg != 'valid':
        #     return get_response(msg)

        if not check_imei( json_req['imei'] ):
            return get_response("valid")
        key = "GetOpenAdsApi_" + json_req['app_version'] + "_" + json_req['channel'] + datetime.datetime.now().strftime('%Y-%m-%d-%H')
        isRelease = False
        if json_req['imei'] not in get_white_imei_list():
            isRelease = True
            c_data = cache.get(key)
            if c_data:
                return c_data

        version = 0
        ver_query = AppVersion.query.filter_by(app_type=4)
        if isRelease:
            ver_query = ver_query.filter_by(is_released=True)
        version_info = ver_query.order_by(AppVersion.id.desc()).limit(1).first()
        if version_info is not None:
            if version_info.version_name == json_req['app_version']:
                version = 1

        refresh_count = 0
        current_time = datetime.datetime.now()
        r_time = str(current_time.year) + '-' + str(current_time.month) + '-' + str(current_time.day) + " "
        refresh_time = r_time + '00:00~' + r_time + '00:00'

        res = []
        flag = 0

        ads_info = OpenScreenAds.query.join(OpenConfig, OpenConfig.ad_id == OpenScreenAds.id).filter(
            OpenScreenAds.status == 1, OpenConfig.status == 1, OpenConfig.channel == json_req['channel'],
            OpenConfig.version == version)

        for info in ads_info:
            icon = ''
            skip_count = 0
            if info.icon != '':
                icon = current_app.config['FILE_SERVER'] + info.icon

            res.append({'ad_id': info.id, 'name': info.name, 'position': info.position, 'source': info.source,
                        'start_time': info.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'ad_number': info.number,
                        'skip_count': skip_count,
                        'sort': info.unit_price,
                        'app_link': info.app_link,
                        'refresh_count': refresh_count,
                        'refresh_time': refresh_time,
                        'end_time': info.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'display_number': info.display_number,
                        'skip_time': info.skip_time, 'icon': icon})

        if not res:
            c_data = get_response({"head": ErrorCode.SUCCESS})
            if isRelease:
                cache.set(key, c_data, timeout=60*5)
            return c_data
        else:
            c_data = get_response({"head": ErrorCode.SUCCESS, "body": res})
            if isRelease:
                cache.set(key, c_data, timeout=60*5)
            return c_data


class GetAdsIconApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        super(GetAdsIconApi, self).__init__()

    def post(self):
        # print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        # msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
        #                       function=self.__class__.__name__)
        # if msg != 'valid':
        #     return get_response(msg)

        if not check_imei(json_req['imei']):
            return get_response("valid")

        ads_strategy = 0
        strategy = ServiceProtocol.query.filter_by(category=1).limit(1).first()
        if strategy is not None:
            ads_strategy = int(strategy.content)

        infos = AdsIcon.query.filter_by(status=1).all()
        resp = []

        for info in infos:
            icon_link = ''
            if len(info.icon_addr) > 10:
                icon_link = current_app.config['FILE_SERVER'] + info.icon_addr
            value = {
                "position": info.position,
                "icon_link": icon_link,
                "jump_link": info.jump_link
            }
            resp.append(value)

        return get_response({'head': ErrorCode.SUCCESS, 'body': {'ads_icon': resp, 'ads_strategy': ads_strategy}})


class GetWeChatFeatureApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('frame_version_code', type=str, required=True,
                                    help='param missing', location='json')
        self.req_parse.add_argument('wechat_version', type=str, required=True, help='param missing', location='json')
        super(GetWeChatFeatureApi, self).__init__()

    def post(self):
        # print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        if not json_req['frame_version_code'].isdigit():
            return get_response({'frame_version_code': 'frame version code not digit'}), 400
        # msg = validate_client_no_imei(imei=json_req['imei'], app_version=json_req['app_version'],
        #                               function=self.__class__.__name__)
        # if msg != 'valid':
        #     return get_response(msg)

        app_query = AppVersion.query
        if json_req['imei'] not in get_white_imei_list():
            app_query = app_query.filter_by(is_released=True)
        app_query = app_query.filter_by(version_name=json_req['wechat_version'], app_type=99)

        res = app_query.filter(AppVersion.min_version_code <= int(json_req['frame_version_code']),
                               AppVersion.max_version_code >= int(json_req['frame_version_code'])).limit(1).first()
        if res is not None:
            # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS',
            #            api_version=g_api_version, imei=json_req['imei'])
            return get_response({'head': ErrorCode.SUCCESS, 'body': {
                'url': current_app.config['FILE_SERVER'] + res.app_dir}})
        else:
            # print_info(action='Response', function=self.__class__.__name__, branch='ALREADY_LATEST',
            #            api_version=g_api_version, imei=json_req['imei'])
            return get_response({'head': ErrorCode.ALREADY_LATEST})


class FeatureApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('frame_version_code', type=str, required=True,
                                    help='param missing', location='json')
        self.req_parse.add_argument('version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('version_code', type=int, required=True, help='param missing', location='json')
        super(FeatureApi, self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()
        if not json_req['frame_version_code'].isdigit():
            return get_response({'frame_version_code': 'frame version code not digit'}), 400
        # msg = validate_client_no_imei(imei=json_req['imei'], app_version=json_req['app_version'],
        #                               function=self.__class__.__name__)
        # if msg != 'valid':
        #     return get_response(msg)

        # redis.rpush('%s-feature' % datetime.datetime.now().date(), dumps({'imei': json_req['imei'],
        #                                                                   'version_name': json_req['version'],
        #                                                                   'version_code': json_req['version_code']}))
        data = dumps({'imei': json_req['imei'], 'version_name': json_req['version'],
                      'version_code': json_req['version_code']})
        queue.feature(data)
        key = "FeatureApi" + str(json_req['app_version']) + str(json_req['frame_version_code']) + \
              str(json_req['version']) + str(json_req['version_code'])

        release_flag = False
        if json_req['imei'] not in get_white_imei_list():
            release_flag = True
            data = cache_simple.get(key)
            if data:
                return get_response(data)

        res = feature_file()
        version_code = json_req['version_code']
        frame_version_code = int(json_req['frame_version_code'])
        version_name = json_req['version']
        if len(res) > 0:
            value = res.get(version_name, 'no')
            if value != 'no':
                versions = res[version_name]
                for version in versions:
                    if (version.min_version_code <= frame_version_code) \
                            and (version.max_version_code >= frame_version_code) \
                            and version.version_code > version_code:
                        if release_flag and version.is_released is False:
                            continue

                        data = {'head': ErrorCode.SUCCESS,
                                'body': {'url': current_app.config['FILE_SERVER'] + version.app_dir,
                                         'version_code': version.version_code}}
                        if release_flag:
                            cache_simple.set(key, data, timeout=60 * 10)  # 对单条数据添加缓存
                        return get_response(data)

        if version_code == 0:
            data = {'head': ErrorCode.VERSION_CODE_NOT_SUPPORTED}
            if release_flag:
                cache_simple.set(key, data, timeout=60 * 10)  # 对单条数据添加缓存
            return get_response(data)

        data = {'head': ErrorCode.ALREADY_LATEST}
        if release_flag:
            cache_simple.set(key, data, timeout=60 * 10)  # 对单条数据添加缓存
        return get_response(data)


class JudgeAddKeyApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing')
        self.req_parse.add_argument('num', type=str, required=True, help='param missing')
        super(JudgeAddKeyApi, self).__init__()

    def get(self):

        json_req = self.req_parse.parse_args()

        msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
                              function=self.__class__.__name__)
        if msg != 'valid':
            return get_response(msg)

        user_record = UserKeyRecord.query.filter_by(imei=json_req['imei'], status=1).limit(1).first()
        if user_record is None:
            return get_response({'head': ErrorCode.ENTER_PAGE})
        else:
            return get_response({'head': ErrorCode.SUCCESS, 'body': {"num": json_req['num']}})


class CheckKeyApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('key_id', type=str, required=True, help='param missing', location='json')
        super(CheckKeyApi, self).__init__()

    def post(self):

        if True:
            return get_response({'head': ErrorCode.KEY_INVALID})

        # json_req = self.req_parse.parse_args()
        # msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
        #                       function=self.__class__.__name__)
        # if msg != 'valid':
        #     return get_response(msg)
        #
        # user_record = UserKeyRecord.query.filter_by(key_id=json_req['key_id'], imei=json_req['imei'], status=1).limit(1).first()
        # if user_record is None:
        #     key = Key.query.filter_by(id=json_req['key_id'], status=0).limit(1).first()
        #     if key is None:
        #         return get_response({'head': ErrorCode.KEY_INVALID})
        #     u_key_record = UserKeyRecord.query.filter_by(imei=json_req['imei'], status=1).limit(1).first()
        #     if u_key_record is not None and u_key_record.key_id != json_req['key_id']:
        #         return get_response({'head': ErrorCode.IMEI_HAS_KEY})
        #
        #     if key.status == 0:
        #         user_record = UserKeyRecord()
        #         user_record.key_id = json_req['key_id']
        #         user_record.imei = json_req['imei']
        #         user_record.activate_time = datetime.datetime.now()
        #         user_record.status = 1
        #         db.session.add(user_record)
        #         key.status = 1
        #         db.session.add(key)
        #         key_record = KeyRecord.query.filter_by(id=key.key_record_id).limit(1).first()
        #         vip_ad_time = 0
        #         if key_record is not None:
        #             vip_ad_time = key_record.vip_ad_time
        #         imei_vip = ImeiVip.query.filter_by(imei=json_req['imei']).limit(1).first()
        #         if imei_vip is None:
        #             imei_vip = ImeiVip()
        #             imei_vip.imei = json_req['imei']
        #             imei_vip.create_time = datetime.datetime.now()
        #             imei_vip.start_time = datetime.datetime.now().date()
        #             imei_vip.valid_time = datetime.datetime.now().date() + datetime.timedelta(days=vip_ad_time - 1)
        #             db.session.add(imei_vip)
        #         else:
        #             imei_vip.start_time = datetime.datetime.now().date()
        #             imei_vip.valid_time = datetime.datetime.now().date() + datetime.timedelta(days=vip_ad_time - 1)
        #             db.session.add(imei_vip)
        #         db.session.commit()
        #         return get_response({'head': ErrorCode.SUCCESS})
        # else:
        #     return get_response({'head': ErrorCode.SUCCESS})


class BuykeyApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('channel', type=str, help='param missing', location='json')
        super(BuykeyApi, self).__init__()

    def post(self):

        json_req = self.req_parse.parse_args()

        if json_req['channel'] is None:
            price = 19900
        else:
            k_channel = KeyChannel.query.filter_by(channel=json_req['channel']).limit(1).first()
            if k_channel is not None:
                price = k_channel.price
            else:
                price = 19900
        msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
                              function=self.__class__.__name__)
        if msg != 'valid':
            return get_response(msg)

        user_record = UserKeyRecord.query.filter_by(imei=json_req['imei'], status=1).limit(1).first()
        if user_record is not None:
            return get_response({'head': ErrorCode.KEY_EXIST})

        key_order = KeyOrder()
        key_order.id = gen_key_order_num()
        key_order.key_id = create_key()
        key_order.price = price
        key_order.imei = json_req['imei']
        key_order.status = 0
        try:
            db.session.add(key_order)
            today = datetime.datetime.today()
            expire_time = today + datetime.timedelta(minutes=30)
            res = WexinPay().unified_order(out_trade_no=key_order.id,
                                           total_fee=key_order.price,
                                           time_start=today.strftime('%Y%m%d%H%M%S'),
                                           time_expire=expire_time.strftime('%Y%m%d%H%M%S'),
                                           body='key', trade_type='APP')

            res['order_number'] = key_order.id
            res['price'] = key_order.price
            db.session.commit()
            return get_response({'head': ErrorCode.SUCCESS, 'body': res})
        except Exception as e:
            db.session.rollback()
            print_error(action='Response', function=self.__class__.__name__, branch='INTERNAL_ERROR',
                        api_version=g_api_version, imei=json_req['imei'], data=e)
            return get_response({'head': ErrorCode.INTERNAL_ERROR})


class ChannelFrameUpdateApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('channel', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('frames', type=list, required=True, help='param missing', location='json')
        super(ChannelFrameUpdateApi, self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()

        # msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
        #                       function=self.__class__.__name__)
        # if msg != 'valid':
        #     return get_response(msg)

        key = "ChannelFrameUpdateApi_" + str(json_req['app_version']) + str(json_req['channel']) + \
              str(json_req['frames'])

        release_flag = False
        if json_req['imei'] not in get_white_imei_list():
            release_flag = True
            data = cache_simple.get(key)
            if data:
                return data

        app_obj = ChannelVersion.query.filter_by(version_name=json_req['app_version']).limit(1).first()
        query = AvatarVersion.query
        if release_flag:
            query = query.filter_by(status=2)
        else:
            query = query.filter(AvatarVersion.status > 0)

        res_list = []
        for frame in json_req['frames']:
            if not str(frame['version_code']).isdigit():
                return get_response({'version_code': 'version code not digit'}), 400

            if 'number' not in frame or 'version_code' not in frame:
                data = {'head': ErrorCode.JSON_FORMAT_INVALID}
                if release_flag:
                    cache_simple.set(key, data, timeout=60 * 10)  # 对单条数据添加缓存
                return get_response(data), 400
            ver_query = query.filter_by(number=int(frame['number'])). \
                order_by(AvatarVersion.version_code.desc())
            if app_obj is not None:
                app_version = ver_query.filter(AvatarVersion.version_code.between(
                    app_obj.min_version_code, app_obj.max_version_code)).limit(1).first()
                if app_version and app_version.version_code > int(frame['version_code']):
                    res_list.append({'number': app_version.number, 'package_name': app_version.pack_name,
                                     'status': app_version.update_status, 'c_status': app_obj.status})
        if res_list:
            data = {'head': ErrorCode.SUCCESS, 'body': res_list}
            if release_flag:
                cache_simple.set(key, data, timeout=60 * 10)  # 对单条数据添加缓存
            return get_response(data)
        else:
            data = {'head': ErrorCode.ALREADY_LATEST}
            if release_flag:
                cache_simple.set(key, data, timeout=60 * 10)  # 对单条数据添加缓存
            return get_response(data)


class ChannelPluginUpdateApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('frame_version_code', type=str, required=True,
                                    help='param missing', location='json')
        self.req_parse.add_argument('plugins', type=list, required=True, help='param missing', location='json')
        self.req_parse.add_argument('channel', type=str, required=True, help='param missing', location='json')
        super(ChannelPluginUpdateApi, self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()
        if not json_req['frame_version_code'].isdigit():
            return get_response({'frame_version_code': 'frame version code not digit'}), 400

        key = "ChannelPluginUpdateApi_" + str(json_req['app_version']) + str(json_req['frame_version_code']) + \
              str(json_req['plugins']) + str(json_req['channel'])


        release_flag = False
        if json_req['imei'] not in get_white_imei_list():
            release_flag = True
            data = cache_simple.get(key)
            if data:
                return data

        app_query = ChannelVersion.query
        if release_flag:
            app_query = app_query.filter_by(is_released=True)
        app_query = app_query.join(AppList, AppList.app_type == ChannelVersion.app_type)

        url_res = []
        for plugin in json_req['plugins']:
            if 'package_name' not in plugin or 'version_code' not in plugin:
                data = {'head': ErrorCode.JSON_FORMAT_INVALID}
                if release_flag:
                    cache_simple.set(key, data, timeout=60 * 10)  # 对单条数据添加缓存
                return data

            res = app_query.filter(AppList.package_name == plugin['package_name'],
                                   ChannelVersion.min_version_code <= int(json_req['frame_version_code']),
                                   ChannelVersion.max_version_code >= int(json_req['frame_version_code']),
                                   ChannelVersion.version_code > int(plugin['version_code'])). \
                order_by(ChannelVersion.version_code.desc()).limit(1).first()
            if res:
                url_res.append(current_app.config['FILE_SERVER'] + res.app_dir)
        if url_res:
            data = {'head': ErrorCode.SUCCESS, 'body': {'url': url_res}}
            if release_flag:
                cache_simple.set(key, data, timeout=60 * 10)  # 对单条数据添加缓存
            return get_response(data)
        else:
            data = {'head': ErrorCode.ALREADY_LATEST}
            if release_flag:
                cache_simple.set(key, data, timeout=60 * 10)  # 对单条数据添加缓存
            return get_response(data)


class GetAvatarChannelAppUrlApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('version_code', type=int, required=True, help='param missing', location='json')
        self.req_parse.add_argument('number', type=int, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_name', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('channel', type=str, required=True, help='param missing', location='json')
        super(GetAvatarChannelAppUrlApi, self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()
        # msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
        #                       function=self.__class__.__name__)
        # if msg != 'valid':
        #     return get_response(msg)

        """
        s_manager = SpreadManager.query.filter_by(channelname=json_req['channel']).first()
        if s_manager is None:
            print_info(action='Response', function=self.__class__.__name__, branch='CHANNEL_NOT_EXIST',
                      api_version=g_api_version, imei=json_req['imei'])
            return {'head': ErrorCode.CHANNEL_NOT_EXIST}
        s_id = s_manager.id
        app_obj = ChannelVersion.query.filter_by(version_name=json_req['app_version'], spread_id=s_id).first()
        """
        app_obj = ChannelVersion.query.filter_by(version_name=json_req['app_version']).limit(1).first()
        query = AvatarVersion.query
        if json_req['imei'] not in get_white_imei_list():
            query = query.filter_by(status=2)
        else:
            query = query.filter(AvatarVersion.status > 0)
        if app_obj is not None:
            query = query.filter(AvatarVersion.version_code.between(app_obj.min_version_code, app_obj.max_version_code))

        avatar_version = query.filter_by(number=json_req['number']).order_by(AvatarVersion.version_code.desc()).limit(1).first()
        if avatar_version is None:
            # print_warn(action='Response', function=self.__class__.__name__, branch='AVATAR_VERSION_NOT_EXIST',
            #            api_version=g_api_version, imei=json_req['imei'])
            return get_response({'head': ErrorCode.AVATAR_VERSION_NOT_EXIST})
        else:
            we_avatar = WeAvatar.query.filter_by(app_name=json_req['app_name'], number=avatar_version.number,
                                                 app_id=avatar_version.id).limit(1).first()
            if we_avatar is None:
                avatar = WeAvatar()
                avatar.app_id = avatar_version.id
                avatar.app_name = json_req['app_name']
                avatar.number = avatar_version.number
                avatar.down_addr = format_apk(os.path.join(os.getcwd(), avatar_version.app_dir),
                                              avatar_version.number, json_req['app_name'])
                db.session.add(avatar)
                db.session.commit()
                return get_response({'head': ErrorCode.SUCCESS, 'body': {
                    'down_addr': current_app.config['FILE_SERVER'] + avatar.down_addr}})
            else:
                return get_response({'head': ErrorCode.SUCCESS, 'body': {
                    'down_addr': current_app.config['FILE_SERVER'] + we_avatar.down_addr}})


class CheckChannelAppUpdateApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_type', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('version_code', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('channel', type=str, required=True, help='param missing', location='json')
        super(CheckChannelAppUpdateApi, self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()
        if not json_req['version_code'].isdigit():
            return get_response({'version_code': 'version code not digit'}), 400
        # msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
        #                       function=self.__class__.__name__)
        # if msg != 'valid':
        #     return get_response(msg)

        if not check_imei(json_req['imei']):
            return get_response("valid")

        if json_req['imei'] not in get_white_imei_list():
            app_version = get_app_version()
        else:
            app_version = get_app_version_white()

        if app_version is None:
            return get_response({'head': ErrorCode.APP_NOT_EXIST})
        if app_version.version_code <= int(json_req['version_code']) and json_req['app_type'] != 4:
            return get_response({'head': ErrorCode.ALREADY_LATEST})
        else:
            return get_response({'head': ErrorCode.SUCCESS,
                                 'body': {'url': current_app.config['FILE_SERVER'] + app_version.app_dir,
                                          'status': app_version.status, 'version_name': app_version.version_name,
                                          'update_msg': app_version.update_msg}})


class GetCommGroupApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing')
        self.req_parse.add_argument('g_type', type=int, required=True, help='param missing')
        super(GetCommGroupApi, self).__init__()

    def get(self):
        # print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        # msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
        #                       function=self.__class__.__name__)
        # if msg != 'valid':
        #     return get_response(msg)

        group_info = CommunicationGroup.query.filter_by(type=json_req['g_type']).all()
        if group_info is not None and len(group_info) > 0:
            data = []
            for info in group_info:
                data.append({'type': info.type, 'group_number': info.group_number, 'group_key': info.group_key})
                # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS',
                #            api_version=g_api_version, imei=json_req['imei'])
            return get_response({'head': ErrorCode.SUCCESS, 'body': {'group_info': data}})

        return get_response({'head': ErrorCode.SUCCESS})


class GetKeyChannelApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing')
        self.req_parse.add_argument('channel', type=str, required=True, help='param missing')
        super(GetKeyChannelApi, self).__init__()

    def get(self):
        # print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
                              function=self.__class__.__name__)
        if msg != 'valid':
            return get_response(msg)

        channel_info = KeyChannel.query.filter_by(channel=json_req['channel'], status=1).limit(1).first()
        if channel_info is not None:
            # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS',
            #            api_version=g_api_version, imei=json_req['imei'])

            return get_response({'head': ErrorCode.SUCCESS, 'body': {'channel': channel_info.channel,
                                                                     'price': channel_info.price,
                                                                     'msg': channel_info.msg}})

        return get_response({'head': ErrorCode.SUCCESS})


class GetKeyInfoApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('user_id', type=str, required=True, help='param missing')
        self.req_parse.add_argument('we_key_id', type=str, required=True, help='param missing')
        super(GetKeyInfoApi, self).__init__()

    def get(self):
        # print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        resp = []
        record_info = KeyRecord.query.filter_by(phone_num=json_req['user_id'],
                                                we_record_id=json_req['we_key_id']).limit(1).first()
        if record_info is not None:
            key_infos = Key.query.filter(Key.key_record_id == record_info.id)
            for key_info in key_infos:
                cell = {
                    'key_id': key_info.id,
                    'status': key_info.status
                }
                resp.append(cell)
        # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS', api_version=g_api_version)

        return get_response({'head': ErrorCode.SUCCESS, 'body': resp})


class MakeKeyApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('user_id', type=str, required=True, help='param missing')
        self.req_parse.add_argument('we_key_id', type=str, required=True, help='param missing')
        self.req_parse.add_argument('ad_time', type=int, required=True, help='param missing')
        self.req_parse.add_argument('key_count', type=int, required=True, help='param missing')
        super(MakeKeyApi, self).__init__()

    def post(self):
        # print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        record_info = KeyRecord.query.filter_by(phone_num=json_req['user_id'],
                                                we_record_id=json_req['we_key_id']).limit(1).first()
        if record_info is None:
            key_record = KeyRecord()
            key_record.id = str(time.time() * 10000).split('.')[0]
            # key_record.expire_time = datetime.datetime.now() + datetime.timedelta(days=12 * 30 * 100)
            key_record.vip_time = 365 * 100
            key_record.vip_ad_time = json_req['ad_time']
            key_record.oeprator = 'Webusiness'
            key_record.content = '微商客购买终身授权码'
            key_record.count = json_req['key_count']
            key_record.create_time = datetime.datetime.now()
            key_record.phone_num = json_req['user_id']
            key_record.we_record_id = json_req['we_key_id']
            db.session.add(key_record)
            db.session.commit()

            for i in range(json_req['key_count']):
                key = Key()
                key.id = create_key()
                key.key_record_id = key_record.id
                db.session.add(key)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                db.session.delete(key_record)
                db.session.commit()
                print_error(action='Response', function=self.__class__.__name__, branch='INTERNAL_ERROR',
                            api_version=g_api_version, data=e)
                return get_response({'head': ErrorCode.INTERNAL_ERROR})

        # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS', api_version=g_api_version)

        return get_response({'head': ErrorCode.SUCCESS})


class GetNoticeApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing')
        self.req_parse.add_argument('flag_id', type=int, required=True, help='param missing')
        super(GetNoticeApi, self).__init__()

    def get(self):
        json_req = self.req_parse.parse_args()
        # 时间段的判断
        hour = int(datetime.datetime.now().strftime('%Y-%m-%d-%H').split("-")[-1])
        time_quantum = 0
        if hour < 6:
            time_quantum = 0
        elif hour < 12:
            time_quantum = 1
        elif hour < 18:
            time_quantum = 2
        else:
            time_quantum = 3
        query = SysNotice.query.filter(SysNotice.flag_id > json_req['flag_id'], SysNotice.time_quantum == time_quantum,
                                       SysNotice.status == 1, SysNotice.end_time >= datetime.datetime.now().date(),
                                       datetime.datetime.now().date() >= SysNotice.start_time)
        max_id = json_req['flag_id']
        data = []
        for notice in query:
            if notice.notice_type == 1:
                if notice.flag_id > max_id:
                    max_id = notice.flag_id
                continue
            dic = dict(id=notice.id, title=notice.title, content=notice.content, flag_id=notice.flag_id,
                       remarks=notice.remarks, oeprator=notice.oeprator,
                       start_time=notice.start_time.strftime('%Y-%m-%d'),
                       end_time=notice.end_time.strftime('%Y-%m-%d'))
            if notice.flag_id > max_id:
                max_id = notice.flag_id
            data.append(dic)

        return get_response({'head': ErrorCode.SUCCESS, 'body': {'notices': data, 'max_id': max_id}})


class NewGetNoticeApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing')
        self.req_parse.add_argument('flag_id', type=int, required=True, help='param missing')
        super(NewGetNoticeApi, self).__init__()

    def get(self):
        json_req = self.req_parse.parse_args()
        key = 'NewGetNoticeApi_' + datetime.datetime.now().strftime('%Y-%m-%d-%H')
        data = cache.get(key)
        if data:
            return data
        # 时间段的判断
        hour = int(datetime.datetime.now().strftime('%Y-%m-%d-%H').split("-")[-1])
        time_quantum = 0
        if hour < 6:
            time_quantum = 0
        elif hour < 12:
            time_quantum = 1
        elif hour < 18:
            time_quantum = 2
        else:
            time_quantum = 3
        notice = SysNotice.query.filter(SysNotice.status == 1, SysNotice.time_quantum == time_quantum,
                                       SysNotice.end_time >= datetime.datetime.now().date(),
                                       datetime.datetime.now().date() >= SysNotice.start_time).\
                                       order_by(SysNotice.flag_id.desc()).limit(1).first()
        max_id = json_req['flag_id']
        data = []
        if notice:
            if notice.notice_type == 1:
                icon = current_app.config['FILE_SERVER'] + notice.icon
                icon_link = notice.icon_link
            else:
                icon = ''
                icon_link = ''
            dic = dict(id=notice.id, title=notice.title, content=notice.content, flag_id=notice.flag_id,
                       notice_type=notice.notice_type, icon=icon, icon_link=icon_link,
                       remarks=notice.remarks, oeprator=notice.oeprator,
                       start_time=notice.start_time.strftime('%Y-%m-%d'),
                       end_time=notice.end_time.strftime('%Y-%m-%d'), notice_user=notice.notice_user)

            max_id = notice.flag_id
            data.append(dic)

        data = get_response({'head': ErrorCode.SUCCESS, 'body': {'notices': data, 'max_id': max_id}})
        cache.set(key, data, timeout=60*60)
        return data


class ReadNoticeApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing')
        self.req_parse.add_argument('notice_id', type=str, required=True, help='param missing')
        super(ReadNoticeApi, self).__init__()

    def get(self):
        # print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
                              function=self.__class__.__name__)
        if msg != 'valid':
            return get_response(msg)

        n_record = NoticeRecord.query.filter_by(notice_id=json_req['notice_id'], imei=json_req['imei'],
                                                status=1).limit(1).first()
        if n_record is None:
            n_record = NoticeRecord()
            n_record.notice_id = json_req['notice_id']
            n_record.imei = json_req['imei']
            n_record.status = 1
            db.session.add(n_record)
            db.session.commit()
        # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS', api_version=g_api_version,
        #            imei=json_req['imei'])

        return get_response({'head': ErrorCode.SUCCESS})


class ServiceProtocolApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('category', type=int, required=True, help='param missing', location='json')
        super(ServiceProtocolApi, self).__init__()

    def post(self):
        # print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        # msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
        #                       function=self.__class__.__name__)
        # if msg != 'valid':
        #     return get_response(msg)
        data = cache_simple.get('ServiceProtocolApi')
        if data:
            return get_response(data)
        protocol = ServiceProtocol.query.filter_by(category=json_req['category']).limit(1).first()
        if protocol is None:
            data = {'head': ErrorCode.NOT_PROTOCOL}
            cache_simple.set('ServiceProtocolApi', data, timeout=60*30)
            return get_response(data)
        else:
            data = {'head': ErrorCode.SUCCESS, 'body': {'content': protocol.content}}
            cache_simple.set('ServiceProtocolApi', data, timeout=60 * 30)
            return get_response(data)


class CrackMakeKeyApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('user_id', type=str, required=True, help='param missing')
        self.req_parse.add_argument('we_key_id', type=str, required=True, help='param missing')
        self.req_parse.add_argument('ad_time', type=int, required=True, help='param missing')
        self.req_parse.add_argument('key_count', type=int, required=True, help='param missing')
        super(CrackMakeKeyApi, self).__init__()

    def post(self):
        print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
                  api_version=g_api_version, data=str(json_req))
        record_info = KeyRecord.query.filter_by(phone_num=json_req['user_id'],
                                                we_record_id=json_req['we_key_id']).limit(1).first()
        if record_info is None:
            key_record = KeyRecord()
            key_record.id = str(time.time() * 10000).split('.')[0]
            # key_record.expire_time = datetime.datetime.now() + datetime.timedelta(days=12 * 30 * 100)
            key_record.vip_time = 365 * 100
            key_record.vip_ad_time = json_req['ad_time']
            key_record.oeprator = 'crack'
            key_record.content = '微商客破解版赠送终身授权码'
            key_record.count = json_req['key_count']
            key_record.create_time = datetime.datetime.now()
            key_record.phone_num = json_req['user_id']
            key_record.we_record_id = json_req['we_key_id']
            db.session.add(key_record)
            db.session.commit()

            for i in range(json_req['key_count']):
                key = Key()
                key.id = create_key()
                key.key_record_id = key_record.id
                db.session.add(key)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                db.session.delete(key_record)
                db.session.commit()
                print_error(action='Response', function=self.__class__.__name__, branch='INTERNAL_ERROR',
                            api_version=g_api_version, data=e)
                return get_response({'head': ErrorCode.INTERNAL_ERROR})

        # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS', api_version=g_api_version)

        return get_response({'head': ErrorCode.SUCCESS})


class JudgeAddKeyArrApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=list, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('num', type=str, required=True, help='param missing', location='json')
        super(JudgeAddKeyArrApi, self).__init__()

    def post(self):
        # print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        imei_list = get_imei(json_req['imei'])
        for imei in imei_list:
            msg = validate_client(imei=imei, app_version=json_req['app_version'],
                                  function=self.__class__.__name__)
            if msg != 'valid':
                return get_response(msg)

        # from flask import request
        # ip = request.headers.get('X-Forwarded-For')
        # print('judge: ', ip, str(json_req['imei']))

        imei_data = db.session.query(UserKeyRecord.imei).filter(UserKeyRecord.imei.in_(imei_list),
                                                                UserKeyRecord.status == 1).limit(1).first()
        if imei_data is not None and imei_data[0] is not None:
            # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS',
            #            api_version=g_api_version, imei=str(json_req['imei']))
            return get_response({'head': ErrorCode.SUCCESS, 'body': {"num": json_req['num'], 'imei': imei_data[0]}})

        return get_response({'head': ErrorCode.ENTER_PAGE})


class CheckKeyArrApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=list, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('key_id', type=str, required=True, help='param missing', location='json')
        super(CheckKeyArrApi, self).__init__()

    def post(self):
        # print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        imei_list = get_imei(json_req['imei'])
        for imei in imei_list:
            msg = validate_client(imei=imei, app_version=json_req['app_version'], function=self.__class__.__name__)
            if msg != 'valid':
                return get_response(msg)

        # from flask import request
        # ip = request.headers.get('X-Forwarded-For')
        # print('check: ', ip, str(json_req['imei']))

        user_record = UserKeyRecord.query.filter(UserKeyRecord.imei.in_(imei_list), UserKeyRecord.status == 1).all()
        if len(user_record) <= 0:
            key = Key.query.filter_by(id=json_req['key_id'], status=0).limit(1).first()
            if key is None:
                # print_error(action='Response', function=self.__class__.__name__, branch='KEY_INVALID',
                #             api_version=g_api_version, imei=str(json_req['imei']))
                return get_response({'head': ErrorCode.KEY_INVALID})

            if key.status == 0:
                for imei in imei_list:
                    user_record = UserKeyRecord()
                    user_record.key_id = json_req['key_id']
                    user_record.imei = imei
                    user_record.activate_time = datetime.datetime.now()
                    user_record.status = 1
                    db.session.add(user_record)

                key.status = 1
                db.session.add(key)

                db.session.commit()
                # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS',
                #            api_version=g_api_version, imei=str(json_req['imei']))
                return get_response({'head': ErrorCode.SUCCESS})
        else:
            for val in user_record:
                if val.key_id == json_req['key_id']:
                    # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS',
                    #            api_version=g_api_version, imei=str(json_req['imei']))
                    return get_response({'head': ErrorCode.SUCCESS})

            # print_error(action='Response ', function=self.__class__.__name__, branch='IMEI_HAS_KEY',
            #             api_version=g_api_version, imei=str(json_req['imei']))
            return get_response({'head': ErrorCode.IMEI_HAS_KEY})


class CheckAppVersionApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('versioncode', type=int, required=True, help='param missing', location='json')
        self.req_parse.add_argument('versionname', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('md5', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('build_time', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('build_rev', type=str, required=True, help='param missing', location='json')
        super(CheckAppVersionApi, self).__init__()

    def post(self):
        # print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        appcheck = AppVersionCheck.query.filter_by(versioncode=json_req['versioncode'],
                                                   versionname=json_req['versionname'],
                                                   build_time=json_req['build_time'],
                                                   build_rev=json_req['build_rev']).limit(1).first()
        if appcheck is not None:
            return get_response({'head': ErrorCode.SUCCESS, 'body': {'status': 1}})
        else:
            return get_response({'head': ErrorCode.SUCCESS, 'body': {'status': 0}})


class VerifyApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('godin_id', type=str, required=True, help='param missing', location='json')
        super(VerifyApi, self).__init__()

    def post(self):
        # print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        godin_account = GodinAccount.query.filter_by(godin_id=json_req['godin_id']).limit(1).first()
        if godin_account is not None:
            phone = godin_account.phone_num
            return get_response({'head': ErrorCode.SUCCESS, 'body': {'phone_num': phone}})
        else:
            return get_response({'head': ErrorCode.USER_NOT_EXIST})


class BusinessBuyVipWareApi(Resource):
    decorators = [http_auth.login_required]

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('godin_id', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('ware_id', type=str, required=True, help='param missing', location='json')
        super(BusinessBuyVipWareApi, self).__init__()

    def post(self):
        # print_info(action='Recevie', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
                              function=self.__class__.__name__)
        if msg != 'valid':
            return get_response(msg)
        ware_info = BusinessWare.query.filter_by(id=json_req['ware_id']).limit(1).first()
        if ware_info is None:
            # print_error(action='Response', function=self.__class__.__name__, branch='WARE_NOT_EXIST',
            #             api_version=g_api_version, imei=json_req['imei'])
            return get_response({'head': ErrorCode.WARE_NOT_EXIST})
        user = UserInfo.query.filter_by(godin_id=json_req['godin_id']).limit(1).first()
        vip_member = BusinessMembers.query.filter_by(godin_id=json_req['godin_id']).limit(1).first()
        if vip_member is None:
            vip_member = BusinessMembers()
            vip_member.godin_id = json_req['godin_id']
            vip_member.status = 0
            if user is not None:
                vip_member.channel = user.device_info.market
            db.session.add(vip_member)
            db.session.commit()

        ware_order = BusinessWareOrder.query.filter_by(buyer_godin_id=json_req['godin_id'],
                                                       ware_id=json_req['ware_id'], status=0).limit(1).first()

        # if ware_info.category == 0:
        #     added_month = 1
        # elif ware_info.category == 1:
        #     added_month = 3
        # elif ware_info.category == 2:
        #     added_month = 6
        # elif ware_info.category == 3:
        #     added_month = 12
        # else:
        #     added_month = 1
        # 用户没有未支付的订单
        if ware_order is None:
            ware_order = BusinessWareOrder()
            old_order = BusinessWareOrder.query.filter_by(buyer_godin_id=json_req['godin_id'], status=1). \
                order_by(BusinessWareOrder.pay_time.desc()).limit(1).first()
            if old_order is not None:
                # 最后一个付款订单结束的时间的下一秒
                if old_order.end_time < datetime.datetime.now():
                    if vip_member.valid_time <= datetime.datetime.now():
                        ware_order.start_time = datetime.datetime.now()
                    else:
                        ware_order.start_time = vip_member.valid_time
                else:
                    if vip_member.valid_time > old_order.end_time:
                        ware_order.start_time = vip_member.valid_time + datetime.timedelta(seconds=1)
                    else:
                        ware_order.start_time = old_order.end_time + datetime.timedelta(seconds=1)
            else:
                if vip_member.valid_time is None:
                    ware_order.start_time = datetime.datetime.now()
                elif vip_member.valid_time <= datetime.datetime.now():
                    ware_order.start_time = datetime.datetime.now()
                else:
                    ware_order.start_time = vip_member.valid_time
            ware_order.order_number = gen_business_vip_order_num()
            ware_order.buyer_godin_id = json_req['godin_id']
            ware_order.ware_id = json_req['ware_id']
            ware_order.ware_price = ware_info.price
            ware_order.discount = ware_info.discount
            # ware_order.discount_price = ware_info.price * ware_info.discount
            discount_price = ware_info.price * ware_info.discount
            # 客户下单时会将小数位截掉，在截掉小数位的整数上进行加1 确保客户付的钱一定是富裕的
            if isinstance(discount_price, float):
                discount_price = int(str(discount_price).split('.')[0]) + 1
            ware_order.discount_price = discount_price

            # 获取key_record_id
            user_key_record = UserKeyRecord.query.filter_by(imei=json_req['imei'], status=1). \
                order_by(UserKeyRecord.activate_time.desc()).limit(1).first()
            if user_key_record is not None:
                key = Key.query.filter_by(id=user_key_record.key_id).limit(1).first()
                if key is not None:
                    ware_order.key_record_id = key.key_record_id
            # ware_order.end_time = add_month(ware_order.start_time, added_month)
            vip_type = BusinessType.query.filter_by(number=ware_info.category).limit(1).first()
            if vip_type is not None:
                ware_order.end_time = ware_order.start_time + datetime.timedelta(days=vip_type.days)
            # status 0 表示订单未支付
            ware_order.status = 0
            try:
                db.session.add(ware_order)
                db.session.commit()
            except Exception as e:
                print_error(action='Response', function=self.__class__.__name__, branch='INTERNAL_ERROR',
                            api_version=g_api_version, imei=json_req['imei'], data=e)
                db.session.rollback()
                return get_response({'head': ErrorCode.INTERNAL_ERROR})
        elif ware_order.ware_price != ware_info.price or ware_order.discount != ware_info.discount or \
                (ware_order.create_time + datetime.timedelta(minutes=15) < datetime.datetime.now()):
            db.session.delete(ware_order)
            db.session.commit()
            # print_info(action='Response', function=self.__class__.__name__, branch='ORDER_EXPIRED',
            #            api_version=g_api_version, imei=json_req['imei'])
            return get_response({'head': ErrorCode.ORDER_EXPIRED})
        try:
            today = datetime.datetime.today()
            expire_time = today + datetime.timedelta(minutes=30)
            res = AvatarWexinPay().unified_order(out_trade_no=ware_order.order_number,
                                                 total_fee=ware_order.discount_price,
                                                 time_start=today.strftime('%Y%m%d%H%M%S'),
                                                 time_expire=expire_time.strftime('%Y%m%d%H%M%S'),
                                                 body=ware_info.name, trade_type='APP')
            # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS', api_version=g_api_version,
            #            imei=json_req['imei'])
            res['order_number'] = ware_order.order_number
            res['price'] = ware_order.discount_price
            return get_response({'head': ErrorCode.SUCCESS, 'body': res})
        except Exception as e:
            db.session.delete(ware_order)
            db.session.commit()
            print_error(action='Response', function=self.__class__.__name__, branch='ORDER_INVALID',
                        api_version=g_api_version, imei=json_req['imei'], data=e)
            return get_response({'head': ErrorCode.ORDER_INVALID})


class GetBusinessVipStatusApi(Resource):
    # decorators = [http_auth.login_required]

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('godin_id', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('status', type=int, required=True, help='param missing', location='json')
        super(GetBusinessVipStatusApi, self).__init__()

    def post(self):
        # print_info(action='Recevie', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
                              function=self.__class__.__name__)
        if msg != 'valid':
            return get_response(msg)

        vip_member = BusinessMembers.query.filter_by(godin_id=json_req['godin_id']).filter_by(status=1).limit(1).first()
        if vip_member is None:
            # print_info(action='Response', function=self.__class__.__name__, branch='USER_NOT_VIP',
            #            api_version=g_api_version, imei=json_req['imei'])
            if json_req['status'] == 1:
                recommend = dict()
                recommend_status = 0
                info = BusinessRecommend.query.limit(1).first()
                if info is not None:
                    ware_info = BusinessWare.query.filter(BusinessWare.id == info.ware_id).limit(1).first()
                    if ware_info is not None:
                        recommend_status = 1
                        recommend['ware_id'] = info.ware_id
                        if info.picture == '':
                            recommend['icon'] = ''
                        else:
                            recommend['icon'] = current_app.config['FILE_SERVER'] + info.picture
                        recommend['ware_name'] = ware_info.name
                return get_response({'head': ErrorCode.USER_NOT_VIP, 'body': {
                    'remain_days': -1,
                    'valid_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'recommend_status': recommend_status,
                    'recommend': recommend
                }})
            return get_response({'head': ErrorCode.USER_NOT_VIP})
        else:
            # 异常处理分支，当前数据库中未发现此类数据
            if not vip_member.valid_time:
                # print_info(action='Response', function=self.__class__.__name__, branch='USER_NOT_VIP',
                #            api_version=g_api_version, imei=json_req['imei'])
                if json_req['status'] == 1:
                    recommend = dict()
                    recommend_status = 0
                    info = BusinessRecommend.query.limit(1).first()
                    if info is not None:
                        ware_info = BusinessWare.query.filter(BusinessWare.id == info.ware_id).limit(1).first()
                        if ware_info is not None:
                            recommend_status = 1
                            recommend['ware_id'] = info.ware_id
                            if info.picture == '':
                                recommend['icon'] = ''
                            else:
                                recommend['icon'] = current_app.config['FILE_SERVER'] + info.picture
                            recommend['ware_name'] = ware_info.name
                    return get_response({'head': ErrorCode.USER_NOT_VIP, 'body': {
                        'remain_days': -1,
                        'valid_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'recommend_status': recommend_status,
                        'recommend': recommend
                    }})
                return get_response({'head': ErrorCode.USER_NOT_VIP})
            else:
                if vip_member.valid_time < datetime.datetime.now() and vip_member.status == 1:
                    vip_member.status = 0
                    db.session.add(vip_member)
                    db.session.commit()
                # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS',
                #            api_version=g_api_version, imei=json_req['imei'])

                # VIP过期，返回VIP过期，不再返回过期时间为负数的情况
                if json_req['status'] == 0 and vip_member.status == 0:
                    return get_response({'head': ErrorCode.USER_NOT_VIP})

                # VIP 过期后，需要重新给予图标
                if json_req['status'] == 1 and vip_member.status == 0:
                    recommend = dict()
                    recommend_status = 0
                    info = BusinessRecommend.query.limit(1).first()
                    if info is not None:
                        ware_info = BusinessWare.query.filter(BusinessWare.id == info.ware_id).limit(1).first()
                        if ware_info is not None:
                            recommend_status = 1
                            recommend['ware_id'] = info.ware_id
                            if info.picture == '':
                                recommend['icon'] = ''
                            else:
                                recommend['icon'] = current_app.config['FILE_SERVER'] + info.picture
                            recommend['ware_name'] = ware_info.name
                    return get_response({'head': ErrorCode.USER_NOT_VIP, 'body': {
                        'remain_days': -1,
                        'valid_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'recommend_status': recommend_status,
                        'recommend': recommend
                    }})

                recommend = dict()
                recommend_status = 0
                if json_req['status'] == 1:
                    info = BusinessRecommend.query.first()
                    if info is not None and (vip_member.valid_time - datetime.datetime.today()).days <= info.tip_time:
                        ware_info = BusinessWare.query.filter(BusinessWare.id == info.ware_id).limit(1).first()
                        if ware_info is not None:
                            recommend_status = 1
                            recommend['ware_id'] = info.ware_id
                            if info.picture == '':
                                recommend['icon'] = ''
                            else:
                                recommend['icon'] = current_app.config['FILE_SERVER'] + info.picture
                            recommend['ware_name'] = ware_info.name
                    return get_response({'head': ErrorCode.SUCCESS, 'body': {
                        'remain_days': (vip_member.valid_time - datetime.datetime.today()).days,
                        'valid_time': vip_member.valid_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'recommend_status': recommend_status,
                        'recommend': recommend
                    }})
                else:
                    return get_response({'head': ErrorCode.SUCCESS, 'body': {
                        'remain_days': (vip_member.valid_time - datetime.datetime.today()).days,
                        'valid_time': vip_member.valid_time.strftime('%Y-%m-%d %H:%M:%S'),
                    }})


class GetFriendApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('godin_id', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('number', type=int, required=True, help='param missing', location='json')
        self.req_parse.add_argument('id', type=str, required=True, help='param missing', location='json')
        super(GetFriendApi, self).__init__()

    def post(self):
        # print_info(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))

        d_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '0:00', '%Y-%m-%d%H:%M')
        d_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '0:03', '%Y-%m-%d%H:%M')

        n_time = datetime.datetime.now()

        if n_time >= d_time and n_time <= d_time1:
            return get_response({'head': ErrorCode.INTERNAL_ERROR})

        number = json_req['number']
        imei_list = get_imei(json_req['imei'])
        for imei in imei_list:
            msg = validate_client(imei=imei, app_version=json_req['app_version'],
                                  function=self.__class__.__name__)
            if msg != 'valid':
                return get_response(msg)
        godin_account = GodinAccount.query.filter_by(godin_id=json_req['godin_id']).limit(1).first()
        if godin_account is None:
            return get_response({'head': ErrorCode.USER_NOT_EXIST})
        # else:
        #     return get_response({'head': ErrorCode.INTERNAL_ERROR})


        we_ids = []
        # 查看是否需要返回秒通过好友
        cur_second_count = 0
        cur_one_number = 0
        vip_member = BusinessMembers.query.filter_by(godin_id=json_req['godin_id']).limit(1).first()
        if vip_member is not None and vip_member.valid_time is not None:
            vip_days = (vip_member.valid_time - datetime.datetime.today()).days
            second_days = redis.get('second_days')
            if second_days:
                if vip_days <= int(second_days):
                    second_count = int(redis.get('second_count'))
                    if second_count:
                        cur_second_count = int(second_count)
                        if cur_second_count > number:
                            cur_second_count = number

        try:
            # 秒通过好友数据获取, 后台设置的数据控制，增加好友通过率
            if cur_second_count > 0:
                # print('cur_second_count: ', cur_second_count)
                one_lock = DataLock.query.filter_by(id=3).limit(1).first()
                if one_lock is not None:
                    last_position = one_lock.count
                    if last_position > one_lock.max_id or (
                                    one_lock.max_id - last_position < cur_second_count):
                        last_position = 1
                    business_ids = db.session.query(BusinessSecondPoolOne.id, BusinessSecondPoolOne.we_id,
                                                    BusinessSecondPoolOne.we_mark).filter(
                        BusinessSecondPoolOne.id > last_position).limit(
                        cur_second_count).all()
                    if len(business_ids) <= 0:
                        cur_second_count = 0
                    else:
                        cur_second_count = len(business_ids)
                    for we_id in business_ids:
                        if last_position < we_id.id:
                            last_position = we_id.id
                        we_ids.append({'we_id': we_id.we_id, 'we_mark': we_id.we_mark})
                    one_lock.count = last_position
                    db.session.add(one_lock)
                    db.session.commit()
            # print('second friends: ', we_ids)
            # 优先级高的好友获取, 后台文件上传的数据
            one_pool_number = number - cur_second_count
            if one_pool_number > 0:
                # print('one_pool_number: ', one_pool_number)
                one_pool_info = OnePool.query.filter(OnePool.we_id == json_req['id']).limit(1).first()
                limit = redis.get('friend_count')
                if one_pool_info and limit:
                    limit = json.loads(limit)
                    one_lock = DataLock.query.filter_by(id=1).limit(1).first()
                    # print('limit count and one_lock count: ', limit['add_count'], one_lock.count)
                    if one_lock is not None:
                        if one_lock.count < int(limit['add_count']):
                            # 记录总操作数
                            one_lock.count += 1
                            db.session.add(one_lock)
                            db.session.commit()
                            by_users = redis.get('by_add_user')

                            if by_users:
                                if one_pool_number >= int(limit['capita_add']):
                                    one_pool_number = int(limit['capita_add'])
                                    cur_one_number = one_pool_number
                                else:
                                    cur_one_number = number

                                # print(json.loads(str(by_users, encoding='utf-8')))
                                vals = random.sample(json.loads(str(by_users, encoding='utf-8')), cur_one_number)
                                if len(vals) > 0:
                                    cur_one_number = len(vals)
                                else:
                                    cur_one_number = 0
                                # print('one pool friends: ', vals)
                                for val in vals:
                                    cur_val = val.split('@')
                                    we_ids.append({'we_id': cur_val[0], 'we_mark': cur_val[1]})
                                db.session.delete(one_pool_info)
                                db.session.commit()
            # print('cur_one_number: ', cur_one_number)
            # 从大池子里获取好友, 优先级最高
            business_pool_number = number - cur_one_number - cur_second_count
            if business_pool_number > 0:
                # print('business_pool_number: ', business_pool_number)
                one_lock = DataLock.query.filter_by(id=2).limit(1).first()
                if one_lock is not None:
                    last_position = one_lock.count
                    if last_position > one_lock.max_id or (
                                    one_lock.max_id - last_position < business_pool_number):
                        last_position = 1
                    # print('last_position: ', last_position)
                    business_ids = db.session.query(BusinessPoolOne.id, BusinessPoolOne.we_id, BusinessPoolOne.we_mark).filter(
                        BusinessPoolOne.id > last_position).limit(
                        business_pool_number).all()
                    for we_id in business_ids:
                        # print('business_pool: ', we_id.we_id)
                        if last_position < we_id.id:
                            last_position = we_id.id
                        we_ids.append({'we_id': we_id.we_id, 'we_mark': we_id.we_mark})
                    one_lock.count = last_position
                    db.session.add(one_lock)
                    db.session.commit()
            # 添加到好友记录
            for we_id in we_ids:
                friend = FriendHistory()
                friend.active_we_id = json_req['id']
                friend.passive_we_id = we_id['we_id']
                friend.passive_mark = we_id['we_mark']
                db.session.add(friend)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            print_error(action='Response', function=self.__class__.__name__, branch='INTERNAL_ERROR',
                        api_version=g_api_version, imei=str(json_req['imei']), data=e)
            return get_response({'head': ErrorCode.INTERNAL_ERROR})

        # try:
        #     db.session.commit()
        # except Exception as e:
        #     # db.session.rollback()
        #     print_error(action='Response', function=self.__class__.__name__, branch='INTERNAL_ERROR',
        #                 api_version=g_api_version, imei=str(json_req['imei']), data=e)
        #     return get_response({'head': ErrorCode.INTERNAL_ERROR})

        # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS',
        #            api_version=g_api_version, imei=str(json_req['imei']))
        # print(we_ids)
        return get_response({'head': ErrorCode.SUCCESS, 'body': {'ids': we_ids}})


class GetOpenAdsInfoApi(Resource):
    """
    The api of getting open screen ads information, this api supports only post method
    param imei: device unique id, imei on android
    param app_version: version of app
    param channel: app channel
    """

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('channel', type=str, required=True, help='param missing', location='json')
        super(GetOpenAdsInfoApi, self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()

        # msg = validate_client_no_imei(imei=json_req['imei'], app_version=json_req['app_version'],
        #                               function=self.__class__.__name__)
        # if msg != 'valid':
        #     return msg
        key = "GetOpenAdsInfoApi_"+ json_req['app_version'] + "_" + json_req['channel'] + datetime.datetime.now().strftime('%Y-%m-%d-%H')
        isRelease = False
        if json_req['imei'] not in get_white_imei_list():
            isRelease = True
            c_data = cache.get(key)
            if c_data:
                return c_data
        version = 0
        ver_query = AppVersion.query.filter_by(app_type=4)
        if isRelease:
            ver_query = ver_query.filter_by(is_released=True)
        version_info = ver_query.order_by(AppVersion.id.desc()).limit(1).first()
        if version_info is not None:
            if version_info.version_name == json_req['app_version']:
                version = 1

        refresh_count = 0
        current_time = datetime.datetime.now()
        r_time = str(current_time.year) + '-' + str(current_time.month) + '-' + str(current_time.day) + " "
        refresh_time = r_time + '00:00~' + r_time + '00:00'

        res = []

        ads_info = OpenScreenAds.query.join(OpenConfig, OpenConfig.ad_id == OpenScreenAds.id).filter(
            OpenScreenAds.status == 1, OpenConfig.status == 1, OpenConfig.channel == json_req['channel'],
            OpenConfig.version == version).all()
        for info in ads_info:
            icon = ''

            if info.icon != '':
                icon = current_app.config['FILE_SERVER'] + info.icon

            res.append({'ad_id': info.id, 'name': info.name, 'position': info.position, 'source': info.source,
                        'start_time': info.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'ad_number': info.number,
                        'virtual_status': 0,
                        'sort': info.unit_price,
                        'app_link': info.app_link,
                        'refresh_count': refresh_count,
                        'refresh_time': refresh_time,
                        'end_time': info.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'display_number': info.display_number,
                        'skip_time': info.skip_time, 'icon': icon,
                        'skip_count': info.skip_count})

        if not res:
            c_data = {"head": ErrorCode.SUCCESS}
            if isRelease:
                cache.set(key, c_data, timeout=60*5)
            return c_data
        else:
            c_data = {"head": ErrorCode.SUCCESS, "body": res}
            if isRelease:
                cache.set(key, c_data, timeout=60 * 5)
            return c_data


class GetOpenAdsStatisticsApi(Resource):
    """
    The api of statistical open screen show or click or real count, this api supports only post method
    param imei: device unique id, imei on android
    param app_version: version of app
    param ad_id: id of open screen ads
    param type: open screen ads  operation   0 show  1 click, 2 real
    """

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('ad_info', type=list, required=True, help='param missing', location='json')

        super(GetOpenAdsStatisticsApi, self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()

        if not check_imei(json_req['imei']):
            return get_response("valid")

        for info in json_req['ad_info']:
            if 'ad_id' not in info or 'type' not in info:
                return get_response({'head': ErrorCode.JSON_FORMAT_INVALID}), 400
            if info['type'] >= 3:
                continue

            value = str({"ad_id": info['ad_id'], "operation": info['type'], "imei": json_req['imei'],
                         "record_time": datetime.date.today()})
            redis.lpush("GetOpenAdsStatistics", value)

        return {'head': ErrorCode.SUCCESS, 'body': {'status': 0}}

        # ad_id = []
        # for info in json_req['ad_info']:
        #     if 'ad_id' not in info or 'type' not in info:
        #         # print_error(action='Response', function=self.__class__.__name__, branch='JSON_FORMAT_INVALID',
        #         #             api_version=g_api_version, imei=json_req['imei'])
        #         return {'head': ErrorCode.JSON_FORMAT_INVALID}, 400
        #     ad_id.append(info['ad_id'])
        # ad_id = set(ad_id)
        # infos = OpenScreenAds.query.filter(OpenScreenAds.id.in_(ad_id)).all()
        # if len(infos) <= 0:
        #     # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS0',
        #     #            api_version=g_api_version, imei=json_req['imei'])
        #     return {'head': ErrorCode.SUCCESS, 'body': {'status': 1}}
        #
        # res = []
        # for info in infos:
        #     simulate_info = OpenScreenSimulateData.query.filter_by(ad_id=info.id,
        #                                                            record_time=datetime.date.today()).order_by(OpenScreenSimulateData.id.desc()).limit(1).first()
        #     for ad in json_req['ad_info']:
        #         temp_type = -1
        #         if ad['ad_id'] == info.id:
        #             temp_type = ad['type']
        #
        #         if temp_type == -1 or temp_type >= 3:
        #             continue
        #
        #         open_ads = OpenScreenAdsStatistics.query.filter_by(ad_id=info.id, operation=temp_type,
        #                                                            imei=json_req['imei'],
        #                                                            record_time=datetime.date.today()
        #                                                            ).limit(1).first()
        #         if simulate_info is not None and temp_type == 1:
        #             simulate_info.actual_control_times += 1
        #         if open_ads is None:
        #             open_ads = OpenScreenAdsStatistics()
        #             open_ads.ad_id = info.id
        #             open_ads.imei = json_req['imei']
        #             open_ads.operation = temp_type
        #             open_ads.count = 1
        #             open_ads.record_time = datetime.date.today()
        #             db.session.add(open_ads)
        #         else:
        #             open_ads.count += 1
        #             db.session.add(open_ads)
        #     if simulate_info is not None:
        #         if simulate_info.actual_control_times > simulate_info.control_times or info.virtual_skip == 0:
        #             res.append({'ad_id': info.id, 'virtual_status': 0})
        #         else:
        #             res.append({'ad_id': info.id, 'virtual_status': 1})
        #     else:
        #         res.append({'ad_id': info.id, 'virtual_status': 0})
        #     if simulate_info is not None:
        #         db.session.add(simulate_info)
        #
        # try:
        #     db.session.commit()
        # except Exception as e:
        #     db.session.rollback()
        #     print_error(action='Response', function=self.__class__.__name__, branch='INTERNAL_ERROR',
        #                 api_version=g_api_version, imei=json_req['imei'], data=e)
        #     return {'head': ErrorCode.INTERNAL_ERROR}
        # #print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS', api_version=g_api_version,
        # #           imei=json_req['imei'])
        # if len(ad_id) != len(infos):
        #     return {'head': ErrorCode.SUCCESS, 'body': {'status': 1, 'ad_info': res}}
        # else:
        #     return {'head': ErrorCode.SUCCESS, 'body': {'status': 0, 'ad_info': res}}


class FreeBusinessVipMemberApi(Resource):
    # decorators = [http_auth.login_required]

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('godin_id', type=str, required=True, help='param missing', location='json')
        super(FreeBusinessVipMemberApi, self).__init__()

    def post(self):
        # print_info(action='Recevie', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #           api_version=g_api_version, data=str(json_req))
        msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
                              function=self.__class__.__name__)
        if msg != 'valid':
            return get_response(msg)
        user = UserInfo.query.filter_by(godin_id=json_req['godin_id']).limit(1).first()
        if user is None:
            print_info(action='Response', function=self.__class__.__name__, branch='USER_NOT_EXIST',
                       api_version=g_api_version, imei=json_req['imei'])
            return get_response({'head': ErrorCode.USER_NOT_EXIST})
        vip_member = BusinessMembers.query.filter_by(godin_id=json_req['godin_id']).limit(1).first()
        days = redis.get('free_vip_days')
        if vip_member is None and days and int(days) > 0:
            current_time = datetime.datetime.now()
            vip_member = BusinessMembers()
            vip_member.godin_id = json_req['godin_id']
            vip_member.status = 1
            vip_member.create_time = current_time
            vip_member.first_pay_time = current_time
            vip_member.valid_time = current_time + datetime.timedelta(days=int(days))
            free_statistics = BusinessGiveStatistics()
            free_statistics.godin_id = user.godin_id
            free_statistics.phone_num = user.godin_account.phone_num
            free_statistics.days = int(days)

            try:
                db.session.add(free_statistics)
                db.session.add(vip_member)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print_error(action='Response', function=self.__class__.__name__, branch='INTERNAL_ERROR',
                            api_version=g_api_version, imei=json_req['imei'], data=e)
                return get_response({'head': ErrorCode.INTERNAL_ERROR})
        return get_response({'head': ErrorCode.SUCCESS})


class BusAssistantApi(Resource):
    # decorators = [http_auth.login_required]

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        super(BusAssistantApi, self).__init__()

    def post(self):

        json_req = self.req_parse.parse_args()

        # msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
        #                       function=self.__class__.__name__)
        # if msg != 'valid':
        #     return get_response(msg)
        bus_assistant = redis.get('bus_assistant')
        if bus_assistant is not None:
            bus_assistant = eval(str(bus_assistant, encoding='utf-8'))
            we_id = bus_assistant.get('we_id', '')
            we_customer_service = bus_assistant.get('we_customer_service', '')
            we_public = bus_assistant.get('we_public', '')
            link = bus_assistant.get('link', '')
        else:
            we_id = ''
            we_public = ''
            we_customer_service = ''
            link = ''
        # print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS',
        #            api_version=g_api_version, imei=json_req['imei'])
        return get_response({'head': ErrorCode.SUCCESS, 'body': {'we_id': we_id, 'we_customer_service': we_customer_service,
                                                                 'we_public': we_public, 'link': link}})


class BusLinkApi(Resource):
    # decorators = [http_auth.login_required]

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        super(BusLinkApi, self).__init__()

    def post(self):
        #print_info(action='Recevie', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        #print_log(action='Parameter', function=self.__class__.__name__, branch='parameter',
        #          api_version=g_api_version, data=str(json_req))
        msg = validate_client(imei=json_req['imei'], app_version=json_req['app_version'],
                              function=self.__class__.__name__)
        if msg != 'valid':
            return get_response(msg)
        bus_link = redis.get('bus_link')
        if bus_link is not None:
            bus_link = str(bus_link, encoding='utf-8')
            link = bus_link
        else:
            link = ''
        #print_info(action='Response', function=self.__class__.__name__, branch='SUCCESS',
        #           api_version=g_api_version, imei=json_req['imei'])
        return get_response({'head': ErrorCode.SUCCESS, 'body': {'link': link}})


class HealthCheckApi(Resource):
    def get(self):
        return get_response({'head': ErrorCode.SUCCESS})


class VSZLAddApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('wx', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        super(VSZLAddApi, self).__init__()

    def post(self):
        # 将当前用户绑定给客服
        json_req = self.req_parse.parse_args()
        service_wx = ""
        nickname = ""
        we_public = ""
        link = ""
        bus_gzh = redis.get('bus_gzh')
        if bus_gzh is not None:
            bus_gzh = eval(str(bus_gzh, encoding='utf-8'))
            we_public = bus_gzh.get('we_public', '')
            link = bus_gzh.get('link', '')

        data = VSZL_Customer_Service.query.filter_by(customer_wx=json_req["wx"]).limit(1).first()
        if data:
            cur_ser = VSZL_Service.query.filter_by(service_wx=data.service_wx).limit(1).first()
            service_wx = cur_ser.service_wx
            nickname = cur_ser.nickname
            return get_response({'head': ErrorCode.USER_ALREADY_EXIST, 'body': {'service_wx': service_wx,
                                                                                'nickname': nickname,
                                                                                "we_public": we_public, "link": link}})

        all_user = VSZL_Service.query.filter_by().all()

        for user in all_user:
            if user.person_num_limit > user.current_person_num:
                vszl_cus_ser = VSZL_Customer_Service()
                vszl_cus_ser.service_wx = user.service_wx
                vszl_cus_ser.customer_wx = json_req["wx"]
                db.session.add(vszl_cus_ser)

                user.current_person_num += 1
                db.session.add(user)
                db.session.commit()
                service_wx = user.service_wx
                nickname = user.nickname
                break
        else:
            # 将Customer_Service中的current_person_num全部清零
            for index, user in enumerate(all_user):
                user.current_person_num = 0
                db.session.add(user)
                db.session.commit()

                if index == 0:
                    vszl_cus_ser = VSZL_Customer_Service()
                    vszl_cus_ser.service_wx = user.service_wx
                    vszl_cus_ser.customer_wx = json_req["wx"]
                    db.session.add(vszl_cus_ser)

                    user.current_person_num += 1
                    db.session.add(user)
                    db.session.commit()
                    service_wx = user.service_wx
                    nickname = user.nickname

        return get_response({'head': ErrorCode.SUCCESS, 'body': {'service_wx': service_wx,
                                                                 'nickname': nickname, "we_public": we_public, "link": link}})


class VSZLSearchApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('wx', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        super(VSZLSearchApi, self).__init__()

    def post(self):
        # 查询当前用户是否被客服绑定
        json_req = self.req_parse.parse_args()
        record = VSZL_Customer_Service.query.filter_by(customer_wx=json_req["wx"]).limit(1).first()
        return get_response({'head': ErrorCode.ALREADY_BIND}) if record else get_response({'head': ErrorCode.NO_BIND})


class ExperienceStatusApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('godin_id', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        super(ExperienceStatusApi, self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()
        record = Free_Experience_Days.query.filter_by(godin_id=json_req["godin_id"]).limit(1).first()
        if record:
            if record.is_exper == 0:
                return get_response({'head': ErrorCode.SUCCESS})
            elif record.valid_time < datetime.datetime.now():
                record.is_exper = 0
                db.session.add(record)
                db.session.commit()
                return get_response({'head': ErrorCode.SUCCESS})
            else:
                return get_response({'head': ErrorCode.ALREADY_EXPER})

        else:
            free_days = cache.get('free_experience_days')
            if not free_days:
                key_value = db.session.query(KeyValue).filter_by(key="free_experience_days").limit(1).first()
                if not key_value:
                    raise Exception("未设置免费体验周期！！！")
                free_days = key_value.value
                cache.set('free_experience_days', free_days, timeout=12 * 60 * 60)
            current_time = datetime.datetime.now()
            free_days = Free_Experience_Days(
                godin_id=json_req["godin_id"],
                first_time=current_time,
                valid_time=current_time + datetime.timedelta(days=int(free_days))
            )
            db.session.add(free_days)
            db.session.commit()
            return get_response({'head': ErrorCode.SUCCESS})


class FreeExperienceApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('godin_id', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        super(FreeExperienceApi, self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()
        record = Free_Experience_Days.query.filter_by(godin_id=json_req["godin_id"]).limit(1).first()
        free_days = cache.get('free_experience_days')
        if not free_days:
            key_value = db.session.query(KeyValue).filter_by(key="free_experience_days").limit(1).first()
            free_days = key_value.value
            cache.set('free_experience_days', free_days, timeout=12 * 60 * 60)
        current_time = datetime.datetime.now()
        record.first_time = current_time
        record.valid_time = current_time + datetime.timedelta(days=int(free_days))
        record.is_exper = 1
        record.exper_count += 1
        db.session.add(record)
        db.session.commit()
        return get_response({'head': ErrorCode.SUCCESS})


class GetTriangleApi(Resource):

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        super(GetTriangleApi, self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()
        set_fun = redis.get('set_fun')
        if set_fun is None:
            redis.set('set_fun', "goumaivip,keduoduo,weiketang,weishangzhuli")
            set_fun = redis.get('set_fun')
        set_fun = str(set_fun, encoding='utf-8')
        return get_response({'head': ErrorCode.SUCCESS, 'body': {'set_fun': set_fun}})


class GetFunctionVideoApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('video_name', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        super(GetFunctionVideoApi, self).__init__()

    def post(self):
        # 获取功能视频的url
        json_req = self.req_parse.parse_args()
        record = FunctionVideo.query.filter_by(function_name=json_req["video_name"]).limit(1).first()
        if record:
            link = current_app.config['FILE_SERVER'] + current_app.config["UPLOAD_VIDEO_PATH"] + record.video_url
            return get_response({'head': ErrorCode.SUCCESS, 'body': {"link": link}})
        return get_response({'head': ErrorCode.RESOURCE_NOT_FOUND})


class GetMicroStoreUrlApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        super(GetMicroStoreUrlApi,self).__init__()

    def post(self):
        # 获取微店铺链接地址
        self.req_parse.parse_args()
        link = cache.get('micro_store_url')
        if not link:
            key_value = db.session.query(KeyValue).filter_by(key="micro_store_url").limit(1).first()
            if key_value:
                link = key_value.value
                cache.set('micro_store_url', link, timeout=12 * 60 * 60)
        return get_response({'head': ErrorCode.SUCCESS, 'body': {'link': link}})


class GetInviteLinkApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('godin_id', type=str, required=True, help='param missing', location='json')
        super(GetInviteLinkApi,self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()
        user = UserGeneralize.query.filter_by(godin_id=json_req["godin_id"]).limit(1).first()
        domain_name = current_app.config["INVITE_LINK"]
        if user:
            return get_response({'head': ErrorCode.SUCCESS,
                                 'body': {"link": domain_name + user.invite_link,
                                          "invite_person_num": user.register_person_num,
                                          "pay_person_num": user.pay_person_num,
                                          "account_award": user.member_award + user.active_code_award
                                          }
                                 })
        else:
            user_info = GodinAccount.query.filter_by(godin_id=json_req["godin_id"]).limit(1).first()
            if user_info:
                user = UserGeneralize(json_req["godin_id"])
                user.phone_num = user_info.phone_num
                user.register_person_num = 0
                user.invite_person_num = 0
                user.pay_person_num = 0
                user.member_award = 0
                user.active_code_award = 0
                user.account_balance = 0
                db.session.add(user)
                db.session.commit()
            else:
                return get_response({'head': ErrorCode.USER_NOT_EXIST})

        return get_response({'head': ErrorCode.SUCCESS,
                             'body': {"link": domain_name + user.invite_link, "invite_person_num": 0,
                                      "pay_person_num": 0, "account_award": 0
                                      }
                             })


class BiFinishNoticeApi(Resource):
    """
    The api of receiving notice from bigdata server, then read analysis data from transfer database,
    this api supports only post method
    param date: request date
    """

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('uid', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('date', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('status', type=str, required=True, help='param missing', location='json')
        super(BiFinishNoticeApi, self).__init__()

    def post(self):
        # print_log(action='Receive', function=self.__class__.__name__, branch='begin', api_version=g_api_version)
        json_req = self.req_parse.parse_args()
        # print(json_req)
        status = json_req['status']
        res = []
        md = hashlib.md5()
        md.update(bytes(json_req['date'] + 'godin', 'utf-8'))
        if md.hexdigest() != json_req['uid']:
            return get_response({'head': ErrorCode.JSON_FORMAT_INVALID})

        try:
            new_date = datetime.datetime.strptime(json_req['date'], '%Y%m%d').date() - datetime.timedelta(days=1)
            if status == '0001':
                read_report_d.delay(target_date=new_date.strftime('%Y%m%d'))
            elif status == '0002':
                read_report_m.delay(target_date=new_date.strftime('%Y%m%d'))

            return {'head': ErrorCode.SUCCESS}
        except Exception as e:
            print('BiFinishNotice: ', e)
            return {'head': ErrorCode.JSON_FORMAT_INVALID}


class GetEveryWashUrlApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        super(GetEveryWashUrlApi,self).__init__()

    def post(self):
        # 获取微店铺链接地址
        self.req_parse.parse_args()
        link = cache.get('every_wash')
        if not link:
            key_value = db.session.query(KeyValue).filter_by(key="every_wash").limit(1).first()
            link = key_value.value
            cache.set('every_wash', link, timeout=12 * 60 * 60)
        return get_response({'head': ErrorCode.SUCCESS, 'body': {'link': link}})


class CheckIMEIApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=list, required=True, help='param missing', location='json')
        super(CheckIMEIApi,self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()
        # 检测imei是否是新用户
        imei_list = get_imei(json_req['imei'])
        user_record = UserKeyRecord.query.filter(UserKeyRecord.imei.in_(imei_list)).limit(1).first()
        if user_record:
            return get_response({'head': ErrorCode.IMEI_NOT_NEW})
        return get_response({'head': ErrorCode.SUCCESS})


class FreeTrialApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=list, required=True, help='param missing', location='json')
        super(FreeTrialApi,self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()
        imei_list = get_imei(json_req['imei'])

        user_record = UserKeyRecord.query.filter(UserKeyRecord.imei.in_(imei_list)).limit(1).first()
        if user_record:
            return get_response({'head': ErrorCode.IMEI_NOT_NEW})

        # 将免费试用一天的批次创建key的数量自增1
        key_record = KeyRecord.query.filter_by(id="00000000000001").limit(1).first()
        key_id = create_key()
        key = Key()
        key.id = key_id
        key.key_record_id = "00000000000001"
        key.status = 1
        key_record.count += 1
        db.session.add(key_record)
        db.session.add(key)
        # 先提交防止外键无效
        db.session.commit()

        for imei in imei_list:
            user_record = UserKeyRecord()
            user_record.key_id = key_id
            user_record.imei = imei
            user_record.activate_time = datetime.datetime.now()
            user_record.status = 1
            db.session.add(user_record)
        db.session.commit()
        return get_response({'head': ErrorCode.SUCCESS})


class GetHotDotApi(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('app_version', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('imei', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('type', type=int, required=True, help='param missing', location='json')
        super(GetHotDotApi,self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()
        all_data = FunctionHotDot.query.filter_by(type=json_req["type"]).all()
        data = []
        for item in all_data:
            if item.today_status == 1:
                data.append(str(item.id))
        return get_response({'head': ErrorCode.SUCCESS, "body": ",".join(data)})


class UploadVoiceApi(Resource):

    def post(self):
        basedir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
        file_dir = os.path.join(basedir, "share/static/images/voice")
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        f = request.files['voice_name']  # 从表单的file字段获取文件，voice_name为该表单的name值
        fname = secure_filename(f.filename)
        ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
        unix_time = int(time.time())
        filename = str(unix_time) + '.' + ext  # 修改上传的文件名
        f.save(os.path.join(file_dir, filename))  # 保存文件到目录

        input_path = os.path.join(file_dir, filename)
        new_filename = str(unix_time) + '.mp3'
        output_path = os.path.join(file_dir, new_filename)
        ff = FFmpeg(inputs={input_path: None}, outputs={output_path: None})
        try:
            ff.run()
        except Exception:
            return get_response({'head': ErrorCode.FILE_FORMAT_ERROR})
        finally:
            # 删除之前的.amr文件
            basedir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
            file_dir = os.path.join(basedir, "share/static/images/voice", filename)
            os.remove(file_dir)

        upload_voice = UploadVoice()
        upload_voice.voice_name = new_filename
        db.session.add(upload_voice)
        db.session.commit()

        return get_response({'head': ErrorCode.SUCCESS, "body": {
            "url": current_app.config['FILE_SERVER'] + "vssq/share/voice?voice_name=" + str(new_filename)}})

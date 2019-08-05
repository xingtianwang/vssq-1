#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: errors.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 16/10/9
# *************************************************************************


class ErrorCode(object):
    SUCCESS = {'statuscode': '000000', 'statusmsg': "success"}
    SMS_SENT = {'statuscode': '000001', 'statusmsg': "sms already sent"}
    SMS_INVALID = {'statuscode': '000002', 'statusmsg': "sms verify code invalid"}
    SMS_EXPIRED = {'statuscode': '000003', 'statusmsg': "sms verify code expired"}
    PHONE_NUM_INVALID = {'statuscode': '000004', 'statusmsg': "phone number invalid"}
    JSON_FORMAT_INVALID = {'statuscode': '000005', 'statusmsg': "json format invalid"}
    WHITE_LIST_UPDATED = {'statuscode': '000006', 'statusmsg': "no white list to update"}
    ALREADY_LATEST = {'statuscode': '000007', 'statusmsg': "already last version"}
    APP_NOT_EXIST = {'statuscode': '000008', 'statusmsg': "app not exists"}
    DEVICE_USER_NOT_MATCH = {'statuscode': '000009', 'statusmsg': "device and user not match"}
    PHOTO_FORMAT_INVALID = {'statuscode': '000010', 'statusmsg': "photo data not invalid"}
    CONTACT_NOT_EXIST = {'statuscode': '000011', 'statusmsg': "contact not exist"}
    REQ_MSG_EMPTY = {'statuscode': '000012', 'statusmsg': "request message body is empty"}
    IMEI_INVALID = {'statuscode': '000013', 'statusmsg': "imei invalid"}
    BLACK_IMEI = {'statuscode': '000014', 'statusmsg': "imei in black list"}
    APP_INVALID = {'statuscode': '000015', 'statusmsg': "app version is invalid"}
    INTERNAL_ERROR = {'statuscode': '000016', 'statusmsg': "internal error"}
    EXCEPTION_APP_INVALID = {'statuscode': '000017', 'statusmsg': "exception app version invalid"}
    USER_NOT_EXIST = {'statuscode': '000018', 'statusmsg': "user not exist"}
    USER_MEMBER_NOT_EXIST = {'statuscode': '000019', 'statusmsg': "member not exist"}
    WARE_NOT_EXIST = {'statuscode': '000020', 'statusmsg': "ware not exist"}
    WARE_ORDER_FAIL = {'statuscode': '000021', 'statusmsg': "ware not pay"}
    GROUP_NOT_EXIST = {'statuscode': '000022', 'statusmsg': "group not exist"}
    ACTIVITY_NOT_EXIST = {'statuscode': '000023', 'statusmsg': "activity not exist"}
    SHARE_CODE_NOT_EXIST = {'statuscode': '000024', 'statusmsg': "share code not exist"}
    CANT_NOT_FILL_IN_YOUR_SHARE_CODE = {'statuscode': '000025', 'statusmsg': "cant not fill in your share code"}
    OPEN_SCREEN_ADS_NOT_EXIST = {'statuscode': '000026', 'statusmsg': "open screen ads not exist"}
    BANNERAD_NOT_EXIST = {'statuscode': '000027', 'statusmsg': "bannerad not exist"}
    CONTROL_CHANNEL_NOT_EXIST = {'statuscode': '000028', 'statusmsg': "control channel not exist"}
    USER_NOT_VIP = {'statuscode': '000029', 'statusmsg': "user is not vip"}
    ALREADY_BUY = {'statuscode': '000030', 'statusmsg': "already buy this ware"}
    ORDER_INVALID = {'statuscode': '000031', 'statusmsg': "order invalid"}
    ORDER_EXPIRED = {'statuscode': '000032', 'statusmsg': "order expired"}
    VIP_NOT_PROTOCOL = {'statuscode': '000033', 'statusmsg': "vip not service protocol"}
    AVATAR_VERSION_NOT_EXIST = {'statuscode': '000034', 'statusmsg': "avatar version not exist"}
    AKREADY_FILL_CODE = {'statuscode': '000035', 'statusmsg': "already fill in share code"}
    KEY_INVALID = {'statuscode': '000036', 'statusmsg': "key invalid"}
    KEY_EXIST = {'statuscode': '000037', 'statusmsg': "key is exist"}
    WECHAT_PAY_FAILURE = {'statuscode': '000038', 'statusmsg': "pay failure"}
    CHANNEL_NOT_EXIST = {'statuscode': '000039', 'statusmsg': "channel speard manage not exist"}
    ENTER_PAGE = {'statuscode': '000040', 'statusmsg': "enter page"}
    RELOAD_LATER = {'statuscode': '000041', 'statusmsg': "The system is busy. Please repeat later"}
    IMEI_HAS_KEY = {'statuscode': '000042', 'statusmsg': "imei has key, can not binding new key"}
    VERSION_CODE_NOT_SUPPORTED = {'statuscode': '000043', 'statusmsg': "version code is not supported"}
    NOT_PROTOCOL = {'statuscode': '000044', 'statusmsg': "not service protocol"}
    IMEI_HAS_ID = {'statuscode': '000045', 'statusmsg': "imei has bind, can not bind new id"}
    NO_BIND = {'statuscode': '000046', 'statusmsg': "no bind"}
    ALREADY_BIND = {'statuscode': '000047', 'statusmsg': "already bind"}
    USER_ALREADY_EXIST = {'statuscode': '000048', 'statusmsg': "can not repeat add"}
    ALREADY_EXPER = {'statuscode': '000049', 'statusmsg': "already experience"}
    RESOURCE_NOT_FOUND = {'statuscode': '000048', 'statusmsg': "Resource not found"}
    URL_ERROR = {'statuscode': '000050', 'statusmsg': "url is error"}
    ALREADY_INVITED = {'statuscode': '000051', 'statusmsg': "already invited"}
    IMEI_NOT_NEW = {'statuscode': '000052', 'statusmsg': "imei is not new"}
    FILE_FORMAT_ERROR = {'statuscode': '000053', 'statusmsg': "file format error"}
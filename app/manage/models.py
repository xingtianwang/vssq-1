#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: models.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 2016/10/21
# *************************************************************************
from datetime import datetime

from app import db


class DutyManager(db.Model):
    __tablename__ = 'duty_manager'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(128), unique=True)
    on_duty = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<DutyManager %r>' % self.email


class BlackList(db.Model):
    __tablename__ = 'black_list'
    id = db.Column(db.Integer, primary_key=True)
    imei = db.Column(db.String(15), primary_key=True, index=True)
    create_time = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, imei):
        self.imei = imei

    def __repr__(self):
        return '<BlackList %r>' % self.imei


class WhiteImeiList(db.Model):
    __tablename__ = 'white_imei_list'
    id = db.Column(db.Integer, primary_key=True)
    imei = db.Column(db.String(15), primary_key=True, index=True)
    create_time = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, imei):
        self.imei = imei

    def __repr__(self):
        return '<WhiteImeiList %r>' % self.imei


class NextDayStay(db.Model):
    __tablename__ = 'next_day_stay'
    id = db.Column(db.Integer, primary_key=True)
    channel = db.Column(db.String(15))
    date = db.Column(db.Date)
    last_come_count = db.Column(db.Integer, default=0)
    stay_count = db.Column(db.Integer, default=0)
    stay_percent = db.Column(db.Float)

    __table_args__ = (db.UniqueConstraint('date', 'channel',
                                          name='uq_next_day_stay_date_channel'),)

    def __repr__(self):
        return '<NextDayStay %r>' % self.imei


class SpreadManager(db.Model):
    __tablename__ = 'spread_manager'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(128))
    channelname = db.Column(db.String(128))
    url_suffix = db.Column(db.String(128), unique=True, index=True)
    apps = db.relationship('AppVersion', backref='spreader', lazy='dynamic')
    app_channel = db.relationship('ChannelVersion', backref='channelspreader', lazy='dynamic')

    def __repr__(self):
        return '<SpreadManager %r>' % self.email


class KeyValue(db.Model):
    __tablename__ = 'key_value'
    key = db.Column(db.String(64), primary_key=True)  # 标识
    value = db.Column(db.String(255))  # 标识所对应的值

    def __repr__(self):
        return '<key_value %r>' % self.key


class FunctionVideo(db.Model):
    __tablename__ = 'function_video'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    function_name = db.Column(db.String(64), unique=True, nullable=False)  # 视频名称
    video_url = db.Column(db.String(64), unique=True, nullable=False)  # 视频 url
    comment = db.Column(db.String(128))  # 备注
    last_operator = db.Column(db.String(64), nullable=False)  # 最后操作人

    def __repr__(self):
        return '<FunctionVideo %r>' % self.id


class WithdrawCheck(db.Model):
    __tablename__ = 'withdraw_check'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    godin_id = db.Column(db.String(32), nullable=False)  # 国鼎id
    apply_time = db.Column(db.DateTime, default=datetime.now)  # 申请时间
    phone_num = db.Column(db.String(11), nullable=False)  # 手机号
    award = db.Column(db.Float(2))  # 总收益, 单位分
    account_balance = db.Column(db.Float(2))  # 余额, 单位分
    withdraw = db.Column(db.SMALLINT, nullable=False)  # 提现金额, 单位分
    zfb_account = db.Column(db.String(64), nullable=False)  # 支付宝账号
    name = db.Column(db.String(64), nullable=False)  # 姓名
    status = db.Column(db.SMALLINT, nullable=False)  # 提现状态 0 待打款 1 完成 2 驳回
    check_time = db.Column(db.DateTime)  # 审核时间
    operator = db.Column(db.String(64))  # 操作人

    def __repr__(self):
        return '<WithdrawCheck %r>' % self.id


class AlterBalance(db.Model):
    __tablename__ = 'alter_balance'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone_num = db.Column(db.String(11), nullable=False)  # 手机号
    create_time = db.Column(db.DateTime, default=datetime.now)  # 修改时间
    type = db.Column(db.SMALLINT, nullable=False)  # 修改类型 0 增加余额 1 减少余额
    amount = db.Column(db.Integer, nullable=False)  # 修改数额, 单位元
    operator = db.Column(db.String(64))  # 操作人
    comment = db.Column(db.String(255), nullable=False)  # 备注

    def __repr__(self):
        return '<AlterBalance %r>' % self.id


class MasterFunctionVideo(db.Model):
    __tablename__ = 'master_function_video'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    function_name = db.Column(db.String(64), unique=True, nullable=False)  # 视频名称
    video_url = db.Column(db.String(64), unique=True, nullable=False)  # 视频 url
    comment = db.Column(db.String(128))  # 备注
    last_operator = db.Column(db.String(64), nullable=False)  # 最后操作人

    def __repr__(self):
        return '<MasterFunctionVideo %r>' % self.id


class AlterDivide(db.Model):
    __tablename__ = 'alter_divide'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    channel_id = db.Column(db.String(6), nullable=False)  # 渠道ID
    channel_name = db.Column(db.String(32), nullable=False)  # 渠道名称
    type = db.Column(db.SMALLINT, nullable=False)  # 修改类型 0 增加分成 1 减少分成
    amount = db.Column(db.Integer, nullable=False)  # 修改数额, 单位元
    operator = db.Column(db.String(64))  # 操作人
    comment = db.Column(db.String(255), nullable=False)  # 备注
    create_time = db.Column(db.DateTime, default=datetime.now)  # 修改时间

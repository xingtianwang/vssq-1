#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: models.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 16/10/8
# *************************************************************************
import hashlib
from datetime import datetime

from flask import current_app, g
from sqlalchemy.orm import backref

from app import db
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import SignatureExpired, BadSignature


class GodinAccount(db.Model):
    __tablename__ = 'godin_account'
    id = db.Column(db.Integer, primary_key=True)
    godin_id = db.Column(db.String(32), unique=True, nullable=False)
    phone_num = db.Column(db.String(11), unique=True, nullable=False)
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)

    def __init__(self, phone_num):
        self.phone_num = phone_num
        md = hashlib.md5()
        md.update(bytes(phone_num, 'utf-8'))
        self.godin_id = md.hexdigest()

    def __repr__(self):
        return '<GodinAccount %r>' % self.godin_id


# 此活动已不用
class RegisterShareCode(db.Model):
    __tablename__ = 'register_share_code'
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    share_code_people = db.Column(db.String(32), db.ForeignKey('user_info.godin_id'), nullable=True)
    register_code_people = db.Column(db.String(32), db.ForeignKey('user_info.godin_id'), nullable=True)

    __table_args__ = (db.UniqueConstraint('activity_id', 'share_code_people', 'register_code_people',
                                          name='uq_activity_id_share_code_people_register_code_people'),)

    def __repr__(self):
        return '<RegisterShareCode %r, %r, %r>' % (self.id, self.activity_id, self.share_code_people)


class UserInfo(db.Model):
    __tablename__ = 'user_info'
    id = db.Column(db.Integer, primary_key=True)
    godin_id = db.Column(db.String(32), db.ForeignKey('godin_account.godin_id'), index=True, nullable=False)
    imei = db.Column(db.String(15), db.ForeignKey('device_info.imei'), nullable=False)
    nick_name = db.Column(db.String(128), default='')
    photo_url = db.Column(db.String(256), default='')
    photo_md5 = db.Column(db.String(32), default='')
    password_hash = db.Column(db.String(128), default='')
    godin_account = db.relationship('GodinAccount', backref=backref('user_info', uselist=False), lazy='joined')
    device_info = db.relationship('DeviceInfo', uselist=False, lazy='joined')
    share_code = db.Column(db.String(10), index=True, unique=True, nullable=False)
    activity_info = db.relationship('ActivityShareCodeCount', backref='code_count', lazy='dynamic')
    register_code = db.relationship('RegisterShareCode', foreign_keys=[RegisterShareCode.register_code_people],
                                    backref=db.backref('register', lazy='joined'),
                                    lazy='dynamic',
                                    cascade='all, delete-orphan')

    def __init__(self, godin_id, imei):
        self.godin_id = godin_id
        self.imei = imei

    def check_godinid_imei_matched(self):
        return UserInfo.query.filter_by(godin_id=self.godin_id, imei=self.imei).first() is not None

    def to_json(self):
        photo_url = ''
        if self.photo_url != '':
            photo_url = current_app.config['FILE_SERVER'] + self.photo_url
        g.current_user = self
        g.token_used = False
        json_userinfo = {
            'godin_id': self.godin_id,
            'imei': self.imei,
            'nick_name': self.nick_name,
            'photo_url': photo_url,
            'photo_md5': self.photo_md5,
            'token': g.current_user.generate_auth_token(current_app.config['TOKEN_EXPIRED_TIME']).decode('utf-8'),
            'expiration': str(current_app.config['TOKEN_EXPIRED_TIME']),
            'create_time': self.godin_account.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'share_code': self.share_code
        }
        return json_userinfo

    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id, 'imei': self.imei})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        return UserInfo.query.filter_by(id=data['id'], imei=data['imei']).first()

    def __repr__(self):
        return '<UserInfo %r>' % self.godin_id


class DeviceInfo(db.Model):
    __tablename__ = 'device_info'
    id = db.Column(db.Integer, primary_key=True)
    imei = db.Column(db.String(15), unique=True, index=True, nullable=False)
    os_version = db.Column(db.String(15), nullable=False)
    device_factory = db.Column(db.String(64), nullable=False)
    device_model = db.Column(db.String(64), nullable=False)
    app_version = db.Column(db.String(64), nullable=False)
    status = db.Column(db.Boolean, default=False, nullable=False)
    market = db.Column(db.String(24), nullable=False)
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)
    last_seen = db.Column(db.DateTime(), default=datetime.now, nullable=False)

    def ping(self):
        self.last_seen = datetime.now()
        db.session.add(self)

    def from_json(self, dev_json):
        if self.imei is None:
            print('*****new imei*****')
            self.imei = dev_json['imei']
        self.os_version = dev_json['os_version']
        self.device_factory = dev_json['device_factory']
        self.device_model = dev_json['device_model']
        self.app_version = dev_json['app_version']

    def __repr__(self):
        return '<DeviceInfo %s>' % self.imei


class UserWeekStatistics(db.Model):
    __tablename__ = 'user_week_statistics'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, default=int(datetime.now().strftime('%Y')), nullable=False)
    week = db.Column(db.Integer, default=int(datetime.now().strftime('%W')), nullable=False)
    market = db.Column(db.String(24), nullable=False)
    new_reg_count = db.Column(db.Integer, default=0)
    new_total_count = db.Column(db.Integer, default=0)

    __table_args__ = (db.UniqueConstraint('year', 'week', 'market',
                                          name='uq_user_app_week_statistics_year_week_market'), )

    def __repr__(self):
        return '<UserStatistics %r-%r-%r>' % (self.year, self.week, self.market)


class UserMonthStatistics(db.Model):
    __tablename__ = 'user_month_statistics'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, default=int(datetime.now().strftime('%Y')), nullable=False)
    month = db.Column(db.Integer, default=int(datetime.now().strftime('%m')), nullable=False)
    market = db.Column(db.String(24), nullable=False)
    new_reg_count = db.Column(db.Integer, default=0)
    new_total_count = db.Column(db.Integer, default=0)

    __table_args__ = (db.UniqueConstraint('year', 'month', 'market',
                                          name='uq_user_app_month_statistics_year_month_market'), )

    def __repr__(self):
        return '<UserMonthStatistics %r-%r-%r>' % (self.year, self.month, self.market)


class BindRecord(db.Model):
    __tablename__ = 'bind_record'
    id = db.Column(db.Integer, primary_key=True)
    godin_id = db.Column(db.String(32), nullable=False)
    imei = db.Column(db.String(15),  nullable=False)
    last_seen = db.Column(db.DateTime(), default=datetime.now, nullable=False)

    def ping(self):
        self.last_seen = datetime.now()
        db.session.add(self)

    def __repr__(self):
        return '<BindRecord %r>' % self.id


class FeedBack(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    phone_num = db.Column(db.String(11), nullable=False)  # 手机号
    imei = db.Column(db.String(15), nullable=False)
    os_version = db.Column(db.String(15), nullable=False)
    device_factory = db.Column(db.String(64), nullable=False)
    device_model = db.Column(db.String(64), nullable=False)
    app_version = db.Column(db.String(64), nullable=False)
    user_contact = db.Column(db.String(64))
    content = db.Column(db.String(512), nullable=False)
    create_time = db.Column(db.DateTime(), default=datetime.now)
    status = db.Column(db.SmallInteger, default=0)  # 0 未回复 1 已回复
    operator = db.Column(db.String(15))  # 操作人
    picture = db.Column(db.String(256), default='')  # 上传的图片地址
    back_content = db.Column(db.Text, default='')  # 回复的消息内容
    back_time = db.Column(db.DateTime())  # 回复时间

    def from_json(self, json_fb):
        self.imei = json_fb['imei']
        self.os_version = json_fb['os_version']
        self.device_factory = json_fb['device_factory']
        self.device_model = json_fb['device_model']
        self.app_version = json_fb['app_version']
        self.user_contact = json_fb['user_contact']
        self.content = json_fb['content']

    def __repr__(self):
        return '<FeedBack %r>' % self.id


# app及插件列表
class AppList(db.Model):
    __tablename__ = 'app_list'
    id = db.Column(db.Integer, primary_key=True)
    app_type = db.Column(db.Integer, nullable=False)  # 文件类型值
    app_name = db.Column(db.String(50), nullable=False)  # 文件名称
    package_name = db.Column(db.String(128), nullable=False)  # 文件包名

    __table_args__ = (db.UniqueConstraint('app_type', 'package_name', name='uq_app_list_app_type_package_name'),)

    def __repr__(self):
        return '<AppList %r>' % self.package_name


# 微商神器, 微商小助手, bi服务, 领航旗舰不用此表
class AppVersion(db.Model):
    __tablename__ = 'app_version'
    id = db.Column(db.Integer, primary_key=True)
    app_type = db.Column(db.Integer, nullable=False)
    version_name = db.Column(db.String(64), nullable=False)
    version_code = db.Column(db.Integer, nullable=False)
    app_size = db.Column(db.Integer, nullable=False)
    app_dir = db.Column(db.String(256), nullable=False)
    min_version_code = db.Column(db.Integer, nullable=False)
    max_version_code = db.Column(db.Integer, nullable=False)
    update_msg = db.Column(db.String(1024), nullable=False)
    release_time = db.Column(db.DateTime(), default=datetime.now)
    is_released = db.Column(db.Boolean, default=False)
    spread_id = db.Column(db.Integer, db.ForeignKey('spread_manager.id'))

    def __repr__(self):
        return '<AppVersion %r>' % self.version_name

    def ping(self):
        self.release_time = datetime.now()
        db.session.add(self)


class ExceptionLog(db.Model):
    __tablename__ = 'exception_log'
    id = db.Column(db.Integer, primary_key=True)
    md5_value = db.Column(db.String(32), nullable=False)
    imei = db.Column(db.String(15), nullable=False, default='')
    app_version = db.Column(db.String(64), nullable=False)
    os_version = db.Column(db.String(15), nullable=False)
    device_model = db.Column(db.String(64), nullable=False)
    package_name = db.Column(db.String(128), nullable=False)
    log_link = db.Column(db.String(128), nullable=False)
    status = db.Column(db.Integer, default=0)
    error_count = db.Column(db.Integer, default=0)
    create_time = db.Column(db.DateTime(), default=datetime.now)

    __table_args__ = (db.UniqueConstraint('md5_value', 'app_version', name='uq_exception_log_md5_value_app_version'),)

    def to_json(self):
        json_exception = {
            'id': self.id,
            'md5_value': self.md5_value,
            'app_version': self.app_version,
            'imei': self.imei,
            'os_version': self.os_version,
            'device_model': self.device_model,
            'package_name': self.package_name,
            'log_link': self.log_link,
            'status': self.status,
            'error_count': self.error_count,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json_exception

    def __repr__(self):
        return '<ExceptionLog %r>' % self.md5_value


class UserAppWeekStatistics(db.Model):
    __tablename__ = 'user_app_week_statistics'
    id = db.Column(db.Integer, primary_key=True)
    imei = db.Column(db.String(15), nullable=False)
    year = db.Column(db.Integer, default=int(datetime.now().strftime('%Y')), nullable=False)
    week = db.Column(db.Integer, default=int(datetime.now().strftime('%W')), nullable=False)
    count = db.Column(db.Integer, default=0)

    __table_args__ = (db.UniqueConstraint('imei', 'year', 'week', name='uq_user_app_week_statistics_imei_year_week'), )

    def __repr__(self):
        return '<UserAppWeekStatistics %r-%r-%r>' % (self.imei, self.year, self.week)


class UserAppMonthStatistics(db.Model):
    __tablename__ = 'user_app_month_statistics'
    id = db.Column(db.Integer, primary_key=True)
    imei = db.Column(db.String(15), nullable=False)
    year = db.Column(db.Integer, default=int(datetime.now().strftime('%Y')), nullable=False)
    month = db.Column(db.Integer, default=int(datetime.now().strftime('%m')), nullable=False)
    count = db.Column(db.Integer, default=0)

    __table_args__ = (db.UniqueConstraint('imei', 'year', 'month',
                                          name='uq_user_app_month_statistics_imei_year_month'), )

    def __repr__(self):
        return '<UserAppMonthStatistics %r-%r-%r>' % (self.imei, self.year, self.month)


# 活动集合表
class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(10), nullable=True)  # 活动编号 000001 邀请得会员 000002 分享领会员 000003 签到领会员 000004 五星好评
    name = db.Column(db.String(68), nullable=True)  # 活动名称
    award_period = db.Column(db.SmallInteger, default=0, nullable=False)  # 领奖周期
    reward = db.Column(db.SmallInteger, default=0, nullable=False)  # vip 奖励
    icon = db.Column(db.String(256), default='')  # 活动图标
    link = db.Column(db.String(256), default='')  # 活动链接
    content = db.Column(db.Text, default='')  # 备注
    status = db.Column(db.SmallInteger, default=0)  # 0 下架 1 上架
    start_time = db.Column(db.Date(), default=datetime.now().date(), nullable=False)  # 以天为单位
    end_time = db.Column(db.Date(), default=datetime.now().date(), nullable=False)  # 以天为单位
    share_title = db.Column(db.String(256), default='')  # 分享标题
    share_description = db.Column(db.String(256), default='')  # 分享描述
    share_icon = db.Column(db.String(256), default='')  # 分享图标
    share_link = db.Column(db.String(256), default='')  # 分享链接
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 创建时间
    update_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 更新时间

    def __repr__(self):
        return '<Activity %r>' % self.name


# 签到领会员数据
class SignData(db.Model):
    __tablename__ = 'sign_data'
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, nullable=True)  # 当前上架的活动id, 主要是区分哪次活动
    number = db.Column(db.String(10), nullable=True)   # 签到会员编号
    sign_godin_id = db.Column(db.String(32), nullable=True)  # 签到人
    total_count = db.Column(db.Integer, nullable=True, default=0)  # 总领奖次数
    sign_count = db.Column(db.Integer, nullable=True, default=0)  # 连续签到次数
    last_sign_time = db.Column(db.Date(), default=datetime.now().date(), nullable=False)  # 最新签到时间, 以天为单位
    phone = db.Column(db.String(15), nullable=True)  # 手机号
    update_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 更新时间

    __table_args__ = (db.UniqueConstraint('activity_id', 'number', 'sign_godin_id', name='uq_sign_data_index'),)

    def __repr__(self):
        return '<SignData %r>' % self.id


# 签到领会员数据记录
class SignRecord(db.Model):
    __tablename__ = 'sign_record'
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, nullable=True)  # 当前上架的活动id, 主要是区分哪次活动
    sign_godin_id = db.Column(db.String(32), nullable=True)  # 签到人
    sign_time = db.Column(db.Date(), default=datetime.now().date(), nullable=False)  # 完成时间, 以天为单位
    phone = db.Column(db.String(15), nullable=True)  # 手机号
    reward = db.Column(db.SmallInteger, default=0, nullable=False)
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 完成具体时间更新时间

    def __repr__(self):
        return '<SignRecord %r>' % self.id


class ActivityShareCodeCount(db.Model):
    __tablename__ = 'activity_share_code_count'
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    godin_id = db.Column(db.String(32), db.ForeignKey('user_info.godin_id'), nullable=False)
    share_count = db.Column(db.Integer, default=0, nullable=False)
    register_count = db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self):
        return '<ActivityShareCodeCount %r, %r, %r>' % (self.id, self.activity_id, self.godin_id)


# banner 广告
class BannerAds(db.Model):
    __tablename__ = 'banner_ads'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)  # 广告名称
    position = db.Column(db.SmallInteger, default=-1)  # 位置 0 优化加速 1 主桌面
    source = db.Column(db.SmallInteger, default=-1)  # 0 自有广告 1 外接广告
    charge_mode = db.Column(db.SmallInteger, default=-1)  # 收费方式 0 CPC
    unit_price = db.Column(db.Integer, default=0, nullable=False)  # 广告单价， 单位分
    contacts = db.Column(db.String(64), nullable=False)  # 广告商联系人
    contact_way = db.Column(db.String(128), nullable=False)  # 广告商联系方式
    advertiser = db.Column(db.String(64), nullable=False)  # 广告商
    number = db.Column(db.String(64), nullable=False)  # 广告编号
    display_number = db.Column(db.SmallInteger, default=0)  # 广告每天每人的展示数
    carousel = db.Column(db.SmallInteger, default=0)  # 0 不轮播, 1 轮播
    carousel_interval = db.Column(db.SmallInteger, default=0)  # 轮播间隔时间秒
    icon = db.Column(db.String(256), default='')  # 广告图标
    icon_dest_link = db.Column(db.String(256), default='')  # 广告图标链接地址
    status = db.Column(db.Boolean, default=0)  # 广告状态 0 关闭, 1 开启
    refresh_status = db.Column(db.Boolean, nullable=False, default=0)  # 刷新状态 0 关闭, 1 开启
    morning_count = db.Column(db.Integer, nullable=False, default=0)  # 上午刷新次数
    afternoon_count = db.Column(db.Integer, nullable=False, default=0)  # 下午刷新次数
    night_count = db.Column(db.Integer, nullable=False, default=0)  # 下午刷新次数
    user_count = db.Column(db.Integer, nullable=False, default=0)  # 昨日活跃的用户数
    start_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 合作开始时间
    end_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 合作结束时间
    banner_statistics = db.relationship('BannerAdsStatistics', backref='bannner', lazy='dynamic')

    def __repr__(self):
        return '<BannerAds %r-%r>' % (self.id, self.name)


# 统计banner展示数和点击量
class BannerAdsStatistics(db.Model):
    __tablename__ = 'banner_ads_statistics'
    id = db.Column(db.Integer, primary_key=True)
    ad_id = db.Column(db.Integer, db.ForeignKey('banner_ads.id'), nullable=False)
    record_time = db.Column(db.Date, default=datetime.today())  # 记录日期 eg:2017-07-10
    imei = db.Column(db.String(15), nullable=False)
    operation = db.Column(db.SmallInteger, default=-1)  # 统计类型 0 展示数, 1 点击数
    count = db.Column(db.Integer, default=-1)  # 计数

    __table_args__ = (db.UniqueConstraint('ad_id', 'record_time', 'imei', 'operation',
                                          name='uq_banner_ads_statistics_index'),)

    def __repr__(self):
        return '<BannerAdsStatistics %r-%r>' % (self.id, self.ad_id)


# 开屏广告
class OpenScreenAds(db.Model):
    __tablename__ = 'open_screen_ads'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)  # 广告名称
    position = db.Column(db.SmallInteger, default=-1)  # 位置 0 开屏首页, 1 应用启动页 2 应用更新
    source = db.Column(db.SmallInteger, default=-1)  # 0 自有广告 1 外接广告
    charge_mode = db.Column(db.SmallInteger, default=-1)  # 收费方式 0 CPM
    unit_price = db.Column(db.Integer, default=0, nullable=False)  # 广告单价， 单位分
    contacts = db.Column(db.String(64), nullable=False)  # 广告商联系人
    contact_way = db.Column(db.String(128), nullable=False)  # 广告商联系方式
    advertiser = db.Column(db.String(64), nullable=False)  # 广告商
    number = db.Column(db.String(64), nullable=False)  # 广告编号
    display_number = db.Column(db.SmallInteger, default=0)  # 广告每天每人的展示数
    skip_time = db.Column(db.SmallInteger, default=0)  # 跳过时间秒
    icon = db.Column(db.String(256), default='')  # 广告图
    status = db.Column(db.Boolean, default=0)  # 广告状态 0 关闭, 1 开启
    start_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 合作开始时间
    end_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 合作结束时间
    virtual_skip = db.Column(db.SmallInteger, default=0, nullable=False)  # 0 关闭, 1 开启
    control_click_rate = db.Column(db.SmallInteger, default=0, nullable=False)  # 控制点击率
    skip_count = db.Column(db.SmallInteger, default=0, nullable=False)  # 用户点击跳过次数限制(最大)
    app_link = db.Column(db.String(256), default='', nullable=False)  # 应用下载链接
    refresh_status = db.Column(db.Boolean, nullable=False, default=0)  # 刷新状态 0 关闭, 1 开启
    morning_count = db.Column(db.Integer, nullable=False, default=0)  # 上午刷新次数
    afternoon_count = db.Column(db.Integer, nullable=False, default=0)  # 下午刷新次数
    night_count = db.Column(db.Integer, nullable=False, default=0)  # 下午刷新次数
    user_count = db.Column(db.Integer, nullable=False, default=0)  # 昨日活跃的用户数
    open_screen_ads_statistics = db.relationship('OpenScreenAdsStatistics', backref='open_screen', lazy='dynamic')

    def __repr__(self):
        return '<OpenScreenAds %r-%r>' % (self.id, self.name)


# 统计开屏广告展示数统计
class OpenScreenAdsStatistics(db.Model):
    __tablename__ = 'open_screen_ads_statistics'
    id = db.Column(db.Integer, primary_key=True)
    ad_id = db.Column(db.Integer, db.ForeignKey('open_screen_ads.id'), nullable=False)
    record_time = db.Column(db.Date, default=datetime.today())  # 记录日期 eg:2017-07-10
    imei = db.Column(db.String(15), nullable=False)
    operation = db.Column(db.SmallInteger, default=0, nullable=False)  # 统计类型 0 展示数, 1 点击数, 2 自然点击数
    count = db.Column(db.Integer, default=-1)  # 计数

    __table_args__ = (db.UniqueConstraint('ad_id', 'record_time', 'imei', 'operation',
                                          name='uq_open_screen_ads_statistics_index'),)

    def __repr__(self):
        return '<OpenScreenAdsStatistics %r-%r>' % (self.id, self.ad_id)


# 开屏广告哪些用户模拟限制跳过广告
class OpenScreenSimulatedUser(db.Model):
    __tablename__ = 'open_screen_simulate_user'
    id = db.Column(db.Integer, primary_key=True)
    ad_id = db.Column(db.Integer, db.ForeignKey('open_screen_ads.id'), nullable=False)
    record_time = db.Column(db.Date, default=datetime.today())  # 记录日期 eg:2017-07-10
    imei = db.Column(db.String(15), nullable=False)
    skip_count = db.Column(db.Integer, default=0)  # 用户点击跳过次数(实际)

    __table_args__ = (db.UniqueConstraint('ad_id', 'record_time', 'imei', name='uq_open_screen_simulate_user_index'),)

    def __repr__(self):
        return '<OpenScreenSimulatedUser %r-%r>' % (self.id, self.ad_id)


# 开屏广告需要跳过广告的模拟数据
class OpenScreenSimulateData(db.Model):
    __tablename__ = 'open_screen_simulate_data'
    id = db.Column(db.Integer, primary_key=True)
    ad_id = db.Column(db.Integer, db.ForeignKey('open_screen_ads.id'), nullable=False)
    record_time = db.Column(db.Date, default=datetime.today())  # 当日记录日期 eg:2017-07-10
    total_display_number = db.Column(db.Integer, nullable=False)  # 昨日总展现量
    display_number = db.Column(db.Integer, nullable=False, default=0)  # 昨日去重展现量
    control_times = db.Column(db.Integer, nullable=False, default=0)  # 控制次数
    control_number = db.Column(db.Integer, nullable=False, default=0)  # 控制人数
    actual_number = db.Column(db.Integer, nullable=False, default=0)  # 实际人数
    actual_control_times = db.Column(db.Integer, nullable=False, default=0)  # 实际控制次数

    __table_args__ = (db.UniqueConstraint('ad_id', 'record_time', name='uq_open_screen_simulate_data_index'),)

    def __repr__(self):
        return '<OpenScreenSimulateData %r-%r>' % (self.id, self.ad_id)


# 今天头条广告点击信息
class TouTiaoAdsClickInfo(db.Model):
    __tablename__ = 'toutiao_ads_click_info'
    id = db.Column(db.Integer, primary_key=True)
    ad_id = db.Column(db.String(32))
    cid = db.Column(db.String(32))
    imei = db.Column(db.String(32), index=True)
    mac = db.Column(db.String(32))
    android_id = db.Column(db.String(32))
    os_version = db.Column(db.Integer)  # 0 android
    timestamp = db.Column(db.Integer)
    callback_url = db.Column(db.String(1024))
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)
    last_seen = db.Column(db.DateTime(), default=datetime.now, nullable=False)
    status = db.Column(db.Integer, default=0)  # 0 未发送, 1 已发送

    __table_args__ = (db.UniqueConstraint('imei', 'mac', name='uq_imei_mac'),)

    def __repr__(self):
        return '<TouTiaoAdsClickInfo %r-%r-%r>' % (self.id, self.ad_id, self.cid)


# 会员商品订单
class MemberWareOrder(db.Model):
    __tablename__ = 'member_ware_order'
    order_number = db.Column(db.String(32), primary_key=True, index=True, nullable=False)  # 订单编号
    buyer_godin_id = db.Column(db.String(32), db.ForeignKey('vip_members.godin_id'))  # 购买者的国鼎ID
    ware_id = db.Column(db.String(32), db.ForeignKey('member_ware.id'))  # 商品ID
    pay_type = db.Column(db.SMALLINT, default=0)  # 0 微信, 1 支付宝, 2 其他
    ware_price = db.Column(db.Integer, nullable=False)  # 下单时的商品标价，单位为分
    discount = db.Column(db.DECIMAL(3, 2))  # 下单时的折扣信息
    discount_price = db.Column(db.Integer, nullable=False)  # 下单时的折后价格，单位为分
    status = db.Column(db.Integer, default=0, nullable=False)  # 订单状态， 0 未支付  1 已支付
    ac_source = db.Column(db.Integer, default=0, nullable=False)  # 订单状态， 0 应用本身支付  1 分身支付
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 订单创建时间
    pay_time = db.Column(db.DateTime())  # 订单支付时间
    start_time = db.Column(db.DateTime(), nullable=False)  # 商品有效起始时间
    end_time = db.Column(db.DateTime(), nullable=False)  # 商品有效结束时间
    category = db.Column(db.SMALLINT, default=0, nullable=False)  # 0 付费, 1 活动, 2 手动添加, 3 其他
    key_record_id = db.Column(db.String(20), index=True, nullable=False, default='00000000000000')  # key操作表id
    buy_type = db.Column(db.String(100))  # 购买类型 普通升黄金, 普通升铂金,  黄金续费黄金...
    buy_grade = db.Column(db.SMALLINT, default=1, nullable=False)  # 当前订单要升级的会员等级 0 黄金 1 铂金
    inviter_godin_id = db.Column(db.String(32))


    def __repr__(self):
        return '<MemberWareOrder %r>' % self.order_number

    def to_json(self, category, type_name):
        now_time = datetime.now()
        if self.end_time < now_time:
            ware_status = 0
        elif self.start_time <= now_time <= self.end_time:
            ware_status = 1
        else:
            ware_status = 2
        json_obj = {
            'order_number': self.order_number,
            'category': category,
            'pay_time': self.pay_time.strftime('%Y-%m-%d %H:%M:%S'),
            'ware_price': self.ware_price,
            'discount': float(self.discount),
            'discount_price': self.discount_price,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'ware_status': ware_status,
            'type_name': type_name,
            'buy_category': self.category
        }
        return json_obj


# 手动添加vip会员需要激活
class ActivateMembers(db.Model):
    __tablename__ = 'activate_members'
    id = db.Column(db.Integer, primary_key=True)
    godin_id = db.Column(db.String(32), nullable=False)  # 国鼎ID
    vip_type = db.Column(db.SmallInteger, nullable=False, default=0)  # 0 手动添加, 1 活动添加
    channel = db.Column(db.String(24), nullable=False)  # 渠道
    ware_id = db.Column(db.String(32), nullable=False)  # 商品ID
    status = db.Column(db.SmallInteger, default=0)  # 0 需要激活, 1 不需要激活
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 手动添加时间
    modify_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 激活时间

    def __repr__(self):
        return '<ActivateMembers %r>' % self.godin_id


# VIP会员
class VipMembers(db.Model):
    __tablename__ = 'vip_members'
    godin_id = db.Column(db.String(32), primary_key=True, unique=True, nullable=False)  # 国鼎ID
    category = db.Column(db.SMALLINT, default=0)  # 0 付费, 1 活动, 2 手动添加, 3 其他
    cur_pay_cate = db.Column(db.SMALLINT)  # 0 月, 1 季, 2 半年, 3 年, 4 扩展
    status = db.Column(db.SmallInteger, default=1)  # 0 无效, 1 有效
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # VIP账户创建时间
    first_pay_time = db.Column(db.DateTime())  # 首次付费时间
    valid_time = db.Column(db.DateTime())  # 铂金会员有效期至
    channel = db.Column(db.String(24), nullable=False)  # 渠道
    grade = db.Column(db.SMALLINT, default=3, nullable=False)  # 会员等级： 0 普通, 1 黄金会员, 2 铂金会员 3 用于区分老版本接口
    gold_valid_time = db.Column(db.DateTime())  # 黄金会员有效期至

    def __repr__(self):
        return '<VipMembers %r>' % self.godin_id


# 会员商品
class MemberWare(db.Model):
    __tablename__ = 'member_ware'
    id = db.Column(db.String(32), primary_key=True)  # 商品ID
    name = db.Column(db.String(64), unique=True)  # 商品名称，唯一
    category = db.Column(db.SMALLINT, default=0)  # 0 月, 1 季, 2 半年, 3 年, 4 扩展
    price = db.Column(db.Integer, nullable=False)  # 商品价格， 单位为分
    discount = db.Column(db.DECIMAL(3, 2))  # 铂金折扣，0.00 -- 1.00
    gold_discount = db.Column(db.DECIMAL(3, 2))  # 黄金折扣，0.00 -- 1.00
    common_discount = db.Column(db.DECIMAL(3, 2))  # 普通折扣，0.00 -- 1.00
    status = db.Column(db.SMALLINT, default=1)  # 0 无效, 1 有效
    priority = db.Column(db.SMALLINT, default=1)  # 推荐位, 0 普通, 1 推荐
    description = db.Column(db.String(1024))  # 商品描述
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 商品创建时间
    channel = db.Column(db.String(32), nullable=False)  # 渠道
    picture = db.Column(db.String(256), default='', nullable=False)  # 会员推荐图标
    ads_category = db.Column(db.String(24), default='', nullable=False)  # 开放广告类型
    gold_or_platinum = db.Column(db.SMALLINT, default=1, nullable=False)  # 商品表示，0 代表黄金， 1 代表铂金

    def __repr__(self):
        return '<MemberWare %r-%r>' % (self.id, self.name)

    def to_json(self):
        json_obj = {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'price': self.price,
            'discount': float(self.discount),
            'gold_discount': float(self.gold_discount),
            'common_discount': float(self.common_discount),
            'discount_price': float(self.price*self.discount),
            'priority': self.priority,
            'description': self.description
        }
        return json_obj


# VIP用户付费周统计
class VipPayWeekStatistics(db.Model):
    __tablename__ = 'vip_pay_week_statistics'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, default=int(datetime.now().strftime('%Y')), nullable=False)
    week = db.Column(db.Integer, default=int(datetime.now().strftime('%W')), nullable=False)
    new_reg_count = db.Column(db.Integer, default=0)  # 新增付费人数
    new_pay_amount = db.Column(db.Integer, default=0)  # 新增付费额，单位为分
    old_not_pay_count = db.Column(db.Integer, default=0)  # 到期未续费人数
    old_pay_count = db.Column(db.Integer, default=0)  # 到期续费人数
    old_pay_amount = db.Column(db.Integer, default=0)  # 续费额, 单位为分
    income_amount = db.Column(db.Integer, default=0)  # 收入总额, 单位为分

    __table_args__ = (db.UniqueConstraint('year', 'week', name='uq_vip_pay_week_statistics_year_week'), )

    def __repr__(self):
        return '<VipPayWeekStatistics %r-%r>' % (self.year, self.week)


# VIP用户付费月统计
class VipPayMonthStatistics(db.Model):
    __tablename__ = 'vip_pay_month_statistics'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, default=int(datetime.now().strftime('%Y')), nullable=False)
    month = db.Column(db.Integer, default=int(datetime.now().strftime('%m')), nullable=False)
    new_reg_count = db.Column(db.Integer, default=0)  # 新增付费人数
    new_pay_amount = db.Column(db.Integer, default=0)  # 新增付费额，单位为分
    old_not_pay_count = db.Column(db.Integer, default=0)  # 到期未续费人数
    old_pay_count = db.Column(db.Integer, default=0)  # 到期续费人数
    old_pay_amount = db.Column(db.Integer, default=0)  # 续费额, 单位为分
    income_amount = db.Column(db.Integer, default=0)  # 收入总额, 单位为分

    __table_args__ = (db.UniqueConstraint('year', 'month', name='uq_vip_pay_month_statistics_year_month'), )

    def __repr__(self):
        return '<VipPayWeekStatistics %r-%r>' % (self.year, self.month)


# VIP用户付费日统计
class VipPayDayStatistics(db.Model):
    __tablename__ = 'vip_pay_day_statistics'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date(), default=datetime.today(), unique=True, nullable=False)
    new_reg_count = db.Column(db.Integer, default=0)  # 新增付费人数
    new_pay_amount = db.Column(db.Integer, default=0)  # 新增付费额，单位为分
    old_not_pay_count = db.Column(db.Integer, default=0)  # 到期未续费人数
    old_pay_count = db.Column(db.Integer, default=0)  # 到期续费人数
    old_pay_amount = db.Column(db.Integer, default=0)  # 续费额, 单位为分
    income_amount = db.Column(db.Integer, default=0)  # 收入总额, 单位为分

    def __repr__(self):
        return '<VipPayDayStatistics %r>' % self.date


class CommunicationGroup(db.Model):
    __tablename__ = 'communication_group'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, nullable=False, default=0)  # 0 微商神器交流群  1 微商神器交流群
    group_number = db.Column(db.String(64), unique=True, index=True, nullable=False, default='')  # 交流群号
    group_key = db.Column(db.String(128), unique=True, index=True, nullable=False, default='')  # 交流群key

    def __repr__(self):
        return '<CommunicationGroup %r>' % self.type


# 开屏广告针对SDK访问数据统计
class OpenScreenAdsData(db.Model):
    __tablename__ = 'open_screen_ads_data'
    id = db.Column(db.Integer, primary_key=True)
    ad_id = db.Column(db.Integer, index=True, nullable=False)
    record_time = db.Column(db.Date, default=datetime.today())  # 记录日期 eg:2017-07-10
    imei = db.Column(db.String(15), nullable=False)
    operation = db.Column(db.SmallInteger, default=0, nullable=False)  # 统计类型 0 进入次数, 1 获取次数
    count = db.Column(db.Integer, default=-1)  # 计数

    __table_args__ = (db.UniqueConstraint('ad_id', 'record_time', 'imei', 'operation',
                                          name='uq_open_screen_ads_data_index'),)

    def __repr__(self):
        return '<OpenScreenAdsData %r-%r>' % (self.id, self.ad_id)


# 互动广告
class InteractiveAds(db.Model):
    __tablename__ = 'interactive_ads'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)  # 广告名称
    position = db.Column(db.SmallInteger, default=-1)  # 位置 0 主界面, 1 社交频道, 百宝箱
    source = db.Column(db.SmallInteger, default=-1)  # 0 互动广告
    charge_mode = db.Column(db.SmallInteger, default=-1)  # 收费方式 0 CPC
    icon = db.Column(db.String(256), default='')  # 广告图
    third_link = db.Column(db.String(256), default='', nullable=False)  # 打开链接
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 创建时间
    status = db.Column(db.Boolean, default=0)  # 广告状态 0 关闭, 1 开启
    refresh_status = db.Column(db.Boolean, nullable=False, default=0)  # 刷新状态 0 关闭, 1 开启
    morning_count = db.Column(db.Integer, nullable=False, default=0)  # 上午刷新次数
    afternoon_count = db.Column(db.Integer, nullable=False, default=0)  # 下午刷新次数
    night_count = db.Column(db.Integer, nullable=False, default=0)  # 下午刷新次数
    user_count = db.Column(db.Integer, nullable=False, default=0)  # 昨日活跃的用户数
    interactive_ads_statistics = db.relationship('InteractiveAdsStatistics', backref='interactive_ads', lazy='dynamic')

    def __repr__(self):
        return '<InteractiveAds %r-%r>' % (self.id, self.name)


# 互动广告统计
class InteractiveAdsStatistics(db.Model):
    __tablename__ = 'interactive_ads_statistics'
    id = db.Column(db.Integer, primary_key=True)
    ad_id = db.Column(db.Integer, db.ForeignKey('interactive_ads.id'), nullable=False)
    record_time = db.Column(db.Date, default=datetime.today())  # 记录日期 eg:2017-07-10
    imei = db.Column(db.String(15), nullable=False)
    operation = db.Column(db.SmallInteger, default=0, nullable=False)  # 统计类型 0 展示数, 1 点击数
    count = db.Column(db.Integer, default=-1)  # 计数

    __table_args__ = (db.UniqueConstraint('ad_id', 'record_time', 'imei', 'operation',
                                          name='uq_interactive_ads_statistics_index'),)

    def __repr__(self):
        return '<InteractiveAdsStatistics %r-%r>' % (self.id, self.ad_id)


# 渠道表
class Channel(db.Model):
    __tablename__ = 'channel'
    channel = db.Column(db.String(32), primary_key=True)  # 渠道
    channel_name = db.Column(db.String(32), nullable=False)  # 渠道名称
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)

    def __repr__(self):
        return '<Channel %r>' % self.channel


# vip 类型表
class VipType(db.Model):
    __tablename__ = 'vip_type'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(32), nullable=False)  # 类型名称
    days = db.Column(db.Integer, nullable=False)  # 类型天数
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)

    def __repr__(self):
        return '<VipType %r>' % self.name


# 服务协议
class ServiceProtocol(db.Model):
    __tablename__ = 'service_protocol'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.SMALLINT)  # 0 会员协议 1 开屏广告展示策略, 涉及第三方 2 软件服务使用协议 4 商业会员服务协议 3 商业智能报告协议 10 推广赚钱活动说明
    content = db.Column(db.Text, default='')   # 协议内容

    def __repr__(self):
        return '<ServiceProtocol>' % self.id


# banner 广告配置
class BannerConfig(db.Model):
    __tablename__ = 'banner_config'
    id = db.Column(db.Integer, primary_key=True)
    channel = db.Column(db.String(32), nullable=False)  # 渠道
    version = db.Column(db.SmallInteger, nullable=False)  # 0 历史版本 1 当前版本
    ad_id = db.Column(db.Integer, nullable=False, default=0)  # 广告id
    status = db.Column(db.Integer, nullable=False, default=0)  # 广告默认不配置
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)

    def __repr__(self):
        return '<BannerConfig %r>' % self.id


# banner 广告刷新数据
class BannerRefreshData(db.Model):
    __tablename__ = 'banner_refresh_data'
    id = db.Column(db.Integer, primary_key=True)
    ad_id = db.Column(db.Integer, db.ForeignKey('banner_ads.id'), nullable=False)
    type = db.Column(db.Integer, nullable=False)  # 0 上午点击, 1 下午点击, 2 晚上点击
    record_time = db.Column(db.Date, default=datetime.today())  # 当日记录日期 eg:2017-07-10
    control_times = db.Column(db.Integer, nullable=False, default=0)  # 控制次数
    control_number = db.Column(db.Integer, nullable=False, default=0)  # 控制人数
    actual_number = db.Column(db.Integer, nullable=False, default=0)  # 实际人数

    __table_args__ = (db.UniqueConstraint('ad_id', 'record_time', 'type', name='uq_banner_refresh_data_index'),)

    def __repr__(self):
        return '<BannerRefreshData %r-%r>' % (self.id, self.ad_id)


# banner 哪些用户需要刷新广告
class BannerRefreshUser(db.Model):
    __tablename__ = 'banner_refresh_user'
    id = db.Column(db.Integer, primary_key=True)
    ad_id = db.Column(db.Integer, db.ForeignKey('banner_ads.id'), nullable=False)
    type = db.Column(db.Integer, nullable=False)  # 0 上午点击, 1 下午点击, 2 晚上点击
    record_time = db.Column(db.Date, default=datetime.today())  # 记录日期 eg:2017-07-10
    imei = db.Column(db.String(15), nullable=False)
    count = db.Column(db.Integer, default=0)  # 用户刷新数

    __table_args__ = (db.UniqueConstraint('ad_id', 'record_time', 'imei', 'type',
                                          name='uq_banner_refresh_user_index'),)

    def __repr__(self):
        return '<BannerRefreshUser %r-%r>' % (self.id, self.ad_id)


# 开屏广告配置
class OpenConfig(db.Model):
    __tablename__ = 'open_config'
    id = db.Column(db.Integer, primary_key=True)
    channel = db.Column(db.String(32), nullable=False)  # 渠道
    version = db.Column(db.SmallInteger, nullable=False)  # 0 历史版本 1 当前版本
    ad_id = db.Column(db.Integer, nullable=False, default=0)  # 广告id
    status = db.Column(db.Integer, nullable=False, default=0)  # 广告默认不配置
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)

    def __repr__(self):
        return '<OpenConfig %r>' % self.id


# 互动广告配置
class InteractiveConfig(db.Model):
    __tablename__ = 'interactive_config'
    id = db.Column(db.Integer, primary_key=True)
    channel = db.Column(db.String(32), nullable=False)  # 渠道
    version = db.Column(db.SmallInteger, nullable=False)  # 0 历史版本 1 当前版本
    ad_id = db.Column(db.Integer, nullable=False, default=0)  # 广告id
    status = db.Column(db.Integer, nullable=False, default=0)  # 广告默认不配置
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)

    def __repr__(self):
        return '<InteractiveConfig %r>' % self.id


# 默认广告图
class AdsIcon(db.Model):
    __tablename__ = 'ads_icon'
    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.SmallInteger, nullable=False)  # 1 第三方应用开屏, 2 banner游戏乐园,
    #  3 banner社交频道, 4 banner备忘录, 5 banner密友, 6 banner微信伪装, 7 banner优化加速
    icon_addr = db.Column(db.String(256), nullable=False, default='')  # 广告默认图地址
    jump_link = db.Column(db.String(256), nullable=False, default='')  # 跳转链接
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)
    status = db.Column(db.Integer, nullable=False, default=0)  # 1 显示  0 不显示

    def __repr__(self):
        return '<ads_icon %r>' % self.id


class WeAvatar(db.Model):
    __tablename__ = 'we_avatar'
    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.Integer, db.ForeignKey('avatar_version.id'), nullable=False)
    number = db.Column(db.Integer, default=-1)  # 制作分身编号
    app_name = db.Column(db.String(64), nullable=False)
    down_addr = db.Column(db.String(256), nullable=False)
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)
    avatar_info = db.relationship('AvatarVersion', backref=backref('we_avatar', uselist=False), lazy='joined')

    def __repr__(self):
        return '<WeAvatar %r>' % self.version_name


class AvatarVersion(db.Model):
    __tablename__ = 'avatar_version'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    version_name = db.Column(db.String(64), nullable=False)
    version_code = db.Column(db.Integer, nullable=False)
    pack_name = db.Column(db.String(64), nullable=False)
    app_size = db.Column(db.Integer, nullable=False)
    app_dir = db.Column(db.String(256), nullable=False)
    decompile_addr = db.Column(db.String(256), nullable=False)
    update_msg = db.Column(db.String(1024), nullable=False)
    update_status = db.Column(db.Integer, nullable=False, default=0)  # 0 普通更新   1 强制更新
    status = db.Column(db.Integer, nullable=False, default=0)  # 0 未反编译 1 已经反编译 2 发布

    def __repr__(self):
        return '<AvatarVersion %r>' % self.version_name


class ShareCode(db.Model):
    __tablename__ = 'share_code'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(6), nullable=True)   # 活动编号   000001 邀请好友得会员
    invite_id = db.Column(db.String(32), nullable=True)  # 邀请人
    share_id = db.Column(db.String(32), nullable=True)   # 被邀请人

    __table_args__ = (db.UniqueConstraint('number', 'invite_id', 'share_id', name='uq_share_code_index'),)

    def __repr__(self):
        return '<ShareCode %r>' % self.id


class ShareCount(db.Model):
    __tablename__ = 'share_count'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(6), nullable=True)   # 活动编号   000001 邀请好友得会员
    invite_id = db.Column(db.String(32), nullable=True)  # 邀请人
    count = db.Column(db.Integer, nullable=True)   # 发送邀请次数

    __table_args__ = (db.UniqueConstraint('number', 'invite_id', name='uq_share_code_index'),)

    def __repr__(self):
        return '<ShareCount %r>' % self.id


class Key(db.Model):
    __tablename__ = 'key'
    id = db.Column(db.String(32), primary_key=True)   # 授权码
    status = db.Column(db.Integer, default=0, nullable=False)   # 状态  0 未激活  1 已激活  2 过期未使用 3 使用结束
    key_record_id = db.Column(db.String(20), db.ForeignKey('key_record.id'), index=True, nullable=False)  # key操作表id
    create_time = db.Column(db.DateTime(), default=datetime.now)  # 创建时间
    give_activate_status = db.Column(db.SmallInteger, default=0, nullable=False)  # 赠送会员是否激活 0 未赠送 1 已赠送

    def __repr__(self):
        return '<key %r>' % self.id


class KeyRecord(db.Model):
    __tablename__ = 'key_record'
    id = db.Column(db.String(14), primary_key=True)
    channel_account_id = db.Column(db.Integer, db.ForeignKey('channel_account.id'), index=True, default=1)  # 渠道账户主鍵id
    create_time = db.Column(db.Date(), default=datetime.now, nullable=False)  # 创建时间
    #expire_time = db.Column(db.DateTime(), nullable=False)  # 有效期截止时间
    vip_time = db.Column(db.Integer, nullable=False, default=0)  # vip有效时间 天
    vip_ad_time = db.Column(db.Integer, nullable=False, default=0)  # 赠送铂金会员时间  天
    vip_gold_ad_time = db.Column(db.Integer, default=0)  # 赠送黄金会员时间  天
    count = db.Column(db.Integer, nullable=False, default=0)  # 创建数量
    oeprator = db.Column(db.String(32), nullable=False)  # 操作人
    content = db.Column(db.TEXT, default='', nullable=False)  # 备注
    phone_num = db.Column(db.String(11), index=True, nullable=False, default='11111111111')
    we_record_id = db.Column(db.String(15), index=True, nullable=False, default='11111111111')
    vip_ratio = db.Column(db.DECIMAL(3, 2), default=0)  # 会员分成比例  %
    business_ratio = db.Column(db.DECIMAL(3, 2), default=0)  # 商业会员分成比例  %
    account = db.relationship('ChannelAccount', backref=backref('key_record', uselist=False), lazy='joined')

    def __repr__(self):
        return '<KeyRecord %r>' % self.id


class UserKeyRecord(db.Model):
    __tablename__ = 'user_key_record'
    id = db.Column(db.Integer, primary_key=True)
    key_id = db.Column(db.String(32), db.ForeignKey('key.id'), index=True, nullable=False)  # 授权码
    activate_time = db.Column(db.DateTime(), nullable=False, default=datetime.now)  # 激活时间
    imei = db.Column(db.String(15), index=True, nullable=False)
    status = db.Column(db.Integer, default=0, nullable=False)  # 0 不可用 1 可用

    def __repr__(self):
        return '<UserKeyRecord %r>' % self.id


class KeyOrder(db.Model):
    __tablename__ = 'key_order'
    id = db.Column(db.String(32), primary_key=True, nullable=False)  # 订单编号
    key_id = db.Column(db.String(32), index=True, nullable=False)  # 授权码
    price = db.Column(db.Integer, nullable=False)  # 授权码价格， 单位为分
    pay_time = db.Column(db.DateTime())  # 订单支付时间
    status = db.Column(db.Integer, default=0, nullable=False)  # 订单状态， 0 未支付  1 已支付
    imei = db.Column(db.String(15), nullable=False)
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 订单创建时间

    def __repr__(self):
        return '<KeyOrder %r>' % self.id


class ChannelVersion(db.Model):
    __tablename__ = 'channel_version'
    id = db.Column(db.Integer, primary_key=True)
    app_type = db.Column(db.Integer, nullable=False)
    version_name = db.Column(db.String(64), nullable=False)
    version_code = db.Column(db.Integer, nullable=False)
    app_size = db.Column(db.Integer, nullable=False)
    app_dir = db.Column(db.String(256), nullable=False)
    min_version_code = db.Column(db.Integer, nullable=False)
    max_version_code = db.Column(db.Integer, nullable=False)
    update_msg = db.Column(db.String(1024), nullable=False)
    release_time = db.Column(db.DateTime(), default=datetime.now)
    status = db.Column(db.Integer, nullable=False, default=0)  # 0 普通更新 1 强制更新
    is_released = db.Column(db.Boolean, default=False)
    spread_id = db.Column(db.Integer, db.ForeignKey('spread_manager.id'), nullable=False)

    def __repr__(self):
        return '<ChannelVersion %r>' % self.version_name

    def ping(self):
        self.release_time = datetime.now()
        db.session.add(self)


# imei 会员
class ImeiVip(db.Model):
    __tablename__ = 'imei_vip'
    imei = db.Column(db.String(20), primary_key=True, unique=True, nullable=False)  # 用户imei
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # imei账户创建时间
    start_time = db.Column(db.Date(), default=datetime.now().date(), nullable=False)  # 以天为单位
    valid_time = db.Column(db.Date(), default=datetime.now().date(), nullable=False)  # 有效期至, 以天为单位

    def __repr__(self):
        return '<imei_vip %r>' % self.imei


# 授权码渠道表
class KeyChannel(db.Model):
    __tablename__ = 'key_channel'
    channel = db.Column(db.String(32), primary_key=True)  # 渠道
    channel_name = db.Column(db.String(32), nullable=False)  # 渠道名称
    price = db.Column(db.Integer, nullable=False)  # 授权码价格， 单位为分
    msg = db.Column(db.String(128), nullable=False)  # 信息描述
    status = db.Column(db.Integer, nullable=False, default=0)  # 0 无效 1 有效
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)

    def __repr__(self):
        return '<KeyChannel %r>' % self.channel


# 通知
class SysNotice(db.Model):
    __tablename__ = 'sys_notice'
    id = db.Column(db.String(30), primary_key=True)  # 通知ID
    flag_id = db.Column(db.Integer, unique=True)  # 标识id
    title = db.Column(db.String(64), unique=True)  # 通知标题
    content = db.Column(db.String(1024), default='')  # 通知内容
    remarks = db.Column(db.String(64), default='')  # 备注
    oeprator = db.Column(db.String(32), nullable=False)  # 操作人
    time_quantum = db.Column(db.SmallInteger)  # 时间段 0, '0：00 ~ 5：59', 1, '6：00 ~ 11：59', 2, '12：00 ~ 17：59',3, '18：00 ~ 23：59'
    notice_type = db.Column(db.SmallInteger, nullable=False)  # 0 普通文本信息 1 图片信息
    icon = db.Column(db.String(128), default='')  # 图片连接
    icon_link = db.Column(db.String(128), default='')  # 点击图片跳转
    status = db.Column(db.SmallInteger, nullable=False)  # 0 关闭 1 开启
    start_time = db.Column(db.Date(), default=datetime.now().date(), nullable=False)  # 开始时间
    end_time = db.Column(db.Date(), default=datetime.now().date(), nullable=False)  # 结束时间
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 消息创建时间
    update_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 消息更新时间
    notice_user = db.Column(db.SmallInteger, default=0, nullable=False)  # 不通知用户 0 全通知 1 普通用户不通知 2 黄金不通知...（可多选,多选值求和）
    wx = db.Column(db.String(255), default='')  # 添加的微信号

    def __repr__(self):
        return '<SysNotice %r-%r>' % (self.id, self.name)


# 通知记录
class NoticeRecord(db.Model):
    __tablename__ = 'notice_record'
    id = db.Column(db.Integer, primary_key=True)  # id
    notice_id = db.Column(db.String(15), nullable=False, index=True)  # 消息id
    imei = db.Column(db.String(15), nullable=False, index=True)  # 通知人
    status = db.Column(db.SmallInteger, nullable=False)  # 0 未读 1 已读
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 消息创建时间
    update_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 消息更新时间

    def __repr__(self):
        return '<NoticeRecord %r>' % self.id


# 授权码激活数据统计
class ActKeyStatistics(db.Model):
    __tablename__ = 'act_key_statistics'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)     # 年
    month = db.Column(db.Integer)    # 月份
    channel_agent = db.Column(db.Integer, default=0)  # 代理渠道
    channel_we = db.Column(db.Integer, default=0)  # 诚招代理
    channel_crack = db.Column(db.Integer, default=0)  # 破解赠送
    channel_buy = db.Column(db.Integer, default=0)  # 购买渠道

    def __repr__(self):
        return '<ActKeyStatistics %r>' % self.id


# 代理渠道详情统计
class AgentStatistics(db.Model):
    __tablename__ = 'agent_statistics'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)  # 年
    month = db.Column(db.Integer)  # 月份
    name = db.Column(db.String(15), nullable=False)  # 代理名称
    try_act = db.Column(db.Integer, default=0)    # 试用激活数量
    general_act = db.Column(db.Integer, default=0)  # 普通激活数量

    def __repr__(self):
        return '<AgentStatistics %r>' % self.id


# 管理代理人员
class Agent(db.Model):
    __tablename__ = 'agent'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)  # 代理名称

    def __repr__(self):
        return '<Agent %r>' % self.id


# 版本检测
class AppVersionCheck(db.Model):
    __tablename__ = 'app_version_check'
    id = db.Column(db.Integer, primary_key=True)
    versioncode = db.Column(db.Integer, nullable=False)
    versionname = db.Column(db.String(64), nullable=False)
    md5 = db.Column(db.String(64), nullable=False)
    build_time = db.Column(db.String(64), nullable=False)
    build_rev = db.Column(db.String(64), nullable=False)
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 创建时间

    def __repr__(self):
        return '<AppVersionCheck %r>' % self.id


# 智能好友会员
class BusinessMembers(db.Model):
    __tablename__ = 'business_members'
    godin_id = db.Column(db.String(32), primary_key=True, unique=True, nullable=False)  # 国鼎ID
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # VIP账户创建时间
    status = db.Column(db.SmallInteger, default=1)  # 0 无效, 1 有效
    first_pay_time = db.Column(db.DateTime())  # 首次付费时间
    valid_time = db.Column(db.DateTime())  # 有效期至

    def __repr__(self):
        return '<BusinessMembers %r>' % self.godin_id


# 智能好友新用户赠送记录
class BusinessGiveStatistics(db.Model):
    __tablename__ = 'business_give_statistics'
    godin_id = db.Column(db.String(32), primary_key=True, unique=True, nullable=False)  # 国鼎ID
    phone_num = db.Column(db.String(11), unique=True, nullable=False)
    days = db.Column(db.Integer, default=1)  # 赠送天数
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 赠送天数

    def __repr__(self):
        return '<BusinessGiveStatistics %r>' % self.godin_id


# 智能好友推荐会员
class BusinessRecommend(db.Model):
    __tablename__ = 'business_recommend'
    id = db.Column(db.Integer, primary_key=True)
    ware_id = db.Column(db.String(32))  # 商品id
    picture = db.Column(db.String(256), default='', nullable=False)  # 会员推荐图标
    tip_time = db.Column(db.Integer, default=0)  # 提示时间
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 创建时间

    def __repr__(self):
        return '<BusinessRecommend %r>' % self.id


# 商业会员类型表
class BusinessType(db.Model):
    __tablename__ = 'business_type'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(32), nullable=False)  # 类型名称
    days = db.Column(db.Integer, nullable=False)  # 类型天数
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)

    def __repr__(self):
        return '<BusinessType %r>' % self.name


# 智能加好友商品
class BusinessWare(db.Model):
    __tablename__ = 'business_ware'
    id = db.Column(db.String(32), primary_key=True)  # 商品ID
    name = db.Column(db.String(64), unique=True)  # 商品名称，唯一
    category = db.Column(db.SMALLINT, default=0)
    price = db.Column(db.Integer, nullable=False)  # 商品价格， 单位为分
    discount = db.Column(db.DECIMAL(3, 2))  # 折扣，0.00 -- 1.00
    status = db.Column(db.SMALLINT, default=1)  # 0 无效, 1 有效
    priority = db.Column(db.SMALLINT, default=1)  # 推荐位, 0 普通, 1 推荐
    description = db.Column(db.String(1024))  # 商品描述
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 商品创建时间
    picture = db.Column(db.String(256), default='', nullable=False)  # 会员推荐图标

    def __repr__(self):
        return '<BusinessWare %r-%r>' % (self.id, self.name)

    def to_json(self):
        json_obj = {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'price': self.price,
            'discount': float(self.discount),
            'discount_price': float(self.price*self.discount),
            'priority': self.priority,
            'description': self.description
        }
        return json_obj


# 商业上品订单
class BusinessWareOrder(db.Model):
    __tablename__ = 'business_ware_order'
    order_number = db.Column(db.String(32), primary_key=True, index=True, nullable=False)  # 订单编号
    buyer_godin_id = db.Column(db.String(32), db.ForeignKey('business_members.godin_id'))  # 购买者的国鼎ID
    ware_id = db.Column(db.String(32), db.ForeignKey('business_ware.id'))  # 商品ID
    pay_type = db.Column(db.SMALLINT, default=0)  # 0 微信, 1 支付宝, 2 其他
    ware_price = db.Column(db.Integer, nullable=False)  # 下单时的商品标价，单位为分
    discount = db.Column(db.DECIMAL(3, 2))  # 下单时的折扣信息
    discount_price = db.Column(db.Integer, nullable=False)  # 下单时的折后价格，单位为分
    status = db.Column(db.Integer, default=0, nullable=False)  # 订单状态， 0 未支付  1 已支付
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 订单创建时间
    pay_time = db.Column(db.DateTime())  # 订单支付时间
    start_time = db.Column(db.DateTime(), nullable=False)  # 商品有效起始时间
    end_time = db.Column(db.DateTime(), nullable=False)  # 商品有效结束时间
    key_record_id = db.Column(db.String(20), index=True, nullable=False, default='00000000000000')  # key操作表id

    def __repr__(self):
        return '<BusinessWareOrder %r>' % self.order_number

    def to_json(self, category, type_name):
        now_time = datetime.now()
        if self.end_time < now_time:
            ware_status = 0
        elif self.start_time <= now_time <= self.end_time:
            ware_status = 1
        else:
            ware_status = 2
        json_obj = {
            'order_number': self.order_number,
            'category': category,
            'pay_time': self.pay_time.strftime('%Y-%m-%d %H:%M:%S'),
            'ware_price': self.ware_price,
            'discount': float(self.discount),
            'discount_price': self.discount_price,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'ware_status': ware_status,
            'type_name': type_name,
            'buy_category': self.category
        }
        return json_obj


# 商业用户付费周统计
class BusinessPayWeekStatistics(db.Model):
    __tablename__ = 'business_pay_week_statistics'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, default=int(datetime.now().strftime('%Y')), nullable=False)
    week = db.Column(db.Integer, default=int(datetime.now().strftime('%W')), nullable=False)
    new_reg_count = db.Column(db.Integer, default=0)  # 新增付费人数
    new_pay_amount = db.Column(db.Integer, default=0)  # 新增付费额，单位为分
    old_not_pay_count = db.Column(db.Integer, default=0)  # 到期未续费人数
    old_pay_count = db.Column(db.Integer, default=0)  # 到期续费人数
    old_pay_amount = db.Column(db.Integer, default=0)  # 续费额, 单位为分
    income_amount = db.Column(db.Integer, default=0)  # 收入总额, 单位为分

    __table_args__ = (db.UniqueConstraint('year', 'week', name='uq_bus_pay_week_statistics_year_week'), )

    def __repr__(self):
        return '<BusinessPayWeekStatistics %r-%r>' % (self.year, self.week)


# 商业用户付费月统计
class BusinessPayMonthStatistics(db.Model):
    __tablename__ = 'business_pay_month_statistics'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, default=int(datetime.now().strftime('%Y')), nullable=False)
    month = db.Column(db.Integer, default=int(datetime.now().strftime('%m')), nullable=False)
    new_reg_count = db.Column(db.Integer, default=0)  # 新增付费人数
    new_pay_amount = db.Column(db.Integer, default=0)  # 新增付费额，单位为分
    old_not_pay_count = db.Column(db.Integer, default=0)  # 到期未续费人数
    old_pay_count = db.Column(db.Integer, default=0)  # 到期续费人数
    old_pay_amount = db.Column(db.Integer, default=0)  # 续费额, 单位为分
    income_amount = db.Column(db.Integer, default=0)  # 收入总额, 单位为分

    __table_args__ = (db.UniqueConstraint('year', 'month', name='uq_bus_pay_month_statistics_year_month'), )

    def __repr__(self):
        return '<BusinessPayWeekStatistics %r-%r>' % (self.year, self.month)


# 商业用户付费日统计
class BusinessPayDayStatistics(db.Model):
    __tablename__ = 'business_pay_day_statistics'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date(), default=datetime.today(), unique=True, nullable=False)
    new_reg_count = db.Column(db.Integer, default=0)  # 新增付费人数
    new_pay_amount = db.Column(db.Integer, default=0)  # 新增付费额，单位为分
    old_not_pay_count = db.Column(db.Integer, default=0)  # 到期未续费人数
    old_pay_count = db.Column(db.Integer, default=0)  # 到期续费人数
    old_pay_amount = db.Column(db.Integer, default=0)  # 续费额, 单位为分
    income_amount = db.Column(db.Integer, default=0)  # 收入总额, 单位为分

    def __repr__(self):
        return '<businessPayDayStatistics %r>' % self.date


# 智能好友池子
class BusinessPool(db.Model):
    __tablename__ = 'business_pool'
    id = db.Column(db.Integer, primary_key=True)
    we_id = db.Column(db.String(128), index=True, nullable=False)  # 微信id
    we_mark = db.Column(db.String(128), default='', nullable=False)  # 微信唯一标签
    count = db.Column(db.Integer, default=0, nullable=False)  # 记录被使用几次, 暂时没用

    def __repr__(self):
        return '<business_pool %r>' % self.id


# 智能好友池子1
class BusinessPoolOne(db.Model):
    __tablename__ = 'business_pool_one'
    id = db.Column(db.Integer, primary_key=True)
    we_id = db.Column(db.String(128), index=True, nullable=False)  # 微信id
    we_mark = db.Column(db.String(128), default='', nullable=False)  # 微信唯一标签
    count = db.Column(db.Integer, default=0, nullable=False)  # 记录被使用几次, 暂时没用

    def __repr__(self):
        return '<business_pool_one %r>' % self.id


# 秒通过的池子
class BusinessSecondPool(db.Model):
    __tablename__ = 'business_second_pool'
    id = db.Column(db.Integer, primary_key=True)
    we_id = db.Column(db.String(128), index=True, nullable=False)  # 微信id
    we_mark = db.Column(db.String(128), default='', nullable=False)  # 微信唯一标签
    count = db.Column(db.Integer, default=0, nullable=False)  # 记录被使用几次

    def __repr__(self):
        return '<business_second_pool %r>' % self.id


# 秒通过的池子1
class BusinessSecondPoolOne(db.Model):
    __tablename__ = 'business_second_pool_one'
    id = db.Column(db.Integer, primary_key=True)
    we_id = db.Column(db.String(128), index=True, nullable=False)  # 微信id
    we_mark = db.Column(db.String(128), default='', nullable=False)  # 微信唯一标签
    count = db.Column(db.Integer, default=0, nullable=False)  # 记录被使用几次

    def __repr__(self):
        return '<business_second_pool_one %r>' % self.id


# 秒通过用户使用过的池子, 暂时无用
class BusinessSecondHistory(db.Model):
    __tablename__ = 'business_second_history'
    id = db.Column(db.Integer, primary_key=True)
    we_id = db.Column(db.String(128), index=True, nullable=False)  # 微信id
    we_mark = db.Column(db.String(128), default='', nullable=False)  # 微信唯一标签
    count = db.Column(db.Integer, default=0, nullable=False)  # 记录被使用几次

    def __repr__(self):
        return '<business_second_history %r>' % self.id


# 秒通过用户使用过的池子, 暂时无用
class BusinessSecondOneHistory(db.Model):
    __tablename__ = 'business_second_one_history'
    id = db.Column(db.Integer, primary_key=True)
    we_id = db.Column(db.String(128), index=True, nullable=False)  # 微信id
    we_mark = db.Column(db.String(128), default='', nullable=False)  # 微信唯一标签
    count = db.Column(db.Integer, default=0, nullable=False)  # 记录被使用几次

    def __repr__(self):
        return '<business_second_one_history %r>' % self.id


# 优先级最高的添加者池子
class OnePool(db.Model):
    __tablename__ = 'one_pool'
    id = db.Column(db.Integer, primary_key=True)
    we_id = db.Column(db.String(128), index=True, nullable=False)  # 微信id
    we_mark = db.Column(db.String(128), default='', nullable=False)  # 微信id
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 创建时间

    def __repr__(self):
        return '<one_pool %r>' % self.id


# 添加好友历史记录
class FriendHistory(db.Model):
    __tablename__ = 'friend_history'
    id = db.Column(db.Integer, primary_key=True)
    active_we_id = db.Column(db.String(128), index=True, nullable=False)  # 主动添加者id
    passive_we_id = db.Column(db.String(128), index=True, nullable=False)  # 被动添加者id
    passive_mark = db.Column(db.String(128), default='', nullable=False)  # 被动添加微信唯一标签
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 创建时间

    def __repr__(self):
        return '<FriendHistory %r>' % self.id


# 数据库行级锁
class DataLock(db.Model):
    __tablename__ = 'data_lock'
    id = db.Column(db.Integer, primary_key=True)  # 1 优先级最高的池, 2 普通池字 3 秒通过
    count = db.Column(db.Integer, default=0, nullable=False)  # 此值多功能, 可以游标位置, 可以记录次数
    max_id = db.Column(db.Integer, default=0, nullable=False)  # 最大游标位置
    min_id = db.Column(db.Integer, default=0, nullable=False)  # 最小游标位置
    update_time = db.Column(db.Date, default=datetime.today())  # 记录日期 eg:2017-07-10

    def __repr__(self):
        return '<DataLock %r>' % self.id


# 客服微信表
class VSZL_Service(db.Model):
    __tablename__ = 'vszl_service'
    service_wx = db.Column(db.String(128), primary_key=True)
    nickname = db.Column(db.String(128), nullable=False)  # 微信昵称
    person_num_limit = db.Column(db.Integer, nullable=False)  # 每次添加的好友限制
    current_person_num = db.Column(db.Integer, nullable=False, default=0)  # 当前已添加人数

    def __repr__(self):
        return '<VSZL_Service %r>' % self.service_wx


# 客服微信和用户微信的映射关系表
class VSZL_Customer_Service(db.Model):
    __tablename__ = 'vszl_cus_ser'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_wx = db.Column(db.String(128), nullable=False, unique=True)  # 用户微信
    vszl_service = db.relationship('VSZL_Service')
    service_wx = db.Column(db.String(128), db.ForeignKey('vszl_service.service_wx'), nullable=False)  # 客服微信

    def __repr__(self):
        return '<VSZL_Customer_Service %r>' % self.id


# 免費体验期限
class Free_Experience_Days(db.Model):
    __tablename__ = 'free_experience_days'
    godin_id = db.Column(db.String(32), primary_key=True)
    first_time = db.Column(db.DateTime())  # 体验时间
    valid_time = db.Column(db.DateTime())  # 体验过期时间
    is_exper = db.Column(db.Integer, nullable=False, default=0)  # 是否已体验
    exper_count = db.Column(db.Integer, nullable=False, default=0)  # 体验次数

    def __repr__(self):
        return '<Free_Experience_Days %r>' % self.godin_id


# 渠道账户表
class ChannelAccount(db.Model):
    __tablename__ = 'channel_account'
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.String(6), unique=True)  # 渠道id
    channel_name = db.Column(db.String(32), unique=True, nullable=False)  # 渠道名称
    account_id = db.Column(db.String(12), unique=True, nullable=False)   # 账号
    password_hash = db.Column(db.String(128), default='')   # 密码
    channel_manager = db.Column(db.String(32), nullable=False)  # 渠道负责人
    content = db.Column(db.Text, default='')  # 备注
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 创建时间
    operator = db.Column(db.String(15), nullable=False)  # 操作人
    # key_record = db.relationship('KeyRecord', backref='key_record')

    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<ChannelAccount %r>' % self.account_id


# 账号绑定公众号的open_id关系
class AccountOpenIdBind(db.Model):
    __tablename__ = 'account_openid_bind'
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.String(12), nullable=False)  # 账号
    nick_name = db.Column(db.String(32), default='')   # 昵称
    wechat_open_id = db.Column(db.String(32), nullable=False)   # 微信openid
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)

    def __repr__(self):
        return '<AccountOpenIdBind %r>' % self.id


# 渠道账户的钱包
class Wallet(db.Model):
    __tablename__ = 'wallet'
    id = db.Column(db.Integer, primary_key=True)
    channel_account_id = db.Column(db.Integer, db.ForeignKey('channel_account.id'), index=True, nullable=False)#渠道账户主鍵id
    account_id = db.Column(db.String(12), unique=True, nullable=False)   # 渠道账号
    income = db.Column(db.DECIMAL(11, 2), default=0.00, nullable=False)  # 渠道账户的收入总金额 = withdraw_cash + balance
    all_divide = db.Column(db.DECIMAL(11, 2), default=0.00, nullable=False)  # 渠道账户和推广收入总金额
    gener_divide = db.Column(db.DECIMAL(11, 2), default=0.00, nullable=False)  # 推广收入总金额
    withdraw_cash = db.Column(db.DECIMAL(11, 2), default=0.00, nullable=False)  # 总的已经提现的金额
    frozen_money = db.Column(db.DECIMAL(11, 2), default=0.00, nullable=False)  # 冻结的资金，提现中
    balance = db.Column(db.DECIMAL(11, 2), default=0.00, nullable=False)  # 剩余总金额，包括冻结的资金
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)
    last_seen = db.Column(db.DateTime(), default=datetime.now, nullable=False)
    withdraw_applies = db.relationship('WithdrawCashApply', backref='wallet', lazy='dynamic')
    account = db.relationship('ChannelAccount', backref=backref('wallet', uselist=False), lazy='joined')

    def __repr__(self):
        return '<Wallet %r>' % self.id

    def ping(self):
        self.last_seen = datetime.now()
        db.session.add(self)


# 提现记录，当前账户只要有一条记录没处理就不会让提现第二次
class WithdrawCashApply(db.Model):
    __tablename__ = 'withdraw_cash_apply'
    id = db.Column(db.Integer, primary_key=True)
    order_num = db.Column(db.String(32), unique=True, index=True, nullable=False) # 订单号
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'))
    account_id = db.Column(db.String(12), nullable=False)  # 渠道账号
    we_open_id = db.Column(db.String(32), nullable=False)  # 提现的微信在公众号下的openid
    we_nick_name = db.Column(db.String(32), nullable=False)  # 微信昵称
    withdraw_type = db.Column(db.Integer, nullable=False, default=1)  # 1: 微信提现 2: 支付宝提现
    money = db.Column(db.DECIMAL(11, 2), nullable=False)  # 提现金额
    current_balance = db.Column(db.DECIMAL(11, 2), default=0.00, nullable=False)  # 当前余额
    status = db.Column(db.Integer, default=0, nullable=False)  # 0: 提现中, 1: 确认提现, 2: 拒绝提现
    trade_num = db.Column(db.String(32), default='')  # 打款后返回的交易号
    process_user = db.Column(db.String(32))  # 操作人
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False) # 创建时间
    last_time = db.Column(db.DateTime(), default=datetime.now, nullable=False) # 最近更新时间

    def __repr__(self):
        return '<WithdrawCashApply %r>' % self.order_num


# 昨日相应渠道账户销售数量，分成金额, 通过定时计算
class ChannelAccountStatistics(db.Model):
    __tablename__ = 'channel_account_statistics'
    id = db.Column(db.Integer, primary_key=True)
    record_time = db.Column(db.Date, default=datetime.today())  # 当日记录日期 eg:2017-07-10
    # channel_account_id = db.Column(db.Integer, index=True, nullable=False)  # 渠道账户id
    channel_account_id = db.Column(db.String(6), index=True, nullable=False)  # 渠道账户id
    account_id = db.Column(db.String(12), nullable=False)  # 渠道账号
    total_count = db.Column(db.SmallInteger, nullable=False, default=0)  # 显示昨日此渠道下账户会员（VIP与客多多等）被购买的次数。
    total_money = db.Column(db.DECIMAL(11, 2), default=0.00, nullable=False)  # 显示分成金额

    def __repr__(self):
        return '<ChannelAccountStatistics %r>' % self.id


# 按授权码创建记录(key_record 中id)进行每天的分成数据统计
class DivideDataStatistics(db.Model):
    __tablename__ = 'divide_data_statistics'
    id = db.Column(db.Integer, primary_key=True)
    record_time = db.Column(db.Date, default=datetime.today())  # 当日记录日期 eg:2017-07-10
    key_record_id = db.Column(db.String(14), index=True, nullable=False)  # key_record 中的id
    vip_people_count = db.Column(db.Integer, default=0, nullable=False)  # 会员购买人数
    vip_count = db.Column(db.Integer, default=0, nullable=False)  # 会员购买次数
    vip_divide_ratio = db.Column(db.DECIMAL(3, 2))  # 铂金会员分成比例
    vip_money = db.Column(db.DECIMAL(11, 2), default=0.00, nullable=False)  # 会员分成金额
    third_people_count = db.Column(db.Integer, default=0, nullable=False)  # 第三方购买人数 eg: 目前智能加粉会员，也就是客多多
    third_vip_count = db.Column(db.Integer, default=0, nullable=False)  # 第三方购买次数
    third_divide_ratio = db.Column(db.DECIMAL(3, 2))  # 商业会员分成比例,也就是客多多
    third_vip_money = db.Column(db.DECIMAL(11, 2), default=0.00, nullable=False)  # 第三方会员分成金额
    total_money = db.Column(db.DECIMAL(11, 2), default=0.00, nullable=False)  # 总的分成金额

    def __repr__(self):
        return '<DivideDataStatistics %r>' % self.id


# 批次总分成
class KeyRecordsStatistics(db.Model):
    __tablename__ = 'key_record_statistics'
    id = db.Column(db.Integer, primary_key=True)
    key_record_id = db.Column(db.String(14), db.ForeignKey('key_record.id'), index=True, nullable=False)  # 批次id
    channel_account_id = db.Column(db.Integer, db.ForeignKey('channel_account.id'), index=True, nullable=False)  # 渠道账户主鍵id
    income = db.Column(db.DECIMAL(11, 2), default=0.00, nullable=False)  # 批次总分成
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)
    last_seen = db.Column(db.DateTime(), default=datetime.now, nullable=False)
    account = db.relationship('ChannelAccount', backref=backref('key_record_statistics', uselist=False), lazy='joined')
    key_record = db.relationship('KeyRecord', backref=backref('key_record_statistics', uselist=False), lazy='joined')

    def ping(self):
        self.last_seen = datetime.now()
        db.session.add(self)

    def __repr__(self):
        return '<DivideDataStatistics %r>' % self.id


# 栏目每日每种商品分成信息
class VipDataStatistics(db.Model):
    __tablename__ = 'vip_data_statistics'
    id = db.Column(db.Integer, primary_key=True)
    record_time = db.Column(db.Date, default=datetime.today())  # 当日记录日期 eg:2017-07-10
    key_record_id = db.Column(db.String(14), index=True, nullable=False)  # key_record 中的id
    ware_name = db.Column(db.String(32), index=True, nullable=False)  # 商品类型
    vip_channel = db.Column(db.String(32), index=True, nullable=False)  # 栏目信息 普通会员 铂金会员
    discount_price = db.Column(db.Integer, nullable=False)  # 下单时的折后价格，单位为分
    vip_people_count = db.Column(db.Integer, default=0, nullable=False)  # 会员购买人数
    vip_count = db.Column(db.Integer, default=0, nullable=False)  # 会员购买次数
    vip_ratio = db.Column(db.DECIMAL(3, 2))  # 铂金会员分成比例
    vip_money = db.Column(db.DECIMAL(11, 2), default=0.00, nullable=False)  # 会员分成金额


class UserGeneralize(db.Model):
    __tablename__ = 'user_generalize'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    godin_id = db.Column(db.String(32), unique=True, nullable=False)  # 国鼎id
    phone_num = db.Column(db.String(11), unique=True, nullable=False)  # 手机号
    invite_link = db.Column(db.String(32), unique=True, nullable=False)  # 邀请链接的后缀标识
    invite_person_num = db.Column(db.Integer)  # 邀请人数
    register_person_num = db.Column(db.Integer)  # 注册人数
    pay_person_num = db.Column(db.Integer)  # 付款人数
    member_award = db.Column(db.Float(2))  # 会员收益, 单位分
    active_code_award = db.Column(db.Float(2))  # 激活码收益, 单位分
    account_balance = db.Column(db.Float(2))  # 余额, 单位分
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 创建时间

    def __init__(self, godin_id):
        self.godin_id = godin_id
        md = hashlib.md5()
        md.update(bytes(datetime.now().strftime("%Y%m%d%H%M%S") + godin_id, 'utf-8'))
        self.invite_link = md.hexdigest()[8:-8]

    def __repr__(self):
        return '<UserGeneralize %r>' % self.godin_id


class InviteInfo(db.Model):
    __tablename__ = 'invite_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    godin_id = db.Column(db.String(32), unique=True, nullable=False)  # 被邀请人的国鼎ID
    inviter_godin_id = db.Column(db.String(32), nullable=False)  # 邀请人的国鼎ID
    phone_num = db.Column(db.String(11), unique=True, nullable=False)  # 被邀请人的手机号
    create_time = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<InviteInfo %r>' % self.id


# 商业报告协议确定
class BiReportProtocol(db.Model):
    __tablename__ = 'bi_report_protocol'
    id = db.Column(db.Integer, primary_key=True)
    we_id = db.Column(db.String(128), index=True, nullable=False)
    status = db.Column(db.SmallInteger, default=0, nullable=False)  # 0 没有确定协议 1 确定使用数据协议
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 创建时间

    def __repr__(self):
        return '<BiReportProtocol %r>' % self.id


# 客户端引流报告数据
class BiReport(db.Model):
    __tablename__ = 'bi_report'
    id = db.Column(db.Integer, primary_key=True)
    record_time = db.Column(db.String(15))  # 记录日期 eg:2017-07-10
    we_id = db.Column(db.String(128), index=True, nullable=False)
    latent_consumer_index = db.Column(db.SmallInteger, default=0, nullable=False)  # 客源指数
    activite_consumer_index = db.Column(db.SmallInteger, default=0, nullable=False)  # 忠粉指数
    extend_work_heat = db.Column(db.SmallInteger, default=0, nullable=False)  # 推广指数
    sale_work_heat = db.Column(db.SmallInteger, default=0, nullable=False)  # 销售指数
    income_index = db.Column(db.SmallInteger, default=0, nullable=False)  # 收入指数
    pay_index = db.Column(db.SmallInteger, default=0, nullable=False)  # 成本指数
    v_webusiness_index = db.Column(db.SmallInteger, default=0, nullable=False)  # 经营指数
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 创建时间
    rank_index = db.Column(db.Integer, default=0, nullable=False)  # 创建时间

    def __repr__(self):
        return '<BiReport %r>' % self.id


# 客户端引流报告月数据
class BiMonthReport(db.Model):
    __tablename__ = 'bi_month_report'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, default=int(datetime.now().strftime('%Y')), nullable=False)
    month = db.Column(db.Integer, default=int(datetime.now().strftime('%m')), nullable=False)
    year_month = db.Column(db.Integer, default=0, nullable=False)  # 例如 2018-01 为201801 用于后续的排序
    we_id = db.Column(db.String(128), index=True, nullable=False)
    rank_index = db.Column(db.Integer, default=0, nullable=False)  # 排名
    latent_consumer_index = db.Column(db.SmallInteger, default=0, nullable=False)  # 潜在消费者指数
    activite_consumer_index = db.Column(db.SmallInteger, default=0, nullable=False)  # 活跃消费者指数
    extend_work_heat = db.Column(db.SmallInteger, default=0, nullable=False)  # 推广工作热度
    sale_work_heat = db.Column(db.SmallInteger, default=0, nullable=False)  # 销售工作热度
    income_index = db.Column(db.SmallInteger, default=0, nullable=False)  # 收入指数
    pay_index = db.Column(db.SmallInteger, default=0, nullable=False)  # 支出指数
    v_webusiness_index = db.Column(db.SmallInteger, default=0, nullable=False)  # 经营指数
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 创建时间

    def __repr__(self):
        return '<BiMonthReport %r>' % self.id


# 邀请素材
class FriendCircle(db.Model):
    __tablename__ = 'friend_circle'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)  # 内容
    picture1 = db.Column(db.String(256), default='')  # 宣传图片1
    picture2 = db.Column(db.String(256), default='')  # 宣传图片2
    picture3 = db.Column(db.String(256), default='')  # 宣传图片3
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)

    def __repr__(self):
        return '<FriendCircle %r>' % self.id


# 邀请者的 key 收益记录
class InviteEarnRecord(db.Model):
    __tablename__ = 'invite_earn_record'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    godin_id = db.Column(db.String(32), nullable=False)  # 国鼎ID
    channel_id = db.Column(db.String(6), nullable=False)  # 渠道id
    channel_name = db.Column(db.String(32), nullable=False)  # 渠道名称
    phone_num = db.Column(db.String(11), nullable=False)  # 手机号
    be_invited_phone = db.Column(db.String(11), nullable=False)  # 被邀请者的手机号
    key_id = db.Column(db.String(32), nullable=False)  # 授权码
    price = db.Column(db.Integer, nullable=False)  # 授权码价格, 单位分
    inviter_per = db.Column(db.Float(2), nullable=False)  # 邀请者分成比例
    channel_per = db.Column(db.Float(2), nullable=False)  # 渠道分成比例
    inviter_earn = db.Column(db.Float(2), nullable=False)  # 邀请者收益
    channel_earn = db.Column(db.Float(2), nullable=False)  # 渠道收益, 单位分
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)

    def __repr__(self):
        return '<InviteEarnRecord %r>' % self.id


# 邀请者的会员收益记录
class MemberEarnRecord(db.Model):
    __tablename__ = 'member_earn_record'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    godin_id = db.Column(db.String(32), nullable=False)  # 国鼎ID
    price = db.Column(db.Integer, nullable=False)  # 授权码价格, 单位分
    member_type = db.Column(db.SMALLINT, nullable=False)  # 会员种类 0 黄金会员 1 铂金会员
    member_name = db.Column(db.String(32), nullable=False)  # 会员类型 月卡 季卡...
    phone_num = db.Column(db.String(11), nullable=False)  # 手机号
    be_invited_phone = db.Column(db.String(11), nullable=False)  # 被邀请者的手机号
    member_divide = db.Column(db.Float(2), nullable=False)  # 会员分成比例
    member_earn = db.Column(db.Float(2), nullable=False)  # 会员收益, 单位分
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)

    def __repr__(self):
        return '<MemberEarnRecord %r>' % self.id


# 功能小红点
class FunctionHotDot(db.Model):
    __tablename__ = 'function_hot_dot'
    id = db.Column(db.Integer, primary_key=True)
    function_name = db.Column(db.String(128), default='')  # 功能名称
    function_spell = db.Column(db.String(128), default='')  # 功能名称拼音
    today_status = db.Column(db.SMALLINT, default=0)  # 今日小红点 0 不显示 1 显示
    tomorrow_status = db.Column(db.SMALLINT, default=0)  # 明日小红点 0 不显示 1 显示
    type = db.Column(db.SMALLINT, default=0)  # 0 分身 1 主应用

    def __repr__(self):
        return '<FunctionHotDot %r>' % self.id


# 语音盒子
class UploadVoice(db.Model):
    __tablename__ = 'upload_voice'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    voice_name = db.Column(db.String(32), nullable=False)  # 音频名称
    create_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)

    def __repr__(self):
        return '<UploadVoice %r>' % self.id


# 用户付款时间
class UserPayTime(db.Model):
    __tablename__ = 'user_pay_time'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone_num = db.Column(db.String(11), nullable=False)  # 用户手机号码
    pay_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)  # 支付时间
    status = db.Column(db.SMALLINT, nullable=False)  # 0 客多多 1 购买黄金铂金会员

    def __repr__(self):
        return '<UserPayTime %r>' % self.id
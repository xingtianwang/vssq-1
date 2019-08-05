#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: forms.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 16/9/27
# *************************************************************************
import re

from flask_wtf import Form
from flask_wtf.file import FileAllowed, FileRequired, FileField
from wtforms import SelectField, StringField, PasswordField, SubmitField, DateTimeField, \
    TextAreaField, DateField, IntegerField, FloatField, RadioField, SelectMultipleField, widgets
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, Email, ValidationError, Optional
from app import db, cache
import datetime
from app.api_1_0.models import ExceptionLog, FeedBack, DeviceInfo, UserMonthStatistics, MemberWare, VipType, \
    Channel, VipMembers, AgentStatistics, ActivateMembers, BusinessType, ChannelAccount
from app.auth.models import Role, AdminUser, Department, AdminLog
from app.config.config import Config
from app.manage.models import SpreadManager


class CreateAdminUserForm(Form):
    user_type = SelectField('用户类型', validators=[DataRequired(message='请选择用户类型')], coerce=int,
                            choices=[(Role.ADMIN, '管理员'), (Role.AUDITOR, '审计员'), (Role.USER, '一般用户')])
    user_department = SelectField('用户部门', validators=[DataRequired(message='请选择用户部门')], coerce=int,
                                  choices=[(Department.PM, '项目经理'), (Department.OPERATION, '运营部'),
                                           (Department.PRODUCTION, '产品部'), (Department.QA, '测试部'),
                                           (Department.DEVELOP, '研发部'), (Department.DEVELOP_SU, '研发部-开发者')])
    username = StringField('用户名', validators=[DataRequired(message='用户名不能为空'),
                                              Length(4, 20, message='用户名长度必须在4-20之间'),
                                              Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, '用户名包含非法字符')])
    email = StringField('邮箱', validators=[DataRequired(message='邮箱不能为空'), Email(message='邮箱格式错误')])
    password = PasswordField('密码', validators=[DataRequired(message='密码不能为空'),
                                               Length(8, 30, message='密码长度必须在8-30之间')])
    password2 = PasswordField('确认密码', validators=[DataRequired(message='确认密码不能为空'),
                                                  Length(8, 30, message='确认密码长度必须在8-30之间'),
                                                  EqualTo('password', message='两次密码输入不一致')])
    submit = SubmitField('添加')

    def validate_username(self, field):
        if AdminUser.query.filter_by(username=field.data).first() is not None:
            raise ValidationError('用户名已存在')

    def validate_email(self, field):
        if AdminUser.query.filter_by(email=field.data).first() is not None:
            raise ValidationError('邮箱已使用')


class AdminLogForm(Form):
    username_choice = [('all', '全部')] + \
                      [(username[0], username[0]) for username in db.session.query(AdminLog.username.distinct())]

    actions_choice = [('all', '全部')] + \
                     [(action[0], action[0]) for action in db.session.query(AdminLog.actions.distinct())]

    ip_choice = [('all', '全部')] + \
                [(ip[0], ip[0]) for ip in db.session.query(AdminLog.client_ip.distinct())]

    def query_username_factory():
        return [r[0] for r in AdminLog.query.with_entities(AdminLog.username).
            order_by(AdminLog.username.desc()).distinct().all()]

    def query_actions_factory():
        return [r[0] for r in AdminLog.query.with_entities(AdminLog.actions).
            order_by(AdminLog.actions.desc()).distinct().all()]

    def query_ip_factory():
        return [r[0] for r in AdminLog.query.with_entities(AdminLog.client_ip).
            order_by(AdminLog.client_ip.desc()).distinct().all()]

    def get_pk(obj):
        return obj

    username = QuerySelectField(allow_blank=True, label='用户名', query_factory=query_username_factory,
                                get_pk=get_pk, blank_text='-- 全部 --')
    actions = QuerySelectField(allow_blank=True, label='操作', query_factory=query_actions_factory,
                               get_pk=get_pk, blank_text='-- 全部 --')
    client_ip = QuerySelectField(allow_blank=True, label='登陆地址', query_factory=query_ip_factory,
                                 get_pk=get_pk, blank_text='-- 全部 --')

    start_time = DateTimeField('起始时间', validators=[Optional()])
    end_time = DateTimeField('终止时间', validators=[Optional()])
    submit = SubmitField('查询')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')


class UploadAppForm(Form):

    def query_spreader_factory():
        return [r[0] for r in SpreadManager.query.with_entities(SpreadManager.channelname).
            order_by(SpreadManager.id.asc()).distinct().all()]

    def get_pk(obj):
        return obj

    app_type = SelectField('应用类型', choices=[(key, val) for key, val in Config.APP_TYPE_DICT.items()],
                           coerce=int, default=4)
    wechat_version_name = StringField('微信版本名称')
    version_code = StringField('版本号')
    version_name = StringField('版本名称')
    upload_target = SelectField('上传文件目的', choices=[(0, "添加新文件"), (1, "更新文件")], coerce=int)
    spreader = QuerySelectField(allow_blank=False, label='推广人员', query_factory=query_spreader_factory,
                                get_pk=get_pk)
    min_frame_code = StringField('最小框架版本号')
    max_frame_code = StringField('最大框架版本号')
    upload_file = FileField('应用文件')
    update_msg = TextAreaField('更新内容', validators=[DataRequired(message='更新内容不能为空')])
    submit = SubmitField('提交')


class ExceptionLogForm(Form):

    def query_factory():
        return [r[0] for r in ExceptionLog.query.with_entities(ExceptionLog.app_version).
            order_by(ExceptionLog.app_version.desc()).distinct().all()]

    def query_os_version_factory():
        return [r[0] for r in ExceptionLog.query.with_entities(ExceptionLog.os_version).
            order_by(ExceptionLog.os_version.desc()).distinct().all()]

    def query_device_model_factory():
        return [r[0] for r in ExceptionLog.query.with_entities(ExceptionLog.device_model).
            order_by(ExceptionLog.device_model).distinct().all()]

    def get_pk(obj):
        return obj

    app_version = QuerySelectField(allow_blank=True, label='应用版本', query_factory=query_factory,
                                   get_pk=get_pk, blank_text='-- 全部 --')
    os_version = QuerySelectField(allow_blank=True, label='系统版本', query_factory=query_os_version_factory,
                                  get_pk=get_pk, blank_text='-- 全部 --')
    device_model = QuerySelectField(allow_blank=True, label='设备型号', query_factory=query_device_model_factory,
                                    get_pk=get_pk, blank_text='-- 全部 --')
    imei = StringField('IMEI', validators=[Optional()])
    submit = SubmitField('查询')


class FeedBackForm(Form):

    def query_os_version_factory():
        return [r[0] for r in db.session.query(FeedBack.os_version.distinct()).order_by(FeedBack.os_version.asc())]

    def query_device_factory_factory():
        return [r[0] for r in db.session.query(FeedBack.device_factory.distinct()).
            order_by(FeedBack.device_factory.asc())]

    def query_device_model_factory():
        return [r[0] for r in db.session.query(FeedBack.device_model.distinct()).
            order_by(FeedBack.device_model.asc())]

    def query_app_version_factory():
        return [r[0] for r in db.session.query(FeedBack.app_version.distinct()).
            order_by(FeedBack.app_version.asc())]

    def get_pk(obj):
        return obj

    imei = StringField('IMEI', validators=[Optional(), Length(14, 15, message='imei长度不合法')])
    os_version = QuerySelectField(allow_blank=True, label='系统版本', query_factory=query_os_version_factory,
                                  get_pk=get_pk, blank_text='-- 全部 --')
    dev_factory = QuerySelectField(allow_blank=True, label='厂商', query_factory=query_device_factory_factory,
                                   get_pk=get_pk, blank_text='-- 全部 --')
    dev_model = QuerySelectField(allow_blank=True, label='型号', query_factory=query_device_model_factory,
                                 get_pk=get_pk, blank_text='-- 全部 --')
    app_version = QuerySelectField(allow_blank=True, label='应用版本', query_factory=query_app_version_factory,
                                   get_pk=get_pk, blank_text='-- 全部 --')
    start_time = DateTimeField('起始时间', validators=[Optional()])
    end_time = DateTimeField('终止时间', validators=[Optional()])
    status = SelectField('状态', choices=[('-1', '全部'), ('0', '未回复'), ('1', '已回复')], default='-1')
    phone_num = StringField('用户帐号', validators=[Optional()])
    submit = SubmitField('查询')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')


class RegisterUserQueryForm(Form):

    @cache.cached(timeout=1800, key_prefix='reg_app_version')
    def query_app_version_factory():
        return [r[0] for r in db.session.query(DeviceInfo.app_version.distinct()).filter_by(status=1).
            order_by(DeviceInfo.app_version.asc())]

    @cache.cached(timeout=1800, key_prefix='reg_market')
    def query_market_factory():
        return [r[0] for r in db.session.query(DeviceInfo.market.distinct()).filter_by(status=1).
            order_by(DeviceInfo.market.asc())]

    def get_pk(obj):
        return obj

    phone_num = StringField('手机号', validators=[Optional()])
    imei = StringField('IMEI', validators=[Optional()])
    os_version = StringField('系统版本', validators=[Optional()])
    dev_factory = StringField('设备厂商', validators=[Optional()])
    dev_model = StringField('设备型号', validators=[Optional()])
    app_version = QuerySelectField(allow_blank=True, label='应用版本', query_factory=query_app_version_factory,
                                   get_pk=get_pk, blank_text='-- 全部 --')
    market = QuerySelectField(allow_blank=True, label='渠道', query_factory=query_market_factory,
                              get_pk=get_pk, blank_text='-- 全部 --')
    order_time = SelectField('时间属性', choices=[('create_time', '注册时间'), ('last_seen', '活跃时间')],
                             default='create_time')
    start_time = DateTimeField('起始时间', validators=[Optional()])
    end_time = DateTimeField('终止时间', validators=[Optional()])
    submit = SubmitField('查询')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')


class UnRegisterUserQueryForm(Form):

    @cache.cached(timeout=1800, key_prefix='unreg_app_version')
    def query_app_version_factory():
        return [r[0] for r in db.session.query(DeviceInfo.app_version.distinct()).filter_by(status=0).
            order_by(DeviceInfo.app_version.asc())]

    @cache.cached(timeout=1800, key_prefix='unreg_market')
    def query_market_factory():
        return [r[0] for r in db.session.query(DeviceInfo.market.distinct()).filter_by(status=0).
            order_by(DeviceInfo.market.asc())]

    def get_pk(obj):
        return obj

    imei = StringField('IMEI', validators=[Optional()])
    os_version = StringField('系统版本', validators=[Optional()])
    dev_factory = StringField('设备厂商', validators=[Optional()])
    dev_model = StringField('设备型号', validators=[Optional()])

    app_version = QuerySelectField(allow_blank=True, label='应用版本', query_factory=query_app_version_factory,
                                   get_pk=get_pk, blank_text='-- 全部 --')
    market = QuerySelectField(allow_blank=True, label='渠道', query_factory=query_market_factory,
                              get_pk=get_pk, blank_text='-- 全部 --')
    order_time = SelectField('时间属性', choices=[('create_time', '首次使用时间'), ('last_seen', '活跃时间')],
                             default='create_time')
    start_time = DateTimeField('起始时间', validators=[Optional()])
    end_time = DateTimeField('终止时间', validators=[Optional()])
    submit = SubmitField('查询')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')


class AddBlackListForm(Form):
    imei = StringField('imei', validators=[Length(14, 15, message='imei长度不合法')])
    submit = SubmitField('提交')


class AddWhiteImeiListForm(Form):
    imei = StringField('imei', validators=[Length(14, 15, message='imei长度不合法')])
    submit = SubmitField('提交')


class AvgUserStatisticsForm(Form):

    def query_market_factory():
        return [r[0] for r in db.session.query(DeviceInfo.market.distinct()).order_by(DeviceInfo.market.asc())]

    def query_year_factory():
        return [r[0] for r in db.session.query(UserMonthStatistics.year.distinct()).
                order_by(UserMonthStatistics.year.desc())]

    def get_pk(obj):
        return obj

    month_choice = [(month, month) for month in range(1, 13)]
    week_choice = [(week, week) for week in range(1, 53)]
    statistics_way = SelectField('统计方式', choices=[(1, '按月统计'), (2, '按周统计')], coerce=int, default=1)
    year = QuerySelectField(allow_blank=False, label='年份', query_factory=query_year_factory,
                            get_pk=get_pk)
    month = SelectField('月份', choices=month_choice, coerce=int)
    week = SelectField('周数', choices=week_choice, coerce=int)
    market = QuerySelectField(allow_blank=True, label='渠道', query_factory=query_market_factory,
                              get_pk=get_pk, blank_text='-- 全部 --')
    submit = SubmitField('提交')


class AddDutyManagerForm(Form):
    name = StringField('姓名', validators=[DataRequired(message='姓名不能为空'), Length(2, 15, message='长度不合法')])
    email = StringField('邮箱', validators=[DataRequired(message='邮箱不能为空'), Email(message='邮箱格式错误')])
    submit = SubmitField('添加')


class NextDayStayStatisticsForm(Form):
    date = DateField('日期', validators=[Optional()])
    submit = SubmitField('查询')


class AddSpreadManagerForm(Form):
    name = StringField('姓名', validators=[DataRequired(message='姓名不能为空'), Length(2, 15, message='长度不合法')])
    email = StringField('邮箱', validators=[DataRequired(message='邮箱不能为空'), Email(message='邮箱格式错误')])
    channel = StringField('渠道', validators=[DataRequired(message='渠道名称不能为空')])
    suffix = StringField('访问地址后缀', validators=[DataRequired(message='访问后缀不能为空')])
    submit = SubmitField('添加')


class ActivityForm(Form):
    number = StringField('活动编号', validators=[Optional()])
    name = StringField('活动名称', validators=[Optional()])
    status = SelectField('活动状态', choices=[(-1, '全部'), (0, '关闭'), (1, '开启')], coerce=int, default=-1)
    submit = SubmitField('查询')


class AddActivityForm(Form):
    number = SelectField('活动编号', choices=[('000003', '签到领会员')], default='000003')
    name = StringField('活动名称', validators=[DataRequired(message='活动名称不能为空'),
                                           Length(1, 15, message='活动名称长度最多为6')])
    award_period = IntegerField('领奖周期(天)', default=0)
    reward = IntegerField('VIP奖励(天)', default=0)
    photo = FileField('活动图片', validators=[DataRequired(message='活动图片不能为空'), FileRequired('请上传图片'),
                                          FileAllowed(['jpg', 'png'], '图片只能上传jpg, png格式')])
    link = StringField('活动链接', validators=[DataRequired(message='活动链接不能为空')])
    content = StringField('备注')
    title = StringField('分享标题')
    description = StringField('分享描述')
    share_photo = FileField('分享图片')
    share_link = StringField('分享链接')

    start_time = DateTimeField('起始时间', validators=[DataRequired(message='起始时间不能为空')])
    end_time = DateTimeField('终止时间', validators=[DataRequired(message='起始时间不能为空')])

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')
    submit = SubmitField('提交')


class EditActivityForm(Form):
    name = StringField('活动名称', validators=[DataRequired(message='活动名称不能为空'),
                                           Length(1, 15, message='活动名称长度最多为6')])
    award_period = IntegerField('领奖周期(天)', default=0)
    reward = IntegerField('VIP奖励(天)', default=0)
    photo = FileField('活动图片')
    link = StringField('活动链接', validators=[DataRequired(message='活动链接不能为空')])
    content = StringField('备注')
    title = StringField('分享标题')
    description = StringField('分享描述')
    share_photo = FileField('分享图片')
    share_link = StringField('分享链接')

    start_time = DateTimeField('起始时间', validators=[DataRequired(message='起始时间不能为空')])
    end_time = DateTimeField('终止时间', validators=[DataRequired(message='起始时间不能为空')])

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')
    submit = SubmitField('提交')


class SignDataActivityForm(Form):
    phone = StringField('手机号', validators=[Optional()])
    sort_type = SelectField('排序方式', choices=[(-1, '----'), (0, '领奖数降序'), (1, '领奖数升序')], coerce=int, default=-1)
    submit = SubmitField('查询')


class ActivityShareCodeCountForm(Form):
    phone_num = StringField('手机号', validators=[Optional()])
    sort_type = SelectField('排序方式', choices=[(0, '----'), (1, '已发送邀请'), (2, '成功注册')], coerce=int, default=0)
    submit = SubmitField('确定')


class ActivityRegisterInfoForm(Form):
    start_time = DateTimeField('起始时间', validators=[Optional()])
    end_time = DateTimeField('终止时间', validators=[Optional()])
    submit = SubmitField('确定')


class AddOpenScreenAdsForm(Form):
    name = StringField('广告名称', validators=[DataRequired(message='名称不能为空'), Length(2, 64, message='名称长度不合法')])
    position = SelectField('广告位置', choices=[
        (key, val) for key, val in Config.OPEN_SCREEN_ADS_POSITION.items()], coerce=int, default=0)
    source = SelectField('广告来源', choices=[
        (key, val) for key, val in Config.ADS_SOURCE.items()], coerce=int, default=0)
    charge_mode = SelectField('计费方式', choices=[(0, 'CPM')], coerce=int, default=0)
    unit_price = FloatField('单价')
    advertiser = StringField('合作商', validators=[DataRequired(message='合作商不能为空'),
                                                Length(2, 64, message='合作商长度不合法')])
    contacts = StringField('联系人', validators=[DataRequired(message='联系人不能为空'),
                                              Length(2, 64, message='联系人长度不合法')])
    contact_way = StringField('联系方式', validators=[DataRequired(message='联系方式不能为空'),
                                                  Length(2, 128, message='联系方式长度不合法')])
    number = StringField('广告编号')
    display_number = IntegerField('展示次数')
    skip_time = IntegerField('跳过倒计时')
    start_time = DateTimeField('起始时间', validators=[Optional()])
    end_time = DateTimeField('终止时间', validators=[Optional()])
    virtual_skip = RadioField('虚拟跳过功能', choices=[(0, '关闭'), (1, '开启')], coerce=int, default=0)
    control_click_rate = IntegerField('控制点击率(%)', default=0)
    skip_count = IntegerField('用户点击跳过次数', default=0)
    user_count = IntegerField('昨日活跃用户数', default=0)
    refresh_status = SelectField('刷广告开关状态', choices=[(0, '关闭'), (1, '开启')], coerce=int, default=0)
    morning_count = IntegerField('上午刷新次数 8:00 至 13：00', default=0)
    afternoon_count = IntegerField('下午刷新次数 13：00 至 18：00', default=0)
    night_count = IntegerField('晚上刷新次数 18：00 至 24:00', default=0)
    icon = FileField('添加广告图(仅限自有广告)')
    app_link = StringField('应用链接地址')
    submit = SubmitField('保存')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')


class QueryOpenScreenAdsForm(Form):
    name = StringField('广告名称', validators=[Optional()])
    position = SelectField('广告位置', choices=[(-1, '全部')] + [
        (key, val) for key, val in Config.OPEN_SCREEN_ADS_POSITION.items()], coerce=int, default=-1)
    source = SelectField('广告来源', choices=[(-1, '全部')] + [
        (key, val) for key, val in Config.ADS_SOURCE.items()], coerce=int, default=-1)
    status = SelectField('状态', choices=[(-1, '全部')] + [(0, '关闭'), (1, '开启')], coerce=int, default=-1)
    start_time = DateField('起始时间', validators=[Optional()])
    end_time = DateField('终止时间', validators=[Optional()])
    submit = SubmitField('查询')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        day = (field.data - self.start_time.data)
        day = day.days + 1
        if day > 30:
            raise ValidationError('查询天数不能大余30天')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')


class EditOpenScreenAdsForm(Form):
    name = StringField('广告名称', validators=[DataRequired(message='名称不能为空'), Length(2, 64, message='名称长度不合法')])
    position = SelectField('广告位置', choices=[
        (key, val) for key, val in Config.OPEN_SCREEN_ADS_POSITION.items()], coerce=int, default=0)
    source = SelectField('广告来源', choices=[
        (key, val) for key, val in Config.ADS_SOURCE.items()], coerce=int, default=0)
    charge_mode = SelectField('计费方式', choices=[(0, 'CPM')], coerce=int, default=0)
    unit_price = FloatField('单价')
    advertiser = StringField('合作商', validators=[DataRequired(message='合作商不能为空'),
                                                Length(2, 64, message='合作商长度不合法')])
    contacts = StringField('联系人', validators=[DataRequired(message='联系人不能为空'),
                                              Length(2, 64, message='联系人长度不合法')])
    contact_way = StringField('联系方式', validators=[DataRequired(message='联系方式不能为空'),
                                                  Length(2, 128, message='联系方式长度不合法')])
    display_number = IntegerField('展示次数')
    skip_time = IntegerField('跳过倒计时')
    start_time = DateTimeField('起始时间', validators=[Optional()])
    end_time = DateTimeField('终止时间', validators=[Optional()])
    virtual_skip = RadioField('虚拟跳过功能', choices=[(0, '关闭'), (1, '开启')], coerce=int, default=0)
    control_click_rate = IntegerField('控制点击率(%)', default=0)
    skip_count = IntegerField('用户点击跳过次数', default=0)
    user_count = IntegerField('昨日活跃用户数', default=0)
    refresh_status = SelectField('刷广告开关状态', choices=[(0, '关闭'), (1, '开启')], coerce=int, default=0)
    morning_count = IntegerField('上午刷新次数 8:00 至 13：00', default=0)
    afternoon_count = IntegerField('下午刷新次数 13：00 至 18：00', default=0)
    night_count = IntegerField('晚上刷新次数 18：00 至 24:00', default=0)
    icon = FileField('编辑广告图(仅限自有广告)')
    app_link = StringField('应用链接地址')
    submit = SubmitField('保存编辑')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')


class AddBannerAdsForm(Form):
    name = StringField('广告名称', validators=[DataRequired(message='广告名称不能为空')])
    position = SelectField('广告位置', choices=[
        (key, val) for key, val in Config.BANNER_ADS_POSITION.items()], coerce=int, default=0)
    source = SelectField('广告来源', choices=[
        (key, val) for key, val in Config.ADS_SOURCE.items()], coerce=int, default=0)
    charge_mode = SelectField('计费方式', choices=[(0, 'CPC')], coerce=int, default=0)
    unit_price = FloatField('广告单价', validators=[DataRequired(message='广告单价不能为空')])
    start_time = DateTimeField('起始时间', validators=[Optional()])
    end_time = DateTimeField('终止时间', validators=[Optional()])
    advertiser = StringField('合作商', validators=[DataRequired(message='合作商不能为空'),
                                                Length(2, 64, message='长度不合法')])
    contacts = StringField('联系人', validators=[DataRequired(message='联系人不能为空')])
    contact_way = StringField('联系方式', validators=[DataRequired(message='联系方式不能为空')])
    number = StringField('广告编号', validators=[DataRequired(message='编号不能为空')])
    display_number = IntegerField('展示次数', validators=[DataRequired(message='展示次数不能为空')])
    carousel = RadioField('是否轮播', choices=[(0, '不轮播'), (1, '轮播')], coerce=int, default=0)
    carousel_interval = IntegerField('轮播间隔')
    icon = FileField('添加广告图(仅限自有广告)')
    icon_dest_link = StringField('打开链接(仅限自有广告)')
    refresh_status = SelectField('刷广告开关状态', choices=[(0, '关闭'), (1, '开启')], coerce=int, default=0)
    user_count = IntegerField('昨日活跃用户数', default=0)
    morning_count = IntegerField('上午刷新次数 8:00 至 13：00', default=0)
    afternoon_count = IntegerField('下午刷新次数 13：00 至 18：00', default=0)
    night_count = IntegerField('晚上刷新次数 18：00 至 24:00', default=0)
    submit = SubmitField('保存')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')


class BannertInfoForm(Form):
    name = StringField('广告名称', validators=[Optional()])
    position = SelectField('广告位置', choices=[(-1, '全部')] + [
        (key, val) for key, val in Config.BANNER_ADS_POSITION.items()], coerce=int, default=-1)
    source = SelectField('广告来源', choices=[(-1, '全部')] + [
        (key, val) for key, val in Config.ADS_SOURCE.items()], coerce=int, default=-1)
    status = SelectField('状态', choices=[(-1, '全部'), (0, '关闭'), (1, '开启')], coerce=int, default=-1)
    start_time = DateField('起始时间', validators=[Optional()])
    end_time = DateField('终止时间', validators=[Optional()])
    submit = SubmitField('筛选')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        day = (field.data - self.start_time.data)
        day = day.days + 1
        if day > 30:
            raise ValidationError('查询天数不能大余30天')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')


class EditBannerAdsForm(Form):
    name = StringField('广告名称', validators=[DataRequired(message='广告名称不能为空')])
    position = SelectField('广告位置', choices=[
        (key, val) for key, val in Config.BANNER_ADS_POSITION.items()], coerce=int, default=0)
    source = SelectField('广告来源', choices=[
        (key, val) for key, val in Config.ADS_SOURCE.items()], coerce=int, default=0)
    charge_mode = SelectField('计费方式', choices=[(0, 'CPC')], coerce=int, default=0)
    unit_price = FloatField('广告单价', validators=[DataRequired(message='广告单价不能为空')])
    start_time = DateTimeField('起始时间', validators=[Optional()])
    end_time = DateTimeField('终止时间', validators=[Optional()])
    advertiser = StringField('合作商', validators=[DataRequired(message='合作商不能为空'),
                                                Length(2, 64, message='长度不合法')])

    contacts = StringField('联系人', validators=[DataRequired(message='联系人不能为空')])
    contact_way = StringField('联系方式', validators=[DataRequired(message='联系方式不能为空')])
    display_number = IntegerField('展示次数', validators=[DataRequired(message='展示次数不能为空')])
    carousel = RadioField('是否轮播', choices=[(0, '不轮播'), (1, '轮播')], coerce=int, default=0)
    carousel_interval = IntegerField('轮播间隔')
    icon = FileField('编辑广告图(仅限自有广告)')
    icon_dest_link = StringField('打开链接(仅限自有广告)')
    refresh_status = SelectField('刷广告开关状态', choices=[(0, '关闭'), (1, '开启')], coerce=int, default=0)
    user_count = IntegerField('昨日活跃用户数', default=0)
    morning_count = IntegerField('上午刷新次数 8:00 至 13：00', default=0)
    afternoon_count = IntegerField('下午刷新次数 13：00 至 18：00', default=0)
    night_count = IntegerField('晚上刷新次数 18：00 至 24:00', default=0)
    submit = SubmitField('保存')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')


class AppAnalysisForm(Form):
    sort_choice = [(0, '----'), (1, '总人数'), (2, '总人数占比'), (3, '启动次数'), (4, '平均启动次数'),
                   (5, '启动次数占比'), (6, '新增人数'), (7, '新增次数'), (8, '活跃人数'), (9, '启动时长'),
                   (10, '平均启动时长'), (11, '启动时长占比')]
    query_choices = [(0, '日'), (1, '周'), (2, '月'), (3, '季'), (4, '年')]
    app_name = StringField('名称', validators=[Optional()])
    sort_type = SelectField('排序方式', choices=sort_choice, coerce=int, default=0)
    query_type = SelectField('查询方式', choices=query_choices, coerce=int, default=0)
    submit = SubmitField('查询')


class AppPageAnalysisForm(Form):
    sort_choice = [(0, '----'), (1, '总人数'), (2, '总人数占比'), (3, '启动次数'), (4, '平均启动次数'),
                   (5, '启动次数占比'), (6, '新增人数'), (7, '新增次数'), (8, '活跃人数'), (9, '启动时长'),
                   (10, '平均启动时长'), (11, '启动时长占比')]
    app_name = StringField('名称', validators=[Optional()])
    sort_type = SelectField('排序方式', choices=sort_choice, coerce=int, default=0)
    submit = SubmitField('查询')


class AddMemberWareForm(Form):
    def query_channel_factory():
        return [r[0] for r in db.session.query(Channel.channel.distinct())]

    def query_category_factory():
        return [r[0] for r in db.session.query(VipType.name)]

    def get_pk(obj):
        return obj

    channel = QuerySelectField(allow_blank=True, label='渠道', query_factory=query_channel_factory,
                               get_pk=get_pk, blank_text='moren')
    category = QuerySelectField(allow_blank=False, label='VIP类型', query_factory=query_category_factory,
                                get_pk=get_pk)
    number = StringField('产品ID', validators=[DataRequired(message='产品ID不能为空')])
    name = StringField('VIP名称', validators=[DataRequired(message='VIP名称不能为空'),
                                            Length(0, 10, message='VIP名称不超过10个字')])
    description = TextAreaField('会员描述', validators=[DataRequired(message='会员描述不能为空'),
                                                    Length(0, 25, message='会员描述不超过25个字')])
    price = FloatField('会员标价', default=0)

    common_discount = FloatField('普通会员购买时折扣', default=0.0)
    gold_discount = FloatField('黄金会员购买时折扣', default=0.0)
    discount = FloatField('铂金会员购买时折扣', default=0.0)
    pay_price = FloatField('普通会员购买价格')
    gold_pay_price = FloatField('黄金会员购买价格')
    platinum_pay_price = FloatField('铂金会员购买价格')

    status = SelectField('状态', choices=[(0, '失效'), (1, '有效')], coerce=int, default=1)
    picture = FileField('会员推荐图标', validators=[Optional()])
    # ads_cate = SelectMultipleField('开屏广告类型', choices=[
    #     (key, val) for key, val in Config.EXTERNAL_ADS_CATEGORY.items()])
    submit = SubmitField('添加')


class EditMemberWareForm(Form):

    name = StringField('VIP名称', validators=[DataRequired(message='VIP名称不能为空'),
                                            Length(0, 10, message='VIP名称不超过10个字')])
    description = TextAreaField('会员描述', validators=[DataRequired(message='会员描述不能为空'),
                                                    Length(0, 25, message='会员描述不超过25个字')])
    price = FloatField('会员标价', validators=[DataRequired(message='会员标价不能为空')])

    common_discount = FloatField('普通会员购买时折扣', default=0.0)
    gold_discount = FloatField('黄金会员购买时折扣', default=0.0)
    discount = FloatField('铂金会员购买时折扣', default=0.0)

    status = SelectField('状态', choices=[(0, '失效'), (1, '有效')], coerce=int, default=1)
    picture = FileField('会员推荐图标', validators=[Optional()])
    # ads_cate = SelectMultipleField('开屏广告类型', choices=[
    #     (key, val) for key, val in Config.EXTERNAL_ADS_CATEGORY.items()])
    submit = SubmitField('提交')


class QueryMemberWareForm(Form):
    def query_channel_factory():
        return [r[0] for r in db.session.query(MemberWare.channel.distinct())]

    def query_category_factory():
        return [r[0] for r in db.session.query(VipType.name.distinct())]

    def get_pk(obj):
        return obj

    channel = QuerySelectField(allow_blank=True, label='渠道', query_factory=query_channel_factory,
                               get_pk=get_pk, blank_text='-- 全部 --')
    category = QuerySelectField(allow_blank=True, label='类型', query_factory=query_category_factory,
                                get_pk=get_pk, blank_text='-- 全部 --')
    status = SelectField('状态', choices=[(-1, '-- 全部 --'), (0, '失效'), (1, '有效')], coerce=int, default=-1)
    submit = SubmitField('查询')


class VipCategoryForm(Form):
    name = StringField('VIP类型')
    submit = SubmitField('查询')


class AddVipCategoryForm(Form):
    name = StringField('类型名称', validators=[DataRequired(message='类型名称不能为空')])
    days = IntegerField('类型天数', validators=[DataRequired(message='类型天数不能为空')])
    submit = SubmitField('添加')


class VipChannelForm(Form):
    channel_name = StringField('渠道名称')
    submit = SubmitField('查询')


class AddVipChannelForm(Form):
    channel = StringField('渠道', validators=[DataRequired(message='渠道不能为空'),
                                            Regexp('^[A-Za-z0-9-]+$', 0, '渠道包仅适合(字母数字-)且不能存在中文')])
    channel_name = StringField('渠道名称', validators=[DataRequired(message='渠道名称不能为空')])
    submit = SubmitField('添加')


class WareStatisticsForm(Form):

    def query_channel_factory():
        return [r[0] for r in db.session.query(MemberWare.channel.distinct())]

    def query_category_factory():
        return [r[0] for r in db.session.query(VipType.name.distinct())]

    def get_pk(obj):
        return obj

    channel = QuerySelectField(allow_blank=True, label='渠道', query_factory=query_channel_factory,
                               get_pk=get_pk,  blank_text='moren')
    category = QuerySelectField(allow_blank=True, label='类型', query_factory=query_category_factory,
                                get_pk=get_pk, blank_text='-- 全部 --')
    name = StringField('产品名称')
    number = StringField('产品ID')
    start_time = DateTimeField('起始时间', validators=[Optional()])
    end_time = DateTimeField('终止时间', validators=[Optional()])

    submit = SubmitField('查询')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')


class VipMembersForm(Form):

    def query_channel_factory():
        return [r[0] for r in db.session.query(VipMembers.channel.distinct())]

    def query_category_factory():
        return [r[0] for r in db.session.query(VipType.name.distinct())]

    def get_pk(obj):
        return obj

    channel = QuerySelectField(allow_blank=True, label='渠道', query_factory=query_channel_factory,
                               get_pk=get_pk,  blank_text='-- 全部 --')
    category_choice = [(-1, '-----'), (0, '付费'), (1, '活动'), (2, '手动添加'), (3, '其他')]
    phone_num = StringField('手机号', validators=[Optional()])
    category = SelectField('会员种类', choices=category_choice, coerce=int, default=-1)
    cur_pay_cate = QuerySelectField(allow_blank=True, label='类型', query_factory=query_category_factory,
                                    get_pk=get_pk, blank_text='-- 全部 --')
    status = SelectField('状态', choices=[(-1, '-----'), (0, '已过期'), (1, '正常')], coerce=int, default=-1)
    start_time = DateTimeField('开始时间', validators=[Optional()])
    end_time = DateTimeField('结束时间', validators=[Optional()])
    submit = SubmitField('查询')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')


class MemberForm(Form):
    def query_channel_factory():
        return [r[0] for r in db.session.query(DeviceInfo.market.distinct())]

    def get_pk(obj):
        return obj

    channel = QuerySelectField(allow_blank=True, label='渠道', query_factory=query_channel_factory,
                               get_pk=get_pk,  blank_text='-- 全部 --')
    phone_num = StringField('手机号', validators=[Optional()])
    submit = SubmitField('查询')


class VipMembersDetailsForm(Form):

    def query_category_factory():
        return [r[0] for r in db.session.query(VipType.name.distinct())]

    def get_pk(obj):
        return obj
    pay_type_choice = [(-1, '----'), (0, '微信'), (1, '支付宝'), (2, '其他')]
    add_choice = [(-1, '-----'), (0, '付费'), (1, '活动'), (2, '手动添加'), (3, '其他')]

    pay_type = SelectField('支付方式', choices=pay_type_choice, coerce=int, default=-1)
    category = QuerySelectField(allow_blank=True, label='VIP类型', query_factory=query_category_factory,
                                           get_pk=get_pk, blank_text='-----')
    add_type = SelectField('会员途径', choices=add_choice, coerce=int, default=-1)
    status = SelectField('会员状态', choices=[(-1, '-----'), (0, '已过期'), (1, '服务中'), (2, '未使用')],
                         coerce=int, default=-1)
    order_number = StringField('订单编号', validators=[Optional()])
    start_time = DateTimeField('开始时间', validators=[Optional()])
    end_time = DateTimeField('结束时间', validators=[Optional()])
    submit = SubmitField('查询')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')


class VipServiceProtocolForm(Form):
    content = TextAreaField('会员服务协议', validators=[DataRequired(message='会员服务协议不能为空')])
    submit = SubmitField('提交')


class VipPayStatisticsForm(Form):
    today_now = datetime.date.today()
    year_choice = [(year, year) for year in range(today_now.year - 5, today_now.year + 1)]
    month_choice = [(month, month) for month in range(1, 13)]
    week_choice = [(week, week) for week in range(1, 53)]

    statistics_way = SelectField('统计方式', choices=[(1, '按月统计'), (2, '按周统计'), (3, '按日统计')],
                                 coerce=int, default=1)

    if today_now.month == 1:
        year_s = today_now.year - 1
        year_e = today_now.year - 1
        month_s = 1
        month_e = 12
    else:
        year_s = today_now.year - 1
        year_e = today_now.year
        month_s = 12 + (today_now.month - 12)
        month_e = today_now.month - 1
    week_now = today_now.isocalendar()[1]
    if week_now - 4 > 1:
        year_s_w = today_now.year
        year_e_w = today_now.year
        week_s = week_now - 4
        week_e = week_now - 1
    else:
        year_s_w = today_now.year - 1
        year_e_w = today_now.year
        week_s = 52 + (week_now - 4)
        week_e = week_now - 1

    start_year_m = SelectField('开始年份', choices=year_choice, coerce=int, default=year_s)
    end_year_m = SelectField('结束年份', choices=year_choice, coerce=int, default=year_e)
    start_year_w = SelectField('开始年份', choices=year_choice, coerce=int, default=year_s_w)
    end_year_w = SelectField('结束年份', choices=year_choice, coerce=int, default=year_e_w)
    month_start = SelectField('开始月', choices=month_choice, coerce=int, default=month_s)
    month_end = SelectField('结束月', choices=month_choice, coerce=int, default=month_e)
    week_start = SelectField('开始周', choices=week_choice, coerce=int, default=week_s)
    week_end = SelectField('结束周', choices=week_choice, coerce=int, default=week_e)
    day_start = DateField('开始日', validators=[Optional()])
    day_end = DateField('结束日', validators=[Optional()])
    submit = SubmitField('查询')

    def validate_day_start(self, field):
        if field.data is not None and self.day_end.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_day_end(self, field):
        if field.data is not None and self.day_start.data is None:
            raise ValidationError('起始时间不能为空')
        if field.data is not None and self.day_start.data is not None and \
                (self.day_start.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')

    def validate_end_year_m(self, field):
        if field.data is not None and self.start_year_m.data is not None and \
                (self.start_year_m.data > field.data):
            raise ValidationError('结束年份不能小于起始年份')

    def validate_end_year_w(self, field):
        if field.data is not None and self.start_year_w.data is not None and \
                (self.start_year_w.data > field.data):
            raise ValidationError('结束年份不能小于起始年份')

    def validate_month_end(self, field):
        if self.start_year_m.data == self.end_year_m.data and self.statistics_way.data == 1:
            if self.month_start.data > field.data:
                raise ValidationError('结束月份不能小于起始月份')

    def validate_week_end(self, field):
        if self.start_year_w.data == self.end_year_w.data and self.statistics_way.data == 2:
            if self.week_start.data > field.data:
                raise ValidationError('结束周数不能小于起始周数')


class CommunicationGroupForm(Form):
    v_group_number = StringField('微商神器交流群', validators=[DataRequired(message='微商神器交流群不能为空')])
    v_group_key = StringField('微商神器交流群key', validators=[DataRequired(message='微商神器交流群key不能为空')])

    submit = SubmitField('提交')


# 针对第三方SDK广告的访问统计
class OpenScreenAdsDataForm(Form):
    name = StringField('广告名称', validators=[Optional()])
    position = SelectField('广告位置', choices=[(-1, '全部')] + [
        (key, val) for key, val in Config.OPEN_SCREEN_ADS_POSITION.items()], coerce=int, default=-1)
    source = SelectField('广告来源', choices=[(-1, '全部')] + [
        (key, val) for key, val in Config.ADS_SOURCE.items()], coerce=int, default=-1)
    status = SelectField('状态', choices=[(-1, '全部')] + [(0, '关闭'), (1, '开启')], coerce=int, default=-1)
    start_time = DateField('起始时间', validators=[Optional()])
    end_time = DateField('终止时间', validators=[Optional()])
    submit = SubmitField('查询')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        day = (field.data - self.start_time.data)
        day = day.days + 1
        if day > 30:
            raise ValidationError('查询天数不能大余30天')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')


class InteractiveAdsForm(Form):
    name = StringField('广告名称', validators=[DataRequired(message='名称不能为空'), Length(2, 64, message='长度不合法')])
    position = SelectField('广告位置', choices=[
        (key, val) for key, val in Config.INTERACTIVE_ADS_POSITION.items()], coerce=int, default=0)
    source = SelectField('广告来源', choices=[
        (key, val) for key, val in Config.INTERACTIVE_ADS_SOURCE.items()], coerce=int, default=0)
    charge_mode = SelectField('计费方式', choices=[(0, 'CPC')], coerce=int, default=0)
    icon = FileField('添加广告图标')
    third_link = StringField('打开链接')
    user_count = IntegerField('昨日活跃用户数', default=0)
    refresh_status = SelectField('刷广告开关状态', choices=[(0, '关闭'), (1, '开启')], coerce=int, default=0)
    morning_count = IntegerField('上午刷新次数 8:00 至 13：00', default=0)
    afternoon_count = IntegerField('下午刷新次数 13：00 至 18：00', default=0)
    night_count = IntegerField('晚上刷新次数 18：00 至 24:00', default=0)
    submit = SubmitField('保存')


class QueryInteractiveAdsForm(Form):
    name = StringField('广告名称', validators=[Optional()])
    position = SelectField('广告位置', choices=[(-1, '全部')] + [
        (key, val) for key, val in Config.INTERACTIVE_ADS_POSITION.items()], coerce=int, default=-1)
    source = SelectField('广告来源', choices=[(-1, '全部')] + [
        (key, val) for key, val in Config.INTERACTIVE_ADS_SOURCE.items()], coerce=int, default=-1)
    status = SelectField('状态', choices=[(-1, '全部')] + [(0, '关闭'), (1, '开启')], coerce=int, default=-1)
    start_time = DateField('起始时间', validators=[Optional()])
    end_time = DateField('终止时间', validators=[Optional()])
    submit = SubmitField('查询')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        day = (field.data - self.start_time.data)
        day = day.days + 1
        if day > 30:
            raise ValidationError('查询天数不能大余30天')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')


class EditInteractiveAdsForm(Form):
    name = StringField('广告名称', validators=[DataRequired(message='名称不能为空'), Length(2, 64, message='长度不合法')])
    position = SelectField('广告位置', choices=[
        (key, val) for key, val in Config.INTERACTIVE_ADS_POSITION.items()], coerce=int, default=0)
    source = SelectField('广告来源', choices=[
        (key, val) for key, val in Config.INTERACTIVE_ADS_SOURCE.items()], coerce=int, default=0)
    charge_mode = SelectField('计费方式', choices=[(0, 'CPC')], coerce=int, default=0)
    icon = FileField('添加广告图标')
    third_link = StringField('打开链接')
    user_count = IntegerField('昨日活跃用户数', default=0)
    refresh_status = SelectField('刷广告开关状态', choices=[(0, '关闭'), (1, '开启')], coerce=int, default=0)
    morning_count = IntegerField('上午刷新次数 8:00 至 13：00', default=0)
    afternoon_count = IntegerField('下午刷新次数 13：00 至 18：00', default=0)
    night_count = IntegerField('晚上刷新次数 18：00 至 24:00', default=0)
    submit = SubmitField('保存编辑')


# 广告渠道和版本控制
class AdsConfigForm(Form):
    channel = StringField('渠道', validators=[Optional()])
    version = SelectField('版本', choices=[(-1, '全部'), (0, '历史版本'), (1, '最新版本')], coerce=int, default=-1)
    submit = SubmitField('筛选')


# 广告默认图
class AdsIconForm(Form):
    position = SelectField('广告位置', choices=[
        (key, val) for key, val in Config.ADS_ICON.items()], coerce=int, default=1)
    icon = FileField('广告默认图')
    jump_link = StringField('广告默认跳转链接')
    submit = SubmitField('保存')


# 设置开屏广告展示策略
class OpenStrategyForm(Form):
    display_number = IntegerField('广告展示策略', default=0)
    submit = SubmitField('提交')


class AddAvatarAppForm(Form):
    number = IntegerField('编号', validators=[DataRequired(message='编号不能为空')])
    upload_file = FileField('应用文件')
    update_msg = TextAreaField('更新内容', validators=[DataRequired(message='更新内容不能为空')])
    status = SelectField('状态', choices=[(1, '强制更新'), (0, '普通更新')], coerce=int, default=0)
    submit = SubmitField('添加')


class MakeAvatarForm(Form):
    app_name = StringField('应用名称', validators=[DataRequired(message='应用名称不能为空')])
    submit = SubmitField('添加')


class AvatarMakeAnalysisForm(Form):
    app_name = StringField('名称')
    start_time = DateField('开始时间', validators=[Optional()])
    end_time = DateField('结束时间', validators=[Optional()])
    submit = SubmitField('查询')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')


class ActivityShareForm(Form):
    act_id = StringField('活动编号', validators=[Optional()])
    submit = SubmitField('查询')


class InviteForm(Form):
    phone_num = StringField('手机号', validators=[Optional()])
    submit = SubmitField('查询')


class ShareForm(Form):
    phone_num = StringField('手机号', validators=[Optional()])
    start_time = DateTimeField('起始时间', validators=[Optional()])
    end_time = DateTimeField('终止时间', validators=[Optional()])
    submit = SubmitField('查询')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')


class AddKeyForm(Form):

    def __init__(self, *args, **kwargs):
        super(AddKeyForm, self).__init__(*args, **kwargs)
        self.channel_id.choices = [(-1, '请选择渠道')] +[(v.id, v.channel_id) for v in ChannelAccount.query.filter(ChannelAccount.id != 1).all()]

    channel_id = SelectField('渠道ID', coerce=int)
    count = IntegerField('创建数量', validators=[DataRequired(message='创建数量不能为空')])
    vip_time = IntegerField('激活码时长', validators=[DataRequired(message='激活码时长不能为空')])
    vip_ad_time = IntegerField('赠送铂金会员', validators=[Optional()])
    vip_gold_ad_time = IntegerField('赠送黄金会员', validators=[Optional()])
    vip_ratio = FloatField('会员分成比例', default=0.0)
    business_ratio = FloatField('第三方分成比例', default=0.0)
    content = TextAreaField('备注',  validators=[DataRequired(message='备注不能为空'),
                                               Length(1, 20, message='备注长度必须在1-20之间')])
    submit = SubmitField('创建')


class EditKeyForm(Form):
    vip_ad_time = IntegerField('免广告', validators=[Optional()])
    # expire_time = DateField('有效期截止', validators=[DataRequired(message='有效期截止不能为空')])
    content = TextAreaField('备注',  validators=[DataRequired(message='备注不能为空'),
                                               Length(1, 20, message='备注长度必须在1-20之间')])
    submit = SubmitField('确定')


class KeyRecordForm(Form):
    oeprator = StringField('操作人', validators=[Optional()])
    content = StringField('备注检索', validators=[Optional()])
    start_time = DateTimeField('创建起始时间', validators=[Optional()])
    end_time = DateTimeField('创建终止时间', validators=[Optional()])
    channel_id = StringField('渠道ID', validators=[Optional()])
    channel_name = StringField('渠道名称', validators=[Optional()])
    submit = SubmitField('查询')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('创建终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('创建起始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('创建终止时间不能小于起始时间')


class KeyDetailForm(Form):
    status = SelectField('状态', choices=[(-1, '全部'), (0, '未激活'), (1, '已激活'), (2, '过期'), (3, '使用结束')],
                         coerce=int, default=-1)
    submit = SubmitField('查询')


class OrderKeyForm(Form):
    status = SelectField('状态', choices=[(-1, '全部'), (0, '未激活'), (1, '已激活'), (2, '过期'), (3, '使用结束')],
                         coerce=int, default=-1)
    o_id = StringField('订单编号')
    submit = SubmitField('查询')


class ChannelUploadAppForm(Form):

    def query_spreader_factory():
        return [r[0] for r in SpreadManager.query.with_entities(SpreadManager.channelname).order_by(
            SpreadManager.id.asc()).distinct().all()]

    def get_pk(obj):
        return obj

    app_type = SelectField('应用类型', choices=[(key, val) for key, val in Config.APP_TYPE_DICT.items() if key != 100],
                           coerce=int, default=8)
    wechat_version_name = StringField('微信版本名称')
    version_code = StringField('版本号')
    version_name = StringField('版本名称')
    upload_target = SelectField('上传文件目的', choices=[(0, "添加新文件"), (1, "更新文件")], coerce=int)
    spreader = QuerySelectField(allow_blank=False, label='推广人员', query_factory=query_spreader_factory,
                                get_pk=get_pk)
    min_frame_code = StringField('最小框架版本号')
    max_frame_code = StringField('最大框架版本号')
    upload_file = FileField('应用文件')
    update_msg = TextAreaField('更新内容', validators=[DataRequired(message='更新内容不能为空')])
    status = SelectField('状态', choices=[(0, '普通更新'), (1, '强制更新')], coerce=int, default=0)
    submit = SubmitField('提交')


class KeyChannelForm(Form):

    def query_channel():
        return [r[0] for r in Channel.query.with_entities(Channel.channel).distinct().all()]

    def get_pk(obj):
        return obj

    channel_name = StringField('渠道名称')
    channel = QuerySelectField(allow_blank=False, label='渠道', query_factory=query_channel, get_pk=get_pk)
    price = FloatField('授权码价格', validators=[DataRequired(message='授权码价铬不能为空')])
    msg = TextAreaField('说明', validators=[DataRequired(message='说明不能为空')])
    status = SelectField('状态', choices=[(0, '无效状态'), (1, '立即生效')], coerce=int, default=0)
    submit = SubmitField('提交')


class EditKeyChannelForm(Form):

    channel_name = StringField('渠道名称')
    price = FloatField('授权码价格', validators=[DataRequired(message='授权码价铬不能为空')])
    msg = TextAreaField('说明', validators=[DataRequired(message='说明不能为空')])
    status = SelectField('状态', choices=[(0, '无效状态'), (1, '立即生效')], coerce=int, default=0)
    submit = SubmitField('提交')


class GetKeyChannelForm(Form):

    channel_name = StringField('渠道名称')
    submit = SubmitField('查询')


class GetKeyInfoForm(Form):

    key_id = StringField('KEY-ID')
    submit = SubmitField('查询')


class AddKeyImeiForm(Form):

    imei = StringField('imei', validators=[DataRequired(message='imei不能为空')])
    submit = SubmitField('提交')


class GetImeiInfoForm(Form):
    imei = StringField('imei')
    submit = SubmitField('查询')


class WeKeyRecordForm(Form):
    phone_num = StringField('手机号', validators=[Optional()])
    operator = StringField('操作人', validators=[Optional()])
    we_key_number = StringField('key记录编号', validators=[Optional()])
    start_time = DateTimeField('创建起始时间', validators=[Optional()])
    end_time = DateTimeField('创建终止时间', validators=[Optional()])
    submit = SubmitField('查询')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('创建终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('创建起始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('创建终止时间不能小于起始时间')


class WeKeyDetailForm(Form):
    status = SelectField('状态', choices=[(-1, '全部'), (0, '未激活'), (1, '已激活'), (2, '过期'), (3, '使用结束')],
                         coerce=int, default=-1)
    submit = SubmitField('查询')


class NoticeForm(Form):
    oeprator = StringField('操作人', validators=[Optional()])
    start_time = DateTimeField('开始时间', validators=[Optional()])
    end_time = DateTimeField('结束时间', validators=[Optional()])
    submit = SubmitField('查询')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('结束时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('开始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('结束时间不能小于开始时间')


class AddNoticeForm(Form):
    notice_type = SelectField('通知类型', choices=[(0, '文字通知'), (1, '图片通知')], coerce=int, default=0)
    icon = FileField('通知图片')
    icon_link = StringField('图片跳转地址', validators=[Optional()])
    time_quantum = SelectField('通知时间段', choices=[(0, '0：00 ~ 5：59'), (1, '6：00 ~ 11：59'), (2, '12：00 ~ 17：59'),
                                                 (3, '18：00 ~ 23：59')], coerce=int, default=0)
    title = StringField('通知标题', validators=[DataRequired(message='通知标题不能为空'),
                                            Length(1, 12, message='通知标题长度最多为12')])
    content = TextAreaField('通知内容', validators=[Optional()])
    remarks = TextAreaField('备注', validators=[Optional()])
    start_time = DateField('开始时间', validators=[DataRequired(message='开始时间不能为空')])
    end_time = DateField('结束时间', validators=[DataRequired(message='结束时间不能为空')])

    notice_user = SelectMultipleField(
        label="不通知用户",
        choices=(
            (1, '普通用户(用户会员最高等级为普通会员)'),
            (2, '黄金用户(用户会员最高等级为黄金会员)'),
            (4, '铂金用户(用户会员最高等级为铂金会员)'),
            (8, '客多多VIP用户(用户为客多多会员用户)'),

        ),
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput(),
        coerce=int
    )
    wx = TextAreaField('添加微信号', validators=[Optional()])
    submit = SubmitField('确定')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('结束时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('开始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('结束时间不能小于开始时间')


class ExportKeyForm(Form):
    count = IntegerField('创建数量', validators=[DataRequired(message='创建数量不能为空')])
    # expire_time = DateField('有效期截止', validators=[DataRequired(message='有效期截止不能为空')])
    vip_time = IntegerField('会员时长', validators=[DataRequired(message='会员时长不能为空')])
    content = TextAreaField('备注',  validators=[DataRequired(message='备注不能为空'),
                                               Length(1, 20, message='备注长度必须在1-20之间')])
    vip_ad_time = IntegerField('免广告', validators=[Optional()])
    upload_file = FileField('上传文件', validators=[DataRequired(message='文件不能为空'), FileRequired('请上传文件'),
                                                FileAllowed(['xlsx', 'xls'], '文件只能上传xlxs, xls')])

    submit = SubmitField('创建')


class AppProtocolForm(Form):
    content = TextAreaField('软件服务使用协议', validators=[DataRequired(message='软件服务使用协议不能为空')])
    submit = SubmitField('提交')


class KeyForm(Form):
    key = StringField('key', validators=[Optional()])
    submit = SubmitField('查询')


class ActKeyStForm(Form):
    start_year_m = IntegerField('开始年份', validators=[Optional()])
    end_year_m = IntegerField('结束年份', validators=[Optional()])
    month_start = IntegerField('开始月份', validators=[Optional()])
    month_end = IntegerField('结束月份', validators=[Optional()])
    submit = SubmitField('查询')

    def validate_end_year_m(self, field):
        if field.data is not None and self.start_year_m.data is not None and \
                (self.start_year_m.data > field.data):
            raise ValidationError('结束年份不能小于起始年份')

    def validate_month_end(self, field):
        if self.start_year_m.data == self.end_year_m.data:
            if self.month_start.data > field.data:
                raise ValidationError('结束月份不能小于开始月份')


class AgentStForm(Form):

    def query_name_factory():
        return [r[0] for r in db.session.query(AgentStatistics.name.distinct())]

    def get_pk(obj):
        return obj

    name = QuerySelectField(allow_blank=True, label='查询', query_factory=query_name_factory,
                            get_pk=get_pk, blank_text='全部')
    submit = SubmitField('查询')


class AddAgentForm(Form):
    name = StringField('代理名称', validators=[DataRequired(message='代理名称不能为空')])
    submit = SubmitField('添加')


class AppVersionCheckForm(Form):
    start_time = DateTimeField('开始时间', validators=[Optional()])
    end_time = DateTimeField('结束时间', validators=[Optional()])
    submit = SubmitField('查询')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('结束时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('开始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('结束时间不能小于开始时间')


class AddVersionCheckForm(Form):
    versioncode = StringField('versioncode', validators=[DataRequired(message='versioncode不能为空')])
    versionname = StringField('versionname', validators=[DataRequired(message='versionname不能为空')])
    md5 = StringField('md5', validators=[DataRequired(message='md5不能为空')])
    build_time = StringField('build_time', validators=[DataRequired(message='build_time不能为空')])
    build_rev = StringField('build_rev', validators=[DataRequired(message='build_rev不能为空')])
    submit = SubmitField('提交')


class AddMembersForm(Form):
    upload_file = FileField('上传文件', validators=[DataRequired(message='文件不能为空'), FileRequired('请上传文件'),
                                           FileAllowed(['xlsx', 'xls'], '文件只能上传xlxs, xls')])
    vip_id = StringField('会员ID', validators=[DataRequired(message='会员ID不能为空')])
    submit = SubmitField('提交')


class ActMemebrForm(Form):

    def query_channel_factory():
        return [r[0] for r in db.session.query(ActivateMembers.channel.distinct())]

    def get_pk(obj):
        return obj

    phone_num = StringField('手机号', validators=[Optional()])
    channel = QuerySelectField(allow_blank=True, label='渠道', query_factory=query_channel_factory,
                              get_pk=get_pk, blank_text='全部')
    vip_type = SelectField('添加方式', choices=[(-1, '全部'), (0, '手动添加'), (1, '活动添加')], coerce=int, default=-1)
    status = SelectField('是否激活', choices=[(-1, '全部'), (0, '未激活'), (1, '已激活')], coerce=int, default=-1)
    start_time = DateTimeField('起始时间', validators=[Optional()])
    end_time = DateTimeField('终止时间', validators=[Optional()])
    submit = SubmitField('查询')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')


class CheckKeyForm(Form):
    key = StringField('Key-ID', validators=[Optional()])
    submit = SubmitField('查询')


class BusinessCategoryForm(Form):
    name = StringField('商业VIP类型')
    submit = SubmitField('查询')


class AddBusinessCategoryForm(Form):
    name = StringField('类型名称', validators=[DataRequired(message='类型名称不能为空')])
    days = IntegerField('类型天数', validators=[DataRequired(message='类型天数不能为空')])
    submit = SubmitField('添加')


class AddBusinessWareForm(Form):

    def query_category_factory():
        return [r[0] for r in db.session.query(BusinessType.name)]

    def get_pk(obj):
        return obj

    category = QuerySelectField(allow_blank=False, label='商业VIP类型', query_factory=query_category_factory,
                                get_pk=get_pk)
    number = StringField('产品ID', validators=[DataRequired(message='产品ID不能为空')])
    name = StringField('VIP名称', validators=[DataRequired(message='VIP名称不能为空'),
                                            Length(0, 10, message='VIP名称不超过10个字')])
    description = TextAreaField('会员描述', validators=[DataRequired(message='会员描述不能为空'),
                                                    Length(0, 25, message='会员描述不超过25个字')])
    price = FloatField('会员标价', default=0)
    pay_price = FloatField('会员购买价格')
    discount = FloatField('会员折扣', default=0.0)
    status = SelectField('状态', choices=[(0, '失效'), (1, '有效')], coerce=int, default=1)
    picture = FileField('会员推荐图标', validators=[Optional()])
    submit = SubmitField('添加')


class EditBusinessWareForm(Form):

    name = StringField('VIP名称', validators=[DataRequired(message='VIP名称不能为空'),
                                            Length(0, 10, message='VIP名称不超过10个字')])
    description = TextAreaField('会员描述', validators=[DataRequired(message='会员描述不能为空'),
                                                    Length(0, 25, message='会员描述不超过25个字')])
    price = FloatField('会员标价', validators=[DataRequired(message='会员标价不能为空')])
    discount = FloatField('会员折扣', default=0.0)
    pay_price = FloatField('会员购买价格')
    status = SelectField('状态', choices=[(0, '失效'), (1, '有效')], coerce=int, default=1)
    picture = FileField('会员推荐图标', validators=[Optional()])
    # ads_cate = SelectMultipleField('开屏广告类型', choices=[
    #     (key, val) for key, val in Config.EXTERNAL_ADS_CATEGORY.items()])
    submit = SubmitField('提交')


class QueryBusinessWareForm(Form):

    def query_category_factory():
        return [r[0] for r in db.session.query(BusinessType.name.distinct())]

    def get_pk(obj):
        return obj

    category = QuerySelectField(allow_blank=True, label='类型', query_factory=query_category_factory,
                                get_pk=get_pk, blank_text='-- 全部 --')
    status = SelectField('状态', choices=[(-1, '-- 全部 --'), (0, '失效'), (1, '有效')], coerce=int, default=-1)
    submit = SubmitField('查询')


class BusStatisticsForm(Form):
    def query_category_factory():
        return [r[0] for r in db.session.query(BusinessType.name.distinct())]

    def get_pk(obj):
        return obj

    category = QuerySelectField(allow_blank=True, label='类型', query_factory=query_category_factory,
                                get_pk=get_pk, blank_text='-- 全部 --')
    name = StringField('产品名称')
    number = StringField('产品ID')
    start_time = DateTimeField('起始时间', validators=[Optional()])
    end_time = DateTimeField('终止时间', validators=[Optional()])

    submit = SubmitField('查询')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')


class BusMembersForm(Form):

    phone_num = StringField('手机号', validators=[Optional()])
    status = SelectField('状态', choices=[(-1, '-----'), (0, '已过期'), (1, '正常')], coerce=int, default=-1)
    start_time = DateTimeField('开始时间', validators=[Optional()])
    end_time = DateTimeField('结束时间', validators=[Optional()])
    submit = SubmitField('查询')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')


class BusinessForm(Form):
    phone_num = StringField('手机号', validators=[Optional()])
    submit = SubmitField('查询')


class BusMembersDetailsForm(Form):

    def query_category_factory():
        return [r[0] for r in db.session.query(BusinessType.name.distinct())]

    def get_pk(obj):
        return obj
    pay_type_choice = [(-1, '----'), (0, '微信'), (1, '支付宝'), (2, '其他')]

    pay_type = SelectField('支付方式', choices=pay_type_choice, coerce=int, default=-1)
    category = QuerySelectField(allow_blank=True, label='VIP类型', query_factory=query_category_factory,
                                           get_pk=get_pk, blank_text='-----')
    status = SelectField('会员状态', choices=[(-1, '-----'), (0, '已过期'), (1, '服务中'), (2, '未使用')],
                         coerce=int, default=-1)
    order_number = StringField('订单编号', validators=[Optional()])
    start_time = DateTimeField('开始时间', validators=[Optional()])
    end_time = DateTimeField('结束时间', validators=[Optional()])
    submit = SubmitField('查询')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')


class BusPayStatisticsForm(Form):
    today_now = datetime.date.today()
    year_choice = [(year, year) for year in range(today_now.year - 5, today_now.year + 1)]
    month_choice = [(month, month) for month in range(1, 13)]
    week_choice = [(week, week) for week in range(1, 53)]

    statistics_way = SelectField('统计方式', choices=[(1, '按月统计'), (2, '按周统计'), (3, '按日统计')],
                                 coerce=int, default=1)

    if today_now.month == 1:
        year_s = today_now.year - 1
        year_e = today_now.year - 1
        month_s = 1
        month_e = 12
    else:
        year_s = today_now.year - 1
        year_e = today_now.year
        month_s = 12 + (today_now.month - 12)
        month_e = today_now.month - 1
    week_now = today_now.isocalendar()[1]
    if week_now - 4 > 1:
        year_s_w = today_now.year
        year_e_w = today_now.year
        week_s = week_now - 4
        week_e = week_now - 1
    else:
        year_s_w = today_now.year - 1
        year_e_w = today_now.year
        week_s = 52 + (week_now - 4)
        week_e = week_now - 1

    start_year_m = SelectField('开始年份', choices=year_choice, coerce=int, default=year_s)
    end_year_m = SelectField('结束年份', choices=year_choice, coerce=int, default=year_e)
    start_year_w = SelectField('开始年份', choices=year_choice, coerce=int, default=year_s_w)
    end_year_w = SelectField('结束年份', choices=year_choice, coerce=int, default=year_e_w)
    month_start = SelectField('开始月', choices=month_choice, coerce=int, default=month_s)
    month_end = SelectField('结束月', choices=month_choice, coerce=int, default=month_e)
    week_start = SelectField('开始周', choices=week_choice, coerce=int, default=week_s)
    week_end = SelectField('结束周', choices=week_choice, coerce=int, default=week_e)
    day_start = DateField('开始日', validators=[Optional()])
    day_end = DateField('结束日', validators=[Optional()])
    submit = SubmitField('查询')

    def validate_day_start(self, field):
        if field.data is not None and self.day_end.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_day_end(self, field):
        if field.data is not None and self.day_start.data is None:
            raise ValidationError('起始时间不能为空')
        if field.data is not None and self.day_start.data is not None and \
                (self.day_start.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')

    def validate_end_year_m(self, field):
        if field.data is not None and self.start_year_m.data is not None and \
                (self.start_year_m.data > field.data):
            raise ValidationError('结束年份不能小于起始年份')

    def validate_end_year_w(self, field):
        if field.data is not None and self.start_year_w.data is not None and \
                (self.start_year_w.data > field.data):
            raise ValidationError('结束年份不能小于起始年份')

    def validate_month_end(self, field):
        if self.start_year_m.data == self.end_year_m.data and self.statistics_way.data == 1:
            if self.month_start.data > field.data:
                raise ValidationError('结束月份不能小于起始月份')

    def validate_week_end(self, field):
        if self.start_year_w.data == self.end_year_w.data and self.statistics_way.data == 2:
            if self.week_start.data > field.data:
                raise ValidationError('结束周数不能小于起始周数')


class AddFriendsForm(Form):
    add_user = FileField('添加者', validators=[DataRequired(message='添加者文件不能为空'), FileRequired('请上传文件'),
                                            FileAllowed(['xlsx', 'xls'], '文件只能上传xlxs, xls')])
    by_add_user = FileField('被添加者', validators=[DataRequired(message='被添加者文件不能为空'), FileRequired('请上传文件'),
                                                FileAllowed(['xlsx', 'xls'], '文件只能上传xlxs, xls')])
    capita_add = IntegerField('人均添加', validators=[DataRequired(message='人均添加不能为空')])
    add_count = IntegerField('每日添加数量', validators=[DataRequired(message='每日添加数量不能为空')])
    submit = SubmitField('确定')


class FreeVipDaysForm(Form):
    days = IntegerField('免费会员天数', validators=[Optional()])
    submit = SubmitField('确定')


class FreeVipForm(Form):
    phone_num = StringField('手机号', validators=[Optional()])
    start_time = DateTimeField('开始时间', validators=[Optional()])
    end_time = DateTimeField('结束时间', validators=[Optional()])
    submit = SubmitField('查询')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')


class BusRecommendForm(Form):
    picture = FileField('显示图片', validators=[DataRequired(message='显示图片不能为空'), FileRequired('请上传显示图片'),
                                            FileAllowed(['png', 'jpg'], '文件只能上传png, jpg')])
    ware_id = StringField('商品ID', validators=[DataRequired(message='商品ID不能为空')])
    tip_time = IntegerField('提示时间', validators=[DataRequired(message='提示时间不能为空')])
    submit = SubmitField('提交')


class SecondDaysForm(Form):
    days = IntegerField('秒通过添加天数设置', validators=[Optional()])
    count = IntegerField('秒通过添加人数设置', validators=[Optional()])
    submit = SubmitField('确定')


class BusAssistantForm(Form):
    nickname = StringField('微信号昵称', validators=[DataRequired(message='微信昵称不能为空')])
    submit_search = SubmitField('搜索')


class AddAssistantForm(Form):
    service_wx = StringField('客服微信号', validators=[DataRequired(message='客服微信号不能为空')])
    nickname = StringField('客服微信昵称', validators=[DataRequired(message='客服微信昵称不能为空')])
    person_num_limit = StringField('添加数量', validators=[DataRequired(message='添加数量不能为空')])
    submit = SubmitField('提交')


class SetGZHForm(Form):
    we_public = StringField('公众号', validators=[DataRequired(message='公众号不能为空')])
    link = StringField('跳转链接', validators=[Optional()])
    submit = SubmitField('提交')


class AddLinkForm(Form):
    link = StringField('跳转链接', validators=[Optional()])
    submit = SubmitField('提交')


class FreeExperienceForm(Form):
    days = StringField('免费体验周期（天）', validators=[DataRequired(message='体验周期不能为空')])
    submit = SubmitField('确定')


class ChannelAccountForm(Form):
    channel_name = StringField('渠道名称', validators=[DataRequired(message='渠道名称不能为空')])
    account = StringField('账号', validators=[DataRequired(message='账号不能为空'),
                                            # Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, '用户名包含非法字符'),
                                            Length(6, 12, message='账号长度必须在6-12之间')
                                            ])
    channel_manager = StringField('渠道负责人', validators=[DataRequired(message='渠道负责人不能为空')])
    content = TextAreaField('备注',  validators=[Length(1, 20, message='备注长度必须在1-20之间')])
    submit = SubmitField('确定')


class GetAccountInfoForm(Form):
    channel_name = StringField('渠道名称')
    channel_manager = StringField('渠道负责人')
    submit = SubmitField('搜索')


class EditChannelAccountForm(Form):
    channel_manager = StringField('渠道负责人', validators=[DataRequired(message='渠道负责人不能为空')])
    content = TextAreaField('备注', validators=[Length(1, 20, message='备注长度必须在1-20之间')])
    submit = SubmitField('确定修改')


# 渠道数据表单
class ChannelDataForm(Form):
    channel_id = StringField('渠道ID', validators=[Optional()])
    channel_name = StringField('渠道名称', validators=[Optional()])
    submit = SubmitField('搜索')


# (2, '激活数量'),
# 渠道数据批次详情
class ChannelDataDetailForm(Form):
    order_by = SelectField('排序', choices=[(0, '默认'), (1, '授权码总数'),  (3, '总分成')], coerce=int, default=0)
    submit = SubmitField('搜索')


# 每个批次每天分成详情
class DayChannelDataDetailForm(Form):

    start_time = DateField('开始时间', validators=[Optional()])
    end_time = DateField('结束时间', validators=[Optional()])
    submit = SubmitField('搜索')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('结束时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('开始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('结束时间不能小于开始时间')


# 各种vip每天分成详情
class DayVipDetailForm(Form):

    channel = StringField('栏目', validators=[Optional()])
    ware_type = StringField('类型名称', validators=[Optional()])
    submit = SubmitField('搜索')


class FunctionVideoForm(Form):
    function_name = StringField('功能名称')
    submit_search = SubmitField('搜索')


class AddVideoForm(Form):
    function_name = StringField('功能名称', validators=[DataRequired(message='功能名称不能为空')])
    video_url = FileField('视频介绍', validators=[FileAllowed(["mp4"], '只能上传 mp4 格式的视频文件'),
                                                   FileRequired('文件未选择！')])
    comment = StringField('备注')
    submit = SubmitField('提交')


class EditVideoForm(Form):
    function_name = StringField('功能名称', validators=[DataRequired(message='功能名称不能为空')])
    video_url = FileField('视频介绍', validators=[FileAllowed(["mp4"], '只能上传 mp4 格式的视频文件')])
    comment = StringField('备注')
    submit = SubmitField('提交')


class SetFunctionForm(Form):
    function_name = StringField('功能名称', validators=[DataRequired(message='功能名称不能为空')])
    submit = SubmitField('提交')


class MicroStoreForm(Form):
    link = StringField('链接地址', validators=[DataRequired(message='链接地址不能为空')])
    submit = SubmitField('提交')


class PhoneForm(Form):
    phone_num = StringField('手机号', validators=[DataRequired(message='手机号不能为空')])
    submit_search = SubmitField('搜索')

    def validate_phone_num(self, field):
        phone = field.data.strip()
        if not str(phone).isdigit():
            raise ValidationError("手机号格式错误")
        # ret = re.match(r"^1[3456789]\d{9}$", phone)
        # if not ret:
        #     raise ValidationError("手机号格式错误")


class MemberDivideForm(Form):
    divide = StringField('会员分成比例', validators=[DataRequired(message='分成比例不能为空')])
    submit = SubmitField('提交')

    def validate_divide(self, field):
        try:
            divide = eval(field.data.strip())
        except Exception:
            raise ValidationError('分成比例必须是数值型')
        else:
            if divide < 0 or divide > 1:
                raise ValidationError('分成比例只能在 0 - 1 之间')


class MemberDetailForm(Form):
    start_time = DateTimeField('开始时间', validators=[Optional()])
    end_time = DateTimeField('结束时间', validators=[Optional()])

    submit = SubmitField('查询')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('结束时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('开始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('结束时间不能小于开始时间')


# 商业智能报告
class BIProtocolForm(Form):
    content = TextAreaField('服务条款', validators=[DataRequired(message='服务条款不能为空')])
    submit = SubmitField('提交')


class FcInfoForm(Form):
    start_time = DateTimeField('起始时间', validators=[Optional()])
    end_time = DateTimeField('终止时间', validators=[Optional()])
    submit = SubmitField('查询')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')


class AddFcContentForm(Form):
    content = TextAreaField('内容', validators=[DataRequired(message='内容不能为空'),
                                              Length(1, 500, message='内容长度必须在1-500字以内')])
    picture1 = FileField('宣传图片1', validators=[FileAllowed(['jpg', 'png'], '图片只能上传jpg, png格式')])
    picture2 = FileField('宣传图片2', validators=[FileAllowed(['jpg', 'png'], '图片只能上传jpg, png格式')])
    picture3 = FileField('宣传图片3', validators=[FileAllowed(['jpg', 'png'], '图片只能上传jpg, png格式')])
    submit = SubmitField('提交')


class EditFcContentForm(Form):
    content = TextAreaField('内容', validators=[DataRequired(message='内容不能为空'),
                                              Length(1, 500, message='内容长度必须在1-500字以内')])
    picture1 = FileField('宣传图片1', validators=[FileAllowed(['jpg', 'png'], '图片只能上传jpg, png格式')])
    picture2 = FileField('宣传图片2', validators=[FileAllowed(['jpg', 'png'], '图片只能上传jpg, png格式')])
    picture3 = FileField('宣传图片3', validators=[FileAllowed(['jpg', 'png'], '图片只能上传jpg, png格式')])
    status1 = SelectField('是否删除宣传图片1', choices=[(0, '删除'), (1, '不删除')], coerce=int, default=1)
    status2 = SelectField('是否删除宣传图片2', choices=[(0, '删除'), (1, '不删除')], coerce=int, default=1)
    status3 = SelectField('是否删除宣传图片3', choices=[(0, '删除'), (1, '不删除')], coerce=int, default=1)
    submit = SubmitField('确认修改')


class ActiveIntroduceForm(Form):
    active_intro = TextAreaField('活动说明', validators=[DataRequired(message='活动说明不能为空')])
    submit = SubmitField('提交')


class EveryWashForm(Form):
    link = StringField('链接地址', validators=[DataRequired(message='链接地址不能为空')])
    submit = SubmitField('提交')


class PrivacyProtocolForm(Form):
    content = TextAreaField('微商指数隐私协议', validators=[DataRequired(message='微商指数隐私协议不能为空')])
    submit = SubmitField('提交')


class ActiveCodeForm(Form):
    channel_id = StringField('渠道ID', validators=[Optional()])
    invite_phone = StringField('邀请人手机号', validators=[Optional()])
    phone = StringField('被邀请人手机号', validators=[Optional()])
    submit = SubmitField('查询')

    def validate_invite_phone(self, field):
        phone = field.data.strip()
        if not str(phone).isdigit():
            raise ValidationError("手机号格式错误")

    def validate_phone(self, field):
        phone = field.data.strip()
        if not str(phone).isdigit():
            raise ValidationError("手机号格式错误")


class AddInviteCodeForm(Form):
    inviter_divide = StringField('邀请者分成比例', validators=[DataRequired(message='邀请者分成比例不能为空')])
    channel_divide = StringField('渠道分成比例', validators=[DataRequired(message='渠道分成比例不能为空')])
    submit = SubmitField('提交')

    def validate_inviter_divide(self, field):
        try:
            divide = eval(field.data.strip())

        except Exception:
            raise ValidationError('分成比例必须是数值型')
        else:
            if divide < 0 or divide > 1:
                raise ValidationError('分成比例只能在 0 - 1 之间')

    def validate_channel_divide(self, field):
        try:
            divide = eval(field.data.strip())
        except Exception:
            raise ValidationError('分成比例必须是数值型')
        else:
            if divide < 0 or divide > 1:
                raise ValidationError('分成比例只能在 0 - 1 之间')


class AlterBalanceForm(Form):
    phone_num = StringField('手机号', validators=[Optional()])
    balance = StringField('当前余额', validators=[Optional()])
    type = SelectField('修改类型', choices=[(0, "增加余额"), (1, "减少余额")], coerce=int, default=1)
    amount = StringField('修改数额', validators=[DataRequired(message='修改数额不能为空')])
    comment = StringField('备注', validators=[DataRequired(message='备注不能为空')])
    submit = SubmitField('确认修改')

    def validate_amount(self, field):
        amount = field.data.strip()
        if not str(amount).isdigit():
            raise ValidationError("修改数额只能为整数")
        if float(amount) > float(self.balance.data) and self.type.data == 1:
            raise ValidationError("减少金额不能大于余额")


class FunctionHotDotForm(Form):
    function_name = StringField('功能名称', validators=[Optional()])
    function_locate = SelectField('功能位置', choices=[(-1, "全部"), (0, "倒三角"), (1, "主应用")], coerce=int, default=-1)
    submit_search = SubmitField('搜索')


class AlterDivideForm(Form):
    channel_id = StringField('渠道ID', validators=[Optional()])
    channel_name = StringField('渠道名称', validators=[Optional()])
    all_divide = StringField('总分成', validators=[Optional()])
    type = SelectField('修改类型', choices=[(0, "增加分成"), (1, "减少分成")], coerce=int, default=1)
    amount = StringField('修改数额', validators=[DataRequired(message='修改数额不能为空')])
    comment = StringField('备注', validators=[DataRequired(message='备注不能为空')])
    submit = SubmitField('确认修改')

    def validate_amount(self, field):
        amount = field.data.strip()
        if not str(amount).isdigit():
            raise ValidationError("修改数额只能为整数")
        if float(amount) > float(self.all_divide.data) and self.type.data == 1:
            raise ValidationError("减少数额不能大于总分成")


class UserPayTimeForm(Form):

    phone_num = StringField('手机号', validators=[Optional()])
    start_time = DateTimeField('开始时间', validators=[Optional()])
    end_time = DateTimeField('结束时间', validators=[Optional()])
    submit = SubmitField('查询')

    def validate_start_time(self, field):
        if field.data is not None and self.end_time.data is None:
            raise ValidationError('终止时间不能为空')

    def validate_end_time(self, field):
        if field.data is not None and self.start_time.data is None:
            raise ValidationError('起始时间不能为空')
        if field.data is not None and self.start_time.data is not None and \
                (self.start_time.data > field.data):
            raise ValidationError('终止时间不能小于起始时间')


class AppealEditForm(Form):
    content = TextAreaField('内容', validators=[DataRequired(message='内容不能为空'),
                                              Length(1, 20, message='内容长度必须在1-200字以内')])

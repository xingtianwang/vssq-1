#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: views.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 16/9/23
# *************************************************************************
import datetime
import json
import time
import os
import uuid

import math
from collections import OrderedDict

from flask import current_app, jsonify
from flask import flash
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user, login_required
import flask_excel as excel
from os.path import getsize
from PIL import Image
import xlrd

from sqlalchemy import func, distinct, or_, and_ , desc
from sqlalchemy.sql import label
from werkzeug.utils import redirect, secure_filename
from app.api_1_0.apktool.conversion_apk import format_apk
from app import db, celery, cache, redis
from app import helper
from app.api_1_0.apktool.tool import decompile
from app.api_1_0.models import AppVersion, AppList, FeedBack, ExceptionLog, DeviceInfo, UserInfo, GodinAccount, \
    Activity, OpenScreenAds, BannerAds, BannerAdsStatistics, \
    OpenScreenSimulateData, OpenScreenAdsStatistics, VipMembers, MemberWareOrder, MemberWare, VipPayMonthStatistics, \
    VipPayWeekStatistics, VipPayDayStatistics, CommunicationGroup, OpenScreenAdsData, InteractiveAds, \
    InteractiveAdsStatistics, VipType, ServiceProtocol, BannerConfig, Channel, BannerRefreshData, OpenConfig, \
    InteractiveConfig, AdsIcon, AvatarVersion, WeAvatar, ActivateMembers, ShareCode, ShareCount, KeyRecord, Key, \
    UserKeyRecord, KeyOrder, ChannelVersion, KeyChannel, SignRecord, SignData, SysNotice, ImeiVip, ActKeyStatistics, \
    AgentStatistics, Agent, AppVersionCheck, BusinessType, BusinessWare, BusinessWareOrder, BusinessMembers, \
    BusinessPayMonthStatistics, BusinessPayWeekStatistics, BusinessPayDayStatistics, OnePool, DataLock, \
    BusinessGiveStatistics, BusinessRecommend, VSZL_Service, VSZL_Customer_Service, ChannelAccount, \
    KeyRecordsStatistics, DivideDataStatistics, ChannelAccountStatistics, Wallet, VipDataStatistics, UserGeneralize, \
    InviteInfo, FriendCircle, MemberEarnRecord, InviteEarnRecord, FunctionHotDot, UploadVoice, UserPayTime

from app.api_1_0.utils import add_all_vip, create_key, gen_notice, is_Chinese, deal_float
from app.auth.models import AdminUser, AdminLog
from app.helper import send_mail, add_admin_log, print_log
from app.manage.apkparser import APKParser
from app.manage.forms import CreateAdminUserForm, AdminLogForm, UploadAppForm, FeedBackForm, ExceptionLogForm, \
    RegisterUserQueryForm, UnRegisterUserQueryForm, AddBlackListForm, AddWhiteImeiListForm, \
    AddDutyManagerForm, NextDayStayStatisticsForm, AddSpreadManagerForm, ActivityForm, AddActivityForm, \
    AddOpenScreenAdsForm, QueryOpenScreenAdsForm, \
    EditOpenScreenAdsForm, AddBannerAdsForm, BannertInfoForm, EditBannerAdsForm, EditActivityForm, \
    AddMemberWareForm, EditMemberWareForm, QueryMemberWareForm, WareStatisticsForm, VipMembersForm, \
    VipMembersDetailsForm, VipPayStatisticsForm, CommunicationGroupForm, OpenScreenAdsDataForm, InteractiveAdsForm, \
    QueryInteractiveAdsForm, EditInteractiveAdsForm, MemberForm, VipServiceProtocolForm, \
    VipCategoryForm, VipChannelForm, AddVipChannelForm, AddVipCategoryForm, AdsConfigForm, AdsIconForm, \
    OpenStrategyForm, AddAvatarAppForm, MakeAvatarForm, ActivityShareForm, InviteForm, \
    ShareForm, AddKeyForm, EditKeyForm, KeyRecordForm, KeyDetailForm, OrderKeyForm, ChannelUploadAppForm, \
    GetKeyChannelForm, KeyChannelForm, EditKeyChannelForm, GetKeyInfoForm, AddKeyImeiForm, SignDataActivityForm, \
    WeKeyRecordForm, WeKeyDetailForm, AddNoticeForm, NoticeForm, ExportKeyForm, AppProtocolForm, KeyForm, \
    GetImeiInfoForm, ActKeyStForm, AgentStForm, AddAgentForm, AppVersionCheckForm, AddVersionCheckForm, \
    AddMembersForm, ActMemebrForm, CheckKeyForm, BusinessCategoryForm, AddBusinessCategoryForm, AddBusinessWareForm, \
    EditBusinessWareForm, QueryBusinessWareForm, BusStatisticsForm, BusMembersForm, BusMembersDetailsForm, \
    BusPayStatisticsForm, AddFriendsForm, FreeVipDaysForm, FreeVipForm, BusRecommendForm, SecondDaysForm, \
    BusAssistantForm, AddLinkForm, AddAssistantForm, SetGZHForm, FreeExperienceForm, GetAccountInfoForm, \
    EditChannelAccountForm, \
    ChannelDataForm, ChannelDataDetailForm, DayChannelDataDetailForm, DayVipDetailForm, ChannelAccountForm, \
    SetFunctionForm, FunctionVideoForm, AddVideoForm, EditVideoForm, MicroStoreForm, PhoneForm, MemberDivideForm, \
    MemberDetailForm, BIProtocolForm, FcInfoForm, AddFcContentForm, EditFcContentForm, ActiveIntroduceForm, \
    EveryWashForm, PrivacyProtocolForm, ActiveCodeForm, AddInviteCodeForm, AlterBalanceForm, FunctionHotDotForm, \
    AlterDivideForm, UserPayTimeForm, AppealEditForm
from app.manage.helper import get_pay_person_num

from app.manage.models import DutyManager, BlackList, WhiteImeiList, NextDayStay, SpreadManager, KeyValue, \
    FunctionVideo, WithdrawCheck, AlterBalance, MasterFunctionVideo, AlterDivide


@login_required
def list_admin_user():
    page = request.args.get('page', 1, type=int)
    pagination = AdminUser.query.order_by(AdminUser.id.asc()). \
        paginate(page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    users = pagination.items
    add_admin_log(user=current_user.username, actions='查询用户', client_ip=request.remote_addr, results='成功')
    return render_template("manage/admin_user.html", users=users, pagination=pagination, action="LIST")


@login_required
def add_admin_user():
    form = CreateAdminUserForm()
    if form.validate_on_submit():
        user = AdminUser()
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.user_type.data
        user.department = form.user_department.data
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirm_token()
        send_mail([user.email], 'Confirm your account', 'auth/email/confirm', user=user, token=token)
        add_admin_log(user=current_user.username, actions='添加用户', client_ip=request.remote_addr, results='成功')
        return redirect(url_for('manage.list_admin_user'))
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
    return render_template("manage/admin_user.html", form=form, action="ADD")


@login_required
def del_admin_user():
    AdminUser.query.filter_by(id=request.args.get('id', type=int)).delete()
    db.session.commit()
    add_admin_log(user=current_user.username, actions='删除用户', client_ip=request.remote_addr, results='成功')
    return jsonify(code=0)


@login_required
def set_admin_user_status():
    user = AdminUser.query.filter_by(id=request.args.get('id', type=int)).first()
    if user is not None:
        user.forbidden = not user.forbidden
        db.session.add(user)
        db.session.commit()
        action = '禁止用户'
        if user.forbidden:
            action = '启用用户'
        add_admin_log(user=current_user.username, actions=action, client_ip=request.remote_addr, results='成功')
    return jsonify(code=0)


@login_required
def audit_user():
    form = AdminLogForm()
    query = AdminLog.query
    if form.validate_on_submit():
        username = form.username.data
        actions = form.actions.data
        client_ip = form.client_ip.data
        start_time = form.start_time.data
        end_time = form.end_time.data
    else:
        username = request.args.get('username')
        actions = request.args.get('actions')
        client_ip = request.args.get('client_ip')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    if username is not None:
        form.username.data = username
        if form.username.data != 'all':
            query = query.filter_by(username=form.username.data)
    if actions is not None:
        form.actions.data = actions
        if form.actions.data != 'all':
            query = query.filter_by(actions=form.actions.data)
    if client_ip is not None:
        form.client_ip.data = client_ip
        if form.client_ip.data != 'all':
            query = query.filter_by(client_ip=form.client_ip.data)
    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
        query = query.filter(AdminLog.log_time.between(form.start_time.data, form.end_time.data))
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    logs = pagination.items
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
            add_admin_log(user=current_user.username, actions='查询日志', client_ip=request.remote_addr, results=error[0])
    if not form.errors:
        add_admin_log(user=current_user.username, actions='查询日志', client_ip=request.remote_addr, results='成功')
    return render_template("manage/audit_user.html", form=form, logs=logs, pagination=pagination)


@login_required
def del_app_version():
    app_ver_id = request.args.get('id', type=int)
    app_version = AppVersion.query.filter_by(id=app_ver_id).first()
    if app_version is None:
        add_admin_log(user=current_user.username, actions='删除应用', client_ip=request.remote_addr, results='失败')
        return jsonify(code=1)
    target_file = os.path.join(os.getcwd(), app_version.app_dir)
    if os.path.isfile(target_file):
        os.remove(target_file)
    db.session.delete(app_version)
    db.session.commit()
    cache.delete('get_valid_app_version_name')
    cache.delete('get_app_version_list')
    if app_version.app_type == 99:
        cache.delete('feature_file')
    add_admin_log(user=current_user.username, actions='删除应用', client_ip=request.remote_addr, results='成功')
    return jsonify(code=0)


@login_required
def get_app_version_info():
    page = request.args.get('page', 1, type=int)
    app_list = AppList.query.all()
    pagination = AppVersion.query.join(AppList, AppList.app_type == AppVersion.app_type).order_by(
        AppVersion.release_time.desc()).paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'],
                                                 error_out=False)
    data = []
    for app_ver in pagination.items:
        for info in app_list:
            if app_ver.app_type == info.app_type:
                cell = dict(id=app_ver.id, app_name=info.app_name, version_name=app_ver.version_name,
                            version_code=app_ver.version_code, username=app_ver.spreader.username,
                            channelname=app_ver.spreader.channelname, release_time=app_ver.release_time,
                            app_size=app_ver.app_size, min_version_code=app_ver.min_version_code,
                            max_version_code=app_ver.max_version_code, is_released=app_ver.is_released)
                data.append(cell)
    add_admin_log(user=current_user.username, actions='查询版本信息', client_ip=request.remote_addr, results='成功')
    return render_template("manage/app_info.html", data=data, pagination=pagination)


@login_required
def upload_app():
    form = UploadAppForm()
    if form.validate_on_submit():
        channel = None
        app_type = int(form.app_type.data)
        max_frame_code = 0
        min_frame_code = 0
        if app_type == 100:
            if form.version_code.data == '' or not form.version_code.data.isdigit():
                flash('版本号不能为空且只能是数字')
                return redirect(url_for('manage.upload_app'))
        elif app_type >= 4:
            if form.min_frame_code.data == '':
                flash('最小可兼容框架版本号不能为空')
                return redirect(url_for('manage.upload_app'))
            if form.max_frame_code.data == '':
                flash('最大可兼容框架版本号不能为空')
                return redirect(url_for('manage.upload_app'))
            if not form.min_frame_code.data.isdigit():
                flash('最小可兼容框架版本号必须为数字')
                return redirect(url_for('manage.upload_app'))
            if not form.max_frame_code.data.isdigit():
                flash('最大可兼容框架版本号必须为数字')
                return redirect(url_for('manage.upload_app'))
            max_frame_code = int(form.max_frame_code.data)
            min_frame_code = int(form.min_frame_code.data)
            if app_type == 99:
                if form.version_code.data == '' or not form.version_code.data.isdigit():
                    flash('版本号不能为空且只能是数字')
                    return redirect(url_for('manage.upload_app'))

        app_name = current_app.config['APP_NAME_DICT'][app_type]
        file = request.files['upload_file']
        file_name = secure_filename(file.filename)
        if app_type == 99:
            file_name = datetime.datetime.now().strftime('%H%M%S') + file_name

        if not helper.allowed_file(file_name):
            flash('文件格式错误')
            add_admin_log(user=current_user.username, actions='上传应用',
                          client_ip=request.remote_addr, results='文件格式错误')
            return redirect(url_for('manage.upload_app'))

        app_dir = os.path.join(os.getcwd(), current_app.config['APK_TAG'], app_name)
        if not os.path.exists(app_dir):
            os.mkdir(app_dir)
        if app_type == 4 and form.spreader.data != 'godinsec':
            app_dir = os.path.join(app_dir, str(form.spreader.data))
            if not os.path.exists(app_dir):
                os.mkdir(app_dir)

        file.save(os.path.join(app_dir, file_name))
        app_size = getsize(os.path.join(app_dir, file_name))
        if app_type == 99:
            version_code = form.version_code.data
            version_name = form.wechat_version_name.data
            file_type = '.' + file_name.rsplit('.', 1)[1]
        elif app_type == 100:
            version_code = form.version_code.data
            version_name = form.version_name.data
            if version_name == '':
                # 此情况无版本默认值
                version_name = 'Permission1.0.0'
            file_type = '.json'
        else:
            apk_parser = APKParser(os.path.join(app_dir, file_name))
            version_code = apk_parser.get_version_code()
            version_name = apk_parser.get_version_name()
            pack_name = apk_parser.get_package()
            channel = apk_parser.get_channel()
            file_type = '.apk'
            if AppList.query.filter_by(package_name=pack_name, app_type=app_type).first() is None:
                flash('应用类型与上传的应用文件不符')
                os.remove(os.path.join(app_dir, file_name))
                add_admin_log(user=current_user.username, actions='删除应用',
                              client_ip=request.remote_addr, results='应用类型与上传的应用文件不符')
                return redirect(url_for('manage.upload_app'))
        spm = SpreadManager.query.filter_by(channelname=form.spreader.data).first()
        if spm is None:
            flash('推广人员异常')
            os.remove(os.path.join(app_dir, file_name))
            add_admin_log(user=current_user.username, actions='删除应用',
                          client_ip=request.remote_addr, results='推广人员异常')
            return redirect(url_for('manage.upload_app'))
        if app_type == 99 and form.upload_target.data == 0:  # 新增文件
            app_ver = AppVersion()
        else:
            app_ver = AppVersion.query.filter_by(app_type=app_type, version_code=version_code,
                                                 version_name=version_name, spread_id=spm.id).first()
            if app_ver is None:
                app_ver = AppVersion()
            else:
                app_ver.ping()

        app_ver.app_type = app_type
        app_ver.version_name = version_name
        app_ver.version_code = version_code
        app_ver.app_size = app_size
        app_ver.spread_id = spm.id
        if app_type == 4 and form.spreader.data != 'godinsec':
            rfile_name = app_name + '_' + version_name + file_type
            app_ver.app_dir = os.path.join(current_app.config['APK_TAG'], app_name, str(form.spreader.data), rfile_name)
        elif app_type == 99:
            rfile_name = app_name + '_' + version_name + '_' + str(min_frame_code) \
                         + '_' + str(max_frame_code) + file_type
            app_ver.app_dir = os.path.join(current_app.config['APK_TAG'], app_name, rfile_name)
        elif app_type == 100:
            rfile_name = app_name + '_' + str(version_code) + file_type
            app_ver.app_dir = os.path.join(current_app.config['APK_TAG'], app_name, rfile_name)
        else:
            rfile_name = app_name + '_' + version_name + file_type
            app_ver.app_dir = os.path.join(current_app.config['APK_TAG'], app_name, rfile_name)

        if channel:
            if channel == 'TGZQ':
                cache.set('TGZQ_apk_path', app_ver.app_dir, timeout=12 * 60 * 60)
                key_value = KeyValue.query.filter_by(key="TGZQ_apk_path").limit(1).first()
                if key_value:
                    key_value.value = app_ver.app_dir
                else:
                    key_value = KeyValue(
                        key='TGZQ_apk_path',
                        value=app_ver.app_dir
                    )
                db.session.add(key_value)
                db.session.commit()
            if channel == 'VSZS':
                cache.set('VSZS_apk_path', app_ver.app_dir, timeout=12 * 60 * 60)
                key_value = KeyValue.query.filter_by(key="VSZS_apk_path").limit(1).first()
                if key_value:
                    key_value.value = app_ver.app_dir
                else:
                    key_value = KeyValue(
                        key='VSZS_apk_path',
                        value=app_ver.app_dir
                    )
                db.session.add(key_value)
                db.session.commit()

        app_ver.min_version_code = min_frame_code
        app_ver.max_version_code = max_frame_code
        app_ver.update_msg = form.update_msg.data
        app_ver.spreader = SpreadManager.query.filter_by(channelname=form.spreader.data).first()
        db.session.add(app_ver)
        db.session.commit()
        os.rename(os.path.join(app_dir, file_name), os.path.join(app_dir, rfile_name))
        add_admin_log(user=current_user.username, actions='上传应用', client_ip=request.remote_addr, results='成功')
        return redirect(url_for('manage.get_app_version_info'))
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
    return render_template("manage/app_manage.html", form=form)


@login_required
def get_feedback():
    form = FeedBackForm()
    query = FeedBack.query
    if form.validate_on_submit() and request.method == 'POST':
        imei = form.imei.data
        os_version = form.os_version.data
        dev_factory = form.dev_factory.data
        dev_model = form.dev_model.data
        app_version = form.app_version.data
        start_time = form.start_time.data
        end_time = form.end_time.data
        status = form.status.data
        phone_num = form.phone_num.data
    else:
        imei = request.args.get('imei')
        os_version = request.args.get('os_version')
        dev_factory = request.args.get('dev_factory')
        dev_model = request.args.get('dev_model')
        app_version = request.args.get('app_version')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        status = request.args.get('status')
        phone_num = request.args.get('phone_num')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    if imei is not None:
        form.imei.data = imei
        if form.imei.data != '':
            query = query.filter(FeedBack.imei.like('%' + form.imei.data + '%'))
    if os_version is not None:
        form.os_version.data = os_version
        if form.os_version.data != 'all':
            query = query.filter_by(os_version=form.os_version.data)
    if dev_factory is not None:
        form.dev_factory.data = dev_factory
        if form.dev_factory.data != 'all':
            query = query.filter_by(device_factory=form.dev_factory.data)
    if dev_model is not None:
        form.dev_model.data = dev_model
        if form.dev_model.data != 'all':
            query = query.filter_by(device_model=form.dev_model.data)
    if app_version is not None:
        form.app_version.data = app_version
        if form.app_version.data != 'all':
            query = query.filter_by(app_version=form.app_version.data)
    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
        query = query.filter(FeedBack.create_time.between(form.start_time.data, form.end_time.data))
    if status is not None:
        form.status.data = status
        if form.status.data != '-1':
            query = query.filter_by(status=form.status.data)
    if phone_num is not None:
        form.phone_num.data = phone_num
        if form.phone_num.data != '':
            query = query.filter(FeedBack.phone_num.like(form.phone_num.data + '%'))

    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(FeedBack.create_time.desc()).paginate(
        page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='查看反馈', client_ip=request.remote_addr, results=error[0])
    if not form.errors:
        add_admin_log(user=current_user.username, actions='查看反馈', client_ip=request.remote_addr, results='成功')
    return render_template("manage/feedback.html", form=form, data=pagination.items, pagination=pagination)


@login_required
def get_exception():
    form = ExceptionLogForm()
    query = ExceptionLog.query
    if form.validate_on_submit():
        app_version = form.app_version.data
        os_version = form.os_version.data
        device_model = form.device_model.data
        imei = form.imei.data
    else:
        app_version = request.args.get('app_version')
        os_version = request.args.get('os_version')
        device_model = request.args.get('device_model')
        imei = request.args.get('imei')
    if app_version is not None:
        form.app_version.data = app_version
        if form.app_version.data != 'all':
            query = query.filter_by(app_version=form.app_version.data)

    if os_version is not None:
        form.os_version.data = os_version
        if form.os_version.data != 'all':
            query = query.filter_by(os_version=form.os_version.data)
    if device_model is not None:
        form.device_model.data = device_model
        if form.device_model.data != 'all':
            query = query.filter_by(device_model=form.device_model.data)
    if imei is not None:
        form.imei.data = imei
        if form.imei.data != '':
            query = query.filter(ExceptionLog.imei.like('%' + form.imei.data + '%'))

    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(ExceptionLog.create_time.desc()). \
        paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='查看异常', client_ip=request.remote_addr, results=error[0])
    if not form.errors:
        add_admin_log(user=current_user.username, actions='查看异常', client_ip=request.remote_addr, results='成功')
    res = []
    for item in pagination.items:
        cell = dict(item.to_json())
        cell['log_link'] = current_app.config['FILE_SERVER'] + item.log_link
        if cell['status'] == 0:
            cell['status'] = '未处理'
        else:
            cell['status'] = '已邮件通知'
        res.append(cell)
    return render_template("manage/exception.html", form=form, data=res, pagination=pagination)


@celery.task(name='check_exception_log')
def check_exception_log():
    exceptions = ExceptionLog.query.filter_by(status=0).order_by(ExceptionLog.create_time.asc()).limit(10).all()
    start_time = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d') +
                                            " 09:00:00", '%Y-%m-%d %H:%M:%S')
    end_time = start_time + datetime.timedelta(minutes=30)
    now_time = datetime.datetime.now()
    if len(exceptions) == 10 or (start_time <= now_time <= end_time):
        res = []
        attch = []
        for item in exceptions:
            cell = item.to_json()
            cell['log_link'] = os.path.join(os.getcwd(), item.log_link)
            attch.append(cell['log_link'])
            res.append(cell)
            ExceptionLog.query.filter_by(md5_value=item.md5_value).update(dict(status=1))
        db.session.commit()
        if res:
            duties = DutyManager.query.filter_by(on_duty=True).all()
            send_mail(to=[duty.email for duty in duties], subject='异常日志通告', template='auth/email/exception_log',
                      attachments=attch, logs=res)
        return True
    else:
        return False


@login_required
def get_reg_user_info():
    form = RegisterUserQueryForm()
    query = UserInfo.query.join(GodinAccount, GodinAccount.godin_id == UserInfo.godin_id). \
        join(DeviceInfo, UserInfo.imei == DeviceInfo.imei).filter(DeviceInfo.status == 1)
    if form.validate_on_submit():
        phone_num = form.phone_num.data
        imei = form.imei.data
        os_version = form.os_version.data
        dev_factory = form.dev_factory.data
        dev_model = form.dev_model.data
        app_version = form.app_version.data
        order_time = form.order_time.data
        market = form.market.data
        start_time = form.start_time.data
        end_time = form.end_time.data
    else:
        phone_num = request.args.get('phone_num')
        imei = request.args.get('imei')
        os_version = request.args.get('os_version')
        dev_factory = request.args.get('dev_factory')
        dev_model = request.args.get('dev_model')
        app_version = request.args.get('app_version')
        order_time = request.args.get('order_time')
        market = request.args.get('market')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    if phone_num is not None:
        form.phone_num.data = phone_num
        if form.phone_num.data != '':
            query = query.filter(GodinAccount.phone_num.like('%' + form.phone_num.data + '%'))
    if imei is not None:
        form.imei.data = imei
        if form.imei.data != '':
            query = query.filter(UserInfo.imei.like('%' + form.imei.data + '%'))
    if os_version is not None:
        form.os_version.data = os_version
        if form.os_version.data != '':
            query = query.filter(DeviceInfo.os_version.like('%' + form.os_version.data + '%'))
    if dev_factory is not None:
        form.dev_factory.data = dev_factory
        if form.dev_factory.data != '':
            query = query.filter(DeviceInfo.device_factory.like('%' + form.dev_factory.data + '%'))
    if dev_model is not None:
        form.dev_model.data = dev_model
        if form.dev_model.data != '':
            query = query.filter(DeviceInfo.device_model.like('%' + form.dev_model.data + '%'))
    if app_version is not None:
        form.app_version.data = app_version
        if form.app_version.data != 'all':
            query = query.filter_by(app_version=form.app_version.data)
    if order_time is not None:
        form.order_time.data = order_time
        if form.order_time.data == 'create_time':
            query = query.order_by(GodinAccount.create_time.desc())
        else:
            query = query.order_by(DeviceInfo.last_seen.desc())
    else:
        query = query.order_by(GodinAccount.create_time.desc())
    if market is not None:
        form.market.data = market
        if form.market.data != 'all':
            query = query.filter_by(market=form.market.data)
    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
        if form.order_time.data == 'create_time':
            query = query.filter(GodinAccount.create_time.between(form.start_time.data, form.end_time.data))
        else:
            query = query.filter(DeviceInfo.last_seen.between(form.start_time.data, form.end_time.data))
    flag = False
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='查看注册用户', client_ip=request.remote_addr, results=error[0])
    add_admin_log(user=current_user.username, actions='查看注册用户', client_ip=request.remote_addr, results='成功')
    return render_template("manage/reg_user_info.html", form=form, data=pagination.items, pagination=pagination)


@login_required
def get_un_reg_user_info():
    form = UnRegisterUserQueryForm()
    query = DeviceInfo.query.filter_by(status=0)
    if form.validate_on_submit():
        imei = form.imei.data
        os_version = form.os_version.data
        dev_factory = form.dev_factory.data
        dev_model = form.dev_model.data
        app_version = form.app_version.data
        order_time = form.order_time.data
        market = form.market.data
        start_time = form.start_time.data
        end_time = form.end_time.data
    else:
        imei = request.args.get('imei')
        os_version = request.args.get('os_version')
        dev_factory = request.args.get('dev_factory')
        dev_model = request.args.get('dev_model')
        app_version = request.args.get('app_version')
        order_time = request.args.get('order_time')
        market = request.args.get('market')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    if imei is not None:
        form.imei.data = imei
        if form.imei.data != '':
            query = query.filter(DeviceInfo.imei.like('%' + form.imei.data + '%'))
    if os_version is not None:
        form.os_version.data = os_version
        if form.os_version.data != '':
            query = query.filter(DeviceInfo.os_version.like('%' + form.os_version.data + '%'))
    if dev_factory is not None:
        form.dev_factory.data = dev_factory
        if form.dev_factory.data != '':
            query = query.filter(DeviceInfo.device_factory.like('%' + form.dev_factory.data + '%'))
    if dev_model is not None:
        form.dev_model.data = dev_model
        if form.dev_model.data != '':
            query = query.filter(DeviceInfo.device_model.like('%' + form.dev_model.data + '%'))
    if app_version is not None:
        form.app_version.data = app_version
        query = query.filter_by(app_version=form.app_version.data)
    if order_time is not None:
        form.order_time.data = order_time
        if form.order_time.data == 'create_time':
            query = query.order_by(DeviceInfo.create_time.desc())
        else:
            query = query.order_by(DeviceInfo.last_seen.desc())
    else:
        query = query.order_by(DeviceInfo.create_time.desc())
    if market is not None:
        form.market.data = market
        query = query.filter_by(market=form.market.data)
    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
        if form.order_time.data == 'create_time':
            query = query.filter(DeviceInfo.create_time.between(form.start_time.data, form.end_time.data))
        else:
            query = query.filter(DeviceInfo.last_seen.between(form.start_time.data, form.end_time.data))
    flag = False
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='查看未注册用户', client_ip=request.remote_addr,
                      results=error[0])
    add_admin_log(user=current_user.username, actions='查看未注册用户', client_ip=request.remote_addr, results='成功')
    return render_template("manage/un_reg_user_info.html", form=form, data=pagination.items, pagination=pagination)


@login_required
# @cache.cached(timeout=10)
def get_godin_app_list():
    res = []
    for item in AppList.query.all():
        res.append(item.package_name)
    return res


@login_required
def get_black_list_info():
    page = request.args.get('page', 1, type=int)
    pagination = BlackList.query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    data = pagination.items
    add_admin_log(user=current_user.username, actions='查询黑名单', client_ip=request.remote_addr, results='成功')
    return render_template("manage/black_list_info.html", data=data, pagination=pagination)


@login_required
def add_black_list():
    form = AddBlackListForm()
    if form.validate_on_submit():
        if BlackList.query.filter_by(imei=form.imei.data).first() is not None:
            flash('该imei已经在黑名单中')
            add_admin_log(user=current_user.username, actions='添加黑名单', client_ip=request.remote_addr, results='失败')
            return redirect(url_for('manage.add_black_list'))
        black_list = BlackList(form.imei.data)
        db.session.add(black_list)
        db.session.commit()
        cache.delete('get_black_imei_list')
        add_admin_log(user=current_user.username, actions='添加黑名单', client_ip=request.remote_addr, results='成功')
        return redirect(url_for('manage.get_black_list_info'))
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='添加黑名单', client_ip=request.remote_addr, results='失败')
    return render_template("manage/black_list_manage.html", form=form)


@login_required
def del_black_list():
    imei = request.args.get('imei')
    black_list = BlackList.query.filter_by(imei=imei).first()
    if black_list is None:
        add_admin_log(user=current_user.username, actions='删除黑名单', client_ip=request.remote_addr, results='失败')
        return jsonify(code=1)
    db.session.delete(black_list)
    db.session.commit()
    cache.delete('get_black_imei_list')
    add_admin_log(user=current_user.username, actions='删除黑名单', client_ip=request.remote_addr, results='成功')
    return jsonify(code=0)


@login_required
def get_white_imei_list_info():
    page = request.args.get('page', 1, type=int)
    pagination = WhiteImeiList.query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'],
                                              error_out=False)
    data = pagination.items
    add_admin_log(user=current_user.username, actions='查询imei白名单', client_ip=request.remote_addr, results='成功')
    return render_template("manage/white_imei_list_info.html", data=data, pagination=pagination)


@login_required
def add_white_imei_list():
    form = AddWhiteImeiListForm()
    if form.validate_on_submit():
        if WhiteImeiList.query.filter_by(imei=form.imei.data).first() is not None:
            flash('该imei已经在IMEI白名单中')
            add_admin_log(user=current_user.username, actions='添加IMEI白名单',
                          client_ip=request.remote_addr, results='失败')
            return redirect(url_for('manage.add_white_imei_list'))
        white_imei_list = WhiteImeiList(form.imei.data)
        db.session.add(white_imei_list)
        db.session.commit()
        cache.delete('get_white_imei_list')
        add_admin_log(user=current_user.username, actions='添加IMEI白名单', client_ip=request.remote_addr, results='成功')
        return redirect(url_for('manage.get_white_imei_list_info'))
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='添加IMEI白名单', client_ip=request.remote_addr, results='失败')
    return render_template("manage/white_imei_list_manage.html", form=form)


@login_required
def del_white_imei_list():
    imei = request.args.get('imei')
    white_imei_list = WhiteImeiList.query.filter_by(imei=imei).first()
    if white_imei_list is None:
        add_admin_log(user=current_user.username, actions='删除IMEI白名单', client_ip=request.remote_addr, results='失败')
        return jsonify(code=1)
    db.session.delete(white_imei_list)
    db.session.commit()
    cache.delete('get_white_imei_list')
    add_admin_log(user=current_user.username, actions='删除IMEI白名单', client_ip=request.remote_addr, results='成功')
    return jsonify(code=0)


@login_required
def export_result():
    export_type = request.args.get('export_type', type=int)
    # register user export
    if export_type == 1:
        query = UserInfo.query.join(GodinAccount, GodinAccount.godin_id == UserInfo.godin_id). \
            join(DeviceInfo, UserInfo.imei == DeviceInfo.imei)
        phone_num = request.args.get('phone_num')
        imei = request.args.get('imei')
        os_version = request.args.get('os_version')
        dev_factory = request.args.get('dev_factory')
        dev_model = request.args.get('dev_model')
        app_version = request.args.get('app_version')
        order_time = request.args.get('order_time')
        market = request.args.get('market')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        # os_version got a str contains 'None' and phone got a None object
        if phone_num is not None:
            query = query.filter(GodinAccount.phone_num.like('%' + phone_num + '%'))
        if imei is not None:
            query = query.filter(UserInfo.imei.like('%' + imei + '%'))
        if os_version is not None:
            query = query.filter(DeviceInfo.os_version.like('%' + os_version + '%'))
        if dev_factory is not None:
            query = query.filter(DeviceInfo.device_factory.like('%' + dev_factory + '%'))
        if dev_model is not None:
            query = query.filter(DeviceInfo.device_model.like('%' + dev_model + '%'))
        if app_version is not None:
            query = query.filter_by(app_version=app_version)
        if market is not None:
            query = query.filter_by(market=market)
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            if order_time == 'create_time':
                query = query.filter(GodinAccount.create_time.between(start_time, end_time))
            else:
                query = query.filter(DeviceInfo.last_seen.between(start_time, end_time))
        res = []
        i = 1
        for item in query.all():
            cell = OrderedDict()
            cell['序号'] = i
            cell['手机号'] = item.godin_account.phone_num
            cell['IMEI'] = item.imei
            cell['厂商'] = item.device_info.device_factory
            cell['型号'] = item.device_info.device_model
            cell['系统版本'] = item.device_info.os_version
            cell['应用版本'] = item.device_info.app_version
            cell['渠道'] = item.device_info.market
            if order_time == 'create_time':
                cell['首次使用时间'] = datetime.datetime.strftime(item.godin_account.create_time, '%Y-%m-%d %H:%M:%S')
            else:
                cell['活跃时间'] = datetime.datetime.strftime(item.device_info.last_seen, '%Y-%m-%d %H:%M:%S')
            res.append(cell)
            i += 1
        return excel.make_response_from_records(res, file_type="xls", file_name='reg_statistics')

    # unregister user export
    elif export_type == 2:
        query = DeviceInfo.query.filter_by(status=0)
        imei = request.args.get('imei')
        os_version = request.args.get('os_version')
        dev_factory = request.args.get('dev_factory')
        dev_model = request.args.get('dev_model')
        app_version = request.args.get('app_version')
        order_time = request.args.get('order_time')
        market = request.args.get('market')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')

        if imei is not None:
            query = query.filter(DeviceInfo.imei.like('%' + imei + '%'))
        if os_version is not None:
            query = query.filter(DeviceInfo.os_version.like('%' + os_version + '%'))
        if dev_factory is not None:
            query = query.filter(DeviceInfo.device_factory.like('%' + dev_factory + '%'))
        if dev_model is not None:
            query = query.filter(DeviceInfo.device_model.like('%' + dev_model + '%'))
        if app_version is not None:
            query = query.filter_by(app_version=app_version)
        if market is not None:
            query = query.filter_by(market=market)
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            if order_time == 'create_time':
                query = query.filter(DeviceInfo.create_time.between(start_time, end_time))
            else:
                query = query.filter(DeviceInfo.last_seen.between(start_time, end_time))
        res = []
        i = 1
        for item in query.all():
            cell = OrderedDict()
            cell['序号'] = i
            cell['IMEI'] = item.imei
            cell['厂商'] = item.device_factory
            cell['型号'] = item.device_model
            cell['系统版本'] = item.os_version
            cell['应用版本'] = item.app_version
            cell['渠道'] = item.market
            if order_time == 'create_time':
                cell['首次使用时间'] = datetime.datetime.strftime(item.create_time, '%Y-%m-%d %H:%M:%S')
            else:
                cell['活跃时间'] = datetime.datetime.strftime(item.last_seen, '%Y-%m-%d %H:%M:%S')
            res.append(cell)
            i += 1
        return excel.make_response_from_records(res, file_type="xls", file_name='un_reg_statistics')
    # exception log export
    elif export_type == 4:
        query = ExceptionLog.query
        app_version = request.args.get('app_version')
        os_version = request.args.get('os_version')
        device_model = request.args.get('device_model')
        imei = request.args.get('imei')
        if app_version is not None:
            if app_version != 'all':
                query = query.filter_by(app_version=app_version)
        if os_version is not None:
            if os_version != 'all':
                query = query.filter_by(os_version=os_version)
        if device_model is not None:
            if device_model != 'all':
                query = query.filter_by(device_model=device_model)
        if imei is not None:
            if imei != '':
                query = query.filter(ExceptionLog.imei.like('%' + imei + '%'))

        res = []
        i = 1
        for item in query.all():
            cell = OrderedDict()
            cell['序号'] = i
            cell['应用版本'] = item.app_version
            cell['系统版本'] = item.os_version
            cell['IMEI'] = item.imei
            cell['型号'] = item.device_model
            cell['MD5'] = item.md5_value
            cell['次数'] = item.error_count
            if item.status == 0:
                cell['状态'] = '未处理'
            else:
                cell['状态'] = '已邮件通知'
            cell['创建时间'] = datetime.datetime.strftime(item.create_time, '%Y-%m-%d %H:%M:%S')
            res.append(cell)
            i += 1
        return excel.make_response_from_records(res, file_type="xls", file_name='exceptions_statistics')
    # export average app statistics
    elif export_type == 5:
        result = request.args.get('result')
        res = eval(result)
        return excel.make_response_from_records(res, file_type="xls", file_name='avg_app_statistics')
    # export open screen ads
    elif export_type == 11:
        name = request.args.get('name')
        position = request.args.get('position', type=int)
        source = request.args.get('source', type=int)
        status = request.args.get('status', type=int)
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d').date()
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d').date()

        query = OpenScreenAds.query
        if name is not None:
            if name != '':
                query = query.filter(OpenScreenAds.name.like('%' + name + '%'))
        if position is not None:
            if position != -1:
                query = query.filter_by(position=position)
        if source is not None:
            if source != -1:
                query = query.filter_by(source=source)
        if status is not None:
            if status != -1:
                query = query.filter_by(status=status)

        res = []
        i = 1
        for open_ads in query.all():
            total_display_query_all = db.session.query(func.sum(OpenScreenAdsStatistics.count), func.count()).filter_by(
                ad_id=open_ads.id,
                operation=0)
            total_click_query_all = db.session.query(func.sum(OpenScreenAdsStatistics.count), func.count()).filter_by(
                ad_id=open_ads.id,
                operation=1)
            real_click_query = db.session.query(func.sum(OpenScreenAdsStatistics.count)).filter_by(
                ad_id=open_ads.id, operation=2)
            if start_time is not None and end_time is not None:
                display_info = total_display_query_all.filter(OpenScreenAdsStatistics.record_time.between(
                    start_time, end_time)).first()

                click_info = total_click_query_all.filter(OpenScreenAdsStatistics.record_time.between(
                    start_time, end_time)).first()
                real_click_number = real_click_query.filter(OpenScreenAdsStatistics.record_time.between(
                    start_time, end_time)).first()[0]
                if real_click_number is None:
                    real_click_number = 0

            if display_info is not None:
                if display_info[1] is None:
                    display_number = 0
                else:
                    display_number = display_info[1]
                if display_info[0] is None:
                    total_display_number = 0
                else:
                    total_display_number = display_info[0]
            else:
                display_number = 0
                total_display_number = 0

            if click_info is not None:
                if click_info[1] is None:
                    click_number = 0
                else:
                    click_number = click_info[1]
                if click_info[0] is None:
                    total_click_number = 0
                else:
                    total_click_number = click_info[0]
            else:
                click_number = 0
                total_click_number = 0

            if real_click_number is None:
                real_click_number = 0

            cell = OrderedDict()
            cell['序号'] = i
            cell['广告ID'] = open_ads.id
            cell['广告名称'] = open_ads.name
            cell['广告来源'] = current_app.config['ADS_SOURCE'][open_ads.source]
            cell['广告位置'] = current_app.config['OPEN_SCREEN_ADS_POSITION'][open_ads.position]
            cell['广告商'] = open_ads.advertiser
            cell['广告编号'] = open_ads.number
            cell['总展现量'] = total_display_number
            cell['去重展现量'] = display_number
            cell['总点击量'] = total_click_number
            cell['去重点击量'] = click_number
            cell['自然点击量'] = real_click_number
            cell['合作开始时间'] = open_ads.start_time.strftime('%Y-%m-%d %H:%M:%S')
            if open_ads.status == 0:
                cell['状态'] = '关闭'
            else:
                cell['状态'] = '开启'
            res.append(cell)
            i += 1
        return excel.make_response_from_records(res, file_type="xls", file_name='open_screen_ads')
    # export banner ads
    elif export_type == 12:
        query = BannerAds.query
        name = request.args.get('name')
        position = request.args.get('position')
        source = request.args.get('source')
        status = request.args.get('status')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d').date()
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d').date()

        if name is not None:
            if name != '':
                query = query.filter(BannerAds.name.like('%' + name + '%'))
        if position is not None:
            if position != '-1':
                query = query.filter_by(position=position)
        if source is not None:
            if source != '-1':
                query = query.filter_by(source=source)
        if status is not None:
            if status != '-1':
                query = query.filter_by(status=status)
        data = {}
        for ad in query:
            show_query_all = db.session.query(func.sum(BannerAdsStatistics.count), func.count()).filter_by(
                ad_id=ad.id, operation=0)
            click_query_all = db.session.query(func.sum(BannerAdsStatistics.count), func.count()).filter_by(
                ad_id=ad.id, operation=1)
            if start_time is not None and end_time is not None:
                show_all_info = show_query_all.filter(
                    BannerAdsStatistics.record_time.between(start_time, end_time)).first()
                click_all_info = click_query_all.filter(BannerAdsStatistics.record_time.between(
                    start_time, end_time)).first()

            if show_all_info is not None:
                if show_all_info[1] is None:
                    show_count = 0
                else:
                    show_count = show_all_info[1]
                if show_all_info[0] is None:
                    show_all = 0
                else:
                    show_all = show_all_info[0]
            else:
                show_count = 0
                show_all = 0
            if click_all_info is not None:
                if click_all_info[1] is None:
                    click_count = 0
                else:
                    click_count = click_all_info[1]
                if click_all_info[0] is None:
                    click_all = 0
                else:
                    click_all = click_all_info[0]
            else:
                click_count = 0
                click_all = 0
            data[ad.id] = [show_all, show_count, click_all, click_count]
        res = []
        i = 1
        for banner in query.all():
            cell = OrderedDict()
            cell['序号'] = i
            cell['广告ID'] = banner.id
            cell['广告名称'] = banner.name
            cell['广告来源'] = current_app.config['ADS_SOURCE'][banner.source]
            cell['广告位置'] = current_app.config['BANNER_ADS_POSITION'][banner.position]
            cell['广告商'] = banner.advertiser
            cell['广告编号'] = banner.number
            cell['总展示量'] = data[banner.id][0]
            cell['去重展示量'] = data[banner.id][1]
            cell['总点击量'] = data[banner.id][2]
            cell['去重点击量'] = data[banner.id][3]
            res.append(cell)
            i += 1
        return excel.make_response_from_records(res, file_type="xls", file_name='bannerads')
    # export vim member ware
    elif export_type == 16:
        query = MemberWare.query.order_by(MemberWare.id.desc())
        channel = request.args.get('channel')
        category = request.args.get('category')
        status = request.args.get('status', type=int)

        if channel is not None:
            if channel != '':
                query = query.filter(MemberWare.channel.like('%' + channel + '%'))
        else:
            query = query.filter(MemberWare.channel.like('%' + 'moren' + '%'))
        if category is not None:
            if category != '':
                vip_type = VipType.query.filter_by(name=category).first()
                if vip_type is not None:
                    type_number = vip_type.number
                else:
                    type_number = 0
                query = query.filter_by(category=type_number)
        if status is not None:
            if status != -1:
                query = query.filter_by(status=status)
        res = []
        i = 1
        for ware in query.all():
            vip_type = VipType.query.filter_by(number=ware.category).first()

            cell = OrderedDict()
            cell['序号'] = i
            cell['渠道'] = ware.channel
            if vip_type is not None:
                cell['VIP类型'] = vip_type.name
            cell['VIP名称'] = ware.name
            if ware.status == 0:
                cell['显示状态'] = '无效'
            elif ware.status == 1:
                cell['显示状态'] = '有效'
            res.append(cell)
            i += 1
        return excel.make_response_from_records(res, file_type='xls', file_name='ware')
    # export vip members
    elif export_type == 17:
        query = VipMembers.query.join(GodinAccount, GodinAccount.godin_id == VipMembers.godin_id). \
            add_entity(GodinAccount).order_by(VipMembers.first_pay_time.desc())
        phone_num = request.args.get('phone_num')
        category = request.args.get('category', -1, type=int)
        cur_pay_cate = request.args.get('cur_pay_cate')
        status = request.args.get('status', -1, type=int)
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        channel = request.args.get('channel')

        if phone_num is not None:
            if phone_num != '':
                query = query.filter(GodinAccount.phone_num.like('%' + phone_num + '%'))
        if cur_pay_cate is not None:
            if cur_pay_cate != '':
                vip_type = VipType.query.filter_by(name=cur_pay_cate).first()
                if vip_type is not None:
                    query = query.filter(VipMembers.cur_pay_cate == vip_type.number)
        if category is not None:
            if category != -1:
                query = query.filter(VipMembers.category == category)
        if status is not None:
            status = status
            if status != -1:
                query = query.filter(VipMembers.status == status)
        if channel is not None:
            if channel != '':
                query = query.filter(VipMembers.channel.like('%' + channel + '%'))
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            query = query.filter(VipMembers.first_pay_time.between(start_time, end_time))
        res = []
        i = 1
        for vip in query.all():
            vip_type = VipType.query.filter_by(number=vip.VipMembers.cur_pay_cate).first()
            cell = OrderedDict()
            cell['序号'] = i
            cell['手机号'] = vip.GodinAccount.phone_num
            cell['来源渠道'] = vip.VipMembers.channel
            if vip.VipMembers.category == 0:
                cell['会员种类'] = '付费'
            elif vip.VipMembers.category == 1:
                cell['会员种类'] = '活动'
            elif vip.VipMembers.category == 2:
                cell['会员种类'] = '手动添加'
            else:
                cell['会员种类'] = '其它'
            if vip.VipMembers.first_pay_time is not None:
                cell['首次购买时间'] = vip.VipMembers.first_pay_time.strftime('%Y-%m-%d %H:%M:%S')
            else:
                cell['首次购买时间'] = vip.VipMembers.first_pay_time
            if vip_type is not None:
                cell['当前使用类型'] = vip_type.name
            if vip.VipMembers.valid_time is not None:
                cell['到期时间'] = vip.VipMembers.valid_time.strftime('%Y-%m-%d %H:%M:%S')
            else:
                cell['到期时间'] = vip.VipMembers.valid_time
            if vip.VipMembers.status == 0:
                cell['状态'] = '已过期'
            elif vip.VipMembers.status == 1:
                cell['状态'] = '正常'
            res.append(cell)
            i += 1
        return excel.make_response_from_records(res, file_type='xls', file_name='vip_members')
    # export vip member details
    elif export_type == 18:
        godin_id = request.args.get('godin_id')
        query = MemberWareOrder.query.join(MemberWare, MemberWare.id == MemberWareOrder.ware_id
                                           ).add_entity(MemberWare).filter(MemberWareOrder.buyer_godin_id == godin_id,
                                                                           MemberWareOrder.status == 1). \
            order_by(MemberWareOrder.pay_time.desc())
        pay_type = request.args.get('pay_type', -1, type=int)
        category = request.args.get('category')
        status = request.args.get('status')
        order_number = request.args.get('order_number')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        add_type = request.args.get('add_type', -1, type=int)
        if pay_type is not None:
            if pay_type != -1:
                query = query.filter(MemberWareOrder.pay_type == pay_type)
        if category is not None:
            if category != '':
                vip_type = VipType.query.filter_by(name=category).first()
                if vip_type is not None:
                    query = query.filter(MemberWare.category == vip_type.number)
        if status is not None:
            if status == 0:
                query = query.filter(MemberWareOrder.end_time < datetime.datetime.now())
            elif status == 1:
                query = query.filter(datetime.datetime.now() > MemberWareOrder.start_time,
                                     datetime.datetime.now() < MemberWareOrder.end_time)
            elif status == 2:
                query = query.filter(MemberWareOrder.start_time > datetime.datetime.now())
        if add_type is not None:
            if add_type != -1:
                query = query.filter(MemberWareOrder.category == add_type)
        if order_number is not None:
            if order_number != '':
                query = query.filter(MemberWareOrder.order_number.like('%' + order_number + '%'))
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            query = query.filter(MemberWareOrder.create_time.between(start_time, end_time))
        res = []
        i = 1
        for item in query.all():
            vip_type = VipType.query.filter_by(number=item.MemberWare.category).first()
            cell = OrderedDict()
            cell['序号'] = i
            cell['订单编号'] = item.MemberWareOrder.order_number
            cell['渠道'] = item.MemberWare.channel
            if item.MemberWareOrder.category == 0:
                cell['会员途径'] = '付费'
            elif item.MemberWareOrder.category == 1:
                cell['会员途径'] = '活动'
            elif item.MemberWareOrder.category == 2:
                cell['会员途径'] = '手动添加'
            elif item.MemberWareOrder.category == 3:
                cell['会员途径'] = '其他'
            cell['订单时间'] = item.MemberWareOrder.create_time.strftime('%Y-%m-%d %H:%M:%S')
            if item.MemberWareOrder.pay_type == 0:
                cell['支付方式'] = '微信'
            elif item.MemberWareOrder.pay_type == 1:
                cell['支付方式'] = '支付宝'
            elif item.MemberWareOrder.pay_type == 2:
                cell['支付方式'] = '其他'
            if item.MemberWareOrder.pay_time is not None:
                cell['支付时间'] = item.MemberWareOrder.pay_time.strftime('%Y-%m-%d %H:%M:%S')
            else:
                cell['支付时间'] = item.MemberWareOrder.pay_time
            if vip_type is not None:
                cell['类型'] = vip_type.name
            cell['产品标价'] = round(item.MemberWareOrder.ware_price / 100, 2)
            cell['折扣信息(%)'] = item.MemberWareOrder.discount
            cell['支付金额'] = round(item.MemberWareOrder.discount_price / 100, 2)
            cell['开始时间'] = item.MemberWareOrder.start_time.strftime('%Y-%m-%d %H:%M:%S')
            cell['到期时间'] = item.MemberWareOrder.end_time.strftime('%Y-%m-%d %H:%M:%S')
            now = datetime.datetime.now()
            if now < item.MemberWareOrder.start_time:
                cell['状态'] = '未开始'
            elif item.MemberWareOrder.start_time <= now <= item.MemberWareOrder.end_time:
                cell['状态'] = '服务中'
            elif now > item.MemberWareOrder.end_time:
                cell['状态'] = '已过期'
            res.append(cell)
            i += 1
        return excel.make_response_from_records(res, file_type='xls', file_name='vip_members_details')
    elif export_type == 20:
        name = request.args.get('name')
        position = request.args.get('position', type=int)
        source = request.args.get('source', type=int)
        status = request.args.get('status', type=int)
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d').date()
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d').date()

        query = InteractiveAds.query
        if name is not None:
            if name != '':
                query = query.filter(InteractiveAds.name.like('%' + name + '%'))
        if position is not None:
            if position != -1:
                query = query.filter_by(position=position)
        if source is not None:
            if source != -1:
                query = query.filter_by(source=source)
        if status is not None:
            if status != -1:
                query = query.filter_by(status=status)

        res = []
        i = 1
        for info in query.all():
            click_number = 0
            total_click_number = 0
            total_click_query_all = db.session.query(func.sum(InteractiveAdsStatistics.count), func.count()).filter_by(
                ad_id=info.id, operation=1)
            if start_time is not None and end_time is not None:
                click_info = total_click_query_all.filter(InteractiveAdsStatistics.record_time.between(
                    start_time, end_time)).first()

            total_display_number = 0
            display_number = 0

            if click_info is not None:
                if click_info[1] is not None:
                    click_number = click_info[1]
                if click_info[0] is not None:
                    total_click_number = click_info[0]

            cell = OrderedDict()
            cell['序号'] = i
            cell['广告ID'] = info.id
            cell['广告名称'] = info.name
            cell['广告来源'] = current_app.config['INTERACTIVE_ADS_SOURCE'][info.source]
            cell['广告位置'] = current_app.config['INTERACTIVE_ADS_POSITION'][info.position]
            cell['总展现量'] = total_display_number
            cell['去重展现量'] = display_number
            cell['总点击量'] = total_click_number
            cell['去重点击量'] = click_number
            if info.status == 0:
                cell['状态'] = '关闭'
            else:
                cell['状态'] = '开启'
            res.append(cell)
            i += 1
        return excel.make_response_from_records(res, file_type="xls", file_name='interactive_ads')
    elif export_type == 21:
        var_id = request.args.get('id')
        query = Key.query.filter_by(key_record_id=var_id)
        status = request.args.get('status', type=int)
        if status is not None:
            if status != -1:
                query = query.filter(Key.status == status)
        dic = {}
        for key in query.filter(Key.status.in_([1, 3])):
            imei_list = []
            user_key = UserKeyRecord.query.filter_by(key_id=key.id)
            if user_key.first() is not None:
                for u_key in user_key:
                    imei_list.append(u_key.imei)
                dic[key.id] = [imei_list, user_key.first().activate_time]

        res = []
        i = 1
        for info in query.all():
            cell = OrderedDict()
            cell['序号'] = i
            cell['Key-ID'] = info.id
            if info.status == 1 or info.status == 3:
                try:
                    cell['激活时间'] = dic[info.id][1]
                    cell['IMEI'] = ','.join(dic[info.id][0])
                except Exception as e:
                    print(e)
                    cell['激活时间'] = ""
                    cell['IMEI'] = ""
            else:
                cell['激活时间'] = ""
                cell['IMEI'] = ""
            if info.status == 0:
                cell['状态'] = '未激活'
            elif info.status == 1:
                cell['状态'] = '激活'
            elif info.status == 2:
                cell['状态'] = '过期'
            elif info.status == 3:
                cell['状态'] = '使用结束'
            res.append(cell)
            i += 1
        return excel.make_response_from_records(res, file_type="xls", file_name='key_detail_all')

    elif export_type == 22:
        var_id = request.args.get('id')
        query = Key.query.filter_by(key_record_id=var_id)
        status = request.args.get('status', type=int)
        if status is not None:
            if status != -1:
                query = query.filter(Key.status == status)

        dic = {}
        for key in query.filter_by(status=1):
            user_key = UserKeyRecord.query.filter_by(key_id=key.id).first()
            if user_key is not None:
                dic[key.id] = [user_key.imei, user_key.activate_time]
        res = []
        i = 1
        for info in query.all():
            cell = OrderedDict()
            cell['序号'] = i
            cell['Key-ID'] = info.id
            res.append(cell)
            i += 1
        return excel.make_response_from_records(res, file_type="xls", file_name='key_detail_id')

    elif export_type == 23:
        query = KeyOrder.query.join(Key, Key.id == KeyOrder.key_id).add_entity(Key)
        status = request.args.get('status', type=int)
        o_id = request.args.get('o_id')

        if status is not None:
            if status != -1:
                query = query.filter(Key.status == status)
        if o_id is not None:
            if o_id != '':
                query = query.filter(KeyOrder.id.like('%' + o_id + '%'))

        dic = {}
        for key in query.filter(Key.status.in_([1, 3])):
            imei_list = []
            user_key = UserKeyRecord.query.filter_by(key_id=key.Key.id)
            if user_key.first() is not None:
                for u_key in user_key:
                    imei_list.append(u_key.imei)
                dic[key.Key.id] = [imei_list, user_key.first().activate_time]
        res = []
        i = 1
        for info in query.all():
            cell = OrderedDict()
            cell['序号'] = i
            cell['订单编号'] = info.KeyOrder.id
            cell['Key-ID'] = info.KeyOrder.key_id
            if info.Key.status == 1 or info.Key.status == 3:
                cell['激活时间'] = dic[info.Key.id][1]
                cell['IMEI'] = ','.join(dic[info.Key.id][0])
            else:
                cell['激活时间'] = ""
                cell['IMEI'] = ""
            if info.Key.status == 0:
                cell['状态'] = '未激活'
            elif info.Key.status == 1:
                cell['状态'] = '激活'
            elif info.Key.status == 2:
                cell['状态'] = '过期'
            elif info.Key.status == 3:
                cell['状态'] = '使用结束'

            cell['购买金额'] = round(info.KeyOrder.price / 100, 2)
            res.append(cell)
            i += 1
        return excel.make_response_from_records(res, file_type="xls", file_name='order_key_all')

    elif export_type == 24:
        query = KeyOrder.query.join(Key, Key.id == KeyOrder.key_id).add_entity(Key)
        status = request.args.get('status', type=int)
        o_id = request.args.get('o_id')

        if status is not None:
            if status != -1:
                query = query.filter(Key.status == status)
        if o_id is not None:
            if o_id != '':
                query = query.filter(KeyOrder.id.like('%' + o_id + '%'))

        dic = {}
        for key in query.filter(Key.status == 1):
            user_key = UserKeyRecord.query.filter_by(key_id=key.Key.id).first()
            if user_key is not None:
                dic[key.Key.id] = [user_key.activate_time]
        res = []
        i = 1
        for info in query.all():
            cell = OrderedDict()
            cell['序号'] = i
            cell['Key-ID'] = info.KeyOrder.key_id
            res.append(cell)
            i += 1
        return excel.make_response_from_records(res, file_type="xls", file_name='order_key_id')
    elif export_type == 25:
        query = KeyRecord.query
                # .filter(KeyRecord.oeprator.notin_(['Webusiness', 'crack']))
        oeprator = request.args.get('oeprator')
        channel_id = request.args.get('channel_id')
        channel_name = request.args.get('channel_name')
        content = request.args.get('content')

        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        if start_time is not None and end_time is not None:
            if start_time != '' and end_time != '':
                query = query.filter(KeyRecord.create_time.between(start_time, end_time))
        if oeprator is not None:
            if oeprator != '':
                query = query.filter(KeyRecord.oeprator.like('%' + oeprator + '%'))
        if content is not None:
            if content != '':
                query = query.filter(KeyRecord.content.like('%' + content + '%'))
        if channel_id is not None:
            if channel_id != '':
                query = query.filter(ChannelAccount.channel_id.like('%' + channel_id + '%'))
        if channel_name is not None:
            if channel_name != '':
                query = query.filter(ChannelAccount.channel_name.like('%' + channel_name + '%'))

        res = []
        i = 1
        for record in query.all():
            count_0 = db.session.query(Key.id).filter_by(status=0, key_record_id=record.id).count()
            count_1 = db.session.query(Key.id).filter_by(status=1, key_record_id=record.id).count()
            count_2 = db.session.query(Key.id).filter_by(status=2, key_record_id=record.id).count()
            cell = OrderedDict()
            cell['序号'] = i
            cell['渠道ID'] = record.account.channel_id
            cell['渠道名称'] = record.account.channel_name
            cell['创建批次'] = record.id
            cell['创建时间'] = record.create_time
            cell['激活码时长(天)'] = record.vip_time
            cell['创建数量'] = record.count
            cell['已激活'] = count_1
            cell['未激活'] = count_0
            cell['免广告时间(天)'] = record.vip_ad_time
            cell['会员分成'] = record.vip_ad_time
            cell['第三方分成'] = record.vip_ad_time
            cell['操作人'] = record.oeprator
            cell['备注'] = record.content
            res.append(cell)
            i += 1
        return excel.make_response_from_records(res, file_type="xls", file_name='key_record')
    elif export_type == 26:
        query = KeyRecord.query
        phone_num = request.args.get('phone_num')
        operator = request.args.get('operator')
        we_key_number = request.args.get('we_key_number')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

        if start_time is not None and end_time is not None:
            if start_time != '' and end_time != '':
                query = query.filter(KeyRecord.create_time.between(start_time, end_time))
        if phone_num is not None:
            if phone_num != '':
                query = query.filter(KeyRecord.phone_num.like('%' + phone_num + '%'))
        if we_key_number is not None:
            if we_key_number != '':
                query = query.filter(KeyRecord.we_record_id == we_key_number)
        if operator is not None:
            if operator != '':
                query = query.filter(KeyRecord.oeprator.like('%' + operator + '%'))
        else:
            query = query.filter(KeyRecord.oeprator.in_(['Webusiness', 'crack']))

        dic = {}
        res = []
        i = 1
        for record in query.all():
            count_0 = db.session.query(Key.id).filter_by(status=0, key_record_id=record.id).count()
            count_1 = db.session.query(Key.id).filter(Key.status.in_([1, 3]), Key.key_record_id == record.id).count()
            count_2 = db.session.query(Key.id).filter_by(status=2, key_record_id=record.id).count()
            cell = OrderedDict()
            print(record.oeprator)
            cell['序号'] = i
            cell['手机号'] = record.phone_num
            cell['key记录编号'] = record.we_record_id
            cell['创建时间'] = record.create_time
            # cell['有效期截至'] = record.expire_time
            cell['VIP有效期(天)'] = record.vip_time
            cell['创建数量'] = record.count
            cell['已激活'] = count_1
            cell['未激活'] = count_0
            cell['过期未使用'] = count_2
            cell['免广告时间(天)'] = record.vip_ad_time
            cell['操作人'] = record.oeprator
            cell['备注'] = record.content
            res.append(cell)
            i += 1
        return excel.make_response_from_records(res, file_type="xls", file_name='we_key_record')
    # activate_member
    elif export_type == 27:
        query = ActivateMembers.query.join(GodinAccount, GodinAccount.godin_id == ActivateMembers.godin_id). \
            add_entity(GodinAccount)

        phone_num = request.args.get('phone_num')
        vip_type = request.args.get('vip_type', type=int)
        channel = request.args.get('channel')
        status = request.args.get('status', type=int)
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        if phone_num is not None:
            if phone_num != '':
                query = query.filter(GodinAccount.phone_num.like('%' + phone_num + '%'))
        if vip_type is not None:
            if vip_type != -1:
                query = query.filter(ActivateMembers.vip_type == vip_type)
        if channel is not None:
            if channel != '全部':
                query = query.filter(ActivateMembers.channel == channel)
        if status is not None:
            if status != -1:
                query = query.filter(ActivateMembers.status == status)
        if start_time is not None and end_time is not None:
            if start_time != '' and end_time != '':
                query = query.filter(ActivateMembers.create_time.between(start_time, end_time))

        res = []
        i = 1
        for info in query.all():
            cell = OrderedDict()
            cell['序号'] = i
            cell['手机号'] = info.GodinAccount.phone_num
            cell['国鼎ID'] = info.ActivateMembers.godin_id
            cell['渠道'] = info.ActivateMembers.channel
            if info.ActivateMembers.vip_type == 0:
                cell['添加方式'] = '手动添加'
            else:
                cell['添加方式'] = '活动添加'
            if info.ActivateMembers.status == 0:
                cell['是否激活'] = '未激活'
            else:
                cell['是否激活'] = '已激活'
            cell['商品ID'] = info.ActivateMembers.ware_id
            cell['添加时间'] = info.ActivateMembers.create_time
            res.append(cell)
            i += 1
        return excel.make_response_from_records(res, file_type="xls", file_name='act_member')
    elif export_type == 30:
        query = BusinessWare.query.order_by(BusinessWare.id.desc())
        category = request.args.get('category')
        status = request.args.get('status', type=int)

        if category is not None:
            if category != '':
                vip_type = BusinessType.query.filter_by(name=category).first()
                if vip_type is not None:
                    type_number = vip_type.number
                else:
                    type_number = 0
                query = query.filter_by(category=type_number)
        if status is not None:
            if status != -1:
                query = query.filter_by(status=status)
        res = []
        i = 1
        for ware in query.all():
            vip_type = BusinessType.query.filter_by(number=ware.category).first()

            cell = OrderedDict()
            cell['序号'] = i
            if vip_type is not None:
                cell['VIP类型'] = vip_type.name
            cell['VIP名称'] = ware.name
            if ware.status == 0:
                cell['显示状态'] = '无效'
            elif ware.status == 1:
                cell['显示状态'] = '有效'
            res.append(cell)
            i += 1
        return excel.make_response_from_records(res, file_type='xls', file_name='bus_ware')
    elif export_type == 28:
        query = BusinessMembers.query.join(GodinAccount, GodinAccount.godin_id == BusinessMembers.godin_id). \
            add_entity(GodinAccount).order_by(BusinessMembers.first_pay_time.desc())
        phone_num = request.args.get('phone_num')
        status = request.args.get('status', -1, type=int)
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')

        if phone_num is not None:
            if phone_num != '':
                query = query.filter(GodinAccount.phone_num.like('%' + phone_num + '%'))
        if status is not None:
            status = status
            if status != -1:
                query = query.filter(BusinessMembers.status == status)
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            query = query.filter(BusinessMembers.first_pay_time.between(start_time, end_time))
        res = []
        i = 1
        for vip in query.all():
            cell = OrderedDict()
            cell['序号'] = i
            cell['手机号'] = vip.GodinAccount.phone_num
            if vip.BusinessMembers.first_pay_time is not None:
                cell['首次购买时间'] = vip.BusinessMembers.first_pay_time.strftime('%Y-%m-%d %H:%M:%S')
            else:
                cell['首次购买时间'] = vip.BusinessMembers.first_pay_time
            if vip.BusinessMembers.valid_time is not None:
                cell['到期时间'] = vip.BusinessMembers.valid_time.strftime('%Y-%m-%d %H:%M:%S')
            else:

                cell['到期时间'] = vip.BusinessMembers.valid_time
            if vip.BusinessMembers.status == 0:
                cell['状态'] = '已过期'
            elif vip.BusinessMembers.status == 1:
                cell['状态'] = '正常'
            res.append(cell)
            i += 1
        return excel.make_response_from_records(res, file_type='xls', file_name='bus_members')
    # export vip member details
    elif export_type == 29:
        godin_id = request.args.get('godin_id')
        query = BusinessWareOrder.query.join(BusinessWare, BusinessWare.id == BusinessWareOrder.ware_id
                                             ).add_entity(BusinessWare).filter(
            BusinessWareOrder.buyer_godin_id == godin_id, BusinessWareOrder.status == 1). \
            order_by(BusinessWareOrder.pay_time.desc())
        pay_type = request.args.get('pay_type', -1, type=int)
        category = request.args.get('category')
        status = request.args.get('status')
        order_number = request.args.get('order_number')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if pay_type is not None:
            if pay_type != -1:
                query = query.filter(BusinessWareOrder.pay_type == pay_type)
        if category is not None:
            if category != '':
                vip_type = BusinessType.query.filter_by(name=category).first()
                if vip_type is not None:
                    query = query.filter(BusinessWare.category == vip_type.number)
        if status is not None:
            if status == 0:
                query = query.filter(BusinessWareOrder.end_time < datetime.datetime.now())
            elif status == 1:
                query = query.filter(datetime.datetime.now() > BusinessWareOrder.start_time,
                                     datetime.datetime.now() < BusinessWareOrder.end_time)
            elif status == 2:
                query = query.filter(BusinessWareOrder.start_time > datetime.datetime.now())
        if order_number is not None:
            if order_number != '':
                query = query.filter(BusinessWareOrder.order_number.like('%' + order_number + '%'))
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            query = query.filter(BusinessWareOrder.create_time.between(start_time, end_time))
        res = []
        i = 1
        for item in query.all():
            vip_type = BusinessType.query.filter_by(number=item.BusinessWare.category).first()
            cell = OrderedDict()
            cell['序号'] = i
            cell['订单编号'] = item.BusinessWareOrder.order_number
            cell['订单时间'] = item.BusinessWareOrder.create_time.strftime('%Y-%m-%d %H:%M:%S')
            if item.BusinessWareOrder.pay_type == 0:
                cell['支付方式'] = '微信'
            elif item.BusinessWareOrder.pay_type == 1:
                cell['支付方式'] = '支付宝'
            elif item.BusinessWareOrder.pay_type == 2:
                cell['支付方式'] = '其他'
            if item.BusinessWareOrder.pay_time is not None:
                cell['支付时间'] = item.BusinessWareOrder.pay_time.strftime('%Y-%m-%d %H:%M:%S')
            else:
                cell['支付时间'] = item.BusinessWareOrder.pay_time
            if vip_type is not None:
                cell['类型'] = vip_type.name
            cell['产品标价'] = round(item.BusinessWareOrder.ware_price / 100, 2)
            cell['折扣信息(%)'] = item.BusinessWareOrder.discount
            cell['支付金额'] = round(item.BusinessWareOrder.discount_price / 100, 2)
            cell['开始时间'] = item.BusinessWareOrder.start_time.strftime('%Y-%m-%d %H:%M:%S')
            cell['到期时间'] = item.BusinessWareOrder.end_time.strftime('%Y-%m-%d %H:%M:%S')
            now = datetime.datetime.now()
            if now < item.BusinessWareOrder.start_time:
                cell['状态'] = '未开始'
            elif item.BusinessWareOrder.start_time <= now <= item.BusinessWareOrder.end_time:
                cell['状态'] = '服务中'
            elif now > item.BusinessWareOrder.end_time:
                cell['状态'] = '已过期'
            res.append(cell)
            i += 1
        return excel.make_response_from_records(res, file_type='xls', file_name='business_members_details')
    # export bus give statistics
    elif export_type == 32:
        query = BusinessGiveStatistics.query.order_by(BusinessGiveStatistics.create_time.desc())
        phone_num = request.args.get('phone_num')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if phone_num is not None:
            if phone_num != '':
                query = query.filter(BusinessGiveStatistics.phone_num.like('%' + phone_num + '%'))

        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            query = query.filter(BusinessGiveStatistics.create_time.between(start_time, end_time))
        res = []
        i = 1
        for item in query.all():
            cell = OrderedDict()
            cell['序号'] = i
            cell['手机号'] = item.phone_num
            cell['增送天数'] = item.days
            cell['添加时间'] = item.create_time.strftime('%Y-%m-%d %H:%M:%S')
            res.append(cell)
            i += 1
        return excel.make_response_from_records(res, file_type='xls', file_name='bus_give_stat')
    elif export_type == 33:
        query = InviteEarnRecord.query
        channel_id = request.args.get('channel_id')
        invite_phone = request.args.get('invite_phone')
        phone = request.args.get('phone')
        if channel_id is not None:
            if channel_id != '':
                query = query.filter(InviteEarnRecord.channel_id.like('%' + channel_id + '%'))

        if invite_phone is not None:
            if invite_phone != '':
                query = query.filter(InviteEarnRecord.phone_num.like(invite_phone + '%'))

        if phone is not None:
            if phone != '':
                query = query.filter(InviteEarnRecord.be_invited_phone.like(phone + '%'))
        res = []
        i = 1
        for item in query.all():
            cell = OrderedDict()
            cell['序号'] = i
            cell['时间'] = item.create_time.strftime('%Y-%m-%d %H:%M:%S')
            cell['渠道ID'] = item.channel_id
            cell['渠道名称'] = item.channel_name
            cell['邀请人手机号'] = item.phone_num
            cell['被邀请人手机号'] = item.be_invited_phone
            cell['key_id'] = item.key_id
            cell['key价格'] = item.price / 100
            cell['邀请者分成比例'] = item.inviter_per
            cell['渠道分成比例'] = item.channel_per
            cell['邀请者收益'] = item.inviter_earn / 100
            cell['渠道收益'] = item.channel_earn / 100
            res.append(cell)
            i += 1
        return excel.make_response_from_records(res, file_type='xls', file_name='invite_code_earn')
    elif export_type == 34:
        query = UserGeneralize.query
        phone_num = request.args.get('phone_num')

        if phone_num is not None and phone_num != '':
            query = query.filter(UserGeneralize.phone_num.like('{0}%'.format(phone_num)))
        else:
            query = query.filter(UserGeneralize.invite_person_num > 0)

        res = []
        i = 1
        for item in query.all():
            cell = OrderedDict()
            cell['序号'] = i
            cell['邀请人手机号'] = item.phone_num
            cell['邀请人数'] = item.invite_person_num
            cell['注册人数'] = item.register_person_num
            cell['付费人数'] = get_pay_person_num(item.godin_id)
            cell['总收益'] = deal_float((item.member_award + item.active_code_award) / 100)
            cell['会员收益'] = deal_float(item.member_award / 100)
            cell['激活码收益'] = deal_float(item.active_code_award / 100)
            cell['账户余额'] = deal_float(item.account_balance / 100)
            res.append(cell)
            i += 1
        return excel.make_response_from_records(res, file_type='xls', file_name='user_generalize_earn')
    else:
        pass


@login_required
def release_app():
    app_version = AppVersion.query.filter_by(id=request.args.get('id', type=int)).first()
    if app_version is not None:
        if app_version.is_released:
            code = 1
            app_version.is_released = False
            add_admin_log(user=current_user.username, actions='取消发布',
                          client_ip=request.remote_addr, results='成功')
        else:
            code = 0
            app_version.is_released = True
            add_admin_log(user=current_user.username, actions='发布',
                          client_ip=request.remote_addr, results='成功')
        db.session.add(app_version)
        db.session.commit()
        cache.delete('get_valid_app_version_name')
        cache.delete('get_app_version_list')
        if app_version.app_type == 99:
            cache.delete('feature_file')
        return jsonify(code=code)
    return jsonify(code=-2)


@login_required
def list_duty_manager():
    page = request.args.get('page', 1, type=int)
    pagination = DutyManager.query.order_by(DutyManager.id.asc()). \
        paginate(page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    users = pagination.items
    add_admin_log(user=current_user.username, actions='查询DM', client_ip=request.remote_addr, results='成功')
    return render_template("manage/duty_manager.html", users=users, pagination=pagination, action="LIST")


@login_required
def add_duty_manager():
    form = AddDutyManagerForm()
    if form.validate_on_submit():
        user = DutyManager()
        user.username = form.name.data
        user.email = form.email.data
        db.session.add(user)
        db.session.commit()
        add_admin_log(user=current_user.username, actions='添加DM', client_ip=request.remote_addr, results='成功')
        return redirect(url_for('manage.list_duty_manager'))
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
    return render_template("manage/duty_manager.html", form=form, action="ADD")


@login_required
def del_duty_manager():
    DutyManager.query.filter_by(id=request.args.get('id', type=int)).delete()
    db.session.commit()
    add_admin_log(user=current_user.username, actions='删除DM', client_ip=request.remote_addr, results='成功')
    return jsonify(code=0)


@login_required
def set_duty_manager_status():
    user = DutyManager.query.filter_by(id=request.args.get('id', type=int)).first()
    if user is not None:
        if user.on_duty:
            user.on_duty = False
            action = '禁止DM'
        else:
            user.on_duty = True
            action = '启用DM'
        db.session.add(user)
        db.session.commit()
        add_admin_log(user=current_user.username, actions=action, client_ip=request.remote_addr, results='成功')
    return jsonify(code=0)


@login_required
def list_spread_manager():
    page = request.args.get('page', 1, type=int)
    pagination = SpreadManager.query.order_by(SpreadManager.id.asc()). \
        paginate(page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    users = pagination.items
    add_admin_log(user=current_user.username, actions='查询推广人员', client_ip=request.remote_addr, results='成功')
    return render_template("manage/spread_manager.html", users=users, pagination=pagination, action="LIST")


@login_required
def add_spread_manager():
    form = AddSpreadManagerForm()
    if form.validate_on_submit():
        user = SpreadManager()
        user.username = form.name.data
        user.email = form.email.data
        user.channelname = form.channel.data
        user.url_suffix = form.suffix.data
        db.session.add(user)
        db.session.commit()
        add_admin_log(user=current_user.username, actions='添加推广人员', client_ip=request.remote_addr, results='成功')
        return redirect(url_for('manage.list_spread_manager'))
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
    return render_template("manage/spread_manager.html", form=form, action="ADD")


@login_required
def del_spread_manager():
    SpreadManager.query.filter_by(id=request.args.get('id', type=int)).delete()
    db.session.commit()
    add_admin_log(user=current_user.username, actions='删除推广人员', client_ip=request.remote_addr, results='成功')
    return jsonify(code=0)


@login_required
def del_feedback():
    FeedBack.query.filter_by(id=request.args.get('id', type=int)).delete()
    db.session.commit()
    add_admin_log(user=current_user.username, actions='删除用户反馈', client_ip=request.remote_addr, results='成功')
    return jsonify(code=0)


@login_required
def get_next_day_stay_statistics():
    form = NextDayStayStatisticsForm()
    results = []
    if form.validate_on_submit():
        date = form.date.data
        results = NextDayStay.query.filter_by(date=date).all()
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='获取次日留存用户统计',
                      client_ip=request.remote_addr, results=error[0])
    if not form.errors:
        add_admin_log(user=current_user.username, actions='获取次日留存用户统计',
                      client_ip=request.remote_addr, results='成功')
    return render_template("manage/next_day_stay.html", form=form, data=results)


@celery.task(name='make_next_day_stay_report')
def make_next_day_stay_report():
    channels = db.session.query(DeviceInfo.market.distinct())
    now_date = datetime.datetime.now().strftime('%Y-%m-%d')
    today_start_time = datetime.datetime.strptime(now_date + " 00:00:00",
                                                  '%Y-%m-%d %H:%M:%S') - datetime.timedelta(days=1)
    today_end_time = datetime.datetime.strptime(now_date + " 23:59:59",
                                                '%Y-%m-%d %H:%M:%S') - datetime.timedelta(days=1)
    last_day_start_time = today_start_time - datetime.timedelta(days=1)
    last_day_end_time = today_end_time - datetime.timedelta(days=1)
    if NextDayStay.query.filter_by(date=now_date).order_by(desc(NextDayStay.id)).limit(1).first() is not None:
        return False
    for channel in channels:
        query = DeviceInfo.query.filter_by(market=channel[0]). \
            filter(DeviceInfo.create_time.between(last_day_start_time, last_day_end_time))
        last_come_count = query.count()
        stay_count = query.filter(DeviceInfo.last_seen.between(today_start_time, today_end_time)).count()
        next_day_stay = NextDayStay()
        next_day_stay.channel = channel[0]
        next_day_stay.date = now_date
        next_day_stay.last_come_count = last_come_count
        next_day_stay.stay_count = stay_count
        if last_come_count == 0:
            next_day_stay.stay_percent = round(stay_count / 1, 2)
        else:
            next_day_stay.stay_percent = round(stay_count / last_come_count, 2)
        db.session.add(next_day_stay)
        db.session.commit()

        # 每天凌晨更新优先级最高的数量限制清零，从新开始
        date_value = datetime.datetime.now().date()
        DataLock.query.filter(DataLock.id == 1, DataLock.update_time < date_value).update(
            dict(count=0, update_time=date_value))
        db.session.commit()
    return True


@login_required
def set_hide_icon_status():
    flag = request.args.get('flag', 0, type=int)
    # hide_icon_switch 0 开启隐藏图标, 1 显示图标
    switch_status = cache.get('hide_icon_switch')
    if switch_status is None:
        flag = 0
        cache.set('hide_icon_switch', 0, timeout=3600 * 24 * 365 * 2)
        return render_template('manage/set_hide_icon.html', data=flag)
    elif flag == -1:
        flag = switch_status
        return render_template('manage/set_hide_icon.html', data=flag)
    else:
        cache.set('hide_icon_switch', flag, timeout=3600 * 24 * 365 * 2)

    add_admin_log(user=current_user.username, actions='设置隐藏图标', client_ip=request.remote_addr,
                  results='成功')
    return jsonify({'code': 0})


@login_required
def add_open_screen_ads():
    form = AddOpenScreenAdsForm()
    if form.validate_on_submit():
        name = form.name.data
        position = form.position.data
        source = form.source.data
        charge_mode = form.charge_mode.data
        unit_price = int(round(form.unit_price.data, 2) * 100)
        advertiser = form.advertiser.data
        contacts = form.contacts.data
        contact_way = form.contact_way.data
        number = form.number.data
        refresh_status = form.refresh_status.data
        user_count = form.user_count.data
        morning_count = form.morning_count.data
        afternoon_count = form.afternoon_count.data
        night_count = form.night_count.data
        display_number = form.display_number.data
        skip_time = form.skip_time.data
        start_time = form.start_time.data
        end_time = form.end_time.data
        virtual_skip = form.virtual_skip.data
        control_click_rate = form.control_click_rate.data
        if control_click_rate > 100 or control_click_rate < 0:
            flash("控制率需要100以内的整数")
            add_admin_log(user=current_user, actions='添加开屏广告', client_ip=request.remote_addr,
                          results='参数错误')
            return render_template("manage/add_open_screen_ads.html", form=form)
        skip_count = form.skip_count.data
        icon = request.files['icon']
        icon_size = len(icon.read())
        icon_name = secure_filename(icon.filename)
        app_link = form.app_link.data

        icon_flag = False
        new_icon_name = str(round(time.time()))
        icon_dir = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], 'OpenScrrenAds')
        if not os.path.exists(icon_dir):
            os.makedirs(icon_dir)

        if icon_size > 0 and form.source.data == 0:
            if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', icon.filename.rsplit('.', 1)[0])):
                flash('图片名称不能为纯汉字')
                add_admin_log(user=current_user.username, actions='添加开屏广告', client_ip=request.remote_addr,
                              results='图片名称不能为纯汉字')
                return render_template("manage/add_open_screen_ads.html", form=form)
            if icon_size > 100 * 1024 or icon_name.rsplit('.', 1)[1] not in ['jpg', 'png', 'jpeg', 'JPG', 'JPEG',
                                                                             'PNG']:
                flash("图片格式不否, 仅支持(jpg/jpeg, png) 小余100k")
                add_admin_log(user=current_user, actions='添加开屏广告', client_ip=request.remote_addr,
                              results='图片格式错误')
                return render_template("manage/add_open_screen_ads.html", form=form)

            img = Image.open(icon)
            new_icon_name = icon_name.rsplit('.', 1)[0] + '_' + new_icon_name + '.' + icon_name.rsplit('.', 1)[1]
            img.save(os.path.join(icon_dir, new_icon_name))
            icon_flag = True

        info = OpenScreenAds()
        info.name = name
        info.position = position
        info.source = source
        info.charge_mode = charge_mode
        info.unit_price = unit_price
        info.advertiser = advertiser
        info.contacts = contacts
        info.contact_way = contact_way
        info.number = number
        info.display_number = display_number
        info.skip_time = skip_time
        info.start_time = start_time
        info.end_time = end_time
        info.virtual_skip = virtual_skip
        info.control_click_rate = control_click_rate
        info.skip_count = skip_count
        info.app_link = app_link.strip()
        info.refresh_status = refresh_status
        info.user_count = user_count
        info.morning_count = morning_count
        info.afternoon_count = afternoon_count
        info.night_count = night_count
        if icon_flag:
            info.icon = os.path.join(current_app.config['PHOTO_TAG'], 'OpenScrrenAds', new_icon_name)

        try:
            db.session.add(info)
            db.session.commit()
            add_admin_log(user=current_user.username, actions='添加开屏广告', client_ip=request.remote_addr,
                          results='成功')
            return redirect(url_for('manage.get_open_screen_ads'))
        except Exception as e:
            print(e)
            db.session.rollback()
            new_icon_name = os.path.join(icon_dir, new_icon_name)
            if icon_flag and os.path.exists(new_icon_name) and os.path.isfile(new_icon_name):
                os.remove(new_icon_name)
            add_admin_log(user=current_user.username, actions='添加开屏广告', client_ip=request.remote_addr,
                          results='失败')
            flash('添加开屏广告失败')
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='添加开屏广告', client_ip=request.remote_addr, results=error[0])

    return render_template("manage/add_open_screen_ads.html", form=form)


@login_required
def get_open_screen_ads():
    form = QueryOpenScreenAdsForm()
    query = OpenScreenAds.query
    if form.validate_on_submit():
        name = form.name.data
        position = form.position.data
        source = form.source.data
        status = form.status.data
        start_time = form.start_time.data
        end_time = form.end_time.data
    else:
        name = request.args.get('name')
        position = request.args.get('position', type=int)
        source = request.args.get('source', type=int)
        status = request.args.get('status', type=int)
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d').date()
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d').date()

    if name is not None:
        form.name.data = name
        if form.name.data != '':
            query = query.filter(OpenScreenAds.name.like('%' + form.name.data + '%'))
    if position is not None:
        form.position.data = position
        if form.position.data != -1:
            query = query.filter_by(position=form.position.data)
    if source is not None:
        form.source.data = source
        if form.source.data != -1:
            query = query.filter_by(source=form.source.data)
    if status is not None:
        form.status.data = status
        if form.status.data != -1:
            query = query.filter_by(status=form.status.data)

    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)

    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
    else:
        days = datetime.datetime.now() - datetime.timedelta(days=6)
        end_time = datetime.datetime.now().date()
        start_time = days.date()
        form.start_time.data = start_time
        form.end_time.data = end_time

    res = []
    for open_ads in pagination.items:
        total_click_rate = 0.0
        real_click_rate = 0.0

        total_display_query_all = db.session.query(func.sum(OpenScreenAdsStatistics.count), func.count()).filter_by(
            ad_id=open_ads.id, operation=0)
        total_click_query_all = db.session.query(func.sum(OpenScreenAdsStatistics.count), func.count()).filter_by(
            ad_id=open_ads.id, operation=1)
        real_click_query = db.session.query(func.sum(OpenScreenAdsStatistics.count)).filter_by(
            ad_id=open_ads.id, operation=2)
        if start_time is not None and end_time is not None:
            display_info = total_display_query_all.filter(OpenScreenAdsStatistics.record_time.between(
                start_time, end_time)).first()
            click_info = total_click_query_all.filter(OpenScreenAdsStatistics.record_time.between(
                start_time, end_time)).first()
            real_click_number = real_click_query.filter(OpenScreenAdsStatistics.record_time.between(
                start_time, end_time)).first()[0]
            if real_click_number is None:
                real_click_number = 0

        if display_info is not None:
            if display_info[1] is None:
                display_number = 0
            else:
                display_number = display_info[1]
            if display_info[0] is None:
                total_display_number = 0
            else:
                total_display_number = display_info[0]
        else:
            display_number = 0
            total_display_number = 0

        if real_click_number is None:
            real_click_number = 0

        if click_info is not None:
            if click_info[1] is None:
                click_number = 0
            else:
                click_number = click_info[1]
            if click_info[0] is None:
                total_click_number = 0
            else:
                total_click_number = click_info[0]
        else:
            click_number = 0
            total_click_number = 0

        # 昨天统计
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        yesterday_total_display_number = total_display_query_all.filter(
            OpenScreenAdsStatistics.record_time == yesterday.date()).first()[0]
        yesterday_total_click_number = total_click_query_all.filter(
            OpenScreenAdsStatistics.record_time == yesterday.date()).first()[0]
        yesterday_real_click_number = real_click_query.filter(
            OpenScreenAdsStatistics.record_time == yesterday.date()).first()[0]
        if yesterday_total_display_number is None:
            yesterday_total_display_number = 0
        if yesterday_total_click_number is None:
            yesterday_total_click_number = 0
        if yesterday_real_click_number is None:
            yesterday_real_click_number = 0

        if yesterday_total_display_number != 0:
            total_click_rate = round((yesterday_total_click_number / yesterday_total_display_number) * 100, 2)
            real_click_rate = round((yesterday_real_click_number / yesterday_total_display_number) * 100, 2)

        cell = dict(id=open_ads.id, name=open_ads.name, source=open_ads.source, position=open_ads.position,
                    advertiser=open_ads.advertiser, number=open_ads.number, total_display_number=total_display_number,
                    display_number=display_number, click_number=click_number, total_click_number=total_click_number,
                    real_click_number=real_click_number, total_click_rate=total_click_rate,
                    real_click_rate=real_click_rate, start_time=open_ads.start_time, status=open_ads.status)
        res.append(cell)

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='查看开屏广告', client_ip=request.remote_addr,
                      results=error[0])
    if not form.errors:
        add_admin_log(user=current_user.username, actions='查看开屏广告', client_ip=request.remote_addr,
                      results='成功')
    return render_template("manage/get_open_screen_ads.html", form=form, data=res, pagination=pagination)


@login_required
def set_open_screen_status():
    ad_id = request.args.get('id', type=int)
    status = request.args.get('status', type=int)

    if ad_id < 0 or (status != 0 and status != 1):
        add_admin_log(user=current_user.username, actions='设置开屏广告状态', client_ip=request.remote_addr,
                      results='参数错误')
        return jsonify({'code': 1})
    else:
        try:
            OpenScreenAds.query.filter_by(id=ad_id).update(dict(status=status))
            db.session.commit()

            add_admin_log(user=current_user.username, actions='设置开屏广告状态', client_ip=request.remote_addr,
                          results='成功')
            return jsonify({'code': 0})
        except Exception as e:
            print(e)
            db.session.rollback()
            add_admin_log(user=current_user.username, actions='设置开屏广告状态', client_ip=request.remote_addr,
                          results='失败')
            return jsonify({'code': 1})


@login_required
def open_screen_ads_info(ad_id):
    ad_info = OpenScreenAds.query.filter_by(id=ad_id).first()

    add_admin_log(user=current_user.username, actions='查看开屏广告信息', client_ip=request.remote_addr, results='成功')
    return render_template("manage/open_screen_ads_info.html", data=ad_info, base_url=current_app.config['FILE_SERVER'],
                           ad_id=ad_id)


@login_required
def edit_open_screen_ads(ad_id):
    form = EditOpenScreenAdsForm()
    info = OpenScreenAds.query.filter_by(id=ad_id).first()
    if form.validate_on_submit() and info is not None:
        name = form.name.data
        # position = form.position.data
        # source = form.source.data
        # charge_mode = form.charge_mode.data
        unit_price = int(round(form.unit_price.data, 2) * 100)
        # advertiser = form.advertiser.data
        # contacts = form.contacts.data
        # contact_way = form.contact_way.data
        display_number = form.display_number.data
        skip_time = form.skip_time.data
        start_time = form.start_time.data
        end_time = form.end_time.data
        virtual_skip = form.virtual_skip.data
        control_click_rate = form.control_click_rate.data
        if control_click_rate > 100 or control_click_rate < 0:
            flash("控制率需要100以内的整数")
            add_admin_log(user=current_user, actions='编辑开屏广告', client_ip=request.remote_addr,
                          results='参数错误')
            return redirect(url_for('manage.edit_open_screen_ads', ad_id=ad_id))
        skip_count = form.skip_count.data
        refresh_status = form.refresh_status.data
        user_count = form.user_count.data
        morning_count = form.morning_count.data
        afternoon_count = form.afternoon_count.data
        night_count = form.night_count.data
        icon = request.files['icon']
        icon_size = len(icon.read())
        icon_name = secure_filename(icon.filename)
        app_link = form.app_link.data

        icon_flag = False
        new_icon_name = str(round(time.time()))
        old_icon_name = info.icon
        icon_dir = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], 'OpenScrrenAds')
        if not os.path.exists(icon_dir):
            os.makedirs(icon_dir)

        if icon_size > 0 and form.source.data == 0:
            if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', icon.filename.rsplit('.', 1)[0])):
                flash('图片名称不能为纯汉字')
                add_admin_log(user=current_user.username, actions='编辑开屏广告', client_ip=request.remote_addr,
                              results='图片名称不能为纯汉字')
                return redirect(url_for('manage.edit_open_screen_ads', ad_id=ad_id))
            if icon_size > 100 * 1024 or icon_name.rsplit('.', 1)[1] not in ['jpg', 'png', 'jpeg', 'JPG', 'JPEG',
                                                                             'PNG']:
                flash("图片格式不否, 仅支持(jpg/jpeg, png) 小余100k")
                add_admin_log(user=current_user, actions='编辑开屏广告', client_ip=request.remote_addr,
                              results='图片格式错误')
                return redirect(url_for('manage.edit_open_screen_ads', ad_id=ad_id))

            icon_dir = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], 'OpenScrrenAds')
            if not os.path.exists(icon_dir):
                os.makedirs(icon_dir)

            img = Image.open(icon)
            new_icon_name = icon_name.rsplit('.', 1)[0] + '_' + new_icon_name + '.' + icon_name.rsplit('.', 1)[1]
            img.save(os.path.join(icon_dir, new_icon_name))
            info.icon = os.path.join(current_app.config['PHOTO_TAG'], 'OpenScrrenAds', new_icon_name)
            icon_flag = True

        info.name = name
        # info.position = position
        # info.source = source
        # info.charge_mode = charge_mode
        info.unit_price = unit_price
        # info.advertiser = advertiser
        # info.contacts = contacts
        # info.contact_way = contact_way
        info.display_number = display_number
        info.skip_time = skip_time
        info.start_time = start_time
        info.end_time = end_time
        info.virtual_skip = virtual_skip
        info.control_click_rate = control_click_rate
        info.skip_count = skip_count
        info.app_link = app_link.strip()
        info.refresh_status = refresh_status
        info.user_count = user_count
        info.morning_count = morning_count
        info.afternoon_count = afternoon_count
        info.night_count = night_count

        try:
            db.session.add(info)
            db.session.commit()
            old_icon_name = os.path.join(os.getcwd(), old_icon_name)
            if icon_flag and os.path.exists(old_icon_name) and os.path.isfile(old_icon_name):
                os.remove(old_icon_name)
            add_admin_log(user=current_user.username, actions='编辑开屏广告', client_ip=request.remote_addr,
                          results='成功')
            return redirect(url_for('manage.open_screen_ads_info', ad_id=ad_id))
        except Exception as e:
            print(e)
            db.session.rollback()
            new_icon_name = os.path.join(icon_dir, new_icon_name)
            if icon_flag and os.path.exists(new_icon_name) and os.path.isfile(new_icon_name):
                os.remove(new_icon_name)
            add_admin_log(user=current_user.username, actions='编辑开屏广告', client_ip=request.remote_addr,
                          results='失败')
            flash('编辑开屏广告失败')

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='编辑开屏广告', client_ip=request.remote_addr, results=error[0])
    if info is not None:
        form.name.data = info.name
        form.position.data = info.position
        form.source.data = info.source
        form.charge_mode.data = info.charge_mode
        form.unit_price.data = info.unit_price / 100
        form.advertiser.data = info.advertiser
        form.contacts.data = info.contacts
        form.contact_way.data = info.contact_way
        form.display_number.data = info.display_number
        form.skip_time.data = info.skip_time
        form.start_time.data = info.start_time
        form.end_time.data = info.end_time
        form.virtual_skip.data = info.virtual_skip
        form.control_click_rate.data = info.control_click_rate
        form.skip_count.data = info.skip_count
        form.app_link.data = info.app_link
        form.refresh_status.data = info.refresh_status
        form.user_count.data = info.user_count
        form.morning_count.data = info.morning_count
        form.afternoon_count.data = info.afternoon_count
        form.night_count.data = info.night_count

    if not form.errors:
        add_admin_log(user=current_user.username, actions='编辑开屏广告', client_ip=request.remote_addr, results='成功')

    return render_template("manage/edit_open_screen_ads.html", form=form, ad_id=ad_id)


@login_required
def add_bannerad():
    form = AddBannerAdsForm()
    if form.validate_on_submit():
        icon = request.files['icon']
        icon_name = secure_filename(icon.filename)
        size = len(icon.read())
        icon_flag = False
        new_icon_name = str(round(time.time()))
        icon_dir = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], 'bannerads')
        if not os.path.exists(icon_dir):
            os.makedirs(icon_dir)

        if size > 0 and form.source.data == 0:
            if size > 102400:
                flash('广告图标大小不能超过100K')
                add_admin_log(user=current_user.username, actions='添加banner广告', client_ip=request.remote_addr,
                              results='广告图标大小不能超过100K')
                return render_template('manage/add_bannerads.html', form=form)
            if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', icon.filename.rsplit('.', 1)[0])):
                flash('广告图标名称不能为纯汉字')
                add_admin_log(user=current_user.username, actions='添加banner广告', client_ip=request.remote_addr,
                              results='广告图标名称不能为纯汉字')
                return render_template('manage/add_bannerads.html', form=form)
            if icon_name.rsplit('.', 1)[1] not in ['jpg', 'png', 'JPG', 'PNG']:
                flash('广告图标格式错误')
                add_admin_log(user=current_user.username, actions='添加banner广告', client_ip=request.remote_addr,
                              results='广告图标格式错误')
                return render_template('manage/add_bannerads.html', form=form)
            im = Image.open(icon)
            new_icon_name = icon_name.rsplit('.', 1)[0] + '_' + new_icon_name + '.' + icon_name.rsplit('.', 1)[1]
            im.save(os.path.join(icon_dir, new_icon_name))
            icon_flag = True

        bannerad = BannerAds()
        bannerad.name = form.name.data
        bannerad.position = form.position.data
        bannerad.source = form.source.data
        bannerad.charge_mode = form.charge_mode.data
        bannerad.unit_price = int(round(form.unit_price.data, 2) * 100)
        bannerad.start_time = form.start_time.data
        bannerad.end_time = form.end_time.data
        bannerad.advertiser = form.advertiser.data
        bannerad.contacts = form.contacts.data
        bannerad.contact_way = form.contact_way.data
        bannerad.number = form.number.data
        bannerad.display_number = form.display_number.data
        bannerad.refresh_status = form.refresh_status.data
        bannerad.user_count = form.user_count.data
        bannerad.morning_count = form.morning_count.data
        bannerad.afternoon_count = form.afternoon_count.data
        bannerad.night_count = form.night_count.data
        bannerad.carousel = form.carousel.data
        bannerad.carousel_interval = form.carousel_interval.data
        bannerad.icon_dest_link = form.icon_dest_link.data
        if icon_flag:
            bannerad.icon = os.path.join(current_app.config['PHOTO_TAG'], 'bannerads', new_icon_name)

        try:
            db.session.add(bannerad)
            db.session.commit()
            add_admin_log(user=current_user.username, actions='添加banner广告', client_ip=request.remote_addr,
                          results='成功')
            return redirect(url_for('manage.get_bannerads_info'))
        except Exception as e:
            print(e)
            db.session.rollback()
            new_icon_name = os.path.join(icon_dir, new_icon_name)
            if icon_flag and os.path.exists(new_icon_name) and os.path.isfile(new_icon_name):
                os.remove(new_icon_name)
            add_admin_log(user=current_user.username, actions='添加banner广告', client_ip=request.remote_addr,
                          results='成功')
            flash('添加banner广告失败')

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='添加banner广告', client_ip=request.remote_addr,
                      results=error[0])
    return render_template('manage/add_bannerads.html', form=form)


@login_required
def get_bannerads_info():
    form = BannertInfoForm()
    query = BannerAds.query
    if form.validate_on_submit():
        name = form.name.data
        position = form.position.data
        source = form.source.data
        status = form.status.data
        start_time = form.start_time.data
        end_time = form.end_time.data
    else:
        name = request.args.get('name')
        position = request.args.get('position')
        source = request.args.get('source')
        status = request.args.get('status')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d').date()
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d').date()

    if name is not None:
        form.name.data = name
        if form.name.data != '':
            query = query.filter(BannerAds.name.like('%' + form.name.data + '%'))
    if position is not None:
        form.position.data = int(position)
        if form.position.data != -1:
            query = query.filter_by(position=form.position.data)
    if source is not None:
        form.source.data = int(source)
        if form.source.data != -1:
            query = query.filter_by(source=form.source.data)
    if status is not None:
        form.status.data = int(status)
        if form.status.data != -1:
            query = query.filter_by(status=form.status.data)

    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
    else:
        days = datetime.datetime.now() - datetime.timedelta(days=6)
        end_time = datetime.datetime.now().date()
        start_time = days.date()
        form.start_time.data = start_time
        form.end_time.data = end_time

    data = {}
    for ad in query:
        show_query_all = db.session.query(func.sum(BannerAdsStatistics.count), func.count()).filter_by(
            ad_id=ad.id, operation=0)
        click_query_all = db.session.query(func.sum(BannerAdsStatistics.count), func.count()).filter_by(
            ad_id=ad.id, operation=1)
        if start_time is not None and end_time is not None:
            show_all_info = show_query_all.filter(BannerAdsStatistics.record_time.between(start_time, end_time)).first()
            click_all_info = click_query_all.filter(BannerAdsStatistics.record_time.between(
                start_time, end_time)).first()

        if show_all_info is not None:
            if show_all_info[1] is None:
                show_count = 0
            else:
                show_count = show_all_info[1]
            if show_all_info[0] is None:
                show_all = 0
            else:
                show_all = show_all_info[0]
        else:
            show_count = 0
            show_all = 0
        if click_all_info is not None:
            if click_all_info[1] is None:
                click_count = 0
            else:
                click_count = click_all_info[1]
            if click_all_info[0] is None:
                click_all = 0
            else:
                click_all = click_all_info[0]
        else:
            click_count = 0
            click_all = 0
        data[ad.id] = [show_all, show_count, click_all, click_count]

    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='获取banner广告信息', client_ip=request.remote_addr,
                      results=error[0])
    add_admin_log(user=current_user.username, actions='获取banner广告信息', client_ip=request.remote_addr, results='成功')
    return render_template('manage/bannerads.html', bannerads=pagination.items, pagination=pagination, form=form,
                           data=data)


@login_required
def get_bannerads_details(ad_id):
    photo_url = current_app.config['FILE_SERVER']
    query = BannerAds.query.filter_by(id=ad_id).first()
    add_admin_log(user=current_user.username, actions='获取banner广告详情', client_ip=request.remote_addr, results='成功')
    return render_template('manage/bannerad_details.html', bannerad=query, photo_url=photo_url)


@login_required
def edit_bannerad_status():
    bannerad = BannerAds.query.filter_by(id=request.args.get('id', type=int)).first()
    if bannerad is not None:
        if bannerad.status == 0:
            code = 1
            bannerad.status = 1
            add_admin_log(user=current_user.username, actions='打开广告', client_ip=request.remote_addr, results='成功')
        else:
            code = 0
            bannerad.status = 0
            add_admin_log(user=current_user.username, actions='关闭广告', client_ip=request.remote_addr, results='成功')
        db.session.add(bannerad)
        db.session.commit()
        return jsonify(code=code)
    return jsonify(code=-1)


@login_required
def edit_bannerad(ad_id):
    form = EditBannerAdsForm()
    bannerad = BannerAds.query.filter_by(id=ad_id).first()
    photo_url = current_app.config['FILE_SERVER']
    if form.validate_on_submit() and bannerad is not None:
        icon = request.files['icon']
        icon_flag = False
        new_icon_name = str(round(time.time()))
        old_icon_name = bannerad.icon
        icon_dir = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], 'bannerads')
        if not os.path.exists(icon_dir):
            os.makedirs(icon_dir)

        if icon and form.source.data == 0:
            icon_name = secure_filename(icon.filename)
            size = len(icon.read())
            if size > 102400:
                flash('广告图标大小不能超过100K')
                add_admin_log(user=current_user.username, actions='编辑banner广告', client_ip=request.remote_addr,
                              results='广告图标大小不能超过100K')
                return redirect(url_for('manage.edit_bannerad', ad_id=ad_id))
            if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', icon.filename.rsplit('.', 1)[0])):
                flash('广告图标名称不能为纯汉字')
                add_admin_log(user=current_user.username, actions='编辑banner广告', client_ip=request.remote_addr,
                              results='广告图标名称不能为纯汉字')
                return redirect(url_for('manage.edit_bannerad', ad_id=ad_id))
            if icon_name.rsplit('.', 1)[1] not in ['jpg', 'png', 'JPG', 'PNG']:
                flash('广告图标格式错误')
                add_admin_log(user=current_user.username, actions='编辑banner广告', client_ip=request.remote_addr,
                              results='广告图标格式错误')
                return redirect(url_for('manage.edit_bannerad', ad_id=ad_id))
            im = Image.open(icon)
            new_icon_name = icon_name.rsplit('.', 1)[0] + '_' + new_icon_name + '.' + icon_name.rsplit('.', 1)[1]
            bannerad.icon = os.path.join(current_app.config['PHOTO_TAG'], 'bannerads', new_icon_name)
            im.save(os.path.join(icon_dir, new_icon_name))
            icon_flag = True

        bannerad.name = form.name.data
        # bannerad.position = form.position.data
        # bannerad.source = form.source.data
        # bannerad.charge_mode = form.charge_mode.data
        bannerad.unit_price = int(round(form.unit_price.data, 2) * 100)
        bannerad.start_time = form.start_time.data
        bannerad.end_time = form.end_time.data
        # bannerad.advertiser = form.advertiser.data
        # bannerad.contacts = form.contacts.data
        # bannerad.contact_way = form.contact_way.data
        bannerad.display_number = form.display_number.data
        bannerad.carousel = form.carousel.data
        bannerad.carousel_interval = form.carousel_interval.data
        bannerad.icon_dest_link = form.icon_dest_link.data
        bannerad.refresh_status = form.refresh_status.data
        bannerad.user_count = form.user_count.data
        bannerad.morning_count = form.morning_count.data
        bannerad.afternoon_count = form.afternoon_count.data
        bannerad.night_count = form.night_count.data

        try:
            db.session.add(bannerad)
            db.session.commit()
            old_icon_name = os.path.join(os.getcwd(), old_icon_name)
            if icon_flag and os.path.exists(old_icon_name) and os.path.isfile(old_icon_name):
                os.remove(old_icon_name)
            add_admin_log(user=current_user.username, actions='编辑banner广告', client_ip=request.remote_addr,
                          results='成功')
            return redirect(url_for('manage.get_bannerads_details', ad_id=ad_id))
        except Exception as e:
            print(e)
            db.session.rollback()
            new_icon_name = os.path.join(icon_dir, new_icon_name)
            if icon_flag and os.path.exists(new_icon_name) and os.path.isfile(new_icon_name):
                os.remove(new_icon_name)
            add_admin_log(user=current_user.username, actions='编辑banner广告', client_ip=request.remote_addr,
                          results='失败')
            flash('编辑banner广告失败')

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='编辑banner广告', client_ip=request.remote_addr,
                      results=error[0])
    if bannerad is not None:
        form.name.data = bannerad.name
        form.position.data = bannerad.position
        form.source.data = bannerad.source
        form.charge_mode.data = bannerad.charge_mode
        form.unit_price.data = bannerad.unit_price / 100
        form.start_time.data = bannerad.start_time
        form.end_time.data = bannerad.end_time
        form.advertiser.data = bannerad.advertiser
        form.contacts.data = bannerad.contacts
        form.contact_way.data = bannerad.contact_way
        form.display_number.data = bannerad.display_number
        form.carousel.data = bannerad.carousel
        form.carousel_interval.data = bannerad.carousel_interval
        form.icon_dest_link.data = bannerad.icon_dest_link
        form.refresh_status.data = bannerad.refresh_status
        form.morning_count.data = bannerad.morning_count
        form.afternoon_count.data = bannerad.afternoon_count
        form.night_count.data = bannerad.night_count
        form.user_count.data = bannerad.user_count
    if not form.errors:
        add_admin_log(user=current_user.username, actions='获取banner广告原数据', client_ip=request.remote_addr,
                      results='成功')
    return render_template('manage/edit_bannerads.html', ad_id=ad_id, form=form, photo_url=photo_url,
                           photo=bannerad.icon)


@celery.task(name='make_open_screen_simulate_data')
def make_open_screen_simulate_data():
    # 开屏广告虚拟控制数据生成
    ad_infos = OpenScreenAds.query.filter_by(status=1).all()

    flag = True
    for open_ads in ad_infos:
        yesterday_display_number = 0
        yesterday_total_display_number = 0
        yesterday_control_times = 0
        yesterday_click_number = 0

        # 昨天数据
        today = datetime.datetime.today()
        yesterday = today
        if flag and OpenScreenSimulateData.query.filter_by(
                ad_id=open_ads.id, record_time=today.strftime('%Y-%m-%d')).order_by(desc(OpenScreenSimulateData.id)).limit(1).first() is not None:
            return False
        flag = False
        statistics_info = db.session.query(func.sum(OpenScreenAdsStatistics.count), func.count()).filter_by(
            ad_id=open_ads.id, operation=0).filter(
            OpenScreenAdsStatistics.record_time == yesterday.strftime('%Y-%m-%d')).limit(1).first()
        if statistics_info is not None:
            if statistics_info[0] is not None:
                yesterday_total_display_number = int(statistics_info[0])
            if statistics_info[1] is not None:
                yesterday_display_number = int(statistics_info[1])

        control_times = math.ceil((open_ads.control_click_rate / 100) * yesterday_total_display_number)
        if control_times > yesterday_display_number:
            control_number = yesterday_display_number
        else:
            control_number = control_times

        info = OpenScreenSimulateData()
        info.ad_id = open_ads.id
        info.record_time = datetime.date.today() + datetime.timedelta(days=1)
        info.actual_number = 0
        info.actual_control_times = 0
        info.display_number = yesterday_display_number
        info.total_display_number = yesterday_total_display_number
        info.control_times = control_times
        info.control_number = control_number
        db.session.add(info)

    # banner 广告刷新数据生成
    banner_flag = True
    banner_infos = BannerAds.query.filter_by(status=1).all()
    for banner_info in banner_infos:
        today = datetime.datetime.today()
        if banner_flag and BannerRefreshData.query.filter_by(
                ad_id=banner_info.id, record_time=today.strftime('%Y-%m-%d'), type=0).order_by(desc(BannerRefreshData.id)).limit(1).first() is not None:
            return False
        banner_flag = False

        # 上午刷新数据生成
        morning_info = BannerRefreshData()
        morning_info.ad_id = banner_info.id
        morning_info.record_time = datetime.date.today()
        morning_info.actual_number = 0
        morning_info.type = 0
        if banner_info.user_count < banner_info.morning_count:
            morning_info.control_times = banner_info.morning_count
            morning_info.control_number = banner_info.user_count
        else:
            morning_info.control_times = banner_info.morning_count
            morning_info.control_number = banner_info.morning_count
        db.session.add(morning_info)

        # 下午刷新数据生成
        afternoon_info = BannerRefreshData()
        afternoon_info.ad_id = banner_info.id
        afternoon_info.record_time = datetime.date.today()
        afternoon_info.actual_number = 0
        afternoon_info.type = 1
        if banner_info.user_count < banner_info.afternoon_count:
            afternoon_info.control_times = banner_info.afternoon_count
            afternoon_info.control_number = banner_info.user_count
        else:
            afternoon_info.control_times = banner_info.afternoon_count
            afternoon_info.control_number = banner_info.afternoon_count
        db.session.add(afternoon_info)

        # 晚上刷新数据生成
        night_info = BannerRefreshData()
        night_info.ad_id = banner_info.id
        night_info.record_time = datetime.date.today()
        night_info.actual_number = 0
        night_info.type = 2
        if banner_info.user_count < banner_info.night_count:
            night_info.control_times = banner_info.night_count
            night_info.control_number = banner_info.user_count
        else:
            night_info.control_times = banner_info.night_count
            night_info.control_number = banner_info.night_count
        db.session.add(night_info)

    if len(ad_infos) > 0 or len(banner_infos) > 0:
        db.session.commit()

    return True


@login_required
def get_app_list_info():
    page = request.args.get('page', 1, type=int)
    pagination = AppList.query.order_by(AppList.app_type.desc()).paginate(
        page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    data = pagination.items
    add_admin_log(user=current_user.username, actions='查看应用列表信息', client_ip=request.remote_addr, results='成功')
    return render_template("manage/app_list.html", data=data, pagination=pagination)


@login_required
def add_ware():
    form = AddMemberWareForm()
    info = MemberWare()
    if form.validate_on_submit():
        channel = form.channel.data
        category = form.category.data
        number = form.number.data
        name = form.name.data
        price = int(round(form.price.data, 2) * 100)
        common_discount = round(form.common_discount.data, 2)
        gold_discount = round(form.gold_discount.data, 2)
        discount = round(form.discount.data, 2)
        description = form.description.data
        status = form.status.data
        picture = request.files['picture']
        # ads_cate = form.ads_cate.data

        if (common_discount > 1.0 or common_discount < 0) and (gold_discount > 1.0 or gold_discount < 0) and \
                (discount > 1.0 or discount < 0):
            flash('折扣区间: 0.00 -- 1.00')
            add_admin_log(user=current_user.username, actions='添加产品', client_ip=request.remote_addr,
                          results='折扣输入错误')
            return render_template("manage/add_ware.html", form=form)

        if MemberWare.query.filter_by(id=number).first() is not None:
            flash('产品编号已经存在')
            add_admin_log(user=current_user.username, actions='添加产品', client_ip=request.remote_addr,
                          results='产品编号存在')
            return render_template("manage/add_ware.html", form=form)

        if MemberWare.query.filter_by(name=name).first() is not None:
            flash('产品名称已存在')
            add_admin_log(user=current_user.username, actions='添加产品', client_ip=request.remote_addr,
                          results='产品名称存在')
            return render_template("manage/add_ware.html", form=form)
        if price * common_discount < 1 or price * gold_discount < 1 or price * discount < 1:
            flash('会员购买价格不能小于1分')
            add_admin_log(user=current_user.username, actions='会员购买价格不能小于1分', client_ip=request.remote_addr,
                          results='会员购买价格不能小于1分')
            return render_template("manage/add_ware.html", form=form)
        vip_type = VipType.query.filter_by(name=category).first()
        if vip_type is not None:
            type_number = vip_type.number
        else:
            type_number = 0
        if channel is None:
            channel = 'moren'
        if MemberWare.query.filter_by(channel=channel, category=type_number, status=1, gold_or_platinum=1).first() is not None:
            flash('该渠道的这个类型的产品已存在')
            add_admin_log(user=current_user.username, actions='添加产品', client_ip=request.remote_addr,
                          results='该渠道的这个类型的产品已存在')
            return render_template("manage/add_ware.html", form=form)
        if picture:
            file_name = secure_filename(picture.filename)
            if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', picture.filename.rsplit('.', 1)[0])):
                flash('图片名称不能为纯汉字')
                add_admin_log(user=current_user.username, actions='添加产品', client_ip=request.remote_addr,
                              results='图片名称不能为纯汉字')
                return redirect(url_for('manage.add_ware'))
            if file_name.rsplit('.', 1)[1] not in ['png', 'jpg']:
                flash('图片格式错误')
                add_admin_log(user=current_user.username, actions='添加产品', client_ip=request.remote_addr,
                              results='图片格式错误')
                return redirect(url_for('manage.add_ware'))
            size = len(picture.read())
            if size > 5120:
                flash("图片大小不能超过5KB")
                add_admin_log(user=current_user.username, actions='添加产品',
                              client_ip=request.remote_addr, results='头像图片大小不能超过5KB')
                return redirect(url_for('manage.add_ware'))

            app_dir = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], "vip_ware")
            file_url = os.path.join(current_app.config['PHOTO_TAG'], "vip_ware")
            if not os.path.exists(app_dir):
                os.mkdir(app_dir)
            im = Image.open(picture)
            info.picture = os.path.join(file_url, file_name)
            im.save(os.path.join(app_dir, file_name))
        else:
            info.picture = ''
        if channel is None:
            info.channel = 'moren'
        else:
            info.channel = channel
        vip_type = VipType.query.filter_by(name=category).first()
        if vip_type is not None:
            info.category = vip_type.number
        info.id = number
        info.name = name
        info.price = price
        info.common_discount = common_discount
        info.gold_discount = gold_discount
        info.discount = discount
        info.description = description
        info.status = status
        info.priority = 0
        info.gold_or_platinum = 1
        # info.ads_category = ','.join(ads_cate)
        db.session.add(info)
        db.session.commit()
        add_admin_log(user=current_user.username, actions='添加产品', client_ip=request.remote_addr, results='成功')
        return redirect(url_for('manage.get_ware_info'))

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='添加产品', client_ip=request.remote_addr, results=error[0])

    return render_template("manage/add_ware.html", form=form)


@login_required
def edit_ware(ware_id):
    form = EditMemberWareForm()
    info = MemberWare.query.filter_by(id=ware_id).first()
    if form.validate_on_submit() and info is not None:
        name = form.name.data
        price = int(round(form.price.data, 2) * 100)
        common_discount = round(form.common_discount.data, 2)
        gold_discount = round(form.gold_discount.data, 2)
        discount = round(form.discount.data, 2)
        description = form.description.data
        status = form.status.data
        picture = request.files['picture']
        # ads_cate = form.ads_cate.data

        if (common_discount > 1.0 or common_discount < 0) and (gold_discount > 1.0 or gold_discount < 0) and \
                (discount > 1.0 or discount < 0):
            flash('折扣区间: 0.00 -- 1.00')
            add_admin_log(user=current_user.username, actions='编辑产品', client_ip=request.remote_addr,
                          results='折扣输入错误')
            return render_template("manage/edit_ware.html", form=form, ware_id=ware_id)

        if MemberWare.query.filter(MemberWare.name == name, MemberWare.id != ware_id).first() is not None:
            flash('产品名称已存在')
            add_admin_log(user=current_user.username, actions='编辑产品', client_ip=request.remote_addr,
                          results='产品名称存在')
            return render_template("manage/edit_ware.html", form=form, ware_id=ware_id)
        if price * common_discount < 1 or price * gold_discount < 1 or price * discount < 1:
            flash('会员购买价格不能小于1分')
            add_admin_log(user=current_user.username, actions='会员购买价格不能小于1分', client_ip=request.remote_addr,
                          results='会员购买价格不能小于1分')
            return render_template("manage/edit_ware.html", form=form)
        if picture:
            file_name = secure_filename(picture.filename)
            if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', picture.filename.rsplit('.', 1)[0])):
                flash('图片名称不能为纯汉字')
                add_admin_log(user=current_user.username, actions='编辑产品', client_ip=request.remote_addr,
                              results='图片名称不能为纯汉字')
                return render_template("manage/edit_ware.html", form=form, ware_id=ware_id)
            if file_name.rsplit('.', 1)[1] not in ['png', 'jpg']:
                flash('图片格式错误')
                add_admin_log(user=current_user.username, actions='编辑产品', client_ip=request.remote_addr,
                              results='图片格式错误')
                return render_template("manage/edit_ware.html", form=form, ware_id=ware_id)
            size = len(picture.read())
            if size > 5120:
                flash("图片大小不能超过5KB")
                add_admin_log(user=current_user.username, actions='编辑产品',
                              client_ip=request.remote_addr, results='头像图片大小不能超过5KB')
                return render_template("manage/edit_ware.html", form=form, ware_id=ware_id)
            app_dir = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], "vip_ware")
            file_url = os.path.join(current_app.config['PHOTO_TAG'], "vip_ware")
            if not os.path.exists(app_dir):
                os.mkdir(app_dir)
            im = Image.open(picture)
            info.picture = os.path.join(file_url, file_name)
            im.save(os.path.join(app_dir, file_name))

        info.name = name
        info.price = price
        info.common_discount = common_discount
        info.gold_discount = gold_discount
        info.discount = discount
        info.description = description
        info.status = status
        # info.ads_category = ','.join(ads_cate)

        db.session.add(info)
        db.session.commit()
        return redirect(url_for('manage.get_ware_info'))
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='编辑产品', client_ip=request.remote_addr, results=error[0])
    if info is not None:
        form.name.data = info.name
        form.price.data = info.price / 100
        form.description.data = info.description
        form.common_discount.data = info.common_discount
        form.gold_discount.data = info.gold_discount
        form.discount.data = info.discount
        form.status.data = info.status
        form.picture.data = info.picture
    vip_type = VipType.query.filter_by(number=info.category).first()
    if vip_type is not None:
        type_name = vip_type.name
    else:
        type_name = ''

    if not form.errors:
        add_admin_log(user=current_user.username, actions='编辑产品', client_ip=request.remote_addr, results='成功')

    return render_template("manage/edit_ware.html", form=form, ware_id=ware_id, channel=info.channel,
                           category=type_name, picture=info.picture,
                           file_url=current_app.config['FILE_SERVER'])


@login_required
def get_vip_category():
    form = VipCategoryForm()
    query = VipType.query
    if form.validate_on_submit():
        name = form.name.data
    else:
        name = request.args.get('name')
    if name is not None:
        form.name.data = name
        if form.name.data != '':
            query = query.filter(VipType.name.like('%' + form.name.data + '%'))
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='vip类型', client_ip=request.remote_addr,
                      results=error[0])
    if not form.errors:
        add_admin_log(user=current_user.username, actions='vip类型', client_ip=request.remote_addr,
                      results='成功')
    return render_template("manage/vip_category.html", form=form, data=pagination.items, pagination=pagination,
                           page=page, per_page=current_app.config['RECORDS_PER_PAGE'])


@login_required
def add_vip_category():
    form = AddVipCategoryForm()
    if form.validate_on_submit():
        name = form.name.data
        days = form.days.data
        id_list = [r[0] for r in db.session.query(VipType.id.distinct())]
        if VipType.query.filter_by(name=name).first() is not None:
            flash('该类型已存在')
            add_admin_log(user=current_user.username, actions='添加vip类型', client_ip=request.remote_addr,
                          results='成功')
            return redirect(url_for('manage.add_vip_category'))
        if VipType.query.filter_by(days=days).first() is not None:
            flash('该天数已存在')
            add_admin_log(user=current_user.username, actions='添加vip类型', client_ip=request.remote_addr,
                          results='成功')
            return redirect(url_for('manage.add_vip_category'))
        vip_type = VipType()
        vip_type.name = name
        vip_type.days = days
        db.session.add(vip_type)
        if len(id_list) == 0:
            vip_type.number = 0
        else:
            v_type = VipType.query.filter_by(id=id_list[-1]).first()
            vip_type.number = v_type.number + 1
        db.session.commit()
        add_admin_log(user=current_user.username, actions='添加vip类型', client_ip=request.remote_addr, results='成功')
        return redirect(url_for('manage.get_vip_category'))
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='添加vip类型', client_ip=request.remote_addr,
                      results=error[0])
    return render_template("manage/add_vip_category.html", form=form)


@login_required
def add_vip_channel():
    form = AddVipChannelForm()
    if form.validate_on_submit():
        channel = form.channel.data
        channel_name = form.channel_name.data

        if Channel.query.filter_by(channel=channel).first() is not None:
            flash('该渠道已存在')
            add_admin_log(user=current_user.username, actions='添加vip渠道', client_ip=request.remote_addr,
                          results='添加vip渠道')
            return redirect(url_for('manage.add_vip_channel'))
        channel_query = Channel()
        channel_query.channel = channel
        channel_query.channel_name = channel_name
        db.session.add(channel_query)
        db.session.commit()
        add_admin_log(user=current_user.username, actions='添加vip渠道', client_ip=request.remote_addr, results='成功')
        return redirect(url_for('manage.get_vip_channel'))
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='添加vip渠道', client_ip=request.remote_addr,
                      results=error[0])
    return render_template("manage/add_vip_channel.html", form=form)


@login_required
def get_vip_channel():
    form = VipChannelForm()
    query = Channel.query
    if form.validate_on_submit():
        channel_name = form.channel_name.data
    else:
        channel_name = request.args.get('channel_name')
    if channel_name is not None:
        form.channel_name.data = channel_name
        if form.channel_name.data != '':
            query = query.filter(Channel.channel_name.like('%' + form.channel_name.data + '%'))
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='vip类型', client_ip=request.remote_addr,
                      results=error[0])
    if not form.errors:
        add_admin_log(user=current_user.username, actions='vip类型', client_ip=request.remote_addr,
                      results='成功')
    return render_template("manage/vip_channel.html", form=form, data=pagination.items, pagination=pagination,
                           page=page, per_page=current_app.config['RECORDS_PER_PAGE'])


@login_required
def get_ware_info():
    form = QueryMemberWareForm()
    query = MemberWare.query.order_by(MemberWare.id.desc()).filter_by(gold_or_platinum=1)
    if form.validate_on_submit():
        channel = form.channel.data
        category = form.category.data
        status = form.status.data
    else:
        channel = request.args.get('channel')
        category = request.args.get('category')
        status = request.args.get('status', type=int)

    if channel is not None:
        form.channel.data = channel
        if form.channel.data != '':
            query = query.filter(MemberWare.channel.like('%' + form.channel.data + '%'))
    if category is not None:
        form.category.data = category
        if form.category.data != '':
            vip_type = VipType.query.filter_by(name=form.category.data).first()
            if vip_type is not None:
                type_number = vip_type.number
            else:
                type_number = 0
            query = query.filter_by(category=type_number)
    if status is not None:
        form.status.data = status
        if form.status.data != -1:
            query = query.filter_by(status=form.status.data)

    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    cell = {}
    for ware in pagination.items:
        vip_type = VipType.query.filter_by(number=ware.category).first()
        if vip_type is not None:
            cell[ware.id] = vip_type.name
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='查看产品', client_ip=request.remote_addr,
                      results=error[0])
    if not form.errors:
        add_admin_log(user=current_user.username, actions='查看产品', client_ip=request.remote_addr,
                      results='成功')
    return render_template("manage/get_ware_info.html", form=form, data=pagination.items, pagination=pagination,
                           page=page, per_page=current_app.config['RECORDS_PER_PAGE'], data_cate=cell)


@login_required
def set_ware_status():
    ware_id = request.args.get('id', type=str)
    status = request.args.get('status', type=int)

    if status != 0 and status != 1:
        add_admin_log(user=current_user.username, actions='设置产品状态', client_ip=request.remote_addr,
                      results='参数错误')
        return jsonify({'code': 1})
    else:
        try:
            MemberWare.query.filter_by(id=ware_id).update(dict(status=status))
            db.session.commit()

            add_admin_log(user=current_user.username, actions='设置产品状态', client_ip=request.remote_addr,
                          results='成功')
            return jsonify({'code': 0})
        except Exception as e:
            print(e)
            db.session.rollback()
            add_admin_log(user=current_user.username, actions='设置产品状态', client_ip=request.remote_addr,
                          results='失败')
            return jsonify({'code': 1})


@login_required
def set_priority():
    ware_id = request.args.get('id', type=str)
    priority = request.args.get('priority', type=int)
    print(ware_id)
    if priority != 0 and priority != 1:
        add_admin_log(user=current_user.username, actions='设置产品推荐', client_ip=request.remote_addr,
                      results='参数错误')
        return jsonify({'code': 1})
    else:
        try:
            MemberWare.query.filter_by(id=ware_id).update(dict(priority=priority))
            db.session.commit()

            add_admin_log(user=current_user.username, actions='设置产品推荐', client_ip=request.remote_addr,
                          results='成功')
            return jsonify({'code': 0})
        except Exception as e:
            print(e)
            db.session.rollback()
            add_admin_log(user=current_user.username, actions='设置产品推荐', client_ip=request.remote_addr,
                          results='失败')
            return jsonify({'code': 1})


@login_required
def get_vip_ware_details(ware_id):
    photo_url = current_app.config['FILE_SERVER']
    query = MemberWare.query.filter_by(id=ware_id).first()
    vip = VipType.query.filter_by(number=query.category).first()
    category = vip.name
    pay_price = (query.price * query.common_discount) / 100
    gold_pay_price = (query.price * query.gold_discount) / 100
    platinum_pay_price = (query.price * query.discount) / 100
    price = [pay_price, gold_pay_price, platinum_pay_price]
    add_admin_log(user=current_user.username, actions='获取vip产品详情', client_ip=request.remote_addr, results='成功')
    return render_template('manage/vip_ware_details.html', ware=query, photo_url=photo_url, ware_id=ware_id,
                           price=price, category=category)


@login_required
def get_ware_statistics():
    form = WareStatisticsForm()
    query = MemberWare.query.order_by(MemberWare.id.desc())
    if form.validate_on_submit():
        channel = form.channel.data
        category = form.category.data
        name = form.name.data
        number = form.number.data
        start_time = form.start_time.data
        end_time = form.end_time.data
    else:
        channel = request.args.get('channel')
        category = request.args.get('category')
        name = request.args.get('name')
        number = request.args.get('number')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

    if channel is not None:
        form.channel.data = channel
        if form.channel.data != '':
            query = query.filter(MemberWare.channel.like('%' + form.channel.data + '%'))
    else:
        query = query.filter(MemberWare.channel.like('%' + 'moren' + '%'))

    if category is not None:
        form.category.data = category
        if form.category.data != '':
            vip_type = VipType.query.filter_by(name=form.category.data).first()
            if vip_type is not None:
                type_number = vip_type.number
            else:
                type_number = 0
            query = query.filter_by(category=type_number)
    if name is not None:
        form.name.data = name
        if form.name.data != '':
            query = query.filter(MemberWare.name.like('%' + form.name.data + '%'))

    if number is not None:
        form.number.data = number
        if form.number.data != '':
            query = query.filter(MemberWare.id == form.number.data)

    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    data = []
    ware_order = db.session.query(func.sum(MemberWareOrder.discount_price), func.count()).filter(
        MemberWareOrder.status == 1, MemberWareOrder.category != 2)
    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
        if form.end_time.data != '' and form.start_time.data != '':
            ware_order_info = ware_order.filter(MemberWareOrder.create_time.between(form.start_time.data,
                                                                                    form.end_time.data)).first()
    else:
        ware_order_info = ware_order.first()
    total_sales = 0.0
    total_sales_count = 0
    if ware_order_info is not None:
        if ware_order_info[0] is not None:
            total_sales = round(ware_order_info[0] / 100, 2)
        if ware_order_info[1] is not None:
            total_sales_count = ware_order_info[1]

    for ware in pagination.items:
        ware_total_sales = 0.0
        ware_total_sales_count = 0
        total_sales_ratio = 0.0
        total_sales_count_ratio = 0.0

        if start_time is not None and end_time is not None:
            form.start_time.data = start_time
            form.end_time.data = end_time
            if form.end_time.data != '' and form.start_time.data != '':
                ware_info = ware_order.filter(MemberWareOrder.ware_id == ware.id,
                                              MemberWareOrder.create_time.between(form.start_time.data,
                                                                                  form.end_time.data)).first()
        else:
            ware_info = ware_order.filter(MemberWareOrder.ware_id == ware.id).first()
        if ware_info is not None:
            if ware_info[0] is not None:
                ware_total_sales = round(ware_info[0] / 100, 2)
            if ware_info[1] is not None:
                ware_total_sales_count = ware_info[1]
        if total_sales != 0.0:
            total_sales_ratio = round((float(ware_total_sales) / float(total_sales)) * 100, 2)
        if total_sales_count != 0:
            total_sales_count_ratio = round((ware_total_sales_count / total_sales_count) * 100, 2)
        vip_type = VipType.query.filter_by(number=ware.category).first()
        if vip_type is not None:
            type_name = vip_type.name
        else:
            type_name = ''
        cell = dict(id=ware.id, category=type_name, ware_total_sales_count=ware_total_sales_count, name=ware.name,
                    ware_total_sales=ware_total_sales, total_sales_ratio=total_sales_ratio, channel=ware.channel,
                    total_sales_count_ratio=total_sales_count_ratio, gold_or_platinum=ware.gold_or_platinum)
        data.append(cell)

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='产品统计', client_ip=request.remote_addr,
                      results=error[0])
    if not form.errors:
        add_admin_log(user=current_user.username, actions='产品统计', client_ip=request.remote_addr,
                      results='成功')
    return render_template("manage/ware_statistics.html", form=form, data=data, pagination=pagination,
                           page=page, per_page=current_app.config['RECORDS_PER_PAGE'])


def get_vip_members():
    form = VipMembersForm()
    query = VipMembers.query.join(GodinAccount, GodinAccount.godin_id == VipMembers.godin_id).add_entity(GodinAccount). \
        order_by(VipMembers.first_pay_time.desc())
    if form.validate_on_submit():
        phone_num = form.phone_num.data
        category = form.category.data
        cur_pay_cate = form.cur_pay_cate.data
        status = form.status.data
        channel = form.channel.data
        start_time = form.start_time.data
        end_time = form.end_time.data
    else:
        phone_num = request.args.get('phone_num')
        category = request.args.get('category', type=int)
        cur_pay_cate = request.args.get('cur_pay_cate')
        status = request.args.get('status', type=int)
        channel = request.args.get('channel')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    if phone_num is not None:
        form.phone_num.data = phone_num
        if form.phone_num.data != '':
            query = query.filter(GodinAccount.phone_num.like('%' + form.phone_num.data + '%'))
    if category is not None:
        form.category.data = category
        if form.category.data != -1:
            query = query.filter(VipMembers.category == form.category.data)
    if cur_pay_cate is not None:
        form.cur_pay_cate.data = cur_pay_cate
        if form.cur_pay_cate.data != -1:
            vip_type = VipType.query.filter_by(name=form.cur_pay_cate.data).first()
            if vip_type is not None:
                query = query.filter(VipMembers.cur_pay_cate == vip_type.number)
    if status is not None:
        form.status.data = status
        if form.status.data != -1:
            query = query.filter(VipMembers.status == form.status.data)
    if channel is not None:
        form.channel.data = channel
        if form.channel.data != '':
            query = query.filter(VipMembers.channel.like('%' + form.channel.data + '%'))
    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
        query = query.filter(VipMembers.first_pay_time.between(form.start_time.data, form.end_time.data))
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    zero_time = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d') + " 00:00:00",
                                           '%Y-%m-%d %H:%M:%S')
    new_count = VipMembers.query.filter(VipMembers.first_pay_time.between(zero_time, datetime.datetime.now())).count()
    all_orders = db.session.query(func.sum(MemberWareOrder.discount_price)). \
        filter(MemberWareOrder.status == 1, MemberWareOrder.category != 2).first()[0]
    if all_orders is None:
        all_orders = 0
    cell = {}
    valid_cell = {}
    for member in pagination.items:
        vip_type = VipType.query.filter_by(number=member.VipMembers.cur_pay_cate).first()
        if vip_type is not None:
            cell[member.VipMembers.godin_id] = vip_type.name
        # 设置到期时间为黄金会员和铂金会员的最大过期时间
        if member.VipMembers.valid_time and not member.VipMembers.gold_valid_time:
            valid_cell[member.VipMembers.godin_id] = member.VipMembers.valid_time
        elif not member.VipMembers.valid_time and member.VipMembers.gold_valid_time:
            valid_cell[member.VipMembers.godin_id] = member.VipMembers.gold_valid_time
        else:
            if member.VipMembers.valid_time > member.VipMembers.gold_valid_time:
                valid_cell[member.VipMembers.godin_id] = member.VipMembers.valid_time
            else:
                valid_cell[member.VipMembers.godin_id] = member.VipMembers.gold_valid_time

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='充值用户管理', client_ip=request.remote_addr,
                      results=error[0])
    if not form.errors:
        add_admin_log(user=current_user.username, actions='充值用户管理', client_ip=request.remote_addr,
                      results='成功')

    return render_template("manage/vip_members.html", form=form, data=pagination.items, page=page, per_page=per_page,
                           pagination=pagination, new_count=new_count, all_orders=all_orders, cur_pay_cate=cell, valid_cell=valid_cell)


@login_required
def get_vip_members_details(godin_id):
    form = VipMembersDetailsForm()
    query = MemberWareOrder.query.join(MemberWare, MemberWare.id == MemberWareOrder.ware_id).add_entity(MemberWare). \
        filter(MemberWareOrder.buyer_godin_id == godin_id, MemberWareOrder.status == 1). \
        order_by(MemberWareOrder.pay_time.desc())
    if form.validate_on_submit():
        pay_type = form.pay_type.data
        category = form.category.data
        status = form.status.data
        order_number = form.order_number.data
        add_type = form.add_type.data
        start_time = form.start_time.data
        end_time = form.end_time.data
    else:
        pay_type = request.args.get('pay_type', type=int)
        category = request.args.get('category', type=int)
        status = request.args.get('status', type=int)
        order_number = request.args.get('order_number')
        add_type = request.args.get('add_type', type=int)
        start_time = request.args.get('start_time')
        end_time = request.args.get('start_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    if pay_type is not None:
        form.pay_type.data = pay_type
        if form.pay_type.data != -1:
            query = query.filter(MemberWareOrder.pay_type == form.pay_type.data)
    if category is not None:
        form.category.data = category
        if form.category.data != '':
            vip_type = VipType.query.filter_by(name=form.category.data).first()
            if vip_type is not None:
                query = query.filter(MemberWare.category == vip_type.number)
    if status is not None:
        form.status.data = status
        if form.status.data == 0:
            query = query.filter(MemberWareOrder.end_time < datetime.datetime.now())
        elif form.status.data == 1:
            query = query.filter(datetime.datetime.now() > MemberWareOrder.start_time,
                                 datetime.datetime.now() < MemberWareOrder.end_time)
        elif form.status.data == 2:
            query = query.filter(MemberWareOrder.start_time > datetime.datetime.now())
    if order_number is not None:
        form.order_number.data = order_number
        if form.order_number.data != '':
            query = query.filter(MemberWareOrder.order_number.like('%' + form.order_number.data + '%'))

    if add_type is not None:
        form.add_type.data = add_type
        if form.add_type.data != -1:
            query = query.filter(MemberWareOrder.category == form.add_type.data)

    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
        query = query.filter(MemberWareOrder.create_time.between(form.start_time.data, form.end_time.data))

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    buyer = GodinAccount.query.filter_by(godin_id=godin_id).first()
    buy_count = MemberWareOrder.query.filter_by(buyer_godin_id=godin_id, status=1).count()
    buy_price = db.session.query(func.sum(MemberWareOrder.discount_price)). \
        filter_by(buyer_godin_id=godin_id, status=1).first()[0]
    if buy_price is None:
        buy_price = 0
    cell = {}
    for query in pagination.items:
        vip_type = VipType.query.filter_by(number=query.MemberWare.category).first()
        if vip_type is not None:
            cell[query.MemberWare.id] = vip_type.name
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='充值用户个人详情管理', client_ip=request.remote_addr,
                      results=error[0])
    if not form.errors:
        add_admin_log(user=current_user.username, actions='充值用户个人详情管理', client_ip=request.remote_addr,
                      results='成功')
    return render_template("manage/vip_members_details.html", form=form, data=pagination.items, page=page,
                           per_page=per_page, pagination=pagination, godin_id=godin_id, buyer=buyer,
                           buy_count=buy_count, buy_price=buy_price, phone_num=buyer.phone_num,
                           create_time=buyer.create_time, now=datetime.datetime.now(), cate_name=cell)


@login_required
def vip_pay_statistics():
    form = VipPayStatisticsForm()
    query = VipPayMonthStatistics.query
    today_now = datetime.date.today()

    if form.validate_on_submit():
        statistics_way = form.statistics_way.data
        year_start_m = form.start_year_m.data
        year_end_m = form.end_year_m.data
        month_start = form.month_start.data
        month_end = form.month_end.data
        year_start_w = form.start_year_w.data
        year_end_w = form.end_year_w.data
        week_start = form.week_start.data
        week_end = form.week_end.data
        day_start = form.day_start.data
        day_end = form.day_end.data
    else:
        statistics_way = request.args.get('statistics_way', 1, type=int)
        year_start_m = request.args.get('year_start_m', type=int)
        year_end_m = request.args.get('year_end_m', type=int)
        month_start = request.args.get('month_start', type=int)
        month_end = request.args.get('month_end', type=int)
        year_start_w = request.args.get('year_start_w', type=int)
        year_end_w = request.args.get('year_end_w', type=int)
        week_start = request.args.get('week_start', type=int)
        week_end = request.args.get('week_end', type=int)
        day_start = request.args.get('day_start')
        day_end = request.args.get('day_end')
        if day_start is not None and day_end is not None:
            if day_start != '0' and day_end != '0':
                day_start = datetime.datetime.strptime(day_start, '%Y-%m-%d').date()
                day_end = datetime.datetime.strptime(day_end, '%Y-%m-%d').date()

    if statistics_way == 1:
        if year_start_m is not None and year_end_m is not None:
            form.statistics_way.data = statistics_way
            form.start_year_m.data = year_start_m
            form.end_year_m.data = year_end_m
            form.month_start.data = month_start
            form.month_end.data = month_end
            if form.start_year_m.data == form.end_year_m.data:
                query = VipPayMonthStatistics.query.filter_by(year=form.start_year_m.data). \
                    filter(VipPayMonthStatistics.month.between(form.month_start.data, form.month_end.data)). \
                    order_by(VipPayMonthStatistics.month.desc())
            else:
                query = query.filter(or_(and_(VipPayMonthStatistics.month.between(form.month_start.data, 12),
                                              VipPayMonthStatistics.year == form.start_year_m.data),
                                         and_(VipPayMonthStatistics.year < form.end_year_m.data,
                                              VipPayMonthStatistics.year > form.start_year_m.data),
                                         and_(VipPayMonthStatistics.year == form.end_year_m.data,
                                              VipPayMonthStatistics.month.between(1, form.month_end.data)))). \
                    order_by(VipPayMonthStatistics.year.desc(), VipPayMonthStatistics.month.desc())
        else:
            year_now = today_now.year
            month_now = today_now.month
            query = VipPayMonthStatistics.query
            year_last = int(year_now) - 1
            month_last = 12 + (month_now - 12)
            query = query.filter(or_(and_(VipPayMonthStatistics.month.between(month_last, 12),
                                          VipPayMonthStatistics.year == year_last),
                                     and_(VipPayMonthStatistics.year == year_now,
                                          VipPayMonthStatistics.month.between(1, month_now - 1)))). \
                order_by(VipPayMonthStatistics.year.desc(), VipPayMonthStatistics.month.desc())
    elif statistics_way == 2:
        form.statistics_way.data = statistics_way
        form.start_year_w.data = year_start_w
        form.end_year_w.data = year_end_w
        form.week_start.data = week_start
        form.week_end.data = week_end
        if form.end_year_w.data == form.start_year_w.data:
            query = VipPayWeekStatistics.query.filter_by(year=form.start_year_w.data). \
                filter(VipPayWeekStatistics.week.between(form.week_start.data, form.week_end.data + 1)). \
                order_by(VipPayWeekStatistics.week.desc())
        else:
            query = VipPayWeekStatistics.query.filter(or_(and_(VipPayWeekStatistics.year == form.start_year_w.data,
                                                               VipPayWeekStatistics.week.between(form.week_start.data,
                                                                                                 52)),
                                                          and_(VipPayWeekStatistics.year < form.end_year_w.data,
                                                               VipPayWeekStatistics.year > form.start_year_w.data),
                                                          and_(VipPayWeekStatistics.year == form.end_year_w.data,
                                                               VipPayWeekStatistics.week.between(1,
                                                                                                 form.week_end.data)))). \
                order_by(VipPayWeekStatistics.year.desc(), VipPayWeekStatistics.week.desc())

    elif statistics_way == 3:
        form.statistics_way.data = statistics_way
        form.day_start.data = day_start
        form.day_end.data = day_end
        if form.day_start.data is not None and form.day_end.data is not None:
            query = VipPayDayStatistics.query.filter(VipPayDayStatistics.date.between(
                form.day_start.data, form.day_end.data)).order_by(VipPayDayStatistics.date.desc())
        else:
            last_time = today_now - datetime.timedelta(days=30)
            query = VipPayDayStatistics.query.filter(VipPayDayStatistics.date.between(last_time, today_now)). \
                order_by(VipPayDayStatistics.date.desc())
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='vip续费统计', client_ip=request.remote_addr,
                      results='失败')
    add_admin_log(user=current_user.username, actions='vip续费统计', client_ip=request.remote_addr, results='成功')
    if statistics_way is None:
        statistics_way = 1
    return render_template("manage/vip_pay_statistics.html", form=form, data=pagination.items,
                           page=page, per_page=per_page, pagination=pagination, statistics_way=statistics_way)


@login_required
def get_member_info():
    form = MemberForm()
    query = UserInfo.query.filter_by(id=-1)
    if form.validate_on_submit():
        phone_num = form.phone_num.data
        channel = form.channel.data
    else:
        phone_num = request.args.get('phone_num')
        channel = request.args.get('channel')
    if phone_num is not None or channel is not None:
        query = UserInfo.query.join(GodinAccount, GodinAccount.godin_id == UserInfo.godin_id). \
            join(DeviceInfo, UserInfo.imei == DeviceInfo.imei).filter(DeviceInfo.status == 1)

    if phone_num is not None:
        form.phone_num.data = phone_num
        if form.phone_num.data != '':
            query = query.filter(GodinAccount.phone_num.like('%' + form.phone_num.data + '%'))
    if channel is not None:
        form.channel.data = channel
        if form.channel.data != '':
            query = query.filter(DeviceInfo.market == form.channel.data)

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='用户信息', client_ip=request.remote_addr,
                      results='失败')
    add_admin_log(user=current_user.username, actions='用户信息', client_ip=request.remote_addr, results='成功')
    return render_template("manage/members_info.html", form=form, data=pagination.items,
                           page=page, per_page=per_page, pagination=pagination, channel=channel)


@login_required
def add_phone_member():
    form = AddMembersForm()
    if form.validate_on_submit():
        vip_id = form.vip_id.data
        upload_file = request.files['upload_file']
        info = xlrd.open_workbook(filename=None, file_contents=upload_file.read())
        worksheet1 = info.sheet_by_name(u'Sheet1')
        num_rows = worksheet1.nrows
        ware = MemberWare.query.filter_by(id=vip_id).limit(1).first()
        if ware is None:
            flash('vip产品不存在')
            return redirect(url_for('manage.add_phone_member'))
        else:
            ware_id = ware.id
        i = 0
        for curr_row in range(num_rows):
            row = worksheet1.row_values(curr_row)
            if len(row) == 1:
                act_member = ActivateMembers()
                phone_num = row[0]
                godin = GodinAccount.query.filter_by(phone_num=phone_num).first()
                if godin is not None:
                    godin_id = godin.godin_id
                    act_member.godin_id = godin_id
                    act_member.vip_type = 0
                    act_member.status = 0
                    act_member.ware_id = ware_id
                    act_member.channel = 'moren'
                    db.session.add(act_member)
                    i += 1
            else:
                flash('手机号不能为空')
                return redirect(url_for('manage.add_phone_member'))
        try:
            db.session.commit()
            add_admin_log(user=current_user.username, actions='批量赠送会员', client_ip=request.remote_addr,
                          results='成功')
            flash('添加成功 %s 人' % i)
            return redirect(url_for('manage.add_phone_member'))
        except Exception as e:
            print(e)
            db.session.rollback()
            add_admin_log(user=current_user.username, actions='批量赠送会员', client_ip=request.remote_addr,
                          results='失败')
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='批量赠送会员', client_ip=request.remote_addr,
                      results=error[0])
    return render_template('manage/add_phone_vip.html', form=form)


@login_required
def get_act_members():
    form = ActMemebrForm()
    query = ActivateMembers.query.join(GodinAccount, GodinAccount.godin_id == ActivateMembers.godin_id). \
        add_entity(GodinAccount)
    if form.validate_on_submit():
        phone_num = form.phone_num.data
        vip_type = form.vip_type.data
        channel = form.channel.data
        status = form.status.data
        start_time = form.start_time.data
        end_time = form.end_time.data
    else:
        phone_num = request.args.get('phone_num')
        vip_type = request.args.get('vip_type', type=int)
        channel = request.args.get('channel')
        status = request.args.get('status', type=int)
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    if phone_num is not None:
        form.phone_num.data = phone_num
        if form.phone_num.data != '':
            query = query.filter(GodinAccount.phone_num.like('%' + form.phone_num.data + '%'))
    if vip_type is not None:
        form.vip_type.data = vip_type
        if form.vip_type.data != -1:
            query = query.filter(ActivateMembers.vip_type == form.vip_type.data)
    if channel is not None:
        form.channel.data = channel
        if form.channel.data != '全部':
            query = query.filter(ActivateMembers.channel == form.channel.data)
    if status is not None:
        form.status.data = status
        if form.status.data != -1:
            query = query.filter(ActivateMembers.status == form.status.data)
    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
        if form.start_time.data != '' and form.end_time.data != '':
            query = query.filter(ActivateMembers.create_time.between(form.start_time.data, form.end_time.data))

    flag = False
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='查看手动添加vip用户', client_ip=request.remote_addr,
                      results=error[0])
    add_admin_log(user=current_user.username, actions='查看手动添加vip用户', client_ip=request.remote_addr, results='成功')
    return render_template("manage/act_member.html", form=form, data=pagination.items, pagination=pagination,
                           page=page, per_page=current_app.config['RECORDS_PER_PAGE'])


@login_required
def vip_wares_info():
    godin_id = request.args.get('godin_id')
    channel = request.args.get('channel')
    gold_or_platinum = request.args.get('gold_or_platinum')
    wares = MemberWare.query.filter(MemberWare.channel.in_(['moren', channel]),
                                    MemberWare.gold_or_platinum == gold_or_platinum)

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    pagination = wares.paginate(page=page, per_page=per_page, error_out=False)
    phone_num = None
    if godin_id != '':
        user = UserInfo.query.filter_by(godin_id=godin_id).first()
        if user is not None or user != '':
            phone_num = user.godin_account.phone_num

    cell = {}
    for ware in pagination.items:
        vip_type = VipType.query.filter_by(number=ware.category).first()
        if vip_type is not None:
            cell[ware.id] = vip_type.name
    add_admin_log(user=current_user.username, actions='用户信息', client_ip=request.remote_addr, results='成功')
    return render_template("manage/vip_wares_info.html", data=pagination.items, page=page, per_page=per_page,
                           pagination=pagination, godin_id=godin_id, channel=channel, cate=cell, phone_num=phone_num)


@login_required
def add_vip_members():
    godin_id = request.args.get('godin_id')
    ware_id = request.args.get('ware_id')
    channel = request.args.get('channel')

    act_member = ActivateMembers()
    act_member.godin_id = godin_id
    act_member.ware_id = ware_id
    act_member.channel = channel
    db.session.add(act_member)
    db.session.commit()
    add_admin_log(user=current_user.username, actions='手动添加会员', client_ip=request.remote_addr, results='成功')
    flash('手动添加会员成功')
    return redirect(url_for('manage.get_member_info'))


@login_required
def vip_wares_all_info():
    channel = request.args.get('channel')
    wares = MemberWare.query.filter(MemberWare.channel.in_(['moren', channel]))
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    pagination = wares.paginate(page=page, per_page=per_page, error_out=False)
    if channel is None:
        flash('请选择渠道')
        return redirect(url_for('manage.get_member_info'))
    cell = {}
    for ware in pagination.items:
        vip_type = VipType.query.filter_by(number=ware.category).first()
        if vip_type is not None:
            cell[ware.id] = vip_type.name
    add_admin_log(user=current_user.username, actions='用户信息', client_ip=request.remote_addr, results='成功')
    return render_template("manage/vip_wares_all_info.html", data=pagination.items, page=page, per_page=per_page,
                           pagination=pagination, channel=channel, cate=cell)


@login_required
def add_all_vip_members():
    ware_id = request.args.get('ware_id')
    channel = request.args.get('channel')
    add_all_vip(ware_id=ware_id, channel=channel)
    add_admin_log(user=current_user.username, actions='手动全部添加会员', client_ip=request.remote_addr, results='成功')
    flash('手动全部添加会员成功')
    return redirect(url_for('manage.get_member_info'))


@login_required
def add_vip_service_protocol():
    form = VipServiceProtocolForm()
    protocol = ServiceProtocol.query.filter_by(category=0).first()
    if form.validate_on_submit():
        content = form.content.data
        if protocol is not None:
            service_protocol = ServiceProtocol.query.filter_by(category=0).first()
            service_protocol.content = content
            service_protocol.category = 0
        else:
            service_protocol = ServiceProtocol()
            service_protocol.content = content
            service_protocol.category = 0

        db.session.add(service_protocol)
        db.session.commit()
        add_admin_log(user=current_user.username, actions='添加会员协议', client_ip=request.remote_addr, results='成功')
        flash('添加会员协议成功')
        return redirect(url_for('manage.add_vip_service_protocol'))
    if protocol is not None:
        form.content.data = protocol.content
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='添加会员协议', client_ip=request.remote_addr,
                      results='失败')
    add_admin_log(user=current_user.username, actions='添加会员协议', client_ip=request.remote_addr, results='成功')
    return render_template("manage/add_vip_service_protocol.html", form=form)


def get_vip_week_range():
    year_start_w = request.args.get('year_start_w', type=int)
    year_end_w = request.args.get('year_end_w', type=int)
    week_start = request.args.get('week_start', type=int)
    week_end = request.args.get('week_end', type=int)

    basic_day = datetime.date(year=year_start_w, month=12, day=31)
    basic_week = basic_day.isocalendar()[1]
    week_first_day = basic_day - datetime.timedelta(days=basic_day.weekday()) - datetime. \
        timedelta(days=(basic_week - week_start) * 7)

    last_day = datetime.date(year=year_end_w, month=12, day=31)
    last_basic_week = last_day.isocalendar()[1]
    week_last_day = last_day - datetime.timedelta(days=last_day.weekday()) - datetime. \
        timedelta(days=(last_basic_week - week_end) * 7)

    data = week_first_day.strftime("%Y-%m-%d") + '--' + week_last_day.strftime("%Y-%m-%d")
    return jsonify(code=0, data=data)


@celery.task(name='make_vip_last_day_data')
def make_vip_last_day_data():
    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=1)
    yesterday_start_time = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
    yesterday_end_time = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)
    if VipPayDayStatistics.query.filter_by(date=yesterday.strftime('%Y-%m-%d')).order_by(desc(VipPayDayStatistics.id)).limit(1).first() is not None:
        return False

    # 新增付费人数, 首次付费用户
    new_reg_count = 0
    # 新增付费额, 新的会员付费额
    new_pay_amount = 0
    vip_member_info = db.session.query(VipMembers, func.sum(MemberWareOrder.discount_price), func.count(
        distinct(MemberWareOrder.buyer_godin_id))).join(MemberWareOrder,
                                                        VipMembers.godin_id == MemberWareOrder.buyer_godin_id).filter(
        VipMembers.first_pay_time.between(yesterday_start_time, yesterday_end_time),
        MemberWareOrder.pay_time.between(yesterday_start_time, yesterday_end_time), MemberWareOrder.status == 1,
                                                                                    MemberWareOrder.category == 0).limit(
        1).first()

    if vip_member_info is not None:
        if vip_member_info[1] is not None:
            new_pay_amount = vip_member_info[1]
        if vip_member_info[2] is not None:
            new_reg_count = vip_member_info[2]

    # 过期用户数
    old_not_pay_count = VipMembers.query.filter(VipMembers.valid_time.between(
        yesterday_start_time, yesterday_end_time)).count()
    if old_not_pay_count is None:
        old_not_pay_count = 0

    # 总的续费额 = 新增付费额 + 续费额
    income_amount = 0
    # 总的续费人数 = 新增人数 + 续费人数
    total_payment_user_count = 0

    pay_info = db.session.query(func.sum(MemberWareOrder.discount_price),
                                func.count(distinct(MemberWareOrder.buyer_godin_id))).filter(
        MemberWareOrder.pay_time.between(yesterday_start_time, yesterday_end_time), MemberWareOrder.status == 1,
                                                                                    MemberWareOrder.category == 0).limit(
        1).first()
    if pay_info is not None:
        if pay_info[0] is not None:
            income_amount = pay_info[0]
        if pay_info[1] is not None:
            total_payment_user_count = pay_info[1]
    # 续费额
    old_pay_amount = income_amount - new_pay_amount
    # 续费人数
    old_pay_count = total_payment_user_count - new_reg_count

    info = VipPayDayStatistics()
    info.new_reg_count = new_reg_count
    info.new_pay_amount = new_pay_amount
    info.old_not_pay_count = old_not_pay_count
    info.old_pay_count = old_pay_count
    info.old_pay_amount = old_pay_amount
    info.income_amount = income_amount
    info.date = yesterday

    db.session.add(info)
    db.session.commit()

    # 商业会员统计
    if BusinessPayDayStatistics.query.filter_by(date=yesterday.strftime('%Y-%m-%d')).order_by(desc(BusinessPayDayStatistics.id)).limit(1).first() is not None:
        return False

    # 新增付费人数, 首次付费用户
    new_reg_count = 0
    # 新增付费额, 新的会员付费额
    new_pay_amount = 0
    vip_member_info = db.session.query(BusinessMembers, func.sum(BusinessWareOrder.discount_price), func.count(
        distinct(BusinessWareOrder.buyer_godin_id))).join(
        BusinessWareOrder, BusinessMembers.godin_id == BusinessWareOrder.buyer_godin_id).filter(
        BusinessMembers.first_pay_time.between(yesterday_start_time, yesterday_end_time),
        BusinessWareOrder.pay_time.between(yesterday_start_time, yesterday_end_time),
        BusinessWareOrder.status == 1).limit(1).first()

    if vip_member_info is not None:
        if vip_member_info[1] is not None:
            new_pay_amount = vip_member_info[1]
        if vip_member_info[2] is not None:
            new_reg_count = vip_member_info[2]

    # 过期用户数
    old_not_pay_count = BusinessMembers.query.filter(BusinessMembers.valid_time.between(
        yesterday_start_time, yesterday_end_time)).count()
    if old_not_pay_count is None:
        old_not_pay_count = 0

    # 总的续费额 = 新增付费额 + 续费额
    income_amount = 0
    # 总的续费人数 = 新增人数 + 续费人数
    total_payment_user_count = 0

    pay_info = db.session.query(func.sum(BusinessWareOrder.discount_price),
                                func.count(distinct(BusinessWareOrder.buyer_godin_id))).filter(
        BusinessWareOrder.pay_time.between(yesterday_start_time, yesterday_end_time),
        BusinessWareOrder.status == 1).limit(1).first()
    if pay_info is not None:
        if pay_info[0] is not None:
            income_amount = pay_info[0]
        if pay_info[1] is not None:
            total_payment_user_count = pay_info[1]
    # 续费额
    old_pay_amount = income_amount - new_pay_amount
    # 续费人数
    old_pay_count = total_payment_user_count - new_reg_count

    info = BusinessPayDayStatistics()
    info.new_reg_count = new_reg_count
    info.new_pay_amount = new_pay_amount
    info.old_not_pay_count = old_not_pay_count
    info.old_pay_count = old_pay_count
    info.old_pay_amount = old_pay_amount
    info.income_amount = income_amount
    info.date = yesterday

    db.session.add(info)
    db.session.commit()

    return True


@celery.task(name='make_vip_last_week_data')
def make_vip_last_week_data():
    today = datetime.datetime.now()
    dayto = today - datetime.timedelta(days=today.isoweekday())
    sixdays = datetime.timedelta(days=6)
    dayfrom = dayto - sixdays
    week_start_time = datetime.datetime(dayfrom.year, dayfrom.month, dayfrom.day, 0, 0, 0)
    week_end_time = datetime.datetime(dayto.year, dayto.month, dayto.day, 23, 59, 59)
    if VipPayWeekStatistics.query.filter_by(year=int(week_start_time.strftime('%Y')),
                                            week=int(week_start_time.strftime('%W'))).order_by(desc(VipPayWeekStatistics.id)).limit(1).first() is not None:
        return False
    # 新增付费人数, 首次付费用户
    new_reg_count = 0
    # 新增付费额, 新的会员付费额
    new_pay_amount = 0
    vip_member_info = db.session.query(VipMembers, func.sum(MemberWareOrder.discount_price), func.count(
        distinct(MemberWareOrder.buyer_godin_id))).join(MemberWareOrder,
                                                        VipMembers.godin_id == MemberWareOrder.buyer_godin_id).filter(
        VipMembers.first_pay_time.between(week_start_time, week_end_time),
        MemberWareOrder.pay_time.between(week_start_time, week_end_time), MemberWareOrder.status == 1,
                                                                          MemberWareOrder.category == 0).limit(1).first()
    if vip_member_info is not None:
        if vip_member_info[1] is not None:
            new_pay_amount = vip_member_info[1]
        if vip_member_info[2] is not None:
            new_reg_count = vip_member_info[2]

    # 过期用户数
    old_not_pay_count = VipMembers.query.filter(VipMembers.valid_time.between(
        week_start_time, week_end_time)).count()
    if old_not_pay_count is None:
        old_not_pay_count = 0

    # 总的续费额 = 新增付费额 + 续费额
    income_amount = 0
    # 总的续费人数 = 新增人数 + 续费人数
    total_payment_user_count = 0

    pay_info = db.session.query(func.sum(MemberWareOrder.discount_price),
                                func.count(distinct(MemberWareOrder.buyer_godin_id))).filter(
        MemberWareOrder.pay_time.between(week_start_time, week_end_time), MemberWareOrder.status == 1,
                                                                          MemberWareOrder.category == 0).limit(1).first()
    if pay_info is not None:
        if pay_info[0] is not None:
            income_amount = pay_info[0]
        if pay_info[1] is not None:
            total_payment_user_count = pay_info[1]
    # 续费额
    old_pay_amount = income_amount - new_pay_amount
    # 续费人数
    old_pay_count = total_payment_user_count - new_reg_count

    info = VipPayWeekStatistics()
    info.new_reg_count = new_reg_count
    info.new_pay_amount = new_pay_amount
    info.old_not_pay_count = old_not_pay_count
    info.old_pay_count = old_pay_count
    info.old_pay_amount = old_pay_amount
    info.income_amount = income_amount
    info.year = int(week_start_time.strftime('%Y'))
    info.week = int(week_start_time.strftime('%W'))

    db.session.add(info)
    db.session.commit()

    if BusinessPayWeekStatistics.query.filter_by(year=int(week_start_time.strftime('%Y')),
                                                 week=int(week_start_time.strftime('%W'))).\
            order_by(desc(BusinessPayWeekStatistics.id)).\
            limit(1).first() is not None:
        return False
        # 新增付费人数, 首次付费用户
    new_reg_count = 0
    # 新增付费额, 新的会员付费额
    new_pay_amount = 0
    vip_member_info = db.session.query(BusinessMembers, func.sum(BusinessWareOrder.discount_price), func.count(
        distinct(BusinessWareOrder.buyer_godin_id))).join(
        BusinessWareOrder, BusinessMembers.godin_id == BusinessWareOrder.buyer_godin_id).filter(
        BusinessMembers.first_pay_time.between(week_start_time, week_end_time),
        BusinessWareOrder.pay_time.between(week_start_time, week_end_time),
        BusinessWareOrder.status == 1).limit(1).first()
    if vip_member_info is not None:
        if vip_member_info[1] is not None:
            new_pay_amount = vip_member_info[1]
        if vip_member_info[2] is not None:
            new_reg_count = vip_member_info[2]

    # 过期用户数
    old_not_pay_count = BusinessMembers.query.filter(BusinessMembers.valid_time.between(
        week_start_time, week_end_time)).count()
    if old_not_pay_count is None:
        old_not_pay_count = 0

    # 总的续费额 = 新增付费额 + 续费额
    income_amount = 0
    # 总的续费人数 = 新增人数 + 续费人数
    total_payment_user_count = 0

    pay_info = db.session.query(func.sum(BusinessWareOrder.discount_price),
                                func.count(distinct(BusinessWareOrder.buyer_godin_id))).filter(
        BusinessWareOrder.pay_time.between(week_start_time, week_end_time),
        BusinessWareOrder.status == 1).limit(1).first()
    if pay_info is not None:
        if pay_info[0] is not None:
            income_amount = pay_info[0]
        if pay_info[1] is not None:
            total_payment_user_count = pay_info[1]
    # 续费额
    old_pay_amount = income_amount - new_pay_amount
    # 续费人数
    old_pay_count = total_payment_user_count - new_reg_count

    info = BusinessPayWeekStatistics()
    info.new_reg_count = new_reg_count
    info.new_pay_amount = new_pay_amount
    info.old_not_pay_count = old_not_pay_count
    info.old_pay_count = old_pay_count
    info.old_pay_amount = old_pay_amount
    info.income_amount = income_amount
    info.year = int(week_start_time.strftime('%Y'))
    info.week = int(week_start_time.strftime('%W'))

    db.session.add(info)
    db.session.commit()

    return True


@celery.task(name='make_vip_last_month_data')
def make_vip_last_month_data():
    today = datetime.datetime.now()
    dayto = today - datetime.timedelta(days=today.day)
    month_start_time = datetime.datetime(dayto.year, dayto.month, 1, 0, 0, 0)
    month_end_time = datetime.datetime(dayto.year, dayto.month, dayto.day, 23, 59, 59)
    if VipPayMonthStatistics.query.filter_by(year=int(month_start_time.strftime('%Y')),
                                             month=int(month_start_time.strftime('%m'))).order_by(desc(VipPayMonthStatistics.id)).limit(1).first() is not None:
        return False
    # 新增付费人数, 首次付费用户
    new_reg_count = 0
    # 新增付费额, 新的会员付费额
    new_pay_amount = 0
    vip_member_info = db.session.query(VipMembers, func.sum(MemberWareOrder.discount_price), func.count(
        distinct(MemberWareOrder.buyer_godin_id))).join(MemberWareOrder,
                                                        VipMembers.godin_id == MemberWareOrder.buyer_godin_id).filter(
        VipMembers.first_pay_time.between(month_start_time, month_end_time),
        MemberWareOrder.pay_time.between(month_start_time, month_end_time), MemberWareOrder.status == 1,
                                                                            MemberWareOrder.category == 0).limit(
        1).first()
    if vip_member_info is not None:
        if vip_member_info[1] is not None:
            new_pay_amount = vip_member_info[1]
        if vip_member_info[2] is not None:
            new_reg_count = vip_member_info[2]

    # 过期用户数
    old_not_pay_count = VipMembers.query.filter(VipMembers.valid_time.between(
        month_start_time, month_end_time)).count()
    if old_not_pay_count is None:
        old_not_pay_count = 0

    # 总的续费额 = 新增付费额 + 续费额
    income_amount = 0
    # 总的续费人数 = 新增人数 + 续费人数
    total_payment_user_count = 0

    pay_info = db.session.query(func.sum(MemberWareOrder.discount_price),
                                func.count(distinct(MemberWareOrder.buyer_godin_id))).filter(
        MemberWareOrder.pay_time.between(month_start_time, month_end_time), MemberWareOrder.status == 1,
                                                                            MemberWareOrder.category == 0).limit(
        1).first()
    if pay_info is not None:
        if pay_info[0] is not None:
            income_amount = pay_info[0]
        if pay_info[1] is not None:
            total_payment_user_count = pay_info[1]
    # 续费额
    old_pay_amount = income_amount - new_pay_amount
    # 续费人数
    old_pay_count = total_payment_user_count - new_reg_count

    info = VipPayMonthStatistics()
    info.new_reg_count = new_reg_count
    info.new_pay_amount = new_pay_amount
    info.old_not_pay_count = old_not_pay_count
    info.old_pay_count = old_pay_count
    info.old_pay_amount = old_pay_amount
    info.income_amount = income_amount
    info.year = int(month_start_time.strftime('%Y'))
    info.month = int(month_start_time.strftime('%m'))

    db.session.add(info)
    db.session.commit()

    if BusinessPayMonthStatistics.query.filter_by(year=int(month_start_time.strftime('%Y')),
                                                  month=int(month_start_time.strftime('%m'))).\
            order_by(desc(BusinessPayMonthStatistics.id)).limit(1).first() is not None:
        return False
        # 新增付费人数, 首次付费用户
    new_reg_count = 0
    # 新增付费额, 新的会员付费额
    new_pay_amount = 0
    vip_member_info = db.session.query(BusinessMembers, func.sum(BusinessWareOrder.discount_price), func.count(
        distinct(BusinessWareOrder.buyer_godin_id))).join(
        BusinessWareOrder, BusinessMembers.godin_id == BusinessWareOrder.buyer_godin_id).filter(
        BusinessMembers.first_pay_time.between(month_start_time, month_end_time),
        BusinessWareOrder.pay_time.between(month_start_time, month_end_time),
        BusinessWareOrder.status == 1).limit(1).first()
    if vip_member_info is not None:
        if vip_member_info[1] is not None:
            new_pay_amount = vip_member_info[1]
        if vip_member_info[2] is not None:
            new_reg_count = vip_member_info[2]

    # 过期用户数
    old_not_pay_count = BusinessMembers.query.filter(BusinessMembers.valid_time.between(
        month_start_time, month_end_time)).count()
    if old_not_pay_count is None:
        old_not_pay_count = 0

    # 总的续费额 = 新增付费额 + 续费额
    income_amount = 0
    # 总的续费人数 = 新增人数 + 续费人数
    total_payment_user_count = 0

    pay_info = db.session.query(func.sum(BusinessWareOrder.discount_price),
                                func.count(distinct(BusinessWareOrder.buyer_godin_id))).filter(
        BusinessWareOrder.pay_time.between(month_start_time, month_end_time),
        BusinessWareOrder.status == 1).limit(1).first()
    if pay_info is not None:
        if pay_info[0] is not None:
            income_amount = pay_info[0]
        if pay_info[1] is not None:
            total_payment_user_count = pay_info[1]
    # 续费额
    old_pay_amount = income_amount - new_pay_amount
    # 续费人数
    old_pay_count = total_payment_user_count - new_reg_count

    info = BusinessPayMonthStatistics()
    info.new_reg_count = new_reg_count
    info.new_pay_amount = new_pay_amount
    info.old_not_pay_count = old_not_pay_count
    info.old_pay_count = old_pay_count
    info.old_pay_amount = old_pay_amount
    info.income_amount = income_amount
    info.year = int(month_start_time.strftime('%Y'))
    info.month = int(month_start_time.strftime('%m'))

    db.session.add(info)
    db.session.commit()
    return True


@login_required
def index():
    zero_time = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d') + " 00:00:00",
                                           '%Y-%m-%d %H:%M:%S')
    reg_count = DeviceInfo.query.filter_by(status=1). \
        filter(DeviceInfo.create_time.between(zero_time, datetime.datetime.now())).count()
    un_reg_count = DeviceInfo.query.filter_by(status=0). \
        filter(DeviceInfo.create_time.between(zero_time, datetime.datetime.now())).count()
    total = DeviceInfo.query.filter_by(status=0).count() + GodinAccount.query.count()
    return render_template("manage/index.html", reg_count=reg_count, un_reg_count=un_reg_count, total=total)


@login_required
def communicate_group():
    form = CommunicationGroupForm()
    infos = CommunicationGroup.query.all()
    if form.validate_on_submit() and infos is not None:
        v_group_number = form.v_group_number.data.strip()
        v_group_key = form.v_group_key.data.strip()

        if len(infos) > 0:
            for info in infos:
                if info.type == 1:
                    info.group_number = v_group_number
                    info.group_key = v_group_key
                db.session.add(info)
        else:
            king_info = CommunicationGroup()
            king_info.type = 1
            king_info.group_number = v_group_number
            king_info.group_key = v_group_key

            db.session.add(king_info)
        try:
            db.session.commit()
            add_admin_log(user=current_user.username, actions='添加交流群成功', client_ip=request.remote_addr,
                          results='成功')
            return render_template("manage/communication_group.html", form=form)
        except Exception as e:
            print(e)
            db.session.rollback()
            add_admin_log(user=current_user.username, actions='添加交流群失败', client_ip=request.remote_addr,
                          results='失败')

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='添加交流群失败', client_ip=request.remote_addr,
                      results=error[0])

    if infos is not None and len(infos) > 0:
        for info in infos:
            if info.type == 1:
                form.v_group_number.data = info.group_number
                form.v_group_key.data = info.group_key

    return render_template("manage/communication_group.html", form=form)


@login_required
def open_screen_ads_data():
    form = OpenScreenAdsDataForm()
    query = OpenScreenAds.query
    if form.validate_on_submit():
        name = form.name.data
        position = form.position.data
        source = form.source.data
        status = form.status.data
        start_time = form.start_time.data
        end_time = form.end_time.data
    else:
        name = request.args.get('name')
        position = request.args.get('position', type=int)
        source = request.args.get('source', type=int)
        status = request.args.get('status', type=int)
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d').date()
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d').date()

    if name is not None:
        form.name.data = name
        if form.name.data != '':
            query = query.filter(OpenScreenAds.name.like('%' + form.name.data + '%'))
    if position is not None:
        form.position.data = position
        if form.position.data != -1:
            query = query.filter_by(position=form.position.data)
    if source is not None:
        form.source.data = source
        if form.source.data != -1:
            query = query.filter_by(source=form.source.data)
    if status is not None:
        form.status.data = status
        if form.status.data != -1:
            query = query.filter_by(status=form.status.data)

    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)

    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
    else:
        days = datetime.datetime.now() - datetime.timedelta(days=6)
        end_time = datetime.datetime.now().date()
        start_time = days.date()
        form.start_time.data = start_time
        form.end_time.data = end_time

    res = []
    for open_ads in pagination.items:
        obtain_number = 0
        entry_number = 0
        total_entry_query_all = db.session.query(func.sum(OpenScreenAdsData.count)).filter_by(
            ad_id=open_ads.id, operation=0)
        total_obtain_query_all = db.session.query(func.sum(OpenScreenAdsData.count)).filter_by(
            ad_id=open_ads.id, operation=1)
        if start_time is not None and end_time is not None:
            entry_info = total_entry_query_all.filter(OpenScreenAdsData.record_time.between(
                start_time, end_time)).first()
            obtain_info = total_obtain_query_all.filter(OpenScreenAdsData.record_time.between(
                start_time, end_time)).first()

            if entry_info is not None:
                if entry_info[0] is not None:
                    entry_number = entry_info[0]
            if obtain_info is not None:
                if obtain_info[0] is not None:
                    obtain_number = obtain_info[0]

        cell = dict(id=open_ads.id, name=open_ads.name, source=open_ads.source, position=open_ads.position,
                    advertiser=open_ads.advertiser, number=open_ads.number, entry_number=entry_number,
                    obtain_number=obtain_number)
        res.append(cell)

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='开屏广告SDK数据', client_ip=request.remote_addr,
                      results=error[0])
    if not form.errors:
        add_admin_log(user=current_user.username, actions='开屏广告SDK数据', client_ip=request.remote_addr,
                      results='成功')
    return render_template("manage/open_screen_ads_data.html", form=form, data=res, pagination=pagination)


@login_required
def interactive_ads():
    form = InteractiveAdsForm()
    if form.validate_on_submit():
        name = form.name.data
        position = form.position.data
        source = form.source.data
        icon = request.files['icon']
        icon_size = len(icon.read())
        icon_name = secure_filename(icon.filename)
        third_link = form.third_link.data
        charge_mode = form.charge_mode.data
        refresh_status = form.refresh_status.data
        user_count = form.user_count.data
        morning_count = form.morning_count.data
        afternoon_count = form.afternoon_count.data
        night_count = form.night_count.data

        icon_flag = False
        new_icon_name = str(round(time.time()))
        icon_dir = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], 'InteractiveAds')
        if not os.path.exists(icon_dir):
            os.makedirs(icon_dir)

        if icon_size > 0 and form.source.data == 0:
            if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', icon.filename.rsplit('.', 1)[0])):
                flash('图片名称不能为纯汉字')
                add_admin_log(user=current_user.username, actions='添加互动广告', client_ip=request.remote_addr,
                              results='图片名称不能为纯汉字')
                return render_template("manage/interactive_ads.html", form=form)
            if icon_size > 100 * 1024 or icon_name.rsplit('.', 1)[1] not in ['jpg', 'png', 'jpeg', 'JPG', 'JPEG',
                                                                             'PNG']:
                flash("图片格式不否, 仅支持(jpg/jpeg, png) 小余100k")
                add_admin_log(user=current_user, actions='添加互动广告', client_ip=request.remote_addr,
                              results='图片格式错误')
                return render_template("manage/interactive_ads.html", form=form)

            img = Image.open(icon)
            new_icon_name = icon_name.rsplit('.', 1)[0] + '_' + new_icon_name + '.' + icon_name.rsplit('.', 1)[1]
            img.save(os.path.join(icon_dir, new_icon_name))
            icon_flag = True

        info = InteractiveAds()
        info.name = name
        info.position = position
        info.source = source
        info.third_link = third_link.strip()
        info.charge_mode = charge_mode
        info.status = 0
        info.refresh_status = refresh_status
        info.user_count = user_count
        info.morning_count = morning_count
        info.afternoon_count = afternoon_count
        info.night_count = night_count
        if icon_flag:
            info.icon = os.path.join(current_app.config['PHOTO_TAG'], 'InteractiveAds', new_icon_name)

        try:
            db.session.add(info)
            db.session.commit()
            add_admin_log(user=current_user.username, actions='添加互动广告', client_ip=request.remote_addr,
                          results='成功')
            return redirect(url_for('manage.get_interactive_ads'))
        except Exception as e:
            print(e)
            db.session.rollback()
            new_icon_name = os.path.join(icon_dir, new_icon_name)
            if icon_flag and os.path.exists(new_icon_name) and os.path.isfile(new_icon_name):
                os.remove(new_icon_name)
            add_admin_log(user=current_user.username, actions='添加互动广告', client_ip=request.remote_addr,
                          results='失败')
            flash('添加互动广告失败')
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='添加互动广告', client_ip=request.remote_addr, results=error[0])

    return render_template("manage/interactive_ads.html", form=form)


@login_required
def get_interactive_ads():
    form = QueryInteractiveAdsForm()
    query = InteractiveAds.query
    if form.validate_on_submit():
        name = form.name.data
        position = form.position.data
        source = form.source.data
        status = form.status.data
        start_time = form.start_time.data
        end_time = form.end_time.data
    else:
        name = request.args.get('name')
        position = request.args.get('position', type=int)
        source = request.args.get('source', type=int)
        status = request.args.get('status', type=int)
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d').date()
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d').date()

    if name is not None:
        form.name.data = name
        if form.name.data != '':
            query = query.filter(InteractiveAds.name.like('%' + form.name.data + '%'))
    if position is not None:
        form.position.data = position
        if form.position.data != -1:
            query = query.filter_by(position=form.position.data)
    if source is not None:
        form.source.data = source
        if form.source.data != -1:
            query = query.filter_by(source=form.source.data)
    if status is not None:
        form.status.data = status
        if form.status.data != -1:
            query = query.filter_by(status=form.status.data)

    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)

    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
    else:
        days = datetime.datetime.now() - datetime.timedelta(days=6)
        end_time = datetime.datetime.now().date()
        start_time = days.date()
        form.start_time.data = start_time
        form.end_time.data = end_time

    res = []
    for info in pagination.items:
        click_number = 0
        total_click_number = 0

        total_click_query_all = db.session.query(func.sum(InteractiveAdsStatistics.count), func.count()).filter_by(
            ad_id=info.id, operation=1)
        if start_time is not None and end_time is not None:
            click_info = total_click_query_all.filter(InteractiveAdsStatistics.record_time.between(
                start_time, end_time)).first()
        total_display_number = 0
        display_number = 0

        if click_info is not None:
            if click_info[1] is not None:
                click_number = click_info[1]
            if click_info[0] is not None:
                total_click_number = click_info[0]

        cell = dict(id=info.id, name=info.name, source=info.source, position=info.position,
                    total_display_number=total_display_number, display_number=display_number,
                    click_number=click_number, total_click_number=total_click_number, status=info.status)
        res.append(cell)

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='查看互动广告', client_ip=request.remote_addr,
                      results=error[0])
    if not form.errors:
        add_admin_log(user=current_user.username, actions='查看互动广告', client_ip=request.remote_addr,
                      results='成功')
    return render_template("manage/get_interactive_ads.html", form=form, data=res, pagination=pagination)


@login_required
def set_interactive_status():
    ad_id = request.args.get('id', type=int)
    status = request.args.get('status', type=int)

    if ad_id < 0 or (status != 0 and status != 1):
        add_admin_log(user=current_user.username, actions='设置互动广告状态', client_ip=request.remote_addr,
                      results='参数错误')
        return jsonify({'code': 1})
    else:
        try:
            InteractiveAds.query.filter_by(id=ad_id).update(dict(status=status))
            db.session.commit()

            add_admin_log(user=current_user.username, actions='设置互动广告状态', client_ip=request.remote_addr,
                          results='成功')
            return jsonify({'code': 0})
        except Exception as e:
            print(e)
            db.session.rollback()
            add_admin_log(user=current_user.username, actions='设置互动广告状态', client_ip=request.remote_addr,
                          results='失败')
            return jsonify({'code': 1})


@login_required
def interactive_ads_info(ad_id):
    ad_info = InteractiveAds.query.filter_by(id=ad_id).first()

    add_admin_log(user=current_user.username, actions='查看互动广告信息', client_ip=request.remote_addr, results='成功')
    return render_template("manage/interactive_ads_info.html", data=ad_info, base_url=current_app.config['FILE_SERVER'],
                           ad_id=ad_id)


@login_required
def edit_interactive_ads(ad_id):
    form = EditInteractiveAdsForm()
    info = InteractiveAds.query.filter_by(id=ad_id).first()
    if form.validate_on_submit() and info is not None:
        name = form.name.data
        # position = form.position.data
        # source = form.source.data
        # charge_mode = form.charge_mode.data
        icon = request.files['icon']
        icon_size = len(icon.read())
        icon_name = secure_filename(icon.filename)
        third_link = form.third_link.data
        refresh_status = form.refresh_status.data
        user_count = form.user_count.data
        morning_count = form.morning_count.data
        afternoon_count = form.afternoon_count.data
        night_count = form.night_count.data

        icon_flag = False
        new_icon_name = str(round(time.time()))
        old_icon_name = info.icon
        icon_dir = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], 'InteractiveAds')
        if not os.path.exists(icon_dir):
            os.makedirs(icon_dir)

        if icon_size > 0 and form.source.data == 0:
            if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', icon.filename.rsplit('.', 1)[0])):
                flash('图片名称不能为纯汉字')
                add_admin_log(user=current_user.username, actions='编辑互动广告', client_ip=request.remote_addr,
                              results='图片名称不能为纯汉字')
                return redirect(url_for('manage.edit_interactive_ads', ad_id=ad_id))
            if icon_size > 100 * 1024 or icon_name.rsplit('.', 1)[1] not in ['jpg', 'png', 'jpeg', 'JPG', 'JPEG',
                                                                             'PNG']:
                flash("图片格式不否, 仅支持(jpg/jpeg, png) 小余100k")
                add_admin_log(user=current_user, actions='编辑互动广告', client_ip=request.remote_addr,
                              results='图片格式错误')
                return redirect(url_for('manage.edit_interactive_ads', ad_id=ad_id))

            icon_dir = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], 'InteractiveAds')
            if not os.path.exists(icon_dir):
                os.makedirs(icon_dir)

            img = Image.open(icon)
            new_icon_name = icon_name.rsplit('.', 1)[0] + '_' + new_icon_name + '.' + icon_name.rsplit('.', 1)[1]
            img.save(os.path.join(icon_dir, new_icon_name))
            info.icon = os.path.join(current_app.config['PHOTO_TAG'], 'InteractiveAds', new_icon_name)
            icon_flag = True

        info.name = name
        # info.position = position
        # info.source = source
        # info.charge_mode = charge_mode
        info.third_link = third_link.strip()
        info.refresh_status = refresh_status
        info.user_count = user_count
        info.morning_count = morning_count
        info.afternoon_count = afternoon_count
        info.night_count = night_count

        try:
            db.session.add(info)
            db.session.commit()
            old_icon_name = os.path.join(os.getcwd(), old_icon_name)
            if icon_flag and os.path.exists(old_icon_name) and os.path.isfile(old_icon_name):
                os.remove(old_icon_name)
            add_admin_log(user=current_user.username, actions='编辑互动广告', client_ip=request.remote_addr,
                          results='成功')
            return redirect(url_for('manage.interactive_ads_info', ad_id=ad_id))
        except Exception as e:
            print(e)
            db.session.rollback()
            new_icon_name = os.path.join(icon_dir, new_icon_name)
            if icon_flag and os.path.exists(new_icon_name) and os.path.isfile(new_icon_name):
                os.remove(new_icon_name)
            add_admin_log(user=current_user.username, actions='编辑互动广告', client_ip=request.remote_addr,
                          results='失败')
            flash('编辑互动广告失败')

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='编辑互动广告', client_ip=request.remote_addr, results=error[0])
    if info is not None:
        form.name.data = info.name
        form.position.data = info.position
        form.source.data = info.source
        form.charge_mode.data = info.charge_mode
        form.third_link.data = info.third_link
        form.refresh_status.data = info.refresh_status
        form.user_count.data = info.user_count
        form.morning_count.data = info.morning_count
        form.afternoon_count.data = info.afternoon_count
        form.night_count.data = info.night_count

    if not form.errors:
        add_admin_log(user=current_user.username, actions='编辑互动广告', client_ip=request.remote_addr, results='成功')

    return render_template("manage/edit_interactive_ads.html", form=form, ad_id=ad_id)


@login_required
def get_banner_config(ad_id):
    print(ad_id)
    form = AdsConfigForm()
    query = BannerConfig.query.filter_by(ad_id=ad_id)
    if form.validate_on_submit():
        channel = form.channel.data
        version = form.version.data
    else:
        channel = request.args.get('channel')
        version = request.args.get('version', type=int)

    if channel is not None:
        form.channel.data = channel
        if form.channel.data != '':
            query = query.filter(BannerConfig.channel.like('%' + form.channel.data + '%'))
    if version is not None:
        form.version.data = version
        if form.version.data != -1:
            query = query.filter_by(version=form.version.data)

    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=120, error_out=False)

    res = []
    for info in pagination.items:
        cell = dict(id=info.id, channel=info.channel, version=info.version, status=info.status)
        res.append(cell)

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='查看banner配置', client_ip=request.remote_addr,
                      results=error[0])
    if not form.errors:
        add_admin_log(user=current_user.username, actions='查看banner配置', client_ip=request.remote_addr,
                      results='成功')
    return render_template("manage/get_banner_config.html", form=form, data=res, pagination=pagination, ad_id=ad_id)


# banner, 开屏, 互动广告和CPA公用接口
@login_required
def ads_config():
    print('*****banner_config*****')
    # 选中
    ids = request.form.getlist('ids', type=int)
    # 位选中
    no_ids = request.form.getlist('no_ids', type=int)
    # 设置的广告id
    ad_id = request.form.get('ad_id', type=int)
    # banner 0, 开屏 1,  互动 2, CPA 3
    ad_type = request.form.get('type', type=int)

    flag = False
    if ad_id == 0:
        add_admin_log(user=current_user.username, actions='更新广告配置' + 'type' + str(ad_type),
                      client_ip=request.remote_addr, results='参数错误')
        return jsonify({'code': 1})
    else:
        try:
            if len(ids) > 0:
                if ad_type == 0:
                    BannerConfig.query.filter(BannerConfig.ad_id == ad_id, BannerConfig.id.in_(ids)).update(
                        dict(status=1), synchronize_session=False)
                if ad_type == 1:
                    OpenConfig.query.filter(OpenConfig.ad_id == ad_id, OpenConfig.id.in_(ids)).update(
                        dict(status=1), synchronize_session=False)
                if ad_type == 2:
                    InteractiveConfig.query.filter(InteractiveConfig.ad_id == ad_id,
                                                   InteractiveConfig.id.in_(ids)).update(dict(status=1),
                                                                                         synchronize_session=False)
                flag = True
            if len(no_ids) > 0:
                if ad_type == 0:
                    BannerConfig.query.filter(BannerConfig.ad_id == ad_id,
                                              BannerConfig.id.in_(no_ids)).update(dict(status=0),
                                                                                  synchronize_session=False)
                if ad_type == 1:
                    OpenConfig.query.filter(OpenConfig.ad_id == ad_id,
                                            OpenConfig.id.in_(no_ids)).update(dict(status=0),
                                                                              synchronize_session=False)
                if ad_type == 2:
                    InteractiveConfig.query.filter(InteractiveConfig.ad_id == ad_id,
                                                   InteractiveConfig.id.in_(no_ids)).update(dict(status=0),
                                                                                            synchronize_session=False)
                flag = True

            if flag:
                db.session.commit()
            add_admin_log(user=current_user.username, actions='更新广告配置' + 'type' + str(ad_type),
                          client_ip=request.remote_addr,
                          results='成功')
            return jsonify({'code': 0})
        except Exception as e:
            print(e)
            db.session.rollback()
            add_admin_log(user=current_user.username, actions='更新广告配置' + 'type' + str(ad_type),
                          client_ip=request.remote_addr, results='失败')
            return jsonify({'code': 1})


# banner, 开屏, 互动广告公用接口
@login_required
def export_channel():
    print('*****export channel*****')
    ad_id = request.form.get('ad_id', type=int)
    # banner 0, 开屏 1,  互动 2, CPA 3
    ad_type = request.form.get('type', type=int)

    flag = False
    if ad_id == 0:
        add_admin_log(user=current_user.username, actions='导入广告渠道' + 'type' + str(ad_type),
                      client_ip=request.remote_addr, results='参数错误')
        return jsonify({'code': 1})
    else:
        try:
            current_time = datetime.datetime.now()
            channel_infos = Channel.query.all()
            for channel_info in channel_infos:
                if ad_type == 0:
                    if BannerConfig.query.filter_by(channel=channel_info.channel, ad_id=ad_id).first():
                        continue
                    history_info = BannerConfig()
                    history_info.channel = channel_info.channel
                    history_info.version = 0
                    history_info.status = 0
                    history_info.create_time = current_time
                    history_info.ad_id = ad_id
                    db.session.add(history_info)

                    now_info = BannerConfig()
                    now_info.channel = channel_info.channel
                    now_info.version = 1
                    now_info.status = 0
                    now_info.create_time = current_time
                    now_info.ad_id = ad_id
                    db.session.add(now_info)
                    flag = True
                if ad_type == 1:
                    if OpenConfig.query.filter_by(channel=channel_info.channel, ad_id=ad_id).first():
                        continue
                    history_info = OpenConfig()
                    history_info.channel = channel_info.channel
                    history_info.version = 0
                    history_info.status = 0
                    history_info.create_time = current_time
                    history_info.ad_id = ad_id
                    db.session.add(history_info)

                    now_info = OpenConfig()
                    now_info.channel = channel_info.channel
                    now_info.version = 1
                    now_info.status = 0
                    now_info.create_time = current_time
                    now_info.ad_id = ad_id
                    db.session.add(now_info)
                    flag = True
                if ad_type == 2:
                    if InteractiveConfig.query.filter_by(channel=channel_info.channel, ad_id=ad_id).first():
                        continue
                    history_info = InteractiveConfig()
                    history_info.channel = channel_info.channel
                    history_info.version = 0
                    history_info.status = 0
                    history_info.create_time = current_time
                    history_info.ad_id = ad_id
                    db.session.add(history_info)

                    now_info = InteractiveConfig()
                    now_info.channel = channel_info.channel
                    now_info.version = 1
                    now_info.status = 0
                    now_info.create_time = current_time
                    now_info.ad_id = ad_id
                    db.session.add(now_info)
                    flag = True
            if flag:
                db.session.commit()
            add_admin_log(user=current_user.username, actions='导入广告渠道' + 'type' + str(ad_type),
                          client_ip=request.remote_addr, results='成功')
            return jsonify({'code': 0})
        except Exception as e:
            print(e)
            db.session.rollback()
            add_admin_log(user=current_user.username, actions='导入广告渠道' + 'type' + str(ad_type),
                          client_ip=request.remote_addr, results='失败')
            return jsonify({'code': 1})


@login_required
def get_open_config(ad_id):
    print(ad_id)
    form = AdsConfigForm()
    query = OpenConfig.query.filter_by(ad_id=ad_id)
    if form.validate_on_submit():
        channel = form.channel.data
        version = form.version.data
    else:
        channel = request.args.get('channel')
        version = request.args.get('version', type=int)

    if channel is not None:
        form.channel.data = channel
        if form.channel.data != '':
            query = query.filter(OpenConfig.channel.like('%' + form.channel.data + '%'))
    if version is not None:
        form.version.data = version
        if form.version.data != -1:
            query = query.filter_by(version=form.version.data)

    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=120, error_out=False)

    res = []
    for info in pagination.items:
        cell = dict(id=info.id, channel=info.channel, version=info.version, status=info.status)
        res.append(cell)

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='查看开屏配置', client_ip=request.remote_addr,
                      results=error[0])
    if not form.errors:
        add_admin_log(user=current_user.username, actions='查看开屏配置', client_ip=request.remote_addr,
                      results='成功')
    return render_template("manage/get_open_config.html", form=form, data=res, pagination=pagination, ad_id=ad_id)


@login_required
def get_interactive_config(ad_id):
    print(ad_id)
    form = AdsConfigForm()
    query = InteractiveConfig.query.filter_by(ad_id=ad_id)
    if form.validate_on_submit():
        channel = form.channel.data
        version = form.version.data
    else:
        channel = request.args.get('channel')
        version = request.args.get('version', type=int)

    if channel is not None:
        form.channel.data = channel
        if form.channel.data != '':
            query = query.filter(InteractiveConfig.channel.like('%' + form.channel.data + '%'))
    if version is not None:
        form.version.data = version
        if form.version.data != -1:
            query = query.filter_by(version=form.version.data)

    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=120, error_out=False)

    res = []
    for info in pagination.items:
        cell = dict(id=info.id, channel=info.channel, version=info.version, status=info.status)
        res.append(cell)

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='查看互动配置', client_ip=request.remote_addr,
                      results=error[0])
    if not form.errors:
        add_admin_log(user=current_user.username, actions='查看互动配置', client_ip=request.remote_addr,
                      results='成功')
    return render_template("manage/get_interactive_config.html", form=form, data=res, pagination=pagination,
                           ad_id=ad_id)


@login_required
def ads_icon():
    form = AdsIconForm()
    if form.validate_on_submit():
        icon = request.files['icon']
        icon_name = secure_filename(icon.filename)
        icon_size = len(icon.read())
        position = form.position.data
        jump_link = form.jump_link.data

        if AdsIcon.query.filter(AdsIcon.position == position).first() is not None:
            flash('该位置广告已经存在, 无法添加')
            return redirect(url_for('manage.ads_icon'))
        if icon_size <= 0:
            flash('广告图不能为空')
            add_admin_log(user=current_user.username, actions='添加默认广告图标', client_ip=request.remote_addr,
                          results='广告图空')
            return redirect(url_for('manage.ads_icon'))
        if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', icon.filename.rsplit('.', 1)[0])):
            flash('图片名称不能为纯汉字')
            add_admin_log(user=current_user.username, actions='添加默认广告图标', client_ip=request.remote_addr,
                          results='图片名称不能为纯汉字')
            return redirect(url_for('manage.ads_icon'))

        if icon_name.rsplit('.', 1)[1] not in ['jpg', 'png', 'jpeg', 'JPG', 'JPEG', 'PNG']:
            flash("图片格式不否/图片没有上传, 仅支持(jpg/jpeg, png)")
            add_admin_log(user=current_user, actions='添加默认广告图标', client_ip=request.remote_addr,
                          results='图片格式错误')
            return redirect(url_for('manage.ads_icon'))

        icon_dir = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], 'AdsIcon')
        if not os.path.exists(icon_dir):
            os.makedirs(icon_dir)

        img = Image.open(icon)
        rname = icon_name.rsplit('.', 1)[0] + '_' + str(round(time.time())) + '.' + icon_name.rsplit('.', 1)[1]
        img.save(os.path.join(icon_dir, rname))

        info = AdsIcon()
        info.icon_addr = os.path.join(current_app.config['PHOTO_TAG'], 'AdsIcon', rname)
        info.position = position
        info.jump_link = jump_link.strip()

        try:
            db.session.add(info)
            db.session.commit()
            add_admin_log(user=current_user.username, actions='添加默认广告图标', client_ip=request.remote_addr,
                          results='成功')
            return redirect(url_for('manage.ads_icon'))
        except Exception as e:
            print(e)
            db.session.rollback()
            name = os.path.join(icon_dir, rname)
            if os.path.exists(name) and os.path.isfile(name):
                os.remove(name)
            add_admin_log(user=current_user.username, actions='添加默认广告图标', client_ip=request.remote_addr,
                          results='失败')
            flash('添加广告默认图标失败')

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
            add_admin_log(user=current_user.username, actions='添加默认广告图标', client_ip=request.remote_addr,
                          results=error[0])

    return render_template("manage/ads_icon.html", form=form)


@login_required
def edit_ads_icon(icon_id):
    form = AdsIconForm()
    info = AdsIcon.query.filter_by(id=icon_id).first()
    if form.validate_on_submit() and info is not None:
        icon = request.files['icon']
        icon_name = secure_filename(icon.filename)
        icon_size = len(icon.read())
        position = form.position.data
        jump_link = form.jump_link.data

        if icon_size > 0 and all(map(lambda c: '\u4e00' <= c <= '\u9fa5', icon.filename.rsplit('.', 1)[0])):
            flash('图片名称不能为纯汉字')
            add_admin_log(user=current_user.username, actions='编辑默认广告图标', client_ip=request.remote_addr,
                          results='图片名称不能为纯汉字')
            return redirect(url_for('manage.edit_ads_icon', icon_id=icon_id))

        if icon_size > 0 and icon_name.rsplit('.', 1)[1] not in ['jpg', 'png', 'jpeg', 'JPG', 'JPEG', 'PNG']:
            flash("图片格式不否/图片没有上传, 仅支持(jpg/jpeg, png)")
            add_admin_log(user=current_user, actions='编辑默认广告图标', client_ip=request.remote_addr,
                          results='图片格式错误')
            return redirect(url_for('manage.edit_ads_icon', icon_id=icon_id))

        icon_dir = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], 'AdsIcon')
        if not os.path.exists(icon_dir):
            os.makedirs(icon_dir)
        old_icon = info.icon_addr
        new_icon = ''
        flag = False
        if icon_size > 0:
            img = Image.open(icon)
            new_icon = icon_name.rsplit('.', 1)[0] + '_' + str(round(time.time())) + '.' + icon_name.rsplit('.', 1)[1]
            img.save(os.path.join(icon_dir, new_icon))
            flag = True

        if flag:
            info.icon_addr = os.path.join(current_app.config['PHOTO_TAG'], 'AdsIcon', new_icon)
        info.position = position
        info.jump_link = jump_link.strip()

        try:
            db.session.add(info)
            db.session.commit()
            name = os.path.join(os.getcwd(), old_icon)
            if flag and os.path.exists(name) and os.path.isfile(name):
                os.remove(name)
            add_admin_log(user=current_user.username, actions='编辑默认广告图标', client_ip=request.remote_addr,
                          results='成功')
            return redirect(url_for('manage.get_ads_icon'))
        except Exception as e:
            print(e)
            db.session.rollback()
            name = os.path.join(icon_dir, new_icon)
            if flag and os.path.exists(name) and os.path.isfile(name):
                os.remove(name)
            add_admin_log(user=current_user.username, actions='编辑默认广告图标', client_ip=request.remote_addr,
                          results='失败')
            flash('编辑广告默认图标失败')
            return redirect(url_for('manage.edit_ads_icon', icon_id=icon_id))

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
            add_admin_log(user=current_user.username, actions='编辑默认广告图标', client_ip=request.remote_addr,
                          results=error[0])
    if info is not None:
        form.jump_link.data = info.jump_link
        form.position.data = info.position

    return render_template("manage/edit_ads_icon.html", form=form, icon_id=icon_id)


@login_required
def get_ads_icon():
    page = request.args.get('page', 1, type=int)
    pagination = AdsIcon.query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    data = pagination.items
    add_admin_log(user=current_user.username, actions='查询默认广告图标信息', client_ip=request.remote_addr,
                  results='成功')
    return render_template("manage/get_ads_icon.html", data=data, base_url=current_app.config['FILE_SERVER'],
                           pagination=pagination)


@login_required
def set_ads_icon_status():
    ad_id = request.args.get('id', type=int)
    icon = AdsIcon.query.filter_by(id=ad_id).first()
    if icon is not None:
        if icon.status == 0:
            code = 1
            icon.status = 1
            add_admin_log(user=current_user.username, actions='打开显示', client_ip=request.remote_addr,
                          results='成功')
        else:
            code = 0
            icon.status = 0
            add_admin_log(user=current_user.username, actions='关闭显示', client_ip=request.remote_addr,
                          results='成功')
        db.session.add(icon)
        db.session.commit()
        return jsonify(code=code)
    return jsonify(code=-1)


@login_required
def edit_open_strategy():
    form = OpenStrategyForm()
    protocol = ServiceProtocol.query.filter_by(category=1).first()
    if form.validate_on_submit():
        display_number = form.display_number.data
        if display_number <= 0:
            add_admin_log(user=current_user.username, actions='编辑开屏广告策略', client_ip=request.remote_addr,
                          results='参数错误')
            flash('展示数必须大于0')
            return redirect(url_for('manage.edit_open_strategy'))

        if protocol is None:
            protocol = ServiceProtocol()

        protocol.content = str(display_number)
        protocol.category = 1

        db.session.add(protocol)
        db.session.commit()
        add_admin_log(user=current_user.username, actions='编辑开屏广告策略', client_ip=request.remote_addr,
                      results='成功')
        flash('编辑开屏广告策略成功')
        return redirect(url_for('manage.edit_open_strategy'))
    if protocol is not None:
        form.display_number.data = int(protocol.content)
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='编辑开屏广告策略', client_ip=request.remote_addr,
                      results='失败')
    add_admin_log(user=current_user.username, actions='编辑开屏广告策略', client_ip=request.remote_addr, results='成功')
    return render_template("manage/edit_open_strategy.html", form=form)


@login_required
def avatar_app_info():
    query = AvatarVersion.query.order_by(AvatarVersion.id.desc())
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    add_admin_log(user=current_user.username, actions='分身基础版信息', client_ip=request.remote_addr, results='成功')
    return render_template('manage/avatar_info.html', data=pagination.items, pagination=pagination, page=page,
                           per_page=current_app.config['RECORDS_PER_PAGE'])


@login_required
def add_avatar_app():
    form = AddAvatarAppForm()
    if form.validate_on_submit():
        number = form.number.data
        file = request.files['upload_file']
        update_msg = form.update_msg.data

        app_version = AvatarVersion()
        file_name = secure_filename(file.filename)
        if not helper.allowed_file(file_name):
            flash('文件格式错误')
            add_admin_log(user=current_user.username, actions='上传应用',
                          client_ip=request.remote_addr, results='文件格式错误')
            return redirect(url_for('manage.add_avatar_app'))

        name = file_name.rsplit('.', 1)[0] + '_' + str(round(time.time())) + '.' + file_name.rsplit('.', 1)[1]
        app_dir = os.path.join(os.getcwd(), current_app.config['APK_TAG'], "X-Avatar")
        store_dir = os.path.join(current_app.config['APK_TAG'], "X-Avatar", name)
        if not os.path.exists(app_dir):
            os.mkdir(app_dir)
        file.save(os.path.join(app_dir, name))
        app_size = getsize(os.path.join(app_dir, name))
        apk_parser = APKParser(os.path.join(app_dir, name))
        version_code = apk_parser.get_version_code()
        version_name = apk_parser.get_version_name()
        pack_name = apk_parser.get_package()
        app_version.number = number
        app_version.version_code = version_code
        app_version.pack_name = pack_name
        app_version.version_name = version_name
        app_version.app_size = app_size
        app_version.app_dir = store_dir
        app_version.decompile_addr = ''
        app_version.update_msg = update_msg
        app_version.update_status = form.status.data
        app_version.status = 1
        db.session.add(app_version)
        db.session.commit()

        add_admin_log(user=current_user.username, actions='上传x分身应用', client_ip=request.remote_addr, results='成功')
        return redirect(url_for('manage.avatar_app_info'))
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
    return render_template("manage/add_avatar_app.html", form=form)


@login_required
def set_decompile_status():
    ava_id = request.args.get('id', type=int)
    status = request.args.get('status', type=int)
    if status == 0:
        avatar = AvatarVersion.query.filter_by(id=ava_id).first()
        if avatar is not None:
            avatar.decompile_addr = decompile(os.path.join(os.getcwd(), avatar.app_dir), avatar.number)
            avatar.status = 1
            db.session.add(avatar)
        db.session.commit()
        return jsonify({'code': 0})
    else:
        return jsonify({'code': 1})


@login_required
def release_avatar_app():
    avatar_id = request.args.get('id', type=int)
    app_version = AvatarVersion.query.filter_by(id=avatar_id).first()

    if app_version is not None:
        if app_version.status == 2:
            code = 1
            app_version.status = 1
            add_admin_log(user=current_user.username, actions='取消发布',
                          client_ip=request.remote_addr, results='成功')
        else:
            code = 0
            app_version.status = 2
            add_admin_log(user=current_user.username, actions='发布',
                          client_ip=request.remote_addr, results='成功')
        cache.delete('get_valid_avatar_version_name')
        db.session.add(app_version)
        db.session.commit()
        return jsonify(code=code)
    return jsonify(code=-2)


@login_required
def make_avatar_app():
    ava_id = request.args.get('id', type=int)
    avatar = AvatarVersion.query.filter_by(id=ava_id).first()
    form = MakeAvatarForm()
    if form.validate_on_submit():
        app_name = form.app_name.data
        we_avatar = WeAvatar()
        if avatar is not None:
            we_avatar.app_name = app_name
            we_avatar.number = avatar.number
            we_avatar.app_id = ava_id
            we_avatar.down_addr = format_apk(os.path.join(os.getcwd(), avatar.app_dir), avatar.number, app_name)
            db.session.add(we_avatar)
        db.session.commit()
        add_admin_log(user=current_user.username, actions='制作分身应用', client_ip=request.remote_addr, results='成功')
        flash('制作分身应用成功')
        return redirect(url_for('manage.avatar_app_info'))
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
    return render_template("manage/make_avatar_app.html", form=form, id=ava_id)


@login_required
def avatar_app_detail():
    app_id = request.args.get('id', type=int)
    query = WeAvatar.query.filter_by(app_id=app_id)
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    add_admin_log(user=current_user.username, actions='分身应用详情', client_ip=request.remote_addr, results='成功')
    return render_template('manage/avatar_app_detail.html', data=pagination.items, pagination=pagination, page=page,
                           per_page=current_app.config['RECORDS_PER_PAGE'], id=app_id)


@login_required
def delete_avatar():
    id = request.args.get('id', type=int)
    for we_avater in WeAvatar.query.filter_by(app_id=id):
        os.remove(we_avater.down_addr)
    WeAvatar.query.filter_by(app_id=id).delete()
    db.session.commit()
    avater = AvatarVersion.query.filter_by(id=id)
    os.remove(avater.first().app_dir)
    avater.delete()
    db.session.commit()
    add_admin_log(user=current_user.username, actions='删除分身基础版', client_ip=request.remote_addr, results='成功')
    return jsonify(code=0)


@login_required
def get_activity_share():
    form = ActivityShareForm()
    query = ShareCount.query.group_by(ShareCount.number)
    if form.validate_on_submit():
        act_id = form.act_id.data
    else:
        act_id = request.args.get('act_id')
    if act_id is not None:
        form.act_id.data = act_id
        if form.act_id.data != '':
            query = query.filter_by(number=form.act_id.data)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    add_admin_log(user=current_user.username, actions='活动邀请', client_ip=request.remote_addr, results='成功')
    return render_template('manage/activity_share.html', data=pagination.items, pagination=pagination, page=page,
                           per_page=per_page, form=form)


@login_required
def get_invite():
    act_id = request.args.get('act_id')
    form = InviteForm()
    query = ShareCount.query.join(GodinAccount, GodinAccount.godin_id == ShareCount.invite_id). \
        add_entity(GodinAccount).join(UserInfo, UserInfo.godin_id == ShareCount.invite_id).add_entity(UserInfo) \
        .filter(ShareCount.number == act_id).order_by(ShareCount.count.desc())

    if form.validate_on_submit():
        phone_num = form.phone_num.data
    else:
        phone_num = request.args.get('phone_num')

    if phone_num is not None:
        form.phone_num.data = phone_num
        if form.phone_num.data != '':
            query = query.filter(GodinAccount.phone_num.like('%' + form.phone_num.data + '%'))

    all_count = db.session.query(func.sum(ShareCount.count)).filter_by(number=act_id).first()[0]
    re_count = db.session.query(func.count(ShareCode.id)).filter_by(number=act_id).first()[0]

    dic = {}
    for q in query:
        count = db.session.query(func.count(ShareCode.id)).filter_by(number=act_id,
                                                                     invite_id=q.ShareCount.invite_id).first()[0]
        if count is not None:
            count = count
        else:
            count = 0
        dic[q.ShareCount.id] = count
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    add_admin_log(user=current_user.username, actions='邀请人', client_ip=request.remote_addr, results='成功')
    return render_template('manage/invite.html', data=pagination.items, pagination=pagination, page=page,
                           per_page=per_page, form=form, act_id=act_id, dic=dic, all_count=all_count, re_count=re_count)


@login_required
def get_share():
    act_id = request.args.get('act_id')
    invite_id = request.args.get('invite_id')
    form = ShareForm()
    query = ShareCode.query.join(GodinAccount, GodinAccount.godin_id == ShareCode.share_id).add_entity(GodinAccount). \
        join(UserInfo, UserInfo.godin_id == ShareCode.share_id).add_entity(UserInfo). \
        filter(ShareCode.number == act_id, ShareCode.invite_id == invite_id)

    if form.validate_on_submit():
        phone_num = form.phone_num.data
        start_time = form.start_time.data
        end_time = form.end_time.data

    else:
        phone_num = request.args.get('phone_num')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

    if phone_num is not None:
        form.phone_num.data = phone_num
        if form.phone_num.data != '':
            query = query.filter(GodinAccount.phone_num.like('%' + form.phone_num.data + '%'))

    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
        if form.start_time.data != '' and form.end_time.data != '':
            query = query.filter(GodinAccount.create_time.between(form.start_time.data, form.end_time.data))

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    add_admin_log(user=current_user.username, actions='被邀请人', client_ip=request.remote_addr, results='成功')
    return render_template('manage/share.html', data=pagination.items, pagination=pagination, page=page,
                           per_page=per_page, form=form, act_id=act_id, invite_id=invite_id)


@login_required
def add_key():
    form = AddKeyForm()
    if form.validate_on_submit():
        cur_id = form.channel_id.data
        count = form.count.data
        vip_time = form.vip_time.data
        content = form.content.data
        vip_gold_ad_time = form.vip_gold_ad_time.data
        vip_ad_time = form.vip_ad_time.data
        vip_ratio = form.vip_ratio.data
        business_ratio = form.business_ratio.data
        if cur_id == -1:
            flash('请选择渠道')
            add_admin_log(user=current_user.username, actions='添加key', client_ip=request.remote_addr, results='选择渠道')
            return render_template('manage/add_key.html', form=form)
        if ChannelAccount.query.filter_by(id=cur_id).first() is None:
            flash('渠道不存在')
            add_admin_log(user=current_user.username, actions='添加key', client_ip=request.remote_addr, results='渠道不存在')
            return render_template('manage/add_key.html', form=form)
        if vip_ratio > 1.0 or vip_ratio < 0:
            flash('会员分成比例: 0.00 -- 1.00')
            return render_template("manage/add_key.html", form=form)
        if business_ratio > 1.0 or business_ratio < 0:
            flash('第三方会员分成比例: 0.00 -- 1.00')
            return render_template("manage/add_key.html", form=form)

        if vip_gold_ad_time is None or vip_gold_ad_time < 0:
            flash('赠送黄金会员时间不能为空或小于0')
            return redirect(url_for('manage.add_key'))

        if vip_gold_ad_time > vip_time:
            flash('赠送黄金会员时间不能大于会员时长')
            return redirect(url_for('manage.add_key'))

        if not vip_ad_time:
            vip_ad_time = 0
        elif vip_ad_time < 0:
            flash('赠送铂金会员时间不能小于0')
            return redirect(url_for('manage.add_key'))

        if vip_ad_time > vip_time:
            flash('赠送铂金会员时间不能大于会员时长')
            return redirect(url_for('manage.add_key'))
        key_record = KeyRecord()
        key_record.channel_account_id = cur_id
        key_record.id = str(time.time() * 10000).split('.')[0]
        key_record.count = count
        key_record.vip_time = vip_time
        key_record.vip_gold_ad_time = vip_gold_ad_time
        key_record.vip_ad_time = vip_ad_time
        key_record.vip_ratio = vip_ratio
        key_record.business_ratio = business_ratio
        key_record.content = content
        key_record.oeprator = current_user.username
        db.session.add(key_record)
        # 先插入数据库防止外健关系失败
        db.session.commit()

        for i in range(count):
            key = Key()
            key.id = create_key()
            key.key_record_id = key_record.id
            db.session.add(key)
        try:
            db.session.commit()
            add_admin_log(user=current_user.username, actions='添加key', client_ip=request.remote_addr, results='成功')
            return redirect(url_for('manage.get_key_record'))
        except Exception as e:
            print(e)
            db.session.rollback()
            db.session.delete(key_record)
            db.session.commit()
            add_admin_log(user=current_user.username, actions='添加key', client_ip=request.remote_addr, results='失败')
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='添加key', client_ip=request.remote_addr,
                      results=error[0])
    return render_template('manage/add_key.html', form=form)


@login_required
def edit_key():
    var_id = request.args.get('id')
    form = EditKeyForm()
    key_record = KeyRecord.query.filter_by(id=var_id).first()
    if form.validate_on_submit() and key_record is not None:
        expire_time = form.expire_time.data
        content = form.content.data
        vip_ad_time = form.vip_ad_time.data
        if expire_time <= datetime.datetime.now().date():
            flash('有效期截止不能小于等于当前时间')
            return redirect(url_for('manage.edit_key', id=var_id))
        if vip_ad_time is None or vip_ad_time < 0:
            flash('免广告时间不能为空或小于0')
            return redirect(url_for('manage.edit_key', id=var_id))
        if vip_ad_time > key_record.vip_time:
            flash('免广告时间不能大于会员时长')
            return redirect(url_for('manage.edit_key', id=var_id))
        key_record.expire_time = expire_time
        key_record.vip_ad_time = vip_ad_time
        key_record.content = content
        db.session.add(key_record)
        db.session.commit()
        add_admin_log(user=current_user.username, actions='添加key', client_ip=request.remote_addr, results='成功')
        return redirect(url_for('manage.get_key_record'))

    if key_record is not None:
        form.expire_time.data = key_record.expire_time
        form.content.data = key_record.content
        form.vip_ad_time.data = key_record.vip_ad_time
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='添加key', client_ip=request.remote_addr,
                      results=error[0])
    return render_template('manage/edit_key.html', form=form, id=var_id)


@login_required
def export_key():
    form = ExportKeyForm()
    if form.validate_on_submit():
        count = form.count.data
        # expire_time = form.expire_time.data
        vip_time = form.vip_time.data
        content = form.content.data
        upload_file = request.files['upload_file']
        info = xlrd.open_workbook(filename=None, file_contents=upload_file.read())
        worksheet1 = info.sheet_by_name(u'Sheet1')
        num_rows = worksheet1.nrows
        vip_ad_time = form.vip_ad_time.data
        if vip_ad_time is None or vip_ad_time < 0:
            flash('免广告时间不能为空或小于0')
            return redirect(url_for('manage.export_key'))
        if vip_ad_time > vip_time:
            flash('免广告时间不能大于会员时长')
            return redirect(url_for('manage.export_key'))
        # file_data = get_data(upload_file, start_row=0)['Sheet1']
        # if expire_time <= datetime.datetime.now().date():
        #     flash('有效期截止不能小于等于当前时间')
        #     return redirect(url_for('manage.export_key'))
        key_record = KeyRecord()
        key_record.id = str(time.time() * 10000).split('.')[0]
        # key_record.expire_time = expire_time
        key_record.count = count
        key_record.vip_time = vip_time
        key_record.content = content
        key_record.vip_ad_time = vip_ad_time
        key_record.oeprator = current_user.username
        db.session.add(key_record)
        # 先插入数据库防止外健关系失败
        db.session.commit()

        print(datetime.datetime.now())
        create_time = datetime.datetime.now()
        for curr_row in range(num_rows):
            row = worksheet1.row_values(curr_row)
            if len(row) == 1:
                key = Key()
                key.id = row[0]
                key.key_record_id = key_record.id
                key.create_time = create_time
                db.session.add(key)
            else:
                flash('key不能为空')
                return redirect(url_for('manage.export_key'))
        try:
            db.session.commit()
            print(datetime.datetime.now())
            add_admin_log(user=current_user.username, actions='导入key', client_ip=request.remote_addr, results='成功')
            return redirect(url_for('manage.get_key_record'))
        except Exception as e:
            print(e)
            print(datetime.datetime.now())
            db.session.rollback()
            db.session.delete(key_record)
            add_admin_log(user=current_user.username, actions='导入key', client_ip=request.remote_addr, results='失败')
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='导入key', client_ip=request.remote_addr,
                      results=error[0])
    return render_template('manage/export_key.html', form=form)


@login_required
def get_key_record():
    form = KeyRecordForm()
    query = KeyRecord.query.join(ChannelAccount, KeyRecord.channel_account_id == ChannelAccount.id)
    data_count = db.session.query(func.count(KeyRecord.id))
    q = dict()
    if form.validate_on_submit():
        start_time = form.start_time.data
        end_time = form.end_time.data
        channel_id = form.channel_id.data
        channel_name = form.channel_name.data
        oeprator = form.oeprator.data
        content = form.content.data
    else:
        oeprator = request.args.get('oeprator')
        content = request.args.get('content')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        channel_id = request.args.get('channel_id')
        channel_name = request.args.get('channel_name')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
        if form.start_time.data != '' and form.end_time.data != '':
            q.update(start_time=str(start_time), end_time=str(end_time))
            query = query.filter(KeyRecord.create_time.between(form.start_time.data, form.end_time.data))
            data_count = data_count.filter(KeyRecord.create_time.between(form.start_time.data, form.end_time.data))
    if oeprator is not None:
        form.oeprator.data = oeprator
        if form.oeprator.data != '':
            q.update(oeprator=oeprator)
            query = query.filter(KeyRecord.oeprator.like('%' + form.oeprator.data + '%'))
            data_count = data_count.filter(KeyRecord.oeprator.like('%' + form.oeprator.data + '%'))
    if content is not None:
        form.content.data = content
        if form.content.data != '':
            q.update(content=content)
            query = query.filter(KeyRecord.content.like('%' + form.content.data + '%'))
            data_count = data_count.filter(KeyRecord.content.like('%' + form.content.data + '%'))

    if channel_id is not None:
        form.channel_id.data = channel_id
        if form.channel_id.data != '':
            q.update(channel_id=channel_id)
            query = query.filter(ChannelAccount.channel_id.like('%' + form.channel_id.data + '%'))
            data_count = data_count.filter(ChannelAccount.channel_id.like('%' + form.channel_id.data + '%'))

    if channel_name is not None:
        form.channel_name.data = channel_name
        if form.channel_name.data != '':
            q.update(channel_name=channel_name)
            query = query.filter(ChannelAccount.channel_name.like('%' + form.channel_name.data + '%'))
            data_count = data_count.filter(ChannelAccount.channel_name.like('%' + form.channel_name.data + '%'))

    dic = {}
    for record in query.all():
        count_0 = db.session.query(Key.id).filter_by(status=0, key_record_id=record.id).count()
        count_1 = db.session.query(Key.id).filter(Key.status.in_([1, 3]), Key.key_record_id == record.id).count()
        count_2 = db.session.query(Key.id).filter_by(status=2, key_record_id=record.id).count()
        dic[record.id] = [count_0, count_1, count_2]

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='key信息', client_ip=request.remote_addr,
                      results=error[0])
    add_admin_log(user=current_user.username, actions='key信息', client_ip=request.remote_addr, results='成功')

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template("manage/key_record.html", data=pagination.items, page=page, per_page=per_page,
                           pagination=pagination, form=form, dic=dic)


@login_required
def key_detail():
    var_id = request.args.get('id')
    oeprator = request.args.get('oeprator')
    form = KeyDetailForm()
    query = Key.query.filter_by(key_record_id=var_id)
    if form.validate_on_submit():
        status = form.status.data
    else:
        status = request.args.get('status', type=int)

    if status is not None:
        form.status.data = status
        if form.status.data != -1:
            query = query.filter(Key.status == form.status.data)

    dic = {}
    for key in query.filter(Key.status.in_([1, 3])):
        imei_list = []
        user_key = UserKeyRecord.query.filter_by(key_id=key.id)
        if user_key.first() is not None:
            for u_key in user_key:
                imei_list.append(u_key.imei)
            dic[key.id] = [imei_list, user_key.first().activate_time]
        else:
            dic[key.id] = ['手动失效', '手动失效']

    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='key使用详情', client_ip=request.remote_addr,
                      results=error[0])
    add_admin_log(user=current_user.username, actions='key使用详情', client_ip=request.remote_addr, results='成功')

    return render_template('manage/key_detail.html', data=pagination.items, form=form, dic=dic, id=var_id,
                           pagination=pagination, page=page, per_page=current_app.config['RECORDS_PER_PAGE'],
                           oeprator=oeprator)


@login_required
def order_key():
    form = OrderKeyForm()
    query = KeyOrder.query.join(Key, Key.id == KeyOrder.key_id).add_entity(Key)
    if form.validate_on_submit():
        status = form.status.data
        o_id = form.o_id.data
    else:
        status = request.args.get('status', type=int)
        o_id = request.args.get('o_id')

    if status is not None:
        form.status.data = status
        if form.status.data != -1:
            query = query.filter(Key.status == form.status.data)
    if o_id is not None:
        form.o_id.data = o_id
        if form.o_id.data != '':
            query = query.filter(KeyOrder.id.like('%' + form.o_id.data + '%'))

    dic = {}
    for key in query.filter(Key.status.in_([1, 3])):
        imei_list = []
        user_key = UserKeyRecord.query.filter_by(key_id=key.Key.id)
        if user_key.first() is not None:
            for u_key in user_key:
                imei_list.append(u_key.imei)
            dic[key.Key.id] = [imei_list, user_key.first().activate_time]

    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='订单key详情', client_ip=request.remote_addr,
                      results=error[0])
    add_admin_log(user=current_user.username, actions='订单key详情', client_ip=request.remote_addr, results='成功')

    return render_template('manage/order_key.html', data=pagination.items, form=form, dic=dic, id=id,
                           pagination=pagination, page=page, per_page=current_app.config['RECORDS_PER_PAGE'])


@celery.task(name='make_key_status')
def make_key_status():
    query = KeyRecord.query.filter(KeyRecord.id != '00000000000000')
    current = datetime.datetime.now()
    for record in query:
        # expire_time = record.expire_time
        vip_time = record.vip_time
        key_endTime = record.create_time + datetime.timedelta(days=vip_time)
        if key_endTime > current:
            continue

        query_key = Key.query.filter(Key.key_record_id == record.id, Key.status==1)
        for key in query_key:
            user_record = UserKeyRecord.query.filter_by(key_id=key.id)
            if user_record.first() is not None:
                for user in user_record:

                    end_vip_time = user.activate_time + datetime.timedelta(days=vip_time)
                    if current > end_vip_time:
                        flag = True
                        if record.id == '00000000000001':
                            imeis = db.session.query(UserKeyRecord.imei).filter(UserKeyRecord.key_id == key.id)
                            if imeis:
                                userInfo = db.session.query(UserInfo.godin_id).filter(UserInfo.imei.in_(imeis))
                                endtime = db.session.query(MemberWareOrder.end_time).filter(
                                    MemberWareOrder.buyer_godin_id.in_(userInfo)).order_by(
                                    MemberWareOrder.end_time.desc()).limit(1).first()
                                if endtime:
                                    if endtime < current:
                                        flag = False

                        if flag:
                            user.status = 0
                            key.status = 3
                            db.session.add(user)
                            db.session.add(key)
            # else:
            #     if expire_time < current.date():
            #         key.status = 2
            #         db.session.add(key)

    db.session.commit()
    # 更新会员到期
    current_time = datetime.datetime.now() - datetime.timedelta(minutes=10)
    BusinessMembers.query.filter(BusinessMembers.status == 1,
                                 BusinessMembers.valid_time < current_time).update(dict(status=0))
    db.session.commit()

    print('key: end')
    return True


@login_required
def channel_upload_app():
    form = ChannelUploadAppForm()
    if form.validate_on_submit():
        app_type = int(form.app_type.data)
        max_frame_code = 0
        min_frame_code = 0
        channel = None
        if app_type >= 4:
            if form.min_frame_code.data == '':
                flash('最小可兼容框架版本号不能为空')
                return redirect(url_for('manage.channel_upload_app'))
            if form.max_frame_code.data == '':
                flash('最大可兼容框架版本号不能为空')
                return redirect(url_for('manage.channel_upload_app'))
            if not form.min_frame_code.data.isdigit():
                flash('最小可兼容框架版本号必须为数字')
                return redirect(url_for('manage.channel_upload_app'))
            if not form.max_frame_code.data.isdigit():
                flash('最大可兼容框架版本号必须为数字')
                return redirect(url_for('manage.channel_upload_app'))
            max_frame_code = int(form.max_frame_code.data)
            min_frame_code = int(form.min_frame_code.data)
            if app_type == 99:
                if form.version_code.data == '' or not form.version_code.data.isdigit():
                    flash('版本号不能为空且只能是数字')
                    return redirect(url_for('manage.channel_upload_app'))

        app_name = current_app.config['APP_NAME_DICT'][app_type]
        file = request.files['upload_file']
        file_name = secure_filename(file.filename)
        if app_type == 99:
            file_name = datetime.datetime.now().strftime('%H%M%S') + file_name

        if not helper.allowed_file(file_name):
            flash('文件格式错误')
            add_admin_log(user=current_user.username, actions='上传应用',
                          client_ip=request.remote_addr, results='文件格式错误')
            return redirect(url_for('manage.channel_upload_app'))

        app_dir = os.path.join(os.getcwd(), current_app.config['APK_TAG'], 'channel-' + app_name)
        if not os.path.exists(app_dir):
            os.mkdir(app_dir)
        if app_type == 4 and form.spreader.data != 'utang':
            app_dir = os.path.join(app_dir, str(form.spreader.data))
            if not os.path.exists(app_dir):
                os.mkdir(app_dir)

        file.save(os.path.join(app_dir, file_name))
        app_size = getsize(os.path.join(app_dir, file_name))
        if app_type == 99:
            version_code = form.version_code.data
            version_name = form.wechat_version_name.data
            file_type = '.' + file_name.rsplit('.', 1)[1]
        else:
            apk_parser = APKParser(os.path.join(app_dir, file_name))
            version_code = apk_parser.get_version_code()
            version_name = apk_parser.get_version_name()
            pack_name = apk_parser.get_package()
            channel = apk_parser.get_channel()
            file_type = '.apk'

            if app_type == 12:
                pack_name += '.ad'
                app_list = AppList.query.filter_by(app_type=12).first()
                if app_list is not None:
                    app_list.app_name = current_app.config['APP_TYPE_DICT'][app_type]
                    app_list.package_name = pack_name
                    db.session.add(app_list)
                else:
                    app_list = AppList()
                    app_list.app_type = 12
                    app_list.app_name = current_app.config['APP_TYPE_DICT'][app_type]
                    app_list.package_name = pack_name
                    db.session.add(app_list)
                db.session.commit()
            if AppList.query.filter_by(package_name=pack_name, app_type=app_type).first() is None:
                flash('应用类型与上传的应用文件不符')
                os.remove(os.path.join(app_dir, file_name))
                add_admin_log(user=current_user.username, actions='删除应用',
                              client_ip=request.remote_addr, results='应用类型与上传的应用文件不符')
                return redirect(url_for('manage.channel_upload_app'))
        spm = SpreadManager.query.filter_by(channelname=form.spreader.data).first()
        if spm is None:
            flash('推广人员异常')
            os.remove(os.path.join(app_dir, file_name))
            add_admin_log(user=current_user.username, actions='删除应用',
                          client_ip=request.remote_addr, results='推广人员异常')
            return redirect(url_for('manage.channel_upload_app'))

        if app_type == 99 and form.upload_target.data == 0:  # 新增文件
            app_ver = ChannelVersion()
        else:
            app_ver = ChannelVersion.query.filter_by(app_type=app_type, version_code=version_code,
                                                     version_name=version_name, spread_id=spm.id).first()
            if app_ver is None:
                app_ver = ChannelVersion()
            else:
                app_ver.ping()

        app_ver.app_type = app_type
        app_ver.version_name = version_name
        app_ver.version_code = version_code
        app_ver.app_size = app_size
        app_ver.spread_id = spm.id
        app_ver.status = form.status.data
        if app_type == 4 and form.spreader.data != 'utang':
            rfile_name = app_name + '_' + version_name + file_type
            app_ver.app_dir = os.path.join(current_app.config['APK_TAG'], 'channel-' + app_name,
                                           str(form.spreader.data), rfile_name)
        elif app_type == 99:
            rfile_name = app_name + '_' + version_name + '_' + str(min_frame_code) \
                         + '_' + str(max_frame_code) + '_' + str(version_code) + file_type
            app_ver.app_dir = os.path.join(current_app.config['APK_TAG'], 'channel-' + app_name, rfile_name)
        else:
            rfile_name = app_name + '_' + version_name + '_' + str(version_code) + '_' + str(int(time.time())) + file_type
            app_ver.app_dir = os.path.join(current_app.config['APK_TAG'], 'channel-' + app_name, rfile_name)
        app_ver.min_version_code = min_frame_code
        app_ver.max_version_code = max_frame_code
        app_ver.update_msg = form.update_msg.data
        app_ver.spreader = SpreadManager.query.filter_by(channelname=form.spreader.data).first()
        db.session.add(app_ver)
        db.session.commit()

        if channel:
            if channel == 'TGZQ':
                cache.set('TGZQ_apk_path', app_ver.app_dir, timeout=12 * 60 * 60)
                key_value = KeyValue.query.filter_by(key="TGZQ_apk_path").limit(1).first()
                if key_value:
                    key_value.value = app_ver.app_dir
                else:
                    key_value = KeyValue(
                        key='TGZQ_apk_path',
                        value=app_ver.app_dir
                    )
                db.session.add(key_value)
                db.session.commit()
            if channel == 'VSZS':
                cache.set('VSZS_apk_path', app_ver.app_dir, timeout=12 * 60 * 60)
                key_value = KeyValue.query.filter_by(key="VSZS_apk_path").limit(1).first()
                if key_value:
                    key_value.value = app_ver.app_dir
                else:
                    key_value = KeyValue(
                        key='VSZS_apk_path',
                        value=app_ver.app_dir
                    )
                db.session.add(key_value)
                db.session.commit()

        if app_type == 99:
            cache.delete('feature_file')
        if app_type == 8:
            cache.delete('get_app_version_white')
        os.rename(os.path.join(app_dir, file_name), os.path.join(app_dir, rfile_name))
        add_admin_log(user=current_user.username, actions='上传应用', client_ip=request.remote_addr, results='成功')
        return redirect(url_for('manage.get_channel_version_info'))
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
    return render_template("manage/channel_upload_app.html", form=form)


@login_required
def get_channel_version_info():
    page = request.args.get('page', 1, type=int)
    app_list = AppList.query.all()
    pagination = ChannelVersion.query.join(AppList, AppList.app_type == ChannelVersion.app_type).order_by(
        ChannelVersion.release_time.desc()).paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'],
                                                     error_out=False)
    data = []
    for app_ver in pagination.items:
        for info in app_list:
            if app_ver.app_type == info.app_type:
                cell = dict(id=app_ver.id, app_name=info.app_name, version_name=app_ver.version_name,
                            version_code=app_ver.version_code, username=app_ver.channelspreader.username,
                            channelname=app_ver.channelspreader.channelname, release_time=app_ver.release_time,
                            app_size=app_ver.app_size, min_version_code=app_ver.min_version_code,
                            max_version_code=app_ver.max_version_code, is_released=app_ver.is_released)
                data.append(cell)
    add_admin_log(user=current_user.username, actions='查询渠道版本信息', client_ip=request.remote_addr, results='成功')
    return render_template("manage/channel_app_info.html", data=data, pagination=pagination)


@login_required
def release_channel_app():
    app_version = ChannelVersion.query.filter_by(id=request.args.get('id', type=int)).first()
    if app_version is not None:
        if app_version.is_released:
            code = 1
            app_version.is_released = False
            add_admin_log(user=current_user.username, actions='取消发布',
                          client_ip=request.remote_addr, results='成功')
        else:
            code = 0
            app_version.is_released = True
            add_admin_log(user=current_user.username, actions='发布',
                          client_ip=request.remote_addr, results='成功')
        db.session.add(app_version)
        db.session.commit()
        cache.delete('get_valid_channel_version_name')
        cache.delete('get_app_version_list')
        cache.delete('get_app_version')
        cache.delete('get_app_version_white')
        if app_version.app_type == 99:
            cache.delete('feature_file')
        return jsonify(code=code)
    return jsonify(code=-2)


@login_required
def del_channel_version():
    app_ver_id = request.args.get('id', type=int)
    app_version = ChannelVersion.query.filter_by(id=app_ver_id).first()
    if app_version is None:
        add_admin_log(user=current_user.username, actions='删除应用', client_ip=request.remote_addr, results='失败')
        return jsonify(code=1)
    target_file = os.path.join(os.getcwd(), app_version.app_dir)
    if os.path.isfile(target_file):
        os.remove(target_file)
    db.session.delete(app_version)
    db.session.commit()
    cache.delete('get_valid_channel_version_name')
    cache.delete('get_app_version_list')
    cache.delete('get_app_version')
    cache.delete('get_app_version_white')
    if app_version.app_type == 99:
        cache.delete('feature_file')
    add_admin_log(user=current_user.username, actions='删除应用', client_ip=request.remote_addr, results='成功')
    return jsonify(code=0)


@login_required
def get_key_channel():
    form = GetKeyChannelForm()
    query = KeyChannel.query
    if form.validate_on_submit():
        channel_name = form.channel_name.data
    else:
        channel_name = request.args.get('channel_name')
    if channel_name is not None:
        form.channel_name.data = channel_name
        if channel_name != '':
            query = query.filter(KeyChannel.channel_name.like('%' + form.channel_name.data + '%'))

    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(KeyChannel.create_time.desc()).paginate(
        page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    add_admin_log(user=current_user.username, actions='查询授权码渠道信息', client_ip=request.remote_addr, results='成功')

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True

    return render_template("manage/get_key_channel.html", data=pagination.items, pagination=pagination, page=page,
                           per_page=current_app.config['RECORDS_PER_PAGE'], form=form)


@login_required
def add_key_channel():
    form = KeyChannelForm()
    if form.validate_on_submit():
        channel = form.channel.data
        channel_name = form.channel_name.data
        price = int(form.price.data * 100)
        status = form.status.data
        msg = form.msg.data

        if KeyChannel.query.filter_by(channel=channel).first() is not None:
            flash('该渠道已存在')
            add_admin_log(user=current_user.username, actions='添加授权码渠道', client_ip=request.remote_addr,
                          results='添加渠道存在')
            return redirect(url_for('manage.add_key_channel'))
        channel_query = KeyChannel()
        channel_query.channel = channel
        channel_query.channel_name = channel_name
        channel_query.status = status
        channel_query.msg = msg
        channel_query.price = price
        db.session.add(channel_query)
        db.session.commit()
        add_admin_log(user=current_user.username, actions='添加授权码渠道', client_ip=request.remote_addr, results='成功')
        return redirect(url_for('manage.get_key_channel'))
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='添加授权码渠道', client_ip=request.remote_addr,
                      results=error[0])
    return render_template("manage/add_key_channel.html", form=form)


@login_required
def edit_key_channel(ch):
    form = EditKeyChannelForm()
    info = KeyChannel.query.filter_by(channel=ch).first()
    if form.validate_on_submit() and info is not None:
        channel_name = form.channel_name.data
        price = int(form.price.data * 100)
        status = form.status.data
        msg = form.msg.data

        info.channel_name = channel_name
        info.status = status
        info.msg = msg
        info.price = price

        db.session.add(info)
        db.session.commit()
        return redirect(url_for('manage.get_key_channel'))
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='编辑key渠道', client_ip=request.remote_addr, results=error[0])
    if info is not None:
        form.channel_name.data = info.channel_name
        form.price.data = info.price / 100
        form.msg.data = info.msg
        form.status.data = info.status

    if not form.errors:
        add_admin_log(user=current_user.username, actions='编辑key渠道', client_ip=request.remote_addr, results='成功')

    return render_template("manage/edit_key_channel.html", form=form, ch=ch)


@login_required
def get_key_info():
    form = GetKeyInfoForm()
    query = []
    if form.validate_on_submit():
        key_id = form.key_id.data
    else:
        key_id = request.args.get('key_id')

    if key_id is not None:
        form.key_id.data = key_id
        if form.key_id.data != '':
            query = UserKeyRecord.query.filter_by(key_id=form.key_id.data, status=1)

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
    add_admin_log(user=current_user.username, actions='查询授权码渠道信息', client_ip=request.remote_addr, results='成功')
    return render_template("manage/get_key_info.html", data=query, form=form)


@login_required
def add_key_imei():
    key_id = request.args.get('key_id')
    key = UserKeyRecord.query.filter_by(key_id=key_id, status=1).first()
    old_imei = ImeiVip.query.filter_by(imei=key.imei).first()
    form = AddKeyImeiForm()
    if form.validate_on_submit():
        imei = form.imei.data
        u_key = UserKeyRecord.query.filter_by(imei=imei, status=1).first()
        if u_key is not None:
            flash('imei已绑定其他key_id')
            return redirect(url_for('manage.get_key_info', key_id=key_id))
        if key is not None and old_imei is not None:
            user_key = UserKeyRecord()
            user_key.key_id = key_id
            user_key.activate_time = key.activate_time
            user_key.imei = imei
            user_key.status = 1
            db.session.add(user_key)

            imei_vip = ImeiVip.query.filter_by(imei=imei).first()
            if imei_vip is None:
                imei_vip = ImeiVip()
                imei_vip.imei = imei
                imei_vip.create_time = datetime.datetime.now()
                imei_vip.start_time = old_imei.start_time
                imei_vip.valid_time = old_imei.valid_time
                db.session.add(imei_vip)
            else:
                flash('imei已绑定其他key_id')
                return redirect(url_for('manage.get_key_info', key_id=key_id))
            db.session.commit()
            return redirect(url_for('manage.get_key_info', key_id=key_id))

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='授权码添加新imei', client_ip=request.remote_addr,
                      results=error[0])
    return render_template("manage/add_key_imei.html", form=form, key_id=key_id)


@login_required
def get_imei_info():
    form = GetImeiInfoForm()
    query = []
    if form.validate_on_submit():
        imei = form.imei.data
    else:
        imei = request.args.get('imei')

    if imei is not None:
        form.imei.data = imei
        if form.imei.data != '':
            query = ImeiVip.query.filter_by(imei=form.imei.data)
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
    add_admin_log(user=current_user.username, actions='查询imei vip信息', client_ip=request.remote_addr, results='成功')
    return render_template("manage/imei_vip.html", data=query, form=form)


@login_required
def add_imei_vip():
    o_imei = request.args.get('imei')
    old_imei = ImeiVip.query.filter_by(imei=o_imei).first()
    form = AddKeyImeiForm()
    if form.validate_on_submit():
        imei = form.imei.data
        imei_vip = ImeiVip.query.filter_by(imei=imei).first()
        if imei_vip is None:
            imei_vip = ImeiVip()
            imei_vip.imei = imei
            imei_vip.create_time = datetime.datetime.now()
            imei_vip.start_time = old_imei.start_time
            imei_vip.valid_time = old_imei.valid_time
            db.session.add(imei_vip)
        else:
            flash('imei已绑定其他key_id')
            return redirect(url_for('manage.get_imei_info', imei=o_imei))
        db.session.commit()
        return redirect(url_for('manage.get_imei_info', imei=o_imei))
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='imei增加免广告时间', client_ip=request.remote_addr,
                      results=error[0])
    return render_template("manage/add_imei_vip.html", form=form, imei=o_imei)


@login_required
def get_activity_info():
    form = ActivityForm()
    query = Activity.query
    if form.validate_on_submit():
        name = form.name.data
        number = form.number.data
        status = form.status.data
    else:
        name = request.args.get('name')
        number = request.args.get('number')
        status = request.args.get('status', type=int)

    if name is not None:
        form.name.data = name
        if name != '':
            query = query.filter(Activity.name.like('%' + name + '%'))
    if number is not None:
        form.number.data = number
        if number != '':
            query = query.filter(Activity.number == number)
    if status is not None:
        form.status.data = status
        if status != -1:
            query = query.filter(Activity.status == status)

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='获取活动信息', client_ip=request.remote_addr, results=error[0])
    photo_url = current_app.config['FILE_SERVER']
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    add_admin_log(user=current_user.username, actions='获取活动信息', client_ip=request.remote_addr, results='成功')
    return render_template('manage/activity.html', activity=pagination.items, pagination=pagination,
                           form=form, photo_url=photo_url)


@login_required
def activity_status():
    activity = Activity.query.filter_by(id=request.args.get('id', type=int)).first()
    if activity is not None:
        if activity.status == 0:
            code = 1
            info = Activity.query.filter_by(number=activity.number, status=1).first()
            if info is not None:
                return jsonify(code=2)
            activity.status = 1
            add_admin_log(user=current_user.username, actions='开启活动', client_ip=request.remote_addr, results='成功')
        else:
            code = 0
            activity.status = 0
            add_admin_log(user=current_user.username, actions='关闭活动', client_ip=request.remote_addr, results='成功')
        activity.update_time = datetime.datetime.now()
        db.session.add(activity)
        db.session.commit()
        return jsonify(code=code)
    return jsonify(code=-1)


@login_required
def add_activity():
    form = AddActivityForm()
    activity = Activity()
    if form.validate_on_submit():
        app_dir = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], "activity")
        file_url = os.path.join(current_app.config['PHOTO_TAG'], "activity")
        if not os.path.exists(app_dir):
            os.mkdir(app_dir)
        # 活动图片
        file = request.files['photo']
        if not file:
            flash("活动图片不能为空")
            add_admin_log(user=current_user.username, actions='添加活动', client_ip=request.remote_addr,
                          results='活动图片不能为空')
            return redirect(url_for('manage.add_activity'))
        file_name = secure_filename(file.filename)
        if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', file.filename.rsplit('.', 1)[0])):
            flash('活动图片名称不能为纯汉字')
            add_admin_log(user=current_user.username, actions='添加活动', client_ip=request.remote_addr,
                          results='活动图片名称不能为纯汉字')
            return redirect(url_for('manage.add_activity'))
        if file_name.rsplit('.', 1)[1] not in ['jpg', 'png', 'gif', 'jpeg', 'JPG', 'JPEG', 'PNG', 'GIF']:
            flash('活动图片格式错误')
            add_admin_log(user=current_user.username, actions='添加活动', client_ip=request.remote_addr,
                          results='活动图片格式错误')
            return redirect(url_for('manage.add_activity'))
        size = len(file.read())
        if size > 5120:
            flash("活动图片大小不能超过5KB")
            add_admin_log(user=current_user.username, actions='添加活动',
                          client_ip=request.remote_addr, results='活动图片大小不能超过5KB')
            return redirect(url_for('manage.add_activity'))

        # 分享图片
        addr2 = ''
        share_file = request.files['share_photo']
        if share_file:
            share_file_name = secure_filename(share_file.filename)
            if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', share_file.filename.rsplit('.', 1)[0])):
                flash('分享图片名不能为纯汉字')
                add_admin_log(user=current_user.username, actions='添加活动', client_ip=request.remote_addr,
                              results='分享图片名不能为纯汉字')
                return redirect(url_for('manage.add_activity'))
            if share_file_name.rsplit('.', 1)[1] not in ['jpg', 'png', 'gif', 'jpeg', 'JPG', 'JPEG', 'PNG', 'GIF']:
                flash('分享图片格式错误')
                add_admin_log(user=current_user.username, actions='添加活动', client_ip=request.remote_addr,
                              results='分享图片格式错误')
                return redirect(url_for('manage.add_activity'))
            size = len(share_file.read())
            if size > 20480:
                flash("分享图片大小不能超过20KB")
                add_admin_log(user=current_user.username, actions='添加活动', client_ip=request.remote_addr,
                              results='分享图片大小不能超过20KB')
                return redirect(url_for('manage.add_activity'))
            new_name = str(round(time.time() * 1000)) + '1.' + share_file_name.rsplit('.', 1)[1]
            share_img = Image.open(share_file)
            activity.share_icon = os.path.join(file_url, new_name)
            share_img.save(os.path.join(app_dir, new_name))
            addr2 = os.path.join(app_dir, new_name)

        im = Image.open(file)
        new_name = str(round(time.time() * 1000)) + '2.' + file_name.rsplit('.', 1)[1]
        activity.icon = os.path.join(file_url, new_name)
        im.save(os.path.join(app_dir, new_name))

        activity.number = form.number.data
        activity.name = form.name.data
        activity.award_period = form.award_period.data
        activity.reward = form.reward.data
        activity.link = form.link.data
        activity.content = form.content.data
        activity.start_time = form.start_time.data
        activity.end_time = form.end_time.data
        activity.share_title = form.title.data
        activity.share_description = form.description.data
        activity.share_link = form.share_link.data
        activity.create_time = datetime.datetime.now()
        activity.update_time = datetime.datetime.now()
        try:
            db.session.add(activity)
            db.session.commit()
            add_admin_log(user=current_user.username, actions='添加活动', client_ip=request.remote_addr, results='成功')
            return redirect(url_for('manage.get_activity_info'))
        except Exception as e:
            print(e)
            db.session.rollback()
            addr1 = os.path.join(app_dir, new_name)
            if len(addr1) > 4 and os.path.exists(addr1) and os.path.isfile(addr1):
                os.remove(addr1)
            if len(addr2) > 4 and os.path.exists(addr2) and os.path.isfile(addr2):
                os.remove(addr2)
            flash('操作数据错误')

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='添加活动', client_ip=request.remote_addr,
                      results=error[0])
    return render_template('manage/add_activity.html', form=form)


@login_required
def edit_activity(activity_id):
    form = EditActivityForm()
    activity = Activity.query.filter_by(id=activity_id).first()
    photo_url = current_app.config['FILE_SERVER']
    if form.validate_on_submit():
        app_dir = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], "activity")
        file_url = os.path.join(current_app.config['PHOTO_TAG'], "activity")
        if not os.path.exists(app_dir):
            os.makedirs(app_dir)
        file = request.files['photo']
        addr1 = ''
        addr2 = ''
        addr1_flag = 0
        addr2_flag = 0
        old_addr1 = activity.icon
        old_addr2 = activity.share_icon
        if file:
            size = len(file.read())
            if size > 5120:
                flash("活动图片大小不能超过5KB")
                add_admin_log(user=current_user.username, actions='编辑活动',
                              client_ip=request.remote_addr, results='活动图片大小不能超过5KB')
                return redirect(url_for('manage.edit_activity', activity_id=activity_id))
            file_name = secure_filename(file.filename)
            if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', file.filename.rsplit('.', 1)[0])):
                flash('活动图片名称不能为纯汉字')
                add_admin_log(user=current_user.username, actions='编辑活动', client_ip=request.remote_addr,
                              results='活动图片名称不能为纯汉字')
                return redirect(url_for('manage.edit_activity', activity_id=activity_id))
            if file_name.rsplit('.', 1)[1] not in ['jpg', 'png', 'gif', 'jpeg', 'JPG', 'JPEG', 'PNG', 'GIF']:
                flash('活动图片格式错误')
                add_admin_log(user=current_user.username, actions='编辑活动', client_ip=request.remote_addr,
                              results='活动图片格式错误')
                return redirect(url_for('manage.edit_activity', activity_id=activity_id))
            im = Image.open(file)
            new_name = str(round(time.time() * 1000)) + '1.' + file_name.rsplit('.', 1)[1]
            activity.icon = os.path.join(file_url, new_name)
            addr1 = os.path.join(app_dir, new_name)
            addr1_flag = 1
            im.save(addr1)
        share_file = request.files['share_photo']
        if share_file:
            size = len(share_file.read())
            if size > 20480:
                flash("头像图片大小不能超过20KB")
                add_admin_log(user=current_user.username, actions='编辑活动',
                              client_ip=request.remote_addr, results='头像图片大小不能超过20KB')
                return redirect(url_for('manage.edit_activity', activity_id=activity_id))
            share_file_name = secure_filename(share_file.filename)
            if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', share_file.filename.rsplit('.', 1)[0])):
                flash('图片名称不能为纯汉字')
                add_admin_log(user=current_user.username, actions='编辑活动', client_ip=request.remote_addr,
                              results='图片名称不能为纯汉字')
                return redirect(url_for('manage.edit_activity', activity_id=activity_id))
            if share_file_name.rsplit('.', 1)[1] not in ['jpg', 'png', 'gif', 'jpeg', 'JPG', 'JPEG', 'PNG', 'GIF']:
                flash('图片格式错误')
                add_admin_log(user=current_user.username, actions='编辑活动', client_ip=request.remote_addr,
                              results='头像图片格式错误')
                return redirect(url_for('manage.edit_activity', activity_id=activity_id))
            im = Image.open(share_file)
            new_name = str(round(time.time() * 1000)) + '2.' + share_file_name.rsplit('.', 1)[1]
            activity.share_icon = os.path.join(file_url, new_name)
            addr2 = os.path.join(app_dir, new_name)
            addr2_flag = 1
            im.save(addr2)

        activity.name = form.name.data
        activity.award_period = form.award_period.data
        activity.reward = form.reward.data
        activity.link = form.link.data
        activity.content = form.content.data
        activity.start_time = form.start_time.data
        activity.end_time = form.end_time.data
        activity.share_title = form.title.data
        activity.share_description = form.description.data
        activity.share_link = form.share_link.data
        activity.update_time = datetime.datetime.now()
        try:
            db.session.add(activity)
            db.session.commit()
            if addr1_flag and len(old_addr1) > 4 and os.path.exists(addr1) and os.path.isfile(old_addr1):
                os.remove(old_addr1)
            if addr2_flag and len(old_addr2) > 4 and os.path.exists(old_addr2) and os.path.isfile(old_addr2):
                os.remove(old_addr2)
            add_admin_log(user=current_user.username, actions='编辑活动', client_ip=request.remote_addr, results='成功')
            return redirect(url_for('manage.get_activity_info'))
        except Exception as e:
            print(e)
            db.session.rollback()
            if addr1_flag and len(addr1) > 4 and os.path.exists(addr1) and os.path.isfile(addr1):
                os.remove(addr1)
            if addr2_flag and len(addr2) > 4 and os.path.exists(addr2) and os.path.isfile(addr2):
                os.remove(addr2)
            flash('操作数据错误')

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='编辑活动', client_ip=request.remote_addr,
                      results=error[0])
    if activity is not None:
        form.name.data = activity.name
        form.award_period.data = activity.award_period
        form.reward.data = activity.reward
        form.link.data = activity.link
        form.content.data = activity.content
        form.start_time.data = activity.start_time
        form.end_time.data = activity.end_time
        form.title.data = activity.share_title
        form.description.data = activity.share_description
        form.share_link.data = activity.share_link
        add_admin_log(user=current_user.username, actions='编辑活动', client_ip=request.remote_addr,
                      results='获取活动信息成功')

    return render_template('manage/edit_activity.html', form=form, photo_url=photo_url, photo=activity.icon,
                           activity_id=activity_id, share_photo=activity.share_icon)


@login_required
def sign_activity_detail(activity_id):
    form = SignDataActivityForm()
    query = SignData.query.join(UserInfo, UserInfo.godin_id == SignData.sign_godin_id).add_entity(
        UserInfo).filter(SignData.activity_id == activity_id, SignData.number == '000003')
    if form.validate_on_submit():
        phone = form.phone.data
        sort_type = form.sort_type.data
    else:
        phone = request.args.get('phone')
        sort_type = request.args.get('sort_type')

    if phone is not None:
        form.phone.data = phone
        if phone != '':
            query = query.filter(SignData.phone.like('%' + phone + '%'))
    if sort_type is not None:
        form.sort_type.data = sort_type
        if sort_type == -1:
            query = query.order_by(SignData.last_sign_time.desc())
        if sort_type == 0:
            query = query.order_by(SignData.total_count.desc())
        if sort_type == 1:
            query = query.order_by(SignData.total_count.asc())

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='签到活动详情信息', client_ip=request.remote_addr,
                      results=error[0])
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    add_admin_log(user=current_user.username, actions='签到活动详情信息', client_ip=request.remote_addr, results='成功')
    return render_template('manage/sign_activity_detail.html', sign_data=pagination.items, pagination=pagination,
                           form=form, activity_id=activity_id)


@login_required
def sign_activity_record(activity_id, sign_godin_id):
    form = SignDataActivityForm()
    query = SignRecord.query.join(UserInfo, UserInfo.godin_id == SignRecord.sign_godin_id).add_entity(
        UserInfo).filter(SignRecord.activity_id == activity_id, SignRecord.sign_godin_id == sign_godin_id)
    if form.validate_on_submit():
        phone = form.phone.data
    else:
        phone = request.args.get('phone')

    if phone is not None:
        form.phone.data = phone
        if phone != '':
            query = query.filter(SignRecord.phone.like('%' + phone + '%'))

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='签到记录活动信息', client_ip=request.remote_addr,
                      results=error[0])
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    add_admin_log(user=current_user.username, actions='签到记录活动信息', client_ip=request.remote_addr, results='成功')
    return render_template('manage/sign_activity_record.html', sign_data=pagination.items, pagination=pagination,
                           form=form, activity_id=activity_id, sign_godin_id=sign_godin_id)


@login_required
def we_get_key_record():
    form = WeKeyRecordForm()
    query = KeyRecord.query
    data_count = db.session.query(func.count(KeyRecord.id))
    q = dict()
    if form.validate_on_submit():
        operator = form.operator.data
        start_time = form.start_time.data
        end_time = form.end_time.data
        phone_num = form.phone_num.data
        we_key_number = form.we_key_number.data
    else:
        try:
            query_data = eval(request.args.get('query'))
        except TypeError:
            query_data = dict()
        phone_num = query_data.get('phone_num')
        operator = query_data.get('operator')
        we_key_number = query_data.get('we_key_number')
        start_time = query_data.get('start_time')
        end_time = query_data.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
        if form.start_time.data != '' and form.end_time.data != '':
            q.update(start_time=str(start_time), end_time=str(end_time))
            query = query.filter(KeyRecord.create_time.between(form.start_time.data, form.end_time.data))
            data_count = data_count.filter(KeyRecord.create_time.between(form.start_time.data, form.end_time.data))
    if phone_num is not None:
        form.phone_num.data = phone_num
        if form.phone_num.data != '':
            q.update(phone_num=phone_num)
            query = query.filter(KeyRecord.phone_num.like('%' + form.phone_num.data + '%'))
            data_count = data_count.filter(KeyRecord.phone_num.like('%' + form.phone_num.data + '%'))
    if operator is not None:
        form.operator.data = operator
        if form.operator.data != '':
            q.update(operator=operator)
            query = query.filter(KeyRecord.oeprator.like('%' + form.operator.data + '%'))
            data_count = data_count.filter(KeyRecord.oeprator.like('%' + form.operator.data + '%'))
    else:
        query = query.filter(KeyRecord.oeprator.in_(['Webusiness', 'crack']))
        data_count = data_count.filter(KeyRecord.oeprator.in_(['Webusiness', 'crack']))
    if we_key_number is not None:
        form.we_key_number.data = we_key_number
        if form.we_key_number.data != '':
            q.update(we_key_number=we_key_number)
            query = query.filter(KeyRecord.we_record_id == we_key_number)
            data_count = data_count.filter(KeyRecord.we_record_id == we_key_number)

    dic = {}
    for record in query.all():
        count_0 = db.session.query(Key.id).filter_by(status=0, key_record_id=record.id).count()
        count_1 = db.session.query(Key.id).filter(Key.status.in_([1, 3]), Key.key_record_id == record.id).count()
        count_2 = db.session.query(Key.id).filter_by(status=2, key_record_id=record.id).count()
        dic[record.id] = [count_0, count_1, count_2]

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='微商key信息', client_ip=request.remote_addr,
                      results=error[0])
    add_admin_log(user=current_user.username, actions='微商key信息', client_ip=request.remote_addr, results='成功')

    # 自定义分页
    per_page = current_app.config['RECORDS_PER_PAGE']
    start_idx, end_idx, cur_page, page_num, page_size, total = helper.paging(data_count.first()[0])
    data = query.offset(start_idx).limit(per_page).all()
    page = {'page_num': page_num, 'cur_page': cur_page, 'page_size': page_size, 'total': total}

    return render_template('manage/we_key_record.html', data=data, form=form, dic=dic, query=q, page=page,
                           cur_page=cur_page, page_size=page_size)


@login_required
def we_key_detail():
    var_id = request.args.get('id')
    oeprator = request.args.get('oeprator')
    form = WeKeyDetailForm()
    query = Key.query.filter_by(key_record_id=var_id)
    if form.validate_on_submit():
        status = form.status.data
    else:
        status = request.args.get('status', type=int)

    if status is not None:
        form.status.data = status
        if form.status.data != -1:
            query = query.filter(Key.status == form.status.data)

    dic = {}
    for key in query.filter(Key.status.in_([1, 3])):
        imei_list = []
        user_key = UserKeyRecord.query.filter_by(key_id=key.id)
        if user_key.first() is not None:
            for u_key in user_key:
                imei_list.append(u_key.imei)
            dic[key.id] = [imei_list, user_key.first().activate_time]

    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='微商key使用详情', client_ip=request.remote_addr,
                      results=error[0])
    add_admin_log(user=current_user.username, actions='微商key使用详情', client_ip=request.remote_addr, results='成功')

    return render_template('manage/we_key_detail.html', data=pagination.items, form=form, dic=dic, id=var_id,
                           pagination=pagination, page=page, per_page=current_app.config['RECORDS_PER_PAGE'],
                           oeprator=oeprator)


@login_required
def get_notice_info():
    form = NoticeForm()
    query = SysNotice.query
    if form.validate_on_submit():
        oeprator = form.oeprator.data
        start_time = form.start_time.data
        end_time = form.end_time.data
    else:
        oeprator = request.args.get('oeprator')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d')

    if oeprator is not None:
        form.oeprator.data = oeprator
        if form.oeprator.data != '':
            query = query.filter(SysNotice.oeprator.like('%' + form.oeprator.data + '%'))
    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
        if form.start_time.data != '' and form.end_time.data != '':
            query = query.filter(SysNotice.create_time.between(form.start_time.data, form.end_time.data))

    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(SysNotice.flag_id.desc()).paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='消息通知', client_ip=request.remote_addr,
                      results=error[0])
    add_admin_log(user=current_user.username, actions='消息通知', client_ip=request.remote_addr, results='成功')

    return render_template('manage/notice.html', data=pagination.items, form=form,
                           pagination=pagination, page=page, per_page=current_app.config['RECORDS_PER_PAGE'])


@login_required
def add_notice():
    form = AddNoticeForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        start_time = form.start_time.data
        end_time = form.end_time.data
        remarks = form.remarks.data
        notice_type = form.notice_type.data
        time_quantum = form.time_quantum.data
        notice_user = form.notice_user.data
        icon_link = form.icon_link.data
        wx = form.wx.data
        notice = SysNotice.query.order_by(SysNotice.flag_id.desc()).first()
        if notice is None:
            flag_id = 1
        else:
            flag_id = notice.flag_id + 1
        notice = SysNotice()

        if title:
            noticecheck = SysNotice.query.filter_by(title=title).first()
            if noticecheck:
                flash('标题存在重复')
                return render_template('manage/add_notice.html', form=form)
        if end_time <= datetime.datetime.now().date():
            flash('结束时间不能小于等于当前时间')
            return render_template('manage/add_notice.html', form=form)
        if notice_type == 0:
            if content == '':
                flash("通知内容不能为空")
                add_admin_log(user=current_user.username, actions='添加通知', client_ip=request.remote_addr,
                              results='通知内容不能为空')
                return render_template('manage/add_notice.html', form=form)
            elif len(content) > 150:
                flash('通知内容长度最多为150')
                add_admin_log(user=current_user.username, actions='添加通知', client_ip=request.remote_addr,
                              results='通知内容长度最多为150')
                return render_template('manage/add_notice.html', form=form)
        if notice_type == 1:
            app_dir = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], "notice")
            file_url = os.path.join(current_app.config['PHOTO_TAG'], "notice")
            if not os.path.exists(app_dir):
                os.mkdir(app_dir)
            file = request.files['icon']
            if not file:
                flash("通知图片不能为空")
                add_admin_log(user=current_user.username, actions='添加通知', client_ip=request.remote_addr,
                              results='通知图片不能为空')
                return render_template('manage/add_notice.html', form=form)
            file_name = secure_filename(file.filename)
            if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', file.filename.rsplit('.', 1)[0])):
                flash('通知图片名称不能为纯汉字')
                add_admin_log(user=current_user.username, actions='添加通知', client_ip=request.remote_addr,
                              results='通知图片名称不能为纯汉字')
                return render_template('manage/add_notice.html', form=form)
            if file_name.rsplit('.', 1)[1] not in ['jpg', 'png', 'gif', 'jpeg', 'JPG', 'JPEG', 'PNG', 'GIF']:
                flash('通知图片格式错误')
                add_admin_log(user=current_user.username, actions='添加通知', client_ip=request.remote_addr,
                              results='通知图片格式错误')
                return render_template('manage/add_notice.html', form=form)

            if file_name.rsplit('.',1)[1] in ['gif',"GIF"]:
                new_name = str(round(time.time() * 1000)) + '3.' + file_name.rsplit('.', 1)[1]
                notice.icon = os.path.join(file_url, new_name)
                file.save(os.path.join(app_dir, new_name))
            else:
                im = Image.open(file)
                new_name = str(round(time.time() * 1000)) + '2.' + file_name.rsplit('.', 1)[1]
                notice.icon = os.path.join(file_url, new_name)
                im.save(os.path.join(app_dir, new_name))
        else:
            notice.icon = ''

        notice.id = gen_notice()
        notice.notice_type = notice_type
        notice.icon_link = icon_link
        notice.title = title
        notice.content = content
        notice.time_quantum = time_quantum
        notice.notice_user = sum(notice_user)
        notice.remarks = remarks
        notice.start_time = start_time
        notice.end_time = end_time
        notice.oeprator = current_user.username
        notice.status = 0
        notice.flag_id = flag_id
        if wx:
            notice.wx = wx
        db.session.add(notice)
        db.session.commit()

        key = 'NewGetNoticeApi_' + datetime.datetime.now().strftime('%Y-%m-%d-%H')
        cache.delete(key)

        add_admin_log(user=current_user.username, actions='添加通知', client_ip=request.remote_addr, results='成功')
        return redirect(url_for('manage.get_notice_info'))
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='添加通知', client_ip=request.remote_addr,
                      results=error[0])
    return render_template('manage/add_notice.html', form=form)


@login_required
def set_notice_status():
    id = request.args.get('id')
    notice = SysNotice.query.filter_by(id=id).first()
    if notice is not None:
        if notice.status == 0:
            code = 1
            notice.status = 1
            db.session.add(notice)
        else:
            code = 0
            notice.status = 0
            db.session.add(notice)
        db.session.commit()

        key = 'NewGetNoticeApi_' + datetime.datetime.now().strftime('%Y-%m-%d-%H')
        cache.delete(key)

        add_admin_log(user=current_user.username, actions='设置消息通知状态', client_ip=request.remote_addr,
                      results='成功')
        return jsonify(code=code)
    else:
        add_admin_log(user=current_user.username, actions='设置消息通知状态', client_ip=request.remote_addr,
                      results='失败')
        return jsonify(code=-1)


@login_required
def notice_detail():
    id = request.args.get('id')
    photo_url = current_app.config['FILE_SERVER']
    notice = SysNotice.query.filter_by(id=id).first()
    add_admin_log(user=current_user.username, actions='通知详情', client_ip=request.remote_addr, results='成功')
    return render_template('manage/notice_detail.html', notice=notice, photo_url=photo_url)


@login_required
def add_app_protocol():
    form = AppProtocolForm()
    protocol = ServiceProtocol.query.filter_by(category=2).first()
    if form.validate_on_submit():
        content = form.content.data
        if protocol is not None:
            service_protocol = ServiceProtocol.query.filter_by(category=2).first()
            service_protocol.content = content
            service_protocol.category = 2
        else:
            service_protocol = ServiceProtocol()
            service_protocol.content = content
            service_protocol.category = 2

        db.session.add(service_protocol)
        db.session.commit()
        add_admin_log(user=current_user.username, actions='添加软件服务使用协议', client_ip=request.remote_addr,
                      results='成功')
        flash('软件服务使用协议成功')
        return redirect(url_for('manage.add_app_protocol'))
    if protocol is not None:
        form.content.data = protocol.content
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='添加软件服务使用协议', client_ip=request.remote_addr,
                      results='失败')
    add_admin_log(user=current_user.username, actions='添加软件服务使用协议', client_ip=request.remote_addr, results='成功')
    return render_template("manage/app_protocol.html", form=form)


@login_required
def key_info():
    form = KeyForm()
    query = Key.query.filter(Key.status.in_([0, 1, 3]))
    if form.validate_on_submit():
        key = form.key.data
    else:
        key = request.args.get('key')
    if key is not None:
        form.key.data = key
        if form.key.data != '':
            query = query.filter_by(id=key)
    else:
        query = query.filter_by(id=1)

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='key信息', client_ip=request.remote_addr,
                      results='失败')
    add_admin_log(user=current_user.username, actions='key信息', client_ip=request.remote_addr, results='成功')
    return render_template("manage/key.html", form=form, data=query)


@login_required
def set_key_status():
    key_id = request.args.get('id')
    key = Key.query.filter_by(id=key_id).first()
    if key is not None:
        key.status = 3
        db.session.add(key)
        user_key = UserKeyRecord.query.filter_by(key_id=key_id)
        for key in user_key:
            key.status = 0
            vip = ImeiVip.query.filter_by(imei=key.imei).first()
            if vip is not None:
                vip.valid_time = datetime.datetime.now()
                db.session.add(vip)
            db.session.add(key)

        db.session.commit()
        add_admin_log(user=current_user.username, actions='设置key状态', client_ip=request.remote_addr,
                      results='成功')
        return jsonify(code=0)
    else:
        add_admin_log(user=current_user.username, actions='设置key状态', client_ip=request.remote_addr,
                      results='失败')
        return jsonify(code=-1)


@login_required
def get_act_key_statistics():
    form = ActKeyStForm()
    query = ActKeyStatistics.query.order_by(ActKeyStatistics.year.desc(), ActKeyStatistics.month.desc())
    if form.validate_on_submit():
        start_year_m = form.start_year_m.data
        end_year_m = form.end_year_m.data
        month_start = form.month_start.data
        month_end = form.month_end.data
    else:
        start_year_m = request.args.get('start_year_m', type=int)
        end_year_m = request.args.get('end_year_m', type=int)
        month_start = request.args.get('month_start', type=int)
        month_end = request.args.get('month_end', type=int)
    if start_year_m is not None and end_year_m is not None:
        if start_year_m != '' and end_year_m != '':
            query = query.filter(ActKeyStatistics.year.between(start_year_m, end_year_m))
            if month_start is not None and month_end is not None:
                if month_start != '' and month_end != '':
                    query = query.filter(ActKeyStatistics.month.between(month_start, month_end))
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='授权码激活数据', client_ip=request.remote_addr,
                      results=error[0])
    add_admin_log(user=current_user.username, actions='授权码激活数据', client_ip=request.remote_addr, results='成功')

    return render_template('manage/act_key_st.html', data=pagination.items, form=form,
                           pagination=pagination, page=page, per_page=current_app.config['RECORDS_PER_PAGE'])


@login_required
def agent_statistics():
    form = AgentStForm()
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    query = AgentStatistics.query.filter_by(year=year, month=month)
    try_all_count = db.session.query(AgentStatistics, func.sum(AgentStatistics.try_act)). \
        filter(AgentStatistics.year == year, AgentStatistics.month == month).first()
    gen_all_count = db.session.query(AgentStatistics, func.sum(AgentStatistics.general_act)). \
        filter(AgentStatistics.year == year, AgentStatistics.month == month).first()

    if form.validate_on_submit():
        name = form.name.data
    else:
        name = request.args.get('name')
    if name is not None:
        form.name.data = name
        if form.name.data != '':
            query = query.filter_by(name=form.name.data)
            try_all_count = db.session.query(AgentStatistics, func.sum(AgentStatistics.try_act)). \
                filter(AgentStatistics.year == year, AgentStatistics.month == month,
                       AgentStatistics.name == form.name.data).first()
            gen_all_count = db.session.query(AgentStatistics, func.sum(AgentStatistics.general_act)). \
                filter(AgentStatistics.year == year, AgentStatistics.month == month,
                       AgentStatistics.name == form.name.data).first()
    tac = 0
    if try_all_count[1] is not None:
        tac = try_all_count[1]
    gac = 0
    if gen_all_count[1] is not None:
        gac = gen_all_count[1]
    dict = {}
    tx_c = 0
    gx_c = 0
    for agent in query:
        if tac == 0:
            t_x = 0
        else:
            t_x = round((agent.try_act / tac) * 100, 2)
        if gac == 0:
            g_x = 0
        else:
            g_x = round((agent.general_act / gac) * 100, 2)
        dict[agent.id] = [t_x, g_x]
        tx_c += t_x
        gx_c += g_x
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=20, error_out=False)
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='代理数据', client_ip=request.remote_addr,
                      results=error[0])
    add_admin_log(user=current_user.username, actions='代理数据', client_ip=request.remote_addr, results='成功')

    return render_template('manage/agent_st.html', data=pagination.items, form=form,
                           pagination=pagination, page=page, per_page=20,
                           year=year, month=month, tac=tac, gac=gac, dict=dict, tx_c=tx_c, gx_c=gx_c)


@celery.task(name='make_act_key_statistics')
def make_act_key_statistics():
    today_now = datetime.datetime.now()
    last_time = today_now - datetime.timedelta(days=1)
    tod = str(today_now.date()).rsplit('-')
    last = str(last_time.date()).rsplit('-')
    if tod[0] != last[0]:
        tod[0] = last[0]
    if tod[1] != last[1]:
        tod[1] = last[1]
    n_tod = tod[0] + '-' + tod[1]

    # 购买渠道
    kr = KeyRecord.query.filter(KeyRecord.oeprator == 'Godin').limit(1).first()

    count = db.session.query(UserKeyRecord, func.count(UserKeyRecord.key_id.distinct())). \
        join(Key, UserKeyRecord.key_id == Key.id).filter(Key.status.in_([1, 3]),
                                                         Key.key_record_id == kr.id,
                                                         UserKeyRecord.activate_time.like(n_tod + '%')).limit(1).first()
    i = 0
    if count is not None:
        if count[1] is not None:
            i = count[1]

    # 诚招代理
    kr = KeyRecord.query.filter(KeyRecord.oeprator == 'Webusiness')
    w = 0
    for k in kr:
        count = db.session.query(UserKeyRecord, func.count(UserKeyRecord.key_id.distinct())). \
            join(Key, UserKeyRecord.key_id == Key.id).filter(Key.status.in_([1, 3]),
                                                             Key.key_record_id == k.id,
                                                             UserKeyRecord.activate_time.like(n_tod + '%')).limit(
            1).first()
        if count is not None:
            if count[1] is not None:
                w += count[1]

    # 破解赠送
    kr = KeyRecord.query.filter(KeyRecord.oeprator == 'crack')
    v = 0
    for k in kr:
        count = db.session.query(UserKeyRecord, func.count(UserKeyRecord.key_id.distinct())). \
            join(Key, UserKeyRecord.key_id == Key.id).filter(Key.status.in_([1, 3]),
                                                             Key.key_record_id == k.id,
                                                             UserKeyRecord.activate_time.like(n_tod + '%')).limit(
            1).first()
        if count is not None:
            if count[1] is not None:
                v += count[1]

    # 代理渠道
    o_list = ['crack', 'Webusiness', 'Godin']
    krr = KeyRecord.query.filter(KeyRecord.oeprator.notin_(o_list))
    agent = db.session.query(Agent.name.distinct())
    a = 0
    for k in krr:
        if not k.content.startswith('内测专用') and not k.content.startswith('内部测试专用') \
                and not k.content.startswith('上海代理') \
                and not k.content.startswith('深圳代理') and not k.content.startswith('LY001'):
            for ag in agent:
                if ag[0] in k.content:
                    count = db.session.query(UserKeyRecord, func.count(UserKeyRecord.key_id.distinct())). \
                        join(Key, UserKeyRecord.key_id == Key.id).filter(Key.status.in_([1, 3]),
                                                                         Key.key_record_id == k.id,
                                                                         UserKeyRecord.activate_time.
                                                                         like(n_tod + '%')).limit(1).first()
                    if count is not None:
                        if count[1] is not None:
                            a += count[1]
    act_stat = ActKeyStatistics.query.filter_by(year=tod[0], month=tod[1]).limit(1).first()
    if act_stat is None:
        act_stat = ActKeyStatistics()
        act_stat.channel_buy = i
        act_stat.channel_we = w
        act_stat.channel_crack = v
        act_stat.channel_agent = a
        act_stat.year = tod[0]
        act_stat.month = tod[1]
        db.session.add(act_stat)
    else:
        act_stat.channel_buy = i
        act_stat.channel_we = w
        act_stat.channel_crack = v
        act_stat.channel_agent = a
        act_stat.year = tod[0]
        act_stat.month = tod[1]
        db.session.add(act_stat)

    for oep in list(set(agent)):
        t_c = 0
        t_g = 0
        k_query = KeyRecord.query.filter(KeyRecord.content.like('%' + oep[0] + '%'), KeyRecord.vip_time < 36000)
        for k in k_query:
            count = db.session.query(UserKeyRecord, func.count(UserKeyRecord.key_id.distinct())). \
                join(Key, UserKeyRecord.key_id == Key.id).filter(Key.status.in_([1, 3]),
                                                                 Key.key_record_id == k.id,
                                                                 UserKeyRecord.activate_time.like(n_tod + '%')).limit(
                1).first()
            if count is not None:
                if count[1] is not None:
                    t_c += count[1]
        k_query = KeyRecord.query.filter(KeyRecord.content.like('%' + oep[0] + '%'), KeyRecord.vip_time >= 36000)
        for k in k_query:
            count = db.session.query(UserKeyRecord, func.count(UserKeyRecord.key_id.distinct())). \
                join(Key, UserKeyRecord.key_id == Key.id).filter(Key.status.in_([1, 3]),
                                                                 Key.key_record_id == k.id,
                                                                 UserKeyRecord.activate_time.like(n_tod + '%')).limit(
                1).first()
            if count is not None:
                if count[1] is not None:
                    t_g += count[1]
        agent_stat = AgentStatistics.query.filter_by(year=tod[0], month=tod[1], name=oep[0]).limit(1).first()
        if agent_stat is None:
            ag_stat = AgentStatistics()
            ag_stat.year = tod[0]
            ag_stat.month = tod[1]
            ag_stat.name = oep[0]
            ag_stat.try_act = t_c
            ag_stat.general_act = t_g
            db.session.add(ag_stat)
        else:
            agent_stat.year = tod[0]
            agent_stat.month = tod[1]
            agent_stat.name = oep[0]
            agent_stat.try_act = t_c
            agent_stat.general_act = t_g
            db.session.add(agent_stat)

    db.session.commit()
    print('key_statistics: end')
    return True


@login_required
def add_agent():
    form = AddAgentForm()
    if form.validate_on_submit():
        name = form.name.data
        a_info = Agent.query.filter_by(name=name).first()
        if a_info is not None:
            flash('该名称已存在')
            return redirect(url_for('manage.add_agent'))
        agent = Agent()
        agent.name = name
        db.session.add(agent)
        db.session.commit()
        add_admin_log(user=current_user.username, actions='添加管理代理人员', client_ip=request.remote_addr,
                      results='成功')
        return redirect(url_for('manage.get_agent'))
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='添加管理代理人员', client_ip=request.remote_addr,
                      results='失败')
    add_admin_log(user=current_user.username, actions='添加管理代理人员', client_ip=request.remote_addr, results='成功')
    return render_template("manage/add_agent.html", form=form)


@login_required
def get_agent():
    query = Agent.query
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    add_admin_log(user=current_user.username, actions='管理代理人员', client_ip=request.remote_addr, results='成功')

    return render_template('manage/agent.html', data=pagination.items,
                           pagination=pagination, page=page, per_page=current_app.config['RECORDS_PER_PAGE'])


@login_required
def del_agent():
    id = request.args.get('id', type=int)
    Agent.query.filter_by(id=id).delete()
    db.session.commit()
    add_admin_log(user=current_user.username, actions='删除管理代理人员', client_ip=request.remote_addr, results='成功')
    return jsonify(code=0)


@login_required
def get_app_version_check():
    form = AppVersionCheckForm()
    query = AppVersionCheck.query
    if form.validate_on_submit():
        start_time = form.start_time.data
        end_time = form.end_time.data
    else:
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d')

    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
        if form.start_time.data != '' and form.end_time.data != '':
            query = query.filter(AppVersionCheck.create_time.between(form.start_time.data, form.end_time.data))
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    add_admin_log(user=current_user.username, actions='版本检测', client_ip=request.remote_addr, results='成功')
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='版本检测', client_ip=request.remote_addr,
                      results='失败')
    return render_template('manage/appversion_check.html', data=pagination.items, form=form,
                           pagination=pagination, page=page, per_page=current_app.config['RECORDS_PER_PAGE'])


@login_required
def add_version_check():
    form = AddVersionCheckForm()
    if form.validate_on_submit():
        app_check = AppVersionCheck()
        app_check.versioncode = form.versioncode.data
        app_check.versionname = form.versionname.data
        app_check.md5 = form.md5.data
        app_check.build_time = form.build_time.data
        app_check.build_rev = form.build_rev.data
        db.session.add(app_check)
        db.session.commit()
        add_admin_log(user=current_user.username, actions='添加版本检测', client_ip=request.remote_addr,
                      results='成功')
        return redirect(url_for('manage.get_app_version_check'))
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='添加版本检测', client_ip=request.remote_addr,
                      results='失败')
    add_admin_log(user=current_user.username, actions='添加版本检测', client_ip=request.remote_addr, results='成功')
    return render_template("manage/add_app_version_check.html", form=form)


@login_required
def del_app_check():
    id = request.args.get('id', type=int)
    AppVersionCheck.query.filter_by(id=id).delete()
    db.session.commit()
    add_admin_log(user=current_user.username, actions='删除版本检测', client_ip=request.remote_addr, results='成功')
    return jsonify(code=0)


@login_required
def edit_version_check():
    id = request.args.get('id', type=int)
    form = AddVersionCheckForm()
    app_check = AppVersionCheck.query.filter_by(id=id).first()
    if form.validate_on_submit() and app_check is not None:
        app_check.versioncode = form.versioncode.data
        app_check.versionname = form.versionname.data
        app_check.md5 = form.md5.data
        app_check.build_time = form.build_time.data
        app_check.build_rev = form.build_rev.data
        db.session.add(app_check)
        db.session.commit()
        add_admin_log(user=current_user.username, actions='编辑版本检测', client_ip=request.remote_addr,
                      results='成功')
        return redirect(url_for('manage.get_app_version_check'))
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='编辑版本检测', client_ip=request.remote_addr,
                      results='失败')
    if app_check is not None:
        form.versioncode.data = app_check.versioncode
        form.versionname.data = app_check.versionname
        form.md5.data = app_check.md5
        form.build_time.data = app_check.build_time
        form.build_rev.data = app_check.build_rev
    add_admin_log(user=current_user.username, actions='编辑版本检测', client_ip=request.remote_addr, results='成功')
    return render_template("manage/edit_app_version_check.html", form=form, id=id)


@login_required
def check_key():
    form = CheckKeyForm()
    if form.validate_on_submit():
        key = form.key.data
    else:
        key = request.args.get('key')

    key_info = Key.query.filter_by(id=key).first()
    data = {}
    if key_info is not None:
        k_record = KeyRecord.query.filter_by(id=key_info.key_record_id).first()
        if k_record is not None:
            data['create_time'] = k_record.create_time
            # data['expire_time'] = k_record.expire_time
            data['vip_time'] = k_record.vip_time
            data['vip_ad_time'] = k_record.vip_ad_time
            data['count'] = k_record.count
            data['oeprator'] = k_record.oeprator
            data['content'] = k_record.content

        user_key = UserKeyRecord.query.filter_by(key_id=key)
        imei_list = []
        activate_time = ''
        status = ''
        for u_key in user_key:
            imei_list.append(u_key.imei)
            activate_time = u_key.activate_time
            status = u_key.status
        data['activate_time'] = activate_time
        data['imei'] = imei_list
        data['status'] = status

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='授权码查询', client_ip=request.remote_addr,
                      results='失败')
    add_admin_log(user=current_user.username, actions='授权码查询', client_ip=request.remote_addr, results='成功')
    return render_template("manage/check_key.html", form=form, data=data)


@celery.task(name='make_feature_data')
def make_feature_data():
    server = current_app.config['SERVER']
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    yes = yesterday.strftime('%Y%m%d')
    statistics_dir = os.path.join(os.getcwd(), current_app.config['STATISTICS_TAG'], 'Feature', yes)
    if not os.path.exists(statistics_dir):
        os.makedirs(statistics_dir)
    file_name = os.path.join(statistics_dir, server + '-' + yes + '.txt')
    if os.path.exists(file_name):
        fp = open(file_name, 'a', encoding='utf8')
    else:
        fp = open(file_name, 'w', encoding='utf8')
    all_data = redis.lrange('%s-feature' % datetime.datetime.now().date(), 0, -1)
    redis.ltrim('%s-feature' % datetime.datetime.now().date(), len(all_data), -1)
    for data in all_data:
        data = eval(str(data, encoding='utf-8'))
        fp.write('%s\n' % ({'imei': data['imei'], 'version_name': data['version_name'],
                            'version_code': data['version_code']}))
    fp.close()
    print('write file finish')
    return True


@celery.task(name='make_feature_data_five')
def make_feature_data_five():
    server = current_app.config['SERVER']
    today = datetime.datetime.now().strftime('%Y%m%d')
    statistics_dir = os.path.join(os.getcwd(), current_app.config['STATISTICS_TAG'], 'Feature', today)
    if not os.path.exists(statistics_dir):
        os.makedirs(statistics_dir)
    file_name = os.path.join(statistics_dir, server + '-' + today + '.txt')
    if os.path.exists(file_name):
        fp = open(file_name, 'a', encoding='utf8')
    else:
        fp = open(file_name, 'w', encoding='utf8')
    all_data = redis.lrange('%s-feature' % datetime.datetime.now().date(), 0, -1)
    redis.ltrim('%s-feature' % datetime.datetime.now().date(), len(all_data), -1)

    for data in all_data:
        data = eval(str(data, encoding='utf-8'))
        fp.write('%s\n' % ({'imei': data['imei'], 'version_name': data['version_name'],
                            'version_code': data['version_code']}))
    fp.close()
    print('write file finish')
    return True


@celery.task(name="make_vip_status")
def make_vip_status():
    vip_members = db.session.query(VipMembers).filter(VipMembers.status == 1,
                                                      VipMembers.valid_time < datetime.datetime.now(),
                                                      VipMembers.gold_valid_time < datetime.datetime.now()).all()
    for vip in vip_members:
        vip.status = 0
        db.session.add(vip)
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()


@login_required
def get_business_category():
    form = BusinessCategoryForm()
    query = BusinessType.query
    if form.validate_on_submit():
        name = form.name.data
    else:
        name = request.args.get('name')
    if name is not None:
        form.name.data = name
        if form.name.data != '':
            query = query.filter(BusinessType.name.like('%' + form.name.data + '%'))
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='商业会员类型', client_ip=request.remote_addr,
                      results=error[0])
    if not form.errors:
        add_admin_log(user=current_user.username, actions='商业会员类型', client_ip=request.remote_addr,
                      results='成功')
    return render_template("manage/business_category.html", form=form, data=pagination.items, pagination=pagination,
                           page=page, per_page=current_app.config['RECORDS_PER_PAGE'])


@login_required
def add_business_category():
    form = AddBusinessCategoryForm()
    if form.validate_on_submit():
        name = form.name.data
        days = form.days.data
        id_list = [r[0] for r in db.session.query(BusinessType.id.distinct())]
        if BusinessType.query.filter_by(name=name).first() is not None:
            flash('该类型已存在')
            add_admin_log(user=current_user.username, actions='添加商业会员类型', client_ip=request.remote_addr,
                          results='成功')
            return redirect(url_for('manage.add_business_category'))
        if BusinessType.query.filter_by(days=days).first() is not None:
            flash('该天数已存在')
            add_admin_log(user=current_user.username, actions='添加商业会员类型', client_ip=request.remote_addr,
                          results='成功')
            return redirect(url_for('manage.add_business_category'))
        vip_type = BusinessType()
        vip_type.name = name
        vip_type.days = days
        db.session.add(vip_type)
        if len(id_list) == 0:
            vip_type.number = 0
        else:
            v_type = BusinessType.query.filter_by(id=id_list[-1]).first()
            vip_type.number = v_type.number + 1
        db.session.commit()
        cache.delete('get_business_type')
        add_admin_log(user=current_user.username, actions='添加商业会员类型', client_ip=request.remote_addr, results='成功')
        return redirect(url_for('manage.get_business_category'))
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='添加商业会员类型', client_ip=request.remote_addr,
                      results=error[0])
    return render_template("manage/add_business_category.html", form=form)


@login_required
def add_business_protocol():
    form = VipServiceProtocolForm()
    protocol = ServiceProtocol.query.filter_by(category=4).first()
    if form.validate_on_submit():
        content = form.content.data
        if protocol is not None:
            service_protocol = ServiceProtocol.query.filter_by(category=4).first()
            service_protocol.content = content
            service_protocol.category = 4
        else:
            service_protocol = ServiceProtocol()
            service_protocol.content = content
            service_protocol.category = 4

        db.session.add(service_protocol)
        db.session.commit()

        add_admin_log(user=current_user.username, actions='添加商业会员协议', client_ip=request.remote_addr, results='成功')
        flash('添加商业会员协议成功')
        return redirect(url_for('manage.add_business_protocol'))

    if protocol is not None:
        form.content.data = protocol.content
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='添加商业会员协议', client_ip=request.remote_addr,
                      results='失败')
    add_admin_log(user=current_user.username, actions='添加商业会员协议', client_ip=request.remote_addr, results='成功')
    return render_template("manage/add_business_protocol.html", form=form)


@login_required
def get_bus_info():
    form = QueryBusinessWareForm()
    query = BusinessWare.query.order_by(BusinessWare.id.desc())
    if form.validate_on_submit():
        category = form.category.data
        status = form.status.data
    else:
        category = request.args.get('category')
        status = request.args.get('status', type=int)

    if category is not None:
        form.category.data = category
        if form.category.data != '':
            vip_type = BusinessType.query.filter_by(name=form.category.data).first()
            if vip_type is not None:
                type_number = vip_type.number
            else:
                type_number = 0
            query = query.filter_by(category=type_number)
    if status is not None:
        form.status.data = status
        if form.status.data != -1:
            query = query.filter_by(status=form.status.data)

    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    cell = {}
    for ware in pagination.items:
        vip_type = BusinessType.query.filter_by(number=ware.category).first()
        if vip_type is not None:
            cell[ware.id] = vip_type.name

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='商业会员查看产品', client_ip=request.remote_addr,
                      results=error[0])
    if not form.errors:
        add_admin_log(user=current_user.username, actions='商业会员查看产品', client_ip=request.remote_addr,
                      results='成功')
    return render_template("manage/get_business_ware_info.html", form=form, data=pagination.items,
                           pagination=pagination,
                           page=page, per_page=current_app.config['RECORDS_PER_PAGE'], data_cate=cell)


@login_required
def get_bus_details(ware_id):
    photo_url = current_app.config['FILE_SERVER']
    query = BusinessWare.query.filter_by(id=ware_id).first()
    vip = BusinessType.query.filter_by(number=query.category).first()
    category = vip.name
    # ads_cate = ''
    # for ads in query.ads_category.split(','):
    #     if ads == '0':
    #         ads_cate = ads_cate + 'banner' + '--'
    #     if ads == '1':
    #         ads_cate = ads_cate + '应用开屏广告' + '--'
    #     if ads == '2':
    #         ads_cate = ads_cate + '第三方应用广告' + '--'
    #     if ads == '3':
    #         ads_cate = ads_cate + '桌面广告' + '--'
    #     if ads == '4':
    #         ads_cate = ads_cate + '友盟推送' + '--'
    pay_price = (query.price * query.discount) / 100
    add_admin_log(user=current_user.username, actions='获取商业vip产品详情', client_ip=request.remote_addr, results='成功')
    return render_template('manage/business_ware_details.html', ware=query, photo_url=photo_url, ware_id=ware_id,
                           pay_price=pay_price, category=category)


@login_required
def set_bus_status():
    ware_id = request.args.get('id', type=str)
    status = request.args.get('status', type=int)

    if status != 0 and status != 1:
        add_admin_log(user=current_user.username, actions='设置商业产品状态', client_ip=request.remote_addr,
                      results='参数错误')
        return jsonify({'code': 1})
    else:
        try:
            BusinessWare.query.filter_by(id=ware_id).update(dict(status=status))
            if status == 0:
                bus = BusinessRecommend.query.filter_by(ware_id=ware_id)
                if bus.first() is not None:
                    picture = bus.first().picture
                    bus.delete()
                    os.remove(picture)
            db.session.commit()

            add_admin_log(user=current_user.username, actions='设置商业产品状态', client_ip=request.remote_addr,
                          results='成功')
            return jsonify({'code': 0})
        except Exception as e:
            print(e)
            db.session.rollback()
            add_admin_log(user=current_user.username, actions='设置商业产品状态', client_ip=request.remote_addr,
                          results='失败')
            return jsonify({'code': 1})


@login_required
def set_bus_priority():
    ware_id = request.args.get('id', type=str)
    priority = request.args.get('priority', type=int)
    print(ware_id)
    if priority != 0 and priority != 1:
        add_admin_log(user=current_user.username, actions='设置商业产品推荐', client_ip=request.remote_addr,
                      results='参数错误')
        return jsonify({'code': 1})
    else:
        try:
            BusinessWare.query.filter_by(id=ware_id).update(dict(priority=priority))
            db.session.commit()

            add_admin_log(user=current_user.username, actions='设置商业产品推荐', client_ip=request.remote_addr,
                          results='成功')
            return jsonify({'code': 0})
        except Exception as e:
            print(e)
            db.session.rollback()
            add_admin_log(user=current_user.username, actions='设置商业产品推荐', client_ip=request.remote_addr,
                          results='失败')
            return jsonify({'code': 1})


@login_required
def add_bus_ware():
    form = AddBusinessWareForm()
    info = BusinessWare()
    if form.validate_on_submit():
        category = form.category.data
        number = form.number.data
        name = form.name.data
        price = int(round(form.price.data, 2) * 100)
        discount = round(form.discount.data, 2)
        description = form.description.data
        status = form.status.data
        picture = request.files['picture']
        # ads_cate = form.ads_cate.data

        if discount > 1.0 or discount < 0:
            flash('折扣区间: 0.00 -- 1.00')
            add_admin_log(user=current_user.username, actions='添加商业产品', client_ip=request.remote_addr,
                          results='折扣输入错误')
            return render_template("manage/add_bus_ware.html", form=form)

        if BusinessWare.query.filter_by(id=number).first() is not None:
            flash('产品编号已经存在')
            add_admin_log(user=current_user.username, actions='添加商业产品', client_ip=request.remote_addr,
                          results='产品编号存在')
            return render_template("manage/add_bus_ware.html", form=form)

        if BusinessWare.query.filter_by(name=name).first() is not None:
            flash('产品名称已存在')
            add_admin_log(user=current_user.username, actions='添加商业产品', client_ip=request.remote_addr,
                          results='产品名称存在')
            return render_template("manage/add_bus_ware.html", form=form)
        if price * discount < 1:
            flash('会员购买价格不能小于1分')
            add_admin_log(user=current_user.username, actions='会员购买价格不能小于1分', client_ip=request.remote_addr,
                          results='会员购买价格不能小于1分')
            return render_template("manage/add_bus_ware.html", form=form)
        vip_type = BusinessType.query.filter_by(name=category).first()
        if vip_type is not None:
            type_number = vip_type.number
        else:
            type_number = 0
        if BusinessWare.query.filter_by(category=type_number, status=1).first() is not None:
            flash('该渠道的这个类型的产品已存在')
            add_admin_log(user=current_user.username, actions='添加商业产品', client_ip=request.remote_addr,
                          results='该渠道的这个类型的产品已存在')
            return render_template("manage/add_bus_ware.html", form=form)
        if picture:
            file_name = secure_filename(picture.filename)
            if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', picture.filename.rsplit('.', 1)[0])):
                flash('图片名称不能为纯汉字')
                add_admin_log(user=current_user.username, actions='添加商业产品', client_ip=request.remote_addr,
                              results='图片名称不能为纯汉字')
                return redirect(url_for('manage.add_bus_ware'))
            if file_name.rsplit('.', 1)[1] not in ['png', 'jpg']:
                flash('图片格式错误')
                add_admin_log(user=current_user.username, actions='添加商业产品', client_ip=request.remote_addr,
                              results='图片格式错误')
                return redirect(url_for('manage.add_bus_ware'))
            size = len(picture.read())
            if size > 5120:
                flash("图片大小不能超过5KB")
                add_admin_log(user=current_user.username, actions='添加商业产品',
                              client_ip=request.remote_addr, results='头像图片大小不能超过5KB')
                return redirect(url_for('manage.add_bus_ware'))

            app_dir = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], "bus_ware")
            file_url = os.path.join(current_app.config['PHOTO_TAG'], "bus_ware")
            if not os.path.exists(app_dir):
                os.mkdir(app_dir)
            im = Image.open(picture)
            info.picture = os.path.join(file_url, file_name)
            im.save(os.path.join(app_dir, file_name))
        else:
            info.picture = ''

        vip_type = BusinessType.query.filter_by(name=category).first()
        if vip_type is not None:
            info.category = vip_type.number
        info.id = number
        info.name = name
        info.price = price
        info.discount = discount
        info.description = description
        info.status = status
        info.priority = 0
        # info.ads_category = ','.join(ads_cate)
        db.session.add(info)
        db.session.commit()
        add_admin_log(user=current_user.username, actions='添加商业产品', client_ip=request.remote_addr, results='成功')
        return redirect(url_for('manage.get_bus_info'))

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='添加商业产品', client_ip=request.remote_addr, results=error[0])

    return render_template("manage/add_bus_ware.html", form=form)


@login_required
def edit_bus_ware(ware_id):
    form = EditBusinessWareForm()
    info = BusinessWare.query.filter_by(id=ware_id).first()
    if form.validate_on_submit() and info is not None:
        name = form.name.data
        price = int(round(form.price.data, 2) * 100)
        discount = round(form.discount.data, 2)
        description = form.description.data
        status = form.status.data
        picture = request.files['picture']
        # ads_cate = form.ads_cate.data

        if discount > 1.0 or discount < 0:
            flash('折扣区间: 0.00 -- 1.00')
            add_admin_log(user=current_user.username, actions='编辑商业产品', client_ip=request.remote_addr,
                          results='折扣输入错误')
            return render_template("manage/edit_bus_ware.html", form=form, ware_id=ware_id)

        if BusinessWare.query.filter(BusinessWare.name == name, BusinessWare.id != ware_id).first() is not None:
            flash('产品名称已存在')
            add_admin_log(user=current_user.username, actions='编辑商业产品', client_ip=request.remote_addr,
                          results='产品名称存在')
            return render_template("manage/edit_bus_ware.html", form=form, ware_id=ware_id)
        if price * discount < 1:
            flash('会员购买价格不能小于1分')
            add_admin_log(user=current_user.username, actions='会员购买价格不能小于1分', client_ip=request.remote_addr,
                          results='会员购买价格不能小于1分')
            return render_template("manage/edit_bus_ware.html", form=form, ware_id=ware_id)
        if picture:
            file_name = secure_filename(picture.filename)
            if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', picture.filename.rsplit('.', 1)[0])):
                flash('图片名称不能为纯汉字')
                add_admin_log(user=current_user.username, actions='编辑商业产品', client_ip=request.remote_addr,
                              results='图片名称不能为纯汉字')
                return render_template("manage/edit_bus_ware.html", form=form, ware_id=ware_id)
            if file_name.rsplit('.', 1)[1] not in ['png', 'jpg']:
                flash('图片格式错误')
                add_admin_log(user=current_user.username, actions='编辑商业产品', client_ip=request.remote_addr,
                              results='图片格式错误')
                return render_template("manage/edit_bus_ware.html", form=form, ware_id=ware_id)
            size = len(picture.read())
            if size > 5120:
                flash("图片大小不能超过5KB")
                add_admin_log(user=current_user.username, actions='编辑商业产品',
                              client_ip=request.remote_addr, results='头像图片大小不能超过5KB')
                return render_template("manage/edit_bus_ware.html", form=form, ware_id=ware_id)
            app_dir = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], "bus_ware")
            file_url = os.path.join(current_app.config['PHOTO_TAG'], "bus_ware")
            if not os.path.exists(app_dir):
                os.mkdir(app_dir)
            im = Image.open(picture)
            info.picture = os.path.join(file_url, file_name)
            im.save(os.path.join(app_dir, file_name))

        info.name = name
        info.price = price
        info.discount = discount
        info.description = description
        info.status = status
        # info.ads_category = ','.join(ads_cate)

        db.session.add(info)
        db.session.commit()
        return redirect(url_for('manage.get_bus_info'))
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='编辑商业产品', client_ip=request.remote_addr, results=error[0])
    if info is not None:
        form.name.data = info.name
        form.price.data = info.price / 100
        form.description.data = info.description
        form.discount.data = info.discount
        form.status.data = info.status
        form.picture.data = info.picture
    vip_type = BusinessType.query.filter_by(number=info.category).first()
    if vip_type is not None:
        type_name = vip_type.name
    else:
        type_name = ''
    # ads_cate = ''
    # for ads in info.ads_category.split(','):
    #     if ads == '0':
    #         ads_cate = ads_cate + 'banner' + '--'
    #     if ads == '1':
    #         ads_cate = ads_cate + '应用开屏广告' + '--'
    #     if ads == '2':
    #         ads_cate = ads_cate + '第三方应用广告' + '--'
    #     if ads == '3':
    #         ads_cate = ads_cate + '桌面广告' + '--'
    #     if ads == '4':
    #         ads_cate = ads_cate + '友盟推送' + '--'

    if not form.errors:
        add_admin_log(user=current_user.username, actions='编辑商业产品', client_ip=request.remote_addr, results='成功')

    return render_template("manage/edit_bus_ware.html", form=form, ware_id=ware_id,
                           category=type_name, picture=info.picture,
                           file_url=current_app.config['FILE_SERVER'])


def get_bus_statistics():
    form = BusStatisticsForm()
    query = BusinessWare.query.order_by(BusinessWare.id.desc())
    if form.validate_on_submit():
        category = form.category.data
        name = form.name.data
        number = form.number.data
        start_time = form.start_time.data
        end_time = form.end_time.data
    else:
        category = request.args.get('category')
        name = request.args.get('name')
        number = request.args.get('number')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

    if category is not None:
        form.category.data = category
        if form.category.data != '':
            vip_type = BusinessType.query.filter_by(name=form.category.data).first()
            if vip_type is not None:
                type_number = vip_type.number
            else:
                type_number = 0
            query = query.filter_by(category=type_number)
    if name is not None:
        form.name.data = name
        if form.name.data != '':
            query = query.filter(BusinessWare.name.like('%' + form.name.data + '%'))

    if number is not None:
        form.number.data = number
        if form.number.data != '':
            query = query.filter(BusinessWare.id == form.number.data)

    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    data = []
    ware_order = db.session.query(func.sum(BusinessWareOrder.discount_price), func.count()).filter(
        BusinessWareOrder.status == 1)
    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
        if form.end_time.data != '' and form.start_time.data != '':
            ware_order_info = ware_order.filter(BusinessWareOrder.create_time.between(form.start_time.data,
                                                                                      form.end_time.data)).first()
    else:
        ware_order_info = ware_order.first()
    total_sales = 0.0
    total_sales_count = 0
    if ware_order_info is not None:
        if ware_order_info[0] is not None:
            total_sales = round(ware_order_info[0] / 100, 2)
        if ware_order_info[1] is not None:
            total_sales_count = ware_order_info[1]

    for ware in pagination.items:
        ware_total_sales = 0.0
        ware_total_sales_count = 0
        total_sales_ratio = 0.0
        total_sales_count_ratio = 0.0

        if start_time is not None and end_time is not None:
            form.start_time.data = start_time
            form.end_time.data = end_time
            if form.end_time.data != '' and form.start_time.data != '':
                ware_info = ware_order.filter(BusinessWareOrder.ware_id == ware.id,
                                              BusinessWareOrder.create_time.between(form.start_time.data,
                                                                                    form.end_time.data)).first()
        else:
            ware_info = ware_order.filter(BusinessWareOrder.ware_id == ware.id).first()
        if ware_info is not None:
            if ware_info[0] is not None:
                ware_total_sales = round(ware_info[0] / 100, 2)
            if ware_info[1] is not None:
                ware_total_sales_count = ware_info[1]
        if total_sales != 0.0:
            total_sales_ratio = round((float(ware_total_sales) / float(total_sales)) * 100, 2)
        if total_sales_count != 0:
            total_sales_count_ratio = round((ware_total_sales_count / total_sales_count) * 100, 2)
        vip_type = BusinessType.query.filter_by(number=ware.category).first()
        if vip_type is not None:
            type_name = vip_type.name
        else:
            type_name = ''
        cell = dict(id=ware.id, category=type_name, ware_total_sales_count=ware_total_sales_count,
                    ware_total_sales=ware_total_sales, total_sales_ratio=total_sales_ratio,
                    total_sales_count_ratio=total_sales_count_ratio, name=ware.name)
        data.append(cell)

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='商业会员产品统计', client_ip=request.remote_addr,
                      results=error[0])
    if not form.errors:
        add_admin_log(user=current_user.username, actions='商业会员产品统计', client_ip=request.remote_addr,
                      results='成功')
    return render_template("manage/bus_statistics.html", form=form, data=data, pagination=pagination,
                           page=page, per_page=current_app.config['RECORDS_PER_PAGE'])


@login_required
def get_bus_members():
    form = BusMembersForm()
    query = BusinessMembers.query.join(GodinAccount, GodinAccount.godin_id == BusinessMembers.godin_id).add_entity(
        GodinAccount). \
        order_by(BusinessMembers.first_pay_time.desc())
    if form.validate_on_submit():
        phone_num = form.phone_num.data
        status = form.status.data
        start_time = form.start_time.data
        end_time = form.end_time.data
    else:
        phone_num = request.args.get('phone_num')
        status = request.args.get('status', type=int)
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    if phone_num is not None:
        form.phone_num.data = phone_num
        if form.phone_num.data != '':
            query = query.filter(GodinAccount.phone_num.like('%' + form.phone_num.data + '%'))

    if status is not None:
        form.status.data = status
        if form.status.data != -1:
            query = query.filter(BusinessMembers.status == form.status.data)
    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
        query = query.filter(BusinessMembers.first_pay_time.between(form.start_time.data, form.end_time.data))
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    zero_time = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d') + " 00:00:00",
                                           '%Y-%m-%d %H:%M:%S')
    new_count = BusinessMembers.query.filter(
        BusinessMembers.first_pay_time.between(zero_time, datetime.datetime.now())).count()
    all_orders = db.session.query(func.sum(BusinessWareOrder.discount_price)). \
        filter(BusinessWareOrder.status == 1).first()[0]
    if all_orders is None:
        all_orders = 0
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='充值商业会员用户管理', client_ip=request.remote_addr,
                      results=error[0])
    if not form.errors:
        add_admin_log(user=current_user.username, actions='充值商业会员用户管理', client_ip=request.remote_addr,
                      results='成功')

    return render_template("manage/bus_members.html", form=form, data=pagination.items, page=page, per_page=per_page,
                           pagination=pagination, new_count=new_count, all_orders=all_orders)


@login_required
def get_bus_members_details(godin_id):
    form = BusMembersDetailsForm()
    query = BusinessWareOrder.query.join(BusinessWare, BusinessWare.id == BusinessWareOrder.ware_id).add_entity(
        BusinessWare).filter(BusinessWareOrder.buyer_godin_id == godin_id, BusinessWareOrder.status == 1). \
        order_by(BusinessWareOrder.pay_time.desc())
    if form.validate_on_submit():
        pay_type = form.pay_type.data
        category = form.category.data
        status = form.status.data
        order_number = form.order_number.data
        start_time = form.start_time.data
        end_time = form.end_time.data
    else:
        pay_type = request.args.get('pay_type', type=int)
        category = request.args.get('category', type=int)
        status = request.args.get('status', type=int)
        order_number = request.args.get('order_number')
        start_time = request.args.get('start_time')
        end_time = request.args.get('start_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    if pay_type is not None:
        form.pay_type.data = pay_type
        if form.pay_type.data != -1:
            query = query.filter(BusinessWareOrder.pay_type == form.pay_type.data)
    if category is not None:
        form.category.data = category
        if form.category.data != '':
            vip_type = BusinessType.query.filter_by(name=form.category.data).first()
            if vip_type is not None:
                query = query.filter(BusinessWare.category == vip_type.number)
    if status is not None:
        form.status.data = status
        if form.status.data == 0:
            query = query.filter(BusinessWareOrder.end_time < datetime.datetime.now())
        elif form.status.data == 1:
            query = query.filter(datetime.datetime.now() > BusinessWareOrder.start_time,
                                 datetime.datetime.now() < BusinessWareOrder.end_time)
        elif form.status.data == 2:
            query = query.filter(BusinessWareOrder.start_time > datetime.datetime.now())
    if order_number is not None:
        form.order_number.data = order_number
        if form.order_number.data != '':
            query = query.filter(BusinessWareOrder.order_number.like('%' + form.order_number.data + '%'))

    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
        query = query.filter(BusinessWareOrder.create_time.between(form.start_time.data, form.end_time.data))

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    buyer = GodinAccount.query.filter_by(godin_id=godin_id).first()
    buy_count = BusinessWareOrder.query.filter_by(buyer_godin_id=godin_id, status=1).count()
    buy_price = db.session.query(func.sum(BusinessWareOrder.discount_price)). \
        filter_by(buyer_godin_id=godin_id, status=1).first()[0]
    if buy_price is None:
        buy_price = 0
    cell = {}
    for query in pagination.items:
        vip_type = BusinessType.query.filter_by(number=query.BusinessWare.category).first()
        if vip_type is not None:
            cell[query.BusinessWare.id] = vip_type.name
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='商业充值用户个人详情管理', client_ip=request.remote_addr,
                      results=error[0])
    if not form.errors:
        add_admin_log(user=current_user.username, actions='商业充值用户个人详情管理', client_ip=request.remote_addr,
                      results='成功')
    return render_template("manage/bus_members_details.html", form=form, data=pagination.items, page=page,
                           per_page=per_page, pagination=pagination, godin_id=godin_id, buyer=buyer,
                           buy_count=buy_count, buy_price=buy_price, phone_num=buyer.phone_num,
                           create_time=buyer.create_time, now=datetime.datetime.now(), cate_name=cell)


@login_required
def bus_pay_statistics():
    form = BusPayStatisticsForm()
    query = BusinessPayMonthStatistics.query
    today_now = datetime.date.today()

    if form.validate_on_submit():
        statistics_way = form.statistics_way.data
        year_start_m = form.start_year_m.data
        year_end_m = form.end_year_m.data
        month_start = form.month_start.data
        month_end = form.month_end.data
        year_start_w = form.start_year_w.data
        year_end_w = form.end_year_w.data
        week_start = form.week_start.data
        week_end = form.week_end.data
        day_start = form.day_start.data
        day_end = form.day_end.data
    else:
        statistics_way = request.args.get('statistics_way', 1, type=int)
        year_start_m = request.args.get('year_start_m', type=int)
        year_end_m = request.args.get('year_end_m', type=int)
        month_start = request.args.get('month_start', type=int)
        month_end = request.args.get('month_end', type=int)
        year_start_w = request.args.get('year_start_w', type=int)
        year_end_w = request.args.get('year_end_w', type=int)
        week_start = request.args.get('week_start', type=int)
        week_end = request.args.get('week_end', type=int)
        day_start = request.args.get('day_start')
        day_end = request.args.get('day_end')
        if day_start is not None and day_end is not None:
            if day_start != '0' and day_end != '0':
                day_start = datetime.datetime.strptime(day_start, '%Y-%m-%d').date()
                day_end = datetime.datetime.strptime(day_end, '%Y-%m-%d').date()

    if statistics_way == 1:
        if year_start_m is not None and year_end_m is not None:
            form.statistics_way.data = statistics_way
            form.start_year_m.data = year_start_m
            form.end_year_m.data = year_end_m
            form.month_start.data = month_start
            form.month_end.data = month_end
            if form.start_year_m.data == form.end_year_m.data:
                query = BusinessPayMonthStatistics.query.filter_by(year=form.start_year_m.data). \
                    filter(BusinessPayMonthStatistics.month.between(form.month_start.data, form.month_end.data)). \
                    order_by(BusinessPayMonthStatistics.month.desc())
            else:
                query = query.filter(or_(and_(BusinessPayMonthStatistics.month.between(form.month_start.data, 12),
                                              BusinessPayMonthStatistics.year == form.start_year_m.data),
                                         and_(BusinessPayMonthStatistics.year < form.end_year_m.data,
                                              BusinessPayMonthStatistics.year > form.start_year_m.data),
                                         and_(BusinessPayMonthStatistics.year == form.end_year_m.data,
                                              BusinessPayMonthStatistics.month.between(1, form.month_end.data)))). \
                    order_by(BusinessPayMonthStatistics.year.desc(), BusinessPayMonthStatistics.month.desc())
        else:
            year_now = today_now.year
            month_now = today_now.month
            query = BusinessPayMonthStatistics.query
            year_last = int(year_now) - 1
            month_last = 12 + (month_now - 12)
            query = query.filter(or_(and_(BusinessPayMonthStatistics.month.between(month_last, 12),
                                          BusinessPayMonthStatistics.year == year_last),
                                     and_(BusinessPayMonthStatistics.year == year_now,
                                          BusinessPayMonthStatistics.month.between(1, month_now - 1)))). \
                order_by(BusinessPayMonthStatistics.year.desc(), BusinessPayMonthStatistics.month.desc())
    elif statistics_way == 2:
        form.statistics_way.data = statistics_way
        form.start_year_w.data = year_start_w
        form.end_year_w.data = year_end_w
        form.week_start.data = week_start
        form.week_end.data = week_end
        if form.end_year_w.data == form.start_year_w.data:
            query = BusinessPayWeekStatistics.query.filter_by(year=form.start_year_w.data). \
                filter(BusinessPayWeekStatistics.week.between(form.week_start.data, form.week_end.data + 1)). \
                order_by(BusinessPayWeekStatistics.week.desc())
        else:
            query = BusinessPayWeekStatistics.query.filter(or_(and_(
                BusinessPayWeekStatistics.year == form.start_year_w.data,
                BusinessPayWeekStatistics.week.between(form.week_start.data, 52)),
                and_(BusinessPayWeekStatistics.year < form.end_year_w.data,
                     BusinessPayWeekStatistics.year > form.start_year_w.data),
                and_(BusinessPayWeekStatistics.year == form.end_year_w.data,
                     BusinessPayWeekStatistics.week.between(1, form.week_end.data)))). \
                order_by(BusinessPayWeekStatistics.year.desc(), BusinessPayWeekStatistics.week.desc())

    elif statistics_way == 3:
        form.statistics_way.data = statistics_way
        form.day_start.data = day_start
        form.day_end.data = day_end
        if form.day_start.data is not None and form.day_end.data is not None:
            query = BusinessPayDayStatistics.query.filter(BusinessPayDayStatistics.date.between(
                form.day_start.data, form.day_end.data)).order_by(BusinessPayDayStatistics.date.desc())
        else:
            last_time = today_now - datetime.timedelta(days=30)
            query = BusinessPayDayStatistics.query.filter(BusinessPayDayStatistics.date.between(last_time, today_now)). \
                order_by(BusinessPayDayStatistics.date.desc())
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='商业会员续费统计', client_ip=request.remote_addr,
                      results='失败')
    add_admin_log(user=current_user.username, actions='商业会员续费统计', client_ip=request.remote_addr, results='成功')
    if statistics_way is None:
        statistics_way = 1
    return render_template("manage/bus_pay_statistics.html", form=form, data=pagination.items,
                           page=page, per_page=per_page, pagination=pagination, statistics_way=statistics_way)


@login_required
def add_friends():
    form = AddFriendsForm()
    if form.validate_on_submit():
        one = OnePool.query.all()
        if len(one) >= 1:
            flash('清空数据后再添加')
            return redirect(url_for('manage.add_friends'))

        add_user = request.files['add_user']
        add_info = xlrd.open_workbook(filename=None, file_contents=add_user.read())
        worksheet1 = add_info.sheet_by_name(u'Sheet1')
        num_rows = worksheet1.nrows
        for curr_row in range(num_rows):
            row = worksheet1.row_values(curr_row)
            if len(row) == 1:
                one_pool = OnePool()
                one_pool.we_id = row[0]
                db.session.add(one_pool)
            else:
                flash('添加者微信id不能为空')
                return redirect(url_for('manage.add_friends'))

        by_add_user = request.files['by_add_user']
        by_info = xlrd.open_workbook(filename=None, file_contents=by_add_user.read())
        worksheet1 = by_info.sheet_by_name(u'Sheet1')
        num_rows = worksheet1.nrows
        by_user = []
        for curr_row in range(num_rows):
            row = worksheet1.row_values(curr_row)
            if len(row) == 1:
                by_user.append(row[0])
                redis.set('by_add_user', json.dumps(by_user))
            else:
                flash('被添加者微信id不能为空')
                return redirect(url_for('manage.add_friends'))

        capita_add = form.capita_add.data
        add_count = form.add_count.data
        if add_count > num_rows:
            flash('每日添加数量不能超过添加者')
            return redirect(url_for('manage.add_friends'))
        count = {'capita_add': capita_add, 'add_count': add_count}
        redis.set('friend_count', json.dumps(count))
        try:
            db.session.commit()
            flash('添加成功')
            add_admin_log(user=current_user.username, actions='智能加好友', client_ip=request.remote_addr, results='成功')
            return redirect(url_for('manage.add_friends'))
        except Exception as e:
            print(e)
            db.session.rollback()
            redis.delete('friend_count')
            redis.delete('by_add_user')
            add_admin_log(user=current_user.username, actions='智能加好友', client_ip=request.remote_addr, results='失败')
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='智能加好友', client_ip=request.remote_addr,
                      results=error[0])
    return render_template('manage/add_friends.html', form=form)


@login_required
def del_friends():
    OnePool.query.delete()
    redis.delete('friend_count')
    redis.delete('by_add_user')
    add_admin_log(user=current_user.username, actions='删除智能加好友', client_ip=request.remote_addr, results='成功')
    return jsonify(code=1)


@login_required
def free_vip_days():
    form = FreeVipDaysForm()
    days = redis.get('free_vip_days')
    if form.validate_on_submit():
        days = form.days.data
        if days is None:
            flash('免费会员天数不能为空')
            return redirect(url_for('manage.free_vip_days'))
        redis.set('free_vip_days', days)
        flash('添加成功')
        return redirect(url_for('manage.free_vip_days'))
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='免费会员天数', client_ip=request.remote_addr,
                      results=error[0])
    if days is not None:
        form.days.data = str(days, encoding=('utf-8'))
    return render_template('manage/free_vip_days.html', form=form)


@login_required
def bus_give_stat():
    form = FreeVipForm()
    query = BusinessGiveStatistics.query.order_by(BusinessGiveStatistics.create_time.desc())
    if form.validate_on_submit():
        phone_num = form.phone_num.data
        start_time = form.start_time.data
        end_time = form.end_time.data
    else:
        phone_num = request.args.get('phone_num')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    if phone_num is not None:
        form.phone_num.data = phone_num
        if form.phone_num.data != '':
            query = query.filter(BusinessGiveStatistics.phone_num.like('%' + form.phone_num.data + '%'))

    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
        query = query.filter(BusinessGiveStatistics.create_time.between(form.start_time.data, form.end_time.data))
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='免费会员数据', client_ip=request.remote_addr,
                      results=error[0])
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    add_admin_log(user=current_user.username, actions='免费会员数据', client_ip=request.remote_addr, results='成功')

    return render_template('manage/bus_give_stat.html', data=pagination.items, form=form,
                           pagination=pagination, page=page, per_page=current_app.config['RECORDS_PER_PAGE'])


@login_required
def bus_recommend():
    form = BusRecommendForm()
    bus = BusinessRecommend.query.first()
    if form.validate_on_submit():
        tip_time = form.tip_time.data
        ware_id = form.ware_id.data
        bus_ware = BusinessWare.query.filter_by(id=ware_id, status=1).first()
        if bus_ware is None:
            flash('商品id无效')
            return render_template('manage/bus_recommend.html', form=form)
        app_dir = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], "bus_recommend")
        file_url = os.path.join(current_app.config['PHOTO_TAG'], "bus_recommend")
        if not os.path.exists(app_dir):
            os.mkdir(app_dir)
        file = request.files['picture']
        file_name = secure_filename(file.filename)
        if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', file.filename.rsplit('.', 1)[0])):
            flash('通知图片名称不能为纯汉字')
            add_admin_log(user=current_user.username, actions='推荐会员', client_ip=request.remote_addr,
                          results='通知图片名称不能为纯汉字')
            return render_template('manage/add_notice.html', form=form)
        im = Image.open(file)
        new_name = str(round(time.time() * 1000)) + '2.' + file_name.rsplit('.', 1)[1]
        picture_url = os.path.join(file_url, new_name)
        im.save(os.path.join(app_dir, new_name))

        if bus is None:
            bus = BusinessRecommend()
            bus.ware_id = ware_id
            bus.tip_time = tip_time
            bus.picture = picture_url
            db.session.add(bus)
        else:
            bus.ware_id = ware_id
            bus.tip_time = tip_time
            bus.picture = picture_url
            db.session.add(bus)

        db.session.commit()
        flash('配置成功')
        add_admin_log(user=current_user.username, actions='推荐会员', client_ip=request.remote_addr, results='成功')
        return redirect(url_for('manage.bus_recommend'))

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='推荐会员', client_ip=request.remote_addr,
                      results=error[0])

    if bus is not None:
        form.ware_id.data = bus.ware_id
        form.tip_time.data = bus.tip_time
        bus_id = bus.id
    else:
        bus_id = 0
    return render_template('manage/bus_recommend.html', form=form, bus_id=bus_id)


@login_required
def del_bus_recommend():
    bus_id = request.args.get('bus_id')
    bus = BusinessRecommend.query.filter_by(id=bus_id)
    if bus.first() is not None:
        picture = bus.first().picture
        bus.delete()
        db.session.commit()
        os.remove(picture)
    add_admin_log(user=current_user.username, actions='清空推荐会员', client_ip=request.remote_addr, results='成功')
    return redirect(url_for('manage.bus_recommend'))


@login_required
def second_add():
    form = SecondDaysForm()
    s_days = redis.get('second_days')
    s_count = redis.get('second_count')
    if form.validate_on_submit():
        days = form.days.data
        count = form.count.data
        if days is None:
            flash('秒通过添加天数设置不能为空')
            return redirect(url_for('manage.second_add'))
        if count is None:
            flash('秒通过添加人数设置不能为空')
            return redirect(url_for('manage.second_add'))
        if count > 10:
            flash('人数设置需小于10')
            return redirect(url_for('manage.second_add'))
        redis.set('second_days', days)
        redis.set('second_count', count)
        flash('设置成功')
    if s_days is None:
        redis.set('second_days', 0)
    else:
        form.days.data = str(s_days, encoding=('utf-8'))
    if s_count is None:
        redis.set('second_count', 0)
    else:
        form.count.data = str(s_count, encoding=('utf-8'))

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='数据源配置', client_ip=request.remote_addr,
                      results=error[0])
    add_admin_log(user=current_user.username, actions='数据源配置', client_ip=request.remote_addr, results='成功')
    return render_template('manage/second_add.html', form=form)

# 过期
# @login_required
# def add_business_assistant():
#     form = BusAssistantForm()
#     bus_assistant = redis.get('bus_assistant')
#     if form.validate_on_submit():
#         we_id = form.we_id.data
#         we_customer_service = form.we_customer_service.data
#         we_public = form.we_public.data
#         link = form.link.data
#         redis.set('bus_assistant', {'we_id': we_id, 'we_customer_service': we_customer_service, 'we_public': we_public, 'link': link})
#         flash('添加成功')
#         return redirect(url_for('manage.add_business_assistant'))
#     if bus_assistant is not None:
#         bus_assistant = eval(str(bus_assistant, encoding='utf-8'))
#         form.we_id.data = bus_assistant.get('we_id', '')
#         form.we_customer_service.data = bus_assistant.get('we_customer_service', '')
#         form.we_public.data = bus_assistant.get('we_public', '')
#         form.link.data = bus_assistant.get('link', '')
#
#     flag = False
#     for field, error in form.errors.items():
#         if not flag:
#             flash(error[0])
#             flag = True
#         add_admin_log(user=current_user.username, actions='微商助理', client_ip=request.remote_addr,
#                       results=error[0])
#     add_admin_log(user=current_user.username, actions='微商助理', client_ip=request.remote_addr, results='成功')
#     return render_template('manage/bus_assistant.html', form=form)


@login_required
def business_assistant():
    nickname = request.args.get("nickname", None)
    page = request.args.get('page', 1, type=int)
    form = BusAssistantForm()
    if nickname:
        form.nickname.data = nickname
        pagination = VSZL_Service.query.filter(VSZL_Service.nickname.like('%{0}%'.format(nickname))).paginate(
            page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
        data = pagination.items

        return render_template('manage/bus_assistant.html', form=form, all_user=data, nickname=nickname, pagination=pagination)

    if form.validate_on_submit():
        nickname = form.nickname.data.strip()
        pagination = VSZL_Service.query.filter(VSZL_Service.nickname.like('%{0}%'.format(nickname))).paginate(
                                page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
        data = pagination.items
        if pagination.total == 0:
            flash("无查询结果")
        return render_template('manage/bus_assistant.html', form=form, all_user=data, nickname=nickname, pagination=pagination)

    if form.is_submitted():
        flash("无查询结果")
        return render_template('manage/bus_assistant.html', form=form, pagination=None)

    for field, error in form.errors.items():
        flash(error[0])

    pagination = VSZL_Service.query.paginate(
        page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    data = pagination.items
    return render_template('manage/bus_assistant.html', form=form, all_user=data, pagination=pagination)


@login_required
def delete_assistant():
    nickname = request.args.get("nickname", None)
    wx = request.args.get("wx", None)
    all_customer = VSZL_Customer_Service.query.filter_by(service_wx=wx).all()
    current_assistant = VSZL_Service.query.filter_by(service_wx=wx).first()
    for customer in all_customer:
        db.session.delete(customer)
    db.session.delete(current_assistant)
    db.session.commit()
    # 删除单条数据之后继续返回到查询页面
    return redirect(url_for('manage.business_assistant', nickname=nickname))


@login_required
def get_assistant_detail():

    page = request.args.get('page', 1, type=int)
    wx = request.args.get('wx')
    pagination = VSZL_Customer_Service.query.filter_by(service_wx=wx).paginate(
                                page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    data = pagination.items
    return render_template("manage/bus_customer.html", all_customer=data, pagination=pagination, wx=wx)


@login_required
def add_assistant():
    form = AddAssistantForm()
    if form.validate_on_submit():
        # 校验 person_num_limit是否为正整数
        service_wx = form.service_wx.data.strip()
        nickname = form.nickname.data.strip()
        person_num_limit = form.person_num_limit.data
        if not person_num_limit.strip().isdigit() or person_num_limit.strip() == "0":
            flash("添加数量必须为正整数")
            return render_template('manage/bus_add_assistant.html', form=form)

        data = VSZL_Service.query.filter_by(service_wx=service_wx).first()
        if data:  # 先判断当前客服微信是否已被添加
            flash("当前客服微信号已被添加")
            return render_template('manage/bus_add_assistant.html', form=form)

        vszl_service = VSZL_Service()
        vszl_service.service_wx = service_wx
        vszl_service.nickname = nickname
        vszl_service.person_num_limit = person_num_limit
        db.session.add(vszl_service)
        db.session.commit()
        flash("添加成功")
        return redirect(url_for("manage.business_assistant", nickname=nickname))
    for field, error in form.errors.items():
        flash(error[0])
        break

    return render_template('manage/bus_add_assistant.html', form=form)


@login_required
def set_gzh():
    form = SetGZHForm()
    bus_gzh = redis.get('bus_gzh')
    if form.validate_on_submit():
        we_public = form.we_public.data
        link = form.link.data
        redis.set('bus_gzh', {'we_public': we_public, 'link': link})
        flash('添加成功')
        return redirect(url_for('manage.set_gzh'))
    if bus_gzh is not None:
        bus_gzh = eval(str(bus_gzh, encoding='utf-8'))
        form.we_public.data = bus_gzh.get('we_public', '')
        form.link.data = bus_gzh.get('link', '')

    for field, error in form.errors.items():
        flash(error[0])
        break

    return render_template('manage/bus_set_gzh.html', form=form)


@login_required
def add_link():
    form = AddLinkForm()
    bus_link = redis.get('bus_link')
    if form.validate_on_submit():
        link = form.link.data
        redis.set('bus_link', link)
        flash('添加成功')
        return redirect(url_for('manage.add_link'))
    if bus_link is not None:
        bus_link = str(bus_link, encoding='utf-8')
        form.link.data = bus_link

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='微课堂', client_ip=request.remote_addr,
                      results=error[0])
    add_admin_log(user=current_user.username, actions='微课堂', client_ip=request.remote_addr, results='成功')
    return render_template('manage/bus_link.html', form=form)


@login_required
def free_experience_days():
    form = FreeExperienceForm()
    if request.method == "GET":
        free_days = cache.get('free_experience_days')
        if free_days:
            form.days.data = int(free_days)
            return render_template("manage/free_experience_days.html", form=form)
        else:
            record = db.session.query(KeyValue).filter_by(key="free_experience_days").limit(1).first()
            if not record:
                key_value = KeyValue(
                    key="free_experience_days"
                )
                db.session.add(key_value)
                db.session.commit()
            else:
                form.days.data = record.value
                cache.set('free_experience_days', record.value, timeout=12 * 60 * 60)

    if form.validate_on_submit():
        days = form.days.data.strip()
        if not days.isdigit() or days == "0":
            flash("添加数量必须为正整数")
            return render_template('manage/free_experience_days.html', form=form)
        record = db.session.query(KeyValue).filter_by(key="free_experience_days").limit(1).first()
        record.value = days
        db.session.add(record)
        db.session.commit()
        cache.set('free_experience_days', days, timeout=12 * 60 * 60)
        flash("添加成功")
    for field, error in form.errors.items():
        flash(error[0])
        break
    return render_template("manage/free_experience_days.html", form=form)


# 渠道
@login_required
def add_account():
    form = ChannelAccountForm()
    if form.validate_on_submit():
        channel_name = form.channel_name.data.strip()
        account = form.account.data.strip()
        channel_manager = form.channel_manager.data.strip()
        content = form.content.data.strip()
        if ChannelAccount.query.filter_by(channel_name=channel_name).first():
            flash('渠道名称已经存在')
            return redirect(url_for('manage.add_account'))
        if ChannelAccount.query.filter_by(account_id=account).first():
            flash('账号已经存在')
            return redirect(url_for('manage.add_account'))
        # 生成随机渠道账号ID
        # 生成两位随机字母(两位)
        str_s = 'qd'
        # for i in range(2):
        #     s = chr(random.randrange(97, 123))
        #     str_s += s
        # 生成四位随机数字
        channel_account = ChannelAccount.query.order_by(ChannelAccount.create_time.desc()).limit(1).first()
        n = int(channel_account.channel_id[2:]) + 1
        # value = redis.get('wsxzsqdzh')
        # if value is None:
        #     redis.set('wsxzsqdzh', 1)
        #     num = 1
        # else:
        #     num = int(value) + 1

        # str_n = '%04d' % random.randint(0, 9999)
        str_n = '%04d' % n
        channel_id = str_s + str_n
        channel_account = ChannelAccount()
        channel_account.channel_id = channel_id
        channel_account.channel_name = channel_name
        channel_account.password = '000000'
        channel_account.account_id = account
        channel_account.channel_manager = channel_manager
        channel_account.content = content
        channel_account.operator = current_user.username  # current_user.username 代表当前登录用户

        db.session.add(channel_account)
        db.session.commit()
        return redirect(url_for('manage.get_account_info'))
        add_admin_log(user=current_user.username, actions='添加渠道账户', client_ip=request.remote_addr, results='成功')

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='添加渠道账户', client_ip=request.remote_addr,
                      results=error[0])
    return render_template('manage/add_account.html', form=form)


@login_required
def get_account_info():
    form = GetAccountInfoForm()
    query = ChannelAccount.query

    if form.validate_on_submit():
        channel_name = form.channel_name.data
        channel_manager = form.channel_manager.data
    else:
        channel_name = request.args.get('channel_name')
        channel_manager = request.args.get('channel_manager')

    if channel_name is not None:
        form.channel_name.data = channel_name
        if form.channel_name.data != '':
            query = query.filter(
                ChannelAccount.channel_name.like('%' + form.channel_name.data + '%'))

    if channel_manager is not None:
        form.channel_manager.data = channel_manager
        if form.channel_manager.data != '':
            query = query.filter(
                ChannelAccount.channel_manager.like('%' + form.channel_manager.data + '%'))

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
    add_admin_log(user=current_user.username, actions='查询渠道账号信息', client_ip=request.remote_addr, results='成功')

    return render_template("manage/get_account_info.html", data=pagination.items, page=page, per_page=per_page,
                           pagination=pagination, form=form)


@login_required
def edit_channel_account(cur_id):
    # cur_id = request.args.get('cur_id')
    form = EditChannelAccountForm()
    channel_account = ChannelAccount.query.filter_by(id=cur_id).first()
    if form.validate_on_submit():
        channel_manager = form.channel_manager.data
        content = form.content.data
        channel_account.operator = current_user.username
        channel_account.channel_manager = channel_manager
        channel_account.content = content
        db.session.add(channel_account)
        db.session.commit()
        add_admin_log(user=current_user.username, actions='修改channel_account', client_ip=request.remote_addr, results='成功')
        return redirect(url_for('manage.get_account_info'))
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='修改channel_account', client_ip=request.remote_addr,
                      results=error[0])
    if channel_account is not None:
        form.channel_manager.data = channel_account.channel_manager
        form.content.data = channel_account.content
    return render_template("manage/edit_channel_account.html", channel_name=channel_account.channel_name,
                            cur_id=cur_id, account_id=channel_account.account_id, form=form)


# 获取渠道数据信息
@login_required
def get_channel_data():
    form = ChannelDataForm()
    query = Wallet.query.join(ChannelAccount, Wallet.channel_account_id == ChannelAccount.id)

    if form.validate_on_submit():
        channel_id = form.channel_id.data
        channel_name = form.channel_name.data
    else:
        channel_name = request.args.get('channel_name')
        channel_id = request.args.get('channel_id')

    if channel_name is not None:
        form.channel_name.data = channel_name
        if form.channel_name.data != '':
            query = query.filter(
                ChannelAccount.channel_name.like('%' + form.channel_name.data + '%'))

    if channel_id is not None:
        form.channel_id.data = channel_id
        if form.channel_id.data != '':
            query = query.filter(
                ChannelAccount.channel_id.like('%' + form.channel_id.data + '%'))
    dic = {}
    for wallet in query.all():
        count_1 = 0
        count_2 = 0
        for record in KeyRecord.query.filter_by(channel_account_id=wallet.channel_account_id).all():
            count_1 += db.session.query(Key.id).filter_by(key_record_id=record.id).count()
            count_2 += db.session.query(Key.id).filter(Key.status.in_([1, 3]), Key.key_record_id == record.id).count()
        dic[wallet.id] = [count_1, count_2]

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
    add_admin_log(user=current_user.username, actions='查询渠道账号信息', client_ip=request.remote_addr, results='成功')

    return render_template("manage/get_channel_data.html", data=pagination.items, page=page, per_page=per_page,
                           pagination=pagination, form=form, dic=dic)


@login_required
def channel_data_detail(channel_id):
    form = ChannelDataDetailForm()
    channel_account = ChannelAccount.query.filter_by(channel_id=channel_id).limit(1).first()
    query = KeyRecordsStatistics.query.join(KeyRecord, KeyRecordsStatistics.key_record_id == KeyRecord.id).\
        filter(KeyRecord.channel_account_id == channel_account.id)

    dic = {}
    for key_record in query.all():
        count_1 = db.session.query(Key.id).filter_by(key_record_id=key_record.key_record_id).count()
        count_2 = db.session.query(Key.id).filter_by(status=1, key_record_id=key_record.key_record_id).count()
        dic[key_record.id] = [count_1, count_2]

    if form.validate_on_submit():
        order_by = form.order_by.data
    else:
        order_by = request.args.get('order_by')

    if order_by is not None:
        form.order_by.data = order_by
        if form.order_by.data == 0:
            query = query.order_by(KeyRecord.create_time.asc())
        elif form.order_by.data == 1:
            query = query.order_by(KeyRecord.count.desc())
        elif form.order_by.data == 2:
            query = query.order_by(KeyRecord.id.desc())
        else:
            query = query.order_by(KeyRecordsStatistics.income.desc())

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
    add_admin_log(user=current_user.username, actions='查询渠道账号信息', client_ip=request.remote_addr, results='成功')

    return render_template("manage/channel_data_detail.html", data=pagination.items, page=page, per_page=per_page,
                           pagination=pagination, form=form, dic=dic, channel_id=channel_id)


@login_required
def day_key_record_detail(key_record_id):
    form = DayChannelDataDetailForm()
    query = DivideDataStatistics.query.filter_by(key_record_id=key_record_id)

    if form.validate_on_submit():
        start_time = form.start_time.data
        end_time = form.end_time.data
    else:
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
        query = query.filter(DivideDataStatistics.record_time.between(form.start_time.data, form.end_time.data))

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
    add_admin_log(user=current_user.username, actions='查询渠道账号信息', client_ip=request.remote_addr, results='成功')

    return render_template("manage/day_key_record_detail.html", data=pagination.items, page=page, per_page=per_page,
                           pagination=pagination, form=form, key_record_id=key_record_id)


@login_required
def day_vip_detail(key_record_id, record_time):
    form = DayVipDetailForm()
    # datetime_strf = record_time.strftime('%Y%m%d%')
    record_time = datetime.datetime.strptime(''.join(record_time[0:10].split('-')), '%Y%m%d')
    query = VipDataStatistics.query.filter_by(key_record_id=key_record_id, record_time=record_time)

    if form.validate_on_submit():
        channel = form.channel.data
        ware_type = form.ware_type.data
    else:
        channel = request.args.get('channel')
        ware_type = request.args.get('ware_type')

    if channel is not None:
        form.channel.data = channel
        if form.channel.data != '':
            query = query.filter(
                VipDataStatistics.vip_channel.like('%' + form.channel.data + '%'))

    if ware_type is not None:
        form.ware_type.data = ware_type
        if form.ware_type.data != '':
            query = query.filter(
                VipDataStatistics.ware_name.like('%' + form.ware_type.data + '%'))

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
    add_admin_log(user=current_user.username, actions='查询渠道账号信息', client_ip=request.remote_addr, results='成功')

    return render_template("manage/day_vip_detail.html", data=pagination.items, page=page, per_page=per_page,
                           pagination=pagination, form=form, key_record_id=key_record_id, record_time=record_time)

# 失效key
@login_required
def expire_key():
    cur_id = request.args.get('id')
    # 通过key_record_id 查询该批次所有ke
    keys = Key.query.filter_by(key_record_id=cur_id, status=0).all()
    for key in keys:
        db.session.delete(key)
    try:
        db.session.commit()
        return jsonify({'code':0})
    except Exception as e:
        print(e)
        print(datetime.datetime.now())
        db.session.rollback()
        add_admin_log(user=current_user.username, actions='失效key', client_ip=request.remote_addr, results='失败')
        return jsonify({'code': 1})


@celery.task(name='make_key_record_radio_day_data')
def make_key_record_radio_day_data():

    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=1)
    yesterday_start_time = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
    yesterday_end_time = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)
    if DivideDataStatistics.query.filter_by(record_time=yesterday.strftime('%Y-%m-%d')).order_by(DivideDataStatistics.id.desc()).limit(1).first() is not None:
        return False
    key_records = db.session.query(KeyRecord.id, KeyRecord.vip_ratio, KeyRecord.business_ratio, KeyRecord.channel_account_id)\
        .filter(KeyRecord.id != '00000000000000',KeyRecord.channel_account_id != 1).all()
    for key_record in key_records:
        divide_data_statistics = DivideDataStatistics()
        # 昨天时间
        divide_data_statistics.record_time = yesterday
        # 批次
        divide_data_statistics.key_record_id = key_record[0]
        # 會員分成比例
        divide_data_statistics.vip_divide_ratio = key_record[1]
        # 三方分成比例
        divide_data_statistics.third_divide_ratio = key_record[2]
        # 計算每日購買會員的次數
        vip_count = db.session.query(func.count(MemberWareOrder.order_number)).filter(MemberWareOrder.status == 1,
                                    MemberWareOrder.pay_time.between(yesterday_start_time, yesterday_end_time)).filter(
            MemberWareOrder.key_record_id == key_record[0], MemberWareOrder.category == 0).first()
        if vip_count is not None:
            divide_data_statistics.vip_count = vip_count[0]
        else:
            divide_data_statistics.vip_count = 0

        # 計算每日購買會員人數
        vip_people_count = db.session.query(func.count(distinct(MemberWareOrder.buyer_godin_id))).filter(
            MemberWareOrder.pay_time.between(yesterday_start_time, yesterday_end_time)).filter \
            (MemberWareOrder.key_record_id == key_record[0], MemberWareOrder.status == 1,
             MemberWareOrder.category == 0).limit(1).first()
        if vip_people_count is not None:
            divide_data_statistics.vip_people_count = vip_people_count[0]
        else:
            divide_data_statistics.vip_people_count = 0
        # 計算鉑金會員每日分成
        member_ware_orders = db.session.query(MemberWareOrder.discount_price).filter(
            MemberWareOrder.key_record_id == key_record[0], MemberWareOrder.status == 1, MemberWareOrder.category == 0,
            MemberWareOrder.pay_time.between(yesterday_start_time, yesterday_end_time)).all()
        vip_money = 0
        if member_ware_orders is not None:
            for member_ware_order in member_ware_orders:
                vip_money += (member_ware_order[0] * key_record[1])/100
            divide_data_statistics.vip_money = vip_money
        # 計算三方會員每日購買次數
        third_vip_count = db.session.query(func.count(BusinessWareOrder.order_number)).filter(BusinessWareOrder.status == 1,
                                    BusinessWareOrder.pay_time.between(yesterday_start_time, yesterday_end_time)).filter \
            (BusinessWareOrder.key_record_id == key_record[0]).limit(1).first()
        if third_vip_count is not None:
            divide_data_statistics.third_vip_count = third_vip_count[0]
        else:
            divide_data_statistics.third_vip_count = 0
        # 計算三方會員每天購買人數
        third_people_count = db.session.query(func.count(distinct(BusinessWareOrder.buyer_godin_id))).filter(
            BusinessWareOrder.pay_time.between(yesterday_start_time, yesterday_end_time)).filter \
            (BusinessWareOrder.key_record_id == key_record[0], BusinessWareOrder.status == 1).limit(1).first()
        if third_people_count is not None:
            divide_data_statistics.third_people_count = third_people_count[0]
        else:
            divide_data_statistics.third_people_count = 0

        # 計算每日三方會員分成
        business_ware_orders = db.session.query(BusinessWareOrder.discount_price).filter(
            BusinessWareOrder.key_record_id == key_record[0], BusinessWareOrder.status == 1,
            BusinessWareOrder.pay_time.between(yesterday_start_time, yesterday_end_time)).all()
        third_vip_money = 0
        if business_ware_orders is not None:
            for business_ware_order in business_ware_orders:
                third_vip_money += (business_ware_order[0] * key_record[2])/100
            divide_data_statistics.third_vip_money = third_vip_money
        divide_data_statistics.total_money = third_vip_money + vip_money
        # 统计每个批次总的分成
        key_record_statistics = db.session.query(KeyRecordsStatistics).filter(KeyRecordsStatistics.key_record_id==key_record[0]).limit(1).first()
        if key_record_statistics is None:
            key_record_statistics = KeyRecordsStatistics()
            key_record_statistics.create_time = yesterday
            key_record_statistics.key_record_id = key_record[0]
            key_record_statistics.channel_account_id = key_record[3]
            key_record_statistics.income = vip_money + third_vip_money
        else:
            if True:
                # 如果某一天数据没有统计上 第二天放开这段进行所有数据从新累加
                divide_data_statistics_query = DivideDataStatistics.query.filter_by(key_record_id=key_record[0]).all()
                key_record_statistics.income = 0
                for day_statistics in divide_data_statistics_query:
                    key_record_statistics.income += (day_statistics.vip_money + day_statistics.third_vip_money)

            # 平时单独放开这一句就可以
            key_record_statistics.income = key_record_statistics.income + vip_money + third_vip_money
        # key_record_statistics.ping()
        if key_record_statistics.income != 0:
            db.session.add(key_record_statistics)
        if vip_money != 0 or third_vip_money != 0:
            db.session.add(divide_data_statistics)
        db.session.commit()

    return True


@celery.task(name='make_channel_account_radio_day_data')
def make_channel_account_radio_day_data():
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    if ChannelAccountStatistics.query.filter_by(record_time=yesterday.strftime('%Y-%m-%d')).order_by(ChannelAccountStatistics.id.desc()).limit(
            1).first() is not None:
        return False

    channel_accounts = db.session.query(ChannelAccount.channel_id, ChannelAccount.account_id, ChannelAccount.id).filter(
        ChannelAccount.id != 1).all()
    for channel_account in channel_accounts:
        channel_account_statistics = ChannelAccountStatistics()
        channel_account_statistics.record_time = yesterday
        channel_account_statistics.channel_account_id = channel_account[0]
        channel_account_statistics.account_id = channel_account[1]
        # 獲取該賬號下的所有批次分成
        key_records = db.session.query(KeyRecord.id).filter(KeyRecord.channel_account_id == channel_account[2]).all()
        channel_account_statistics.total_count = 0
        channel_account_statistics.total_money = 0
        for key_record in key_records:
            divide_data_statistics = db.session.query(DivideDataStatistics).filter(
                DivideDataStatistics.record_time == yesterday.strftime('%Y-%m-%d')).filter \
                (DivideDataStatistics.key_record_id == key_record[0]).limit(1).first()

            if divide_data_statistics is not None:
                channel_account_statistics.total_count += (
                        divide_data_statistics.vip_count + divide_data_statistics.third_vip_count)
                channel_account_statistics.total_money += (
                        divide_data_statistics.vip_money + divide_data_statistics.third_vip_money)
        wallet = Wallet.query.filter_by(channel_account_id=channel_account[2]).limit(1).first()
        if wallet is None:
            wallet = Wallet()
            wallet.create_time = yesterday
            wallet.channel_account_id = channel_account[2]
            wallet.account_id = channel_account[1]
            wallet.income = channel_account_statistics.total_money
            wallet.all_divide = channel_account_statistics.total_money
            wallet.balance = channel_account_statistics.total_money
        else:
            # 如果某一天数据没有统计上 第二天放开这段进行所有数据从新累加
            # channel_account_statistics_query = ChannelAccountStatistics.query.filter_by(channel_account_id=channel_account[0])
            # wallet.income = 0
            # for data_channel_account in channel_account_statistics_query:
            #     wallet.income += data_channel_account.total_money
            # 平时单独放开这一句就可以
            wallet.income = wallet.income + channel_account_statistics.total_money
            wallet.all_divide = wallet.all_divide + channel_account_statistics.total_money
        wallet.ping()
        db.session.add(wallet)
        db.session.add(channel_account_statistics)
        db.session.commit()
    return True


# 栏目每日分成数据统计
@celery.task(name='make_vip_type_radio_day_data')
def make_vip_type_radio_day_data():
    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=1)
    yesterday_start_time = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
    yesterday_end_time = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)
    if VipDataStatistics.query.filter_by(record_time=yesterday.strftime('%Y-%m-%d')).limit(1).first() is not None:
        return False
    # if BusinessDataStatistics.query.filter_by(record_time=yesterday.strftime('%Y-%m-%d')).first() is not None:
    #     return False

    key_records = db.session.query(KeyRecord.id, KeyRecord.vip_ratio, KeyRecord.business_ratio).filter(
        KeyRecord.id != '00000000000000').filter(KeyRecord.channel_account_id != 1).all()
    for key_record in key_records:
        # vip
        for ware in MemberWare.query.all():
            vip_data_statistics = VipDataStatistics()

            vip_data_statistics.record_time = yesterday
            # 批次
            vip_data_statistics.key_record_id = key_record[0]
            # 會員分成比例
            vip_data_statistics.vip_ratio = key_record[1]
            # 計算每日購買會員的次數
            vip_data_statistics.vip_channel = '黄金会员'
            if ware.gold_or_platinum == 1:
                vip_data_statistics.vip_channel = '铂金会员'
            member_ware_orders = db.session.query(MemberWareOrder.discount_price).filter(
                MemberWareOrder.ware_id == ware.id,
                MemberWareOrder.key_record_id == key_record[0], MemberWareOrder.status == 1,
                MemberWareOrder.category == 0,
                MemberWareOrder.pay_time.between(yesterday_start_time, yesterday_end_time)).all()
            vip_money = 0
            if member_ware_orders:
                vip_data_statistics.ware_name = ware.name

                for member_ware_order in member_ware_orders:
                    vip_data_statistics.discount_price = member_ware_order.discount_price
                    vip_money += (member_ware_order[0] * key_record[1]) / 100
                vip_data_statistics.vip_money = vip_money
                vip_count = db.session.query(func.count(MemberWareOrder.order_number)). \
                    filter(MemberWareOrder.status == 1,
                           MemberWareOrder.pay_time.between(yesterday_start_time, yesterday_end_time)). \
                    filter(MemberWareOrder.key_record_id == key_record[0], MemberWareOrder.category == 0). \
                    filter(MemberWareOrder.ware_id == ware.id).first()
                vip_data_statistics.vip_count = vip_count[0]
                # 計算每日購買會員人數
                vip_people_count = db.session.query(func.count(distinct(MemberWareOrder.buyer_godin_id))). \
                    filter(MemberWareOrder.pay_time.between(yesterday_start_time, yesterday_end_time)). \
                    filter(MemberWareOrder.key_record_id == key_record[0], MemberWareOrder.category == 0). \
                    filter(MemberWareOrder.ware_id == ware.id, MemberWareOrder.status == 1).limit(1).first()
                vip_data_statistics.vip_people_count = vip_people_count[0]
                if vip_data_statistics.vip_money > 0:
                    db.session.add(vip_data_statistics)
                    db.session.commit()

        # 客多多
        for ware in BusinessWare.query.all():
            business_data_statistics = VipDataStatistics()

            business_data_statistics.record_time = yesterday
            # 批次
            business_data_statistics.key_record_id = key_record[0]
            # 三方分成比例
            business_data_statistics.vip_ratio = key_record[2]
            # 計算每日購買會員的次數
            business_data_statistics.vip_channel = '客多多'
            # 客多多
            business_ware_orders = db.session.query(BusinessWareOrder.discount_price).filter(
                BusinessWareOrder.ware_id == ware.id,
                BusinessWareOrder.key_record_id == key_record[0], BusinessWareOrder.status == 1,
                BusinessWareOrder.pay_time.between(yesterday_start_time, yesterday_end_time)).all()
            business_money = 0
            if business_ware_orders:
                business_data_statistics.ware_name = ware.name
                for business_ware_order in business_ware_orders:
                    business_data_statistics.discount_price = business_ware_order.discount_price
                    business_money += (business_ware_order[0] * key_record[2]) / 100
                    business_data_statistics.vip_money = business_money
                vip_count = db.session.query(func.count(BusinessWareOrder.order_number)).filter(
                    BusinessWareOrder.status == 1,
                    BusinessWareOrder.pay_time.between(yesterday_start_time, yesterday_end_time)). \
                    filter(BusinessWareOrder.key_record_id == key_record[0]). \
                    filter(BusinessWareOrder.ware_id == ware.id).first()
                business_data_statistics.vip_count = vip_count[0]
                # 計算每日購買會員人數
                vip_people_count = db.session.query(func.count(distinct(BusinessWareOrder.buyer_godin_id))). \
                    filter(BusinessWareOrder.pay_time.between(yesterday_start_time, yesterday_end_time)). \
                    filter(BusinessWareOrder.key_record_id == key_record[0]). \
                    filter(BusinessWareOrder.ware_id == ware.id, BusinessWareOrder.status == 1).limit(1).first()
                business_data_statistics.vip_people_count = vip_people_count[0]

                if business_data_statistics.vip_money > 0:
                    db.session.add(business_data_statistics)
                    db.session.commit()

    return True

@celery.task(name='make_download_log_print')
def make_download_log_print():
    pass

@login_required
def get_function_video():
    # request.args.get只能获取到 get 请求的参数
    function_name = request.args.get("function_name")
    search_keyword = function_name  # 记录当前的搜索关键字
    page = request.args.get('page', 1, type=int)
    video_server = current_app.config['FILE_SERVER'] + current_app.config["UPLOAD_VIDEO_PATH"]
    form = FunctionVideoForm()
    if function_name:
        form.function_name.data = function_name
        pagination = FunctionVideo.query.filter(FunctionVideo.function_name.like('%{0}%'.format(function_name))).paginate(
            page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
        data = pagination.items

        return render_template('manage/get_function_video.html', form=form, all_video=data, pagination=pagination, search_keyword=search_keyword, video_server=video_server)

    if form.validate_on_submit():
        function_name = form.function_name.data.strip()
        search_keyword = function_name  # 点击搜索时记录当前搜索关键字，后续做删除操作之后继续保持之前的查询状态
        if len(function_name) == 0:
            flash("无查询结果")
            return render_template('manage/get_function_video.html', form=form, pagination=None, search_keyword=search_keyword, video_server=video_server)

        pagination = FunctionVideo.query.filter(FunctionVideo.function_name.like('%{0}%'.format(function_name))).paginate(
                              page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
        data = pagination.items
        if pagination.total == 0:
            flash("无查询结果")
        return render_template('manage/get_function_video.html', form=form, all_video=data, pagination=pagination,
                               search_keyword=search_keyword, video_server=video_server)
    for field, error in form.errors.items():
        flash(error[0])

    pagination = FunctionVideo.query.paginate(page=page,
                                              per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    data = pagination.items
    return render_template('manage/get_function_video.html', form=form, all_video=data, pagination=pagination, search_keyword=search_keyword, video_server=video_server)


@login_required
def add_function_video():
    form = AddVideoForm()
    if form.validate_on_submit():

        data = FunctionVideo.query.filter_by(function_name=form.function_name.data.strip()).limit(1).first()
        if data:
            flash("不能添加已存在的功能介绍!")
            return redirect(url_for("manage.add_function_video"))

        video_url = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + ".mp4"
        path = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

        dir_path = path + "/" + current_app.config['UPLOAD_VIDEO_PATH']
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        form.video_url.data.save(dir_path + video_url)

        video = FunctionVideo(
            function_name=form.function_name.data.strip(),
            video_url=video_url,
            comment=form.comment.data,
            last_operator=current_user.username
        )
        db.session.add(video)
        db.session.commit()
        flash("添加成功")
        return redirect(url_for("manage.get_function_video", function_name=form.function_name.data.strip()))
    for field, error in form.errors.items():
        flash(error[0])
        break
    return render_template("manage/add_function_video.html", form=form)


@login_required
def del_function_video():
    id = request.args.get("id")
    search_keyword = request.args.get("search_keyword")
    video = FunctionVideo.query.get_or_404(id)
    path = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    complete_path = os.path.join(path, current_app.config['UPLOAD_VIDEO_PATH'], video.video_url)
    os.remove(complete_path)
    db.session.delete(video)
    db.session.commit()
    flash("删除成功")
    return redirect(url_for("manage.get_function_video", function_name=search_keyword))


@login_required
def edit_function_video():
    form = EditVideoForm()
    id = request.args.get("id")
    video = FunctionVideo.query.get_or_404(id)
    if request.method == "GET":
        form.function_name.data = video.function_name
        form.comment.data = video.comment
    if form.validate_on_submit():

        record = FunctionVideo.query.filter_by(function_name=form.function_name.data.strip()).count()
        if video.function_name != form.function_name.data.strip() and record:
            flash("不能添加已存在的功能介绍!")
            form.function_name.data = form.function_name.data.strip()
            return render_template("manage/edit_function_video.html", form=form, id=id)

        if form.video_url.data.filename != "":  # 如果文件名不为空则说明用户新上传了文件
            video_url = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + ".mp4"
            path = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
            dir_path = path + "/" + current_app.config['UPLOAD_VIDEO_PATH']
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            # 删除原来保存的视频并添加新的视频
            os.remove(dir_path + video.video_url)
            form.video_url.data.save(dir_path + video_url)
            video.video_url = video_url

        video.function_name = form.function_name.data.strip()
        video.comment = form.comment.data.strip()
        video.last_operator = current_user.username
        db.session.add(video)
        db.session.commit()
        flash("提交成功")
        return redirect(url_for("manage.get_function_video", function_name=video.function_name))
    for field, error in form.errors.items():
        flash(error[0])
        break
    return render_template("manage/edit_function_video.html", form=form, id=id)


@login_required
def set_function():
    # 倒三角功能配置
    set_fun = redis.get('set_fun')
    if set_fun is None:
        redis.set('set_fun', "goumaivip,keduoduo,weiketang,weishangzhuli")

    form = SetFunctionForm()
    if form.validate_on_submit():
        function_name = form.function_name.data
        result = function_name.split(",")
        result = [i for i in result if i != ""]
        if len(result) == 4:
            for word in result:
                if is_Chinese(word):
                    break
            else:
                redis.set('set_fun', function_name)
                flash('添加成功')
                return redirect(url_for('manage.set_function'))

        flash('格式错误')
        return redirect(url_for('manage.set_function', function_name=function_name))
    set_fun = str(redis.get('set_fun'), encoding='utf-8')
    if request.args.get("function_name"):
        set_fun = request.args.get("function_name")
    form.function_name.data = set_fun
    for field, error in form.errors.items():
        flash(error[0])
        break

    return render_template('manage/set_function.html', form=form)


@celery.task(name="make_ads_count")
def make_ads_count():
    ads = db.session.query(OpenScreenAds).all()
    ad_ids = [ad.id for ad in ads]  # 取出 OpenScreenAds 表中的所有广告类型

    all_key = redis.smembers("GetOpenScreenAdsStatistics")
    all_key = [str(i, encoding="utf-8") for i in all_key]
    num = 0
    for key in all_key:
        value = redis.get(key)
        infos = eval(key)
        if infos["ad_id"] not in ad_ids:  # 如果 ad_id 不在 ad_ids 则忽略当前记录
            redis.srem("GetOpenScreenAdsStatistics", key)
            del redis[key]
            continue
        open_ads = OpenScreenAdsStatistics.query.filter_by(ad_id=infos["ad_id"], operation=infos["operation"],
                                                           imei=infos["imei"],
                                                           record_time=infos["record_time"]
                                                           ).with_lockmode('update').limit(1).first()
        if open_ads is None:
            open_ads = OpenScreenAdsStatistics()
            open_ads.ad_id = infos["ad_id"]
            open_ads.imei = infos["imei"]
            open_ads.operation = infos["operation"]
            open_ads.count = int(value)
            open_ads.record_time = infos["record_time"]
            db.session.add(open_ads)
        else:
            open_ads.count += int(value)
            db.session.add(open_ads)
        num += 1
        try:
            if num % 100 ==0:
                db.session.commit()
            redis.srem("GetOpenScreenAdsStatistics", key)
            del redis[key]
        except Exception as e:
            print(e)
            db.session.rollback()
            print_log(action='Response', function='GetOpenScreenAdsStatisticsApi', branch='DB_SESSION_EXCEPTION',
                      api_version='v1.0', imei=infos['imei'])
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print_log(action='Response', function='GetOpenScreenAdsStatisticsApi', branch='DB_SESSION_EXCEPTION',
                  api_version='v1.0', imei=infos['imei'])


@celery.task(name="make_data_update")
def make_data_update():
    # 按目前时间计算，将七天之前的记录删除
    valid_time = datetime.datetime.today() - datetime.timedelta(days=7)
    valid_time = datetime.datetime.date(valid_time)  # 将时间从转换成 date 类型

    banner_ads = db.session.query(BannerAdsStatistics).filter(BannerAdsStatistics.record_time < valid_time).all()
    open_ads = db.session.query(OpenScreenAdsData).filter(OpenScreenAdsData.record_time < valid_time).all()

    try:
        for ad in banner_ads:
            db.session.delete(ad)
        for ad in open_ads:
            db.session.delete(ad)
        db.session.commit()
    except Exception:
        db.session.rollback()


@celery.task(name="make_banner_ads_count")
def make_banner_ads_count():
    ads = db.session.query(BannerAds).all()
    ad_ids = [ad.id for ad in ads]  # 取出 OpenScreenAds 表中的所有广告类型
    num = 0
    while True:
        value = redis.rpop("BannerAdsStatistics")
        if value is None:
            break
        infos = eval(value)
        if infos["ad_id"] not in ad_ids:  # 如果 ad_id 不在 ad_ids 则忽略当前记录
            continue
        banner_ads = BannerAdsStatistics.query.filter_by(ad_id=infos["ad_id"], operation=infos["operation"],
                                                         imei=infos["imei"], record_time=infos["record_time"]
                                                         ).with_lockmode('update').limit(1).first()
        if banner_ads is None:
            banner_ads = BannerAdsStatistics()
            banner_ads.ad_id = infos["ad_id"]
            banner_ads.imei = infos["imei"]
            banner_ads.operation = infos["operation"]
            banner_ads.record_time = infos["record_time"]
            banner_ads.count = 1
            db.session.add(banner_ads)
        else:
            banner_ads.count += 1
            db.session.add(banner_ads)
        num += 1
        try:
            if num % 100 ==0 :
                db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            print_log(action='Response', function='BannerAdsStatistics', branch='DB_SESSION_EXCEPTION',
                      api_version='v1.0', imei=infos['imei'])
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        print_log(action='Response', function='BannerAdsStatistics', branch='DB_SESSION_EXCEPTION',
                  api_version='v1.0', imei=infos['imei'])

@celery.task(name="make_open_screen_ads_count")
def make_open_screen_ads_count():
    ads = db.session.query(OpenScreenAds).all()
    ad_ids = [ad.id for ad in ads]  # 取出 OpenScreenAds 表中的所有广告类型
    num = 0
    while True:
        value = redis.rpop("OpenScreenAdsData")
        if value is None:
            break
        infos = eval(value)
        if infos["ad_id"] not in ad_ids:  # 如果 ad_id 不在 ad_ids 则忽略当前记录
            continue

        ads_info = OpenScreenAdsData.query.filter_by(ad_id=infos["ad_id"], imei=infos['imei'], operation=infos['operation'],
                                                     record_time=infos["record_time"]).limit(1).first()
        if ads_info is None:
            ads_info = OpenScreenAdsData()
            ads_info.ad_id = infos["ad_id"]
            ads_info.imei = infos["imei"]
            ads_info.operation = infos["operation"]
            ads_info.record_time = infos["record_time"]
            ads_info.count = 1
            db.session.add(ads_info)
        else:
            ads_info.count += 1
            db.session.add(ads_info)
        num += 1
        try:
            if num % 100 == 0:
                db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            print_log(action='Response', function='OpenScreenAdsData', branch='INTERNAL_ERROR',
                      api_version='v1.0', imei=infos['imei'])
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        print_log(action='Response', function='OpenScreenAdsData', branch='INTERNAL_ERROR',
                  api_version='v1.0', imei=infos['imei'])

@celery.task(name="make_open_ads_count")
def make_open_ads_count():
    ads = db.session.query(OpenScreenAds).all()
    ad_ids = [ad.id for ad in ads]  # 取出 OpenScreenAds 表中的所有广告类型
    num = 0
    while True:
        value = redis.rpop("GetOpenAdsStatistics")
        if value is None:
            break
        infos = eval(value)
        if infos["ad_id"] not in ad_ids:  # 如果 ad_id 不在 ad_ids 则忽略当前记录
            continue

        ads_info = OpenScreenAdsStatistics.query.filter_by(ad_id=infos["ad_id"], imei=infos['imei'],
                                                           operation=infos['operation'],
                                                           record_time=infos["record_time"]).limit(1).first()
        if ads_info is None:
            ads_info = OpenScreenAdsStatistics()
            ads_info.ad_id = infos["ad_id"]
            ads_info.imei = infos["imei"]
            ads_info.operation = infos["operation"]
            ads_info.record_time = infos["record_time"]
            ads_info.count = 1
            db.session.add(ads_info)
        else:
            ads_info.count += 1
            db.session.add(ads_info)
        num += 1
        try:
            if num % 100 == 0:
                db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            print_log(action='Response', function='GetOpenAdsStatistics', branch='INTERNAL_ERROR',
                      api_version='v1.0', imei=infos['imei'])
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        print_log(action='Response', function='GetOpenAdsStatistics', branch='INTERNAL_ERROR',
                  api_version='v1.0', imei=infos['imei'])

@celery.task(name="make_screen_simulate_ads_count")
def make_screen_simulate_ads_count():
    ads = db.session.query(OpenScreenAds).all()
    ad_ids = [ad.id for ad in ads]  # 取出 OpenScreenAds 表中的所有广告类型
    num = 0
    for ad_id in ad_ids:
        key = str(ad_id) + str(datetime.date.today() - datetime.timedelta(days=1))
        sim_info = cache.get(key)
        if sim_info is not None:
            simulate = OpenScreenSimulateData.query.filter_by(ad_id=ad_id,
                                                              record_time=datetime.date.today()).order_by(
                                                              OpenScreenSimulateData.id.desc()).limit(1).first()
            if simulate is not None:
                simulate.actual_control_times = sim_info.actual_control_times
                db.session.add(simulate)
                num =+ 1
                if num % 100 ==0:
                    db.session.commit()
        else:
            continue
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()


@login_required
def get_gold_ware_info():
    form = QueryMemberWareForm()
    query = MemberWare.query.order_by(MemberWare.id.desc()).filter_by(gold_or_platinum=0)
    if form.validate_on_submit():
        channel = form.channel.data
        category = form.category.data
        status = form.status.data
    else:
        channel = request.args.get('channel')
        category = request.args.get('category')
        status = request.args.get('status', type=int)

    if channel is not None:
        form.channel.data = channel
        if form.channel.data != '':
            query = query.filter(MemberWare.channel.like('%' + form.channel.data + '%'))
    if category is not None:
        form.category.data = category
        if form.category.data != '':
            vip_type = VipType.query.filter_by(name=form.category.data).first()
            if vip_type is not None:
                type_number = vip_type.number
            else:
                type_number = 0
            query = query.filter_by(category=type_number)
    if status is not None:
        form.status.data = status
        if form.status.data != -1:
            query = query.filter_by(status=form.status.data)

    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    cell = {}
    for ware in pagination.items:
        vip_type = VipType.query.filter_by(number=ware.category).first()
        if vip_type is not None:
            cell[ware.id] = vip_type.name
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='查看产品', client_ip=request.remote_addr,
                      results=error[0])
    if not form.errors:
        add_admin_log(user=current_user.username, actions='查看产品', client_ip=request.remote_addr,
                      results='成功')
    return render_template("manage/get_gold_ware_info.html", form=form, data=pagination.items, pagination=pagination,
                           page=page, per_page=current_app.config['RECORDS_PER_PAGE'], data_cate=cell)


@login_required
def add_gold_ware():
    form = AddMemberWareForm()
    info = MemberWare()
    if form.validate_on_submit():
        channel = form.channel.data
        category = form.category.data
        number = form.number.data
        name = form.name.data
        price = int(round(form.price.data, 2) * 100)
        discount = round(form.common_discount.data, 2)
        gold_discount = round(form.gold_discount.data, 2)
        description = form.description.data
        status = form.status.data
        picture = request.files['picture']

        if (discount > 1.0 or discount < 0) and (gold_discount > 1.0 or gold_discount < 0):
            flash('折扣区间: 0.00 -- 1.00')
            add_admin_log(user=current_user.username, actions='添加产品', client_ip=request.remote_addr,
                          results='折扣输入错误')
            return render_template("manage/add_gold_ware.html", form=form)

        if MemberWare.query.filter_by(id=number).first() is not None:
            flash('产品编号已经存在')
            add_admin_log(user=current_user.username, actions='添加产品', client_ip=request.remote_addr,
                          results='产品编号存在')
            return render_template("manage/add_gold_ware.html", form=form)

        if MemberWare.query.filter_by(name=name).first() is not None:
            flash('产品名称已存在')
            add_admin_log(user=current_user.username, actions='添加产品', client_ip=request.remote_addr,
                          results='产品名称存在')
            return render_template("manage/add_gold_ware.html", form=form)
        if price * discount < 1 or price * gold_discount < 1:
            flash('会员购买价格不能小于1分')
            add_admin_log(user=current_user.username, actions='会员购买价格不能小于1分', client_ip=request.remote_addr,
                          results='会员购买价格不能小于1分')
            return render_template("manage/add_gold_ware.html", form=form)
        vip_type = VipType.query.filter_by(name=category).first()
        if vip_type is not None:
            type_number = vip_type.number
        else:
            type_number = 0
        if channel is None:
            channel = 'moren'
        if MemberWare.query.filter_by(channel=channel, category=type_number, status=1, gold_or_platinum=0).first() is not None:
            flash('该渠道的这个类型的产品已存在')
            add_admin_log(user=current_user.username, actions='添加产品', client_ip=request.remote_addr,
                          results='该渠道的这个类型的产品已存在')
            return render_template("manage/add_gold_ware.html", form=form)
        if picture:
            file_name = secure_filename(picture.filename)
            if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', picture.filename.rsplit('.', 1)[0])):
                flash('图片名称不能为纯汉字')
                add_admin_log(user=current_user.username, actions='添加产品', client_ip=request.remote_addr,
                              results='图片名称不能为纯汉字')
                return redirect(url_for('manage.add_gold_ware'))
            if file_name.rsplit('.', 1)[1] not in ['png', 'jpg']:
                flash('图片格式错误')
                add_admin_log(user=current_user.username, actions='添加产品', client_ip=request.remote_addr,
                              results='图片格式错误')
                return redirect(url_for('manage.add_gold_ware'))
            size = len(picture.read())
            if size > 5120:
                flash("图片大小不能超过5KB")
                add_admin_log(user=current_user.username, actions='添加产品',
                              client_ip=request.remote_addr, results='头像图片大小不能超过5KB')
                return redirect(url_for('manage.add_gold_ware'))

            app_dir = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], "vip_ware")
            file_url = os.path.join(current_app.config['PHOTO_TAG'], "vip_ware")
            if not os.path.exists(app_dir):
                os.mkdir(app_dir)
            im = Image.open(picture)
            info.picture = os.path.join(file_url, file_name)
            im.save(os.path.join(app_dir, file_name))
        else:
            info.picture = ''
        if channel is None:
            info.channel = 'moren'
        else:
            info.channel = channel
        vip_type = VipType.query.filter_by(name=category).first()
        if vip_type is not None:
            info.category = vip_type.number
        info.id = number
        info.name = name
        info.price = price
        info.common_discount = discount
        info.gold_discount = gold_discount
        info.description = description
        info.status = status
        info.priority = 0
        info.gold_or_platinum = 0
        db.session.add(info)
        db.session.commit()
        add_admin_log(user=current_user.username, actions='添加产品', client_ip=request.remote_addr, results='成功')
        return redirect(url_for('manage.get_gold_ware_info'))

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='添加产品', client_ip=request.remote_addr, results=error[0])
    return render_template("manage/add_gold_ware.html", form=form)


@login_required
def get_vip_gold_ware_details(ware_id):
    photo_url = current_app.config['FILE_SERVER']
    query = MemberWare.query.filter_by(id=ware_id).first()
    vip = VipType.query.filter_by(number=query.category).first()
    category = vip.name
    pay_price = (query.price * query.common_discount) / 100
    gold_pay_price = (query.price * query.gold_discount) / 100
    price = [pay_price, gold_pay_price]
    add_admin_log(user=current_user.username, actions='获取vip产品详情', client_ip=request.remote_addr, results='成功')
    return render_template('manage/vip_gold_ware_details.html', ware=query, photo_url=photo_url, ware_id=ware_id,
                           price=price, category=category)


@login_required
def edit_gold_ware(ware_id):
    form = EditMemberWareForm()
    info = MemberWare.query.filter_by(id=ware_id).first()
    if form.validate_on_submit() and info is not None:
        name = form.name.data
        price = int(round(form.price.data, 2) * 100)
        common_discount = round(form.common_discount.data, 2)
        gold_discount = round(form.gold_discount.data, 2)
        description = form.description.data
        status = form.status.data
        picture = request.files['picture']

        if (common_discount > 1.0 or common_discount < 0) and (gold_discount > 1.0 or gold_discount < 0):
            flash('折扣区间: 0.00 -- 1.00')
            add_admin_log(user=current_user.username, actions='编辑产品', client_ip=request.remote_addr,
                          results='折扣输入错误')
            return render_template("manage/edit_gold_ware.html", form=form, ware_id=ware_id)

        if MemberWare.query.filter(MemberWare.name == name, MemberWare.id != ware_id).first() is not None:
            flash('产品名称已存在')
            add_admin_log(user=current_user.username, actions='编辑产品', client_ip=request.remote_addr,
                          results='产品名称存在')
            return render_template("manage/edit_gold_ware.html", form=form, ware_id=ware_id)
        if price * common_discount < 1 or price * gold_discount < 1:
            flash('会员购买价格不能小于1分')
            add_admin_log(user=current_user.username, actions='会员购买价格不能小于1分', client_ip=request.remote_addr,
                          results='会员购买价格不能小于1分')
            return render_template("manage/edit_gold_ware.html", form=form)
        if picture:
            file_name = secure_filename(picture.filename)
            if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', picture.filename.rsplit('.', 1)[0])):
                flash('图片名称不能为纯汉字')
                add_admin_log(user=current_user.username, actions='编辑产品', client_ip=request.remote_addr,
                              results='图片名称不能为纯汉字')
                return render_template("manage/edit_ware.html", form=form, ware_id=ware_id)
            if file_name.rsplit('.', 1)[1] not in ['png', 'jpg']:
                flash('图片格式错误')
                add_admin_log(user=current_user.username, actions='编辑产品', client_ip=request.remote_addr,
                              results='图片格式错误')
                return render_template("manage/edit_ware.html", form=form, ware_id=ware_id)
            size = len(picture.read())
            if size > 5120:
                flash("图片大小不能超过5KB")
                add_admin_log(user=current_user.username, actions='编辑产品',
                              client_ip=request.remote_addr, results='头像图片大小不能超过5KB')
                return render_template("manage/edit_gold_ware.html", form=form, ware_id=ware_id)
            app_dir = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], "vip_ware")
            file_url = os.path.join(current_app.config['PHOTO_TAG'], "vip_ware")
            if not os.path.exists(app_dir):
                os.mkdir(app_dir)
            im = Image.open(picture)
            info.picture = os.path.join(file_url, file_name)
            im.save(os.path.join(app_dir, file_name))

        info.name = name
        info.price = price
        info.common_discount = common_discount
        info.gold_discount = gold_discount
        info.description = description
        info.status = status
        # info.ads_category = ','.join(ads_cate)

        db.session.add(info)
        db.session.commit()
        return redirect(url_for('manage.get_gold_ware_info'))
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='编辑产品', client_ip=request.remote_addr, results=error[0])
    if info is not None:
        form.name.data = info.name
        form.price.data = info.price / 100
        form.description.data = info.description
        form.common_discount.data = info.common_discount
        form.gold_discount.data = info.gold_discount
        form.status.data = info.status
        form.picture.data = info.picture
    vip_type = VipType.query.filter_by(number=info.category).first()
    if vip_type is not None:
        type_name = vip_type.name
    else:
        type_name = ''

    if not form.errors:
        add_admin_log(user=current_user.username, actions='编辑产品', client_ip=request.remote_addr, results='成功')

    return render_template("manage/edit_gold_ware.html", form=form, ware_id=ware_id, channel=info.channel,
                           category=type_name, picture=info.picture,
                           file_url=current_app.config['FILE_SERVER'])


@login_required
def micro_store_url():
    # 微店铺跳转链接
    form = MicroStoreForm()
    if request.method == "GET":
        link = cache.get('micro_store_url')
        if link:
            form.link.data = link
            return render_template("manage/micro_store_url.html", form=form)
        else:
            record = db.session.query(KeyValue).filter_by(key="micro_store_url").limit(1).first()
            if not record:
                key_value = KeyValue(
                    key="micro_store_url"
                )
                db.session.add(key_value)
                db.session.commit()
            else:
                form.link.data = record.value
                cache.set('micro_store_url', record.value, timeout=12 * 60 * 60)

    if form.validate_on_submit():
        link = form.link.data.strip()
        record = db.session.query(KeyValue).filter_by(key="micro_store_url").limit(1).first()
        record.value = link
        db.session.add(record)
        db.session.commit()
        cache.set('micro_store_url', link, timeout=12 * 60 * 60)
        flash("添加成功")
    for field, error in form.errors.items():
        flash(error[0])
        break
    return render_template("manage/micro_store_url.html", form=form)


@login_required
def generalize_data():
    phone_num = request.args.get("phone_num", None)
    page = request.args.get('page', 1, type=int)
    all_award = 0
    form = PhoneForm()
    if phone_num:
        form.phone_num.data = phone_num
        pagination = UserGeneralize.query.filter(UserGeneralize.phone_num.like('{0}%'.format(phone_num))).paginate(
            page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)

        for item in pagination.items:
            item.member_award = deal_float(item.member_award / 100)
            item.active_code_award = deal_float(item.active_code_award / 100)
            item.account_balance = deal_float(item.account_balance / 100)
            item.all_award = deal_float(item.member_award + item.active_code_award)
            item.pay_person_num = get_pay_person_num(item.godin_id)

        return render_template('manage/generalize_data.html', form=form, data=pagination.items, phone_num=phone_num,
                               pagination=pagination)

    if request.method == "GET":
        pagination = UserGeneralize.query.filter(UserGeneralize.invite_person_num > 0).paginate(
            page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
        for item in pagination.items:
            item.member_award = deal_float(item.member_award / 100)
            item.active_code_award = deal_float(item.active_code_award / 100)
            item.account_balance = deal_float(item.account_balance / 100)
            item.all_award = deal_float(item.member_award + item.active_code_award)
            item.pay_person_num = get_pay_person_num(item.godin_id)
        return render_template('manage/generalize_data.html', form=form, data=pagination.items, pagination=pagination)

    if form.validate_on_submit():
        phone_num = form.phone_num.data.strip()
        pagination = UserGeneralize.query.filter(UserGeneralize.phone_num.like('{0}%'.format(phone_num))).paginate(
            page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
        if pagination.total == 0:
            flash("无查询结果")
        for item in pagination.items:
            item.member_award = deal_float(item.member_award / 100)
            item.active_code_award = deal_float(item.active_code_award / 100)
            item.account_balance = deal_float(item.account_balance / 100)
            item.all_award = deal_float(item.member_award + item.active_code_award)
            item.pay_person_num = get_pay_person_num(item.godin_id)
        return render_template('manage/generalize_data.html', form=form, data=pagination.items, phone_num=phone_num,
                               pagination=pagination)

    if form.is_submitted():
        if not form.phone_num.data.strip():
            flash("无查询结果")
            return render_template('manage/generalize_data.html', form=form, pagination=None)

    for field, error in form.errors.items():
        flash(error[0])
        break

    return render_template('manage/generalize_data.html', form=form, data={}, pagination=None)


@login_required
def member_divide():
    # 会员分成比例
    form = MemberDivideForm()
    if request.method == "GET":
        divide = cache.get('member_divide')
        if divide:
            form.divide.data = divide
            return render_template("manage/member_divide.html", form=form)
        else:
            record = db.session.query(KeyValue).filter_by(key="member_divide").limit(1).first()
            if not record:
                key_value = KeyValue(
                    key="member_divide"
                )
                db.session.add(key_value)
                db.session.commit()
            else:
                form.divide.data = record.value
                cache.set('member_divide', record.value, timeout=12 * 60 * 60)

    if form.validate_on_submit():
        record = db.session.query(KeyValue).filter_by(key="member_divide").limit(1).first()
        record.value = form.divide.data
        db.session.add(record)
        db.session.commit()
        cache.set('member_divide', form.divide.data, timeout=12 * 60 * 60)
        flash("添加成功")
    for field, error in form.errors.items():
        flash(error[0])
        break
    return render_template("manage/member_divide.html", form=form)


@login_required
def get_invite_detail():
    godin_id = request.args.get("godin_id", None)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    form = PhoneForm()
    # 获取被邀请的人
    if form.validate_on_submit():
        phone_num = form.phone_num.data
    else:
        phone_num = request.args.get("phone_num", None)
    query = InviteInfo.query.filter_by(inviter_godin_id=godin_id)
    if phone_num:
        query = query.filter(InviteInfo.phone_num.like('{0}%'.format(phone_num)))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    data = []
    for item in pagination.items:
        sum_earn = 0
        # 判断被邀请人是否注册
        godin_account = GodinAccount.query.filter_by(godin_id=item.godin_id).limit(1).first()
        if godin_account:
            # 如果注册了判断是否有消费记录
            member_earn = MemberEarnRecord.query.with_entities(
                label('sum_earn', func.sum(MemberEarnRecord.member_earn))).filter_by(
                be_invited_phone=godin_account.phone_num).group_by(MemberEarnRecord.be_invited_phone).first()
            if member_earn:
                sum_earn = deal_float(float(member_earn.sum_earn) / 100)
            data.append([item.phone_num, item.create_time, godin_account.create_time, sum_earn])
        else:
            data.append([item.phone_num, item.create_time, "", sum_earn])
    if len(data) == 0:
        flash("无查询结果")
    for field, error in form.errors.items():
        flash(error[0])
        break
    return render_template('manage/invite_data.html', form=form, data=data, pagination=pagination,
                            godin_id=godin_id, phone_num=phone_num, page=page, per_page=per_page)


@login_required
def get_invite_detail_detail():
    form = MemberDetailForm()
    phone_num = request.args.get("phone_num", None)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    query = MemberEarnRecord.query.filter_by(be_invited_phone=phone_num).order_by(MemberEarnRecord.create_time.desc())
    if form.validate_on_submit():
        start_time = form.start_time.data
        end_time = form.end_time.data
    else:
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
        if form.end_time.data != '' and form.start_time.data != '':
            query = query.filter(MemberEarnRecord.create_time.between(form.start_time.data,
                                                                            form.end_time.data))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    data = []
    for item in pagination.items:
        data.append([item.create_time, item.member_type, item.member_name, deal_float(item.price / 100),
                     item.member_divide, deal_float(item.member_earn / 100)])

    for field, error in form.errors.items():
        flash(error[0])
        break
    return render_template('manage/invite_data_detail.html', form=form, data=data, pagination=pagination,
                           phone_num=phone_num, page=page, per_page=per_page)


@login_required
def invite_code_data():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    form = ActiveCodeForm()

    if form.validate_on_submit():
        channel_id = form.channel_id.data
        invite_phone = form.invite_phone.data
        phone = form.phone.data
    else:
        channel_id = request.args.get('channel_id')
        invite_phone = request.args.get('invite_phone')
        phone = request.args.get('phone')
    query = InviteEarnRecord.query

    if channel_id is not None:
        form.channel_id.data = channel_id
        if form.channel_id.data != '':
            query = query.filter(InviteEarnRecord.channel_id.like('%' + form.channel_id.data + '%'))

    if invite_phone is not None:
        form.invite_phone.data = invite_phone
        if form.invite_phone.data != '':
            query = query.filter(InviteEarnRecord.phone_num.like(form.invite_phone.data + '%'))

    if phone is not None:
        form.phone.data = phone
        if form.phone.data != '':
            query = query.filter(InviteEarnRecord.be_invited_phone.like(form.phone.data + '%'))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    if pagination.total == 0:
        flash("无查询结果")
    for field, error in form.errors.items():
        flash(error[0])
        break

    for item in pagination.items:
        item.price = deal_float(item.price / 100)
        item.inviter_earn = deal_float(item.inviter_earn / 100)
        item.channel_earn = deal_float(item.channel_earn / 100)

    return render_template("manage/invite_code.html", form=form, data=pagination.items, pagination=pagination,
                           page=page, per_page=per_page)


@login_required
def invite_code_divide():
    # 邀请码分成比例设置
    form = AddInviteCodeForm()
    if request.method == "GET":
        inviter_divide = cache.get('inviter_divide')
        channel_divide = cache.get('channel_divide')
        if inviter_divide and channel_divide:
            form.inviter_divide.data = inviter_divide
            form.channel_divide.data = channel_divide
            return render_template("manage/invite_code_divide.html", form=form)
        else:
            record = KeyValue.query.filter(or_(KeyValue.key == "inviter_divide", KeyValue.key == "channel_divide")).all()
            if not record:
                key_value1 = KeyValue(
                    key="inviter_divide"
                )
                key_value2 = KeyValue(
                    key="channel_divide"
                )
                db.session.add(key_value1)
                db.session.add(key_value2)
                db.session.commit()
            else:
                for item in record:
                    if item.key == "inviter_divide":
                        form.inviter_divide.data = item.value
                        cache.set('inviter_divide', item.value, timeout=12 * 60 * 60)
                    else:
                        form.channel_divide.data = item.value
                        cache.set('channel_divide', item.value, timeout=12 * 60 * 60)

    if form.validate_on_submit():
        record = KeyValue.query.filter(or_(KeyValue.key == "inviter_divide", KeyValue.key == "channel_divide")).all()
        for item in record:
            if item.key == "inviter_divide":
                item.value = form.inviter_divide.data
                cache.set('inviter_divide', form.inviter_divide.data, timeout=12 * 60 * 60)
            else:
                item.value = form.channel_divide.data
                cache.set('channel_divide', form.channel_divide.data, timeout=12 * 60 * 60)
            db.session.add(item)
        db.session.commit()
        flash("添加成功")
    for field, error in form.errors.items():
        flash(error[0])
        break
    return render_template("manage/invite_code_divide.html", form=form)


@login_required
def active_intro():
    # 活动说明
    form = ActiveIntroduceForm()
    if request.method == "GET":
        active_intro = cache.get('active_introduce')
        if active_intro:
            form.active_intro.data = active_intro
            return render_template("manage/active_introduce.html", form=form)
        else:
            record = db.session.query(ServiceProtocol).filter_by(category=10).limit(1).first()
            if not record:
                ser_pro = ServiceProtocol(
                    category=10
                )
                db.session.add(ser_pro)
                db.session.commit()
            else:
                form.active_intro.data = record.content
                cache.set('active_introduce', record.content, timeout=12 * 60 * 60)

    if form.validate_on_submit():
        active_intro = form.active_intro.data
        record = db.session.query(ServiceProtocol).filter_by(category="10").limit(1).first()
        record.content = active_intro
        db.session.add(record)
        db.session.commit()
        cache.set('active_introduce', active_intro, timeout=12 * 60 * 60)
        flash("添加成功")
    for field, error in form.errors.items():
        flash(error[0])
        break
    return render_template("manage/active_introduce.html", form=form)


@login_required
def fc_info():
    form = FcInfoForm()
    query = FriendCircle.query
    file_ser = current_app.config['FILE_SERVER']
    if form.validate_on_submit():
        start_time = form.start_time.data
        end_time = form.end_time.data
    else:
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
        if form.start_time.data != '' and form.end_time.data != '':
            query = query.filter(FriendCircle.create_time.between(form.start_time.data, form.end_time.data))

    flag = False
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='朋友圈推广素材', client_ip=request.remote_addr,
                      results=error[0])
    add_admin_log(user=current_user.username, actions='朋友圈推广素材', client_ip=request.remote_addr, results='成功')
    return render_template("manage/cf_info.html", form=form, data=pagination.items, pagination=pagination,
                           page=page, per_page=current_app.config['RECORDS_PER_PAGE'], file_ser=file_ser)


@login_required
def add_fc_content():
    form = AddFcContentForm()
    if form.validate_on_submit():
        fc = FriendCircle()
        content = form.content.data
        picture1 = request.files['picture1']
        picture2 = request.files['picture2']
        picture3 = request.files['picture3']
        if picture1:
            file_name = secure_filename(picture1.filename)
            if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', picture1.filename.rsplit('.', 1)[0])):
                flash('宣传图片1名称不能为纯汉字')
                add_admin_log(user=current_user.username, actions='新建素材', client_ip=request.remote_addr,
                              results='宣传图片1名称不能为纯汉字')
                return redirect(url_for('manage.add_fc_content'))
            size = len(picture1.read())
            if size > 204800:
                flash("宣传图片1大小不能超过200KB")
                add_admin_log(user=current_user.username, actions='新建素材',
                              client_ip=request.remote_addr, results='宣传图片1大小不能超过200KB')
                return redirect(url_for('manage.add_fc_content'))

            app_dir = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], "friend_circle")
            file_url = os.path.join(current_app.config['PHOTO_TAG'], "friend_circle")
            if not os.path.exists(app_dir):
                os.mkdir(app_dir)
            im = Image.open(picture1)
            new_name = str(int(time.time() * 10000)) + '.' + file_name.rsplit('.', 1)[1]
            fc.picture1 = os.path.join(file_url, new_name)
            im.save(os.path.join(app_dir, new_name))
        if picture2:
            file_name = secure_filename(picture2.filename)
            if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', picture2.filename.rsplit('.', 1)[0])):
                flash('宣传图片2名称不能为纯汉字')
                add_admin_log(user=current_user.username, actions='新建素材', client_ip=request.remote_addr,
                              results='宣传图片2名称不能为纯汉字')
                return redirect(url_for('manage.add_fc_content'))

            size = len(picture2.read())
            if size > 204800:
                flash("宣传图片2大小不能超过200KB")
                add_admin_log(user=current_user.username, actions='新建素材',
                              client_ip=request.remote_addr, results='宣传图片2大小不能超过200KB')
                return redirect(url_for('manage.add_fc_content'))

            app_dir = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], "friend_circle")
            file_url = os.path.join(current_app.config['PHOTO_TAG'], "friend_circle")
            if not os.path.exists(app_dir):
                os.mkdir(app_dir)
            im = Image.open(picture2)
            new_name = str(int(time.time() * 10000)) + '.' + file_name.rsplit('.', 1)[1]
            fc.picture2 = os.path.join(file_url, new_name)
            im.save(os.path.join(app_dir, new_name))
        if picture3:
            file_name = secure_filename(picture3.filename)
            if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', picture3.filename.rsplit('.', 1)[0])):
                flash('宣传图片3名称不能为纯汉字')
                add_admin_log(user=current_user.username, actions='新建素材', client_ip=request.remote_addr,
                              results='宣传图片3名称不能为纯汉字')
                return redirect(url_for('manage.add_fc_content'))

            size = len(picture3.read())
            if size > 204800:
                flash("宣传图片3大小不能超过200KB")
                add_admin_log(user=current_user.username, actions='新建素材',
                              client_ip=request.remote_addr, results='宣传图片3大小不能超过200KB')
                return redirect(url_for('manage.add_fc_content'))

            app_dir = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], "friend_circle")
            file_url = os.path.join(current_app.config['PHOTO_TAG'], "friend_circle")
            if not os.path.exists(app_dir):
                os.mkdir(app_dir)
            im = Image.open(picture3)
            new_name = str(int(time.time() * 10000)) + '.' + file_name.rsplit('.', 1)[1]
            fc.picture3 = os.path.join(file_url, new_name)
            im.save(os.path.join(app_dir, new_name))
        fc.content = content
        db.session.add(fc)
        db.session.commit()
        add_admin_log(user=current_user.username, actions='新建素材', client_ip=request.remote_addr,
                      results='成功')
        return redirect(url_for('manage.fc_info'))

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='新建素材', client_ip=request.remote_addr,
                      results=error[0])
    return render_template('manage/add_fc_content.html', form=form)


@login_required
def del_cf():
    cf_id = request.args.get('id', type=int)
    FriendCircle.query.filter_by(id=cf_id).delete()
    db.session.commit()
    add_admin_log(user=current_user.username, actions='删除朋友圈推广素材', client_ip=request.remote_addr, results='成功')
    return jsonify(code=0)


@login_required
def edit_cf_content():
    cf_id = request.args.get('id', type=int)
    form = EditFcContentForm()
    file_ser = current_app.config['FILE_SERVER']
    fc = FriendCircle.query.filter_by(id=cf_id).limit(1).first()
    old_picture1 = fc.picture1
    old_picture2 = fc.picture2
    old_picture3 = fc.picture3
    flag1 = 0
    flag2 = 0
    flag3 = 0
    app_dir1 = ''
    app_dir2 = ''
    app_dir3 = ''
    if form.validate_on_submit():
        content = form.content.data
        picture1 = request.files['picture1']
        picture2 = request.files['picture2']
        picture3 = request.files['picture3']
        status1 = form.status1.data
        status2 = form.status2.data
        status3 = form.status3.data
        if status1 == 0:
            fc.picture1 = ''
            flag1 = 1
            app_dir1 = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], "friend_circle")
        if status2 == 0:
            fc.picture2 = ''
            flag2 = 1
            app_dir2 = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], "friend_circle")
        if status3 == 0:
            fc.picture3 = ''
            flag3 = 1
            app_dir3 = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], "friend_circle")

        if picture1:
            file_name = secure_filename(picture1.filename)
            if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', picture1.filename.rsplit('.', 1)[0])):
                flash('宣传图片1名称不能为纯汉字')
                add_admin_log(user=current_user.username, actions='编辑素材', client_ip=request.remote_addr,
                              results='宣传图片1名称不能为纯汉字')
                return redirect(url_for('manage.edit_cf_content', id=cf_id))
            size = len(picture1.read())
            if size > 204800:
                flash("宣传图片1大小不能超过200KB")
                add_admin_log(user=current_user.username, actions='编辑素材',
                              client_ip=request.remote_addr, results='宣传图片1大小不能超过200KB')
                return redirect(url_for('manage.edit_cf_content', id=cf_id))

            app_dir1 = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], "friend_circle")
            file_url = os.path.join(current_app.config['PHOTO_TAG'], "friend_circle")
            if not os.path.exists(app_dir1):
                os.mkdir(app_dir1)
            im = Image.open(picture1)
            new_name = str(int(time.time() * 10000)) + '.' + file_name.rsplit('.', 1)[1]
            fc.picture1 = os.path.join(file_url, new_name)
            im.save(os.path.join(app_dir1, new_name))
            flag1 = 1
        if picture2:
            file_name = secure_filename(picture2.filename)
            if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', picture2.filename.rsplit('.', 1)[0])):
                flash('宣传图片2名称不能为纯汉字')
                add_admin_log(user=current_user.username, actions='编辑素材', client_ip=request.remote_addr,
                              results='宣传图片2名称不能为纯汉字')
                return redirect(url_for('manage.edit_cf_content', id=cf_id))

            size = len(picture2.read())
            if size > 204800:
                flash("宣传图片2大小不能超过200KB")
                add_admin_log(user=current_user.username, actions='编辑素材',
                              client_ip=request.remote_addr, results='宣传图片2大小不能超过200KB')
                return redirect(url_for('manage.edit_cf_content', id=cf_id))

            app_dir2 = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], "friend_circle")
            file_url = os.path.join(current_app.config['PHOTO_TAG'], "friend_circle")
            if not os.path.exists(app_dir2):
                os.mkdir(app_dir2)
            im = Image.open(picture2)
            new_name = str(int(time.time() * 10000)) + '.' + file_name.rsplit('.', 1)[1]
            fc.picture2 = os.path.join(file_url, new_name)
            im.save(os.path.join(app_dir2, new_name))
            flag2 = 1
        if picture3:
            file_name = secure_filename(picture3.filename)
            if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', picture3.filename.rsplit('.', 1)[0])):
                flash('宣传图片3名称不能为纯汉字')
                add_admin_log(user=current_user.username, actions='编辑素材', client_ip=request.remote_addr,
                              results='宣传图片3名称不能为纯汉字')
                return redirect(url_for('manage.edit_cf_content', id=cf_id))

            size = len(picture3.read())
            if size > 204800:
                flash("宣传图片3大小不能超过200KB")
                add_admin_log(user=current_user.username, actions='编辑素材',
                              client_ip=request.remote_addr, results='宣传图片3大小不能超过200KB')
                return redirect(url_for('manage.edit_cf_content', id=cf_id))

            app_dir3 = os.path.join(os.getcwd(), current_app.config['PHOTO_TAG'], "friend_circle")
            file_url = os.path.join(current_app.config['PHOTO_TAG'], "friend_circle")
            if not os.path.exists(app_dir3):
                os.mkdir(app_dir3)
            im = Image.open(picture3)
            new_name = str(int(time.time() * 10000)) + '.' + file_name.rsplit('.', 1)[1]
            fc.picture3 = os.path.join(file_url, new_name)
            im.save(os.path.join(app_dir3, new_name))
            flag3 = 1
        fc.content = content
        try:
            db.session.add(fc)
            db.session.commit()
            if flag1 and len(old_picture1) > 4 and os.path.exists(app_dir1) and os.path.isfile(old_picture1):
                print(33333)
                os.remove(old_picture1)
            if flag2 and len(old_picture2) > 4 and os.path.exists(app_dir2) and os.path.isfile(old_picture2):
                os.remove(old_picture2)
            if flag3 and len(old_picture1) > 4 and os.path.exists(app_dir3) and os.path.isfile(old_picture1):
                os.remove(old_picture3)
            add_admin_log(user=current_user.username, actions='编辑素材', client_ip=request.remote_addr, results='成功')
            return redirect(url_for('manage.fc_info'))
        except Exception as e:
            print(e)
            db.session.rollback()
            if flag1 and len(app_dir1) > 4 and os.path.exists(app_dir1) and os.path.isfile(app_dir1):
                os.remove(app_dir1)
            if flag2 and len(app_dir2) > 4 and os.path.exists(app_dir2) and os.path.isfile(app_dir2):
                os.remove(app_dir2)
            if flag3 and len(app_dir3) > 4 and os.path.exists(app_dir3) and os.path.isfile(app_dir3):
                os.remove(app_dir3)
            flash('操作数据错误')

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='编辑素材', client_ip=request.remote_addr,
                      results=error[0])
    if fc is not None:
        form.content.data = fc.content
        form.picture1.data = fc.picture1
        form.picture2.data = fc.picture2
        form.picture3.data = fc.picture3
        add_admin_log(user=current_user.username, actions='编辑素材', client_ip=request.remote_addr,
                      results='编辑素材成功')

    return render_template('manage/edit_fc_content.html', form=form, file_ser=file_ser, id=cf_id,
                           picture1=fc.picture1, picture2=fc.picture2, picture3=fc.picture3)


@login_required
def money_check():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    status = request.args.get('status')
    if status:
        godin_id = request.args.get('godin_id')
        if status == "1":
            # 提现成功
            wd_check = WithdrawCheck.query.filter_by(godin_id=godin_id, status=0).first()
            wd_check.status = 1
            wd_check.check_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            wd_check.operator = current_user.username
            db.session.add(wd_check)
            flash("已完成")
        else:
            wd_check = WithdrawCheck.query.filter_by(godin_id=godin_id, status=0).first()
            wd_check.status = 2
            wd_check.check_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            wd_check.operator = current_user.username
            db.session.add(wd_check)

            user = UserGeneralize.query.filter_by(godin_id=godin_id).first()
            user.account_balance += wd_check.withdraw
            db.session.add(user)
            flash("已驳回")
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
        return redirect(url_for('manage.money_check'))

    form = PhoneForm()
    query = WithdrawCheck.query.order_by(WithdrawCheck.status.asc())
    if form.validate_on_submit():
        phone_num = form.phone_num.data.strip()
    else:
        phone_num = request.args.get('phone_num')
    if phone_num is not None:
        form.phone_num.data = phone_num
        if form.phone_num.data != '':
            query = query.filter(WithdrawCheck.phone_num.like('%' + form.phone_num.data + '%'))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    for field, error in form.errors.items():
        flash(error[0])
        break

    for item in pagination.items:
        item.award = deal_float(item.award / 100)
        item.account_balance = deal_float(item.account_balance / 100)
        item.withdraw = deal_float(item.withdraw / 100)

    return render_template('manage/money_check.html', form=form, data=pagination.items, pagination=pagination,
                           page=page, per_page=per_page)


# 商业智能报告
@login_required
def add_bi_protocol():
    form = BIProtocolForm()
    protocol = ServiceProtocol.query.filter_by(category=3).first()
    if form.validate_on_submit():
        content = form.content.data
        if protocol is not None:
            service_protocol = ServiceProtocol.query.filter_by(category=3).first()
            service_protocol.content = content
            service_protocol.category = 3
        else:
            service_protocol = ServiceProtocol()
            service_protocol.content = content
            service_protocol.category = 3

        db.session.add(service_protocol)
        db.session.commit()

        add_admin_log(user=current_user.username, actions='添加服务条款', client_ip=request.remote_addr,
                      results='成功')
        flash('服务条款成功')
        return redirect(url_for('manage.add_bi_protocol'))

    if protocol is not None:
        form.content.data = protocol.content
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='添加服务条款', client_ip=request.remote_addr,
                      results='失败')
    add_admin_log(user=current_user.username, actions='添加服务条款', client_ip=request.remote_addr, results='成功')
    return render_template("manage/bi_protocol.html", form=form)


@login_required
def every_wash():
    # 微店铺跳转链接
    form = EveryWashForm()
    if request.method == "GET":
        link = cache.get('every_wash')
        if link:
            form.link.data = link
            return render_template("manage/every_wash.html", form=form)
        else:
            record = db.session.query(KeyValue).filter_by(key="every_wash").limit(1).first()
            if not record:
                key_value = KeyValue(
                    key="every_wash"
                )
                db.session.add(key_value)
                db.session.commit()
            else:
                form.link.data = record.value
                cache.set('every_wash', record.value, timeout=12 * 60 * 60)

    if form.validate_on_submit():
        link = form.link.data.strip()
        record = db.session.query(KeyValue).filter_by(key="every_wash").limit(1).first()
        record.value = link
        db.session.add(record)
        db.session.commit()
        cache.set('every_wash', link, timeout=12 * 60 * 60)
        flash("添加成功")
    for field, error in form.errors.items():
        flash(error[0])
        break
    return render_template("manage/every_wash.html", form=form)


@login_required
def add_privacy_protocol():
    form = PrivacyProtocolForm()
    protocol = ServiceProtocol.query.filter_by(category=3).first()
    if form.validate_on_submit():
        content = form.content.data
        if protocol is not None:
            service_protocol = ServiceProtocol.query.filter_by(category=3).first()
            service_protocol.content = content
            service_protocol.category = 3
        else:
            service_protocol = ServiceProtocol()
            service_protocol.content = content
            service_protocol.category = 3

        db.session.add(service_protocol)
        db.session.commit()
        add_admin_log(user=current_user.username, actions='添加微商指数隐私协议', client_ip=request.remote_addr,
                      results='成功')
        flash('添加成功')
        return redirect(url_for('manage.add_privacy_protocol'))
    if protocol is not None:
        form.content.data = protocol.content
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
        add_admin_log(user=current_user.username, actions='添加微商指数隐私协议', client_ip=request.remote_addr,
                      results='失败')
    add_admin_log(user=current_user.username, actions='添加微商指数隐私协议', client_ip=request.remote_addr, results='成功')
    return render_template("manage/privacy_protocol.html", form=form)


@login_required
def alter_balance():
    phone_num = request.args.get("phone_num", "")
    balance = request.args.get("balance", "")
    form = AlterBalanceForm()
    if request.method == "GET":
        form.balance.data = float(balance)
        form.phone_num.data = phone_num
    if form.validate_on_submit():
        alt_bal = AlterBalance()
        alt_bal.phone_num = form.phone_num.data
        alt_bal.create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alt_bal.type = form.type.data
        alt_bal.amount = form.amount.data
        alt_bal.operator = current_user.username
        alt_bal.comment = form.comment.data
        db.session.add(alt_bal)
        user = UserGeneralize.query.filter_by(phone_num=form.phone_num.data).limit(1).first()
        if form.type.data == 0:
            user.account_balance += int(form.amount.data) * 100
        else:
            user.account_balance -= int(form.amount.data) * 100
        try:
            db.session.commit()
            flash("修改成功")
        except Exception as e:
            db.session.rollback()
            flash("修改失败，请稍后再试")
        return redirect(url_for("manage.generalize_data"))
    for field, error in form.errors.items():
        flash(error[0])
        break
    return render_template('manage/alter_balance.html', form=form)


@login_required
def alter_detail():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    phone_num = request.args.get("phone_num", "")
    pagination = AlterBalance.query.filter_by(phone_num=phone_num).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('manage/alter_detail.html', data=pagination.items, pagination=pagination,
                           page=page, per_page=per_page, phone_num=phone_num)


@login_required
def delete_detail():
    id = request.args.get('id')
    notice = SysNotice.query.filter_by(id=id).first()
    if notice:
        db.session.delete(notice)
        db.session.commit()
        flash("删除成功")
    else:
        flash("删除失败，请稍后重试")
    return redirect(url_for("manage.get_notice_info"))


@celery.task(name='make_log_print')
def make_log_print():
    today = datetime.datetime.now().strftime('%Y%m%d')
    statistics_dir = os.path.join(os.getcwd(), current_app.config['INVITE_SHARE_TAG'], today)
    if not os.path.exists(statistics_dir):
        os.makedirs(statistics_dir)
    file_name = os.path.join(statistics_dir, today + '.txt')
    if os.path.exists(file_name):
        fp = open(file_name, 'a', encoding='utf8')
    else:
        fp = open(file_name, 'w', encoding='utf8')
    all_data = redis.lrange('invite_share_log', 0, -1)
    redis.ltrim('invite_share_log', len(all_data), -1)

    for data in all_data:
        data = eval(str(data, encoding='utf-8'))
        fp.write('%s\n' % ({'event': data['event'], 'args': data['args'], 'time': data['time'], 'ip': data['ip']}))
    fp.close()


@celery.task(name='make_log_print_yes')
def make_log_print_yes():
    yes = datetime.datetime.now() - datetime.timedelta(days=1)
    yesterday = yes.strftime('%Y%m%d')
    statistics_dir = os.path.join(os.getcwd(), current_app.config['INVITE_SHARE_TAG'], yesterday)
    if not os.path.exists(statistics_dir):
        os.makedirs(statistics_dir)
    file_name = os.path.join(statistics_dir, yesterday + '.txt')
    if os.path.exists(file_name):
        fp = open(file_name, 'a', encoding='utf8')
    else:
        fp = open(file_name, 'w', encoding='utf8')
    all_data = redis.lrange('invite_share_log', 0, -1)
    redis.ltrim('invite_share_log', len(all_data), -1)

    for data in all_data:
        data = eval(str(data, encoding='utf-8'))
        fp.write('%s\n' % ({'event': data['event'], 'args': data['args'], 'time': data['time'], 'ip': data['ip']}))

    # 获取前一天的总邀请人数
    start_time = yes.strftime('%Y-%m-%d') + " 00:00:00"
    end_time = yes.strftime('%Y-%m-%d') + " 23:59:59"
    start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

    invite_info = InviteInfo.query.with_entities(func.count(InviteInfo.id)).filter(InviteInfo.create_time.between(
                    start_time, end_time)).first()
    if invite_info:
        fp.write('%s\n' % ({'event': "new_add_person", 'args': invite_info[0], 'time': "", 'ip': ""}))
    fp.close()


@login_required
def function_hot_dot():
    # 功能小红点
    show_id = request.values.get('show_id', None)
    if show_id:
        hot_dot = FunctionHotDot.query.get_or_404(show_id)
        if hot_dot.tomorrow_status == 0:
            hot_dot.tomorrow_status = 1
        else:
            hot_dot.tomorrow_status = 0
        db.session.add(hot_dot)
        try:
            db.session.commit()
            return jsonify({"statuscode": "0000"})
        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify({"statuscode": "0001"})

    page = request.args.get('page', 1, type=int)
    per_page = 50
    form = FunctionHotDotForm()
    query = FunctionHotDot.query
    if form.validate_on_submit():
        function_name = form.function_name.data
        function_locate = form.function_locate.data
    else:
        function_name = request.args.get("function_name")
        function_locate = request.args.get("function_locate")

    if function_name is not None:
        form.function_name.data = function_name
        if form.function_name.data != '':
            query = query.filter(FunctionHotDot.function_name.like('%' + form.function_name.data + '%'))

    if function_locate is not None:
        form.function_locate.data = function_locate
        if form.function_locate.data != '' and form.function_locate.data != -1:
            query = query.filter_by(type=form.function_locate.data)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    for field, error in form.errors.items():
        flash(error[0])
        break
    return render_template("manage/function_hot_dot.html", form=form, pagination=pagination, data=pagination.items,
                           page=page, per_page=per_page)


@celery.task(name='update_hot_dot')
def update_hot_dot():
    all_data = FunctionHotDot.query.all()
    for item in all_data:
        item.today_status = item.tomorrow_status
        item.tomorrow_status = 0
        db.session.add(item)
    db.session.commit()


@login_required
def master_get_function_video():
    # request.args.get只能获取到 get 请求的参数
    function_name = request.args.get("function_name")
    search_keyword = function_name  # 记录当前的搜索关键字
    page = request.args.get('page', 1, type=int)
    video_server = current_app.config['FILE_SERVER'] + current_app.config["UPLOAD_VIDEO_PATH"]
    form = FunctionVideoForm()
    if function_name:
        form.function_name.data = function_name
        pagination = MasterFunctionVideo.query.filter(MasterFunctionVideo.function_name.like('%{0}%'.format(
            function_name))).paginate(page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
        data = pagination.items

        return render_template('manage/master_get_function_video.html', form=form, all_video=data,
                               pagination=pagination, search_keyword=search_keyword, video_server=video_server)

    if form.validate_on_submit():
        function_name = form.function_name.data.strip()
        search_keyword = function_name  # 点击搜索时记录当前搜索关键字，后续做删除操作之后继续保持之前的查询状态
        if len(function_name) == 0:
            flash("无查询结果")
            return render_template('manage/master_get_function_video.html', form=form, pagination=None, search_keyword=search_keyword, video_server=video_server)

        pagination = FunctionVideo.query.filter(FunctionVideo.function_name.like('%{0}%'.format(function_name))).paginate(
                              page=page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
        data = pagination.items
        if pagination.total == 0:
            flash("无查询结果")
        return render_template('manage/master_get_function_video.html', form=form, all_video=data, pagination=pagination,
                               search_keyword=search_keyword, video_server=video_server)
    for field, error in form.errors.items():
        flash(error[0])

    pagination = MasterFunctionVideo.query.paginate(page=page,
                                              per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    data = pagination.items
    return render_template('manage/master_get_function_video.html', form=form, all_video=data,
                           pagination=pagination, search_keyword=search_keyword, video_server=video_server)


@login_required
def master_add_function_video():
    form = AddVideoForm()
    if form.validate_on_submit():

        data = MasterFunctionVideo.query.filter_by(function_name=form.function_name.data.strip()).limit(1).first()
        if data:
            flash("不能添加已存在的功能介绍!")
            return redirect(url_for("manage.master_add_function_video"))

        video_url = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + ".mp4"
        path = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

        dir_path = path + "/" + current_app.config['UPLOAD_VIDEO_PATH']
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        form.video_url.data.save(dir_path + video_url)

        video = MasterFunctionVideo(
            function_name=form.function_name.data.strip(),
            video_url=video_url,
            comment=form.comment.data,
            last_operator=current_user.username
        )
        db.session.add(video)
        db.session.commit()
        flash("添加成功")
        return redirect(url_for("manage.master_get_function_video", function_name=form.function_name.data.strip()))
    for field, error in form.errors.items():
        flash(error[0])
        break
    return render_template("manage/master_add_function_video.html", form=form)


@login_required
def master_del_function_video():
    id = request.args.get("id")
    search_keyword = request.args.get("search_keyword")
    video = MasterFunctionVideo.query.get_or_404(id)
    path = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    complete_path = os.path.join(path, current_app.config['UPLOAD_VIDEO_PATH'], video.video_url)
    os.remove(complete_path)
    db.session.delete(video)
    db.session.commit()
    flash("删除成功")
    return redirect(url_for("manage.master_get_function_video", function_name=search_keyword))


@login_required
def master_edit_function_video():
    form = EditVideoForm()
    id = request.args.get("id")
    video = MasterFunctionVideo.query.get_or_404(id)
    if request.method == "GET":
        form.function_name.data = video.function_name
        form.comment.data = video.comment
    if form.validate_on_submit():

        record = MasterFunctionVideo.query.filter_by(function_name=form.function_name.data.strip()).count()
        if video.function_name != form.function_name.data.strip() and record:
            flash("不能添加已存在的功能介绍!")
            form.function_name.data = form.function_name.data.strip()
            return render_template("manage/edit_function_video.html", form=form, id=id)

        if form.video_url.data.filename != "":  # 如果文件名不为空则说明用户新上传了文件
            video_url = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + ".mp4"
            path = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
            dir_path = path + "/" + current_app.config['UPLOAD_VIDEO_PATH']
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            # 删除原来保存的视频并添加新的视频
            os.remove(dir_path + video.video_url)
            form.video_url.data.save(dir_path + video_url)
            video.video_url = video_url

        video.function_name = form.function_name.data.strip()
        video.comment = form.comment.data.strip()
        video.last_operator = current_user.username
        db.session.add(video)
        db.session.commit()
        flash("提交成功")
        return redirect(url_for("manage.master_get_function_video", function_name=video.function_name))
    for field, error in form.errors.items():
        flash(error[0])
        break
    return render_template("manage/master_edit_function_video.html", form=form, id=id)


@login_required
def alter_divide():
    channel_id = request.args.get("channel_id", "")
    channel_name = request.args.get("channel_name", "")
    all_divide = request.args.get("all_divide", "")
    form = AlterDivideForm()
    if request.method == "GET":
        form.channel_id.data = channel_id
        form.channel_name.data = channel_name
        form.all_divide.data = float(all_divide)
    if form.validate_on_submit():
        alt_div = AlterDivide()
        alt_div.channel_id = form.channel_id.data
        alt_div.channel_name = form.channel_name.data
        alt_div.create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alt_div.type = form.type.data
        alt_div.amount = form.amount.data
        alt_div.operator = current_user.username
        alt_div.comment = form.comment.data
        db.session.add(alt_div)
        channel_account = ChannelAccount.query.filter_by(channel_id=form.channel_id.data).first_or_404()
        wallet = Wallet.query.filter_by(channel_account_id=channel_account.id).limit(1).first()
        if form.type.data == 0:
            wallet.all_divide += int(form.amount.data)
        else:
            wallet.all_divide -= int(form.amount.data)
        try:
            db.session.commit()
            flash("修改成功")
        except Exception as e:
            db.session.rollback()
            flash("修改失败，请稍后再试")
        return redirect(url_for("manage.get_channel_data"))
    for field, error in form.errors.items():
        flash(error[0])
        break
    return render_template('manage/alter_divide.html', form=form)


@login_required
def alter_divide_detail():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    channel_id = request.args.get("channel_id", "")
    pagination = AlterDivide.query.filter_by(channel_id=channel_id).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('manage/alter_divide_detail.html', data=pagination.items, pagination=pagination,
                           page=page, per_page=per_page, channel_id=channel_id)


@celery.task(name='delete_expire_video')
def delete_expire_video():
    before_time = datetime.datetime.now() - datetime.timedelta(days=3)
    all_data = UploadVoice.query.filter(UploadVoice.create_time < before_time).all()
    for item in all_data:
        db.session.delete(item)
        # 同时删除音频文件
        basedir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
        file_dir = os.path.join(basedir, "share/static/images/voice", item.voice_name)
        try:
            os.remove(file_dir)
        except Exception:
            pass
    db.session.commit()


@login_required
def get_pay_time():
    form = UserPayTimeForm()
    query = UserPayTime.query.filter_by(status=0).order_by(UserPayTime.pay_time.desc())
    if form.validate_on_submit():
        phone_num = form.phone_num.data
        start_time = form.start_time.data
        end_time = form.end_time.data
    else:
        phone_num = request.args.get('phone_num')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    if phone_num is not None:
        form.phone_num.data = phone_num
        if form.phone_num.data != '':
            query = query.filter(UserPayTime.phone_num.like(form.phone_num.data + '%'))

    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
        query = query.filter(UserPayTime.pay_time.between(form.start_time.data, form.end_time.data))
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    for field, error in form.errors.items():
        flash(error[0])
        break

    return render_template("manage/user_pay_time.html", form=form, data=pagination.items, page=page, per_page=per_page,
                           pagination=pagination)


@login_required
def get_vip_pay_time():
    form = UserPayTimeForm()
    query = UserPayTime.query.filter_by(status=1).order_by(UserPayTime.pay_time.desc())
    if form.validate_on_submit():
        phone_num = form.phone_num.data
        start_time = form.start_time.data
        end_time = form.end_time.data
    else:
        phone_num = request.args.get('phone_num')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is not None and end_time is not None:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    if phone_num is not None:
        form.phone_num.data = phone_num
        if form.phone_num.data != '':
            query = query.filter(UserPayTime.phone_num.like(form.phone_num.data + '%'))

    if start_time is not None and end_time is not None:
        form.start_time.data = start_time
        form.end_time.data = end_time
        query = query.filter(UserPayTime.pay_time.between(form.start_time.data, form.end_time.data))
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORDS_PER_PAGE']
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    for field, error in form.errors.items():
        flash(error[0])
        break

    return render_template("manage/user_vip_pay_time.html", form=form, data=pagination.items, page=page, per_page=per_page,
                           pagination=pagination)


@login_required
def appeal_edit():
    id = request.args.get('id', type=int)
    form = AppealEditForm()
    file_ser = current_app.config['FILE_SERVER']
    if not id:
        id = request.values.get('id', type=int)
        content = request.values.get('content')
        fb = FeedBack.query.get_or_404(id)
        fb.back_content = content
        fb.operator = current_user.username
        fb.status = 1
        fb.back_time = datetime.datetime.now()
        db.session.add(fb)
        try:
            db.session.commit()
            return jsonify({"code": "0"})
        except Exception as e:
            db.session.rollback()
            print(e)
            return jsonify({"code": "1"})

    fb = FeedBack.query.get_or_404(id)
    return render_template('manage/appeal_edit.html', form=form, file_ser=file_ser, fb=fb)


@login_required
def appeal_detail():
    id = request.args.get('id', type=int)
    file_ser = current_app.config['FILE_SERVER']
    fb = FeedBack.query.get_or_404(id)
    return render_template('manage/appeal_detail.html', file_ser=file_ser, fb=fb)

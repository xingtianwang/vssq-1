#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: views.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 2016/10/17
# *************************************************************************
import datetime
import hashlib
import os

from flask import current_app
from flask import jsonify
from flask import render_template
from flask import request
from flask import url_for
from sqlalchemy import func, distinct
from sqlalchemy.sql import label
from werkzeug.utils import redirect

from app import db, cache
from app.api_1_0.models import AppVersion, UserInfo, SignData, Activity, ChannelVersion, ServiceProtocol, \
    BiReportProtocol, BiReport, BiMonthReport, UserGeneralize, GodinAccount, FriendCircle, InviteInfo, InviteEarnRecord, \
    MemberEarnRecord, SysNotice, FeedBack
from app.api_1_0.utils import deal_float
from app.api_1_0.utils import log_print
from app.manage.helper import get_pay_person_num
from app.manage.models import SpreadManager, KeyValue, WithdrawCheck
from app.share import share


@share.route('/download', methods=['GET'])
@share.route('/download/<string:suffix>', methods=['GET'])
def get_latest_version(suffix='VSSQ'):
    # print('*****get_latest_version*****')
    spread_info = SpreadManager.query.filter_by(url_suffix=suffix).first()
    if spread_info is not None:
        data = ChannelVersion.query.filter_by(app_type=8).filter_by(spread_id=spread_info.id).\
            filter_by(is_released=True).order_by(ChannelVersion.version_code.desc()).first()
    else:
        data = None
    res = {}
    if data is None:
        res['version_name'] = 'None'
        res['app_size'] = 0
        res['release_time'] = '0000-00-00'
        res['app_dir'] = '#'
    else:
        res['version_name'] = data.version_name
        res['app_size'] = data.app_size//10000/100
        res['release_time'] = data.release_time
        res['app_dir'] = current_app.config['FILE_SERVER'] + data.app_dir
    qr_code_name = 'QR_CODE_IMAGE'
    if suffix != 'VSSQ':
        qr_code_name += '_' + suffix.upper()
        res['channel'] = suffix
        res['qr_code'] = ''
        return render_template("share/channeldownload.html", data=res)
    res['qr_code'] = current_app.config[qr_code_name]
    return render_template("share/download.html", data=res)


@share.route('/activity_share', methods=['GET'])
@share.route('/activity_share/<string:godin_id>', methods=['GET'])
def activity_share(godin_id='1'):

    user = UserInfo.query.filter_by(godin_id=godin_id).first()
    if user is not None:
        share_code = user.share_code
    else:
        share_code = None
    return render_template("share/share.html", share_code=share_code)


@share.route('/activity_load', methods=['GET'])
@share.route('/activity_load/<string:godin_id>', methods=['GET'])
def activity_load(godin_id='1'):
    user = UserInfo.query.filter_by(godin_id=godin_id).first()
    if user is not None:
        share_code = user.share_code
    else:
        share_code = None
    spread_info = SpreadManager.query.filter_by(url_suffix=1).first()
    if spread_info is not None:
        data = AppVersion.query.filter_by(app_type=4).filter_by(spread_id=spread_info.id). \
            filter_by(is_released=True).order_by(AppVersion.version_code.desc()).first()
    else:
        data = None
    if data is None:
        load_url = "#"
    else:
        load_url = current_app.config['FILE_SERVER'] + data.app_dir
    return render_template("share/xfen-load.html", share_code=share_code, load_url=load_url)


@share.route('/activity_prize', methods=['GET'])
def activity_prize():
    return render_template('share/winner-list.html')


@share.route('/channel_share', methods=['GET'])
@share.route('/channel_share/<string:godin_id>', methods=['GET'])
def channel_share(godin_id='1'):

    user = UserInfo.query.filter_by(godin_id=godin_id).first()
    if user is not None:
        share_code = user.share_code
    else:
        share_code = None
    return render_template("share/take-part.html", share_code=share_code)


@share.route('/channel_load', methods=['GET'])
@share.route('/channel_load/<string:godin_id>', methods=['GET'])
def channel_load(godin_id='1'):
    user = UserInfo.query.filter_by(godin_id=godin_id).first()
    if user is not None:
        share_code = user.share_code
    else:
        share_code = None
    spread_info = SpreadManager.query.filter_by(url_suffix='tuijianyoujiang').first()
    if spread_info is not None:
        data = AppVersion.query.filter_by(app_type=4).filter_by(spread_id=spread_info.id). \
            filter_by(is_released=True).order_by(AppVersion.version_code.desc()).first()
    else:
        data = None
    if data is None:
        load_url = "#"
    else:
        load_url = current_app.config['FILE_SERVER'] + data.app_dir
    return render_template("share/xfen-qd-load.html", share_code=share_code, load_url=load_url)


@share.route('/invite', methods=['GET'])
@share.route('/invite/<string:godin_id>', methods=['GET'])
def invite(godin_id='1'):
    user = UserInfo.query.filter_by(godin_id=godin_id).first()
    if user is not None:
        share_code = user.share_code
    else:
        share_code = None
    return render_template("invit/wskyqhy.html", share_code=share_code)


@share.route('/load_app', methods=['GET'])
@share.route('/load_app/<string:godin_id>', methods=['GET'])
def load_app(godin_id='1'):
    user = UserInfo.query.filter_by(godin_id=godin_id).first()
    if user is not None:
        share_code = user.share_code
    else:
        share_code = None
    return render_template("invit/wskjsyq.html", share_code=share_code)


# 签到活动页面
@share.route('/sa/<string:godin_id>', methods=['GET'])
def sa(godin_id):
    base_ser = current_app.config['FILE_SERVER']
    scount = 0
    info = ''
    flag_s = 0
    current_time = datetime.datetime.now().date()
    activity_info = Activity.query.filter(Activity.number == '000003', Activity.status == 1).first()
    if activity_info is not None:
        icon = ''
        if len(activity_info.icon) > 4:
            icon = base_ser + activity_info.icon
        sign_info = SignData.query.filter(SignData.activity_id == activity_info.id,
                                          SignData.number == activity_info.number,
                                          SignData.sign_godin_id == godin_id).first()
        if sign_info is not None:
            last_sign_time = sign_info.last_sign_time
            if sign_info is not None and last_sign_time + datetime.timedelta(days=1) == current_time:
                scount = sign_info.sign_count
            elif sign_info is not None and last_sign_time == current_time:
                scount = sign_info.sign_count
                flag_s = 1
            else:
                scount = 0
        info = {'activity_id': activity_info.id, 'name': activity_info.name, 'number': activity_info.number,
                'icon': icon, 'link': activity_info.link, 'content': activity_info.content,
                'award_period': activity_info.award_period, 'reward': activity_info.reward}
    return render_template("activity/signIn.html", data=info, godin_id=godin_id, ev='100004', scount=scount,
                           flag_s=flag_s)


@share.route('/v_load', methods=['GET'])
@share.route('/v_load/<string:suffix>', methods=['GET'])
def v_load(suffix='VSSQ'):
    # print('*****get_latest_version*****')
    spread_info = SpreadManager.query.filter_by(url_suffix=suffix).first()
    if spread_info is not None:
        data = ChannelVersion.query.filter_by(app_type=8).filter_by(spread_id=spread_info.id).\
            filter_by(is_released=True).order_by(ChannelVersion.version_code.desc()).first()
    else:
        data = None
    if data is None:
        app_dir = '#'
    else:
        app_dir = current_app.config['FILE_SERVER'] + data.app_dir
    return render_template("load/vLoad.html", app_dir=app_dir)


@share.route('/k_act', methods=['GET'])
def k_act():
    return render_template('activity/guestActivity.html')


@share.route('/frame_ad', methods=['GET'])
def frame_ad():
    flag_id = request.args.get('flag_id')
    data = 'g2451894827,zjy1683117560,qxzbbqx888,zh2015091011,Z010905y,hy19921215ll,yuan654652,yu1426150342,zth20011105,al702323'
    sys_notice = SysNotice.query.filter_by(flag_id=flag_id).limit(1).first()
    if sys_notice:
        data = sys_notice.wx
    return render_template('frame_ad/join.html', data=data)


@share.route('/bi_index', methods=['GET'])
def bi_index():
    we_id = request.args.get('id')
    report = BiReportProtocol.query.filter_by(we_id=we_id, status=1).first()
    video_server = current_app.config['FILE_SERVER'] + current_app.config["IMAGE_PATH"]
    if report is not None:
        report_info = BiReport.query.order_by(BiReport.create_time.desc()).filter(BiReport.we_id == we_id).first()
        if report_info is None:
            return render_template("business/report-empty.html", id=we_id)
        else:
            year = report_info.record_time[0:4]
            month = report_info.record_time[4:6]
            day = report_info.record_time[6:]
            return render_template("business/report.html", id=we_id, report=report_info, year=year, month=month,
                                   day=day, video_server=video_server)
    else:
        return redirect(url_for('share.agree', id=we_id))


@share.route('/agree', methods=['GET'])
def agree():
    we_id = request.args.get('id')
    report = BiReportProtocol.query.filter_by(we_id=we_id, status=1).first()
    if report is not None:
        return render_template("business/report-empty.html", id=we_id)

    content = ''
    protocol = ServiceProtocol.query.filter_by(category=3).first()
    if protocol is not None:
        content = protocol.content
    return render_template("business/serviceTrems.html", content=content, id=we_id)


@share.route('/bireport', methods=['GET'])
def bireport():
    we_id = request.args.get('id')
    report = BiReportProtocol.query.filter_by(we_id=we_id, status=1).limit(1).first()
    video_server = current_app.config['FILE_SERVER'] + current_app.config["IMAGE_PATH"]
    if report is None:
        report = BiReportProtocol()
        report.we_id = we_id
        report.status = 1
        db.session.add(report)
        db.session.commit()
        return render_template("business/report-empty.html", we_id=we_id)
    else:
        report = BiReport.query.order_by(BiReport.id.desc()).filter(BiReport.we_id == we_id).limit(1).first()
        if report is not None:
            year = report.record_time[0:4]
            month = report.record_time[4:6]
            day = report.record_time[6:]
        else:
            return render_template("business/report-empty.html", we_id=we_id)

        return render_template("business/report.html", id=we_id, report=report, year=year, month=month, day=day,
                               video_server=video_server)


@share.route('/bireport_detail', methods=['GET'])
def bireport_detail():
    we_id = request.args.get('id')
    t_data = {'0': 'extend_work_heat', '1': 'latent_consumer_index', '2': 'activite_consumer_index',
              '3': 'sale_work_heat', '4': 'income_index', '5': 'pay_index'}
    c_type = request.args.get('c_type')
    time_type = request.args.get('time_type')
    if c_type is None:
        c_type = '0'
    if time_type is None:
        time_type = '0'
    t_dic = []
    if time_type == '0':
        query = BiReport.query.order_by(BiReport.create_time.desc()).filter_by(we_id=we_id).limit(7)
        for report in query:
            dev = eval('report.%s' % t_data[c_type])
            data = {'time': report.record_time, 'value': dev}
            t_dic.append(data)
    elif time_type == '1':
        query = BiReport.query.order_by(BiReport.create_time.desc()).filter_by(we_id=we_id).limit(30)
        for report in query:
            dev = eval('report.%s' % t_data[c_type])
            data = {'time': report.record_time, 'value': dev}
            t_dic.append(data)
    elif time_type == '2':
        query = BiMonthReport.query.order_by(BiMonthReport.create_time.desc()).filter_by(we_id=we_id).limit(3)
        for report in query:
            dev = eval('report.%s' % t_data[c_type])
            data = {'time': str(report.year) + '-' + str(report.month), 'value': dev}
            t_dic.append(data)
    elif time_type == '3':
        query = BiMonthReport.query.order_by(BiMonthReport.create_time.desc()).filter_by(we_id=we_id).limit(6)
        for report in query:
            dev = eval('report.%s' % t_data[c_type])
            data = {'time': str(report.year) + '-' + str(report.month), 'value': dev}
            t_dic.append(data)
    elif time_type == '4':
        query = BiMonthReport.query.order_by(BiMonthReport.create_time.desc()).filter_by(we_id=we_id).limit(12)
        for report in query:
            dev = eval('report.%s' % t_data[c_type])
            data = {'time': str(report.year) + '-' + str(report.month), 'value': dev}
            t_dic.append(data)
    time_data = []
    value_data = []
    for data in t_dic:
        time_data.append(data['time'])
        value_data.append(data['value'])
    time_data.reverse()
    value_data.reverse()
    return render_template("business/details.html", id=we_id, t_dic=t_dic, c_type=c_type,
                           time_data=time_data, value_data=value_data)


@share.route('/bireport_select', methods=['GET'])
def bireport_select():
    we_id = request.args.get('id')
    t_data = {'0': 'extend_work_heat', '1': 'latent_consumer_index', '2': 'activite_consumer_index',
              '3': 'sale_work_heat', '4': 'income_index', '5': 'pay_index'}
    c_type = request.args.get('c_type')
    time_type = request.args.get('time_type')
    if c_type is None:
        c_type = '0'
    if time_type is None:
        time_type = '0'
    t_dic = []
    if time_type == '0':
        query = BiReport.query.order_by(BiReport.create_time.desc()).filter_by(we_id=we_id).limit(7)
        for report in query:
            dev = eval('report.%s' % t_data[c_type])
            data = {'time': report.record_time, 'value': dev}
            t_dic.append(data)
    elif time_type == '1':
        query = BiReport.query.order_by(BiReport.create_time.desc()).filter_by(we_id=we_id).limit(30)
        for report in query:
            dev = eval('report.%s' % t_data[c_type])
            data = {'time': report.record_time, 'value': dev}
            t_dic.append(data)
    elif time_type == '2':
        query = BiMonthReport.query.order_by(BiMonthReport.create_time.desc()).filter_by(we_id=we_id).limit(3)
        for report in query:
            dev = eval('report.%s' % t_data[c_type])
            data = {'time': str(report.year) + '-' + str(report.month), 'value': dev}
            t_dic.append(data)
    elif time_type == '3':
        query = BiMonthReport.query.order_by(BiMonthReport.create_time.desc()).filter_by(we_id=we_id).limit(6)
        for report in query:
            dev = eval('report.%s' % t_data[c_type])
            data = {'time': str(report.year) + '-' + str(report.month), 'value': dev}
            t_dic.append(data)
    elif time_type == '4':
        query = BiMonthReport.query.order_by(BiMonthReport.create_time.desc()).filter_by(we_id=we_id).limit(12)
        for report in query:
            dev = eval('report.%s' % t_data[c_type])
            data = {'time': str(report.year) + '-' + str(report.month), 'value': dev}
            t_dic.append(data)
    time_data = []
    value_data = []
    for data in t_dic:
        time_data.append(data['time'])
        value_data.append(data['value'])
    time_data.reverse()
    value_data.reverse()
    return jsonify(id=we_id, t_dic=t_dic, c_type=c_type, time_data=time_data, value_data=value_data)


@share.route('/generalize/<string:godin_id>', methods=['GET'])
def generalize(godin_id='1'):
    # 邀请链接页面
    user = UserGeneralize.query.filter_by(godin_id=godin_id).limit(1).first()
    domain_name = current_app.config["INVITE_LINK"]
    active_intro = cache.get('active_introduce')
    if not active_intro:
        record = db.session.query(ServiceProtocol).filter_by(category=10).limit(1).first()
        active_intro = record.content
        cache.set('active_introduce', active_intro, timeout=12 * 60 * 60)
    if user:
        pay_person_num = get_pay_person_num(godin_id)

        account_award = (user.member_award + user.active_code_award) / 100
        return render_template("share/generalize.html", link=domain_name + user.invite_link,
                               register_person_num=user.register_person_num,
                               pay_person_num=pay_person_num,
                               account_award=deal_float(account_award),
                               account_balance=deal_float(user.account_balance / 100), godin_id=godin_id, active_intro=active_intro)
    else:
        user_info = GodinAccount.query.filter_by(godin_id=godin_id).limit(1).first()
        if user_info:
            user = UserGeneralize(godin_id)
            user.phone_num = user_info.phone_num
            user.register_person_num = 0
            user.invite_person_num = 0
            user.pay_person_num = 0
            user.member_award = 0
            user.active_code_award = 0
            user.account_balance = 0
            db.session.add(user)
            db.session.commit()
            account_award = (user.member_award + user.active_code_award) / 100
            return render_template("share/generalize.html", link=domain_name + user.invite_link,
                                   register_person_num=user.register_person_num,
                                   pay_person_num=user.pay_person_num,
                                   account_award=deal_float(account_award),
                                   account_balance=deal_float(user.account_balance / 100), godin_id=godin_id, active_intro=active_intro)

    return render_template("share/generalize.html", link=domain_name,
                           register_person_num=0,
                           pay_person_num=0,
                           account_award=0,
                           account_balance=0, godin_id=godin_id, active_intro=active_intro)


@share.route('/withdraw', methods=['GET', "POST"])
def withdraw():
    # 提现页面
    godin_id = request.args.get('godin_id')
    money = request.values.get('money')
    if money:
        godin_id = request.values.get('godin_id').strip()
        zfb_account = request.values.get('zfb_account').strip()
        name = request.values.get('name').strip()
        # 判断当前用户是否有正在提现的记录
        record = WithdrawCheck.query.filter_by(godin_id=godin_id, status=0).first()
        if record:
            return jsonify({"statuscode": "0001"})
        # 将当前用户的余额减去提现金额
        user = UserGeneralize.query.filter_by(godin_id=godin_id).first()
        if not user:
            return jsonify({"statuscode": "0001"})
        user.account_balance -= int(float(money)) * 100
        with_draw = WithdrawCheck()
        with_draw.godin_id = godin_id
        with_draw.apply_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with_draw.phone_num = user.phone_num
        with_draw.withdraw = int(float(money)) * 100
        with_draw.zfb_account = zfb_account
        with_draw.name = name
        with_draw.status = 0
        with_draw.award = user.member_award + user.active_code_award
        with_draw.account_balance = user.account_balance

        db.session.add(user)
        db.session.add(with_draw)
        try:
            db.session.commit()
            return jsonify({"statuscode": "0000"})
        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify({"statuscode": "0002"})
    user = UserGeneralize.query.filter_by(godin_id=godin_id).limit(1).first()
    return render_template("share/withdraw.html", account_balance=deal_float(user.account_balance / 100), godin_id=godin_id)


@share.route('/earning', methods=['GET'])
def earning():
    # 收益记录
    godin_id = request.args.get('godin_id')
    record = GodinAccount.query.filter_by(godin_id=godin_id).limit(1).first()
    if not record:
        return render_template("share/earning.html", data=[], all_award=0, register_num=0,
                               member_num=0)
    # 获取总收益
    user = UserGeneralize.query.filter_by(godin_id=godin_id).first()
    all_award = (user.member_award + user.active_code_award) / 100
    # 获取购买会员人数
    member_earn = MemberEarnRecord.query.filter_by(godin_id=godin_id).with_entities(
        func.count(distinct(MemberEarnRecord.be_invited_phone))).first()

    member_num = 0
    if member_earn:
        member_num = member_earn[0]
    # 获取所有邀请人
    invite_info = InviteInfo.query.filter_by(inviter_godin_id=godin_id).all()
    data = []
    register_num = 0
    for info in invite_info:
        godin_account = GodinAccount.query.filter_by(godin_id=info.godin_id).limit(1).first()
        if godin_account:
            # 将注册人数加 1
            register_num += 1
            # 分别获取 key 收益和会员收益
            key_award = InviteEarnRecord.query.filter_by(be_invited_phone=info.phone_num).with_entities(label(
                'key_earn', func.sum(InviteEarnRecord.inviter_earn))).group_by(
                    InviteEarnRecord.be_invited_phone).first()

            member_award = MemberEarnRecord.query.filter_by(be_invited_phone=info.phone_num).with_entities(label(
                'member_award', func.sum(MemberEarnRecord.member_earn))).group_by(
                MemberEarnRecord.be_invited_phone).first()
            award = 0
            if key_award:
                if member_award:
                    award = key_award[0] + member_award[0]
                else:
                    award = key_award[0]
            else:
                if member_award:
                    award = member_award[0]
                else:
                    award = ""

            data.append({"phone_num": info.phone_num, "register_time": godin_account.create_time, "award": award})
        else:
            data.append({"phone_num": info.phone_num, "register_time": "", "award": ""})

    for item in data:
        if item["award"] != "":
            item["award"] = deal_float(item["award"] / 100)
    return render_template("share/earning.html", data=data, all_award=deal_float(all_award), register_num=register_num, member_num=member_num)


@share.route('/history/<string:godin_id>', methods=['GET'])
def history(godin_id='1'):
    # 提现记录
    records = WithdrawCheck.query.filter_by(godin_id=godin_id).order_by(WithdrawCheck.apply_time.desc()).all()
    for record in records:
        record.withdraw = deal_float(record.withdraw / 100)
    return render_template("share/history.html", records=records)


@share.route('/fc', methods=['GET'])
def fc():
    # 邀请素材
    link = request.args.get('link')
    godin_id = request.args.get('godin_id')
    photo_url = current_app.config['FILE_SERVER']
    query = FriendCircle.query.order_by(FriendCircle.create_time.desc())
    data = {}
    for item in query:
        attch = []
        if item.picture1:
            attch.append(photo_url + item.picture1)
        if item.picture2:
            attch.append(photo_url + item.picture2)
        if item.picture3:
            attch.append(photo_url + item.picture3)
        data[item.id] = attch
    return render_template("share/invite.html", link=link, query=query, photo_url=photo_url, data=data)


@share.route('/invite_url/<string:identity_id>')
def invite_url(identity_id="1"):
    identity_id = identity_id.strip()
    # 判断当前邀请链接是否对应某个用户
    UserGeneralize.query.filter_by(invite_link=identity_id).first_or_404()
    log_print("invite_url", identity_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    request.headers.get('X-Forwarded-For'))
    apk_path = cache.get("TGZQ_apk_path")
    if not apk_path:
        # 如果没有缓存，则去数据库获取
        key_value = KeyValue.query.filter_by(key="TGZQ_apk_path").limit(1).first()
        if key_value:
            apk_path = key_value.value
            cache.set('TGZQ_apk_path', apk_path, timeout=12 * 60 * 60)
    full_apk_path = current_app.config['FILE_SERVER'] + apk_path
    return render_template("share/linkshare.html", identity_id=identity_id, full_apk_path=full_apk_path)


@share.route('/skip_url', methods=['GET', 'POST'])
def skip_url():
    identity_id = request.values.get('identity_id').strip()
    phone = request.values.get('phone').strip()
    # 判断当前手机号是否已被邀请
    info = InviteInfo.query.filter_by(phone_num=phone).limit(1).first()
    if info:
        return jsonify({"statuscode": "0000"})
    # 判断当前手机号是否已注册
    info = GodinAccount.query.filter_by(phone_num=phone).limit(1).first()
    if info:
        return jsonify({"statuscode": "0000"})
    user = UserGeneralize.query.filter_by(invite_link=identity_id).limit(1).first()
    if user:
        # 将邀请记录存入数据表
        info = InviteInfo()
        md = hashlib.md5()
        md.update(bytes(phone, 'utf-8'))
        info.godin_id = md.hexdigest()
        info.inviter_godin_id = user.godin_id
        info.phone_num = phone
        # 将邀请者的邀请人数加 1
        user.invite_person_num += 1
        db.session.add(info)
        db.session.add(user)
        db.session.commit()
    return jsonify({"statuscode": "0000"})


@share.route('/vssq_download_url', methods=['GET', 'POST'])
def share_url():
    log_print("share_url", "", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        request.headers.get('X-Forwarded-For'))
    apk_path = cache.get("VSZS_apk_path")
    if not apk_path:
        # 如果没有缓存，则去数据库获取
        key_value = KeyValue.query.filter_by(key="VSZS_apk_path").limit(1).first()
        if key_value:
            apk_path = key_value.value
            cache.set('VSZS_apk_path', apk_path, timeout=12 * 60 * 60)
    full_apk_path = current_app.config['FILE_SERVER'] + apk_path
    return render_template("business/vssqLoad.html", full_apk_path=full_apk_path)


@share.route('/voice', methods=['GET', 'POST'])
def player_voide():
    voice_name = request.values.get('voice_name')
    file_dir = "images/voice/" + voice_name
    basedir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    full_file = os.path.join(basedir, "share/static/images/voice", voice_name)
    if not os.path.exists(full_file):
        file_dir = None
    return render_template("share/voice.html", file_dir=file_dir)


@share.route('/appeal')
def appeal():
    return render_template("share/appeal.html")


@share.route('/appeal_history')
def appeal_history():
    godin_id = request.args.get('godin_id')
    godin_account = GodinAccount.query.filter_by(godin_id=godin_id).first()
    feed_backs = []
    if godin_account:
        feed_backs = FeedBack.query.filter_by(phone_num=godin_account.phone_num).order_by(FeedBack.create_time.desc()).all()
    return render_template("share/appeal_history.html", feed_backs=feed_backs)


@share.route('/appeal_details')
def appeal_details():
    id = request.args.get('id')
    feed_back = FeedBack.query.get_or_404(id)
    file_ser = current_app.config['FILE_SERVER']
    return render_template("share/appeal_details.html", feed_back=feed_back, file_ser=file_ser)




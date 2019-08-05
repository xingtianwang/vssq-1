#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import current_app
from app import db, create_app
import datetime
from app.api_1_0.models import KeyRecord, ChannelAccount


def add_key_record():
    app = create_app('default')
    app_context = app.app_context()
    app_context.push()
    key_record = KeyRecord.query.filter_by(id='00000000000000').first()
    channel_account = ChannelAccount.query.filter_by(channel_id='qd0000').first()
    if channel_account is None:

        channel_account = ChannelAccount()
        channel_account.id = 1
        channel_account.channel_id = 'qd0000'
        channel_account.channel_name = '国鼎账号'
        channel_account.account_id = 'godinsec'
        channel_account.password = '000000'
        channel_account.create_time = datetime.datetime.now()
        channel_account.channel_manager = 'godinsec'
        channel_account.content = '国鼎'
        channel_account.operator = 'godinsec'
        db.session.add(channel_account)
    else:
        channel_account.channel_id = 'qd0000'
        channel_account.account_id = 'godinsec'
        channel_account.channel_name = 'godinsec'
        channel_account.password = '000000'
        channel_account.channel_manager = 'godinsec'
        channel_account.content = '国鼎'
        channel_account.operator = 'godinsec'
        db.session.add(channel_account)
    db.session.commit()
    if key_record is None:
        key_record = KeyRecord()
        key_record.id = '00000000000000'
        key_record.channel_account_id = channel_account.id
        key_record.create_time = datetime.datetime.now()
        key_record.oeprator = 'Godin'
        key_record.content = '购买终身授权码'
        key_record.count = 0
        key_record.vip_time = 365 * 100
        key_record.vip_ad_time = 7
        # key_record.expire_time = datetime.datetime.now() + datetime.timedelta(days=12 * 30 * 100)
        db.session.add(key_record)
    else:
        key_record.oeprator = 'Godin'
        key_record.content = '购买终身授权码'
        key_record.count = 0
        key_record.vip_time = 365 * 100
        key_record.vip_ad_time = 7
        # key_record.expire_time = datetime.datetime.now() + datetime.timedelta(days=12 * 30 * 100)
        db.session.add(key_record)
    db.session.commit()


if __name__ == '__main__':
    add_key_record()

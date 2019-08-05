#!/usr/bin/env python
# -*- coding:utf-8 -*-

from app import db, create_app
import datetime
from app.api_1_0.models import ChannelAccountStatistics, ChannelAccount, KeyRecord, \
    DivideDataStatistics, Wallet


def make_channel_account_radio_day_data():
    app = create_app('default')
    app_context = app.app_context()
    app_context.push()

    today = datetime.date.today()
    if ChannelAccountStatistics.query.filter_by(record_time=today).limit(
            1).first() is not None:
        return False

    channel_accounts = db.session.query(ChannelAccount.channel_id, ChannelAccount.account_id, ChannelAccount.id).filter(
        ChannelAccount.id != 1)
    for channel_account in channel_accounts:
        channel_account_statistics = ChannelAccountStatistics()
        channel_account_statistics.channel_account_id = channel_account[0]
        channel_account_statistics.account_id = channel_account[1]
        # 獲取該賬號下的所有批次分成
        key_records = db.session.query(KeyRecord.id).filter(KeyRecord.channel_account_id == channel_account[2])
        channel_account_statistics.total_count = 0
        channel_account_statistics.total_money = 0
        for key_record in key_records:
            divide_data_statistics = db.session.query(DivideDataStatistics).filter(
                DivideDataStatistics.record_time == today).filter \
                (DivideDataStatistics.key_record_id == key_record[0]).limit(1).first()

            if divide_data_statistics is not None:
                channel_account_statistics.total_count += (
                        divide_data_statistics.vip_count + divide_data_statistics.third_vip_count)
                channel_account_statistics.total_money += (
                        divide_data_statistics.vip_money + divide_data_statistics.third_vip_money)
        wallet = Wallet.query.filter_by(channel_account_id=channel_account[2]).limit(1).first()
        if wallet is None:
            wallet = Wallet()
            wallet.channel_account_id = channel_account[2]
            wallet.account_id = channel_account[1]
            wallet.income = channel_account_statistics.total_money
            wallet.balance = channel_account_statistics.total_money
        else:
            # 如果某一天数据没有统计上 第二天放开这段进行所有数据从新累加
            # channel_account_statistics = ChannelAccountStatistics.query.filter_by(channel_account_id=channel_account[0])
            # wallet.income = 0
            # for data_channel_account in channel_account_statistics:
            #     wallet.income += data_channel_account.total_money
            # 平时单独放开这一句就可以
            wallet.income = wallet.income + channel_account_statistics.total_money
        wallet.ping()
        db.session.add(wallet)
        db.session.add(channel_account_statistics)
        db.session.commit()
    return True


if __name__ == '__main__':
    make_channel_account_radio_day_data()

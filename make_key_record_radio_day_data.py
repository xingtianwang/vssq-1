#!/usr/bin/env python
# -*- coding:utf-8 -*-
from sqlalchemy import func, distinct
from app import db, create_app
import datetime
from app.api_1_0.models import KeyRecord, DivideDataStatistics, MemberWareOrder, BusinessWareOrder, KeyRecordsStatistics


def make_key_record_radio_day_data():
    app = create_app('default')
    app_context = app.app_context()
    app_context.push()

    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=8)
    yesterday_start_time = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
    yesterday_end_time = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)
    if DivideDataStatistics.query.filter_by(record_time=today.strftime('%Y-%m-%d')).first() is not None:
        return False
    key_records = db.session.query(KeyRecord.id, KeyRecord.vip_ratio, KeyRecord.business_ratio,
                                   KeyRecord.channel_account_id) \
        .filter(KeyRecord.id != '00000000000000')
    for key_record in key_records:
        divide_data_statistics = DivideDataStatistics()
        # 批次
        divide_data_statistics.key_record_id = key_record[0]
        # 會員分成比例
        divide_data_statistics.vip_divide_ratio = key_record[1]
        # 三方分成比例
        divide_data_statistics.third_divide_ratio = key_record[2]
        # 計算每日購買會員的次數
        vip_count = db.session.query(func.count(MemberWareOrder.order_number)).filter(MemberWareOrder.status == 1,
                                                                                      MemberWareOrder.pay_time.between(
                                                                                          yesterday_start_time,
                                                                                          yesterday_end_time)).filter(
            MemberWareOrder.key_record_id == key_record[0], MemberWareOrder.category == 0).first()
        divide_data_statistics.vip_count = vip_count[0]
        # 計算每日購買會員人數
        vip_people_count = db.session.query(func.count(distinct(MemberWareOrder.buyer_godin_id))).filter(
            MemberWareOrder.pay_time.between(yesterday_start_time, yesterday_end_time)).filter \
            (MemberWareOrder.key_record_id == key_record[0], MemberWareOrder.status == 1,
             MemberWareOrder.category == 0).limit(1).first()
        divide_data_statistics.vip_people_count = vip_people_count[0]
        # 計算鉑金會員每日分成
        member_ware_orders = db.session.query(MemberWareOrder.discount_price).filter(
            MemberWareOrder.key_record_id == key_record[0], MemberWareOrder.status == 1, MemberWareOrder.category == 0,
            MemberWareOrder.pay_time.between(yesterday_start_time, yesterday_end_time))
        vip_money = 0
        if member_ware_orders is not None:
            for member_ware_order in member_ware_orders:
                vip_money += (member_ware_order[0] * key_record[1]) / 100
            divide_data_statistics.vip_money = vip_money
        # 計算三方會員每日購買次數
        third_vip_count = db.session.query(func.count(BusinessWareOrder.order_number)).filter(
            BusinessWareOrder.status == 1,
            BusinessWareOrder.pay_time.between(yesterday_start_time, yesterday_end_time)).filter \
            (BusinessWareOrder.key_record_id == key_record[0]).limit(1).first()
        divide_data_statistics.third_vip_count = third_vip_count[0]
        # 計算三方會員每天購買人數
        third_people_count = db.session.query(func.count(distinct(BusinessWareOrder.buyer_godin_id))).filter(
            BusinessWareOrder.pay_time.between(yesterday_start_time, yesterday_end_time)).filter \
            (BusinessWareOrder.key_record_id == key_record[0], BusinessWareOrder.status == 1).limit(1).first()
        divide_data_statistics.third_people_count = third_people_count[0]
        # 計算每日三方會員分成
        business_ware_orders = db.session.query(BusinessWareOrder.discount_price).filter(
            BusinessWareOrder.key_record_id == key_record[0], BusinessWareOrder.status == 1,
            BusinessWareOrder.pay_time.between(yesterday_start_time, yesterday_end_time))
        third_vip_money = 0
        if business_ware_orders is not None:
            for business_ware_order in business_ware_orders:
                third_vip_money += (business_ware_order[0] * key_record[2]) / 100
            divide_data_statistics.third_vip_money = third_vip_money
        divide_data_statistics.total_money = third_vip_money + vip_money
        # 统计每个批次总的分成
        key_record_statistics = KeyRecordsStatistics.query.filter_by(key_record_id=key_record[0]).limit(1).first()
        if key_record_statistics is None:
            key_record_statistics = KeyRecordsStatistics()
            key_record_statistics.key_record_id = key_record[0]
            key_record_statistics.channel_account_id = key_record[3]
            key_record_statistics.income = vip_money + third_vip_money
        else:
            # 如果某一天数据没有统计上 第二天放开这段进行所有数据从新累加
            # divide_data_statistics = DivideDataStatistics.query.filter_by(key_record_id=key_record[0])
            # key_record_statistics.income = 0
            # for day_statistics in divide_data_statistics:
            #     key_record_statistics.income += (day_statistics.vip_money + day_statistics.third_vip_money)
            # 平时单独放开这一句就可以
            key_record_statistics.income = key_record_statistics.income + vip_money + third_vip_money
        key_record_statistics.ping()
        db.session.add(key_record_statistics)
        if vip_money != 0 or third_vip_money != 0:
            db.session.add(divide_data_statistics)
        db.session.commit()

    return True


if __name__ == '__main__':
    make_key_record_radio_day_data()

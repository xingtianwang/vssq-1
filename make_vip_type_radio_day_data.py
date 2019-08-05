#!/usr/bin/env python
# -*- coding:utf-8 -*-
from sqlalchemy import func, distinct
from app import db, create_app
import datetime
from app.api_1_0.models import KeyRecord, MemberWareOrder, \
    VipDataStatistics, MemberWare, BusinessWareOrder, BusinessWare


def make_vip_type_radio_day_data():
    app = create_app('default')
    app_context = app.app_context()
    app_context.push()

    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=8)
    yesterday_start_time = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
    yesterday_end_time = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)
    if VipDataStatistics.query.filter_by(record_time=today.strftime('%Y-%m-%d')).first() is not None:
        return False
    # if BusinessDataStatistics.query.filter_by(record_time=yesterday.strftime('%Y-%m-%d')).first() is not None:
    #     return False

    key_records = db.session.query(KeyRecord.id, KeyRecord.vip_ratio, KeyRecord.business_ratio).filter(
        KeyRecord.id != '00000000000000')
    for key_record in key_records:
        # vip
        for ware in MemberWare.query.all():
            vip_data_statistics = VipDataStatistics()
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

                db.session.add(vip_data_statistics)
                db.session.commit()

        # 客多多
        for ware in BusinessWare.query.all():
            business_data_statistics = VipDataStatistics()
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

                db.session.add(business_data_statistics)
                db.session.commit()

    return True


if __name__ == '__main__':
    make_vip_type_radio_day_data()

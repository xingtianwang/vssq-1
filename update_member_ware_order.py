#!/usr/bin/env python
# -*- coding:utf-8 -*-
from app import db, create_app
from sqlalchemy import func, distinct, desc

import datetime
from app.api_1_0.models import MemberWareOrder, UserInfo, UserKeyRecord, Key, BusinessWareOrder, \
    DivideDataStatistics, KeyRecord, KeyRecordsStatistics, ChannelAccountStatistics, ChannelAccount, Wallet, \
    VipDataStatistics, MemberWare, BusinessWare, VipPayDayStatistics, VipMembers, BusinessPayDayStatistics, \
    BusinessMembers


def update_order_key_record_id():
    app = create_app('production')
    app_context = app.app_context()
    app_context.push()
    user_infos = db.session.query(UserInfo.imei, UserInfo.godin_id).filter_by()
    with open('a.txt', 'a') as f:
        for user_info in user_infos:
            user_key_record = db.session.query(UserKeyRecord.key_id).filter_by(imei=user_info[0]).limit(1).first()
            if user_key_record is not None:
                key = db.session.query(Key.key_record_id).filter_by(id=user_key_record[0]).limit(1).first()
                if key[0] in ['15566179782450', '15572988453208', '15579111253760', '15579118094291']:
                    member_orders = MemberWareOrder.query.filter_by(buyer_godin_id=user_info[1])
                    for member_order in member_orders:
                        member_order.key_record_id = key[0]
                        # if member_order.key_record_id in ['15566179782450', '15572988453208', '15579111253760', '15579118094291']:
                        f.write('订单号：%s 批次号：%s%s' % (member_order.order_number, member_order.key_record_id, "\n"))
                        # print(member_order.order_number, member_order.key_record_id)
                    # db.session.add(member_order)
                # db.session.commit()


def update_order_key_record_id_optimize():
    app = create_app('production')
    # app = create_app('test')
    app_context = app.app_context()
    app_context.push()

    Keys = db.session.query(Key.id, Key.key_record_id, Key.create_time).filter(Key.status != 0).filter(
        Key.key_record_id.in_(['15566179782450', '15572988453208', '15579111253760', '15579118094291']))
    print(Keys.count())
    with open('a.txt', 'a') as f:
        for key in Keys:
            user_key_record = db.session.query(UserKeyRecord.imei).filter(UserKeyRecord.key_id == key[0])
            if user_key_record is not None:
                userInfo = db.session.query(UserInfo.godin_id, UserInfo.imei).filter(UserInfo.imei.in_(user_key_record))
                count = userInfo.count()
                if count > 1:
                    for u in userInfo:
                        # f.write('userInfo %s count  %s\n' % (u[0], u[1]))
                        print('userInfo %s count  %s\n' % (u[0], u[1]))

                if userInfo is not None:
                    for user in userInfo:
                        mwo = db.session.query(MemberWareOrder).filter(
                            MemberWareOrder.buyer_godin_id == user[0]).filter(
                            MemberWareOrder.pay_time >= key[2]).filter(MemberWareOrder.category == 0)
                        if mwo is not None:
                            for mo in mwo:
                                f.write('订单号：%s 批次号：%s  %s %s %s %s  %s %s  %s' % (
                                    mo.order_number, key[0], key[1], key[2], user[0], user[1], mo.key_record_id,
                                    mo.discount_price, "\n"))
                                # mo.key_record_id = key[1]
                                # db.session.add(mo)

                            # db.session.commit()
                        bus = db.session.query(BusinessWareOrder).filter(
                            BusinessWareOrder.buyer_godin_id == user[0]).filter(
                            BusinessWareOrder.pay_time >= key[2])
                        if bus is not None:
                            for bu in bus:
                                f.write('订单号：%s 批次号：%s  %s %s %s %s  %s  %s %s' % (
                                    bu.order_number, key[0], key[1], key[2], user[0], user[1], bu.key_record_id,
                                    bu.discount_price, "\n"))
                            #     bu.key_record_id = key[1]
                            #     db.session.add(bu)
                            # db.session.commit()
    f.close()


def make_key_record_radio_day_data():
    app = create_app('production')
    # app = create_app('test')
    app_context = app.app_context()
    app_context.push()

    print('aaaa')
    for num in range(1, 9):
        # print(num)
        d = 9 - num
        today = datetime.datetime.today()
        yesterday = today - datetime.timedelta(days=d)
        yesterday_start_time = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
        yesterday_end_time = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)

        print('yesterday %s  %s\n' % (yesterday_start_time, yesterday_end_time))

        if db.session.query(DivideDataStatistics).filter(
                DivideDataStatistics.record_time == yesterday_end_time.strftime('%Y-%m-%d')).limit(
            1).first() is not None:
            # return False
            continue
        key_records = db.session.query(KeyRecord.id, KeyRecord.vip_ratio, KeyRecord.business_ratio,
                                       KeyRecord.channel_account_id) \
            .filter(KeyRecord.id != '00000000000000').filter(KeyRecord.channel_account_id != 1).all()
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
                                                                                          MemberWareOrder.pay_time.between(
                                                                                              yesterday_start_time,
                                                                                              yesterday_end_time)).filter(
                MemberWareOrder.key_record_id == key_record[0], MemberWareOrder.category == 0).first()
            if vip_count is not None:
                divide_data_statistics.vip_count = vip_count[0]
            else:
                divide_data_statistics.vip_count = 0
                # 計算每日購買會員人數
            vip_people_count = db.session.query(func.count(distinct(MemberWareOrder.buyer_godin_id))).filter(
                MemberWareOrder.pay_time.between(yesterday_start_time, yesterday_end_time)).filter \
                (MemberWareOrder.key_record_id == key_record[0], MemberWareOrder.status == 1,
                 MemberWareOrder.category == 0).first()
            if vip_people_count is not None:
                divide_data_statistics.vip_people_count = vip_people_count[0]
            else:
                divide_data_statistics.vip_people_count = 0
            # 計算鉑金會員每日分成
            member_ware_orders = db.session.query(MemberWareOrder.discount_price).filter(
                MemberWareOrder.key_record_id == key_record[0], MemberWareOrder.status == 1,
                MemberWareOrder.category == 0,
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
                BusinessWareOrder.pay_time.between(yesterday_start_time, yesterday_end_time))
            third_vip_money = 0
            if business_ware_orders is not None:
                for business_ware_order in business_ware_orders:
                    third_vip_money += (business_ware_order[0] * key_record[2]) / 100
            divide_data_statistics.third_vip_money = third_vip_money
            divide_data_statistics.total_money = third_vip_money + vip_money
            # 统计每个批次总的分成
            key_record_statistics = db.session.query(KeyRecordsStatistics).filter_by(key_record_id=key_record[0]).limit(
                1).first()
            if key_record_statistics is None:
                key_record_statistics = KeyRecordsStatistics()
                key_record_statistics.create_time = yesterday
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
                print('exist')
            key_record_statistics.ping()

            if key_record_statistics.income != 0:
                db.session.add(key_record_statistics)
            if vip_money != 0 or third_vip_money != 0:
                db.session.add(divide_data_statistics)
                print('insert')
            print('key_record_id %s channel_account_id  %s  income %s\n' % (key_record_statistics.key_record_id, \
                                                                            key_record_statistics.channel_account_id, \
                                                                            key_record_statistics.income))
            db.session.commit()


def make_channel_account_radio_day_data():
    app = create_app('production')
    # app = create_app('test')
    app_context = app.app_context()
    app_context.push()

    for num in range(1, 9):
        # print(num)
        d = 9 - num
        today = datetime.datetime.today()
        yesterday = today - datetime.timedelta(days=d)
        yesterday_start_time = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
        yesterday_end_time = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)

        if db.session.query(ChannelAccountStatistics).filter(ChannelAccountStatistics.record_time == yesterday).limit(
                1).first() is not None:
            continue

        channel_accounts = db.session.query(ChannelAccount.channel_id, ChannelAccount.account_id,
                                            ChannelAccount.id).filter(
            ChannelAccount.id != 1)
        for channel_account in channel_accounts:
            channel_account_statistics = ChannelAccountStatistics()
            channel_account_statistics.record_time = yesterday
            channel_account_statistics.channel_account_id = channel_account[0]
            channel_account_statistics.account_id = channel_account[1]
            # 獲取該賬號下的所有批次分成
            key_records = db.session.query(KeyRecord.id).filter(KeyRecord.channel_account_id == channel_account[2])
            channel_account_statistics.total_count = 0
            channel_account_statistics.total_money = 0
            for key_record in key_records:
                divide_data_statistics = db.session.query(DivideDataStatistics).filter(
                    DivideDataStatistics.record_time == yesterday_end_time.strftime('%Y-%m-%d')).filter \
                    (DivideDataStatistics.key_record_id == key_record[0]).limit(1).first()
                print('yesterday %s  %s\n' % (yesterday, key_record[0]))
                if divide_data_statistics is not None:
                    channel_account_statistics.total_count += (
                            divide_data_statistics.vip_count + divide_data_statistics.third_vip_count)
                    channel_account_statistics.total_money += (
                            divide_data_statistics.vip_money + divide_data_statistics.third_vip_money)
                    print('channel_account_statistics %s  %s\n' % (
                        channel_account_statistics.total_count, channel_account_statistics.total_money))
            wallet = db.session.query(Wallet).filter(Wallet.channel_account_id == channel_account[2]).limit(1).first()
            if wallet is None:
                wallet = Wallet()
                wallet.create_time = yesterday_end_time
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


def make_vip_type_radio_day_data():
    app = create_app('production')
    # app = create_app('test')
    app_context = app.app_context()
    app_context.push()

    for num in range(1, 9):
        # print(num)
        d = 9 - num
        today = datetime.datetime.today()
        yesterday = today - datetime.timedelta(days=d)
        yesterday_start_time = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
        yesterday_end_time = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)
        if db.session.query(VipDataStatistics).filter(
                VipDataStatistics.record_time == yesterday.strftime('%Y-%m-%d')).order_by(
            VipDataStatistics.id.desc()).limit(1).first() is not None:
            continue
        # if BusinessDataStatistics.query.filter_by(record_time=yesterday.strftime('%Y-%m-%d')).first() is not None:
        #     return False

        key_records = db.session.query(KeyRecord.id, KeyRecord.vip_ratio, KeyRecord.business_ratio).filter(
            KeyRecord.id != '00000000000000').filter(KeyRecord.channel_account_id != 1)
        for key_record in key_records:
            # vip
            for ware in db.session.query(MemberWare).all():
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
            for ware in db.session.query(BusinessWare).all():
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


def make_vip_last_day_data():
    app = create_app('production')
    # app = create_app('test')
    app_context = app.app_context()
    app_context.push()

    for num in range(1, 2):
        # print(num)
        d = 5 - num

        today = datetime.datetime.today()
        yesterday = today - datetime.timedelta(days=d)
        yesterday_start_time = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
        yesterday_end_time = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)

        print('yesterday %s  %s\n' % (yesterday_start_time, yesterday_end_time))

        if db.session.query(VipPayDayStatistics).filter(VipPayDayStatistics.date==yesterday.strftime('%Y-%m-%d')).order_by(
                desc(VipPayDayStatistics.id)).limit(1).first() is not None:
            return False

        print('11111')
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
        print('2222')
        # 商业会员统计
        if BusinessPayDayStatistics.query.filter_by(date=yesterday.strftime('%Y-%m-%d')).order_by(
                desc(BusinessPayDayStatistics.id)).limit(1).first() is not None:
            return False
        print('3333')
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
        print('4444')
        db.session.add(info)
        db.session.commit()

    return True


if __name__ == '__main__':
    # make_key_record_radio_day_data()
    # make_channel_account_radio_day_data()
    make_vip_type_radio_day_data()
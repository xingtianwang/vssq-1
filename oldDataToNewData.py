#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime
import random
import string
import traceback

from sqlalchemy import distinct
from app import db, create_app
from app.api_1_0.models import MemberWareOrder, UserInfo, UserKeyRecord, Key, KeyRecord, VipMembers, GodinAccount


def gen_free_vip_order_num():
    return 'free' + datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S') + \
           ''.join(random.sample(string.ascii_letters + string.digits, 15))

def oldDataToNewData():
    app = create_app('production')
    app_context = app.app_context()
    app_context.push()

    datenow = datetime.datetime.now()

    key_records = db.session.query(KeyRecord).all()
    num = 0
    for key_record in key_records:
        keys = db.session.query(Key).filter(Key.key_record_id == key_record.id, Key.give_activate_status == 0, Key.status == 1).all()

        if keys is None:
            continue

        # if num > 10:
        #     break
        #
        # print('keys:'+str(len(keys)))
        #
        # for k in keys:
        #     print(k)

        if len(keys) > 0:

            for key in keys:
                user_key_record = db.session.query(UserKeyRecord).filter(UserKeyRecord.key_id == key.id,
                                                                         UserKeyRecord.status == 1).limit(1).first()

                if user_key_record is None:
                    continue
                # print(key.id)

                if user_key_record:
                    try:
                        ukr = db.session.query(UserKeyRecord.imei).filter(UserKeyRecord.key_id == key.id,
                                                                          UserKeyRecord.status == 1)
                        if ukr is not None:
                            userInfo = db.session.query(UserInfo.godin_id).filter(UserInfo.imei.in_(ukr))
                            # print('-----------------  %s -------------' % (key.id))

                            # if num > 10:
                            #     break

                            if userInfo:
                                # 查询是否存在订单
                                # 查询是否存在订单
                                mwo = db.session.query(MemberWareOrder).filter(
                                    MemberWareOrder.buyer_godin_id.in_(userInfo), MemberWareOrder.status == 1,
                                                                                  MemberWareOrder.buy_grade == 1, \
                                                                                  MemberWareOrder.ware_id != 'freevip'). \
                                    order_by(MemberWareOrder.end_time.desc()).limit(1).first()

                                mwo_god = db.session.query(MemberWareOrder).filter(
                                    MemberWareOrder.buyer_godin_id.in_(userInfo), MemberWareOrder.status == 1,
                                                                                  MemberWareOrder.buy_grade == 0, \
                                                                                  MemberWareOrder.ware_id != 'freegod'). \
                                    order_by(MemberWareOrder.end_time.desc()).limit(1).first()
                                # 存在
                                if mwo:
                                    vipmember = db.session.query(VipMembers).filter(
                                        VipMembers.godin_id == mwo.buyer_godin_id).limit(1).first()

                                    if vipmember:
                                        # print('vipmember is exist.'+mwo.buyer_godin_id)
                                        if vipmember.valid_time:
                                            if vipmember.valid_time < user_key_record.activate_time + datetime.timedelta(days=key_record.vip_ad_time):
                                                vipmember.valid_time = user_key_record.activate_time + datetime.timedelta(days=key_record.vip_ad_time)
                                        else:
                                            vipmember.valid_time = user_key_record.activate_time + datetime.timedelta(days=key_record.vip_ad_time)

                                        if vipmember.gold_valid_time is None:
                                            vipmember.gold_valid_time = user_key_record.activate_time + datetime.timedelta(days=key_record.vip_gold_ad_time)
                                        else:
                                            if mwo_god:
                                                vipmember.gold_valid_time = mwo_god.end_time + datetime.timedelta(
                                                    days=key_record.vip_gold_ad_time)

                                        freegod = None
                                        freevip = None
                                        godaccount = db.session.query(GodinAccount.godin_id).filter(
                                            GodinAccount.godin_id==mwo.buyer_godin_id).order_by(
                                            GodinAccount.create_time.desc()).limit(1).first()
                                        if key_record.vip_gold_ad_time > 0:
                                            vipmember.grade = 1
                                            vip_gold_ad_time = key_record.vip_gold_ad_time
                                            # 赠送黄金会员
                                            freegod = MemberWareOrder()
                                            freegod.ware_id = 'freegod'
                                            freegod.order_number = gen_free_vip_order_num()
                                            freegod.buyer_godin_id = godaccount[0]
                                            freegod.pay_type = 2
                                            freegod.ware_price = 0
                                            freegod.discount_price = 0
                                            freegod.discount = 0
                                            freegod.status = 1
                                            freegod.ac_source = 0
                                            freegod.pay_time = datetime.datetime.now()
                                            freegod.start_time = user_key_record.activate_time
                                            freegod.end_time = user_key_record.activate_time + datetime.timedelta(
                                                days=vip_gold_ad_time)
                                            freegod.category = 1
                                            freegod.key_record_id = key.key_record_id
                                            freegod.buy_grade = 0

                                            # 当存在订单时，需要判断订单的时间和赠送的时间，取最大的值
                                            if mwo:
                                                if mwo.end_time > freegod.end_time:
                                                    freegod.end_time = mwo.end_time
                                                    vipmember.gold_valid_time = mwo.end_time

                                        if key_record.vip_ad_time > 0:
                                            vipmember.grade = 2
                                            vip_ad_time = key_record.vip_ad_time
                                            # 赠送铂金会员
                                            freevip = MemberWareOrder()
                                            freevip.ware_id = 'freevip'
                                            freevip.order_number = gen_free_vip_order_num()
                                            freevip.buyer_godin_id = godaccount[0]
                                            freevip.pay_type = 2
                                            freevip.ware_price = 0
                                            freevip.discount_price = 0
                                            freevip.discount = 0
                                            freevip.status = 1
                                            freevip.ac_source = 0
                                            freevip.pay_time = datetime.datetime.now()
                                            freevip.start_time = user_key_record.activate_time
                                            freevip.end_time = user_key_record.activate_time + datetime.timedelta(
                                                days=vip_ad_time)
                                            freevip.category = 1
                                            freevip.key_record_id = key.key_record_id
                                            freevip.buy_grade = 1

                                            if mwo is not None:
                                                if mwo.end_time > freevip.end_time:
                                                    freevip.end_time = mwo.end_time
                                                    vipmember.valid_time = mwo.end_time

                                        if freegod:
                                            print('add freegod %s  %s' % (freegod.buyer_godin_id,freegod.end_time))
                                            if freegod.end_time >= datenow:
                                                vipmember.grade = 1
                                            db.session.add(freegod)
                                        if freevip:
                                            print('add freevip %s  %s' % (freevip.buyer_godin_id,freevip.end_time))
                                            if freevip.end_time >= datenow:
                                                vipmember.grade = 2
                                            db.session.add(freevip)

                                        # print(godaccount)
                                        # print('add vipmember')
                                        # print('add key')
                                        num = num + 1

                                        db.session.add(vipmember)
                                        key.give_activate_status = 1
                                        db.session.add(key)
                                        db.session.commit()

                                        print('vipmember godin_id:%s  %s  %s %s' % (
                                        vipmember.godin_id, vipmember.valid_time, vipmember.gold_valid_time,
                                        vipmember.grade))
                                        print('key %s  give_activate_status:%s' % (key.id, key.give_activate_status))

                                # 不存在订单
                                else:
                                    godaccount = db.session.query(GodinAccount.godin_id).filter(
                                        GodinAccount.godin_id.in_(userInfo)).order_by(
                                        GodinAccount.create_time.desc()).first()

                                    if godaccount:
                                        vipmember = VipMembers()
                                        vipmember.valid_time = user_key_record.activate_time + datetime.timedelta(key_record.vip_ad_time)
                                        vipmember.gold_valid_time = user_key_record.activate_time + datetime.timedelta(key_record.vip_gold_ad_time)
                                        vipmember.status = 1
                                        vipmember.channel = ''
                                        vipmember.godin_id = godaccount[0]
                                        vipmember.grade = 2
                                        vipmember.category = 1
                                        vipmember.create_time = datenow
                                        # db.session.add(vipmember)
                                        # db.session.commit()

                                        # 赠送黄金会员
                                        freegod = MemberWareOrder()
                                        freegod.ware_id = 'freegod'
                                        freegod.order_number = gen_free_vip_order_num()
                                        freegod.buyer_godin_id = godaccount[0]
                                        freegod.pay_type = 2
                                        freegod.ware_price = 0
                                        freegod.discount_price = 0
                                        freegod.discount = 0
                                        freegod.status = 1
                                        freegod.ac_source = 0
                                        freegod.pay_time = datetime.datetime.now()
                                        freegod.start_time = user_key_record.activate_time
                                        freegod.end_time = user_key_record.activate_time + datetime.timedelta(
                                            days=key_record.vip_gold_ad_time)
                                        freegod.category = 1
                                        freegod.key_record_id = key.key_record_id
                                        freegod.buy_grade = 0

                                        vipmember.grade = 2
                                        # 赠送铂金会员
                                        freevip = MemberWareOrder()
                                        freevip.ware_id = 'freevip'
                                        freevip.order_number = gen_free_vip_order_num()
                                        freevip.buyer_godin_id = godaccount[0]
                                        freevip.pay_type = 2
                                        freevip.ware_price = 0
                                        freevip.discount_price = 0
                                        freevip.discount = 0
                                        freevip.status = 1
                                        freevip.ac_source = 0
                                        freevip.pay_time = datetime.datetime.now()
                                        freevip.start_time = user_key_record.activate_time
                                        freevip.end_time = user_key_record.activate_time + datetime.timedelta(
                                            days=key_record.vip_ad_time)
                                        freevip.category = 1
                                        freevip.key_record_id = key.key_record_id
                                        freevip.buy_grade = 1

                                        vipmember.valid_time = user_key_record.activate_time + datetime.timedelta(
                                            days=key_record.vip_ad_time)
                                        vipmember.gold_valid_time = user_key_record.activate_time + datetime.timedelta(
                                            days=key_record.vip_gold_ad_time)

                                        # print(godaccount)
                                        if vipmember.gold_valid_time:
                                            if vipmember.gold_valid_time > datenow:
                                                vipmember.grade = 1
                                        if vipmember.valid_time:
                                            if vipmember.valid_time > datenow:
                                                vipmember.grade = 2
                                        print('not vipmember godin_id:%s  %s  %s  %s' %( vipmember.godin_id, vipmember.valid_time,
                                              vipmember.gold_valid_time, vipmember.grade))
                                        db.session.add(vipmember)
                                        db.session.commit()

                                        if freegod:
                                            print('add freegod %s  %s' %(freegod.buyer_godin_id,freegod.end_time))
                                            db.session.add(freegod)
                                        if freevip:
                                            print('add freevip %s  %s'  %(freevip.buyer_godin_id, freevip.end_time))
                                            db.session.add(freevip)

                                        print('add key %s give_activate_status:%s' %( key.id,key.give_activate_status))

                                        num = num + 1
                                        key.give_activate_status = 1
                                        db.session.add(key)
                                        db.session.commit()
                    except Exception as e:
                        print(e)
                        print(traceback.format_exc())
                        db.session.rollback()
                # db.session.commit()
                    print(num)



def oldDataToNewDataOne():
    app = create_app('production')
    app_context = app.app_context()
    app_context.push()

    datenow = datetime.datetime.now()

    key_record = db.session.query(KeyRecord).filter(KeyRecord.id == '15517544095327').limit(1).first()
    num = 0
    print(key_record)
    keys = db.session.query(Key).filter(Key.id == 'key6li9Rb85sfSGtpvF7', Key.key_record_id == '15517544095327', Key.give_activate_status == 0, Key.status == 1).all()
    print(keys)
    # if num > 10:
    #     break
    #
    # print('keys:'+str(len(keys)))
    #
    # for k in keys:
    #     print(k)
    print(str(len(keys)))
    if len(keys) > 0:

        for key in keys:
            print(key)
            user_key_record = db.session.query(UserKeyRecord).filter(UserKeyRecord.key_id == key.id,
                                                                     UserKeyRecord.status == 1).limit(1).first()
            print(user_key_record)
            if user_key_record:
                try:
                    ukr = db.session.query(UserKeyRecord.imei).filter(UserKeyRecord.key_id == key.id,
                                                                      UserKeyRecord.status == 1)

                    print(ukr)
                    if ukr is not None:
                        userInfo = db.session.query(UserInfo.godin_id).filter(UserInfo.imei.in_(ukr))
                        # print('-----------------  %s -------------' % (key.id))

                        # if num > 10:
                        #     break

                        if userInfo:
                            # 查询是否存在订单
                            mwo = db.session.query(MemberWareOrder).filter(
                                MemberWareOrder.buyer_godin_id.in_(userInfo), MemberWareOrder.status==1,MemberWareOrder.buy_grade==1,\
                                MemberWareOrder.ware_id!='freevip'). \
                                order_by(MemberWareOrder.end_time.desc()).limit(1).first()

                            mwo_god = db.session.query(MemberWareOrder).filter(
                                MemberWareOrder.buyer_godin_id.in_(userInfo), MemberWareOrder.status == 1,
                                                                              MemberWareOrder.buy_grade == 0,\
                                MemberWareOrder.ware_id!='freegod'). \
                                order_by(MemberWareOrder.end_time.desc()).limit(1).first()
                            # 存在
                            if mwo:
                                vipmember = db.session.query(VipMembers).filter(
                                    VipMembers.godin_id == mwo.buyer_godin_id).limit(1).first()

                                if vipmember:
                                    # print('vipmember is exist.'+mwo.buyer_godin_id)
                                    if vipmember.valid_time:
                                        if vipmember.valid_time < user_key_record.activate_time + datetime.timedelta(days=key_record.vip_ad_time):
                                            vipmember.valid_time = user_key_record.activate_time + datetime.timedelta(days=key_record.vip_ad_time)
                                    else:
                                        vipmember.valid_time = user_key_record.activate_time + datetime.timedelta(days=key_record.vip_ad_time)

                                    if vipmember.gold_valid_time is None:
                                        vipmember.gold_valid_time = user_key_record.activate_time + datetime.timedelta(days=key_record.vip_gold_ad_time)
                                    else:
                                        if mwo_god:
                                            vipmember.gold_valid_time = mwo_god.end_time + datetime.timedelta(days=key_record.vip_gold_ad_time)

                                    freegod = None
                                    freevip = None
                                    godaccount = db.session.query(GodinAccount.godin_id).filter(
                                        GodinAccount.godin_id==mwo.buyer_godin_id).order_by(
                                        GodinAccount.create_time.desc()).limit(1).first()
                                    if key_record.vip_gold_ad_time > 0:
                                        vipmember.grade = 1
                                        vip_gold_ad_time = key_record.vip_gold_ad_time
                                        # 赠送黄金会员
                                        freegod = MemberWareOrder()
                                        freegod.ware_id = 'freegod'
                                        freegod.order_number = gen_free_vip_order_num()
                                        freegod.buyer_godin_id = godaccount[0]
                                        freegod.pay_type = 2
                                        freegod.ware_price = 0
                                        freegod.discount_price = 0
                                        freegod.discount = 0
                                        freegod.status = 1
                                        freegod.ac_source = 0
                                        freegod.pay_time = datetime.datetime.now()
                                        freegod.start_time = user_key_record.activate_time
                                        freegod.end_time = user_key_record.activate_time + datetime.timedelta(
                                            days=vip_gold_ad_time)
                                        freegod.category = 1
                                        freegod.key_record_id = key.key_record_id
                                        freegod.buy_grade = 0

                                        # 当存在订单时，需要判断订单的时间和赠送的时间，取最大的值
                                        if mwo:
                                            if mwo.end_time > freegod.end_time:
                                                freegod.end_time = mwo.end_time
                                                vipmember.gold_valid_time = mwo.end_time

                                    if key_record.vip_ad_time > 0:
                                        vipmember.grade = 2
                                        vip_ad_time = key_record.vip_ad_time
                                        # 赠送铂金会员
                                        freevip = MemberWareOrder()
                                        freevip.ware_id = 'freevip'
                                        freevip.order_number = gen_free_vip_order_num()
                                        freevip.buyer_godin_id = godaccount[0]
                                        freevip.pay_type = 2
                                        freevip.ware_price = 0
                                        freevip.discount_price = 0
                                        freevip.discount = 0
                                        freevip.status = 1
                                        freevip.ac_source = 0
                                        freevip.pay_time = datetime.datetime.now()
                                        freevip.start_time = user_key_record.activate_time
                                        freevip.end_time = user_key_record.activate_time + datetime.timedelta(
                                            days=vip_ad_time)
                                        freevip.category = 1
                                        freevip.key_record_id = key.key_record_id
                                        freevip.buy_grade = 1

                                        if mwo is not None:
                                            if mwo.end_time > freevip.end_time:
                                                freevip.end_time = mwo.end_time
                                                vipmember.valid_time = mwo.end_time

                                    if freegod:
                                        print('add freegod %s  %s' % (freegod.buyer_godin_id,freegod.end_time))
                                        if freegod.end_time >= datenow:
                                            vipmember.grade = 1
                                        db.session.add(freegod)
                                    if freevip:
                                        print('add freevip %s  %s' % (freevip.buyer_godin_id,freevip.end_time))
                                        if freevip.end_time >= datenow:
                                            vipmember.grade = 2
                                        db.session.add(freevip)

                                    # print(godaccount)
                                    # print('add vipmember')
                                    # print('add key')
                                    num = num + 1

                                    db.session.add(vipmember)
                                    key.give_activate_status = 1
                                    db.session.add(key)
                                    db.session.commit()

                                    print('vipmember godin_id:%s  %s  %s %s' % (
                                    vipmember.godin_id, vipmember.valid_time, vipmember.gold_valid_time,
                                    vipmember.grade))

                                    print('key %s  give_activate_status:%s' % (key.id, key.give_activate_status))

                            # 不存在订单
                            else:
                                godaccount = db.session.query(GodinAccount.godin_id).filter(
                                    GodinAccount.godin_id.in_(userInfo)).order_by(
                                    GodinAccount.create_time.desc()).first()

                                if godaccount:

                                    vipmember = db.session.query(VipMembers).filter(
                                        VipMembers.godin_id == godaccount[0]).limit(1).first()
                                    if vipmember is None:
                                        vipmember = VipMembers()
                                    vipmember.valid_time = user_key_record.activate_time + datetime.timedelta(key_record.vip_ad_time)
                                    vipmember.gold_valid_time = user_key_record.activate_time + datetime.timedelta(key_record.vip_gold_ad_time)
                                    vipmember.status = 1
                                    vipmember.channel = ''
                                    vipmember.godin_id = godaccount[0]
                                    vipmember.grade = 2
                                    vipmember.category = 1
                                    vipmember.create_time = datenow
                                    # db.session.add(vipmember)
                                    # db.session.commit()

                                    # 赠送黄金会员
                                    freegod = MemberWareOrder()
                                    freegod.ware_id = 'freegod'
                                    freegod.order_number = gen_free_vip_order_num()
                                    freegod.buyer_godin_id = godaccount[0]
                                    freegod.pay_type = 2
                                    freegod.ware_price = 0
                                    freegod.discount_price = 0
                                    freegod.discount = 0
                                    freegod.status = 1
                                    freegod.ac_source = 0
                                    freegod.pay_time = datetime.datetime.now()
                                    freegod.start_time = user_key_record.activate_time
                                    freegod.end_time = user_key_record.activate_time + datetime.timedelta(
                                        days=key_record.vip_gold_ad_time)
                                    freegod.category = 1
                                    freegod.key_record_id = key.key_record_id
                                    freegod.buy_grade = 0

                                    vipmember.grade = 2
                                    # 赠送铂金会员
                                    freevip = MemberWareOrder()
                                    freevip.ware_id = 'freevip'
                                    freevip.order_number = gen_free_vip_order_num()
                                    freevip.buyer_godin_id = godaccount[0]
                                    freevip.pay_type = 2
                                    freevip.ware_price = 0
                                    freevip.discount_price = 0
                                    freevip.discount = 0
                                    freevip.status = 1
                                    freevip.ac_source = 0
                                    freevip.pay_time = datetime.datetime.now()
                                    freevip.start_time = user_key_record.activate_time
                                    freevip.end_time = user_key_record.activate_time + datetime.timedelta(
                                        days=key_record.vip_ad_time)
                                    freevip.category = 1
                                    freevip.key_record_id = key.key_record_id
                                    freevip.buy_grade = 1

                                    vipmember.valid_time = user_key_record.activate_time + datetime.timedelta(
                                        days=key_record.vip_ad_time)
                                    vipmember.gold_valid_time = user_key_record.activate_time + datetime.timedelta(
                                        days=key_record.vip_gold_ad_time)

                                    # print(godaccount)
                                    if vipmember.gold_valid_time:
                                        if vipmember.gold_valid_time > datenow:
                                            vipmember.grade = 1
                                    if vipmember.valid_time:
                                        if vipmember.valid_time > datenow:
                                            vipmember.grade = 2
                                    print('not vipmember godin_id:%s  %s  %s  %s' %( vipmember.godin_id, vipmember.valid_time,
                                          vipmember.gold_valid_time, vipmember.grade))
                                    db.session.add(vipmember)
                                    db.session.commit()

                                    if freegod:
                                        print('add freegod %s  %s' %(freegod.buyer_godin_id,freegod.end_time))
                                        db.session.add(freegod)
                                    if freevip:
                                        print('add freevip %s  %s'  %(freevip.buyer_godin_id, freevip.end_time))
                                        db.session.add(freevip)

                                    print('add key %s give_activate_status:%s' %( key.id,key.give_activate_status))

                                    num = num + 1
                                    key.give_activate_status = 1
                                    db.session.add(key)
                                    db.session.commit()
                except Exception as e:
                    print(e)
                    print(traceback.format_exc())
                    db.session.rollback()
            # db.session.commit()
                print(num)


def resetvipmember():
    app = create_app('production')
    app_context = app.app_context()
    app_context.push()

    wares = db.session.query(distinct(MemberWareOrder.buyer_godin_id)).filter(MemberWareOrder.status==0).all()

    datenow = datetime.datetime.now()

    num = 0
    for ware in wares:

        one = db.session.query(MemberWareOrder).filter(MemberWareOrder.buyer_godin_id == ware[0],
                                                       MemberWareOrder.ware_id != 'freevip',
                                                       MemberWareOrder.ware_id != 'freegod').order_by(
            MemberWareOrder.end_time.desc()).limit(1).first()
        if one:
            if one.end_time > datenow and one.status == 0:
                vip = db.session.query(VipMembers).filter(VipMembers.godin_id == one.buyer_godin_id).limit(1).first()
                if vip:
                    if vip.valid_time:

                        imeis = db.session.query(UserInfo.imei).filter(UserInfo.godin_id == ware[0])

                        userkeyrecord = db.session.query(UserKeyRecord).filter(UserKeyRecord.imei.in_(imeis)).order_by(UserKeyRecord.activate_time.desc()).limit(1).first()


                        if userkeyrecord is None:
                            continue

                        onenew = db.session.query(MemberWareOrder).filter(MemberWareOrder.buyer_godin_id == ware[0],
                                                                          MemberWareOrder.ware_id != 'freevip',
                                                                          MemberWareOrder.ware_id != 'freegod',
                                                                          MemberWareOrder.status == 1).order_by(
                            MemberWareOrder.end_time.desc()).limit(1).first()

                        key_record = db.session.query(KeyRecord).filter(
                            KeyRecord.id == one.key_record_id).limit(1).first()

                        freevip = db.session.query(MemberWareOrder).filter(MemberWareOrder.buyer_godin_id == one.buyer_godin_id,
                                                                      MemberWareOrder.ware_id == 'freevip').limit(
                            1).first()
                        freegod = db.session.query(MemberWareOrder).filter(MemberWareOrder.buyer_godin_id == one.buyer_godin_id,
                                                                      MemberWareOrder.ware_id == 'freegod').limit(
                            1).first()

                        num = num + 1
                        if onenew:

                            viptime = userkeyrecord.activate_time + datetime.timedelta(
                                        days=key_record.vip_ad_time)
                            if viptime < onenew.end_time:
                                if freevip:
                                    freevip.end_time = onenew.end_time
                                    db.session.add(freevip)
                                    print('change freevip  %s  %s  %s' %(ware[0],vip.valid_time,onenew.end_time))
                            else:
                                if freevip:
                                    freevip.end_time = viptime
                                    db.session.add(freevip)
                                    print('change freevip2  %s  %s  %s' % (ware[0], vip.valid_time, freevip.end_time))

                            godtime = userkeyrecord.activate_time + datetime.timedelta(
                                        days=key_record.vip_gold_ad_time)
                            if godtime < onenew.end_time:
                                if freegod:
                                    freegod.end_time = onenew.end_time
                                    db.session.add(freegod)
                                    print('change freegod  %s  %s  %s' % (ware[0], vip.gold_valid_time, onenew.end_time))
                            else:
                                if freegod:
                                    freegod.end_time = godtime
                                    db.session.add(freegod)
                                    print('change freegod2  %s  %s  %s' % (ware[0], vip.gold_valid_time, freegod.end_time))

                            if freevip:
                                vip.valid_time = freevip.end_time
                            if freegod:
                                vip.gold_valid_time = freegod.end_time

                            db.session.add(vip)
                            db.session.commit()

                            print('change vipmember  new %s   %s  %s ' %(
                                ware[0],vip.valid_time,vip.gold_valid_time))
                        else:

                            viptime = userkeyrecord.activate_time + datetime.timedelta(
                                days=key_record.vip_ad_time)

                            godtime = userkeyrecord.activate_time + datetime.timedelta(
                                days=key_record.vip_gold_ad_time)

                            print('change freevip1  %s  %s  %s' % (ware[0], vip.valid_time, viptime))
                            print('change freegod1  %s  %s  %s' % (ware[0], vip.gold_valid_time, godtime))


                            if freevip:
                                freevip.end_time = viptime
                                vip.valid_time = freevip.end_time

                            if freegod:
                                freegod.end_time = godtime
                                vip.gold_valid_time = freegod.end_time



                            db.session.add(vip)
                            db.session.commit()

                            print('change vipmember1  new %s   %s  %s ' % (
                                ware[0], vip.valid_time, vip.gold_valid_time))

if __name__ == '__main__':
    oldDataToNewDataOne()

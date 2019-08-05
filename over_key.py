#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime
import json
import os

from flask import current_app

from app import create_app, db, cache, redis
from app.api_1_0.models import Key, UserKeyRecord, BiReport, BiReportProtocol, KeyRecord, MemberWareOrder, UserInfo


def del_key():
    app = create_app('production')
    app_context = app.app_context()
    app_context.push()

    f = open("del.csv")  # 返回一个文件对象
    line = f.readline()  # 调用文件的 readline()方法
    i = 0
    while line:
        # print(line)
        line = f.readline()

        keyObject = db.session.query(Key).filter(Key.id == line.replace("\n", "").replace("\r", "")).limit(1).first()
        if keyObject:

            if keyObject.status != 0:
                print(keyObject.id)

            print("key :" + str(i))
            i = i + 1
            # print("key :"+str(i))

            keyObject.status = 3
            db.session.add(keyObject)
            db.session.commit()

    f.close()


def del_key_record():
    app = create_app('production')
    app_context = app.app_context()
    app_context.push()

    f = open("delkey.txt")  # 返回一个文件对象
    line = f.readline()  # 调用文件的 readline()方法
    i = 0
    while line:
        # print(line)
        line = f.readline()

        keyObject = db.session.query(UserKeyRecord).filter(
            UserKeyRecord.key_id == line.replace("\n", "").replace("\r", ""))
        for user in keyObject:
            if user.status != 0:
                print(user.key_id + " :" + str(i))
                i = i + 1
                user.status = 0
                db.session.add(user)
        db.session.commit()

    f.close()


def bi():
    app = create_app('test')
    app_context = app.app_context()
    app_context.push()

    target_date = '20190626'
    name = os.path.join(os.getcwd(), current_app.config['STATISTICS_TAG'], 'bi', target_date, 'report_d.json')
    if os.path.exists(name):
        print('read_report_d file exist')
    else:
        print('read_report_d file not exist')
        return True

    # if BiReport.query.filter_by(record_time=target_date).first() is not None:
    #     print('read_report_d already exist')
    #     return True

    dbreports = BiReportProtocol.query.filter_by(status=1).all()
    for re in dbreports:
        cache.set(str(re.we_id), '1', timeout=60 * 10)
        redis.lpush("BiReportProtocol", str(re.we_id))

    bi_default = BiReport()
    with open(os.path.join(os.getcwd(), current_app.config['STATISTICS_TAG'], 'bi',
                           target_date, 'report_d.json'), 'r') as file:
        data = file.readlines()
        for report in data:
            try:
                report = json.loads(report)

                if report['we_id'] != 'default':
                    print(report['we_id'])
                    data = cache.get(report['we_id'])
                    if data:
                        bi_report = BiReport()
                        bi_report.record_time = report['record_time']
                        bi_report.we_id = report['we_id']
                        bi_report.rank_index = report['rank_index']
                        bi_report.latent_consumer_index = report['latent_consumer_index']
                        bi_report.activite_consumer_index = report['activite_consumer_index']
                        bi_report.extend_work_heat = report['extend_work_heat']
                        bi_report.sale_work_heat = report['sale_work_heat']
                        bi_report.income_index = report['income_index']
                        bi_report.pay_index = report['pay_index']
                        bi_report.v_webusiness_index = report['v_webusiness_index']
                        # db.session.add(bi_report)
                        print('add bi_report')
                        cache.set(str(report['we_id']), '2', timeout=60 * 10)
                else:
                    bi_default.record_time = report['record_time']
                    bi_default.we_id = report['we_id']
                    bi_default.rank_index = report['rank_index']
                    bi_default.latent_consumer_index = report['latent_consumer_index']
                    bi_default.activite_consumer_index = report['activite_consumer_index']
                    bi_default.extend_work_heat = report['extend_work_heat']
                    bi_default.sale_work_heat = report['sale_work_heat']
                    bi_default.income_index = report['income_index']
                    bi_default.pay_index = report['pay_index']
                    bi_default.v_webusiness_index = report['v_webusiness_index']

            except Exception as e:
                print('read_report_d: ', e)

        db.session.commit()
        all_data = redis.lrange('BiReportProtocol', 0, -1)

        for key in all_data:
            print(key)
            data = cache.get(key.decode())
            print(data)
            if data == '1':
                print('add')
                bi_report = BiReport()
                bi_report.record_time = bi_default.record_time
                bi_report.we_id = key.decode()
                bi_report.rank_index = bi_default.rank_index
                bi_report.latent_consumer_index = bi_default.latent_consumer_index
                bi_report.activite_consumer_index = bi_default.activite_consumer_index
                bi_report.extend_work_heat = bi_default.extend_work_heat
                bi_report.sale_work_heat = bi_default.sale_work_heat
                bi_report.income_index = bi_default.income_index
                bi_report.pay_index = bi_default.pay_index
                bi_report.v_webusiness_index = bi_default.v_webusiness_index
                db.session.add(bi_report)
                db.session.commit()
        redis.delete('BiReportProtocol')
    print('read_report_d finish')


def make_key_status():

    app = create_app('test')
    app_context = app.app_context()
    app_context.push()

    query = db.session.query(KeyRecord).filter(KeyRecord.id != '00000000000000')
    current = datetime.datetime.now()
    for record in query:
        # expire_time = record.expire_time
        vip_time = record.vip_time
        key_endTime = record.create_time + datetime.timedelta(days=vip_time)
        if record.id != '00000000000001':
            if key_endTime > current:
                continue

        query_key = db.session.query(Key).filter(Key.key_record_id == record.id, Key.status==1)
        for key in query_key:
            print('key  %s' %(key.id))
            user_record = UserKeyRecord.query.filter_by(key_id=key.id)
            if user_record.first() is not None:

                for user in user_record:

                    end_vip_time = user.activate_time + datetime.timedelta(days=vip_time)
                    print('end_vip_time  %s'  %(end_vip_time))
                    if current > end_vip_time:
                        flag = True
                        if record.id == '00000000000001':
                            print(user.key_id)
                            imeis = db.session.query(UserKeyRecord.imei).filter(UserKeyRecord.key_id==key.id)
                            print(imeis)
                            if imeis:
                                userInfo = db.session.query(UserInfo.godin_id).filter(UserInfo.imei.in_(imeis))
                                print(userInfo)
                                endtime = db.session.query(MemberWareOrder.end_time).filter(
                                    MemberWareOrder.buyer_godin_id.in_(userInfo)).order_by(
                                    MemberWareOrder.end_time.desc()).limit(1).first()
                                print(endtime)
                                if endtime:
                                    if endtime < current:
                                        flag = False

                        if flag:
                            user.status = 0
                            key.status = 3
                            # db.session.add(user)
                            # db.session.add(key)
            # else:
            #     if expire_time < current.date():
            #         key.status = 2
            #         db.session.add(key)

    # db.session.commit()

    print('key: end')
    return True

if __name__ == '__main__':
    make_key_status()

#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import current_app
from app import db, create_app
import datetime
from sqlalchemy import func
from app.api_1_0.models import KeyRecord, AgentStatistics, UserKeyRecord, Key, ActKeyStatistics, Agent


def act_key_count():
    app = create_app('default')
    app_context = app.app_context()
    app_context.push()
    krecord = KeyRecord.query.order_by(KeyRecord.create_time.asc()).first()
    k_time = krecord.create_time.month
    for month in range(k_time, 11):
        if month == 10:
            n_tod = '2018' + '-' + str(month)
        else:
            n_tod = '2018' + '-0' + str(month)
        # 购买渠道
        kr = KeyRecord.query.filter(KeyRecord.oeprator == 'Godin').first()
        count = db.session.query(UserKeyRecord, func.count(UserKeyRecord.key_id.distinct())).\
            join(Key, UserKeyRecord.key_id == Key.id).filter(Key.status.in_([1, 3]),
                                                                            Key.key_record_id == kr.id,
                                                                            UserKeyRecord.activate_time.like(
                                                                                n_tod + '%')).first()
        i = 0
        if count is not None:
            if count[1] is not None:
                i = count[1]

        # 诚招代理
        kr = KeyRecord.query.filter(KeyRecord.oeprator == 'Webusiness')
        w = 0
        for k in kr:
            count = db.session.query(UserKeyRecord, func.count(UserKeyRecord.key_id.distinct())).\
                join(Key, UserKeyRecord.key_id == Key.id).filter(Key.status.in_([1, 3]),
                                                                 Key.key_record_id == k.id,
                                                                 UserKeyRecord.activate_time.like( n_tod + '%')).first()
            if count is not None:
                if count[1] is not None:
                    w += count[1]

        # 破解赠送
        kr = KeyRecord.query.filter(KeyRecord.oeprator == 'crack')
        v = 0
        for k in kr:
            count = db.session.query(UserKeyRecord, func.count(UserKeyRecord.key_id.distinct())).\
                join(Key, UserKeyRecord.key_id == Key.id).filter(Key.status.in_([1, 3]),
                                                                 Key.key_record_id == k.id,
                                                                 UserKeyRecord.activate_time.like(n_tod + '%')).first()
            if count is not None:
                if count[1] is not None:
                    v += count[1]

        # 代理渠道
        o_list = ['crack', 'Webusiness', 'Godin']
        agent = db.session.query(Agent.name.distinct())
        krr = KeyRecord.query.filter(KeyRecord.oeprator.notin_(o_list))
        a = 0
        for k in krr:
            if not k.content.startswith('内测专用') and not k.content.startswith('内部测试专用') \
                    and not k.content.startswith('上海代理') \
                    and not k.content.startswith('深圳代理') and not k.content.startswith('LY001'):
                for ag in agent:
                    if ag[0] in k.content:
                        count = db.session.query(UserKeyRecord, func.count(UserKeyRecord.key_id.distinct())).\
                            join(Key, UserKeyRecord.key_id == Key.id).filter(Key.status.in_([1, 3]),
                                                                             Key.key_record_id == k.id,
                                                                             UserKeyRecord.activate_time.
                                                                             like(n_tod + '%')).first()
                        if count is not None:
                            if count[1] is not None:
                                a += count[1]

        act_stat = ActKeyStatistics()
        act_stat.channel_buy = i
        act_stat.channel_we = w
        act_stat.channel_crack = v
        act_stat.channel_agent = a
        act_stat.year = 2018
        act_stat.month = month
        db.session.add(act_stat)

        for oep in list(set(agent)):
            t_c = 0
            t_g = 0
            k_query = KeyRecord.query.filter(KeyRecord.content.like('%' + oep[0] + '%'), KeyRecord.vip_time < 36000)
            for k in k_query:
                count = db.session.query(UserKeyRecord, func.count(UserKeyRecord.key_id.distinct())).\
                    join(Key, UserKeyRecord.key_id == Key.id).filter(Key.status.in_([1, 3]),
                                                                     Key.key_record_id == k.id,
                                                                     UserKeyRecord.activate_time.like(
                                                                         n_tod + '%')).first()
                if count is not None:
                    if count[1] is not None:
                        t_c += count[1]
            k_query = KeyRecord.query.filter(KeyRecord.content.like('%' + oep[0] + '%'), KeyRecord.vip_time >= 36000)
            for k in k_query:
                count = db.session.query(UserKeyRecord, func.count(UserKeyRecord.key_id.distinct())).\
                    join(Key, UserKeyRecord.key_id == Key.id).filter(Key.status.in_([1, 3]),
                                                                     Key.key_record_id == k.id,
                                                                     UserKeyRecord.activate_time.like(
                                                                         n_tod + '%')).first()
                if count is not None:
                    if count[1] is not None:
                        t_g += count[1]

            ag_stat = AgentStatistics()
            ag_stat.year = 2018
            ag_stat.month = month
            ag_stat.name = oep[0]
            ag_stat.try_act = t_c
            ag_stat.general_act = t_g
            db.session.add(ag_stat)

    db.session.commit()

if __name__ == '__main__':
    act_key_count()
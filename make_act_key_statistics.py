#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime

from app import db, create_app
from sqlalchemy import func, distinct, or_, and_ , desc
from app.api_1_0.models import UserKeyRecord, Key, KeyRecord, Agent, ActKeyStatistics, AgentStatistics


def make_act_key_statistics():

    app = create_app('production')
    app_context = app.app_context()
    app_context.push()

    today_now = datetime.datetime.now()
    last_time = today_now - datetime.timedelta(days=40)
    tod = str(today_now.date()).rsplit('-')
    last = str(last_time.date()).rsplit('-')
    if tod[0] != last[0]:
        tod[0] = last[0]
    if tod[1] != last[1]:
        tod[1] = last[1]
    n_tod = tod[0] + '-' + tod[1]

    # # 购买渠道
    # kr = KeyRecord.query.filter(KeyRecord.oeprator == 'Godin').limit(1).first()
    #
    # count = db.session.query(UserKeyRecord, func.count(UserKeyRecord.key_id.distinct())). \
    #     join(Key, UserKeyRecord.key_id == Key.id).filter(Key.status.in_([1, 3]),
    #                                                      Key.key_record_id == kr.id,
    #                                                      UserKeyRecord.activate_time.like(n_tod + '%')).limit(1).first()
    # i = 0
    # if count is not None:
    #     if count[1] is not None:
    #         i = count[1]
    #
    # # 诚招代理
    # kr = KeyRecord.query.filter(KeyRecord.oeprator == 'Webusiness')
    # w = 0
    # for k in kr:
    #     count = db.session.query(UserKeyRecord, func.count(UserKeyRecord.key_id.distinct())). \
    #         join(Key, UserKeyRecord.key_id == Key.id).filter(Key.status.in_([1, 3]),
    #                                                          Key.key_record_id == k.id,
    #                                                          UserKeyRecord.activate_time.like(n_tod + '%')).limit(
    #         1).first()
    #     if count is not None:
    #         if count[1] is not None:
    #             w += count[1]
    #
    # # 破解赠送
    # kr = KeyRecord.query.filter(KeyRecord.oeprator == 'crack')
    # v = 0
    # for k in kr:
    #     count = db.session.query(UserKeyRecord, func.count(UserKeyRecord.key_id.distinct())). \
    #         join(Key, UserKeyRecord.key_id == Key.id).filter(Key.status.in_([1, 3]),
    #                                                          Key.key_record_id == k.id,
    #                                                          UserKeyRecord.activate_time.like(n_tod + '%')).limit(
    #         1).first()
    #     if count is not None:
    #         if count[1] is not None:
    #             v += count[1]

    i = 0
    w = 0
    v = 0
    # 代理渠道
    o_list = ['crack', 'Webusiness', 'Godin']
    krr = KeyRecord.query.all()
    agent = db.session.query(Agent.name.distinct())
    a = 0
    for k in krr:
        if not k.content.startswith('内测专用') and not k.content.startswith('内部测试专用') \
                and not k.content.startswith('上海代理') \
                and not k.content.startswith('深圳代理') and not k.content.startswith('LY001'):

            count = db.session.query(UserKeyRecord, func.count(UserKeyRecord.key_id.distinct())). \
                join(Key, UserKeyRecord.key_id == Key.id).filter(Key.status.in_([1, 3]),
                                                                 Key.key_record_id == k.id,
                                                                 func.date_format(UserKeyRecord.activate_time,'%Y-%m')==n_tod).first()
            if count is not None:
                if count[1] is not None:
                    a += count[1]

    act_stat = db.session.query(ActKeyStatistics).filter(ActKeyStatistics.year==tod[0], ActKeyStatistics.month==tod[1]).limit(1).first()
    if act_stat is None:
        act_stat = ActKeyStatistics()
        act_stat.channel_buy = i
        act_stat.channel_we = w
        act_stat.channel_crack = v
        act_stat.channel_agent = a
        act_stat.year = tod[0]
        act_stat.month = tod[1]
        print("act_stat: %s   %s   %s  %s" %(act_stat.channel_agent, act_stat.channel_crack, act_stat.channel_buy, act_stat.channel_we))
        # db.session.add(act_stat)
    else:
        act_stat.channel_buy = i
        act_stat.channel_we = w
        act_stat.channel_crack = v
        act_stat.channel_agent = a
        act_stat.year = tod[0]
        act_stat.month = tod[1]
        print("exist act_stat: %s   %s   %s  %s" % (act_stat.channel_agent, act_stat.channel_crack, act_stat.channel_buy, act_stat.channel_we))
        # db.session.add(act_stat)

    # for oep in list(set(agent)):
    #     t_c = 0
    #     t_g = 0
    #     k_query = KeyRecord.query.filter(KeyRecord.content.like('%' + oep[0] + '%'), KeyRecord.vip_time < 36000)
    #     for k in k_query:
    #         count = db.session.query(UserKeyRecord, func.count(UserKeyRecord.key_id.distinct())). \
    #             join(Key, UserKeyRecord.key_id == Key.id).filter(Key.status.in_([1, 3]),
    #                                                              Key.key_record_id == k.id,
    #                                                              UserKeyRecord.activate_time.like(n_tod + '%')).limit(
    #             1).first()
    #         if count is not None:
    #             if count[1] is not None:
    #                 t_c += count[1]
    #     k_query = KeyRecord.query.filter(KeyRecord.content.like('%' + oep[0] + '%'), KeyRecord.vip_time >= 36000)
    #     for k in k_query:
    #         count = db.session.query(UserKeyRecord, func.count(UserKeyRecord.key_id.distinct())). \
    #             join(Key, UserKeyRecord.key_id == Key.id).filter(Key.status.in_([1, 3]),
    #                                                              Key.key_record_id == k.id,
    #                                                              UserKeyRecord.activate_time.like(n_tod + '%')).limit(
    #             1).first()
    #         if count is not None:
    #             if count[1] is not None:
    #                 t_g += count[1]
    #     agent_stat = db.session.query(AgentStatistics).filter_by(AgentStatistics.year==tod[0], AgentStatistics.month==tod[1], AgentStatistics.name==oep[0]).limit(1).first()
    #     if agent_stat is None:
    #         ag_stat = AgentStatistics()
    #         ag_stat.year = tod[0]
    #         ag_stat.month = tod[1]
    #         ag_stat.name = oep[0]
    #         ag_stat.try_act = t_c
    #         ag_stat.general_act = t_g
    #         # db.session.add(ag_stat)
    #     else:
    #         agent_stat.year = tod[0]
    #         agent_stat.month = tod[1]
    #         agent_stat.name = oep[0]
    #         agent_stat.try_act = t_c
    #         agent_stat.general_act = t_g
    #         # db.session.add(agent_stat)

    db.session.commit()
    print('key_statistics: end')
    return True

if __name__ == '__main__':
    make_act_key_statistics()

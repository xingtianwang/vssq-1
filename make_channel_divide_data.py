#!/usr/bin/env python
# -*- coding:utf-8 -*-
from sqlalchemy import func

from app import db, create_app
from app.api_1_0.models import ChannelAccount, InviteEarnRecord, Wallet



def make_data():
    """
    给 Wallet 的总分成和推广分成赋值
    :return:
    """
    app = create_app('default')
    app_context = app.app_context()
    app_context.push()

    # 获取所有代理渠道
    all_wallet = Wallet.query.all()
    for wallet in all_wallet:
        # 获取渠道名称
        channel_account = ChannelAccount.query.get(wallet.channel_account_id)
        if channel_account:
            invite_earn = InviteEarnRecord.query.with_entities(func.sum(InviteEarnRecord.channel_earn)).filter_by(
                channel_id=channel_account.channel_id).first()[0]
            if invite_earn:
                from app.api_1_0.utils import deal_float
                wallet.gener_divide = deal_float(invite_earn / 100)
                wallet.all_divide = deal_float(wallet.gener_divide + float(wallet.income))
                db.session.add(wallet)
        try:
            db.session.commit()
            print("成功咯")
        except Exception as e:
            print("失败 ---->", e)
            print("失败 ---->", str(wallet.id))
            db.session.rollback()


if __name__ == '__main__':
    make_data()

#!/usr/bin/env python
# -*- coding:utf-8 -*-

from app import db, create_app
from app.api_1_0.models import UserGeneralize, InviteInfo, GodinAccount, UserInfo, UserKeyRecord, Key, KeyRecord, \
    ChannelAccount, KeyOrder, InviteEarnRecord, MemberWareOrder, MemberWare, MemberEarnRecord


def make_data():
    app = create_app('default')
    app_context = app.app_context()
    app_context.push()

    # 获取所有有邀请链接的用户
    all_user = UserGeneralize.query.all()
    for user in all_user:
        # 获取当前用户邀请的所有人
        invite_info = InviteInfo.query.filter_by(inviter_godin_id=user.godin_id).all()
        for info in invite_info:
            # 判断当前被邀请者是否注册
            user_info = UserInfo.query.filter_by(godin_id=info.godin_id).limit(1).first()
            if user_info:
                # 通过 imei 查询当前被邀请者所绑定的 key_id
                user_key_record = UserKeyRecord.query.filter_by(imei=user_info.imei, status=1).first()
                # 判断当前 key 是否已分成, 已分成则不做处理
                invite_record = InviteEarnRecord.query.filter_by(key_id=user_key_record.key_id).first()
                if not invite_record:
                    # 将邀请人的已注册人数加1
                    user.register_person_num += 1
                    # 将邀请人的付款人数加1
                    user.pay_person_num += 1

                    if user_key_record:
                        # 查询 key 是否是在线上购买的
                        key_order = KeyOrder.query.filter_by(key_id=user_key_record.key_id, status=1).limit(1).first()
                        if key_order:
                            # 找到邀请人的上级渠道，判断是否需要分成
                            # 找到当前用户的 imei
                            inviter_user_info = UserInfo.query.filter_by(godin_id=user.godin_id).limit(1).first()
                            # 通过 imei 查询当前用户所绑定的 key_id
                            inviter_user_key_record = UserKeyRecord.query.filter_by(imei=inviter_user_info.imei, status=1).first()

                            key = Key.query.filter_by(id=inviter_user_key_record.key_id).limit(1).first()
                            key_record = KeyRecord.query.filter_by(id=key.key_record_id).limit(1).first()
                            # 找到邀请者对应的渠道
                            channel_account = ChannelAccount.query.filter_by(id=key_record.channel_account_id).limit(1).first()

                            # 讲该条记录存入key的收益表
                            invite_earn = InviteEarnRecord()
                            invite_earn.godin_id = user.godin_id
                            invite_earn.channel_id = channel_account.channel_id
                            invite_earn.channel_name = channel_account.channel_name
                            invite_earn.phone_num = user.phone_num
                            invite_earn.be_invited_phone = info.phone_num
                            invite_earn.key_id = user_key_record.key_id
                            invite_earn.price = key_order.price
                            from app.manage.helper import get_invite_channel_divide
                            inviter_divide, channel_divide = get_invite_channel_divide()
                            invite_earn.inviter_per = inviter_divide
                            invite_earn.channel_per = channel_divide
                            invite_earn.inviter_earn = key_order.price * inviter_divide
                            invite_earn.channel_earn = key_order.price * channel_divide
                            if channel_account.channel_id == "qd0000":
                                invite_earn.channel_per = 0
                                invite_earn.channel_earn = 0

                            # 获取被邀请者的注册时间作为分成记录时间
                            godin_account = GodinAccount.query.filter_by(godin_id=user.godin_id).first()
                            invite_earn.create_time = godin_account.create_time
                            print("InviteEarnRecord = {0}, phone = {1}, be_invited_phone = {2}, key_id = {3}, "
                                  "key_price = {4}, inviter_earn = {5}, channel_id = {6}, channel_earn = {7}".format(
                                    invite_earn.godin_id, invite_earn.phone_num, invite_earn.be_invited_phone,
                                    invite_earn.key_id, invite_earn.price, invite_earn.inviter_earn, invite_earn.channel_id,
                                    invite_earn.channel_earn))

                            db.session.add(invite_earn)

                            # 将邀请者的激活码收益和余额加上 key 的收益
                            user.active_code_award += key_order.price * inviter_divide
                            user.account_balance += key_order.price * inviter_divide

                # 判断会员是否已分成
                godin_record = GodinAccount.query.filter_by(godin_id=info.godin_id).first()
                member_record = MemberEarnRecord.query.filter_by(be_invited_phone=godin_record.phone_num).first()
                if member_record:
                    continue

                # 判断已注册用户是否购买会员
                ware_orders = MemberWareOrder.query.filter_by(buyer_godin_id=info.godin_id, status=1, category=0).all()
                for ware_order in ware_orders:
                    if ware_order:
                        # 购买的商品类型
                        ware_info = MemberWare.query.filter_by(id=ware_order.ware_id).first()
                        # 生成会员分成记录
                        member_earn = MemberEarnRecord()
                        member_earn.godin_id = user.godin_id
                        member_earn.price = ware_order.discount_price
                        member_earn.member_type = ware_info.gold_or_platinum
                        member_earn.member_name = ware_info.name
                        member_earn.phone_num = user.phone_num
                        member_earn.be_invited_phone = info.phone_num
                        from app.manage.helper import get_member_divide
                        member_earn.member_divide = get_member_divide()
                        member_earn.member_earn = member_earn.price * member_earn.member_divide
                        member_earn.create_time = ware_order.create_time

                        # 将邀请者的会员收益和余额加上当前收益
                        user.member_award += member_earn.price * member_earn.member_divide
                        user.account_balance += member_earn.price * member_earn.member_divide
                        print("MemberEarnRecord = {0}, phone = {1}, be_invited_phone = {2}, member_price = {3}, "
                              "member_earn = {4}".format(member_earn.godin_id, member_earn.phone_num,
                                                         member_earn.be_invited_phone, member_earn.price,
                                                         member_earn.member_earn))

                        db.session.add(member_earn)
                print("UserGeneralize = {0}, register_person_num = {1}, active_code_award = {2}, member_award = {3}, "
                      "account_balance = {4}".format(user.godin_id, user.register_person_num, user.active_code_award,
                                                     user.member_award, user.account_balance))
                db.session.add(user)
        try:
            db.session.commit()
            print("成功咯")
        except Exception as e:
            print("失败 ---->", e)
            print("失败 ---->", str(user.godin_id))
            db.session.rollback()


if __name__ == '__main__':
    make_data()

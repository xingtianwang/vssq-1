import datetime

from sqlalchemy import or_

from app import cache
from app.api_1_0.models import InviteEarnRecord, ChannelAccount, KeyRecord, UserKeyRecord, Key, UserInfo, KeyOrder, \
    UserGeneralize, InviteInfo, MemberWareOrder, MemberEarnRecord, MemberWare, Wallet
from app.manage.models import KeyValue


def get_invite_channel_divide():
    # 获取邀请者分成比例和渠道分成比例
    inviter_divide = cache.get('inviter_divide')
    channel_divide = cache.get('channel_divide')
    if not inviter_divide or not channel_divide:
        record = KeyValue.query.filter(or_(KeyValue.key == "inviter_divide", KeyValue.key == "channel_divide")).all()
        for item in record:
            if item.key == "inviter_divide":
                inviter_divide = item.value
                cache.set('inviter_divide', item.value, timeout=12 * 60 * 60)
            else:
                channel_divide = item.value
                cache.set('channel_divide', item.value, timeout=12 * 60 * 60)
    return float(inviter_divide), float(channel_divide)


def get_member_divide():
    # 获取会员分成比例
    member_divide = cache.get('member_divide')
    if not member_divide:
        record = KeyValue.query.filter_by(key="member_divide").limit(1).first()
        member_divide = record.value
        cache.set('member_divide', record.value, timeout=12 * 60 * 60)
    return float(member_divide)


def key_is_divide(db, phone_num, imei, is_new_user):
    """
    判断当前激活的key是否需要分成
    :param db: 操作数据库的实例对象
    :param phone_num: 手机号
    :param imei: imei 号
    :param is_new_user: 是否是新用户
    """
    # 检测该用户是否是被邀请用户
    invite = InviteInfo.query.filter_by(phone_num=phone_num).limit(1).first()
    if invite:
        # 通过被邀请人找到邀请人
        user_gener = UserGeneralize.query.filter_by(godin_id=invite.inviter_godin_id).limit(1).first()
        if is_new_user:
            # 将邀请者的注册人数加1
            user_gener.register_person_num += 1

        # 通过 imei 查询当前所绑定的 key_id, 并且 key 的激活时间大于 7月6号 的才进行分成操作
        activite = datetime.datetime.strptime("2019-07-06 00:00:00", '%Y-%m-%d %H:%M:%S')
        user_key = UserKeyRecord.query.filter_by(imei=imei, status=1).filter(UserKeyRecord.activate_time > activite).first()
        if user_key:
            # 查询 key 是否是在线上购买的
            key_order = KeyOrder.query.filter_by(key_id=user_key.key_id, status=1).limit(1).first()
            if key_order:
                # 如果是线上购买的,判断是否有分成记录,没有才进行分成
                invite_earn = InviteEarnRecord.query.filter_by(key_id=user_key.key_id).first()
                if not invite_earn:
                    # 分成操作, 获取当前邀请者的上级渠道
                    user_info = UserInfo.query.filter_by(godin_id=invite.inviter_godin_id).limit(1).first()
                    # 根据 imei 查询到邀请者最新的 key_id
                    if user_info:
                        user_key_record = UserKeyRecord.query.filter_by(imei=user_info.imei, status=1).first()
                        if user_key_record:
                            key = Key.query.filter_by(id=user_key_record.key_id).limit(1).first()
                            if key:
                                key_record = KeyRecord.query.filter_by(id=key.key_record_id).limit(1).first()
                                if key_record:
                                    # 找到邀请者对应的渠道
                                    channel_account = ChannelAccount.query.filter_by(
                                        id=key_record.channel_account_id).limit(1).first()
                                    # 讲该条记录存入key的收益表
                                    invite_earn = InviteEarnRecord()
                                    invite_earn.godin_id = user_gener.godin_id
                                    invite_earn.channel_id = channel_account.channel_id
                                    invite_earn.channel_name = channel_account.channel_name
                                    invite_earn.phone_num = user_gener.phone_num
                                    invite_earn.be_invited_phone = invite.phone_num
                                    invite_earn.key_id = user_key.key_id
                                    invite_earn.price = key_order.price
                                    inviter_divide, channel_divide = get_invite_channel_divide()
                                    invite_earn.inviter_per = inviter_divide
                                    invite_earn.channel_per = channel_divide
                                    invite_earn.inviter_earn = key_order.price * inviter_divide
                                    invite_earn.channel_earn = key_order.price * channel_divide
                                    # 渠道分成
                                    wallet = Wallet.query.filter_by(channel_account_id=channel_account.id).limit(1).first()
                                    if wallet:
                                        wallet.gener_divide += key_order.price * channel_divide
                                        wallet.all_divide += key_order.price * channel_divide
                                        db.session.add(wallet)
                                    if channel_account.channel_id == "qd0000":
                                        invite_earn.channel_per = 0
                                        invite_earn.channel_earn = 0
                                    invite_earn.create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    db.session.add(invite_earn)
                                    # 将邀请者的激活码收益和余额加上 key 的收益
                                    user_gener.active_code_award += key_order.price * inviter_divide
                                    user_gener.account_balance += key_order.price * inviter_divide
        db.session.add(user_gener)


def member_earn_divide(db, order_number):
    """
    判断当前购买会员的用户是否被邀请, 被邀请则给邀请者分成
    :param db: db: 操作数据库的实例对象
    :param order_number: 订单编号
    """
    # 根据订单编号获取会员购买信息
    ware_order = MemberWareOrder.query.filter_by(order_number=order_number).first()
    # 检测该用户是否是被邀请用户
    invite = InviteInfo.query.filter_by(godin_id=ware_order.buyer_godin_id).limit(1).first()
    if invite:
        # 购买的商品类型
        ware_info = MemberWare.query.filter_by(id=ware_order.ware_id).first()
        # 通过被邀请人找到邀请人
        user_gener = UserGeneralize.query.filter_by(godin_id=invite.inviter_godin_id).limit(1).first()
        if user_gener:
            # 生成会员分成记录
            member_earn = MemberEarnRecord()
            member_earn.godin_id = user_gener.godin_id
            member_earn.price = ware_order.discount_price
            member_earn.member_type = ware_info.gold_or_platinum
            member_earn.member_name = ware_info.name
            member_earn.phone_num = user_gener.phone_num
            member_earn.be_invited_phone = invite.phone_num
            member_earn.member_divide = get_member_divide()
            member_earn.member_earn = member_earn.price * member_earn.member_divide
            member_earn.create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 付款人数加1
            user_gener.pay_person_num += 1
            # 将邀请者的会员收益和余额加上当前收益
            user_gener.member_award += member_earn.price * member_earn.member_divide
            user_gener.account_balance += member_earn.price * member_earn.member_divide
            db.session.add(member_earn)
            db.session.add(user_gener)


def get_pay_person_num(godin_id):
    # 根据收益记录表计算付款人数
    # 获取所有邀请人
    invite_info = InviteInfo.query.filter_by(inviter_godin_id=godin_id).all()
    pay_person_num = 0
    for info in invite_info:
        # 分别获取 key 收益和会员收益
        key_award = InviteEarnRecord.query.filter_by(be_invited_phone=info.phone_num).first()
        if key_award:
            pay_person_num += 1
            continue
        member_award = MemberEarnRecord.query.filter_by(be_invited_phone=info.phone_num).first()
        if member_award:
            pay_person_num += 1
            continue
    return pay_person_num
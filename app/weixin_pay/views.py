#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2017 Godinsec. All rights reserved.
#   File Name: views.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 2017/2/24
# *************************************************************************
import datetime

from flask import Response
from flask import request
from flask_restful import Resource
from flask_restful import reqparse

from app import db
from app.api_1_0.errors import ErrorCode
from app.api_1_0.models import MemberWareOrder, VipMembers, MemberWare, VipType, KeyOrder, KeyRecord, Key, \
    BusinessWareOrder, BusinessWare, BusinessType, BusinessMembers, UserPayTime, GodinAccount
from app.helper import print_error
from app.manage.helper import member_earn_divide
from app.weixin_pay.models import WeixinPayResults
from app.weixin_pay.new_weixin_pay import AvatarWexinPay
from app.weixin_pay.utils import gen_order_id
from app.weixin_pay.weixin_pay import WexinPay


class UnifiedOrderApi(Resource):

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('goods_id', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('total_fee', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('description', type=str, required=True, help='param missing', location='json')
        super(UnifiedOrderApi, self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()
        print(json_req)
        order_id = gen_order_id()
        res = WexinPay().unified_order(out_trade_no=order_id, total_fee=int(json_req['total_fee']),
                                       body=json_req['description'], trade_type='APP')
        return res


class ResultAsynNoticeApi(Resource):

    def __init__(self):
        super(ResultAsynNoticeApi, self).__init__()

    def post(self):
        print("receive data:", request.data.decode('utf-8'))

        weixin_pay = WexinPay()
        # xml data
        ret = weixin_pay.reply(ret_msg=request.data.decode('utf-8'))
        # dict data
        ret_info = weixin_pay.xml_to_dict(ret)
        # print("response data: ", ret, ret_info)
        if ret_info['return_code'] == 'SUCCESS':
            res = weixin_pay.xml_to_dict(request.data.decode('utf-8'))
            wx_res = WeixinPayResults.query.filter_by(transaction_id=res['transaction_id']).first()
            if wx_res is None:
                wx_res = WeixinPayResults()
                wx_res.appid = res['appid']
                wx_res.mch_id = res['mch_id']
                if 'device_info' in res:
                    wx_res.device_info = res['device_info']
                wx_res.nonce_str = res['nonce_str']
                wx_res.sign = res['sign']
                wx_res.result_code = res['result_code']
                if 'err_code' in res:
                    wx_res.err_code = res['err_code']
                if 'err_code_des' in res:
                    wx_res.err_code_des = res['err_code_des']
                wx_res.openid = res['openid']
                if 'is_subscribe' in res:
                    wx_res.is_subscribe = res['is_subscribe']
                wx_res.trade_type = res['trade_type']
                wx_res.bank_type = res['bank_type']
                wx_res.total_fee = res['total_fee']
                if 'fee_type' in res:
                    wx_res.fee_type = res['fee_type']
                wx_res.cash_fee = res['cash_fee']
                if 'coupon_fee' in res:
                    wx_res.coupon_fee = res['coupon_fee']
                if 'coupon_count' in res:
                    wx_res.coupon_count = res['coupon_count']
                if 'err_code_des' in res:
                    wx_res.err_code_des = res['err_code_des']
                wx_res.transaction_id = res['transaction_id']
                wx_res.out_trade_no = res['out_trade_no']
                if 'attach'in res:
                    wx_res.attach = res['attach']
                wx_res.time_end = res['time_end']
                db.session.add(wx_res)

            # key order
            if res['out_trade_no'].startswith('key'):
                key_order = KeyOrder.query.filter_by(id=res['out_trade_no']).with_lockmode('update').first()
                if key_order is not None and key_order.status == 0:
                    key_order.pay_time = datetime.datetime.now()
                    key_order.status = 1
                    db.session.add(key_order)
                    key_info = Key.query.filter_by(id=key_order.key_id).with_lockmode('update').first()
                    if key_info is None:
                        key_record = KeyRecord.query.filter_by(id='00000000000000').with_lockmode('update').first()
                        if key_record is not None:
                            key_record.count += 1
                            db.session.add(key_record)
                            key = Key()
                            key.key_record_id = key_record.id
                            key.id = key_order.key_id
                            db.session.add(key)
                            db.session.commit()
            else:
                ware_order = MemberWareOrder.query.filter_by(order_number=res['out_trade_no']).with_lockmode(
                    'update').first()
                if ware_order is not None and ware_order.status == 0:
                    # 添加支付时间的记录
                    godin_account = GodinAccount.query.filter_by(godin_id=ware_order.buyer_godin_id).limit(1).first()
                    user_pay_time = UserPayTime()
                    user_pay_time.phone_num = godin_account.phone_num
                    user_pay_time.status = 1
                    db.session.add(user_pay_time)
                    db.session.commit()

                    vip_user = VipMembers.query.filter_by(godin_id=ware_order.buyer_godin_id).first()

                    # 用户不存在时
                    if vip_user is None:
                        db.session.commit()
                        print_error(action='Response', function=self.__class__.__name__, branch='vip_user is null',
                                    buyer_godin_id=ware_order.buyer_godin_id, transaction_id=res['transaction_id'])

                        return Response(ret, status=200, mimetype='application/xml')

                    ware_info = MemberWare.query.filter_by(id=ware_order.ware_id).first()
                    if ware_info is not None:
                        # 获取升级至黄金（grade = 1）还是铂金(grade = 2)

                        # 验证用户vip是否过期
                        gradechange = False     # 是否grade需要改变
                        if vip_user.grade == 2:
                            if vip_user.valid_time and vip_user.valid_time > datetime.datetime.now():
                                pass
                            else:
                                vip_user.grade = 1
                                gradechange = True

                        if vip_user.grade == 1:
                            if vip_user.gold_valid_time and vip_user.gold_valid_time > datetime.datetime.now():
                                pass
                            else:
                                vip_user.grade = 0
                                gradechange = True
                        # 修改grade字段
                        if gradechange:
                            db.session.add(vip_user)
                            db.session.commit()

                        if vip_user.grade == 2 or vip_user.grade == 3:
                            if ware_info.gold_or_platinum == 1:
                                old_order = MemberWareOrder.query.filter_by(buyer_godin_id=ware_order.buyer_godin_id,
                                                                            status=1). \
                                    order_by(MemberWareOrder.pay_time.desc()).first()
                            else:
                                db.session.commit()

                                print_error(action='Response', function=self.__class__.__name__,
                                            branch='supervip can not pay godvip',
                                            buyer_godin_id=ware_order.buyer_godin_id,
                                            transaction_id=res['transaction_id'])

                                return Response(ret, status=200, mimetype='application/xml')
                        else:
                            old_order = MemberWareOrder.query.filter_by(buyer_godin_id=ware_order.buyer_godin_id,
                                                                        status=1, buy_grade=ware_info.gold_or_platinum)\
                                .order_by(MemberWareOrder.pay_time.desc()).first()
                        if old_order is not None:
                            # 最后一个付款订单结束的时间的下一秒
                            if old_order.end_time < datetime.datetime.now():
                                ware_order.start_time = datetime.datetime.now()
                            else:
                                ware_order.start_time = old_order.end_time + datetime.timedelta(seconds=1)
                        else:
                            ware_order.start_time = datetime.datetime.now()

                        vip_type = VipType.query.filter_by(number=ware_info.category).first()
                        if vip_type is not None:
                            ware_order.end_time = ware_order.start_time + datetime.timedelta(days=vip_type.days)

                    ware_order.status = 1
                    ware_order.pay_time = datetime.datetime.now()

                    if vip_user is not None:
                        # 获取升级至黄金（grade = 1）还是铂金(grade = 2)
                        if vip_user.grade == 2 or vip_user.grade == 3:
                            vip_user.valid_time = ware_order.end_time
                            vip_user.grade = 2
                        else:
                            if ware_info.gold_or_platinum == 1:
                                vip_user.valid_time = ware_order.end_time
                                vip_user.grade = 2
                            else:
                                vip_user.gold_valid_time = ware_order.end_time
                                vip_user.grade = 1

                        if not vip_user.first_pay_time:
                            vip_user.first_pay_time = datetime.datetime.now()
                        if vip_user.status == 0:
                            vip_user.status = 1
                        vip_user.cur_pay_cate = ware_info.category
                        db.session.add(vip_user)
                    db.session.add(ware_order)
                    # 添加会员收益记录
                    member_earn_divide(db, res['out_trade_no'])
            db.session.commit()
        return Response(ret, status=200, mimetype='application/xml')


class OrderQueryApi(Resource):

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('transaction_id', type=str, help='param missing', location='json')
        self.req_parse.add_argument('out_trade_no', type=str, help='param missing', location='json')
        super(OrderQueryApi, self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()
        print(json_req)
        ret_info = WexinPay().order_query(out_trade_no=json_req['out_trade_no'])
        if json_req['out_trade_no'].startswith('key'):
            if ret_info['return_code'] == 'SUCCESS' and ret_info['result_code'] == 'SUCCESS' \
                    and ret_info['trade_state'] == 'SUCCESS':
                # key order
                key_order = KeyOrder.query.filter_by(id=json_req['out_trade_no']).with_lockmode('update').first()
                if key_order is not None:
                    print('QuertOrder000 ', key_order.id, key_order.status)
                    if key_order.status == 1:
                        pass
                    else:
                        if ret_info['result_code'] == 'SUCCESS':
                            key_order.status = 1
                            key_order.pay_time = datetime.datetime.now()
                            db.session.add(key_order)
                            key_info = Key.query.filter_by(id=key_order.key_id).with_lockmode('update').first()
                            if key_info is None:
                                key_record = KeyRecord.query.filter_by(id='00000000000000').with_lockmode(
                                    'update').first()
                                if key_record is not None:
                                    key_record.count += 1
                                    db.session.add(key_record)
                                    key = Key()
                                    key.key_record_id = key_record.id
                                    key.id = key_order.key_id
                                    db.session.add(key)
                            print("支付成功")
                        else:
                            # 支付失败时设置状态
                            db.session.delete(key_order)
                            print("支付失败: ", key_order.id, key_order.status)

                    db.session.commit()
                if key_order.status == 1:
                    print('QuertOrder111 ', key_order.id, key_order.status)
                    return {'head': ErrorCode.SUCCESS, "body": {"key_id": key_order.key_id}}
                else:
                    print('QuertOrder333 ', key_order.id)
                    return {'head': ErrorCode.WECHAT_PAY_FAILURE}
            else:
                return {'head': ErrorCode.WECHAT_PAY_FAILURE}
        else:
            return {'head': ErrorCode.SUCCESS}


class CloseOrderApi(Resource):

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('out_trade_no', type=str, required=True, help='param missing', location='json')
        super(CloseOrderApi, self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()
        print(json_req)
        res = WexinPay().close_order(out_trade_no=json_req['out_trade_no'])
        return res


class DownloadBillApi(Resource):

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('bill_date', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('bill_type', type=str, required=True, help='param missing', location='json')
        super(DownloadBillApi, self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()
        print(json_req)
        total, detail = WexinPay().download_bill(bill_date=json_req['bill_date'], bill_type=json_req['bill_type'])
        return detail


class NewUnifiedOrderApi(Resource):

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('goods_id', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('total_fee', type=str, required=True, help='param missing', location='json')
        self.req_parse.add_argument('description', type=str, required=True, help='param missing', location='json')
        super(NewUnifiedOrderApi, self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()
        print(json_req)
        order_id = gen_order_id()
        res = AvatarWexinPay().unified_order(out_trade_no=order_id, total_fee=int(json_req['total_fee']),
                                       body=json_req['description'], trade_type='APP')
        return res


class NewResultAsynNoticeApi(Resource):

    def __init__(self):
        super(NewResultAsynNoticeApi, self).__init__()

    def post(self):
        # print("receive data:", request.data.decode('utf-8'))

        weixin_pay = AvatarWexinPay()
        # xml data
        ret = weixin_pay.reply(ret_msg=request.data.decode('utf-8'))
        # dict data
        ret_info = weixin_pay.xml_to_dict(ret)
        # print("response data: ", ret, ret_info)
        if ret_info['return_code'] == 'SUCCESS':
            res = weixin_pay.xml_to_dict(request.data.decode('utf-8'))
            wx_res = WeixinPayResults.query.filter_by(transaction_id=res['transaction_id']).first()
            if wx_res is None:
                wx_res = WeixinPayResults()
                wx_res.appid = res['appid']
                wx_res.mch_id = res['mch_id']
                if 'device_info' in res:
                    wx_res.device_info = res['device_info']
                wx_res.nonce_str = res['nonce_str']
                wx_res.sign = res['sign']
                wx_res.result_code = res['result_code']
                if 'err_code' in res:
                    wx_res.err_code = res['err_code']
                if 'err_code_des' in res:
                    wx_res.err_code_des = res['err_code_des']
                wx_res.openid = res['openid']
                if 'is_subscribe' in res:
                    wx_res.is_subscribe = res['is_subscribe']
                wx_res.trade_type = res['trade_type']
                wx_res.bank_type = res['bank_type']
                wx_res.total_fee = res['total_fee']
                if 'fee_type' in res:
                    wx_res.fee_type = res['fee_type']
                wx_res.cash_fee = res['cash_fee']
                if 'coupon_fee' in res:
                    wx_res.coupon_fee = res['coupon_fee']
                if 'coupon_count' in res:
                    wx_res.coupon_count = res['coupon_count']
                if 'err_code_des' in res:
                    wx_res.err_code_des = res['err_code_des']
                wx_res.transaction_id = res['transaction_id']
                wx_res.out_trade_no = res['out_trade_no']
                if 'attach'in res:
                    wx_res.attach = res['attach']
                wx_res.time_end = res['time_end']
                db.session.add(wx_res)
                db.session.commit()

            # VIP
            if res['out_trade_no'].startswith('ava'):
                ware_order = MemberWareOrder.query.filter_by(order_number=res['out_trade_no']).with_lockmode(
                    'update').first()
                if ware_order is not None and ware_order.status == 0:
                    # 添加支付时间的记录
                    godin_account = GodinAccount.query.filter_by(godin_id=ware_order.buyer_godin_id).limit(1).first()
                    user_pay_time = UserPayTime()
                    user_pay_time.phone_num = godin_account.phone_num
                    user_pay_time.status = 0
                    db.session.add(user_pay_time)
                    db.session.commit()

                    vip_user = VipMembers.query.filter_by(godin_id=ware_order.buyer_godin_id).first()

                    # 用户不存在时
                    if vip_user is None:
                        db.session.commit()
                        print_error(action='Response', function=self.__class__.__name__, branch='vip_user is null',
                                    buyer_godin_id=ware_order.buyer_godin_id, transaction_id=res['transaction_id'])
                        return Response(ret, status=200, mimetype='application/xml')

                    ware_info = MemberWare.query.filter_by(id=ware_order.ware_id).first()
                    if ware_info is not None:
                        old_order = MemberWareOrder.query.filter_by(buyer_godin_id=ware_order.buyer_godin_id,
                                                                    status=1).order_by(
                            MemberWareOrder.pay_time.desc()).first()
                        if old_order is not None:

                            # 验证用户vip是否过期
                            gradechange = False  # 是否grade需要改变

                            if vip_user.grade is None:
                                vip_user.grade = 2

                            if vip_user.grade == 2:
                                if vip_user.valid_time and vip_user.valid_time > datetime.datetime.now():
                                    pass
                                else:
                                    vip_user.grade = 1
                                    gradechange = True

                            if vip_user.grade == 1:
                                if vip_user.gold_valid_time and vip_user.gold_valid_time > datetime.datetime.now():
                                    pass
                                else:
                                    vip_user.grade = 0
                                    gradechange = True
                            # 修改grade字段
                            if gradechange:
                                db.session.add(vip_user)
                                db.session.commit()

                            if vip_user.grade == 2 or vip_user.grade == 3:
                                if ware_info.gold_or_platinum == 1:
                                    old_order = MemberWareOrder.query.filter_by(
                                        buyer_godin_id=ware_order.buyer_godin_id,
                                        status=1). \
                                        order_by(MemberWareOrder.pay_time.desc()).first()
                                else:
                                    db.session.commit()
                                    print_error(action='Response', function=self.__class__.__name__,
                                                branch='supervip can not pay godvip',
                                                buyer_godin_id=ware_order.buyer_godin_id,
                                                transaction_id=res['transaction_id'])

                                    return Response(ret, status=200, mimetype='application/xml')
                            else:
                                old_order = MemberWareOrder.query.filter_by(buyer_godin_id=ware_order.buyer_godin_id,
                                                                            status=1,
                                                                            buy_grade=ware_info.gold_or_platinum) \
                                    .order_by(MemberWareOrder.pay_time.desc()).first()

                            if old_order is not None:
                                # 最后一个付款订单结束的时间的下一秒
                                if old_order.end_time < datetime.datetime.now():
                                    ware_order.start_time = datetime.datetime.now()
                                else:
                                    ware_order.start_time = old_order.end_time + datetime.timedelta(seconds=1)
                            else:
                                ware_order.start_time = datetime.datetime.now()

                            vip_type = VipType.query.filter_by(number=ware_info.category).first()
                            if vip_type is not None:
                                ware_order.end_time = ware_order.start_time + datetime.timedelta(days=vip_type.days)

                            # 最后一个付款订单结束的时间的下一秒
                            if old_order.end_time < datetime.datetime.now():
                                ware_order.start_time = datetime.datetime.now()
                            else:
                                ware_order.start_time = old_order.end_time + datetime.timedelta(seconds=1)

                            ware_order.status = 1
                            ware_order.pay_time = datetime.datetime.now()

                            if vip_user is not None:
                                # 获取升级至黄金（grade = 1）还是铂金(grade = 2)
                                if vip_user.grade == 2 or vip_user.grade == 3:

                                    if ware_info.gold_or_platinum == 1:
                                        vip_user.valid_time = ware_order.end_time
                                        vip_user.grade = 2
                                    else:
                                        vip_user.gold_valid_time = ware_order.end_time
                                        vip_user.grade = 1

                                else:
                                    if ware_info.gold_or_platinum == 1:
                                        vip_user.valid_time = ware_order.end_time
                                        vip_user.grade = 2
                                    else:
                                        vip_user.gold_valid_time = ware_order.end_time
                                        vip_user.grade = 1

                                if not vip_user.first_pay_time:
                                    vip_user.first_pay_time = datetime.datetime.now()
                                if vip_user.status == 0:
                                    vip_user.status = 1
                                vip_user.cur_pay_cate = ware_info.category
                                db.session.add(vip_user)
                            db.session.add(ware_order)
                            # 添加会员收益记录
                            member_earn_divide(db, res['out_trade_no'])
                            db.session.commit()
            # 商业智能app
            elif res['out_trade_no'].startswith('Buss'):
                ware_order = BusinessWareOrder.query.filter_by(order_number=res['out_trade_no']).with_lockmode(
                    'update').first()
                if ware_order is not None and ware_order.status == 0:
                    vip_user = BusinessMembers.query.filter_by(godin_id=ware_order.buyer_godin_id).first()
                    ware_info = BusinessWare.query.filter_by(id=ware_order.ware_id).first()
                    if ware_info is not None:
                        old_order = BusinessWareOrder.query.filter_by(buyer_godin_id=ware_order.buyer_godin_id,
                                                                      status=1).order_by(
                            BusinessWareOrder.pay_time.desc()).first()
                        if old_order is not None:
                            if old_order.end_time < datetime.datetime.now():
                                if vip_user.valid_time <= datetime.datetime.now():
                                    ware_order.start_time = datetime.datetime.now()
                                else:
                                    ware_order.start_time = vip_user.valid_time
                            else:
                                if vip_user.valid_time >= old_order.end_time:
                                    ware_order.start_time = vip_user.valid_time + datetime.timedelta(seconds=1)
                                else:
                                    ware_order.start_time = old_order.end_time + datetime.timedelta(seconds=1)
                        else:
                            print('vip_user:', vip_user.valid_time)
                            if vip_user.valid_time is None:
                                ware_order.start_time = datetime.datetime.now()
                            elif vip_user.valid_time <= datetime.datetime.now():
                                ware_order.start_time = datetime.datetime.now()
                            else:
                                ware_order.start_time = vip_user.valid_time
                        vip_type = BusinessType.query.filter_by(number=ware_info.category).first()
                        if vip_type is not None:
                            ware_order.end_time = ware_order.start_time + datetime.timedelta(days=vip_type.days)

                    ware_order.status = 1
                    ware_order.pay_time = datetime.datetime.now()

                    if vip_user is not None:
                        vip_user.valid_time = ware_order.end_time
                        if not vip_user.first_pay_time:
                            vip_user.first_pay_time = datetime.datetime.now()
                        if vip_user.status == 0:
                            vip_user.status = 1
                        db.session.add(vip_user)
                    db.session.add(ware_order)
                    db.session.commit()
        return Response(ret, status=200, mimetype='application/xml')


class NewOrderQueryApi(Resource):

    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('transaction_id', type=str, help='param missing', location='json')
        self.req_parse.add_argument('out_trade_no', type=str, help='param missing', location='json')
        super(NewOrderQueryApi, self).__init__()

    def post(self):
        json_req = self.req_parse.parse_args()
        print(json_req)
        ret_info = AvatarWexinPay().order_query(out_trade_no=json_req['out_trade_no'])
        if json_req['out_trade_no'].startswith('ava'):
            if ret_info['return_code'] == 'SUCCESS' and ret_info['result_code'] == 'SUCCESS' \
                    and ret_info['trade_state'] == 'SUCCESS':
                ware_order = MemberWareOrder.query.filter_by(order_number=json_req['out_trade_no']).with_lockmode(
                    'update').first()
                if ware_order is not None and ware_order.status == 0:
                    ware_info = MemberWare.query.filter_by(id=ware_order.ware_id).first()
                    if ware_info is not None:
                        old_order = MemberWareOrder.query.filter_by(buyer_godin_id=ware_order.buyer_godin_id,
                                                                    status=1).order_by(
                            MemberWareOrder.pay_time.desc()).first()
                        if old_order is not None:
                            # 最后一个付款订单结束的时间的下一秒
                            if old_order.end_time < datetime.datetime.now():
                                ware_order.start_time = datetime.datetime.now()
                            else:
                                ware_order.start_time = old_order.end_time + datetime.timedelta(seconds=1)
                        else:
                            ware_order.start_time = datetime.datetime.now()

                        vip_type = VipType.query.filter_by(number=ware_info.category).first()
                        if vip_type is not None:
                            ware_order.end_time = ware_order.start_time + datetime.timedelta(days=vip_type.days)

                    ware_order.status = 1
                    ware_order.pay_time = datetime.datetime.now()

                    vip_user = VipMembers.query.filter_by(godin_id=ware_order.buyer_godin_id).first()
                    if vip_user is not None:
                        vip_user.valid_time = ware_order.end_time
                        if not vip_user.first_pay_time:
                            vip_user.first_pay_time = datetime.datetime.now()
                        if vip_user.status == 0:
                            vip_user.status = 1
                        vip_user.cur_pay_cate = ware_info.category
                        db.session.add(vip_user)
                    db.session.add(ware_order)
                    db.session.commit()
                if ware_order is not None and ware_order.status == 1:
                    return {'head': ErrorCode.SUCCESS}
                else:
                    return {'head': ErrorCode.WECHAT_PAY_FAILURE}
            else:
                return {'head': ErrorCode.WECHAT_PAY_FAILURE}
        elif json_req['out_trade_no'].startswith('Buss'):
            if ret_info['return_code'] == 'SUCCESS' and ret_info['result_code'] == 'SUCCESS' \
                    and ret_info['trade_state'] == 'SUCCESS':
                ware_order = BusinessWareOrder.query.filter_by(order_number=json_req['out_trade_no']).with_lockmode(
                    'update').first()
                if ware_order is not None and ware_order.status == 0:
                    ware_info = BusinessWare.query.filter_by(id=ware_order.ware_id).first()
                    vip_user = BusinessMembers.query.filter_by(godin_id=ware_order.buyer_godin_id).first()
                    if ware_info is not None:
                        old_order = BusinessWareOrder.query.filter_by(buyer_godin_id=ware_order.buyer_godin_id,
                                                                      status=1).order_by(
                            BusinessWareOrder.pay_time.desc()).first()
                        if old_order is not None:
                            if old_order.end_time < datetime.datetime.now():
                                if vip_user.valid_time <= datetime.datetime.now():
                                    ware_order.start_time = datetime.datetime.now()
                                else:
                                    ware_order.start_time = vip_user.valid_time
                            else:
                                if vip_user.valid_time >= old_order.end_time:
                                    ware_order.start_time = vip_user.valid_time + datetime.timedelta(seconds=1)
                                else:
                                    ware_order.start_time = old_order.end_time + datetime.timedelta(seconds=1)
                        else:
                            print('vip_user:', vip_user.valid_time)
                            if vip_user.valid_time is None:
                                ware_order.start_time = datetime.datetime.now()
                            elif vip_user.valid_time <= datetime.datetime.now():
                                ware_order.start_time = datetime.datetime.now()
                            else:
                                ware_order.start_time = vip_user.valid_time

                        vip_type = BusinessType.query.filter_by(number=ware_info.category).first()
                        if vip_type is not None:
                            ware_order.end_time = ware_order.start_time + datetime.timedelta(days=vip_type.days)

                    ware_order.status = 1
                    ware_order.pay_time = datetime.datetime.now()

                    if vip_user is not None:
                        vip_user.valid_time = ware_order.end_time
                        if not vip_user.first_pay_time:
                            vip_user.first_pay_time = datetime.datetime.now()
                        if vip_user.status == 0:
                            vip_user.status = 1
                        db.session.add(vip_user)
                    db.session.add(ware_order)
                    db.session.commit()
                if ware_order is not None and ware_order.status == 1:
                    return {'head': ErrorCode.SUCCESS}
                else:
                    return {'head': ErrorCode.WECHAT_PAY_FAILURE}
            else:
                return {'head': ErrorCode.WECHAT_PAY_FAILURE}
        else:
            return {'head': ErrorCode.SUCCESS}

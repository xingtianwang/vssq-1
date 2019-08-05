#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2017 Godinsec. All rights reserved.
#   File Name: urls.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 2017/2/24
# *************************************************************************
from flask import Blueprint
from flask_restful import Api

from app.weixin_pay.views import UnifiedOrderApi, ResultAsynNoticeApi, OrderQueryApi, CloseOrderApi, DownloadBillApi,\
    NewUnifiedOrderApi, NewOrderQueryApi, NewResultAsynNoticeApi

weixinpay_blueprint = Blueprint('weixinpay', __name__)
weixinpay_api = Api(weixinpay_blueprint)
weixinpay_api.add_resource(UnifiedOrderApi, '/UnifiedOrder', endpoint='UnifiedOrder')
weixinpay_api.add_resource(ResultAsynNoticeApi, '/ResultAsynNotice', endpoint='ResultAsynNotice')
weixinpay_api.add_resource(OrderQueryApi, '/OrderQuery', endpoint='OrderQuery')
weixinpay_api.add_resource(CloseOrderApi, '/CloseOrder', endpoint='CloseOrder')
weixinpay_api.add_resource(DownloadBillApi, '/DownloadBill', endpoint='DownloadBill')

weixinpay_api.add_resource(NewUnifiedOrderApi, '/u_order', endpoint='u_order')
weixinpay_api.add_resource(NewOrderQueryApi, '/q_order', endpoint='q_order')
weixinpay_api.add_resource(NewResultAsynNoticeApi, '/r_notice', endpoint='r_notice')


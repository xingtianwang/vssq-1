#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2017 Godinsec. All rights reserved.
#   File Name: models.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 2017/3/13
# *************************************************************************
from app import db


class WeixinPayResults(db.Model):
    __table_name__ = 'wxpay_results'
    appid = db.Column(db.String(32), nullable=False)
    mch_id = db.Column(db.String(32), nullable=False)
    device_info = db.Column(db.String(32), default='')
    nonce_str = db.Column(db.String(32), nullable=False)
    sign = db.Column(db.String(32), nullable=False)
    result_code = db.Column(db.String(16), nullable=False)
    err_code = db.Column(db.String(32), default='')
    err_code_des = db.Column(db.String(128), default='')
    openid = db.Column(db.String(128), nullable=False)
    is_subscribe = db.Column(db.String(1), default='N')
    trade_type = db.Column(db.String(128), nullable=False, default='APP')
    bank_type = db.Column(db.String(128), nullable=False)
    total_fee = db.Column(db.Integer, nullable=False)
    fee_type = db.Column(db.String(8), nullable=False, default='CNY')
    cash_fee = db.Column(db.Integer, nullable=False)
    cash_fee_type = db.Column(db.String(16), nullable=False, default='CNY')
    coupon_fee = db.Column(db.Integer)
    coupon_count = db.Column(db.Integer)
    transaction_id = db.Column(db.String(32), nullable=False, primary_key=True)
    out_trade_no = db.Column(db.String(32), nullable=False)
    attach = db.Column(db.String(128), default='')
    time_end = db.Column(db.String(14), nullable=False)

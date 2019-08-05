#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2017 Godinsec. All rights reserved.
#   File Name: cash_cat.py
#   Author: bao.zhang
#   Mail: bao.zhang@godinsec.com
#   Created Time: 2017/10/17
# *************************************************************************
import hashlib
import random
import string
import time
import requests
from urllib.request import quote
from flask import current_app


class CashCat(object):
    """
    变现猫生成url接口
    """

    def __init__(self):
        # self.CAT_KEY = current_app.config['CAT_KEYCAT_KEY']
        # self.CAT_SECRET = current_app.config['CAT_SECRET']
        self.CAT_KEY = '58f02938a31d4210be8ae35a870f2d3a'
        self.CAT_SECRET = 'b867891fd3734e6b8aab0974a7422024'

    def sign(self, kw):
        """
        计算签名
        :param kw: 需要签名的参数
        :return: 签名结果
        """
        dict_str = ''.join(['%s' % (str(kw[k])) for k in sorted(kw) if kw[k] is not None])
        print(dict_str)
        return hashlib.md5(bytes(dict_str, 'utf-8')).hexdigest()

    def check_sign(self, kw):
        """
        校验签名
        :param kw: 包含签名及被签名的字段
        :return: 签名结果一致返回True,否则返回False
        """
        wechat_sign = kw.pop('sign')
        return wechat_sign == self.sign(kw)

    def get_url(self, url, **data):
        """
        返回带签名url的接口
        参考 http://live.bianxianmao.com/redirect.htm?appUid=2&appType=app&sign=34528670eebb3735411b13e89d5f37d8&
        timestamp=1508223505449&appKey=58f02938a31d4210be8ae35a870f2d3a
        :param data: 字典类型参数，必须包含字段app_Uid(用户唯一标识), appType(应用类型app)
        :return: 生成拼接后的URL
        """
        url = url
        if 'appUid' not in data:
            raise Exception(msg='缺少必须参数用户id')
        if 'appType' not in data:
            raise Exception(msg='缺少必须参数应用类型')

        data.setdefault('appKey', self.CAT_KEY)
        data.setdefault('appSecret', self.CAT_SECRET)
        data.setdefault('timestamp', int(round(time.time() * 1000)))
        data.setdefault('sign', self.sign(data))

        data.pop('appSecret')
        url = url + '?' + ''.join(['%s=%s&' % (key, quote(str(data[key]).encode('utf-8'))) for key in data
                                   if data[key] is not None])
        url = url[0:len(url)-1]
        return url


# if __name__ == "__main__":
#   info = CashCat()
#   data = {
#       'appUid': 2,
#       'appType': 'app'
#   }
#   info.get_url('http://live.bianxianmao.com/redirect.htm', **data)

#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2017 Godinsec. All rights reserved.
#   File Name: weixin_pay.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 2017/2/23
# *************************************************************************
import hashlib
import random
import string
import time
import requests
import xmltodict
from flask import current_app

from app.weixin_pay.utils import process_weinxin_bill


class WexinPay(object):
    """
    微信支付接口
    """

    def __init__(self):
        self.APP_ID = current_app.config['WX_APP_ID']
        self.MCH_ID = current_app.config['WX_MCH_ID']
        self.MCH_KEY = current_app.config['WX_MCH_KEY']
        self.SPBILL_CREATE_IP = current_app.config['WX_SPBILL_CREATE_IP']
        self.NOTIFY_URL = current_app.config['WX_NOTIFY_URL']

    @property
    def nonce_str(self):
        return ''.join(random.sample(string.ascii_letters + string.digits, 32))

    @property
    def spbill_create_ip(self):
        return self.SPBILL_CREATE_IP

    @spbill_create_ip.setter
    def spbill_create_ip(self, spbill_ip):
        self.SPBILL_CREATE_IP = spbill_ip

    @property
    def notify_url(self):
        return self.NOTIFY_URL

    @notify_url.setter
    def notify_url(self, notify_url):
        self.NOTIFY_URL = notify_url

    def sign(self, kw):
        """
        计算签名
        :param kw: 需要签名的参数
        :return: 签名结果
        """
        dict_str = '&'.join(['%s=%s' % (k, str(kw[k])) for k in sorted(kw) if kw[k] is not None])
        dict_str += '&key=' + self.MCH_KEY
        return hashlib.md5(bytes(dict_str, 'utf-8')).hexdigest().upper()

    def check_sign(self, kw):
        """
        校验签名
        :param kw: 包含签名及被签名的字段
        :return: 签名结果一致返回True,否则返回False
        """
        wechat_sign = kw.pop('sign')
        return wechat_sign == self.sign(kw)

    @staticmethod
    def xml_to_dict(content):
        content = xmltodict.parse(content)
        if 'xml' in content:
            return content['xml']
        else:
            return content

    @staticmethod
    def dict_to_xml(kw):
        res = ''
        for k, v in kw.items():
            res += '<{0}>{1}</{0}>'.format(k, v, k)
        return '<xml>{0}</xml>'.format(res)

    def send_data(self, url, data):
        resp = requests.post(url=url, data=bytes(self.dict_to_xml(data), 'utf-8'))
        return self.xml_to_dict(resp.content.decode('utf-8'))

    def reply(self, ret_msg):
        """
        接收微信服务器的异步通知支付结果之后，将本地处理结果通知微信服务器
        参考 https://pay.weixin.qq.com/wiki/doc/api/app/app.php?chapter=9_7&index=3
        :param ret_msg: 微信服务器通知支付结果消息
        :return: 微信官方文档格式的本地处理结果
        """
        res = self.xml_to_dict(ret_msg)
        err_code = 'SUCCESS'
        err_msg = 'OK'
        if not res:
            err_code = 'FAIL'
            err_msg = '参数格式校验错误'
        elif not self.check_sign(res):
            err_code = 'FAIL'
            err_msg = '签名失败'
        return self.dict_to_xml(dict(return_code=err_code, return_msg=err_msg))

    def unified_order(self, **data):
        """
        统一下单接口
        参考 https://pay.weixin.qq.com/wiki/doc/api/app/app.php?chapter=9_1
        :param data: 字典类型参数，必须包含字段out_trade_no(调用者产生)， total_fee(单位为分)，body，
                    trade_type(可为NATIVE, APP, JSAPI)
        :return: 客户端调起支付接口所需的参数，字典类型
        """
        url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
        if 'out_trade_no' not in data:
            raise Exception(msg='缺少必须参数商户订单号')
        if 'total_fee' not in data:
            raise Exception(msg='缺少必须参数总金额')
        if 'body' not in data:
            raise Exception(msg='缺少必须参数商品描述')
        if 'trade_type' not in data:
            raise Exception(msg='缺少必须参数交易类型')

        data.setdefault('appid', self.APP_ID)
        data.setdefault('mch_id', self.MCH_ID)
        data.setdefault('nonce_str', self.nonce_str)
        data.setdefault('notify_url', self.notify_url)
        data.setdefault('spbill_create_ip', self.spbill_create_ip)
        data.setdefault('sign', self.sign(data))

        resp = self.send_data(url, data)
        if resp['return_code'] == 'FAIL':
            raise Exception(resp['return_msg'])
        time_stamp = int(time.time())
        res = dict(appid=self.APP_ID, partnerid=self.MCH_ID, noncestr=self.nonce_str, package='Sign=WXPay',
                   prepayid=resp['prepay_id'], timestamp=str(time_stamp))
        res['sign'] = self.sign(res)

        return res

    def order_query(self, **data):
        """
        查询订单接口
        参考 https://pay.weixin.qq.com/wiki/doc/api/app/app.php?chapter=9_2&index=4
        :param data: 字典类型参数，必须包含字段transaction_id或者out_trade_no， 建议使用transaction_id
        :return: 微信服务器返回的消息，字典类型
        :example:
        res = order_query(transaction_id='1111122222')
        if 'return_code' in res:
            if res['return_code'] == 'FAIL':
                pass
            else:
                if 'result_code' in res and res['result_code'] == 'FAIL':
                    if 'err_code' in res and 'err_code_des' in res:
                        pass
                else:
                    pass
        else:
            pass
        """
        url = 'https://api.mch.weixin.qq.com/pay/orderquery'
        if 'transaction_id' in data:
            if 'out_trade_no' in data:
                raise Exception(msg='商户订单及微信订单号只能包含一个')
        else:
            if 'out_trade_no' not in data:
                raise Exception(msg='缺少必须参数商户订单号')
        data.setdefault('appid', self.APP_ID)
        data.setdefault('mch_id', self.MCH_ID)
        data.setdefault('nonce_str', self.nonce_str)
        data.setdefault('sign', self.sign(data))
        resp = self.send_data(url, data)
        print(resp)
        if resp['return_code'] == 'FAIL':
            return dict(return_code=resp['return_code'], return_msg=resp['return_msg'])
        if not self.check_sign(resp):
            return dict(result_code='FAIL', err_code='SIGNFAILED', err_code_des='sign check failed')
        return resp

    def close_order(self, out_trade_no):
        """
        关闭订单接口
        参考 https://pay.weixin.qq.com/wiki/doc/api/app/app.php?chapter=9_3&index=5
        :param out_trade_no:商户订单号
        :return:微信服务器返回的消息，字典类型
        """
        url = 'https://api.mch.weixin.qq.com/pay/closeorder'
        if not out_trade_no:
            raise Exception('商户系统内部订单号不能为空')
        data = dict(appid=self.APP_ID, mch_id=self.MCH_ID, nonce_str=self.nonce_str, out_trade_no=out_trade_no)
        data['sign'] = self.sign(data)
        resp = self.send_data(url, data)
        if resp['return_code'] == 'FAIL':
            return dict(return_code=resp['return_code'], return_msg=resp['return_msg'])
        if not self.check_sign(resp):
            return dict(err_code='SIGNFAILED', err_code_des='sign check failed')
        return resp

    def download_bill(self, **data):
        """
        下载对账单接口
        参考 https://pay.weixin.qq.com/wiki/doc/api/app/app.php?chapter=9_6&index=8
        :param data: 字典类型参数，必须包含字段bill_date，bill_type
        :return: 成功返回对应的订单内容，失败返回错误码
        成功时返回的数据：
        返回值1：
        {'总企业红包退款金额': '0.00', '总交易额': '0.02', '总退款金额': '0.00', '手续费总金额': '0.00000', '总交易单数': '2'}
        返回值2：
        [{
            "交易时间": "2017-03-03 16:31:09",
            "交易状态": "SUCCESS",
            "交易类型": "APP",
            "付款银行": "CFT",
            "企业红包退款金额": "0.00",
            "企业红包金额": "0.00",
            "公众账号ID": "wx643b87be508f1eaa",
            "商品名称": "X流量包充值",
            "商户号": "1424058002",
            "商户数据包": "",
            "商户订单号": "20170303163059hMZFrs6vCoRBunS23j",
            "商户退款单号": "0",
            "子商户号": "0",
            "微信订单号": "4007712001201703032068201773",
            "微信退款单号": "0",
            "总金额": "0.01",
            "手续费": "0.00000",
            "用户标识": "oi5iywYimJ7fKA--H4rXkdKukQs4",
            "设备号": "",
            "货币种类": "CNY",
            "费率": "1.00%",
            "退款状态": "",
            "退款类型": "",
            "退款金额": "0.00"
        },
        {
            "交易时间": "2017-03-03 16:29:09",
            "交易状态": "SUCCESS",
            "交易类型": "APP",
            "付款银行": "CFT",
            "企业红包退款金额": "0.00",
            "企业红包金额": "0.00",
            "公众账号ID": "wx643b87be508f1eaa",
            "商品名称": "X流量包充值",
            "商户号": "1424058002",
            "商户数据包": "",
            "商户订单号": "20170303162855z7Eok0FUeyCnKSHV1B",
            "商户退款单号": "0",
            "子商户号": "0",
            "微信订单号": "4010222001201703032069774473",
            "微信退款单号": "0",
            "总金额": "0.01",
            "手续费": "0.00000",
            "用户标识": "oi5iywXmKxpWV6kAh3f8kDpdKmCg",
            "设备号": "",
            "货币种类": "CNY",
            "费率": "1.00%",
            "退款状态": "",
            "退款类型": "",
            "退款金额": "0.00"
        }]
        失败时返回数据为：
        返回值1：None
        返回值2位OrderedDict
        [('return_code', 'FAIL'), ('return_msg', 'No Bill Exist'), ('error_code', '20002')]
        """
        url = 'https://api.mch.weixin.qq.com/pay/downloadbill'
        if 'bill_date' not in data:
            raise Exception(msg="缺少必须参数对账日期")
        if 'bill_type' not in data:
            raise Exception(msg="缺少必须参数账单类型")
        if data['bill_type'] not in ['ALL', 'SUCCESS', 'REFUND', 'RECHARGE_REFUND']:
            raise Exception(msg="账单类型参数错误")
        data.setdefault('appid', self.APP_ID)
        data.setdefault('mch_id', self.MCH_ID)
        data.setdefault('nonce_str', self.nonce_str)
        data.setdefault('sign', self.sign(data))
        resp = requests.post(url=url, data=bytes(self.dict_to_xml(data), 'utf-8')).content.decode('utf-8')
        if '<xml>' in resp:
            content = self.xml_to_dict(resp)
            return None, content
        return process_weinxin_bill(resp)

    def refund(self, cert_path, key_path, **data):
        """
        申请退款接口，该接口目前不需要，暂时没有添加证书，功能不完整。
        参考 https://pay.weixin.qq.com/wiki/doc/api/app/app.php?chapter=9_4&index=6
        :param cert_path: 证书文件路径
        :param key_path: Key文件路径
        :param data: 字典类型参数，必须包含字段transaction_id(或out_trade_no二者二选一)，out_refund_no，
                    total_fee(单位为分),refund_fee(单位为分)
        :return:
        """
        url = 'https://api.mch.weixin.qq.com/secapi/pay/refund'
        if 'transaction_id' not in data and 'out_trade_no' not in data:
            raise Exception(msg="微信订单号、商户订单号至少包含一个")
        if 'out_refund_no' not in data:
            raise Exception(msg="缺少必须参数商户退款单号")
        if 'total_fee' not in data:
            raise Exception(msg="缺少必须参数总金额")
        if 'refund_fee' not in data:
            raise Exception(msg="缺少必须参数退款金额")
        if int(data['refund_fee']) > int(data['total_fee']):
            raise Exception(msg="t退款金额大于总金额")
        data.setdefault('appid', self.APP_ID)
        data.setdefault('mch_id', self.MCH_ID)
        data.setdefault('nonce_str', self.nonce_str)
        data.setdefault('op_user_id', self.MCH_ID)
        data.setdefault('sign', self.sign(data))
        resp = self.send_data(url, data)
        if resp['return_code'] == "FAIL":
            raise Exception(resp['return_msg'])
        if 'result_code' in resp and resp['result_code'] == 'FAIL':
            raise Exception('{0}:{1}'.format(resp['err_code'], resp['err_code_des']))
        return resp

    def refund_query(self, **data):
        """
        查询退款接口
        参考 https://pay.weixin.qq.com/wiki/doc/api/app/app.php?chapter=9_5&index=7
        :param data: 字典类型参数，transaction_id，out_trade_no，out_refund_no，refund_id四个字段四选一即可
        :return:
        """
        url = 'https://api.mch.weixin.qq.com/pay/refundquery'
        if 'transaction_id' not in data and 'out_trade_no' not in data \
                and 'out_refund_no' not in data and 'refund_id' not in data:
            raise Exception(msg="微信订单号、商户订单号、商户退款单号或者微信退款单号至少包含一个")
        data.setdefault('appid', self.APP_ID)
        data.setdefault('mch_id', self.MCH_ID)
        data.setdefault('nonce_str', self.nonce_str)
        data.setdefault('sign', self.sign(data))
        resp = self.send_data(url, data)
        if resp['return_code'] == "FAIL":
            raise Exception(resp['return_msg'])
        if 'result_code' in resp and resp['result_code'] == 'FAIL':
            raise Exception('{0}:{1}'.format(resp['err_code'], resp['err_code_des']))
        return resp

#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: sms.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 16/10/8
# *************************************************************************
from threading import Thread

import requests
import xmltodict
from flask import current_app
from .CCPRestSDK import REST


class SMS(object):
    def __init__(self):
        self._restServer = REST(current_app.config['SMS_SERVER_ADDR'],
                                current_app.config['SMS_SERVER_PORT'],
                                current_app.config['SOFT_VERSION'])
        self._restServer.setAccount(current_app.config['ACCOUNT_SID'],
                                    current_app.config['ACCOUNT_TOKEN'])
        self._restServer.setAppId(current_app.config['APP_ID'])

    def send_template_sms(self, to, content, template_id):
        """发送通知短信
        @param to ：短信接收者手机号码，如果有多个接收者使用逗号分隔，'13800000000', '13800000000, 13900000000'
        @param content : 短信模板接收的参数，要采用list的样式，如参数为两个['param1', 'param2'], 如果无参数则为['']
        @param template_id : 短信模板id,用来区分发送不同类型的短信
        @return: none

        """
        def send_sms_async(to, content, template_id):
            result = self._restServer.sendTemplateSMS(to, content, template_id)
            if 'statusCode' in result:
                print('statusCode : %s' % result['statusCode'])
                if result['statusCode'] == '000000':
                    print('短信发送成功')
                else:
                    print('短信发送失败')
            print(result)

        thr = Thread(target=send_sms_async, args=[to, content, template_id])
        thr.start()


class SmsWwtl(object):
    """
    使用微网通联发送短信
    """
    def __init__(self):
        self._sName = "dlgdwlkj"
        self._sPwd = "guoding8"
        self._url = "http://cf.51welink.com/submitdata/Service.asmx/g_SubmitWithKey"
        self._sCorpId = ""
        self._sPrdId = "1012888"
        self._key = "godinsec"

    @staticmethod
    def xml_to_dict(content):
        content = xmltodict.parse(content)
        if 'xml' in content:
            return content['xml']
        else:
            return content

    def _send_single_sms(self, to, content, template_id):
        if len(content) == 0:
            return "param invalid"
        if template_id == 1:
            sms = '尊敬的用户，您本次的验证码是%s，请及时输入验证码完成操作。【国鼎安全】' % content[0]
        elif template_id == 2:
            sms = '服务器%s发生故障，请您尽快登陆该服务器，处理该故障。【国鼎安全】' % content[0]
        elif template_id == 3:
            sms = '您充值的%s流量已充值%s，查询流量详情请与运营商联系，其它问题请联系流量驿站客服。QQ：179203321。【国鼎安全】' \
                  % (content[0], content[1])
        elif template_id == 4:
            sms = '尊敬的用户，您本次的验证码是%s，请及时输入验证码完成操作。【V商神器】' % content[0]
        else:
            sms = content
        params = dict(sname=self._sName, spwd=self._sPwd, scorpid=self._sCorpId, sprdid=self._sPrdId,
                      sdst=to, smsg=sms, key=self._key)
        resp = requests.get(url=self._url, params=params)
        return self.xml_to_dict(resp.content.decode("utf-8"))

    def send_template_sms(self, to, content, template_id):
        """发送通知短信
        @param to ：短信接收者手机号码，如果有多个接收者使用逗号分隔，'13800000000', '13800000000, 13900000000'
        @param content : 短信模板接收的参数，要采用list的样式，如参数为两个['param1', 'param2'], 如果无参数则为['']
        @param template_id : 短信模板id,用来区分发送不同类型的短信, 1: 短信验证码, 2: 故障报警， 3：流量充值
        @return: none

        """
        def send_sms_async(dst, msg, temp_id):
            receivers = dst.split(',')
            for rec in receivers:
                result = self._send_single_sms(rec, msg, temp_id)
                if 'CSubmitState' in result and 'State' in result['CSubmitState']:
                    print('MsgID: %s, %s' % (result['CSubmitState']['MsgID'], result['CSubmitState']['MsgState']))
                else:
                    print(result)

        thr = Thread(target=send_sms_async, args=[to, content, template_id])
        thr.start()

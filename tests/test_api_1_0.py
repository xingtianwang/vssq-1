#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json

import requests
import unittest
import hashlib


class TestApi0(unittest.TestCase):

    def setUp(self):
        self.url = 'http://127.0.0.1:9103/vssq/'

    def test_auth_sms(self):
        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "phone_num": "18810634461",
            "msg_type": "1",
            "imei": "123456789012345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetAuthSms'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "phone_num": "18810634461",
            "msg_type": "1",
            "imei": "123456789012345"
        }
        url = self.url + 'api/v1.0/GetAuthSms'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "phone_num": "18810634461",
            "msg_type": "1",
            "imei": "123456789012345111111111111111111111",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetAuthSms'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "phone_num": "18810634461",
            "msg_type": "1",
            "imei": "123456789012345",
            "app_version": "1.1.1"
        }
        url = self.url + 'api/v1.0/GetAuthSms'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "phone_num": "18810634461",
        #     "msg_type": "1",
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6"
        # }
        # url = self.url + 'api/v1.0/GetAuthSms'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

        # phone number invalid
        print("**********phone number invalid **********")
        json_req = {
            "phone_num": "188106",
            "msg_type": "1",
            "imei": "123456789012345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetAuthSms'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000004', 'phone number invalid'
        print('phone number invalid test passed')
        print("##########phone number invalid##########")

        # sms already sent
        print("**********sms already sent**********")
        json_req = {
            "phone_num": "18810634461",
            "msg_type": "1",
            "imei": "123456789012345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetAuthSms'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000001', "sms already sent"
        print('sms already sent test passed')
        print("##########sms already sent##########")

    def test_register(self):
        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "phone_num": "18810634461",
            "device_model": "Nexus7",
            "smsverifycode": "921805",
            "app_version": "1.0.6",
            "device_factory": "Google",
            "msg_type": "1",
            "imei": "123456789012345",
            "os_version": "5.1.1",
            "market": "new-media",
            "password": "111111"
        }
        url = self.url + 'api/v1.0/Register'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "phone_num": "18810634461",
            "device_model": "Nexus7",
            "smsverifycode": "642081",
            "app_version": "1.0.6",
            "device_factory": "Google",
            "msg_type": "1",
            "imei": "123456789012345",
            "os_version": "5.1.1",
            "market": "new-media"
        }
        url = self.url + 'api/v1.0/Register'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "phone_num": "18810634461",
            "device_model": "Nexus7",
            "smsverifycode": "642081",
            "app_version": "1.0.6",
            "device_factory": "Google",
            "msg_type": "1",
            "imei": "12345678",
            "os_version": "5.1.1",
            "market": "new-media",
            "password": "111111"
        }
        url = self.url + 'api/v1.0/Register'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "phone_num": "18810634461",
            "device_model": "Nexus7",
            "smsverifycode": "642081",
            "app_version": "1.1.1",
            "device_factory": "Google",
            "msg_type": "1",
            "imei": "123456789012345",
            "os_version": "5.1.1",
            "market": "new-media",
            "password": "111111"
        }
        url = self.url + 'api/v1.0/Register'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "phone_num": "18810634461",
        #     "device_model": "Nexus7",
        #     "smsverifycode": "642081",
        #     "app_version": "1.0.6",
        #     "device_factory": "Google",
        #     "msg_type": "1",
        #     "imei": "123456789012345",
        #     "os_version": "5.1.1",
        #     "market": "new-media",
        #     "password": "111111"
        # }
        # url = self.url + 'api/v1.0/Register'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

        # phone number invalid
        print("**********phone number invalid **********")
        json_req = {
            "phone_num": "18810",
            "device_model": "Nexus7",
            "smsverifycode": "642081",
            "app_version": "1.0.6",
            "device_factory": "Google",
            "msg_type": "1",
            "imei": "123456789012345",
            "os_version": "5.1.1",
            "market": "new-media",
            "password": "111111"
        }
        url = self.url + 'api/v1.0/Register'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000004', 'phone number invalid'
        print('phone number invalid test passed')
        print("##########phone number invalid##########")

    def test_token(self):
        json_req = {
            "phone_num": "18810634461",
            "imei": "123456789012345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetAuthToken'
        r = requests.post(url=url, json=json_req, auth=('18810634461', '111111'))
        print(r.url)
        print(r.text)
        print(r.status_code)
        return r.json()

    def test_tokens(self):
        # no token
        print("**********no token**********")
        json_req = {
            "phone_num": "18810634461",
            "imei": "123456789012345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetAuthToken'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 401, "no token test failed"
        print('no token test passed')
        print("##########no token##########")

        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "phone_num": "18810634461",
            "imei": "123456789012345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetAuthToken'
        r = requests.post(url=url, json=json_req, auth=('18810634461', '111111'))
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "phone_num": "18810634461",
            "imei": "123456789012345"
        }
        url = self.url + 'api/v1.0/GetAuthToken'
        r = requests.post(url=url, json=json_req, auth=('18810634461', '111111'))
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "phone_num": "18810634461",
            "imei": "12345678945",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetAuthToken'
        r = requests.post(url=url, json=json_req, auth=('18810634461', '111111'))
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "phone_num": "18810634461",
            "imei": "123456789012345",
            "app_version": "1.1.6"
        }
        url = self.url + 'api/v1.0/GetAuthToken'
        r = requests.post(url=url, json=json_req, auth=('18810634461', '111111'))
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "phone_num": "18810634461",
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6"
        # }
        # url = self.url + 'api/v1.0/GetAuthToken'
        # r = requests.post(url=url, json=json_req, auth=('18810634461', '111111'))
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

    def test_upload_mobile(self):
        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "imei": "123456789012345",
            "os_version": "5.1.1",
            "device_factory": "Google",
            "device_model": "Nexus7",
            "app_version": "1.0.6",
            "market": "new-media"
        }
        url = self.url + 'api/v1.0/UploadMobileInfo'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "imei": "123456789012345",
            "os_version": "5.1.1",
            "device_factory": "Google",
            "device_model": "Nexus7",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/UploadMobileInfo'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "1234567",
            "os_version": "5.1.1",
            "device_factory": "Google",
            "device_model": "Nexus7",
            "app_version": "1.0.6",
            "market": "new-media"
        }
        url = self.url + 'api/v1.0/UploadMobileInfo'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "os_version": "5.1.1",
            "device_factory": "Google",
            "device_model": "Nexus7",
            "app_version": "1.1.1",
            "market": "new-media"
        }
        url = self.url + 'api/v1.0/UploadMobileInfo'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "os_version": "5.1.1",
        #     "device_factory": "Google",
        #     "device_model": "Nexus7",
        #     "app_version": "1.0.6",
        #     "market": "new-media"
        # }
        # url = self.url + 'api/v1.0/UploadMobileInfo'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

    def test_getwhitelist(self):
        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "version_code": "1",
            "imei": "123456789012345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetWhiteList'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "version_code": "1",
            "imei": "123456789012345"
        }
        url = self.url + 'api/v1.0/GetWhiteList'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "version_code": "1",
            "imei": "12345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetWhiteList'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "version_code": "1",
            "imei": "123456789012345",
            "app_version": "1.1.1"
        }
        url = self.url + 'api/v1.0/GetWhiteList'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "version_code": "1",
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6"
        # }
        # url = self.url + 'api/v1.0/GetWhiteList'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

        # no white list to update
        # print("**********no white list to update**********")
        # json_req = {
        #     "version_code": "1",
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6"
        # }
        # url = self.url + 'api/v1.0/GetWhiteList'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000006', "no white list to update"
        # print('no white list to update test passed')
        # print("##########no white list to update##########")

    def test_feedback(self):
        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "imei": "123456789012345",
            "os_version": "5.1.1",
            "device_factory": "Google",
            "device_model": "Nexus7",
            "app_version": "1.0.6",
            'user_contact': 'test@godinsec.com',
            "content": "this is my feedback message"
        }
        url = self.url + 'api/v1.0/FeedBack'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "imei": "123456789012345",
            "os_version": "5.1.1",
            "device_factory": "Google",
            "device_model": "Nexus7",
            "app_version": "1.0.6",
            'user_contact': 'test@godinsec.com'
        }
        url = self.url + 'api/v1.0/FeedBack'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "1234567",
            "os_version": "5.1.1",
            "device_factory": "Google",
            "device_model": "Nexus7",
            "app_version": "1.0.6",
            'user_contact': 'test@godinsec.com',
            "content": "this is my feedback message"
        }
        url = self.url + 'api/v1.0/FeedBack'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "os_version": "5.1.1",
            "device_factory": "Google",
            "device_model": "Nexus7",
            "app_version": "1.1.1",
            'user_contact': 'test@godinsec.com',
            "content": "this is my feedback message"
        }
        url = self.url + 'api/v1.0/FeedBack'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "os_version": "5.1.1",
        #     "device_factory": "Google",
        #     "device_model": "Nexus7",
        #     "app_version": "1.0.6",
        #     'user_contact': 'test@godinsec.com',
        #     "content": "this is my feedback message"
        # }
        # url = self.url + 'api/v1.0/FeedBack'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

    def test_checkframeupdate(self):
        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "frames": [{'number': 1, 'version_code': 1}],
            "imei": "123456789012345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/CheckFrameUpdate'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "frames": [{'number': 1, 'version_code': 1}],
            "imei": "123456789012345"
        }
        url = self.url + 'api/v1.0/CheckFrameUpdate'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "frames": [{'number': 1, 'version_code': 1}],
            "imei": "12345678",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/CheckFrameUpdate'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "frames": [{'number': 1, 'version_code': 1}],
            "imei": "123456789012345",
            "app_version": "1.1.1"
        }
        url = self.url + 'api/v1.0/CheckFrameUpdate'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "frames": [{'number': 1, 'version_code': 1}],
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6"
        # }
        # url = self.url + 'api/v1.0/CheckFrameUpdate'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

    def test_checkpluginupdate(self):
        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "frame_version_code": "1",
            "plugins":
            [
                {"package_name": "com.godinsec.settings", "version_code": "2"}
            ]
        }
        url = self.url + 'api/v1.0/CheckPluginUpdate'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "imei": "123456789012345",
            "frame_version_code": "1",
            "plugins":
                [
                    {"package_name": "com.godinsec.settings", "version_code": "2"}
                ]
        }
        url = self.url + 'api/v1.0/CheckPluginUpdate'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "12345678",
            "app_version": "1.0.6",
            "frame_version_code": "1",
            "plugins":
                [
                    {"package_name": "com.godinsec.settings", "version_code": "2"}
                ]
        }
        url = self.url + 'api/v1.0/CheckPluginUpdate'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.1.1",
            "frame_version_code": "1",
            "plugins":
                [
                    {"package_name": "com.godinsec.settings", "version_code": "2"}
                ]
        }
        url = self.url + 'api/v1.0/CheckPluginUpdate'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6",
        #     "frame_version_code": "1",
        #     "plugins":
        #         [
        #             {"package_name": "com.godinsec.settings", "version_code": "2"}
        #         ]
        # }
        # url = self.url + 'api/v1.0/CheckPluginUpdate'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

        # already last version
        print("**********app version is invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "frame_version_code": "1",
            "plugins":
                [
                    {"package_name": "com.godinsec.settings", "version_code": "2"}
                ]
        }
        url = self.url + 'api/v1.0/CheckPluginUpdate'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000007', "already last version"
        print('already last version test passed')
        print("##########already last version##########")

    def test_setuserinfo(self):
        # no token
        print("**********no token**********")
        json_req = {
            "godin_id": "4c59396301ab6274bd7892f0b31df36e",
            "nick_name": "Allan",
            "imei": "123456789012345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/SetUserInfo'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 401, "no token test failed"
        print('no token test passed')
        print("##########no token##########")

        token = self.test_token()['body']['token']
        print(token)

        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "godin_id": "bdb3c26bf367d92fbf990cde2d36cd1d",
            "nick_name": "jlc",
            "imei": "123456789012345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/SetUserInfo'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "godin_id": "4c59396301ab6274bd7892f0b31df36e",
            "nick_name": "Allan",
            "imei": "123456789012345"
        }
        url = self.url + 'api/v1.0/SetUserInfo'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "godin_id": "4c59396301ab6274bd7892f0b31df36e",
            "nick_name": "Allan",
            "imei": "12345678",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/SetUserInfo'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "godin_id": "4c59396301ab6274bd7892f0b31df36e",
            "nick_name": "Allan",
            "imei": "123456789012345",
            "app_version": "1.1.1"
        }
        url = self.url + 'api/v1.0/SetUserInfo'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "godin_id": "4c59396301ab6274bd7892f0b31df36e",
        #     "nick_name": "Allan",
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6"
        # }
        # url = self.url + 'api/v1.0/SetUserInfo'
        # r = requests.post(url=url, json=json_req, auth=(token, ''))
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

        # user not exist
        print("**********user not exist**********")
        json_req = {
            "godin_id": "4c59396301ab6274bd7892f0b31df36e",
            "nick_name": "xxxxx",
            "imei": "123456789012345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/SetUserInfo'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000018', "user not exist test passed"
        print('user not exist test passed')
        print("##########user not exist##########")

        # photo data not invalid
        print("**********photo data not invalid**********")
        json_req = {
            "godin_id": "bdb3c26bf367d92fbf990cde2d36cd1d",
            "nick_name": "jlc",
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "photo": "sssssssssssssssssss"
        }
        url = self.url + 'api/v1.0/SetUserInfo'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000010', "photo data not invalid test passed"
        print('photo data not invalid test passed')
        print("##########photo data not invalid##########")

    def test_uploadexceptionlog(self):
        # # success, with bundle
        # print("**********success with bundle**********")
        # json_req = {
        #     "md5_value": "4c59396301ab6274bd7892f0b31df36e",
        #     "app_version": "1.0.6",
        #     "imei": "123456789012345",
        #     "os_version": "6.0.1",
        #     "device_model": "Honour6",
        #     "package_name": "com.godinsec.launcher",
        #     "content": "log content"
        # }
        # url = self.url + 'api/v1.0/UploadExceptionLog'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        # print('success test passed')
        # print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "md5_value": "4c59396301ab6274bd7892f0b31df36e",
            "app_version": "1.0.6",
            "imei": "123456789012345",
            "os_version": "6.0.1",
            "device_model": "Honour6",
            "package_name": "com.godinsec.launcher"
        }
        url = self.url + 'api/v1.0/UploadExceptionLog'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "md5_value": "4c59396301ab6274bd7892f0b31df36e",
            "app_version": "1.0.6",
            "imei": "1234567",
            "os_version": "6.0.1",
            "device_model": "Honour6",
            "package_name": "com.godinsec.launcher",
            "content": "log content"
        }
        url = self.url + 'api/v1.0/UploadExceptionLog'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "md5_value": "4c59396301ab6274bd7892f0b31df36e",
            "app_version": "1.1.1",
            "imei": "123456789012345",
            "os_version": "6.0.1",
            "device_model": "Honour6",
            "package_name": "com.godinsec.launcher",
            "content": "log content"
        }
        url = self.url + 'api/v1.0/UploadExceptionLog'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "md5_value": "4c59396301ab6274bd7892f0b31df36e",
        #     "app_version": "1.0.6",
        #     "imei": "123456789012345",
        #     "os_version": "6.0.1",
        #     "device_model": "Honour6",
        #     "package_name": "com.godinsec.launcher",
        #     "content": "log content"
        # }
        # url = self.url + 'api/v1.0/UploadExceptionLog'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

        # exception app version invalid
        print("**********exception app version invalid**********")
        json_req = {
            "md5_value": "4c59396301ab6274bd7892f0b31df36e",
            "app_version": "1.0.6",
            "imei": "123456789012345",
            "os_version": "6.0.1",
            "device_model": "Honour6",
            "package_name": "com.godinsec.launcher",
            "content": "log content"
        }
        url = self.url + 'api/v1.0/UploadExceptionLog'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000017', "exception app version invalid test failed"
        print('exception app version invalid test passed')
        print("##########exception app version invalid##########")

    def test_getpermission(self):
        # # success, with bundle
        # print("**********success with bundle**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6",
        #     "permission_version_code": "1"
        # }
        # url = self.url + 'api/v1.0/GetPermission'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        # print('success test passed')
        # print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "imei": "123456789012345",
            "permission_version_code": "1"
        }
        url = self.url + 'api/v1.0/GetPermission'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "1234512345",
            "app_version": "1.0.6",
            "permission_version_code": "1"
        }
        url = self.url + 'api/v1.0/GetPermission'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.1.6",
            "permission_version_code": "1"
        }
        url = self.url + 'api/v1.0/GetPermission'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6",
        #     "permission_version_code": "1"
        # }
        # url = self.url + 'api/v1.0/GetPermission'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

        # already last version
        print("**********already last version**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "permission_version_code": "1"
        }
        url = self.url + 'api/v1.0/GetPermission'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000007', "already last version test failed"
        print('already last version test passed')
        print("##########already last version##########")

    def test_getsharecode(self):
        # no token
        print("**********no token**********")
        json_req = {
            "imei": "395125050989799",
            "app_version": "1.0.6",
            "godin_id": "4b941562804f13603cdcc0ec898e582f",
            "activity_id": 1
        }
        url = self.url + 'api/v1.0/GetShareCode'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 401, "no token test failed"
        print('no token test passed')
        print("##########no token##########")

        token = self.test_token()['body']['token']
        print(token)

        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "imei": "395125050989799",
            "app_version": "1.0.6",
            "godin_id": "4b941562804f13603cdcc0ec898e582f",
            "activity_id": 1
        }
        url = self.url + 'api/v1.0/GetShareCode'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "app_version": "1.0.6",
            "godin_id": "4b941562804f13603cdcc0ec898e582f",
            "activity_id": 1
        }
        url = self.url + 'api/v1.0/GetShareCode'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "3951250509",
            "app_version": "1.0.6",
            "godin_id": "4b941562804f13603cdcc0ec898e582f",
            "activity_id": 1
        }
        url = self.url + 'api/v1.0/GetShareCode'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "876080027995020",
            "app_version": "xxxxx",
            "godin_id": "4b941562804f13603cdcc0ec898e582f",
            "activity_id": 1
        }
        url = self.url + 'api/v1.0/GetShareCode'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "imei": "395125050989799",
        #     "app_version": "1.0.6",
        #     "godin_id": "4b941562804f13603cdcc0ec898e582f",
        #     "activity_id": 1
        # }
        # url = self.url + 'api/v1.0/GetShareCode'
        # r = requests.post(url=url, json=json_req, auth=(token, ''))
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

        # user not exist
        print("**********user not exist**********")
        json_req = {
            "imei": "395125050989799",
            "app_version": "1.0.6",
            "godin_id": "4b941562804f13603cdcc0ec111e582f",
            "activity_id": 1
        }
        url = self.url + 'api/v1.0/GetShareCode'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000018', "user not exist test failed"
        print('user not exist test passed')
        print("##########user not exist##########")

        # activity not exist
        print("**********activity not exist**********")
        json_req = {
            "imei": "395125050989799",
            "app_version": "1.0.6",
            "godin_id": "4b941562804f13603cdcc0ec898e582f",
            "activity_id": 666
        }
        url = self.url + 'api/v1.0/GetShareCode'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000023', "activity not exist test failed"
        print('activity not exist test passed')
        print("##########activity not exist##########")

    def test_getactivityregistercount(self):
        # no token
        print("**********no token**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": "429a2d57e70bb09c2080d7b029ab14dc",
            "activity_id": 1
        }
        url = self.url + 'api/v1.0/GetActivityRegisterCount'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 401, "no token test failed"
        print('no token test passed')
        print("##########no token##########")

        token = self.test_token()['body']['token']
        print(token)

        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": "429a2d57e70bb09c2080d7b029ab14dc",
            "activity_id": 1
        }
        url = self.url + 'api/v1.0/GetActivityRegisterCount'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "app_version": "1.0.6",
            "godin_id": "429a2d57e70bb09c2080d7b029ab14dc",
            "activity_id": 1
        }
        url = self.url + 'api/v1.0/GetActivityRegisterCount'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "12342345",
            "app_version": "1.0.6",
            "godin_id": "429a2d57e70bb09c2080d7b029ab14dc",
            "activity_id": 1
        }
        url = self.url + 'api/v1.0/GetActivityRegisterCount'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.1.6",
            "godin_id": "429a2d57e70bb09c2080d7b029ab14dc",
            "activity_id": 1
        }
        url = self.url + 'api/v1.0/GetActivityRegisterCount'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6",
        #     "godin_id": "429a2d57e70bb09c2080d7b029ab14dc",
        #     "activity_id": 1
        # }
        # url = self.url + 'api/v1.0/GetActivityRegisterCount'
        # r = requests.post(url=url, json=json_req, auth=(token, ''))
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

        # user not exist
        print("**********user not exist**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": "429a2d57e70bb1112080d7b029ab14dc",
            "activity_id": 1
        }
        url = self.url + 'api/v1.0/GetActivityRegisterCount'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000018', "user not exist test failed"
        print('user not exist test passed')
        print("##########user not exist##########")

        # activity not exist
        print("**********activity not exist**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": "429a2d57e70bb09c2080d7b029ab14dc",
            "activity_id": 666
        }
        url = self.url + 'api/v1.0/GetActivityRegisterCount'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000023', "activity not exist test failed"
        print('activity not exist test passed')
        print("##########activity not exist##########")

    def test_getsharecount(self):
        # no token
        print("**********no token**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": "fe8803d81eed1591b96624ab8e38b77e",
            "activity_id": 12
        }
        url = self.url + 'api/v1.0/GetShareCount'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 401, "no token test failed"
        print('no token test passed')
        print("##########no token##########")

        token = self.test_token()['body']['token']
        print(token)

        # success, with bundle
        print("**********success with bundle**********")
        token = self.test_token()['body']['token']
        print(token)
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": "fe8803d81eed1591b96624ab8e38b77e",
            "activity_id": 12
        }
        url = self.url + 'api/v1.0/GetShareCount'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "app_version": "1.0.6",
            "godin_id": "fe8803d81eed1591b96624ab8e38b77e",
            "activity_id": 12
        }
        url = self.url + 'api/v1.0/GetShareCount'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "129012345",
            "app_version": "1.0.6",
            "godin_id": "fe8803d81eed1591b96624ab8e38b77e",
            "activity_id": 12
        }
        url = self.url + 'api/v1.0/GetShareCount'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.1.6",
            "godin_id": "fe8803d81eed1591b96624ab8e38b77e",
            "activity_id": 12
        }
        url = self.url + 'api/v1.0/GetShareCount'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6",
        #     "godin_id": "fe8803d81eed1591b96624ab8e38b77e",
        #     "activity_id": 12
        # }
        # url = self.url + 'api/v1.0/GetShareCount'
        # r = requests.post(url=url, json=json_req, auth=(token, ''))
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

        # user not exist
        print("**********user not exist**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": "429a2d57e70bb1112080d7b029ab14dc",
            "activity_id": 1
        }
        url = self.url + 'api/v1.0/GetShareCount'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000018', "user not exist test failed"
        print('user not exist test passed')
        print("##########user not exist##########")

        # activity not exist
        print("**********activity not exist**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": "429a2d57e70bb09c2080d7b029ab14dc",
            "activity_id": 666
        }
        url = self.url + 'api/v1.0/GetShareCount'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000023', "activity not exist test failed"
        print('activity not exist test passed')
        print("##########activity not exist##########")

    def test_getregistercount(self):
        # no token
        print("**********no token**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": "747c2a8e03a2f8571a96f1d873f87bd3",
            "activity_id": 12,
            "share_code": "6120563464"
        }
        url = self.url + 'api/v1.0/GetRegisterCount'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 401, "no token test failed"
        print('no token test passed')
        print("##########no token##########")

        token = self.test_token()['body']['token']
        print(token)

        # success, with bundle
        print("**********success with bundle**********")
        token = self.test_token()['body']['token']
        print(token)
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": "747c2a8e03a2f8571a96f1d873f87bd3",
            "activity_id": 12,
            "share_code": "6120563464"
        }
        url = self.url + 'api/v1.0/GetRegisterCount'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "app_version": "1.0.6",
            "godin_id": "747c2a8e03a2f8571a96f1d873f87bd3",
            "activity_id": 12,
            "share_code": "6120563464"
        }
        url = self.url + 'api/v1.0/GetRegisterCount'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "12312345",
            "app_version": "1.0.6",
            "godin_id": "747c2a8e03a2f8571a96f1d873f87bd3",
            "activity_id": 12,
            "share_code": "6120563464"
        }
        url = self.url + 'api/v1.0/GetRegisterCount'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.1.6",
            "godin_id": "747c2a8e03a2f8571a96f1d873f87bd3",
            "activity_id": 12,
            "share_code": "6120563464"
        }
        url = self.url + 'api/v1.0/GetRegisterCount'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6",
        #     "godin_id": "747c2a8e03a2f8571a96f1d873f87bd3",
        #     "activity_id": 12,
        #     "share_code": "6120563464"
        # }
        # url = self.url + 'api/v1.0/GetRegisterCount'
        # r = requests.post(url=url, json=json_req, auth=(token, ''))
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

        # user not exist
        print("**********user not exist**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": "747c2a8111a2f8571a96f1d873f87bd3",
            "activity_id": 12,
            "share_code": "6120563464"
        }
        url = self.url + 'api/v1.0/GetRegisterCount'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000018', "user not exist test failed"
        print('user not exist test passed')
        print("##########user not exist##########")

        # activity not exist
        print("**********activity not exist**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": "747c2a8e03a2f8571a96f1d873f87bd3",
            "activity_id": 444,
            "share_code": "6120563464"
        }
        url = self.url + 'api/v1.0/GetRegisterCount'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000023', "activity not exist test failed"
        print('activity not exist test passed')
        print("##########activity not exist##########")

        # share code not exist
        print("**********share code not exist**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": "747c2a8e03a2f8571a96f1d873f87bd3",
            "activity_id": 12,
            "share_code": "6222222464"
        }
        url = self.url + 'api/v1.0/GetRegisterCount'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000024', "share code not exist test failed"
        print('share code not exist test passed')
        print("##########share code not exist##########")

        # cant not fill in your share code
        print("**********cant not fill in your share code**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": "bdb3c26bf367d92fbf990cde2d36cd1d",
            "activity_id": 12,
            "share_code": "9812637465"
        }
        url = self.url + 'api/v1.0/GetRegisterCount'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000025', "cant not fill in your share code test failed"
        print('cant not fill in your share code test passed')
        print("##########cant not fill in your share code##########")

    def test_getactivityinfo(self):
        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetActivityInfo'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetActivityInfo'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "12312345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetActivityInfo'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.1.6"
        }
        url = self.url + 'api/v1.0/GetActivityInfo'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6"
        # }
        # url = self.url + 'api/v1.0/GetActivityInfo'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("#1#########in black list##########")

    def test_getactivityprize(self):
        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetActivityPrize'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetActivityPrize'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "112345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetActivityPrize'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.1.6"
        }
        url = self.url + 'api/v1.0/GetActivityPrize'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6"
        # }
        # url = self.url + 'api/v1.0/GetActivityPrize'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

    def test_getactivitystatus(self):
        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetActivityStatus'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetActivityStatus'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "12312345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetActivityStatus'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.1.6"
        }
        url = self.url + 'api/v1.0/GetActivityStatus'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6"
        # }
        # url = self.url + 'api/v1.0/GetActivityStatus'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

    def test_getOpenScreenAdsStatistics(self):
        # success, with bundle
        print("**********success with bundle**********")
        ad_id = [2, 1]
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "ad_id": ad_id
        }
        url = self.url + 'api/v1.0/GetOpenScreenAdsStatistics'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "app_version": "1.0.6",
            "ad_id": ad_id
        }
        url = self.url + 'api/v1.0/GetOpenScreenAdsStatistics'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "1234562345",
            "app_version": "1.0.6",
            "ad_id": ad_id
        }
        url = self.url + 'api/v1.0/GetOpenScreenAdsStatistics'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.1.6",
            "ad_id": ad_id
        }
        url = self.url + 'api/v1.0/GetOpenScreenAdsStatistics'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6",
        #     "ad_id": ad_id
        # }
        # url = self.url + 'api/v1.0/GetOpenScreenAdsStatistics'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

    def test_banneradstatistics(self):
        # success, with bundle
        print("**********success with bundle**********")
        ad_info = [
                   {
                       "ad_id": 2,
                       "type": 0
                   },
                   {
                       "ad_id": 2,
                       "type": 1
                   },
                   {
                       "ad_id": 1,
                       "type": 1
                   },
                   {
                       "ad_id": 2,
                       "type": 1
                   },
                   {
                       "ad_id": 100,
                       "type": 1
                   }
                  ]
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "ad_info": ad_info
        }
        url = self.url + 'api/v1.0/GetBanneradsStatistics'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetBanneradsStatistics'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "123456345",
            "app_version": "1.0.6",
            "ad_info": ad_info
        }
        url = self.url + 'api/v1.0/GetBanneradsStatistics'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.1.6",
            "ad_info": ad_info
        }
        url = self.url + 'api/v1.0/GetBanneradsStatistics'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6",
        #     "ad_info": ad_info
        # }
        # url = self.url + 'api/v1.0/GetBanneradsStatistics'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

    def test_openscreenadstatistics(self):
        # success, with bundle
        print("**********success with bundle**********")
        ad_info = [
                   {
                       "ad_id": 2,
                       "type": 0
                   },
                   {
                       "ad_id": 2,
                       "type": 1
                   },
                   {
                       "ad_id": 1,
                       "type": 1
                   },
                   {
                       "ad_id": 2,
                       "type": 1
                   },
                   {
                       "ad_id": 2,
                       "type": 2
                   }
                  ]
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "ad_info": ad_info
        }
        url = self.url + 'api/v1.0/GetOpenScreenAdsStatistics'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetOpenScreenAdsStatistics'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "12312345",
            "app_version": "1.0.6",
            "ad_info": ad_info
        }
        url = self.url + 'api/v1.0/GetOpenScreenAdsStatistics'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.1.6",
            "ad_info": ad_info
        }
        url = self.url + 'api/v1.0/GetOpenScreenAdsStatistics'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6",
        #     "ad_info": ad_info
        # }
        # url = self.url + 'api/v1.0/GetOpenScreenAdsStatistics'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")
    def test_uploadstatistics(self):
        # success, with bundle
        print("**********success with bundle**********")
        statistics = {
            "deviceid": "111111111",
            "accountid": "00000000000000",
            "date": "1501429445000",
            "os_info": {
                "os_version": "6.0.1",
                "os": "Nexus 5",
                "mac": "cc:fa:00:c6:ca:01",
                "device_id": "353490061934887"
            },
            "versioncode": "1.1.7",
            "channel": "godinsec",
            "resolution": "1776*1080",
            "access": "wifi",
            "ip": "103.36.220.98",
            "cpu": "ARMv7 Processor rev 0 (v7l)",
            "operators": "46000***",
            "network_type": "mobile",
            "subtype": "LTE",
            "version": 1,
            "data": [
                {
                    "serial_number": 100,
                    "package_name": "com.tencent.mm",
                    "pagename": "com.***.activity",
                    "starttime": "1501429444517",
                    "endtime": "1501429445517"
                },
                {
                    "serial_number": 200,
                    "package_name": "com.tencent.qq",
                    "pagename": "com.***.activity",
                    "starttime": "1501429411111",
                    "endtime": "1501429445517"
                }
            ]
        }
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "statistics": statistics
        }
        url = self.url + 'api/v1.0/UploadStatistics'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "app_version": "1.0.6",
            "statistics": statistics
        }
        url = self.url + 'api/v1.0/UploadStatistics'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "1234345",
            "app_version": "1.0.6",
            "statistics": statistics
        }
        url = self.url + 'api/v1.0/UploadStatistics'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.1.6",
            "statistics": statistics
        }
        url = self.url + 'api/v1.0/UploadStatistics'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6",
        #     "statistics": statistics
        # }
        # url = self.url + 'api/v1.0/UploadStatistics'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

    def test_toutiaoadsclickinfo(self):
        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "adid": "13348898719",
            "cid": "65737453819",
            "imei": "58b9b9268acaef64ac6a80b0543357e6",
            "mac": "50:733:85",
            "androidid": "12363387458",
            "os": "0",
            "timestamp": "1503392654",
            "callback_url": "http://www.baidu.com"
        }
        # self.url = 'https://x-phone.cn/'
        url = self.url + 'api/v1.0/GetTouTiaoClick'
        r = requests.get(url=url, params=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['status'] == 0, "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "cid": "65737453819",
            "imei": "58b9b9268acaef64ac6a80b0543357e6",
            "mac": "50:733:85",
            "androidid": "12363387458",
            "os": "0",
            "timestamp": "1503392654",
            "callback_url": "http://www.baidu.com"
        }
        url = self.url + 'api/v1.0/GetTouTiaoClick'
        r = requests.get(url=url, params=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

    def test_statisticsfinishnotice(self):
        # self.url = 'https://godinsec.cn/webusiness/'
        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "date": "20180313"
        }
        url = self.url + 'api/v1.0/StatisticsFinishNotice'
        r = requests.get(url=url, params=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {

        }
        url = self.url + 'api/v1.0/StatisticsFinishNotice'
        r = requests.get(url=url, params=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

    def test_weekstatisticsfinishnotice(self):
        # self.url = 'https://godinsec.cn/'
        url = self.url + 'api/v1.0/WeekStatisticsFinishNotice'
        # param missing
        print("**********para missing**********")
        json_req = {
            "year": 2017
        }
        r = requests.get(url=url, params=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "year": 2017,
            "week": 41
        }
        r = requests.get(url=url, params=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

    def test_monthstatisticsfinishnotice(self):
        url = self.url + 'api/v1.0/MonthStatisticsFinishNotice'
        # param missing
        print("**********para missing**********")
        json_req = {
            "year": 2017
        }
        r = requests.get(url=url, params=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "year": 2017,
            "month": 10
        }
        r = requests.get(url=url, params=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

    def test_seasonstatisticsfinishnotice(self):
        url = self.url + 'api/v1.0/SeasonStatisticsFinishNotice'
        # param missing
        print("**********para missing**********")
        json_req = {
            "year": 2017
        }
        r = requests.get(url=url, params=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "year": 2017,
            "season": 3
        }
        r = requests.get(url=url, params=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

    def test_yearstatisticsfinishnotice(self):
        url = self.url + 'api/v1.0/YearStatisticsFinishNotice'
        # param missing
        print("**********para missing**********")
        json_req = {
        }
        r = requests.get(url=url, params=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "year": 2017
        }
        r = requests.get(url=url, params=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

    def test_get_user_vip_status(self):
        url = self.url + 'api/v1.0/GetUserVipStatus'

        # no token
        # print("**********no token**********")
        # json_req = {
        #     "imei": "866647020146354",
        #     "app_version": "1.0.6",
        #     "godin_id": "0c8350eca41fc087ea4c4cb4fdbe24fe"
        # }
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # assert r.status_code == 401, "no token test failed"
        # print('no token test passed')
        # print("##########no token##########")

        # token = self.test_token()['body']['token']
        # print(token)
        token = self.test_token()['body']['token']
        print(token)

        # param missing
        print("**********para missing**********")
        json_req = {
            "imei": "123456789012345",
            "godin_id": '18835d61df97bc36fbad43db626705f2'
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "1111111",
            "app_version": "1.0.6",
            "godin_id": "0c8350eca41fc087ea4c4cb4fdbe24fe",
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.666",
            "godin_id": '58b9b9268acaef64ac6a80b0543357e6'
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########imei invalid##########")

        # not vip
        print("**********user not vip**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": '0000000000000000000'
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000029', "user not vip test failed"
        print('user not vip test passed')
        print("##########user not vip##########")

        # success
        print("**********success**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": '4b941562804f13603cdcc0ec898e582f'
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success test failed"
        print('success test passed')
        print("##########success##########")

    def test_get_vip_wares(self):
        url = self.url + 'api/v1.0/GetVipWare'

        # no token
        # print("**********no token**********")
        # json_req = {
        #     "imei": "866647020146354",
        #     "app_version": "1.0.6"
        # }
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # assert r.status_code == 401, "no token test failed"
        # print('no token test passed')
        # print("##########no token##########")

        # token = self.test_token()['body']['token']
        # print(token)
        token = ''

        # param missing
        print("**********para missing**********")
        json_req = {
            "imei": "123456789012345"
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "1111111",
            "app_version": "1.0.6"
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.666"
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########imei invalid##########")

        # success
        print("**********success**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6"
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success test failed"
        print('success test passed')
        print("##########success##########")

    def test_get_vip_wares(self):
        url = self.url + 'api/v1.0/GetChannelVipWare'

        # no token
        # print("**********no token**********")
        # json_req = {
        #     "imei": "866647020146354",
        #     "app_version": "1.0.6",
        #       "channel": "huawei"
        # }
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # assert r.status_code == 401, "no token test failed"
        # print('no token test passed')
        # print("##########no token##########")

        # token = self.test_token()['body']['token']
        # print(token)
        token = ''

        # param missing
        print("**********para missing**********")
        json_req = {
            "imei": "123456789012345"
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "1111111",
            "app_version": "1.0.6",
            "channel": "huawei"
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.666",
            "channel": "huawei"
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########imei invalid##########")

        # success
        print("**********success**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "channel": "huawei"
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success test failed"
        print('success test passed')
        print("##########success##########")

    def test_get_vip_order(self):
        url = self.url + 'api/v1.0/GetUserVipOrder'

        # no token
        # print("**********no token**********")
        # json_req = {
        #     "imei": "866647020146354",
        #     "app_version": "1.0.6",
        #     "godin_id": "0c8350eca41fc087ea4c4cb4fdbe24fe"
        # }
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # assert r.status_code == 401, "no token test failed"
        # print('no token test passed')
        # print("##########no token##########")

        # token = self.test_token()['body']['token']
        # print(token)
        token = self.test_token()['body']['token']
        print(token)

        # param missing
        print("**********para missing**********")
        json_req = {
            "imei": "123456789012345",
            "godin_id": '58b9b9268acaef64ac6a80b0543357e6'
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "1111111",
            "app_version": "1.0.6",
            "godin_id": "0c8350eca41fc087ea4c4cb4fdbe24fe",
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.666",
            "godin_id": '58b9b9268acaef64ac6a80b0543357e6'
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########imei invalid##########")

        # success
        print("**********success**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": '55d21003b3a6519b136fc1b1fb051c5d'
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success test failed"
        print('success test passed')
        print("##########success##########")

    def test_buy_vip_ware(self):
        url = self.url + 'api/v1.0/BuyVipWare'

        # no token
        # print("**********no token**********")
        # json_req = {
        #     "imei": "866647020146354",
        #     "app_version": "1.0.6",
        #     "godin_id": "0c8350eca41fc087ea4c4cb4fdbe24fe",
        #     "ware_id": "10001"
        # }
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # assert r.status_code == 401, "no token test failed"
        # print('no token test passed')
        # print("##########no token##########")

        # token = self.test_token()['body']['token']
        # print(token)

        token = self.test_token()['body']['token']
        print(token)

        # param missing
        print("**********para missing**********")
        json_req = {
            "imei": "123456789012345",
            "godin_id": "58b9b9268acaef64ac6a80b0543357e6"
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "1111111",
            "app_version": "1.0.6",
            "godin_id": "58b9b9268acaef64ac6a80b0543357e6",
            "ware_id": "10001"
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.666",
            "godin_id": "58b9b9268acaef64ac6a80b0543357e6",
            "ware_id": "10001"
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########imei invalid##########")

        # success - buy month
        print("**********success-buy_month**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": "bdb3c26bf367d92fbf990cde2d36cd1d",
            "ware_id": "10001"
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success-buy_month test failed"
        print('success-buy_month test passed')
        print("##########success-buy_month##########")

        # success - buy quarter
        print("**********success-buy_quarter**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": "bdb3c26bf367d92fbf990cde2d36cd1d",
            "ware_id": "10002"
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success-buy_quarter test failed"
        print('success-buy_quarter test passed')
        print("##########success-buy_quarter##########")

        # success - buy half year
        print("**********success-buy half year**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": "58b9b9268acaef64ac6a80b0543357e6",
            "ware_id": "10003"
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success-buy half year test failed"
        print('success-buy_quarter test passed')
        print("##########success-buy half year##########")

        # success - buy year
        print("**********success-buy year**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": "58b9b9268acaef64ac6a80b0543357e6",
            "ware_id": "10004"
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success-buy year test failed"
        print('success-buy_quarter test passed')
        print("##########success-buy year##########")

    def test_get_vip_orders_status(self):
        url = self.url + 'api/v1.0/GetVipOrdersStatus'

        order_nums = ['vip20170908162033nvz3CrOt2Z7XKiL', 'vip20170908162154I9hHvizCjcoBUy0']

        # no token
        # print("**********no token**********")
        # json_req = {
        #     "imei": "866647020146354",
        #     "app_version": "1.0.6",
        #     "godin_id": "0c8350eca41fc087ea4c4cb4fdbe24fe",
        #     "order_nums": order_nums
        # }
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # assert r.status_code == 401, "no token test failed"
        # print('no token test passed')
        # print("##########no token##########")

        # token = self.test_token()['body']['token']
        # print(token)
        token = self.test_token()['body']['token']
        print(token)

        # param missing
        print("**********para missing**********")
        json_req = {
            "imei": "123456789012345",
            "godin_id": "58b9b9268acaef64ac6a80b0543357e6",
            "order_nums": order_nums
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "1111111",
            "app_version": "1.0.6",
            "godin_id": "58b9b9268acaef64ac6a80b0543357e6",
            "order_nums": order_nums
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.666",
            "godin_id": "58b9b9268acaef64ac6a80b0543357e6",
            "order_nums": order_nums
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########imei invalid##########")

        # success
        print("**********success**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": "58b9b9268acaef64ac6a80b0543357e6",
            "order_nums": order_nums
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success test failed"
        print('success test passed')
        print("##########success##########")

    def test_OpenScreenAdsData(self):
        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "type": 1,
            "ad_id": 1
        }
        print(json_req)
        url = self.url + 'api/v1.0/OpenScreenAdsData'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "imei": "123456789012345"
        }
        url = self.url + 'api/v1.0/OpenScreenAdsData'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "12345",
            "app_version": "1.0.6",
            "type": 1,
            "ad_id": 2
        }
        url = self.url + 'api/v1.0/OpenScreenAdsData'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.1.6",
            "type": 1,
            "ad_id": 2
        }
        url = self.url + 'api/v1.0/OpenScreenAds'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6",
        #     "type": 0,
        #     "ad_id": 2
        # }
        # url = self.url + 'api/v1.0/OpenScreenAdsData'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

    def test_GetInteractiveAds(self):
        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "channel": "godinsec"
        }
        url = self.url + 'api/v1.0/GetInteractiveAds'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetInteractiveAds'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "123452345",
            "app_version": "1.0.6",
            "channel": "godinsec"
        }
        url = self.url + 'api/v1.0/GetInteractiveAds'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.1.6"
        }
        url = self.url + 'api/v1.0/GetInteractiveAds'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6",
        #     "channel": "godinsec"
        # }
        # url = self.url + 'api/v1.0/GetInteractiveAds'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

    def test_InteractiveAds(self):
        # success, with bundle
        print("**********success with bundle**********")
        ad_info = [
                   {
                       "ad_id": 2,
                       "type": 0
                   },
                   {
                       "ad_id": 2,
                       "type": 1
                   },
                   {
                       "ad_id": 1,
                       "type": 1
                   },
                   {
                       "ad_id": 2,
                       "type": 1
                   }
                  ]
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "ad_info": ad_info
        }
        url = self.url + 'api/v1.0/InteractiveAds'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/InteractiveAds'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "12312345",
            "app_version": "1.0.6",
            "ad_info": ad_info
        }
        url = self.url + 'api/v1.0/InteractiveAds'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.1.6",
            "ad_info": ad_info
        }
        url = self.url + 'api/v1.0/InteractiveAds'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6",
        #     "ad_info": ad_info
        # }
        # url = self.url + 'api/v1.0/InteractiveAds'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

    def test_GetLink(self):
        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "ad_id": 4
        }
        url = self.url + 'api/v1.0/GetLink'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetLink'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "123452345",
            "app_version": "1.0.6",
            "ad_id": 1
        }
        url = self.url + 'api/v1.0/GetLink'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.1.6",
            "ad_id": 1
        }
        url = self.url + 'api/v1.0/GetLink'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6",
        #     "ad_id": 1
        # }
        # url = self.url + 'api/v1.0/GetLink'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

    def test_specificadsstatistics(self):
        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "number": 20170724001,
            "type": 1
        }
        url = self.url + 'api/v1.0/Specificads'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/Specificads'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.1.6",
            "number": 20170724001,
            "type": 1
        }
        url = self.url + 'api/v1.0/Specificads'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # open screen ads not exist
        print("**********ads not exist**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "number": 20170721,
            "type": 1
        }
        url = self.url + 'api/v1.0/Specificads'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000026', "open screen ads not exist"
        print('ads not exist test passed')
        print("##########aads not exist##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6",
        #     "number": 20170724001,
        #     "type": 1
        # }
        # url = self.url + 'api/v1.0/Specificads'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

    def test_getbannerads(self):
        # success, with bundle
        print("**********success with bundle**********")
        # success
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "channel": "godinsec"
        }
        url = self.url + 'api/v1.0/GetBannerads'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetBannerads'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "123412345",
            "app_version": "1.0.6",
            "channel": "godinsec"
        }
        url = self.url + 'api/v1.0/GetBannerads'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.1.6",
            "channel": "godinsec"
        }
        url = self.url + 'api/v1.0/GetBannerads'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6",
        #     "channel": "godinsec"
        # }
        # url = self.url + 'api/v1.0/GetBannerads'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

    def test_getOpenads(self):
        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "channel": "godin"
        }
        url = self.url + 'api/v1.0/GetOpenads'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetOpenads'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "123452345",
            "app_version": "1.0.6",
            "channel": "godinsec"
        }
        url = self.url + 'api/v1.0/GetOpenads'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.1.6",
            "channel": "godinsec"
        }
        url = self.url + 'api/v1.0/GetOpenads'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6",
        #     "channel": "godinsec"
        # }
        # url = self.url + 'api/v1.0/GetOpenads'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

    def test_vip_service_protocol(self):
        # no token
        print("**********no token**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/VipServiceProtocol'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 401, "no token test failed"
        print('no token test passed')
        print("##########no token##########")

        token = self.test_token()['body']['token']
        print(token)

        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/VipServiceProtocol'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "imei": "123456789012345"
        }
        url = self.url + 'api/v1.0/VipServiceProtocol'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "12345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/VipServiceProtocol'
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # # vip not service protocol
        # print("**********app invalid**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "app_version": "1.1.6"
        # }
        # url = self.url + 'api/v1.0/VipServiceProtocol'
        # r = requests.post(url=url, json=json_req, auth=(token, ''))
        # print(r.url)
        # print(r.text)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000033', "vip not service protocol test failed"
        # print('app invalid test passed')
        # print("##########vip not service protocol##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6"
        # }
        # url = self.url + 'api/v1.0/VipServiceProtocol'
        # r = requests.post(url=url, json=json_req, auth=(token, ''))
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

    def test_GetAdsIcon(self):
        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetAdsIcon'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "imei": "123456789012345"
        }
        url = self.url + 'api/v1.0/GetAdsIcon'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "12345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetAdsIcon'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.1.6"
        }
        url = self.url + 'api/v1.0/GetAdsIcon'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6"
        # }
        # url = self.url + 'api/v1.0/GetAdsIcon'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

    def test_activate_vip_member(self):
        url = self.url + 'api/v1.0/ActivateVipMember'

        # no token
        # print("**********no token**********")
        # json_req = {
        #     "imei": "866647020146354",
        #     "app_version": "1.0.6",
        #     "godin_id": "18835d61df97bc36fbad43db626705f2"
        # }
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # assert r.status_code == 401, "no token test failed"
        # print('no token test passed')
        # print("##########no token##########")

        # token = self.test_token()['body']['token']
        # print(token)
        token = self.test_token()['body']['token']
        print(token)

        # param missing
        print("**********para missing**********")
        json_req = {
            "imei": "123456789012345",
            "godin_id": '18835d61df97bc36fbad43db626705f2'
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "imei": "1111111",
            "app_version": "1.0.6",
            "godin_id": "18835d61df97bc36fbad43db626705f2",
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # success
        print("**********success**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": '55d21003b3a6519b136fc1b1fb051c5d'
        }
        r = requests.post(url=url, json=json_req, auth=(token, ''))
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success test failed"
        print('success test passed')
        print("##########success##########")

    def test_avatar_down_url(self):
        url = self.url + 'api/v1.0/GetAvatarAppUrl'

        # # param missing
        print("**********para missing**********")
        json_req = {
            "imei": "123456789012345",
            "version_code": 1,
            "number": 1,
            "app_name": 'fs1'
        }
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # # imei invalid
        # print("**********imei invalid**********")
        # json_req = {
        #     "imei": "1111111",
        #     "app_version": "1.0.6",
        #     "version_code": 1,
        #     "number": 1,
        #     "app_name": 'fs1'
        # }
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        # print('imei invalid test passed')
        # print("##########imei invalid##########")

        # # app invalid
        # print("**********app invalid**********")
        # json_req = {
        #     "imei": "123456789012345",
        #     "app_version": "1.1.6",
        #     "version_code": 1,
        #     "number": 1,
        #     "app_name": 'fs1'
        # }
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        # print('app invalid test passed')
        # print("##########app invalid##########")

        # avatar version not exist
        print("**********avatar version not exist**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "version_code": 10,
            "number": 10,
            "app_name": 'fs1'
        }
        r = requests.post(url=url, json=json_req)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000034', "avatar version not exist test failed"
        print('avatar version not exist test passed')
        print("##########avatar version not exist##########")

        # success
        print("**********success**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "version_code": 5,
            "number": 5,
            "app_name": 'fs4'
        }
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success test failed"
        print('success test passed')
        print("##########success##########")

    def test_checkappupdate(self):
        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "app_type": "5",
            "version_code": "1",
            "imei": "123456789012345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/CheckAppUpdate'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "app_type": "5",
            "version_code": "1",
            "imei": "123456789012345"
        }
        url = self.url + 'api/v1.0/CheckAppUpdate'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "app_type": "5",
            "version_code": "1",
            "imei": "12345678",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/CheckAppUpdate'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "app_type": "5",
            "version_code": "1",
            "imei": "123456789012345",
            "app_version": "1.1.1"
        }
        url = self.url + 'api/v1.0/CheckAppUpdate'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "app_type": "5",
        #     "version_code": "1",
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6"
        # }
        # url = self.url + 'api/v1.0/CheckAppUpdate'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

    def test_getwechatfeature(self):
        # # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "frame_version_code": "1",
            "imei": "123456789012345",
            "app_version": "1.0.3",
            "wechat_version": "6.5.4"
        }
        url = self.url + 'api/v1.0/GetWeChatFeature'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

        # param missing
        print("**********para missing**********")
        json_req = {
            "frame_version_code": "1",
            "imei": "123456789012345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetWeChatFeature'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        assert r.status_code == 400, "param missing test failed"
        print('param missing test passed')
        print("##########para missing##########")

        # imei invalid
        print("**********imei invalid**********")
        json_req = {
            "frame_version_code": "1",
            "imei": "123456345",
            "app_version": "1.0.6",
            "wechat_version": "6.5.4"
        }
        url = self.url + 'api/v1.0/GetWeChatFeature'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000013', "imei invalid test failed"
        print('imei invalid test passed')
        print("##########imei invalid##########")

        # app invalid
        print("**********app invalid**********")
        json_req = {
            "frame_version_code": "1",
            "imei": "123456789012345",
            "app_version": "1.1.6",
            "wechat_version": "6.5.4"
        }
        url = self.url + 'api/v1.0/GetWeChatFeature'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000015', "app invalid test failed"
        print('app invalid test passed')
        print("##########app invalid##########")

        # # in blacklist, add the imei in black list
        # print("**********in black list**********")
        # json_req = {
        #     "frame_version_code": "1",
        #     "imei": "123456789012345",
        #     "app_version": "1.0.6",
        #     "wechat_version": "6.5.4"
        # }
        # url = self.url + 'api/v1.0/GetWeChatFeature'
        # r = requests.post(url=url, json=json_req)
        # print(r.url)
        # print(r.text)
        # print(r.status_code)
        # ret = json.loads(r.text)
        # assert ret['head']['statuscode'] == '000014', "in black list test failed"
        # print('in black list test passed')
        # print("##########in black list##########")

        # already last version
        print("**********already last version**********")
        json_req = {
            "frame_version_code": "1",
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "wechat_version": "6.5.4"
        }
        url = self.url + 'api/v1.0/GetWeChatFeature'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000007', "already last version test failed"
        print('already last version test passed')
        print("##########already last version##########")

    def test_invite(self):
        # # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": "eefc78e937f99dfe156ad4fd548b13ce",
            "share_code": "4812012737",
            "number": "000001"
        }
        url = self.url + 'api/v1.0/GetInvitee'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)

    def test_count(self):
        # # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": "f881450a35fc9b803aefe56b7c338aa7",
            "number": "000005"
        }
        url = self.url + 'api/v1.0/GetCount'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)

    def test_feature(self):
        # # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "frame_version_code": "1",
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "version": "6.5.4",
            "version_code": 0
        }
        url = self.url + 'api/v1.0/Feature'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)

    def test_key(self):
        # # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "imei": "861504034843666",
            "app_version": "1.0.6",
            "key_id": "key1537862523349egcv"
        }
        url = self.url + 'api/v1.0/CheckKey'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)

    def test_juge_key(self):
        # # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "imei": "395125050989711",
            "app_version": "1.0.2",
            "num": "123"
        }
        url = self.url + 'api/v1.0/JudgeAddKey'
        r = requests.get(url=url, params=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)

    def test_buy_key(self):
        # # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "imei": "862534031404101",
            "app_version": "1.0.6",
            "channel": "VSSQ"
        }
        url = self.url + 'api/v1.0/Buykey'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)

    def test_channel_frame_update(self):
        # # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "frames": [{'number': 1, 'version_code': 1}],
            "imei": "123456789012345",
            "app_version": "1.2.12",
            "channel": 'gind'
        }
        url = self.url + 'api/v1.0/ChannelFrameUpdate'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)

    def test_channel_plugin_update(self):
        # # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.2.12",
            "frame_version_code": "2",
            "plugins":
            [
                {"package_name": "Permission", "version_code": "1"}
            ],
            "channel": 'gind'
        }
        url = self.url + 'api/v1.0/ChannelPluginUpdate'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)

    def test_channel_avatar_down_url(self):

        print("**********para missing**********")
        json_req = {
            "imei": "123456789012345",
            "version_code": 1,
            "app_version": "1.2.12",
            "number": 1,
            "app_name": 'fs1',
            "channel": 'gind'
        }
        url = self.url + 'api/v1.0/AvatarChannelAppUrl'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)

    def test_channel_app_update(self):

        print("**********para missing**********")
        json_req = {
            "app_type": "4",
            "app_version": "1.0.1",
            "imei": "123456789012345",
            "version_code": "1",
            "channel": 'gind'
        }
        url = self.url + 'api/v1.0/ChannelAppUpdate'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)

    def test_commu_roup(self):

        print("**********para missing**********")
        json_req = {
            "g_type": 1,
            "app_version": "1.0.1",
            "imei": "123456789012345"
        }
        url = self.url + 'api/v1.0/GetCommGroup'
        r = requests.get(url=url, params=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)

    def test_key_channel(self):

        print("**********para missing**********")
        json_req = {
            "channel": "huawei",
            "app_version": "1.0.1",
            "imei": "123456789012345"
        }
        url = self.url + 'api/v1.0/GetCh'
        r = requests.get(url=url, params=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)

    def test_get_activity(self):
        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "godin_id": "429a2d57e70bb09c2080d7b029ab14dc",
            "imei": "123456789012345",
            "app_version": "1.0.6"
        }
        url = self.url + 'api/v1.0/GetActivity'
        r = requests.get(url=url, params=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

    def test_activity_func(self):
        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "godin_id": "fa54a842ed1ab94b8334f3c318296e21",
            "imei": "395125050989799",
            "app_version": "1.0.6",
            "activity_id": 1,
            "number": '000001',
            "event": "100000",
            "attach": {}
        }
        url = self.url + 'api/v1.0/ActivityFunc'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

    def test_get_key_info(self):
        # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "user_id": "15011329055",
            "we_key_id": "2222222222"
        }
        url = self.url + 'api/v1.0/we_key'
        r = requests.get(url=url, params=json_req)
        print(r.url)
        print(r.text)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success with bundle test failed"
        print('success test passed')
        print("##########success with bundle##########")

    def test_we_make_key(self):

        print("**********para missing**********")
        json_req = {
            "user_id": "15801065647",
            "key_count": 24,
            "ad_time": 3,
            "we_key_id": "333"
        }
        url = self.url + 'api/v1.0/m_key'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)

    def test_crack_make_key(self):

        print("**********para missing**********")
        json_req = {
            "user_id": "15801065647",
            "key_count": 20,
            "ad_time": 30,
            "we_key_id": "333"
        }
        url = self.url + 'api/v1.0/cm_key'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)

    def test_notice(self):
        # # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "imei": "862534031404101",
            "flag_id": 0,
            "app_version": "1.0.1"
        }
        url = self.url + 'api/v1.0/notice'
        r = requests.get(url=url, params=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)

    def test_read_notice(self):
        # # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "imei": "123456789012345",
            "notice_id": 'n20180822163030',
            "app_version": "1.0.1"
        }
        url = self.url + 'api/v1.0/read_notice'
        r = requests.get(url=url, params=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)

    def test_avatar_buy_vip_ware(self):
        url = self.url + 'api/v1.0/ava_b_vip'
        json_req = {
            "imei": "866647020146354",
            "app_version": "1.0.6",
            "godin_id": "429a2d57e70bb09c2080d7b029ab14dc",
            "ware_id": "1"
        }
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)

    def test_new_key(self):
        # # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "imei": ["561504034843978", "461504034843978", "461504034843978", "461504034843978", "461504034843111",
                     "461504034843222", "4615040", "461504034843333", "4615040348439789", "461504034843444",
                     "4615040348439"],
            "app_version": "1.0.6",
            "key_id": "WSLHZZYDGD1"
        }
        url = self.url + 'api/v1.0/check_k'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)

    def test_new_juge_key(self):
        # # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "imei": ["561504034843978", "461504034843978", "461504034843978", "461504034843978", "461504034843111",
                     "461504034843222", "4615040", "461504034843333", "4615040348439789", "461504034843444",
                     "4615040348439"],
            "app_version": "1.0.2",
            "num": "123"
        }
        url = self.url + 'api/v1.0/judge_k'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)

    def test_check_app(self):
        # # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "versioncode": 1,
            "versionname": "1.0.2",
            "md5": "sssssssss",
            "build_time": "sssssssqqqq",
            "build_rev": "www"
        }
        url = self.url + 'api/v1.0/check_app'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)

    def test_phone(self):
        # # success, with bundle
        print("**********success with bundle**********")
        json_req = {
            "godin_id": '429a2d57e70bb09c2080d7b029ab14d1'
        }
        url = self.url + 'api/v1.0/verify'
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)

    def test_buy(self):
        url = self.url + 'api/v1.0/buy'
        print("**********success-buy_month**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": "bdb3c26bf367d92fbf990cde2d36cd1d",
            "ware_id": "10001"
        }
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "test failed"
        print("##########success##########")

    def test_status(self):
        url = self.url + 'api/v1.0/status'
        # success
        print("**********success**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "status": 1,
            "godin_id": '4b941562804f13603cdcc0ec898e582f'
        }
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success test failed"
        print('success test passed')
        print("##########success##########")

    def test_ids(self):
        url = self.url + 'api/v1.0/ids'
        # success
        print("**********success**********")
        json_req = {
            "imei": "123456789012345",
            "app_version": "1.0.6",
            "godin_id": '4b941562804f13603cdcc0ec898e582f',
            "number": 10,
            "id": "12233213343343"
        }
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success test failed"
        print('success test passed')
        print("##########success##########")

    def test_open_screen(self):
        url = self.url + 'api/v1.0/open_screen'
        # success
        print("**********success**********")
        json_req = {
            "imei": "395125050989799",
            "app_version": "1.0.6",
            "channel": "huwawei"
        }
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success test failed"
        print('success test passed')
        print("##########success##########")

    def test_open_statistics(self):
        url = self.url + 'api/v1.0/open_statistics'
        # success
        print("**********success**********")
        json_req = {
            "imei": "395125050989799",
            "app_version": "1.0.6",
            "ad_info":[
	                {'ad_id': 2, 'type': 0},
	                {'ad_id': 2, 'type': 1}
	                ]
        }
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success test failed"
        print('success test passed')
        print("##########success##########")

    def test_f_vip(self):
        url = self.url + 'api/v1.0/f_vip'
        # success
        print("**********success**********")
        json_req = {
            "imei": "395125050989799",
            "app_version": "1.0.6",
            "godin_id": '4b941562804f13603cdcc0ec898e582f',
        }
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success test failed"
        print('success test passed')
        print("##########success##########")

    def test_b_assistant(self):
        url = self.url + 'api/v1.0/b_assistant'
        # success
        print("**********success**********")
        json_req = {
            "imei": "395125050989799",
            "app_version": "1.0.6"
        }
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success test failed"
        print('success test passed')
        print("##########success##########")

    def test_b_link(self):
        url = self.url + 'api/v1.0/b_link'
        # success
        print("**********success**********")
        json_req = {
            "imei": "395125050989799",
            "app_version": "1.0.6"
        }
        r = requests.post(url=url, json=json_req)
        print(r.url)
        print(r.text)
        print(r.status_code)
        ret = json.loads(r.text)
        assert ret['head']['statuscode'] == '000000', "success test failed"
        print('success test passed')
        print("##########success##########")



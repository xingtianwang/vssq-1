#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: tool.py
#   Author: bao.zhang
#   Mail: bao.zhang@godinsec.com
#   Created Time: 17/11/20
# *************************************************************************

import os
# import modRes
# import reSign
from app.api_1_0.apktool import modRes
from app.api_1_0.apktool import reSign
from flask import current_app
import datetime


# 反编译接口
# avatar_path: 分身基础版绝对路径
# number: 分身基础版对应的编号
# avatar_id: 分身基础版对应的id
def decompile(avatar_path, number):
    if len(avatar_path) < 10:
        return ''
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    tag = current_app.config['APK_TAG']
    # tag = 'WeApk'
    dest_path = os.path.join(os.getcwd(), tag, 'decompile', str(number), current_time)
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    apktool_cmd = "apktool d -s -f " + avatar_path + " -o " + dest_path
    os.system(apktool_cmd)

    return os.path.join(tag, 'decompile', str(number), current_time)


# 重新打包签名接口
# decompile_path: 反编译后的绝对路径
# number: 分身编号
# app_name: 应用名称
def repack(decompile_path, number, app_name):
    # begain = datetime.datetime.now()
    if len(decompile_path) < 10:
        return ''
    tag = current_app.config['APK_TAG']
    # tag = 'WeApk'
    current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    apk_name = 'we_xavatar' + str(number) + '.apk'
    apk_path = os.path.join(os.getcwd(), tag, 'WeXavtar', str(number), current_time)
    if not os.path.exists(apk_path):
        os.makedirs(apk_path)

    # 修改apk名称
    modRes.modifyRes(app_name, decompile_path)

    # 重打包apk
    cmd_packapk = "apktool b -f " + decompile_path
    os.system(cmd_packapk)

    # 重签名apk
    for filename in os.listdir(os.path.join(os.getcwd(), decompile_path + "/dist/")):
        temp_name = filename
    newapkpath = decompile_path + "/dist/" + temp_name
    apk_unsign_path = os.path.join(apk_path, "unsign.apk")
    cmd_cpnewapk = "cp " + newapkpath + " " + apk_unsign_path
    os.system(cmd_cpnewapk)
    apk_sign_path = os.path.join(apk_path, apk_name)
    reSign.reSigner(apk_unsign_path, apk_sign_path)

    # 删除中间文件
    cmd_remove_unsignapk = "rm -f " + apk_unsign_path
    os.system(cmd_remove_unsignapk)
    # end_time = datetime.datetime.now()
    # print(end_time - begain)
    return os.path.join(tag, 'WeXavtar', str(number), current_time, apk_name)

"""
if __name__ == "__main__":
    addr = decompile(os.path.join(os.getcwd(), 'WeApk/1rongrong.apk'), 1)
    print(addr)

    addr1 = repack(os.path.join(os.getcwd(), addr), 1, '宝')
    print(addr1)
"""


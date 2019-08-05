#!/usr/bin/env python
# -*- coding:utf-8 -*-
# ************************************************************************
#   Copyright © 2017 Godinsec. All rights reserved.
#   File Name: tool.py
#   Author: zhaochen
#   Mail: chen.zhao@godinsec.com
#   Created Time: 17/12/29
# ************************************************************************
import os, shutil
from flask import current_app
from zipfile import ZipFile
import ctypes
import time
from datetime import datetime
# lib = current_app.extensions['avater_lib']


def reSigner(oldapk, newapk, keystore="guding.keystore", keypass="Guding@123!"):
    cmd_sign = r'jarsigner -digestalg SHA1 -sigalg MD5withRSA -verbose' \
               r' -keystore %s -storepass %s -signedjar %s %s guding' % (keystore, keypass, newapk, oldapk)

    os.system(cmd_sign)


def init_dir(dir_type):

    def initialize_dir(dir_name, tag):
        for dir in dir_name:
            dest_path = os.path.join(os.getcwd(), tag, dir)
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)

    def create_dir(dir_name):
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

    if isinstance(dir_type, list):
        return initialize_dir
    return create_dir


def format_apk(apk_path, number, app_name):
    start_time = datetime.now()
    print('-------begin time',  start_time)
    current_time = str(int(time.time() * 10000))
    package_name = '{0}_{1}'.format(str(number), current_time)
    tag = current_app.config['APK_TAG']
    init_dir(list())(['packages', 'new_package'], tag)
    num_dir = os.path.join(os.getcwd(), tag, 'packages/' + str(number))
    init_dir(str)(num_dir)
    apk_dir = num_dir + '/' + package_name
    init_dir(str)(apk_dir)
    mv_apk_path = os.path.join(apk_dir + '/' + apk_path.split('/')[-1])
    shutil.copyfile(apk_path, mv_apk_path)

    u = ZipFile(mv_apk_path, 'r')
    u.extract('AndroidManifest.xml',  apk_dir)
    u.close()

    xml_path = os.path.join(apk_dir + '/' + 'AndroidManifest.xml')

    '''utf-16编码用户字符串'''
    size = len(app_name)
    naonaosize = size * 2 + 2 + 2
    sizestr = chr(size)

    type_char_array = ctypes.c_ushort * naonaosize
    temp = type_char_array()
    j = 0

    sizestr.encode('utf-16')
    for i in sizestr:
       x = ord(i)
       temp[j] = x
       j += 1

    app_name.encode('utf-16')
    for i in app_name:
       x = ord(i)
       temp[j] = x
       j += 1

    temp[j] = 0x00
    temp[j+1] = 0x00

    '''修改xml并压缩'''
    lib = current_app.extensions['avater_lib']
    bytes = xml_path.encode('utf-8')
    lib.modtest(temp, naonaosize, bytes)
    cmd_zip_Axml = "cd {0}; /usr/bin/zip -m {1} {2}".format(apk_dir, apk_path.split('/')[-1], 'AndroidManifest.xml')
    cmd_rm_meta = "cd {0}; /usr/bin/zip -d {1} {2}".format(apk_dir, apk_path.split('/')[-1], "META-INF/*")
    os.system(cmd_zip_Axml)
    os.system(cmd_rm_meta)

    new_name = 'WeAvatar' + current_time + '_' + str(number) + '.' + 'apk'
    apk_sign_path = apk_dir + '/' + new_name
    reSigner(mv_apk_path, apk_sign_path)
    shutil.move(apk_sign_path, os.path.join(os.getcwd(), current_app.config['APK_TAG'] + '/' + 'new_package'))

    # '''删除中间文件/目录'''
    shutil.rmtree(apk_dir)
    end_time = datetime.now()

    print('-------end time',  end_time - start_time)
    return current_app.config['APK_TAG'] + '/' + 'new_package' + '/' + new_name

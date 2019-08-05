#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: apk.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 16/9/27
# *************************************************************************
import zipfile
import re
from . import apk


class APKParser(object):
    """
    function:
        parse AndroidManifest.xml and get attributes from it
    """

    def __init__(self, apk_dir):
        self._file_name = "AndroidManifest.xml"
        zfile = zipfile.ZipFile(apk_dir)
        ap = apk.AXMLPrinter(zfile.read(self._file_name))
        xml = ap.get_buff()
        buff_len = 6000
        if len(xml) < 6000:
            buff_len = len(xml)
        code = re.search("manifest[\s\S]*?versionCode=\"(.*?)\"", xml[0:buff_len])
        name = re.search("manifest[\s\S]*?versionName=\"(.*?)\"", xml[0:buff_len])
        pack = re.search("manifest[\s\S]*?package=\"(.*?)\"", xml[0:buff_len])
        channel = re.search("meta-data[\s\S]android:name=\"UMENG_CHANNEL\"[\s\S]android:value=\"(.*?)\"", xml[0:buff_len])

        self.version_code = int(code.group(1), 10)
        self.version_name = name.group(1)
        self.package = pack.group(1)
        if channel:
            self.channel = channel.group(1)
        else:
            self.channel = ''

    def get_version_code(self):
        return self.version_code

    def get_version_name(self):
        return self.version_name

    def get_package(self):
        return self.package

    def get_channel(self):
        return self.channel


if __name__ == "__main__":
    apkinfo = APKParser("/Users/allan/Desktop/ASDAPhone_Product.apk")
    print("versionCode: %s" % apkinfo.get_version_code())
    print("versionName: %s" % apkinfo.get_version_name())
    print("package: %s" % apkinfo.get_package())

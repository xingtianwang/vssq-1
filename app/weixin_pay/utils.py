#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2017 Godinsec. All rights reserved.
#   File Name: utils.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 2017/2/23
# *************************************************************************
import datetime
import random
import string


def gen_order_id():
    return datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S') +\
           ''.join(random.sample(string.ascii_letters + string.digits, 18))


def process_weinxin_bill(data):
    res = data.split('\r\n')
    fields = res[0].split(',')
    # 去掉每条数据前的特殊字符
    fields[0] = fields[0][1:]
    details = list()
    for j in range(1, len(res) - 3):
        temp = res[j].split(',`')
        # 去掉交易时间值前边的反引号
        temp[0] = temp[0][1:]
        details.append(dict(zip(fields, temp)))
    res[-2] = res[-2][1:]
    total = dict(zip(res[-3].split(','), res[len(res)-2].split(',`')))
    return total, details

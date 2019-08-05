#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import current_app
from app import db, create_app
import datetime
import json
from app.api_1_0.models import BusinessSecondPool, DataLock
import os


def insert_business_second_pool():
    app = create_app('production')
    app_context = app.app_context()
    app_context.push()
   
    i = 0 
    total_count = 0
    f = open(os.path.join(os.getcwd(), 'accurate_pool.json'), 'r')
    for line in f.readlines():
        line=line.strip('\n')
        val = json.loads(line)
        info = BusinessSecondPool()
        info.id = total_count + 1
        info.we_id = val['we_id']
        info.we_mark = val['we_mark']
        info.count = 0
        info.update_time = datetime.datetime.now().date()
        db.session.add(info)
        total_count += 1
        i += 1 
        if i % 100 == 0:
            db.session.commit()
            i = 0
        if total_count == 1000000:
            f.close()
            break
    DataLock.query.filter(DataLock.id == 3).update({'count': 0, 'max_id': total_count})
    db.session.commit()

if __name__ == '__main__':
    insert_business_second_pool()

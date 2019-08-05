#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import current_app
from app import db, create_app
import os
from app.api_1_0.models import UserKeyRecord


def check_key_imei():
    app = create_app('production')
    app_context = app.app_context()
    app_context.push()

    no_f = open(os.path.join(os.getcwd(), 'no_imei.txt'), 'w')
    with open(os.path.join(os.getcwd(), 'imei.txt'), 'r') as file:
        with open(os.path.join(os.getcwd(), 'key_imei.txt'), 'w') as f:
            imei_list = file.readlines()
            for imei in imei_list:
                user_key = UserKeyRecord.query.filter_by(imei=imei.strip()).first()
                if user_key is not None:
                    key_id = user_key.key_id
                    query = UserKeyRecord.query.filter_by(key_id=key_id)
                    imei_list = []
                    for key in query:
                        imei_list.append(key.imei)
                    f.write('%s\n' % ({key_id: imei_list}))
                else:
                    no_f.write('%s\n' % imei.strip())

if __name__ == '__main__':
    check_key_imei()

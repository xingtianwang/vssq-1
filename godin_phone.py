#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import current_app
from app import db, create_app
import os
from app.api_1_0.models import GodinAccount


def godin_info():
    app = create_app('production')
    app_context = app.app_context()
    app_context.push()

    phone = open(os.path.join(os.getcwd(), 'new_xiaofeizhe.txt'), 'w')
    with open(os.path.join(os.getcwd(), 'xiaofeizhe.txt'), 'r') as f:
        godin_list = f.readlines()
        for godin_id in godin_list:
                godin_info = GodinAccount.query.filter_by(godin_id=godin_id.strip()).first()
                if godin_info is not None:
                    phone.write('%s\n' % godin_info.phone_num)

if __name__ == '__main__':
    godin_info()

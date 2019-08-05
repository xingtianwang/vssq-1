#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: authentication.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 2016/12/23
# *************************************************************************
from flask import g
from app import http_auth
from app.api_1_0.models import UserInfo, GodinAccount


@http_auth.verify_password
def verify_password(phone_num_or_token, password):
    if phone_num_or_token == '':
        return False
    if password == '':
        g.current_user = UserInfo.verify_auth_token(phone_num_or_token)
        g.token_used = True
        return g.current_user is not None
    else:
        user = GodinAccount.query.filter_by(phone_num=phone_num_or_token).first()
        if user is None:
            return False
        g.current_user = user.user_info
        g.token_used = False
        return user.user_info.verify_password(password)

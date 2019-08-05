#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: urls.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 16/9/21
# # *************************************************************************
from flask import Blueprint
from .views import get_captcha, login, logout, change_password, unconfirmed,\
    before_request, confirm, resend_confirmation, forbidden_page, active_request

auth = Blueprint('auth', __name__, static_folder='static', template_folder='templates')

auth.before_app_request(before_request)

auth.add_url_rule('/captcha', view_func=get_captcha)
auth.add_url_rule('/login', view_func=login, methods=['GET', 'POST'])
auth.add_url_rule('/change_password', view_func=change_password, methods=['GET', 'POST'])
auth.add_url_rule('/logout', view_func=logout)
auth.add_url_rule('/confirm/<token>', view_func=confirm)
auth.add_url_rule('/confirm', view_func=resend_confirmation)
auth.add_url_rule('/unconfirmed', view_func=unconfirmed)
auth.add_url_rule('/forbidden/<int:req_active>', view_func=forbidden_page)
auth.add_url_rule('/active', view_func=active_request)

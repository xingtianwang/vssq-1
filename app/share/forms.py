#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: forms.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 2016/10/17
# *************************************************************************
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class ShareForm(Form):
    extract_code = StringField('提取码', validators=[DataRequired(message='用户名不能为空')])
    submit = SubmitField('提交')

#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: __init__.py.py
#   Author: bao.zhang
#   Mail: bao.zhang@godinsec.com
#   Created Time: 2017/12/01
# *************************************************************************
from flask import Blueprint

guide = Blueprint('guide', __name__, static_folder='statics', template_folder='templates')

from .views import index

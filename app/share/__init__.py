#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: __init__.py.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 2016/10/17
# *************************************************************************
from flask import Blueprint

share = Blueprint('share', __name__, static_folder='static', template_folder='templates')

from . import views

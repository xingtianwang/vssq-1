#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: __init__.py.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 16/9/22
# *************************************************************************
from app.config.config import Config
from .urls import manage
from app.auth.models import Role, Department


@manage.app_context_processor
def inject_role_and_departmeng():
    return dict(Role=Role, Department=Department, APP_TYPE_DICT=Config.APP_TYPE_DICT,
                ADS_SOURCE=Config.ADS_SOURCE, OPEN_SCREEN_ADS_POSITION=Config.OPEN_SCREEN_ADS_POSITION,
                BANNER_ADS_POSITION=Config.BANNER_ADS_POSITION, GAME_PARK_TYPE=Config.GAME_PARK_TYPE,
                INTERACTIVE_ADS_SOURCE=Config.INTERACTIVE_ADS_SOURCE,
                INTERACTIVE_ADS_POSITION=Config.INTERACTIVE_ADS_POSITION, ADS_ICON=Config.ADS_ICON)

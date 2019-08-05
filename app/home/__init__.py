#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import Blueprint

home = Blueprint('home', __name__, static_folder='statics', template_folder='templates')

from .views import index

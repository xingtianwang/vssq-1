#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: __init__.py.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 16/9/21
# *************************************************************************
from celery import Celery, platforms
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_pagedown import PageDown
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_moment import Moment
from flask_wtf import CsrfProtect
from flask_cache import Cache
from flask_httpauth import HTTPBasicAuth
import ctypes, os
from .config.config import config
from flask_redis import FlaskRedis
#from .FlaskRedisPool  import FlaskRedisPool
import warnings
from flask.exthook import ExtDeprecationWarning

#
bootstrap = Bootstrap()
page_down = PageDown()
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
http_auth = HTTPBasicAuth()
moment = Moment()
cache = Cache()
cache_simple = Cache()
csrf = CsrfProtect()
celery = Celery()
redis = FlaskRedis()
#redis = FlaskRedisPool()
warnings.simplefilter('ignore', ExtDeprecationWarning)

login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    bootstrap.init_app(app)
    page_down.init_app(app)
    db.init_app(app)
    db.app = app
    mail.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    cache.init_app(app)
    cache_simple.init_app(app, config={'CACHE_TYPE': 'simple'})
    redis.init_app(app)
    app.jinja_env.add_extension('jinja2.ext.do')
    global celery
    celery = make_celery(app)
    # csrf.init_app(app)

    so = ctypes.cdll.LoadLibrary
    lib = so(os.path.join(os.path.join(os.getcwd(), 'app/api_1_0/apktool/', 'modaxml.so')))
    app.extensions['avater_lib'] = lib

    from .manage.urls import manage as manage_blueprint
    app.register_blueprint(manage_blueprint, url_prefix='/vssq/manage')

    from .auth.urls import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/vssq/auth')

    from .api_1_0.urls import api_v_1_0 as api_v_1_0_blueprint
    app.register_blueprint(api_v_1_0_blueprint, url_prefix='/vssq/api/v1.0')

    from .api_1_1.urls import api_v_1_1 as api_v_1_1_blueprint
    app.register_blueprint(api_v_1_1_blueprint, url_prefix='/vssq/api/v1.1')

    from .share import share as share_blueprint
    app.register_blueprint(share_blueprint, url_prefix='/vssq/share')

    from .guide import guide as guide_blueprint
    app.register_blueprint(guide_blueprint, url_prefix='/vssq/guide')

    from .weixin_pay.urls import weixinpay_blueprint
    app.register_blueprint(weixinpay_blueprint, url_prefix='/vssq/wxpay')

    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint, url_prefix='/vssq')

    return app


def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'], broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    platforms.C_FORCE_ROOT = True

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

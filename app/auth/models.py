#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: models.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 16/9/22
# *************************************************************************
from datetime import datetime

from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


class Role(object):
    ADMIN = 0x01
    AUDITOR = 0x02
    USER = 0x03

    description = {ADMIN: '超级管理员', AUDITOR: '审计管理员', USER: '普通管理员'}


class Department(object):
    LEADER = 0x00
    PM = 0x01
    OPERATION = 0x02
    PRODUCTION = 0x03
    QA = 0x04
    DEVELOP = 0x05
    DEVELOP_SU = 0x06

    description = {LEADER: '管理层', PM: '项目经理', OPERATION: '运营部',
                   PRODUCTION: '产品部', QA: '质量管理部', DEVELOP: '研发部', DEVELOP_SU: '研发部-开发者'}


class AdminUser(db.Model, UserMixin):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(128), unique=True)
    role = db.Column(db.Integer)
    department = db.Column(db.Integer)
    confirmed = db.Column(db.Boolean, default=False)
    forbidden = db.Column(db.Boolean, default=False)
    join_time = db.Column(db.DateTime(), default=datetime.now)
    last_seen = db.Column(db.DateTime(), default=datetime.now)

    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirm_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def can(self, role, department):
        if self.role == role:
            if role == Role.ADMIN or role == Role.AUDITOR:
                return True
            elif role == Role.USER:
                if self.department == Department.DEVELOP_SU:
                    return True
                elif department == self.department:
                    return True
                else:
                    return False
        else:
            return False

    def ping(self):
        self.last_seen = datetime.now()
        db.session.add(self)
        db.session.commit()


class AdminLog(db.Model):
    __tablename__ = 'admin_log'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    actions = db.Column(db.String(128))
    results = db.Column(db.String(128))
    client_ip = db.Column(db.String(64))
    log_time = db.Column(db.DateTime, default=datetime.now)


class AnonymousUser(AnonymousUserMixin):

    def can(self, role, department):
        return False


@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))


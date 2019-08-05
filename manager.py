#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: manager.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 16/9/21
# *************************************************************************
from flask import current_app
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db
from app.auth.models import AdminUser, Role, Department

app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)

# 用于supervisord启动celery任务
from app import celery


@manager.command
def runserver():
    app.run(host=current_app.config['SERVER_ADDRESS'],
            port=current_app.config['SERVER_PORT'],
            debug=current_app.config['DEBUG'])


def make_shell_context():
    return dict(app=app, AdminUser=AdminUser, Role=Role, Department=Department)


@manager.option('-u', '--username', dest='username', default='admin')
@manager.option('-e', '--email', dest='email')
@manager.option('-p', '--password', dest='password')
def create_admin(username, email, password):
    if username == 'admin':
        username = input('Username(default admin):')
    if email is None:
        email = input('Email:')
    if password is None:
        password = input('Password:')
    user = AdminUser()
    user.username = username
    user.email = email
    user.password = password
    user.department = Department.LEADER
    user.role = Role.ADMIN
    if AdminUser.query.filter_by(username=username, email=email).first() is None:
        db.session.add(user)
        db.session.commit()
    else:
        print('user exists')


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()

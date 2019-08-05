#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: forms.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 16/9/21
# *************************************************************************
from flask import flash
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Length, Regexp, Email, EqualTo, ValidationError, DataRequired
from .models import AdminUser


class BaseForm(Form):
    username = StringField('用户名', validators=[DataRequired(message='用户名不能为空'), Length(4, 20, message='用户名长度必须在4-20之间'),
                                              Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, '包含非法字符')])
    password = PasswordField('密码', validators=[DataRequired(message='密码不能为空'),
                                               Length(8, 30, message='密码长度必须在8-30之间')])
    captcha = StringField('验证码', validators=[DataRequired(message='验证码不能为空'), Length(4, 4, message='验证码长度不为4')])


class LoginForm(BaseForm):
    remember_me = BooleanField('记住登陆', default=False)
    submit = SubmitField('登陆')


class RegisterBaseForm(BaseForm):
    email = StringField('邮箱', validators=[DataRequired(message='邮箱不能为空'), Email()])
    password2 = PasswordField('确认密码', validators=[DataRequired(message='确认密码不能为空'),
                                                  Length(8, 30, message='确认密码长度必须在8-30之间'),
                                                  EqualTo('password', message='两次输入密码必须一致')])

    def validate_username(self, field):
        if AdminUser.query.filter_by(username=field.data).first() is not None:
            raise ValidationError('用户名已存在')

    def validate_email(self, field):
        if AdminUser.query_.filter_by(email=field.data).first() is not None:
            raise ValidationError('邮箱已注册')


class RegisterForm(RegisterBaseForm):
    submit = SubmitField('注册')


class AddUserForm(RegisterBaseForm):
    submit = SubmitField('添加')


class ChangePasswordForm(Form):
    old_password = PasswordField('旧密码', validators=[DataRequired(message='旧密码不能为空')])
    new_password = PasswordField('新密码', validators=[DataRequired(message='新密码不能为空'),
                                                    Length(8, 30, message='密码长度必须在8-30之间')])
    repeat_password = PasswordField('确认密码', validators=[DataRequired(message='新密码不能为空'),
                                                        Length(8, 30, message='密码长度必须在8-30之间'),
                                                        EqualTo('new_password', message='确认密码与密码不一致')])
    submit = SubmitField('提交')





#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: views.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 16/9/21
# *************************************************************************
from flask import flash
from flask import make_response
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.utils import redirect

from app import db
from app.helper import send_mail, add_admin_log
from .captcha import Captcha
from flask_login import login_user, logout_user, login_required, current_user

from .models import AdminUser, Role
from .forms import LoginForm, ChangePasswordForm


def get_captcha():
    img, captcha = Captcha().create_validate_code()
    session['captcha'] = captcha.lower()
    response = make_response(img)
    response.headers['Content-Type'] = 'image/jpeg'
    return response


def login():
    form = LoginForm()
    if form.validate_on_submit():
        if 'captcha' not in session or form.captcha.data.lower() != session['captcha']:
            flash('验证码错误', category='info')
            add_admin_log(user=form.username.data, actions='登陆', client_ip=request.remote_addr, results='验证码错误')
        else:
            user = AdminUser.query.filter_by(username=form.username.data).first()
            if user is not None and user.verify_password(password=form.password.data):
                login_user(user, remember=form.remember_me.data)
                end_point = 'manage.index'
                if user.role == Role.ADMIN:
                    end_point = 'manage.list_admin_user'
                elif user.role == Role.AUDITOR:
                    end_point = 'manage.audit_user'
                else:
                    end_point = 'manage.index'
                add_admin_log(user=user.username, actions='登陆', client_ip=request.remote_addr, results='成功')
                return redirect(url_for(request.args.get('next') or end_point))
            add_admin_log(user=form.username.data, actions='登陆', client_ip=request.remote_addr, results='用户名或密码错误')
            flash('用户名或密码错误')
    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True

    return render_template('auth/login.html', form=form)


@login_required
def logout():
    add_admin_log(user=current_user.username, actions='退出登陆', client_ip=request.remote_addr, results='成功')
    logout_user()
    return redirect(url_for('auth.login'))


@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = AdminUser.query.filter_by(username=current_user.username).first()
        if not user.verify_password(form.old_password.data):
            flash('旧密码错误')
            add_admin_log(current_user.username, '修改密码', request.remote_addr, '旧密码错误')
        else:
            user.password = form.new_password.data
            db.session.add(user)
            db.session.commit()
            flash('密码修改成功')
            add_admin_log(current_user.username, '修改密码', request.remote_addr, '成功')
        return redirect(url_for('auth.change_password'))

    flag = False
    for field, error in form.errors.items():
        if not flag:
            flash(error[0])
            flag = True
    return render_template('auth/change_password.html', form=form)


def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint[:5] != 'auth.'\
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))
    if current_user.is_authenticated and current_user.forbidden \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.forbidden_page', req_active=False))


@login_required
def confirm(token):
    end_point = 'manage.get_reg_user_info'
    if current_user.role == Role.ADMIN:
        end_point = 'manage.list_admin_user'
    elif current_user.role == Role.AUDITOR:
        end_point = 'manage.audit_user'
    else:
        end_point = 'manage.get_reg_user_info'

    if current_user.confirmed:
        return redirect(url_for(request.args.get('next') or end_point))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
        add_admin_log(user=current_user.username, actions='确认', client_ip=request.remote_addr, results='确认成功')
        return redirect(url_for(request.args.get('next') or end_point))
    else:
        flash('confirm invalid')
        add_admin_log(user=current_user.username, actions='确认', client_ip=request.remote_addr, results='无效确认')
        return redirect(url_for('auth.unconfirmed'))


@login_required
def unconfirmed():
    if current_user.confirmed:
        end_point = 'manage.get_reg_user_info'
        if current_user.role == Role.ADMIN:
            end_point = 'manage.list_admin_user'
        elif current_user.role == Role.AUDITOR:
            end_point = 'manage.audit_user'
        else:
            end_point = 'manage.get_reg_user_info'
        return redirect(url_for(request.args.get('next') or end_point))
    else:
        return render_template('auth/unconfirmed.html')


def resend_confirmation():
    token = current_user.generate_confirm_token()
    send_mail([current_user.email], 'Confirm your account', 'auth/email/confirm', user=current_user, token=token)
    flash('A new confirm email has been sent to you ,check you email')
    add_admin_log(user=current_user.username, actions='重新发送确认', client_ip=request.remote_addr, results='成功')
    return redirect(url_for('auth.unconfirmed'))


@login_required
def forbidden_page(req_active=False):
    if not current_user.forbidden:
        end_point = 'manage.get_reg_user_info'
        if current_user.role == Role.ADMIN:
            end_point = 'manage.list_admin_user'
        elif current_user.role == Role.AUDITOR:
            end_point = 'manage.audit_user'
        else:
            end_point = 'manage.get_reg_user_info'
        return redirect(url_for(request.args.get('next') or end_point))
    else:
        return render_template('auth/forbidden.html', req_active=req_active)


@login_required
def active_request():
    admin_user = AdminUser.query.filter_by(role=Role.ADMIN).first()
    if admin_user is not None:
        send_mail([admin_user.email], 'Account re-active', 'auth/email/active',
                  admin_user=admin_user, user=current_user)
        add_admin_log(user=current_user.username, actions='发送激活请求', client_ip=request.remote_addr, results='成功')
    return redirect(url_for('auth.forbidden_page', req_active=True))




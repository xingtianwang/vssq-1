#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: views.py
#   Author: bao.zhang
#   Mail: bao.zhang@godinsec.com
#   Created Time: 2017/12/01
# *************************************************************************
from flask import render_template
from . import guide


@guide.route('/')
@guide.route('/index')
def index():
    return render_template("index.html")


@guide.route('/details01')
def details01():
    return render_template("details01.html")


@guide.route('/details02')
def details02():
    return render_template("details02.html")


@guide.route('/details03')
def details03():
    return render_template("details03.html")


@guide.route('/tutorial')
def tutorial():
    return render_template("tutorial.html")


@guide.route('/tutorial01')
def tutorial01():
    return render_template("tutorial01.html")


@guide.route('/tutorial02')
def tutorial02():
    return render_template("tutorial02.html")


@guide.route('/tutorial03')
def tutorial03():
    return render_template("tutorial03.html")


@guide.route('/tutorial04')
def tutorial04():
    return render_template("tutorial04.html")


@guide.route('/tutorial05')
def tutorial05():
    return render_template("tutorial05.html")


@guide.route('/tutorial06')
def tutorial06():
    return render_template("tutorial06.html")


@guide.route('/tutorial07')
def tutorial07():
    return render_template("tutorial07.html")


@guide.route('/tutorial08')
def tutorial08():
    return render_template("tutorial08.html")


@guide.route('/tutorial09')
def tutorial09():
    return render_template("tutorial09.html")


@guide.route('/icon')
def icon():
    return render_template("icon.html")


@guide.route('/prerogative')
def prerogative():
    return render_template("prerogative.html")

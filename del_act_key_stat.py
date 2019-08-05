#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import current_app
from app import db, create_app
import datetime
from app.api_1_0.models import AgentStatistics, ActKeyStatistics


def del_act_key_stat():
    app = create_app('default')
    app_context = app.app_context()
    app_context.push()

    ActKeyStatistics.query.filter_by(year=2018, month=12).delete()
    db.session.commit()
    AgentStatistics.query.filter_by(year=2018, month=12).delete()
    db.session.commit()

if __name__ == '__main__':
    del_act_key_stat()

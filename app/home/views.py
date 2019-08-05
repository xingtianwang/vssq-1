#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import current_app, request, jsonify
from flask import render_template

from app.api_1_0.models import Key, UserKeyRecord, KeyRecord, BusinessWare, ServiceProtocol, \
    BusinessWareOrder
from app.api_1_0.utils import get_business_type
from . import home
from app import db


@home.route('/')
@home.route('/index')
def index():
    return render_template("home/index.html")


@home.route('/about')
def about():
    return render_template('home/about.html')


@home.route('/newl')
def news_list():
    return render_template('home/newsList.html')


@home.route('/news1')
def news1():
    return render_template('home/news01.html')


@home.route('/news2')
def news2():
    return render_template('home/news02.html')


@home.route('/key')
def key():
    return render_template('home/key-id.html')


@home.route('/get_key_info')
def get_key_info():
    key_id = request.args.get('key_id')
    activate_time = ''
    k_status = ''
    if key_id == '':
        status = -1
        print(status)
    else:
        key = Key.query.filter_by(id=key_id).first()
        if key is not None:
            k_status = key.status
            status = 1
            if key.status == 1 or key.status == 3:
                user_key = UserKeyRecord.query.filter_by(key_id=key_id).first()
                if user_key is not None:
                    activate_time = user_key.activate_time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            status = 0
    return jsonify(code=1, status=status, activate_time=activate_time, k_id=key_id, k_status=k_status)


@home.route('/vc', methods=['GET'])
@home.route('/vc/<string:key_record_id>', methods=['GET'])
def invite(key_record_id='1'):
    res = []
    record_info = KeyRecord.query.filter_by(we_record_id=key_record_id).first()
    if record_info is not None:
        user = Key.query.filter_by(key_record_id=record_info.id).all()
        if user is not None:
            i = 1
            for item in user:
                res.append({'i': i, 'code': item.id})
                i += 1

    return render_template("home/agency.html", data=res)


@home.route('/buy_list', methods=['GET'])
@home.route('/buy_list/<string:uid>', methods=['GET'])
def buy_list(uid='1'):
    type_info = get_business_type()

    res = []
    record_infos = BusinessWare.query.filter_by(status=1).order_by(BusinessWare.priority.desc()).all()
    for record_info in record_infos:
        type_name = ''
        name = type_info.get(record_info.category, 'no')
        if name != 'no':
            type_name = name
        res.append({'id': record_info.id, 'name': record_info.name, 'price':record_info.price,
                    'priority': record_info.priority, 'imags': current_app.config['FILE_SERVER'] + record_info.picture,
                    'discount': record_info.discount, 'des': record_info.description, 'type_name': type_name,
                    'discount_price': int(record_info.price * record_info.discount)})

    return render_template("intelligent/buyList.html", data=res)


@home.route('/agree', methods=['GET'])
def agree():
    content = ''
    protocol = ServiceProtocol.query.filter_by(category=4).first()
    if protocol is not None:
        content = protocol.content
    return render_template("intelligent/agreement.html", content=content)


@home.route('/his/<string:uid>', methods=['GET'])
def his(uid='1'):
    infos = db.session.query(BusinessWareOrder.pay_time, BusinessWareOrder.order_number,
                             BusinessWareOrder.discount_price, BusinessWareOrder.status, BusinessWare.category).join(
        BusinessWare, BusinessWareOrder.ware_id == BusinessWare.id).filter(
        BusinessWareOrder.buyer_godin_id == uid, BusinessWareOrder.status == 1).order_by(
        BusinessWare.create_time.desc())
    print(infos)
    type_info = get_business_type()
    res = []
    for info in infos:
        type_name = ''
        name = type_info.get(info.category, 'no')
        if name != 'no':
            type_name = name
        else:
            continue
        res.append({'order': info.order_number, 'discount_price': info.discount_price, 'type_name': type_name,
                    'pay_time': info.pay_time.strftime('%Y-%m-%d')})
    return render_template("intelligent/history.html", data=res)


@home.route('/free_page/<string:uid>', methods=['GET'])
def free_page(uid='1'):
    return render_template("intelligent/guestMore.html", uid=uid)


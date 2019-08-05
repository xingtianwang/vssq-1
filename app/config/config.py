#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: config.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 16/9/21
# *************************************************************************
from collections import OrderedDict
from datetime import timedelta

from celery.schedules import crontab


class Config(object):

    # 后台登录账号密钥值
    SECRET_KEY = 'vssq1435qaz'
    # 如果设置成 True (默认情况)，Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。这需要额外的内存， 如果不必要的可以禁用它
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 通知邮件配置, 主要是异常log的邮件发送
    MAIL_SERVER = 'smtp.mxhichina.com'
    MAIL_PORT = 465
    MAIL_USERNAME = 'sys_report@godinsec.com'
    MAIL_PASSWORD = 'Godinsec@123!'
    MAIL_SENDER = 'Admin <sys_report@godinsec.com>'
    MAIL_USE_SSL = True

    # 数据翻页功能，每页的数量
    RECORDS_PER_PAGE = 10

    # Flask-WTF 也通过 RecaptchaField 提供了对 Recaptcha 的支持
    # 必须公钥
    RECAPTCHA_PUBLIC_KEY = '6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J'
    # 必须私钥
    RECAPTCHA_PRIVATE_KEY = '6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu'

    # 借助容联平台发送告警短信配置，此处已不用
    ACCOUNT_SID = '8a48b5514b0b8727014b2f6c18e92303'
    ACCOUNT_TOKEN = '35cd67202bc848f5a0d066f681924c72'
    APP_ID = 'aaf98f894b353559014b48e442560917'
    SMS_SERVER_ADDR = 'app.cloopen.com'
    SMS_SERVER_PORT = '8883'
    SOFT_VERSION = '2013-12-26'
    REG_TEMPLATE_ID = '62134'
    MODIFY_LOCK_TEMPLATE_ID = '90460'

    # flask cache use REDIS
    CACHE_TYPE = 'redis'
    # celery

    # celery 格式定义 
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']

    # 异常log存储目录
    EXCEPTION_TAG = 'WeData/WeException'
    # 邀请, 分享log存储目录
    INVITE_SHARE_TAG = 'Statistics/WeDownload'
    # 图片存储目录
    PHOTO_TAG = 'WeData/WePhoto'
    # 应用及插件存储目录
    APK_TAG = 'WeData/WeApk'
    # 大数据存储目录
    STATISTICS_TAG = 'Statistics'

    # 暂时无用
    EXTRACT_CODE = 'godinsec'

    # 数据库连接池的大小
    SQLALCHEMY_POOL_SIZE = 5
    # 控制在连接池达到最大值后可以创建的连接数。当这些额外的 连接回收到连接池后将会被断开和抛弃
    SQLALCHEMY_MAX_OVERFLOW = 20

    # Token有效时间
    TOKEN_EXPIRED_TIME = 3600 * 2

    # 应用及插件及特征文件等的类型定义，供上传应用使用，与app_list 中的app_type 对应
    APP_NAME_DICT = OrderedDict({5: 'wemi_hongbao', 6: 'p-plug', 7: 'launcher', 8: 'vs-business',
                                 9: 'ad-plug', 10: 'new-ad_plug', 99: 'WeChatFeature', 100: 'Permission',
                                 12: 'new-adver_plug', 13: 'sucaiku', 14: 'vbusiness'})

    APP_TYPE_DICT = OrderedDict({5: '微信红包', 6: '支付插件', 7: '桌面', 8: '微商神器',
                                 9: '破解版广告插件', 10: '广告插件', 99: '微信特征文件', 100: '隐私分身权限文件',
                                 12: '新广告插件', 13: '素材库', 14: '微商报告'})

    # 以下用不上
    CAMOUFLAGE_WARE_DICT = OrderedDict({0: 30, 1: 90, 2: 365})
    CAMOUFLAGE_WARE_NAME_DICT = OrderedDict({0: '月', 1: '季', 2: '年'})
    WEEK_ACTIVE_THRESHOLD = 5
    MONTH_ACTIVE_THRESHOLD = 20

    # celery 定时, 负载均衡时两台服务期时间可以使用不同，或者一台服务开启，另一台注释
    CELERYBEAT_SCHEDULE = {
        # 异常log定时
        # 'check_exception_log': {
        #     'task': 'check_exception_log',
        #     'schedule': timedelta(minutes=7)
        # },
        # 计算用户留存数据
        'make_next_day_stay_report': {
            'task': 'make_next_day_stay_report',
            'schedule': crontab(minute=0, hour=2)
        },
        # 开屏广告模拟数据计算
        'make_open_screen_simulate_data': {
            'task': 'make_open_screen_simulate_data',
            'schedule': crontab(minute=55, hour=23)
        },
        # 以下3条vip会员统计和智能加粉会员统计
        'make_vip_last_day_data': {
            'task': 'make_vip_last_day_data',
            'schedule': crontab(minute=6, hour=2)
        },
        'make_vip_last_week_data': {
            'task': 'make_vip_last_week_data',
            'schedule': crontab(minute=11, hour=2, day_of_week=1)
        },
        'make_vip_last_month_data': {
            'task': 'make_vip_last_month_data',
            'schedule': crontab(minute=17, hour=2, day_of_month=1)
        },
        # 授权码状态更新
        'make_key_status': {
            'task': 'make_key_status',
            'schedule': crontab(minute=25, hour=2)
        },
        # 激活码的统计
        'make_act_key_statistics': {
            'task': 'make_act_key_statistics',
            'schedule': crontab(minute=10, hour=2)
        },
        # 特征文件上一天的的访问记录存储
        'make_feature_data': {
            'task': 'make_feature_data',
            'schedule': crontab(minute=15, hour=2)
        },
        # 特征文件五分钟内的的访问记录存储
        'make_feature_data_five': {
            'task': 'make_feature_data_five',
            'schedule': timedelta(minutes=5)
        },
        # 将会员已过期的VIP用户status状态修改为无效
        'make_vip_status': {
            'task': 'make_vip_status',
            'schedule': crontab(minute=35, hour=1)
        },
        # 授权码批次每日分成数据统计
        #  !!!!一定要早於渠道賬戶每日分成成数据统计
        'make_key_record_radio_day_data': {
            'task': 'make_key_record_radio_day_data',
            'schedule': crontab(minute=30, hour=1)
        },
        # 渠道账户每日分成数据统计
        'make_channel_account_radio_day_data': {
            'task': 'make_channel_account_radio_day_data',
            'schedule': crontab(minute=40, hour=1)
        },
        # 栏目每种商品每日分成数据统计
        'make_vip_type_radio_day_data': {
            'task': 'make_vip_type_radio_day_data',
            'schedule': crontab(minute=48, hour=1)
        },
        # 更新mysql数据库的广告触发次数
        'make_ads_count': {
            'task': 'make_ads_count',
            'schedule': timedelta(minutes=15)
        },
        # 删除数据库表中的过期数据
        'make_data_update': {
            'task': 'make_data_update',
            'schedule': crontab(minute=35, hour=3)
        },
        # 更新mysql数据库的广告触发次数
        'make_banner_ads_count': {
            'task': 'make_banner_ads_count',
            'schedule': timedelta(minutes=5)
        },
        # 更新mysql数据库的广告触发次数
        'make_open_screen_ads_count': {
            'task': 'make_open_screen_ads_count',
            'schedule': timedelta(minutes=5)
        },
        # 更新mysql数据库的广告触发次数
        'make_open_ads_count': {
            'task': 'make_open_ads_count',
            'schedule': timedelta(minutes=5)
        },
        # 更新mysql数据库的虚拟点击广告次数
        'make_screen_simulate_ads_count': {
            'task': 'make_screen_simulate_ads_count',
            'schedule': crontab(minute=40, hour=2)
        },
        # 邀请,分享日志文件两小时内的打印记录存储
        'make_log_print': {
            'task': 'make_log_print',
            'schedule': timedelta(hours=2)
        },

        # 邀请,分享日志文件内前一天的打印记录存储
        'make_log_print_yes': {
            'task': 'make_log_print_yes',
            'schedule': crontab(minute=1, hour=0)
        },
        # 更新今日小红点状态
        'update_hot_dot': {
            'task': 'update_hot_dot',
            'schedule': crontab(minute=5, hour=0)
        },
        # 删除超过72小时的语音盒子
        'delete_expire_video': {
            'task': 'delete_expire_video',
            'schedule': crontab(minute=5, hour=1)
        },

    }
    # 定时时区 
    CELERY_TIMEZONE = 'Asia/Shanghai'
    # log的级别 0 debug 1 info 2 warn 3 error
    LOG_FLAG = 0
    CELERY_IGNORE_RESULT = True
    #CELERYD_MAX_TASKS_PER_CHILD = 100
    #CELERYD_PREFETCH_MULTIPLIER = 2

    CELERYD_CONCURRENCY = 2

    # 后台上传广告下拉菜单配置，值会存储到数据库
    ADS_SOURCE = OrderedDict({0: '自有广告', 1: '外接SDK'})
    OPEN_SCREEN_ADS_POSITION = OrderedDict({0: '开屏首页', 1: '应用启动页', 2: '应用更新'})

    BANNER_ADS_POSITION = OrderedDict({0: '优化加速', 1: '主桌面', 2: '倒三角页面'})
    GAME_PARK_TYPE = OrderedDict({0: '全部', 1: '竞技', 2: '角色', 3: '休闲', 4: '棋牌'})

    INTERACTIVE_ADS_POSITION = OrderedDict({0: '主界面-图标', 1: '主界面-浮标'})
    INTERACTIVE_ADS_SOURCE = OrderedDict({0: '互动广告'})
    EXTERNAL_ADS_CATEGORY = OrderedDict({'0': 'banner', '1': '应用开屏广告', '2': '第三方应用广告', '3': '桌面广告',
                                        '4': '友盟推送'})
    ADS_ICON = OrderedDict({1: '第三方应用开屏'})
    UPLOAD_VIDEO_PATH = "WeData/WePhoto/WeVideo/"
    IMAGE_PATH = "WeData/WePhoto/"


    def __repr__(self):
        return '<Config>'


class ProductionConfig(Config):
    DEBUG = False
    # 连接数据库
    SQLALCHEMY_DATABASE_URI = 'mysql://godin_root:Godinsec2016@rm-2ze0lg4xvs6ki7qi0.mysql.rds.aliyuncs.com/vssq'
    # 老版本从测试环境同步大数据，已不用
    SQLALCHEMY_BINDS = {'transfer': 'mysql://root:sa@112.126.81.177/vssq_analyze'}
    # 绑定地址
    SERVER_ADDRESS = '0.0.0.0'
    # 绑定端口
    SERVER_PORT = 9103
    # flask cache redis 配置
    # 主机
    CACHE_REDIS_HOST = '192.168.1.4'
    # 端口
    CACHE_REDIS_PORT = '6379'
    # 密码
    CACHE_REDIS_PASSWORD = 'godinsec'
    # 所使用数据库
    CACHE_REDIS_DB = 12
    # celery 定时使用
    CELERY_BROKER_URL = 'redis://:godinsec@192.168.1.5:6379/12'
    CELERY_RESULT_BACKEND = 'redis://:godinsec@192.168.1.5:6379/12'
    # 直接连接redis存储业务数据
    REDIS_URL = "redis://:godinsec@192.168.1.4:6379/12"
    # 负载均衡访问余名地址，和数据库中文件路径拼接，给客户端调用
    FILE_SERVER = 'http://wemiyao.com/'
    # 二维码
    QR_CODE_IMAGE = 'qr_code_product.png'
    MAIL_SUBJECT_PREFIX = '微商神器生产环境'
    # 所在服务器的不同，值不同，部署查看内网ip,使用对应值, 负载均衡两台服务，一台A 一台B
    SERVER = 'A'  # 192.168.1.4 is A  192.168.1.5 is B
    # SERVER = 'B'

    # 主程序微信账号，微信id,商户号，商户密钥，支付成功回调函数
    WX_APP_ID = 'wx6ffbc23eed45caae'
    WX_MCH_ID = '1509589831'
    WX_MCH_KEY = 'E613D5097CB428B52D1E748A54E3469C'
    WX_NOTIFY_URL = 'https://wemiyao.com/vssq/wxpay/ResultAsynNotice'

    # 分身插件微信支付账号, 微信id,商户号，商户密钥，支付成功回调函数
    AVATAR_WX_APP_ID = 'wx45e5c33e04895ca7'
    AVATAR_WX_MCH_ID = '1495060552'
    AVATAR_WX_MCH_KEY = 'E613D5097CB428B52D1E748A54E3469C'
    AVATAR_WX_NOTIFY_URL = 'https://wemiyao.com/vssq/wxpay/r_notice'

    # 微信支付所使用ip, 部署时根据内网ip设置对应值
    WX_SPBILL_CREATE_IP = '47.93.203.160'  # xavatar-b 192.168.1.4
    # WX_SPBILL_CREATE_IP = '47.93.198.122'   # xavatar-1 192.168.1.5

    INVITE_LINK = "https://wemiyao.com/vssq/share/invite_url/"

    def __repr__(self):
        return '<ProductionConfig>'


class TestConfig(Config):
    DEBUG = True
    SECRET_KEY = 'test1435qaz'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:sa@127.0.0.1/vssq'
    SQLALCHEMY_BINDS = {'transfer': 'mysql://root:sa@112.126.81.177/vssq_analyze_test'}
    SERVER_ADDRESS = '0.0.0.0'
    SERVER_PORT = 9103
    CACHE_REDIS_HOST = '127.0.0.1'
    CACHE_REDIS_PORT = '6379'
    CACHE_REDIS_PASSWORD = 'godinsec'
    CACHE_REDIS_DB = 14
    CELERY_BROKER_URL = 'redis://:godinsec@127.0.0.1:6379/14'
    CELERY_RESULT_BACKEND = 'redis://:godinsec@127.0.0.1:6379/14'
    REDIS_URL = "redis://:godinsec@127.0.0.1:6379/14"
    FILE_SERVER = 'http://godinsec.cn/'
    QR_CODE_IMAGE = 'qr_code_test.png'
    MAIL_SUBJECT_PREFIX = '微商神器外网测试环境'
    SERVER = 'A'  # 192.168.1.4 is A  192.168.1.5 is B
    # SERVER = 'B'

    WX_APP_ID = 'wx6ffbc23eed45caae'
    WX_MCH_ID = '1509589831'
    WX_MCH_KEY = 'E613D5097CB428B52D1E748A54E3469C'
    WX_NOTIFY_URL = 'https://godinsec.cn/vssq/wxpay/ResultAsynNotice'
    # 新增支付账号
    AVATAR_WX_APP_ID = 'wxa8ae1f1045adf15d'
    AVATAR_WX_MCH_ID = '1481972562'
    AVATAR_WX_MCH_KEY = 'E613D5097CB428B52D1E748A54E3469C'
    AVATAR_WX_NOTIFY_URL = 'https://godinsec.cn/vssq/wxpay/r_notice'

    WX_SPBILL_CREATE_IP = '112.126.81.177'

    INVITE_LINK = "http://godinsec.cn/vssq/share/invite_url/"

    def __repr__(self):
        return '<TestConfig>'


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'develop1435qaz'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root@127.0.0.1/vssq'
    SQLALCHEMY_BINDS = {'transfer': 'mysql://root:sa@127.0.0.1/vssq_analyze_test'}
    SERVER_ADDRESS = '0.0.0.0'
    SERVER_PORT = 9103
    CACHE_REDIS_HOST = '127.0.0.1'
    CACHE_REDIS_PORT = '6379'
    CACHE_REDIS_PASSWORD = ''
    CACHE_REDIS_DB = 14
    CELERY_BROKER_URL = 'redis://127.0.0.1:6379/14'
    CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/14'
    REDIS_URL = "redis://:@127.0.0.1:6379/14"
    FILE_SERVER = 'http://127.0.0.1/'
    QR_CODE_IMAGE = 'qr_code_develop.png'
    MAIL_SUBJECT_PREFIX = '微商神器开发环境'
    SERVER = 'A'  # 192.168.1.4 is A  192.168.1.5 is B
    # SERVER = 'B'

    WX_APP_ID = 'wx6ffbc23eed45caae'
    WX_MCH_ID = '1509589831'
    WX_MCH_KEY = 'E613D5097CB428B52D1E748A54E3469C'
    WX_NOTIFY_URL = 'https://godinsec.cn/vssq/wxpay/ResultAsynNotice'
    # 新增支付账号
    AVATAR_WX_APP_ID = 'wxa8ae1f1045adf15d'
    AVATAR_WX_MCH_ID = '1481972562'
    AVATAR_WX_MCH_KEY = 'E613D5097CB428B52D1E748A54E3469C'
    AVATAR_WX_NOTIFY_URL = 'https://godinsec.cn/vssq/wxpay/r_notice'

    WX_SPBILL_CREATE_IP = '112.126.81.177'
	
    INVITE_LINK = "http://godinsec.cn/vssq/share/invite_url/"

    def __repr__(self):
        return '<DevelopmentConfig>'


config = {'development': DevelopmentConfig,
          'test': TestConfig,
          'production': ProductionConfig,

          'default': DevelopmentConfig}

#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: urls.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 2016/11/17
# *************************************************************************
from flask import Blueprint
from flask_restful import Api

from .views import GetAuthSmsApi, RegisterApi, UploadMobileInfoApi, FeedBackApi, SetUserInfoApi, UploadExceptionLogApi, \
    HealthCheckApi, GetAuthTokenApi, GetBanneradsStatisticsApi, GetOpenScreenAdsStatisticsApi, UploadStatisticsApi, \
    GetUserVipStatusApi, GetUserVipOrderApi, BuyVipWareApi, GetVipOrdersStatusApi, GetCommunicationGroupApi, \
    OpenScreenAdsDataApi, GetInteractiveAdsApi, InteractiveAdsStatisticsApi, GetLinkApi, SpecificadsStatisticsApi, \
    GetBanneradsApi, GetOpenAdsApi, VipServiceProtocolApi, ActivateVipMemberApi, GetAdsIconApi, GetChannelVipWareApi, \
    GetWeChatFeatureApi, FeatureApi, CheckKeyApi, JudgeAddKeyApi, BuykeyApi, ChannelFrameUpdateApi, \
    ChannelPluginUpdateApi, GetAvatarChannelAppUrlApi, CheckChannelAppUpdateApi, GetCommGroupApi, GetKeyChannelApi, \
    GetActivityApi, ActivityFuncApi, GetKeyInfoApi, MakeKeyApi, GetNoticeApi, ReadNoticeApi, ServiceProtocolApi, \
    CrackMakeKeyApi, NewBuyVipWareApi, CheckKeyArrApi, JudgeAddKeyArrApi, CheckAppVersionApi, VerifyApi, \
    GetBusinessVipStatusApi, BusinessBuyVipWareApi, GetFriendApi, GetOpenAdsInfoApi, GetOpenAdsStatisticsApi, \
    NewGetNoticeApi, FreeBusinessVipMemberApi, BusAssistantApi, BusLinkApi, VSZLSearchApi, VSZLAddApi, \
    FreeExperienceApi, ExperienceStatusApi, GetTriangleApi, GetFunctionVideoApi

api_v_1_0 = Blueprint('api', __name__)
api = Api(api_v_1_0)
api.add_resource(GetAuthSmsApi, '/GetAuthSms', endpoint='GetAuthSms')
api.add_resource(RegisterApi, '/Register', endpoint='Register')
api.add_resource(UploadMobileInfoApi, '/UploadMobileInfo', endpoint='UploadMobileInfo')
api.add_resource(FeedBackApi, '/FeedBack', endpoint='FeedBack')
api.add_resource(SetUserInfoApi, '/SetUserInfo', endpoint='SetUserInfo')
api.add_resource(UploadExceptionLogApi, '/UploadExceptionLog', endpoint='UploadExceptionLog')
api.add_resource(HealthCheckApi, '/HealthCheck', endpoint='HealthCheckApi')
api.add_resource(GetAuthTokenApi, '/GetAuthToken', endpoint='GetAuthToken')
api.add_resource(GetBanneradsStatisticsApi, '/GetBanneradsStatistics', endpoint='GetBanneradsStatistics')
api.add_resource(GetOpenScreenAdsStatisticsApi, '/GetOpenScreenAdsStatistics', endpoint='GetOpenScreenAdsStatistics')
api.add_resource(UploadStatisticsApi, '/UploadStatistics', endpoint='UploadStatistics')
api.add_resource(GetUserVipStatusApi, '/GetUserVipStatus', endpoint='GetUserVipStatus')
api.add_resource(GetChannelVipWareApi, '/GetChannelVipWare', endpoint='GetChannelVipWare')
api.add_resource(GetUserVipOrderApi, '/GetUserVipOrder', endpoint='GetUserVipOrder')
api.add_resource(BuyVipWareApi, '/BuyVipWare', endpoint='BuyVipWare')
api.add_resource(GetVipOrdersStatusApi, '/GetVipOrdersStatus', endpoint='GetVipOrdersStatus')
api.add_resource(ActivateVipMemberApi, '/ActivateVipMember', endpoint='ActivateVipMember')
api.add_resource(GetCommunicationGroupApi, '/GetGroup', endpoint='GetGroup')
api.add_resource(OpenScreenAdsDataApi, '/OpenScreenAdsData', endpoint='OpenScreenAdsData')
api.add_resource(GetInteractiveAdsApi, '/GetInteractiveAds', endpoint='GetInteractiveAds')
api.add_resource(InteractiveAdsStatisticsApi, '/InteractiveAds', endpoint='InteractiveAds')
api.add_resource(GetLinkApi, '/GetLink', endpoint='GetLink')
api.add_resource(SpecificadsStatisticsApi, '/Specificads', endpoint='Specificads')
api.add_resource(GetBanneradsApi, '/GetBannerads', endpoint='GetBannerads')
api.add_resource(GetOpenAdsApi, '/GetOpenads', endpoint='GetOpenads')
api.add_resource(VipServiceProtocolApi, '/VipServiceProtocol', endpoint='VipServiceProtocol')
api.add_resource(GetAdsIconApi, '/GetAdsIcon', endpoint='GetAdsIcon')
api.add_resource(GetWeChatFeatureApi, '/GetWeChatFeature', endpoint='GetWeChatFeature')
api.add_resource(FeatureApi, '/Feature', endpoint='Feature')
api.add_resource(CheckKeyApi, '/CheckKey', endpoint='CheckKey')
api.add_resource(JudgeAddKeyApi, '/JudgeAddKey', endpoint='JudgeAddKey')
api.add_resource(BuykeyApi, '/Buykey', endpoint='Buykey')
api.add_resource(ChannelFrameUpdateApi, '/ChannelFrameUpdate', endpoint='ChannelFrameUpdate')
api.add_resource(ChannelPluginUpdateApi, '/ChannelPluginUpdate', endpoint='ChannelPluginUpdate')
api.add_resource(GetAvatarChannelAppUrlApi, '/AvatarChannelAppUrl', endpoint='AvatarChannelAppUrl')
api.add_resource(CheckChannelAppUpdateApi, '/ChannelAppUpdate', endpoint='ChannelAppUpdate')
api.add_resource(GetCommGroupApi, '/GetCommGroup', endpoint='GetCommGroup')
api.add_resource(GetKeyChannelApi, '/GetCh', endpoint='GetCh')
api.add_resource(GetActivityApi, '/GetActivity', endpoint='GetActivity')
api.add_resource(ActivityFuncApi, '/ac_func', endpoint='ac_func')
api.add_resource(GetKeyInfoApi, '/we_key', endpoint='we_key')
api.add_resource(MakeKeyApi, '/m_key', endpoint='m_key')
api.add_resource(GetNoticeApi, '/notice', endpoint='notice')
api.add_resource(ReadNoticeApi, '/read_notice', endpoint='read_notice')
api.add_resource(ServiceProtocolApi, '/ser_pro', endpoint='ser_pro')
api.add_resource(CrackMakeKeyApi, '/cm_key', endpoint='cm_key')
api.add_resource(NewBuyVipWareApi, '/ava_b_vip', endpoint='ava_b_vip')
api.add_resource(CheckKeyArrApi, '/check_k', endpoint='check_k')
api.add_resource(JudgeAddKeyArrApi, '/judge_k', endpoint='judge_k')
api.add_resource(CheckAppVersionApi, '/check_app', endpoint='check_app')
api.add_resource(VerifyApi, '/verify', endpoint='verify')
api.add_resource(GetBusinessVipStatusApi, '/status', endpoint='status')
api.add_resource(BusinessBuyVipWareApi, '/buy', endpoint='buy')
api.add_resource(GetFriendApi, '/ids', endpoint='ids')
api.add_resource(GetOpenAdsInfoApi, '/open_screen', endpoint='open_screen')
api.add_resource(GetOpenAdsStatisticsApi, '/open_statistics', endpoint='open_statistics')
api.add_resource(NewGetNoticeApi, '/n_notice', endpoint='n_notice')
api.add_resource(FreeBusinessVipMemberApi, '/f_vip', endpoint='f_vip')
api.add_resource(BusAssistantApi, '/b_assistant', endpoint='b_assistant')
api.add_resource(BusLinkApi, '/b_link', endpoint='b_link')
api.add_resource(VSZLSearchApi, '/vszl_search', endpoint='vszl_search')
api.add_resource(VSZLAddApi, '/vszl_add', endpoint='vszl_add')
api.add_resource(FreeExperienceApi, '/free_experience', endpoint='free_experience')
api.add_resource(ExperienceStatusApi, '/experience_status', endpoint='experience_status')
# 倒三角接口
api.add_resource(GetTriangleApi, '/get_triangle', endpoint='get_triangle')
# 功能视频获取接口
api.add_resource(GetFunctionVideoApi, '/function_video', endpoint='function_video')

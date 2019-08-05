#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2016 Godinsec. All rights reserved.
#   File Name: urls.py
#   Author: Allan
#   Mail: allan.yan@godinsec.com
#   Created Time: 16/9/23
# *************************************************************************
from .views import list_admin_user, add_admin_user, del_admin_user, set_admin_user_status, audit_user, \
    del_app_version, get_feedback, get_exception, get_reg_user_info, get_un_reg_user_info, \
    get_black_list_info, add_black_list, del_black_list, export_result, \
    get_white_imei_list_info, add_white_imei_list, del_white_imei_list, release_app, list_duty_manager, \
    add_duty_manager, del_duty_manager, set_duty_manager_status, del_feedback, get_next_day_stay_statistics, \
    list_spread_manager, add_spread_manager, del_spread_manager, set_hide_icon_status, \
    get_activity_info, activity_status, add_activity, edit_activity, add_open_screen_ads, get_open_screen_ads, \
    set_open_screen_status, open_screen_ads_info, edit_open_screen_ads, add_bannerad, get_bannerads_info, \
    get_bannerads_details, edit_bannerad_status, edit_bannerad, get_app_list_info, add_ware, edit_ware, get_ware_info, \
    set_priority, set_ware_status, get_ware_statistics, get_vip_members, get_vip_members_details, vip_pay_statistics, \
    get_vip_week_range, index, communicate_group, open_screen_ads_data, interactive_ads, edit_interactive_ads, \
    set_interactive_status, get_interactive_ads, interactive_ads_info, get_vip_ware_details, get_member_info, \
    add_vip_members, add_vip_service_protocol, vip_wares_info, add_all_vip_members, vip_wares_all_info, \
    get_vip_category, get_vip_channel, add_vip_channel, add_vip_category, ads_config, export_channel, get_open_config, \
    get_interactive_config, get_ads_icon, ads_icon, edit_ads_icon, edit_open_strategy, avatar_app_info, add_avatar_app, \
    set_decompile_status, make_avatar_app, avatar_app_detail, release_avatar_app, get_banner_config, \
    set_ads_icon_status, get_activity_share, get_invite, get_share, add_key, get_key_record, edit_key, key_detail, \
    order_key, channel_upload_app, get_channel_version_info, release_channel_app, del_channel_version, get_key_channel, \
    edit_key_channel, add_key_channel, get_key_info, add_key_imei, delete_avatar, \
    sign_activity_detail, sign_activity_record, we_key_detail, we_get_key_record, get_notice_info, add_notice, \
    set_notice_status, notice_detail, export_key, add_app_protocol, key_info, set_key_status, get_imei_info, \
    add_imei_vip, get_act_key_statistics, agent_statistics, add_agent, get_agent, del_agent, get_app_version_check, \
    add_version_check, del_app_check, edit_version_check, add_phone_member, get_act_members, check_key, \
    get_business_category, add_business_category, add_business_protocol, get_bus_info, set_bus_priority, \
    set_bus_status, add_bus_ware, edit_bus_ware, get_bus_details, get_bus_statistics, get_bus_members, \
    get_bus_members_details, bus_pay_statistics, add_friends, del_friends, free_vip_days, bus_give_stat, \
    bus_recommend, del_bus_recommend, second_add, business_assistant, add_link, delete_assistant, get_assistant_detail, \
    add_assistant, set_gzh, free_experience_days, add_account, get_account_info, edit_channel_account, get_channel_data, \
    channel_data_detail, \
    day_key_record_detail, day_vip_detail, expire_key, get_function_video, add_function_video, del_function_video, \
    edit_function_video, set_function, get_gold_ware_info, add_gold_ware, get_vip_gold_ware_details, edit_gold_ware, \
    generalize_data, invite_code_data, active_intro, fc_info, money_check, micro_store_url, get_invite_detail, \
    member_divide, get_invite_detail_detail, add_fc_content, edit_cf_content, del_cf, every_wash, add_privacy_protocol, \
    invite_code_divide, alter_balance, alter_detail, delete_detail, function_hot_dot, master_get_function_video, \
    master_add_function_video, master_del_function_video, master_edit_function_video, alter_divide, alter_divide_detail, \
    get_pay_time, get_vip_pay_time, appeal_edit, appeal_detail

from flask import Blueprint

manage = Blueprint('manage', __name__, static_folder='static', template_folder='templates')

manage.add_url_rule('/list_admin_user', view_func=list_admin_user)
manage.add_url_rule('/add_admin_user', view_func=add_admin_user, methods=['GET', 'POST'])
manage.add_url_rule('/del_admin_user', view_func=del_admin_user)
manage.add_url_rule('/set_admin_user_status', view_func=set_admin_user_status)
manage.add_url_rule('/audit_user', view_func=audit_user, methods=['GET', 'POST'])
manage.add_url_rule('/del_app_version', view_func=del_app_version)
manage.add_url_rule('/feedback', view_func=get_feedback, methods=['GET', 'POST'])
manage.add_url_rule('/exception', view_func=get_exception, methods=['GET', 'POST'])
manage.add_url_rule('/reg_info', view_func=get_reg_user_info, methods=['GET', 'POST'])
manage.add_url_rule('/un_reg_info', view_func=get_un_reg_user_info, methods=['GET', 'POST'])
manage.add_url_rule('/black_list', view_func=get_black_list_info, methods=['GET', 'POST'])
manage.add_url_rule('/add_black_list', view_func=add_black_list, methods=['GET', 'POST'])
manage.add_url_rule('/del_black_list', view_func=del_black_list)
manage.add_url_rule('/export', view_func=export_result)
manage.add_url_rule('/white_imei_list', view_func=get_white_imei_list_info, methods=['GET', 'POST'])
manage.add_url_rule('/add_white_imei_list', view_func=add_white_imei_list, methods=['GET', 'POST'])
manage.add_url_rule('/del_white_imei_list', view_func=del_white_imei_list)
manage.add_url_rule('/release', view_func=release_app)
manage.add_url_rule('/list_dm', view_func=list_duty_manager)
manage.add_url_rule('/add_dm', view_func=add_duty_manager, methods=['GET', 'POST'])
manage.add_url_rule('/del_dm', view_func=del_duty_manager)
manage.add_url_rule('/set_dm_status', view_func=set_duty_manager_status)
manage.add_url_rule('/list_sm', view_func=list_spread_manager)
manage.add_url_rule('/add_sm', view_func=add_spread_manager, methods=['GET', 'POST'])
manage.add_url_rule('/del_sm', view_func=del_spread_manager)
manage.add_url_rule('/del_feedback', view_func=del_feedback)
manage.add_url_rule('/next_day_stay_statistics', view_func=get_next_day_stay_statistics, methods=['GET', 'POST'])
manage.add_url_rule('/set_hide_icon_status', view_func=set_hide_icon_status, methods=['GET', 'POST'])
manage.add_url_rule('/activity_info', view_func=get_activity_info, methods=['GET', 'POST'])
manage.add_url_rule('/activity_status', view_func=activity_status, methods=['GET', 'POST'])
manage.add_url_rule('/add_activity', view_func=add_activity, methods=['GET', 'POST'])
manage.add_url_rule('/edit_activity/<int:activity_id>', view_func=edit_activity, methods=['GET', 'POST'])
manage.add_url_rule('/add_open_screen_ads', view_func=add_open_screen_ads, methods=['get', 'POST'])
manage.add_url_rule('/open_screen_ads', view_func=get_open_screen_ads, methods=['get', 'POST'])
manage.add_url_rule('/set_open_screen_status', view_func=set_open_screen_status, methods=['get', 'POST'])
manage.add_url_rule('/open_screen_ads_info<int:ad_id>', view_func=open_screen_ads_info, methods=['GET', 'POST'])
manage.add_url_rule('/edit_open_screen_ads<int:ad_id>', view_func=edit_open_screen_ads, methods=['GET', 'POST'])
manage.add_url_rule('/add_bannerad', view_func=add_bannerad, methods=['GET', 'POST'])
manage.add_url_rule('/bannerads_info', view_func=get_bannerads_info, methods=['GET', 'POST'])
manage.add_url_rule('/bannerads_details/<int:ad_id>', view_func=get_bannerads_details, methods=['GET', 'POST'])
manage.add_url_rule('/edit_bannerad_status', view_func=edit_bannerad_status, methods=['GET', 'POST'])
manage.add_url_rule('/edit_bannerad/<int:ad_id>', view_func=edit_bannerad, methods=['GET', 'POST'])
manage.add_url_rule('/app_list_info', view_func=get_app_list_info, methods=['GET', 'POST'])
manage.add_url_rule('/add_ware', view_func=add_ware, methods=['GET', 'POST'])
manage.add_url_rule('/ware_info', view_func=get_ware_info, methods=['GET', 'POST'])
manage.add_url_rule('/set_ware_status', view_func=set_ware_status, methods=['GET', 'POST'])
manage.add_url_rule('/vip_ware_details/<ware_id>', view_func=get_vip_ware_details, methods=['GET', 'POST'])
manage.add_url_rule('/set_priority', view_func=set_priority, methods=['GET', 'POST'])
manage.add_url_rule('/edit_ware/<string:ware_id>', view_func=edit_ware, methods=['GET', 'POST'])
manage.add_url_rule('/ware_statistics', view_func=get_ware_statistics, methods=['GET', 'POST'])
manage.add_url_rule('/vip_members', view_func=get_vip_members, methods=['GET', 'POST'])
manage.add_url_rule('/vip_members_details/<godin_id>', view_func=get_vip_members_details, methods=['GET', 'POST'])
manage.add_url_rule('/vip_pay_statistics', view_func=vip_pay_statistics, methods=['GET', 'POST'])
manage.add_url_rule('/member_info', view_func=get_member_info, methods=['GET', 'POST'])
manage.add_url_rule('/vip_wares_info', view_func=vip_wares_info, methods=['GET', 'POST'])
manage.add_url_rule('/vip_category', view_func=get_vip_category, methods=['GET', 'POST'])
manage.add_url_rule('/vip_channel', view_func=get_vip_channel, methods=['GET', 'POST'])
manage.add_url_rule('/add_vip_category', view_func=add_vip_category, methods=['GET', 'POST'])
manage.add_url_rule('/add_vip_channel', view_func=add_vip_channel, methods=['GET', 'POST'])
manage.add_url_rule('/vip_wares_all_info', view_func=vip_wares_all_info, methods=['GET', 'POST'])
manage.add_url_rule('/add_vip_members', view_func=add_vip_members, methods=['GET', 'POST'])
manage.add_url_rule('/add_all_vip_members', view_func=add_all_vip_members, methods=['GET', 'POST'])
manage.add_url_rule('/vip_week_range', view_func=get_vip_week_range, methods=['GET', 'POST'])
manage.add_url_rule('/index', view_func=index, methods=['GET'])
manage.add_url_rule('/communicate_group', view_func=communicate_group, methods=['GET', 'POST'])
manage.add_url_rule('/open_screen_ads_data', view_func=open_screen_ads_data, methods=['GET', 'POST'])
manage.add_url_rule('/interactive_ads', view_func=interactive_ads, methods=['get', 'POST'])
manage.add_url_rule('/get_interactive_ads', view_func=get_interactive_ads, methods=['get', 'POST'])
manage.add_url_rule('/set_interactive_status', view_func=set_interactive_status, methods=['get', 'POST'])
manage.add_url_rule('/interactive_ads_info<int:ad_id>', view_func=interactive_ads_info, methods=['GET', 'POST'])
manage.add_url_rule('/edit_interactive_ads<int:ad_id>', view_func=edit_interactive_ads, methods=['GET', 'POST'])
manage.add_url_rule('/add_vip_service_protocol', view_func=add_vip_service_protocol, methods=['GET', 'POST'])
manage.add_url_rule('/get_banner_config<int:ad_id>', view_func=get_banner_config, methods=['GET', 'POST'])
manage.add_url_rule('/banner_config', view_func=ads_config, methods=['GET', 'POST'])
manage.add_url_rule('/export_channel', view_func=export_channel, methods=['GET', 'POST'])
manage.add_url_rule('/get_open_config<int:ad_id>', view_func=get_open_config, methods=['GET', 'POST'])
manage.add_url_rule('/get_interactive_config<int:ad_id>', view_func=get_interactive_config, methods=['GET', 'POST'])
manage.add_url_rule('/edit_ads_icon/<int:icon_id>', view_func=edit_ads_icon, methods=['GET', 'POST'])
manage.add_url_rule('/ads_icon', view_func=ads_icon, methods=['GET', 'POST'])
manage.add_url_rule('/get_ads_icon', view_func=get_ads_icon, methods=['GET', 'POST'])
manage.add_url_rule('/edit_open_strategy', view_func=edit_open_strategy, methods=['GET', 'POST'])
manage.add_url_rule('/avatar_app_info', view_func=avatar_app_info, methods=['GET', 'POST'])
manage.add_url_rule('/add_avatar_app', view_func=add_avatar_app, methods=['GET', 'POST'])
manage.add_url_rule('/set_decompile_status', view_func=set_decompile_status, methods=['GET', 'POST'])
manage.add_url_rule('/make_avatar_app', view_func=make_avatar_app, methods=['GET', 'POST'])
manage.add_url_rule('/avatar_app_detail', view_func=avatar_app_detail, methods=['GET', 'POST'])
manage.add_url_rule('/release_avatar_app', view_func=release_avatar_app, methods=['GET', 'POST'])
manage.add_url_rule('/set_ads_icon_status', view_func=set_ads_icon_status, methods=['GET', 'POST'])
manage.add_url_rule('/get_activity_share', view_func=get_activity_share, methods=['GET', 'POST'])
manage.add_url_rule('/get_invite', view_func=get_invite, methods=['GET', 'POST'])
manage.add_url_rule('/get_share', view_func=get_share, methods=['GET', 'POST'])
manage.add_url_rule('/add_key', view_func=add_key, methods=['GET', 'POST'])
manage.add_url_rule('/edit_key', view_func=edit_key, methods=['GET', 'POST'])
manage.add_url_rule('/get_key_record', view_func=get_key_record, methods=['GET', 'POST'])
manage.add_url_rule('/key_detail', view_func=key_detail, methods=['GET', 'POST'])
manage.add_url_rule('/order_key', view_func=order_key, methods=['GET', 'POST'])
manage.add_url_rule('/channel_upload_app', view_func=channel_upload_app, methods=['GET', 'POST'])
manage.add_url_rule('/get_channel_version_info', view_func=get_channel_version_info, methods=['GET', 'POST'])
manage.add_url_rule('/release_channel_app', view_func=release_channel_app, methods=['GET', 'POST'])
manage.add_url_rule('/del_channel_version', view_func=del_channel_version, methods=['GET', 'POST'])
manage.add_url_rule('/get_key_channel', view_func=get_key_channel, methods=['GET', 'POST'])
manage.add_url_rule('/add_key_channel', view_func=add_key_channel, methods=['GET', 'POST'])
manage.add_url_rule('/edit_key_channel/<string:ch>', view_func=edit_key_channel, methods=['GET', 'POST'])
manage.add_url_rule('/get_key_info', view_func=get_key_info, methods=['GET', 'POST'])
manage.add_url_rule('/add_key_imei', view_func=add_key_imei, methods=['GET', 'POST'])
manage.add_url_rule('/delete_avatar', view_func=delete_avatar, methods=['GET', 'POST'])
manage.add_url_rule('/sign_activity_detail/<int:activity_id>', view_func=sign_activity_detail,
                    methods=['GET', 'POST'])
manage.add_url_rule('/sign_activity_record/<int:activity_id>/<string:sign_godin_id>', view_func=sign_activity_record,
                    methods=['GET', 'POST'])
manage.add_url_rule('/we_get_key_record', view_func=we_get_key_record, methods=['GET', 'POST'])
manage.add_url_rule('/we_key_detail', view_func=we_key_detail, methods=['GET', 'POST'])
manage.add_url_rule('/get_notice_info', view_func=get_notice_info, methods=['GET', 'POST'])
manage.add_url_rule('/add_notice', view_func=add_notice, methods=['GET', 'POST'])
manage.add_url_rule('/set_notice_status', view_func=set_notice_status, methods=['GET', 'POST'])
manage.add_url_rule('/notice_detail', view_func=notice_detail, methods=['GET', 'POST'])
manage.add_url_rule('/export_key', view_func=export_key, methods=['GET', 'POST'])
manage.add_url_rule('/add_app_protocol', view_func=add_app_protocol, methods=['GET', 'POST'])
manage.add_url_rule('/key_info', view_func=key_info, methods=['GET', 'POST'])
manage.add_url_rule('/set_key_status', view_func=set_key_status, methods=['GET', 'POST'])
manage.add_url_rule('/get_imei_info', view_func=get_imei_info, methods=['GET', 'POST'])
manage.add_url_rule('/add_imei_vip', view_func=add_imei_vip, methods=['GET', 'POST'])
manage.add_url_rule('/get_act_key_statistics', view_func=get_act_key_statistics, methods=['GET', 'POST'])
manage.add_url_rule('/agent_statistics', view_func=agent_statistics, methods=['GET', 'POST'])
manage.add_url_rule('/add_agent', view_func=add_agent, methods=['GET', 'POST'])
manage.add_url_rule('/get_agent', view_func=get_agent, methods=['GET', 'POST'])
manage.add_url_rule('/del_agent', view_func=del_agent, methods=['GET', 'POST'])
manage.add_url_rule('/get_app_version_check', view_func=get_app_version_check, methods=['GET', 'POST'])
manage.add_url_rule('/add_version_check', view_func=add_version_check, methods=['GET', 'POST'])
manage.add_url_rule('/del_app_check', view_func=del_app_check, methods=['GET', 'POST'])
manage.add_url_rule('/edit_version_check', view_func=edit_version_check, methods=['GET', 'POST'])
manage.add_url_rule('/add_phone_member', view_func=add_phone_member, methods=['GET', 'POST'])
manage.add_url_rule('/get_act_members', view_func=get_act_members, methods=['GET', 'POST'])
manage.add_url_rule('/check_key', view_func=check_key, methods=['GET', 'POST'])
manage.add_url_rule('/get_business_category', view_func=get_business_category, methods=['GET', 'POST'])
manage.add_url_rule('/add_business_category', view_func=add_business_category, methods=['GET', 'POST'])
manage.add_url_rule('/add_business_protocol', view_func=add_business_protocol, methods=['GET', 'POST'])
manage.add_url_rule('/add_bus_ware', view_func=add_bus_ware, methods=['GET', 'POST'])
manage.add_url_rule('/get_bus_info', view_func=get_bus_info, methods=['GET', 'POST'])
manage.add_url_rule('/set_bus_status', view_func=set_bus_status, methods=['GET', 'POST'])
manage.add_url_rule('/get_bus_details/<ware_id>', view_func=get_bus_details, methods=['GET', 'POST'])
manage.add_url_rule('/set_bus_priority', view_func=set_bus_priority, methods=['GET', 'POST'])
manage.add_url_rule('/edit_bus_ware<string:ware_id>', view_func=edit_bus_ware, methods=['GET', 'POST'])
manage.add_url_rule('/bus_statistics', view_func=get_bus_statistics, methods=['GET', 'POST'])
manage.add_url_rule('/get_bus_members', view_func=get_bus_members, methods=['GET', 'POST'])
manage.add_url_rule('/get_bus_members_details/<godin_id>', view_func=get_bus_members_details, methods=['GET', 'POST'])
manage.add_url_rule('/bus_pay_statistics', view_func=bus_pay_statistics, methods=['GET', 'POST'])
manage.add_url_rule('/add_friends', view_func=add_friends, methods=['GET', 'POST'])
manage.add_url_rule('/del_friends', view_func=del_friends, methods=['GET', 'POST'])
manage.add_url_rule('/free_vip_days', view_func=free_vip_days, methods=['GET', 'POST'])
manage.add_url_rule('/bus_give_stat', view_func=bus_give_stat, methods=['GET', 'POST'])
manage.add_url_rule('/bus_recommend', view_func=bus_recommend, methods=['GET', 'POST'])
manage.add_url_rule('/del_bus_recommend', view_func=del_bus_recommend, methods=['GET', 'POST'])
manage.add_url_rule('/second_add', view_func=second_add, methods=['GET', 'POST'])
manage.add_url_rule('/add_link', view_func=add_link, methods=['GET', 'POST'])

# 微信助理客服查询页面
manage.add_url_rule('/business_assistant', view_func=business_assistant, methods=['GET', 'POST'])
# 删除单个客服信息
manage.add_url_rule('/delete_assistant', view_func=delete_assistant, methods=['GET', 'POST'])
# 查询单个客服信息
manage.add_url_rule('/get_assistant_detail', view_func=get_assistant_detail, methods=['GET', 'POST'])
# 添加客服
manage.add_url_rule('/add_assistant', view_func=add_assistant, methods=['GET', 'POST'])
# 配置公众号
manage.add_url_rule('/set_gzh', view_func=set_gzh, methods=['GET', 'POST'])

# 免费体验周期
manage.add_url_rule('/free_experience_days', view_func=free_experience_days, methods=['GET', 'POST'])

manage.add_url_rule('/add_account', view_func=add_account, methods=['GET', 'POST'])
manage.add_url_rule('/get_account_info', view_func=get_account_info, methods=['GET', 'POST'])
manage.add_url_rule('/edit_channel_account/<int:cur_id>', view_func=edit_channel_account, methods=['GET', 'POST'])
manage.add_url_rule('/get_channel_data', view_func=get_channel_data, methods=['GET', 'POST'])
manage.add_url_rule('/channel_data_detail/<string:channel_id>', view_func=channel_data_detail, methods=['GET', 'POST'])
manage.add_url_rule('/day_key_record_detail/<key_record_id>', view_func=day_key_record_detail, methods=['GET', 'POST'])
manage.add_url_rule('/day_vip_detail/<key_record_id>/<record_time>', view_func=day_vip_detail, methods=['GET', 'POST'])
manage.add_url_rule('/expire_key', view_func=expire_key, methods=['GET', 'POST'])
manage.add_url_rule('/get_function_video', view_func=get_function_video, methods=['GET', 'POST'])
manage.add_url_rule('/add_function_video', view_func=add_function_video, methods=['GET', 'POST'])
manage.add_url_rule('/del_function_video', view_func=del_function_video, methods=['GET', 'POST'])
manage.add_url_rule('/edit_function_video', view_func=edit_function_video, methods=['GET', 'POST'])
# 倒三角功能配置
manage.add_url_rule('/set_function', view_func=set_function, methods=['GET', 'POST'])
manage.add_url_rule('/get_gold_ware_info', view_func=get_gold_ware_info, methods=['GET', 'POST'])
manage.add_url_rule('/add_gold_ware', view_func=add_gold_ware, methods=['GET', 'POST'])
manage.add_url_rule('/get_vip_gold_ware_details/<ware_id>', view_func=get_vip_gold_ware_details, methods=['GET', 'POST'])
manage.add_url_rule('/edit_gold_ware/<string:ware_id>', view_func=edit_gold_ware, methods=['GET', 'POST'])
manage.add_url_rule('/micro_store_url', view_func=micro_store_url, methods=['GET', 'POST'])
manage.add_url_rule('/generalize_data', view_func=generalize_data, methods=['GET', 'POST'])
manage.add_url_rule('/invite_detail', view_func=get_invite_detail, methods=['GET', 'POST'])
manage.add_url_rule('/invite_detail_detail', view_func=get_invite_detail_detail, methods=['GET', 'POST'])
manage.add_url_rule('/member_divide', view_func=member_divide, methods=['GET', 'POST'])
manage.add_url_rule('/invite_code_data', view_func=invite_code_data, methods=['GET', 'POST'])
manage.add_url_rule('/active_intro', view_func=active_intro, methods=['GET', 'POST'])
manage.add_url_rule('/money_check', view_func=money_check, methods=['GET', 'POST'])
manage.add_url_rule('/add_fc_content', view_func=add_fc_content, methods=['GET', 'POST'])
manage.add_url_rule('/fc_info', view_func=fc_info, methods=['GET', 'POST'])
manage.add_url_rule('/del_cf', view_func=del_cf, methods=['GET', 'POST'])
manage.add_url_rule('/edit_cf_content', view_func=edit_cf_content, methods=['GET', 'POST'])
manage.add_url_rule('/every_wash', view_func=every_wash, methods=['GET', 'POST'])
manage.add_url_rule('/add_privacy_protocol', view_func=add_privacy_protocol, methods=['GET', 'POST'])
manage.add_url_rule('/invite_code_divide', view_func=invite_code_divide, methods=['GET', 'POST'])
manage.add_url_rule('/alter_balance', view_func=alter_balance, methods=['GET', 'POST'])
manage.add_url_rule('/alter_detail', view_func=alter_detail, methods=['GET', 'POST'])
manage.add_url_rule('/delete_detail', view_func=delete_detail, methods=['GET', 'POST'])
manage.add_url_rule('/function_hot_dot', view_func=function_hot_dot, methods=['GET', 'POST'])
manage.add_url_rule('/master_get_function_video', view_func=master_get_function_video, methods=['GET', 'POST'])
manage.add_url_rule('/master_add_function_video', view_func=master_add_function_video, methods=['GET', 'POST'])
manage.add_url_rule('/master_del_function_video', view_func=master_del_function_video, methods=['GET', 'POST'])
manage.add_url_rule('/master_edit_function_video', view_func=master_edit_function_video, methods=['GET', 'POST'])
manage.add_url_rule('/alter_divide', view_func=alter_divide, methods=['GET', 'POST'])
manage.add_url_rule('/alter_divide_detail', view_func=alter_divide_detail, methods=['GET', 'POST'])
manage.add_url_rule('/get_pay_time', view_func=get_pay_time, methods=['GET', 'POST'])
manage.add_url_rule('/get_vip_pay_time', view_func=get_vip_pay_time, methods=['GET', 'POST'])
manage.add_url_rule('/appeal_edit', view_func=appeal_edit, methods=['GET', 'POST'])
manage.add_url_rule('/appeal_detail', view_func=appeal_detail, methods=['GET', 'POST'])

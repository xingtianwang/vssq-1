
# 添加素材库和微商报告
INSERT INTO `vssq`.`app_list` (`id`, `app_type`, `app_name`, `package_name`) VALUES ('9', '13', '素材库', 'com.materiallibrary');
INSERT INTO `vssq`.`app_list` (`id`, `app_type`, `app_name`, `package_name`) VALUES ('10', '14', '微商报告', 'com.guding.vbusiness');

# 插入默认的两个订单，赠送黄金或铂金会员
INSERT INTO `vssq`.`member_ware` (`id`, `name`, `category`, `price`, `discount`, `status`, `priority`, `description`, `create_time`, `channel`, `picture`, `ads_category`, `gold_discount`, `gold_or_platinum`, `common_discount`) VALUES ('freegod', '黄金会员赠送', '0', '0', '0.00', '0', '0', '黄金会员赠送', '0000-00-00 00:00:00', 'zensong', '', '', '0.00', '0', '0.00');
INSERT INTO `vssq`.`member_ware` (`id`, `name`, `category`, `price`, `discount`, `status`, `priority`, `description`, `create_time`, `channel`, `picture`, `ads_category`, `gold_discount`, `gold_or_platinum`, `common_discount`) VALUES ('freevip', '铂金会员赠送', '0', '0', '0.00', '0', '0', '铂金会员赠送', '0000-00-00 00:00:00', 'zensong', '', '', '0.00', '0', '0.00');


# 将已存在的账单修改为铂金会员账单
update `vssq`.`member_ware_order` set buy_grade = 1

update vssq.key_record set vip_gold_ad_time = 365 where vip_gold_ad_time is NULL;


# 对Key表进行数据迁移，将已经过期的设置为已经赠送，未激活标记为未赠送
update `vssq`.`key` set give_activate_status = 0 where status = 0
update `vssq`.`key` set give_activate_status = 1 where status = 2
update `vssq`.`key` set give_activate_status = 1 where status = 3

update `vssq`.`key` set give_activate_status = 0 where give_activate_status is NULL

# 更新老的商品为铂金商品
update vssq.member_ware set common_discount = 1 where common_discount is NULL;
update vssq.member_ware set gold_discount = 1 where gold_discount is NULL;
update vssq.member_ware set gold_or_platinum = 1 where gold_or_platinum is NULL;

# 设置通知表时间段为上午6:00到9:00
update vssq.sys_notice set time_quantum = 1

# 设置vip状态表为铂金会员
update vssq.vip_members set grade = 2

# 免费赠送十天
INSERT INTO `vssq`.`key_record` (`id`, `create_time`, `vip_time`, `count`, `oeprator`, `content`, `vip_ad_time`, `phone_num`, `we_record_id`, `channel_account_id`, `business_ratio`, `vip_ratio`, `vip_gold_ad_time`) VALUES ('00000000000001', '2019-07-01 15:37:02', '10', '0', 'Godin', '免费试用十天', '10', '', '', '1', '0.00', '0.00', 10);






##
update `vssq`.`member_ware_order` set buy_grade = 1;
update `vssq`.`key` set give_activate_status = 0 where give_activate_status is NULL;



INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('1', '自动抢红包', 'zidongqianghongbao', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('2', '虚拟定位', 'xunidingwei', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('3', '好友秒通过', 'haoyoumiaotongguo', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('4', '一键转发', 'yijianzhuanfa', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('5', '加群好友', 'jiaqunhaoyou', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('6', '自动打招呼', 'zidongdazhaohu', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('7', '清理好友', 'qinglihaoyou', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('8', '自助群发', 'zizhuqunfa', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('9', '通讯录加粉', 'tongxunlujiafen', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('10', '手机加粉', 'shoujijiafen', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('11', '群发群消息', 'qunfaqunxiaoxi', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('12', '群发名片', 'qunfamingpian', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('13', '便捷助手', 'bianjiezhushou', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('14', '图文转发', 'tuwenzhuanfa', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('15', '标记已读', 'biaojiyidu', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('16', '群发好友', 'qunfahaoyou', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('17', '一键点赞', 'yijiandianzan', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('18', '一键评论', 'yijianpinglun', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('19', '素材库', 'sucaiku', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('20', '语音转发', 'yuyinzhuanfa', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('21', '微课堂', 'weiketang', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('22', '微商助理', 'weishangzhuli', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('23', '微报告', 'weibaogao', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('24', '微商招募', 'weishangzhaomu', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('25', '推广赚钱', 'tuiguangzhuanqian', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('26', '有好商品', 'youhaoshangpin', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('27', '每日一淘', 'meiriyitao', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('28', '微商指数', 'weishangzhishu', '0', '0');
INSERT INTO `vssq`.`function_hot_dot` (`id`, `function_name`, `function_spell`, `today_status`, `tomorrow_status`) VALUES ('29', '购买会员', 'goumaivip', '0', '0');



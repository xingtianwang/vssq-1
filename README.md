# X分身服务器文档
***

#### 说明：
* 程序为X分身的业务系统后台，为X分身App提供REST API以及相应的管理系统。
* 程序的部署方式为 supervisor + gunicorn + flask + celery + nginx
* 详细的接口说明文档参见文件 [api-1.0](http://godinsec.gitlab.com/Private-Space/vservice-server/blob/develop/api_1_0), [api-1.1](http://godinsec.gitlab.com/Private-Space/vservice-server/blob/develop/api_1_1)及[api-1.2](http://godinsec.gitlab.com/Private-Space/vservice-server/blob/develop/api_1_2.md)

***
## 系统初始化
### 系统生成数据库迁移脚本出现错误时,执行以下shell
```
1、mv app/manage/form.py app/manage/form.py_bak
2、mv app/manage/form.py.mig app/manage/form.py
```

之后可以生成成功数据库脚本，数据库更新完成之后，需要执行2，1
### 系统在首次部署
* 首先生成迁移脚本 

	```
	python manager.py db init
	python manager.py db migrate -m "message"
	```
* 其次创建数据库表单：

	```
	python manager.py db upgrade
	```

* 第三，执行 ```python manager.py setup``` 对系统进行初始化
* 第四，执行 ```python manager.py create_admin``` 创建系统的超级管理员，之后登陆超级管理员，创建审计管理员及其他的用户。
***

## 数据库表单更新:
* 生成迁移脚本 

	```
	python manager.py db migrate -m "message"
	```
* 执行数据库脚本，修改数据库表单

	```
	python manager.py db upgrade
	```

## 服务器初始配置或重启
### 服务器上运行的服务
##### xavatar-a(101.201.69.156/192.168.1.1)
* 运行的服务列表及功能：

	```
	1、nginx:请求转发，静态文件访问
	2、redis-server: 缓存及短信验证码缓存
	3、rpcbind, nfs: 主机文件共享， 目前该机器是as_godinsec服务的nfs server端
	4、supervisord: python进程管理
	```
* 服务器重启后需要按照顺序执行以下脚本：

	```
	启动nginx命令:
	nginx -c /usr/local/nginx/conf/nginx.conf
	
	启动redis
	redis-server /etc/redis.conf
	
	启动nfs:
	service rpcbind  start
	service nfs  start 
	mount -t nfs 192.168.1.3:/data/xphone-server/XPhonePhoto /data/xphone-server/XPhonePhoto -o proto=tcp -o nolock
	mount -t nfs 192.168.1.3:/data/xphone-server/XPhoneException /data/xphone-server/XPhoneException -o proto=tcp -o nolock
	mount -t nfs 192.168.1.3:/data/xphone-server/XPhoneApk /data/xphone-server/XPhoneApk -o proto=tcp -o nolock
	mount -t nfs 192.168.1.3:/data/vservice-server/AvatarPhoto /data/vservice-server/AvatarPhoto -o proto=tcp -o nolock
	mount -t nfs 192.168.1.3:/data/vservice-server/AvatarException /data/vservice-server/AvatarException -o proto=tcp -o nolock
	mount -t nfs 192.168.1.3:/data/vservice-server/AvatarApk /data/vservice-server/AvatarApk -o proto=tcp -o nolock
	
	启动supervisord：
	supervisord -c /data/supervisord/supervisord.conf
	```

##### xavatar-b(101.201.234.100/192.168.1.3)
* 运行的服务列表及功能：

	```
	1、nginx:请求转发，静态文件访问
	2、rpcbind, nfs: 主机文件共享， 目前该机器是X分身以及XPhone服务的nfs server端
	3、supervisord: python进程管理
	```
* 服务器重启后需要按照顺序执行以下脚本：

	```
	启动nginx命令:
	nginx -c /usr/local/nginx/conf/nginx.conf
	
	启动nfs:
	service rpcbind  start
	service nfs  start 
	mount -t nfs 192.168.1.1:/data/as_godinsec/as_godinsec_file /data/as_godinsec/as_godinsec_file -o proto=tcp -o nolock
	
	启动supervisord：
	supervisord -c /data/supervisord/supervisord.conf
	```

## CentOS nfs配置
### 环境
* 服务器：10.0.5.23
* 客户端：10.0.5.24
* 安装软件包: ```yum -y install nfs-utils  rpcbind```

### 服务端配置
* 在服务器端建立共享目录：```/data/as_godinsec/as_godinsec_file```
* 设置共享目录的读写权限：```chmod 777 /data/as_godinsec/as_godinsec_file```
* 编辑export文件: ```vi /etc/exports```,在文件中添加以下内容：
	```
	/data/as_godinsec/as_godinsec_file/ 10.0.5.24(rw,no_root_squash,no_all_squash,sync)
	```
* 配置生效：```exportfs ```
   
* 启动服务rpcbind、nfs服务
	
	```
    service rpcbind  start
    service nfs  start 
	```
* 重启nfs：```service nfs restart```
	
### 客户端配置
*  创建挂载目录：```mkdir /data/as_godinsec/as_godinsec_file```
* 查看服务器抛出的共享目录信息 ``` showmount -e 10.0.5.23 //如果没有命令安装 yum install showmount```
	如果配置成功显示以下结果: 
	
	```
	Export list for 10.0.5.23:
	/data/as_godinsec/as_godinsec_file 10.0.5.24
	```
* tcp 挂载服务: ```mount -t nfs 10.0.5.23:/data/as_godinsec/as_godinsec_file /data/as_godinsec/as_godinsec_file  -o proto=tcp -o nolock```

* 卸载已挂载的NFS:```umount /data/as_godinsec/as_godinsec_file```
    
* 查看挂载目录的信息: ```fuser -m -v /data/as_godinsec/as_godinsec_file```	    

## 相关运维指令
* 其中supervisor 为启动和守护gunicorn及celery进程的监控程序，gunicorn所启动的服务为web及rest API接口部分, celery任务为定时检测异常日志的状态并发送邮件给PM。
* 服务器端程序首选通过supervisor启动，如紧急情况下supervisor 不能启动时，将gun.py中的daemon = True这一行的注释去掉，通过gunicorn启动。

* 通过supervisor启动时，一定要确保gun.py中的daemon = True这一行是被注释掉的

* supervisor 如果加上 -n 参数，则supervisor进程不是守护进程

* supervisor 首次启动时使用以下指令:

	```
	supervisord -c /data/supervisord/supervisord.conf
	```

* 查看状态:
	
	```
	supervisorctl -c /data/supervisord/supervisord.conf status
	```

* 停止某个应用:

	```
	supervisorctl -c /data/supervisord/supervisord.conf stop send_exception(或者all或者vservice)
	```

* 启动某个应用

	```
	supervisorctl -c /data/supervisord/supervisord.conf start send_exception(或者all或者vservice)
	```

* 重启某个应用

	```
	supervisorctl -c /data/supervisord/supervisord.conf restart send_exception(或者all或者vservice)
	```

* gunicorn 方式启动：
程序运行指令 ```gunicorn -c gun.py manager:app```

* 运行celery任务

	```
	celery worker -A manager.celery -l INFO
	celery beat --app manager.celery -l INFO
	```

* 压力测试: 
	指令：
	```
	ab -p GetWhiteList.json -T application/json -c 5000 -n 500000  http://127.0.0.1:9000/api/v1.0/GetWhiteList
	```
	
其中 -c 参数为并发数， -n参数为总的请求数,请求数据在对应的test_data目录下的对应接口同名的.json文件中。

* 单元测试

	```
	python -m unittest tests.test_api_1_1.TestApi1(执行api_1_1的TestApi1的所有测试脚本)
	python -m unittest tests.test_api_1_1.TestApi1.test_register(执行api_1_1的TestApi1的注册测试脚本)
	```
* 使用httpie测试

	```
http --json POST http://127.0.0.1:9010/api/v1.2/GetAuthSms @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/GetAuthSms.json
http -a 'eyJleHAiOjE0ODk2NDgzNDAsImlhdCI6MTQ4OTY0NDc0MCwiYWxnIjoiSFMyNTYifQ.eyJpZCI6MX0._RNQrc9BhepAdm5NXaAlqi_QBpL0bEMsR_dRcHiUcP8':"" --json POST https://127.0.0.1:9010/api/v1.2/VerifySms @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/VerifySms.json
http --json POST http://127.0.0.1:9010/api/v1.2/Register @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/Register.json
http --json POST http://127.0.0.1:9010/api/v1.2/UploadMobileInfo @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/UploadMobileInfo.json
http --json POST http://127.0.0.1:9010/api/v1.2/GetWhiteList @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/GetWhiteList.json
http --json POST http://127.0.0.1:9010/api/v1.2/FeedBack @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/FeedBack.json
http --json POST http://127.0.0.1:9010/api/v1.2/CheckFrameUpdate @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/CheckFrameUpdate.json
http --json POST http://127.0.0.1:9010/api/v1.2/CheckPluginUpdate @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/CheckPluginUpdate.json
http -a 'eyJleHAiOjE0ODk2NDgzNDAsImlhdCI6MTQ4OTY0NDc0MCwiYWxnIjoiSFMyNTYifQ.eyJpZCI6MX0._RNQrc9BhepAdm5NXaAlqi_QBpL0bEMsR_dRcHiUcP8':"" --json POST http://127.0.0.1:9010/api/v1.2/SetUserInfo @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/SetUserInfo.json
http --json POST http://127.0.0.1:9010/api/v1.2/UploadExceptionLog @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/UploadExceptionLog.json
http --json POST http://127.0.0.1:9010/api/v1.2/UploadAppStatistics @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/UploadAppStatistics.json
http -a 'eyJleHAiOjE0ODk2NDgzNDAsImlhdCI6MTQ4OTY0NDc0MCwiYWxnIjoiSFMyNTYifQ.eyJpZCI6MX0._RNQrc9BhepAdm5NXaAlqi_QBpL0bEMsR_dRcHiUcP8':"" --json POST http://127.0.0.1:9010/api/v1.2/ValidateLoginUser @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/ValidateLoginUser.json
http -a 'eyJleHAiOjE0ODk2NDgzNDAsImlhdCI6MTQ4OTY0NDc0MCwiYWxnIjoiSFMyNTYifQ.eyJpZCI6MX0._RNQrc9BhepAdm5NXaAlqi_QBpL0bEMsR_dRcHiUcP8':"" --json POST http://127.0.0.1:9010/api/v1.2/AddPrivateContact @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/AddPrivateContact.json
http -a 'eyJleHAiOjE0ODk2NDgzNDAsImlhdCI6MTQ4OTY0NDc0MCwiYWxnIjoiSFMyNTYifQ.eyJpZCI6MX0._RNQrc9BhepAdm5NXaAlqi_QBpL0bEMsR_dRcHiUcP8':"" --json POST http://127.0.0.1:9010/api/v1.2/UpdatePrivateContact @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/UpdatePrivateContact.json
http -a 'eyJleHAiOjE0ODk2NDgzNDAsImlhdCI6MTQ4OTY0NDc0MCwiYWxnIjoiSFMyNTYifQ.eyJpZCI6MX0._RNQrc9BhepAdm5NXaAlqi_QBpL0bEMsR_dRcHiUcP8':"" --json POST http://127.0.0.1:9010/api/v1.2/DeletePrivateContact @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/DeletePrivateContact.json
http -a 'eyJleHAiOjE0ODk2NDgzNDAsImlhdCI6MTQ4OTY0NDc0MCwiYWxnIjoiSFMyNTYifQ.eyJpZCI6MX0._RNQrc9BhepAdm5NXaAlqi_QBpL0bEMsR_dRcHiUcP8':"" --json POST http://127.0.0.1:9010/api/v1.2/GetPrivateContact @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/GetPrivateContact.json
http --json POST http://127.0.0.1:9010/api/v1.2/UploadFramePluginVersion @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/UploadFramePluginVersion.json
http --json POST http://127.0.0.1:9010/api/v1.2/UploadFramePluginStatistics @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/UploadFramePluginStatistics.json
http -a 'eyJleHAiOjE0ODk2NDgzNDAsImlhdCI6MTQ4OTY0NDc0MCwiYWxnIjoiSFMyNTYifQ.eyJpZCI6MX0._RNQrc9BhepAdm5NXaAlqi_QBpL0bEMsR_dRcHiUcP8':"" --json POST http://127.0.0.1:9010/api/v1.2/VoiceStatistics @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/VoiceStatistics.json
http --json POST https://127.0.0.1:9010/api/v1.2/GetWeChatFeature @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/GetWeChatFeature.json
http -a 'eyJleHAiOjE0ODk2NDgzNDAsImlhdCI6MTQ4OTY0NDc0MCwiYWxnIjoiSFMyNTYifQ.eyJpZCI6MX0._RNQrc9BhepAdm5NXaAlqi_QBpL0bEMsR_dRcHiUcP8':"" --json POST http://127.0.0.1:9010/api/v1.2/UploadCamouflageInfo @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/UploadCamouflageInfo.json
http -a '15011329055':"718935"  --json POST http://127.0.0.1:9010/api/v1.2/GetAuthToken @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/GetAuthToken.json
http -a 'eyJleHAiOjE0OTI4MzE3NzMsImlhdCI6MTQ5Mjc0NTM3MywiYWxnIjoiSFMyNTYifQ.eyJpZCI6MTA5LCJpbWVpIjoiODc2ODg2MDI0Mzk5OTAzIn0.bvdzsB--fyay-vUBnJYtUr0NxrV1pxItFgc0WPrxNO4':"" --json POST http://127.0.0.1:9010/api/v1.2/GetCamouflageWare @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/GetCamouflageWare.json
http -a 'eyJleHAiOjE0OTI4MzE3NzMsImlhdCI6MTQ5Mjc0NTM3MywiYWxnIjoiSFMyNTYifQ.eyJpZCI6MTA5LCJpbWVpIjoiODc2ODg2MDI0Mzk5OTAzIn0.bvdzsB--fyay-vUBnJYtUr0NxrV1pxItFgc0WPrxNO4':"" --json POST http://127.0.0.1:9010/api/v1.2/FirstCamouflageMember @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/FirstCamouflageMember.json
http -a 'eyJleHAiOjE0OTI4MzE3NzMsImlhdCI6MTQ5Mjc0NTM3MywiYWxnIjoiSFMyNTYifQ.eyJpZCI6MTA5LCJpbWVpIjoiODc2ODg2MDI0Mzk5OTAzIn0.bvdzsB--fyay-vUBnJYtUr0NxrV1pxItFgc0WPrxNO4':"" --json POST http://127.0.0.1:9010/api/v1.2/BuyCamouflageWare @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/BuyCamouflageWare.json
http -a 'eyJleHAiOjE0OTI4MzE3NzMsImlhdCI6MTQ5Mjc0NTM3MywiYWxnIjoiSFMyNTYifQ.eyJpZCI6MTA5LCJpbWVpIjoiODc2ODg2MDI0Mzk5OTAzIn0.bvdzsB--fyay-vUBnJYtUr0NxrV1pxItFgc0WPrxNO4':"" --json POST http://127.0.0.1:9010/api/v1.2/GetCamouflageWareTime @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/GetCamouflageWareTime.json
http -a 'eyJleHAiOjE0OTI4MzE3NzMsImlhdCI6MTQ5Mjc0NTM3MywiYWxnIjoiSFMyNTYifQ.eyJpZCI6MTA5LCJpbWVpIjoiODc2ODg2MDI0Mzk5OTAzIn0.bvdzsB--fyay-vUBnJYtUr0NxrV1pxItFgc0WPrxNO4':"" --json POST http://127.0.0.1:9010/api/v1.2/GetPermission @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/GetPermission.json
http -a 'eyjlehaioje0oti4mze3nzmsimlhdci6mtq5mjc0ntm3mywiywxnijoisfmyntyifq.eyjpzci6mta5lcjpbwvpijoiodc2odg2mdi0mzk5otazin0.bvdzsb--fyay-vubnjytur0nxrv1pxitfgc0wprxno4':"" --json post http://127.0.0.1:9010/api/v1.2/HideIconSwitch @/users/allan/projects/python/vservice-server/test_data/v_1_2/HideIconSwitch.json
http --json POST http://127.0.0.1:9010/api/v1.2/GetAppExtension @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/GetAppExtension.json
http --json POST http://127.0.0.1:9010/api/v1.2/ExtensionStatistics @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/ExtensionStatistics.json
http --json POST http://127.0.0.1:9010/api/v1.2/GetOpenScreenAds @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/GetOpenScreenAds.json
http --json POST http://127.0.0.1:9010/api/v1.2/OpenScreenAdsStatistics @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/OpenScreenAdsStatistics.json
http --json POST http://127.0.0.1:9010/api/v1.2/GetBanneradsStatistics @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/GetBanneradsStatistics.json
http --json POST http://127.0.0.1:9010/api/v1.2/GetBanneradsInfo @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/GetBanneradsInfo.json
http --json POST http://127.0.0.1:9010/api/v1.2/GetOpenScreenAdsStatistics @/Users/allan/Projects/python/vservice-server/test_data/v_1_2/GetOpenScreenAdsStatistics.json
	```



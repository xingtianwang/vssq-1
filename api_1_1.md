# 微商神器接口文档---v1.0
***
#### 导语：
* 所有的请求消息只有一层JSON封装。
* 所有的响应消息，在head中只有statuscode和statusmsg,数据载荷都封装在body字段中，除列出特别说明的，都为必须字段。只有在SetUserInfo接口中的nick_name和photo和person_profile字段是可选的。
* 请求token时需要手机号：密码验证。
* 以下的接口文档中的url，**server_addr** 需要根据相应的部署环境替换为相应的地址，例如，测试环境下**server_addr** 需要替换为**godinsec.cn**，在生产环境下，**server_addr** 需要替换为**wemiyao.com**。

*** 

## 接口说明
### **1. 请求验证码:**	

* url: https://**server_addr**/vssq/api/v1.1/GetAuthSms
* method: POST
*  请求消息示例:

	```
	{
	  "app_version": "1.0.1",
	  "imei": "123456789012345",
	  "msg_type": "1",
	  "phone_num": "15011329055"
	}
	```
	
	##### 参数说明:
	```
	phone_num: 用户手机号
	msg_type: "1" 代表此验证码被用作注册登录接口
	imei: 用户唯一设备标识，imei
	app_version: 应用版本名
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
		"head": {
	        "statuscode": "000000",
	        "statusmsg": "Success"
	    }
	}
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: 电话号码格式或长度错误, HTTP状态码为200
	```
	{
		"head": {
        "statuscode": "000004",
        "statusmsg": "phone number invalid"
    	}
	}
	```
	##### fail-3: 已经发送过验证码并且验证码还未过期，用户发送重复请求, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000001",
	        "statusmsg": "sms already sent"
	    }
	}
	```
	##### fail-4: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-5: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-6: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```

### **2. 注册登录:**	

* url: https://**server_addr**/vssq/api/v1.1/Register
* method: POST
*  请求消息示例:

	```
	{
	  "phone_num": "15011329055",
	  "device_model": "Nexus7",
	  "smsverifycode": "671830",
	  "password": "111111",
	  "app_version": "1.0.1",
	  "device_factory": "Google",
	  "msg_type": "1",
	  "imei": "123456789012345",
	  "os_type": "android",
	  "os_version": "5.1.1",
	  "channel": "godinsec",
	}
	```
	
	##### 参数说明:
	```
	phone_num: 用户手机号
	device_model: 设备型号
	device_factory: 设备厂商
	imei: 用户唯一设备标识，imei
	app_version: 应用版本
	smsverifycode: 短信验证码
	password: 调用注册登录接口时客户端随机生成的密码串，客户端需要保存，后续刷新token使用
	msg_type: 注册登录此值"1"
	os_type: "android", 代表安卓系统, "ios"代表苹果系统
	os_version: 系统版本好
	channel: 渠道
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	    "body": {
	        "create_time": "2016-10-10 14:25:38",
	        "godin_id": "4c59396301ab6274bd7892f0b31df36e",
	        "imei": "123456789012345",
	        "expiration": "3600",
	        "nick_name": "",
	        "photo_md5": "",
	        "photo_url": "",
	        "virtual_lock": "",
	        "token": "eyJhbGciOiJIUzI1NiIsImV4cCI6MTQ4Mzk1MjM3NiwiaWF0IjoxNDgzOTQ4Nzc2fQ.eyJpZCI6MX0.bIR0v-c5_Id7rVFSDv4SYapMQ3Xawsg3-OHRxpKaGr0",
	        "current_time":"2016-04-20 14:25:38"
	    },
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "Success"
	    }
	}
	```
	##### 参数说明:
	```
	create_time: 创建时间
	token: 接口交互所需要的token
	expiration: token有效期，时间单位为秒
	godin_id: 用户国鼎ID
	imei: 用户唯一设备标识，imei
	nick_name: 用户昵称
	person_profile: 个人资料
	photo: 用户头像url
	photo_md5: 用户头像的MD5值
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: 电话号码格式或长度错误, HTTP状态码为200
	```
	{
		"head": {
        "statuscode": "000004",
        "statusmsg": "phone number invalid"
    	}
	}
	```
	##### fail-3: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-4: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-5: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-6: 内部错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000016",
	        "statusmsg": "internal error"
	    }
	}
	```
	##### fail-7: 验证码违法, HTTP状态码为200
	```
	{
		"head": {
            "statuscode": "000002",
            "statusmsg": "sms verify code invalid"
        }
	}
	```
	##### fail-8: 验证码过期, HTTP状态码为200
	```
	{
		"head": {
            "statuscode": "000003",
            "statusmsg": "sms verify code expired"
        }
	}
	```
	
### **3. 上传设备信息:**	

* url: https://**server_addr**/vssq/api/v1.1/UploadMobileInfo
* method: POST
*  请求消息示例:

	```
	{
	  "app_version": "1.0.1",
	  "device_factory": "Google",
	  "device_model": "Nexus7",
	  "imei": "123456789012345",
	  "os_type": "android",
	  "os_version": "5.1.1",
	  "market": "godinsec",
	}
	```
	
	##### 参数说明:
	```
	device_model: 设备型号
	device_factory: 设备厂商
	imei: 用户唯一设备标识**，imei
	app_version: 应用版本
	os_type: "android", 代表安卓系统, "ios"代表苹果系统
	os_version: 系统版本好
	market: 渠道
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "Success"
	    }
	}
	```
	
	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 内部错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000016",
	        "statusmsg": "internal error"
	    }
	}
	```


### **5. 用户反馈信息:**	

* url: https://**server_addr**/vssq/api/v1.1/FeedBack
* method: POST
*  请求消息示例:

	```
	{
	  "app_version": "1.0.1",
	  "godin_id": "fa54a842ed1ab94b8334f3c318296e21"
	  "device_factory": "Google",
	  "device_model": "Nexus7",
	  "imei": "123456789012345",
	  "os_type": "android",
	  "os_version": "5.1.1",
	  "user_contact": "test@godinsec.com",
	  "content": "this is my feedback message",
	  "attach": {"suffix": 'jpg', "photo": "iVBORw0KGgoAAAANSUhEUgAAAGoAAABqCAIAAA=="}
	}
	```
	
	##### 参数说明:
	```
	app_version: 应用版本
	godin_id: 国鼎ID
	device_model: 设备型号
	device_factory: 设备厂商
	imei: 用户唯一设备标识，imei
	os_type: "android", 代表安卓系统, "ios"代表苹果系统
	os_version: 系统版本好
	user_contact: 用户联系方式, 必填
	content: 反馈内容
	attach: 附加参数, 图片数据
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}
	```
	##### 参数说明:
 	```
	package_name: 新增的白名单列表
	version_code: 服务器端白名单的版本，类型的字符串
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	
### **6. 设置用户信息:**	

* url: https://**server_addr**/vssq/api/v1.1/SetUserInfo
* method: POST
* http请求头部添加: Authorization: Basic MTUwMTEzMjkwNTU6MTExMTEx(此处为base64编码数据，数据内容:(token值:""))
* 请求消息示例:

	```
	{
	  "nick_name": "hello",
	  "person_profile": "thanks",
	  "imei": "123456789012345",
	  "app_version": "1.0.1",
	  "photo": "iVBORw0KGgoAAAANSUhEUgAAAGoAAABqCAIAAADbQ1PAAAAAA3NCSVQICAjb4U/gAAAPlElEQVR4nO1cWa9cx3H vurTZ/a7cBEpUgs3a7FII3IU2EJgZVMAGfYDEwQJkgfnJU/5V/JbYMSxlTh2gCQPMixZsCxbXhRYoihZIinykry829xZzun68nDmLqJox9EsN3LmQwN3cGfm1PSH6qqu6urioWOfxhwfF3bQP CTjTl9Y2FO31iY0zcW5vSNhTl9Y2FO31iY0zcW5vSNhTl9Y2FO31iY0zcW5vSNhTl9Y2FO31jIDkqwwXdfJwIwgAAoyAoA8BokUmCSklgHCwpQDCgAc4Tq2wfx80c4MPr2Kz5FMJECLGN66Mgfnj3xB624WFL94e2t3rXN7o3b6 /c2vigYFc2KFUDEzGgDDrIBXRw9IkASJI0ZBYKiUT 1Om/ 8y5L2ZpkewLdHd3l5jQG2D16p0f/fLG6 /e H5SAZgUeaDaFxrtowci2JiFkJkF0gxGiKovdx7 k8/8vaEOlrKSgDgUCljPw8DQWswffOjwk4 c ONmXFzv3hj6BsED f0Vpk5fZdIIJ0QkwgxZtEYIe9OWZW5G9h859qUHjj4JJiCCCaQ7BEiEAyiFQnIwW26fOnvid5pcvLX5nqfC6ARViRqNWWDq9HHvLwHLQsyyGmkkAZJGGpFkyZQfW/7UA8u/DzisD WgJKEiEA5IckmJW/KA1F5snz5x9HxvcGtrcM3J2W8kZkCfA4QCGWMWzSIw8q EQQRoJKwkGyrLRx/8PFEHB1BdSFJFmUtJ8BF9cvehuC12M9aOHX4yY3t18xcukDNdyzOgTwCzrF7LG2QASIIkUSkgSGaquZVQPizWcoX7lj4LJsAAl Se7qLPkSSXSx4KJSEttw8fbpz7YOOnkqY6nbswFfr22zuHhSzGvCmYVe/Idj9CGhnAMiAaBera uu3Nt4EVJZb3cEqQmEZBcghFAll0tATIboSWEqiCIV6bfFw59QH6z8vdyzlDMBpHJPvt0BZqNXrTXmQAKjCvvcdgFBISim5e2l9U27uRB KVL0WDx9aOnn86KdPHvm9hi3B14cusZ9SgjddAylJSVKptNp990dvf9WTnLNQw6lo3669C6HWrC0YMggEhbum5KAnHw7KfpkKV9KITTqCmDtqbmmI9fX e9duv/HWe/ 60b3abDwY41JKdCRHf2QM4YCoUA H6g2/eWdFLCY r49iSvQJIBlbzU6GOgWCBtOORlRu1z0Ni56rSEg0CAIVPICJLMEEJtAhA4IBkt3pXbu88p9Ff2Vp4bhSyzWA 457SWDP1G/mpwZa2dhemfi8Poqp0CeKylr1Q9EWZENRogRhx1dIGvrmsOwLEkAQIkGCVTAC7NnH0TNHcQog3t5 94Pblw8tLUZbpLtYSCkBLk As1hqnlrZuFz6GtQ0FpraNnBKnpd51mo1FkHSQO44CiMJKQ2LXpGGH//pyMpybWXl3U6nk8dll0EJ6CWnq3RPoNfqndU7l8m TzMwnRJ9YbF9LLAGCtLu/q7axw2GWykNxzTsZkVC/8bq wud5RgbkhHDJEheSclDq7e93itvCDnutrkTw1Toy2OzVT9ERLCUsBtdgBgMukXZA5PGiBCMQ1dTyNw2bq1eO7J00rwFd4d2dtoJSvVaZ XOJU3TBU MPtEJmmjgUvOhLGSAA1ZZLQAki7TVH2yDCdA49kgIo8cqS7a91V09unSGHCQkwV2l4ElFZLM3uNErtiYywXtictpXeVMwzxrt1uHd4KmKMQAIxdb2GuCooteJmXMrhpt5aDTy48mHPnLEVYwMhOHq1vXpLd4JxtgEXVItXyDDvkEiAhwOe66BUE5aLmTp6u0f97XpGu4OKUlFp3nSmE9Q1l2YbIrCSTbqnWrbMaIPIxL7g60d1ZskCIc3emn99uZb7uW 4a4S3mi3FicrcT8mRh8lkwXW89gKoAkmBJAmUkUaFBg4zGGTptBhAyje2ngz TAlOXrucA2SCk/FUrx/XxJwwhvACe J8lgnYmXdqv8QEdRg0JusoH2ojjt8u7dVlFuZLcgdGkICHGK91pqa6AkuXjpgMdahYDYapBExBJZpMK1MnAwjv Wb3RXXwL10L9y9ykTkcYr0TVj7YlYjI1HuaJ8ok4ZlOVRI08kGj0I5AIPhhquUl0AiIpGgkrQsy1JK00gFTmw ApwerJ0bzczMSJpZCNHdYAMoTErWRySPeOmpO1Q/qXQoYZAkx9ClDC2qNJlN lhugtpnEIJFIhgpqEpPuWaUuQSQUjna8clG/omAgtm0zkAmSB8BmJlZcHAv2JjalvVe8JQKUMYMTBBU1SlMDZOjT4YqmGDYT1m1lCcm5deCrLISTF5UGyYiAHCf1gqYHH0soOjqGXOo0rpK 0xZy0FHaZiS RvBLEou5bTCHTQnMqqeuO0IoGMULE8ME7V9SK4S NBpYUBmWSNjXiJNex1noe4qKaN7dVQlODkoy1LSNHZOE11WLIfDnpkFi8GiMTNmgRZQa9YWZlDLk4WGJKncSd8DUJl6U IOk973 WDY3cktI4QAIMgTQ6u5vNW/OT0fXLETQgTcJSpUCSApDYabUxM7Se1zIOsN1xNljLtDIaPZUvtTFK0aHy7uGxMiQaejlS/Ck7s74eZC4V4mpl7a3NkGaOKZq4kvKO/2bplluyMwBmaN2FxoPQgWYLGTRp0UVJ2757EhpN0z3 otqej3u5OTdTcmOA2DDCzWt65gtAE0M8tQD2YBzZNHzkM1AFUkPympVYVgjLUs1KuDDveyIhH0MvXKtD0pWR/FRNOlIOibWzerZJ9ZlmV5sDxazKzeaZw4snxmh8EJo1FvpQR3d087Oigp9fpdcIr1k5PM9wFy5QW7q uXApuk6BHBaO0QQsbGuWPPxHypDO7Ix8nB2Wi4wZW8mS8HNMjKnlY1NEhQaf3N/h23KdZcTWUzcX39DWffsGAGs8zMjJlZiKF94fQf1dJRs7VJyLEqRRZj7g7fLTeoDtuQtnsbVc5qErLujakcVJbajrG51Hg4o2jBmJFmzDLLGuFIp710c 160sfPAFY1NHKLWb1Wb1E5YaMqhb2ihLTRXXEWwBTVbyr0OcNWd/X Q4/UQhs0s2CsdJBRtUbtyMLiqVubP/vYoWhVQxOzeh7rYGaIEMCkkVMigO3eepE2xRLIPmH0gRQGg 3u0SOPRsXMLNCMGZkhBCJ0assnjlzobt3pFrcdHlgIOWCyQfCMIBEIq5xRNdz2TKXJYmzGrEHE0cUPCDBTojIzufc2BrcEAmGKlm969BEa9Psx51LzNFknYzCx0kELIcQalx8 cb5VO7S9uTZMPYWeWMIbyrqyJJYyNwDU7qAIWWaNPGYhZJChOkAGIVbpHtFd5db2po9ORKeLKRWoEZSY7nSvdVpHmvXlwHowmGVVOalZZmFgWlhunnvkoac7rft8iN72BllCORWoUOnZrspRFrNaHhox1HbiQgEu7aRFKTII5XZ/LXk51dqMvZlOrQkTRYFl7p3fffwvD9UeDQRMgFW WMhjIBmC1XNGWDb0jdt33rnZfXu7t94brCbfvtN7rygKkiEEUwQgJADCbjLZISNJBtLEOCzWi3KK  S7Jzn1Hlb0nJ3PPvLlw62nwAGRkxnNcjJYZpYbswyNKkIxBlnImGUWAZTa smlb//k/a 6ctiouLd65t7zlXEH/XKjLHfX7Ce2OPfDMGm4svJ o8WlxkNmZaAyRGPFVzQLgdHMRnc8LAQGowEgWsfv 9RWr3t76/KoCnonmMVuVpFOCvDBsFf6LApy92MG9JEonYPrq  WqXd44XzQ4RC7RM0sI4JZFphV9NkefYGkWFjKFxfab7z/LQC7l2PwoYxs6V4WxUBKk4ukf1PM4lKWE4KJXO2 98Hq64uLzWbtTKCMkTRjNFT2y0iDmdEq7ZMsE2Mtf 3NfxN6kle1WvvjCFdRphIQbSbO4sOYOn2VrapeGlCU6 /d Pn64O3FztFGftjQCkxC3UgLHixRDbO8uhYilqLubN/4rysvYPScaowuaKVUlkpTyeT9ZpjpjUqKoINld3vjzauv3t56O8vYad0fjIGZeZ1qI/QDzSCwDKkub//w0vM3uj mwm7K071MqaxuGx3ohcoZeN59MBFMlRMoA4iCXmvwvpNHzt1/5NNHOo8vt08hi5HNwExIKLdfe drr737fFksBdvG7pHjvmU6u0P4e2Hm9I3EioLAZJINWeYBVXFqaDQON/LF3JpCur31/rZWkBYzdD cHPJ9rw7yNvlM6fvtw7yTxliY0zcW5vSNhTl9Y2FO31iY0zcW5vSNhTl9Y2FO31iY0zcW5vSNhel3UGMJGBFUdS3Yw0dOLUb/NpLuPrrgWvXV DU1bQfagG4Gsg2ys2fP1mr1neYYaa/qqWrAt3 AZ86cbTSaZ86cbTQa0qh87x6fPOjmfZgFfTKA589fqNUacspZTVujCz4Binu9ImiAPfHEhVqt6tgk0iRAcVTDNfrMKO08245L98AM2h9WC9YgW gcfuaZZ2KMly5d tkbPzy0fOjpzz8TY23l5rWXXnppcXHxC1/4gie0WwtyLi4sX79 9amnngohPnDyoWsfXHn55Zerz5BcW1t7/fXXNzc3pVlUE/wqzED5BSZ4DSyee 7LP3zt y/88z8 9tj548dOPvbY4y 9/OI3X/jaqYcfabebf/rsl1555eV//49vt9sLYHH//SdrtdrxYw/0e8Ov/9M/nD59emFh4dlnn33llVe 851vnTt3rl7PhT7oe2Pm/ftm2nyz3W5ev35d0uXLl44fP/HOO7/83OeezvO80 lkWbawsHDz5k3Jr1y5sv9bV69elbS vp5lWafTWVlZkdKV96 NaiR/213HHspymOcNIHQ6re5W74vPfenll1554Zv/srGxQbIoilqtRrLdbu//VuWFq9PJoiiazSYZlpeXR2Z0x2geiB2cqfZ9/5WX/vzP/mJtba3eyL/73e8  uijTz/9NIAYY7PZ/N73vnfx4sXNzY3l5eVf9YQXX3zx4sWL/X5/YWFJ0oULF r11g9 8IOvfOVvn3/  SeeeLzRaLz66qszm9GszzpCCHme93qju/nNZrPf72unOV2MkWRZlveonKRD9uSTn/3pT39eFv7Xf/NX3/jG17e3t2fbLfJuzFT7JJVlmdJeqXu328W ioui B KVDY2Ni5evJhSeuutX/R6vYPlDp kk7ZRJ7qquZrvBS3/f1zH5LAb8B3sKflBNl3/X2KkZdprUj/qgXqQ IRq3/8VzOkbC3P6xsKcvrEwp28szOkbC3P6xsKcvrEwp28szOkbC3P6xsKcvrEwp28s/DdVGytosu62 QAAAABJRU5ErkJggg==",
	  "godin_id": "0e6ad2a71e31752deb69d6e8c9eabe76"
	}
	```
	
	##### 参数说明:
	```
	imei: 用户唯一设备标识，imei
	app_version: 应用版本
	godin_id: 用户国鼎ID
	nick_name: 用户昵称，可选字段
	person_profile: 个人简介，可选字段
	photo: 头像文件，Base64格式编码， 可选字段
	```
	#### 响应消息及错误码：
	##### success, HTTP状态码为200:
	```
	{
	    "head": {
	        "statuscode": "000000", 
	        "statusmsg": "success"
	    }
	}
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: 身份验证不通过, HTTP状态码为401 
	```
	HTTP/1.0 401 UNAUTHORIZED
	WWW-Authenticate: Basic realm="Authentication Required"
	```

	##### fail-3: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-4: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-5: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-6: 用户不存在, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000026",
	        "statusmsg": "user not exist"
	    }
	}
	```
	##### fail-7: 图片格式错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000010",
	        "statusmsg": "photo data not invalid"
	    }
	}
	```

### **7. 上传异常log:**	

* url: https://**server_addr**/vssq/api/v1.1/UploadExceptionLog
* method: POST
*  请求消息示例:

	```
	{
		"app_version": "1.0.5",
		"content": "log content",
		"device_model": "Honour6",
		"imei": "123456789012345",
		"md5_value": "4c59396301ab6274bd7892f0b31df36e",
		"os_version": "6.0.1",
		"package_name": "com.godinsec.launcher"
	}
	```
	
	##### 参数说明:
	```
	app_version: 应用版本
	content: 反馈内容
	device_model: 手机型号
	imei: 用户唯一设备标识，imei
	md5_value: 异常log的MD5值
	os_version: 系统版本号
	package_name: 产生异常的插件包名
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: app版本错误,目前只记录最新版本log, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000017",
	        "statusmsg": "exception app version invalid"
	    }
	}
	```

	
### **8. 获取国鼎token:**

* url: https://**server_addr**/vssq/api/v1.1/GetAuthToken
* http请求头部添加: Authorization: Basic MTUwMTEzMjkwNTU6MTExMTEx(此处为base64编码数据，数据内容为(token值:""))
* method: POST
*  请求消息示例:

	```
	{
		"imei": "123456789012345",
		"app_version": "1.0.6",
		"phone_num": "15011329055"
 	}
	```
	
	##### 参数说明:
	```
	app_version: 框架版本名称，
	imei: 用户唯一设备标识，imei,
	phone_num: 用户电话号码
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	    "body": {
	        "token": "eyJleHAiOjE0ODM2OTg3NTgsImlhdCI6MTQ4MzY5NTE1OCwiYWxnIjoiSFMyNTYifQ.eyJpZCI6MX0.rlZ65MRSSxHPJ54xyMMqDe0vs1QGpeDNbmwyozZTW_g" //验证令牌
	        "current_time": "2016-04-20 14:25:38",
	        "expiration": "3600" //过期时间s
	    },
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}
	```
	##### 参数说明:
	```
	token: 验证令牌，客户端需要保存，请求其它接口需要验证此参数，注意过期时间，过期需要重新请求
	expiration: 令牌有效期,单位s
	current_time: 服务器当前时间
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 用户不存在, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000018",
	        "statusmsg": "user not exist"
	    }
	}
	```
	##### fail-6: token认证失败, HTTP状态码为401
	```
	HTTP/1.0 401 UNAUTHORIZED
	WWW-Authenticate: Basic realm="Authentication Required"	```


### **10. banner展示数和点击量统计:**

* url: https://**server_addr**/vssq/api/v1.1/GetBanneradsStatistics
* method: POST
*  请求消息示例:

	```
	{
	      "imei": "395125050989799",
	      "app_version": "1.0.6",
	      "ad_info":[
	                {'ad_id': 2, 'type': 0},
	                {'ad_id': 2, 'type': 1}
	                ]
	}
	```
	
	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	ad_info: 统计的广告
   ad_id: banner广告id
   type:操作类型   0 展示  1 点击
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	    "body": {
	        "status": 0
	    },
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}	
	```
	##### 参数说明:
	```
	status: 0 广告id都存在, 1 部分广告id不存在
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 内部错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000016",
	        "statusmsg": "internal error"
	    }
	}
	```
	
### **11. 统计开屏展示数和点击量和真实点击:**

* url: https://**server_addr**/vssq/api/v1.1/GetOpenScreenAdsStatistics
* method: POST
*  请求消息示例:

	```
	{
	      "imei": "395125050989799",
	      "app_version": "1.0.6",
	      "ad_info":[
	                {'ad_id': 2, 'type': 0},
	                {'ad_id': 2, 'type': 1}
	                ]
	}
	```
	
	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	ad_info: 统计的广告
   ad_id: 开屏广告id
   type:操作类型   0 展示  1 点击 2 真实点击
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	    "body": {
	        "status": 0
	    },
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}	
	```
	##### 参数说明:
	```
	status: 0 广告id都存在, 1 部分广告id不存在
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 内部错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000016",
	        "statusmsg": "internal error"
	    }
	}
	```
	
### **12. 上传客户端用户行为数据:**

* url: https://**server_addr**/vssq/api/v1.1/UploadStatistics
* method: POST
*  请求消息示例:

	```
	{
	      "imei": "395125050989799",
	      "app_version": "1.0.6",
	      "statistics": {
	            "deviceid": "111111111",
	            "accountid": "00000000000000",
	            "date": "1501429445000",
	            "os_info": {
	                "os_version": "6.0.1",
	                "os": "Nexus 5",
	                "mac": "cc:fa:00:c6:ca:01",
	                "device_id": "353490061934887"
	            },
	            "versioncode": "1.1.7",
	            "channel": "godinsec",
	            "resolution": "1776*1080",
	            "access": "wifi",
	            "ip": "103.36.220.98",
	            "cpu": "ARMv7 Processor rev 0 (v7l)",
	            "operators": "46000***",
	            "network_type": "mobile",
	            "subtype": "LTE",
	            "version": 1,
	            "data": [
	                {
	                    "serial_number": 100,
	                    "package_name": "com.tencent.mm",
	                    "pagename": "com.***.activity",
	                    "starttime": "1501429444517",
	                    "endtime": "1501429445517"
	                },
	                {
	                    "serial_number": 200,
	                    "package_name": "com.tencent.qq",
	                    "pagename": "com.***.activity",
	                    "starttime": "1501429411111",
	                    "endtime": "1501429445517"
	                }
	            ]
	        }
	}
	```
	
	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	statistics: 统计数据
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}	
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 上传数据失败， 服务器忙导致, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000041",
	        "statusmsg": "The system is busy. Please repeat later"
	    }
	}
	```
	
### **13. 获取用户VIP状态信息:**

* url: https://**server_addr**/vssq/api/v1.1/GetUserVipStatus
* method: POST
*  请求消息示例:

	```
	{
	    "imei": "395125050989799",
	    "app_version": "1.0.6",
	    "godin_id": "0c8350eca41fc087ea4c4cb4fdbe24fe"
	}
	```
	
	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	godin_id: 用户的国鼎ID
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
        "body": {
            "activate": 0,
            "grade": 1,
            "remain_days": 9,
            "second_remain_day": -1,
            "second_valid_time": "",
            "valid_time": "2019-06-29 17:35:22"
        },
        "head": {
            "statuscode": "000000",
            "statusmsg": "success"
        }
    }	
	```
	##### 参数说明:
	```
	remain_days: 最高等级的会员剩余天数，int型，剩余天数为正，表示会员有效，剩余天数为0或者负数，表示已过期。
	valid_time: 最高等级会员到期时间， 日期格式参见相应消息示例
	activate: 是否有需要激活手动添加的vip    1 有  0 没有
	grade:  0 不是会员 1 黄金会员 2 铂金会员
	second_remain_day：次高等级的会员剩余天数，int型，剩余天数为正，表示会员有效，剩余天数为0或者负数，表示已过期。
	second_valid_time: 最高等级会员到期时间， 日期格式参见相应消息示例
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 用户不是VIP, HTTP状态码为200
	```
	{
	    "body": {
	        "grade": 0
            "activate": 0
        },
	    "head": {
	        "statuscode": "000029",
	        "statusmsg": "user is not vip"
	    }
	}
	```
	##### fail-6: token认证失败, HTTP状态码为401
	```
	HTTP/1.0 401 UNAUTHORIZED
	WWW-Authenticate: Basic realm="Authentication Required"	```

### **14. 获取用户VIP商品订单:**

* url: https://**server_addr**/vssq/api/v1.1/GetUserVipOrder
* http请求头部添加: Authorization: Basic MTUwMTEzMjkwNTU6MTExMTEx(此处为base64编码数据，数据内容为(token值:""))
* method: POST
*  请求消息示例:

	```
	{
	    "imei": "395125050989799",
	    "app_version": "1.0.6",
	    "godin_id": "0c8350eca41fc087ea4c4cb4fdbe24fe"
	}
	```
	
	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	godin_id: 用户的国鼎ID
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	    "body": {
	        "ware_order": [
	            {
	                "category": 0,
	                "discount": 0.8,
	                "discount_price": 97,
	                "end_time": "2017-10-08 16:20:33",
	                "order_number": "vip20170908162033nvz3CrOt2Z7XKiL",
	                "pay_time": "2017-09-08 16:21:34",
	                "start_time": "2017-09-08 16:20:34",
	                "ware_price": 121,
	                "ware_status": 1,
                    "type_name": "\u6708\u5361",
	                "buy_category": 2
	            },
	            {
	                "category": 0,
	                "discount": 0.8,
	                "discount_price": 400,
	                "end_time": "2017-07-04 16:20:34",
	                "order_number": "vip20170908162154I9hHvizCjcoBUy0",
	                "pay_time": "2017-06-04 16:36:25",
	                "start_time": "2017-06-04 16:20:34",
	                "ware_price": 500,
	                "ware_status": 0,
                    "type_name": "\u6708\u5361",
	                "buy_category": 2
	            },
	            {
	                "category": 1,
	                "discount": 0.75,
	                "discount_price": 1125,
	                "end_time": "2018-01-08 16:20:34",
	                "order_number": "vip20170908162233tY2yZk09oClRNag",
	                "pay_time": "2017-09-08 16:36:20",
	                "start_time": "2017-10-08 16:20:34",
	                "ware_price": 1500,
	                "ware_status": 2,
                    "type_name": "\u6708\u5361",
	                "buy_category": 0
	            }
	        ]
	    },
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}	
	```
	##### 参数说明:
	```
	ware_order: 用户订单列表列表， 是一个list
	每个商品字段意义如下：
	category: 商品类型， int型， 0 代表黄金， 1 代表铂金
	discount: 折扣， float类型
	discount_price： 商品折扣后价格，单位为分
	ware_price: 商品标价， 整形，单位为分
	pay_time: 订单支付时间
	start_time: 会员订单有效期起始时间
	end_time: 会员订单有效期结束时间
	ware_status: 商品是否使用，int型， 0：已过期，1：使用中，2：未使用
	buy_category: 订单生成方式  0 付费, 1 活动, 2 手动添加, 3 其他
    type_name: 当前类型的名称, 如 月卡, 季卡
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: token认证失败, HTTP状态码为401
	```
	HTTP/1.0 401 UNAUTHORIZED
	WWW-Authenticate: Basic realm="Authentication Required"	```

### **15. 购买VIP商品:**

* url: https://**server_addr**/vssq/api/v1.1/BuyVipWare
* http请求头部添加: Authorization: Basic MTUwMTEzMjkwNTU6MTExMTEx(此处为base64编码数据，数据内容为(token值:""))
* method: POST
*  请求消息示例:

	```
	{
	    "imei": "395125050989799",
	    "app_version": "1.0.6",
	    "godin_id": "0c8350eca41fc087ea4c4cb4fdbe24fe",
	    "ware_id": "10001"
	}
	```
	
	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	godin_id: 用户的国鼎ID
	ware_id: VIP 商品编号
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	     "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	     },
	     "body:" {
	        "appid": "wx643b87be508f1eaa",
	        "noncestr": "gTr6Pdv251c8LNiuOkpqxRYQ0hAXG9wH",
	        "package": "Sign=WXPay",
	        "partnerid": "1424058002",
	        "prepayid": "wx2017030115342949a37158c60913162114",
	        "sign": "60FEAC74E49D7435741FF6311D2A054C",
	        "timestamp": "1488353669"
	        "order_number": "HJHQJGLTQBYRYJRVPS20170215151210",
	        "price": 400
	     }
	}
	```
	##### 参数说明:
	```
	字段为调起微信支付客户端所需要的参数
	appid: 微信支付账号的应用id
	noncestr: 随机字符串
	package: 该字段固定使用"Sign=WXPay"
	partnerid: 商户号
	prepayid: 预支付编号
	sign: 签名
	timestamp: 时间戳
	order_number: 订单号
	price: 商品的价格，单位为分
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 内部错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000016",
	        "statusmsg": "internal error"
	    }
	}
	```
	##### fail-6: 订单过期, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000032",
	        "statusmsg": "order expired"
	    }
	}
	```
	##### fail-7: 订单非法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000031",
	        "statusmsg": "order invalid"
	    }
	}
	```
	##### fail-8: token认证失败, HTTP状态码为401
	```
	HTTP/1.0 401 UNAUTHORIZED
	WWW-Authenticate: Basic realm="Authentication Required"	```
	
### **16. 获取指定VIP订单状态:**

* url: https://**server_addr**/vssq/api/v1.1/GetVipOrdersStatus
* http请求头部添加: Authorization: Basic MTUwMTEzMjkwNTU6MTExMTEx(此处为base64编码数据，数据内容为(token值:""))
* method: POST
*  请求消息示例:

	```
	{
	    "imei": "395125050989799",
	    "app_version": "1.0.6",
	    "godin_id": "0c8350eca41fc087ea4c4cb4fdbe24fe",
	    "order_nums": ['vip2017090815573101jptoQBX6wylab', 'vip201709081557317G6HVRIeM2CU0JF']
	}
	```
	
	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	godin_id: 用户的国鼎ID
	order_nums: 订单号数组
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	    "body": [
	        {
	            "order_num": "vip2017090815573101jptoQBX6wylab",
	            "status": 0
	        },
	        {
	            "order_num": "vip201709081557317G6HVRIeM2CU0JF",
	            "status": 0
	        }
	    ],
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}
	```
	##### 参数说明:
	```
	消息体为一个list，每个元素包含以下字段
	order_num: 客户查询的订单号
	status: 订单的状态， 0 未支付， 1 已支付
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: token认证失败, HTTP状态码为401
	```
	HTTP/1.0 401 UNAUTHORIZED
	WWW-Authenticate: Basic realm="Authentication Required"	```
	

### **17. 开屏广告第三方数据对比统计:**

* url: https://**server_addr**/vssq/api/v1.1/OpenScreenAdsData
* method: POST
*  请求消息示例:

	```
	{
	    "imei": "123456789012345",
	    "app_version": "1.0.6",
        "type": 0,
        "ad_id": 1
	}
	```

	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
    type: 0 进入次数 1 获取次数
    ad_id: 广告id
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
    {
        "head": {
            "statuscode": "000000",
            "statusmsg": "success"
        }
    }
	```
	##### 参数说明:
	```
    无
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 广告不存在, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000026",
	        "statusmsg": "open screen ads not exist"
	    }
	}
	```
	##### fail-6: 内部错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000016",
	        "statusmsg": "internal error"
	    }
	}
	```

### **18. 获取互动广告信息:**

* url: https://**server_addr**/vssq/api/v1.1/GetInteractiveAds
* method: POST
*  请求消息示例:

	```
	{
	      "imei": "395125050989799",
	      "app_version": "1.0.6",
          "channel": "huawei"
	}
	```

	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
    channel: 应用渠道
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
    {
        "body": [
            {
                "ad_id": 1,
                "icon": "http://127.0.0.1/AvatarPhoto/InteractiveAds/0459155433732d1b2529d94902c3f95294b4391b5_1507972155.jpg",
                "name": "\u5feb\u773c",
                "position": 2,
                "source": 0,
                "refresh_time": "00:00~00:00",
                "refresh_count": 0,
                "third_link": "http://127.0.0.1:9010/1"
            },
            {
                "ad_id": 2,
                "icon": "",
                "name": "ddd",
                "position": 0,
                "source": 0,
                "refresh_time": "08:00~13:00",
                "refresh_count": 1,
                "third_link": ""
            }
        ],
        "head": {
            "statuscode": "000000",
            "statusmsg": "success"
        }
    }
	```
	##### 参数说明:
	```
	body 字段在有数据时返回，为一个数组。 无数据没有此字段

	ad_id: 广告id
	name: 广告名称
	source: 广告来源  0: '互动广告'
	position: 广告位置 0: '主界面', 1: '社交频道', 3: '百宝箱'
	icon: 广告图
    third_link: 打开链接, 不存在时此值是空字符串, 目前只有广告的链接可以直接使用
    refresh_time: 广告刷新时间段， 本时间段内客户端随即刷新
    refresh_count: 当前用户刷新次数
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```

### **19. 统计互动广告展示数和点击量:**

* url: https://**server_addr**/vssq/api/v1.1/InteractiveAds
* method: POST
*  请求消息示例:

	```
	{
	      "imei": "395125050989799",
	      "app_version": "1.0.6",
	      "ad_info":[
	                {'ad_id': 2, 'type': 0},
	                {'ad_id': 2, 'type': 1}
	                ]
	}
	```

	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	ad_info: 统计的广告
    ad_id: 互动广告id
    type:操作类型   0 展示  1 点击
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
	{
	    "body": {
	        "status": 0
	    },
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}
	```
	##### 参数说明:
	```
	status: 0 广告id都存在, 1 部分广告id不存在
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 内部错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000016",
	        "statusmsg": "internal error"
	    }
	}
	```

### **20. 获取变现猫免登录信息:**

* url: https://**server_addr**/vssq/api/v1.1/GetLink
* method: POST
*  请求消息示例:

	```
	{
	      "imei": "395125050989799",
	      "app_version": "1.0.6",
          "ad_id": 2
	}
	```

	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
    ad_id: 广告id
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
    {
        "body": {
            "icon_link": "http://bookopen.bianxianmao.com/redirect.htm?timestamp=1508228322630&appUid=123456789012345&appKey=58f02938a31d4210be8ae35a870f2d3a&sign=cc0759b842dbf87ccdea21d44d63dce9&appType=app"
        },
        "head": {
            "statuscode": "000000",
            "statusmsg": "success"
        }
    }
	```
	##### 参数说明:
	```
    主要涉及到：福利社, 小说阅读, 视频直播
    icon_link: 变现猫免登录URL, 不存在时此值是空字符串
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```

###  **21.特定开屏广告统计:**

* url: https://**server_addr**/vssq/api/v1.1/Specificads
* method: POST
*  请求消息示例:

	```
	{
	      "imei": "395125050989799",
	      "app_version": "1.0.6",
	      "number": 20170724001,
	      "type": 1
	}
	```
	
	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	number: 广告编号
	type: 统计类型 0 展示数, 1 点击数, 2 自然点击数
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}	
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	```
    {
        "message": {
            "imei": "param missing"
        }
    }
    ```
	##### fail-2: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-3: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-4: 开屏广告不存在, HTTP状态码为200
	```
	{
        "head": {
            "statuscode": "000026",
            "statusmsg": "open screen ads not exist"
        }
    }
	```
	##### fail-5: 内部错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000016",
	        "statusmsg": "internal error"
	    }
	}
	```

### **22. 获取banner广告信息:**

* url: https://**server_addr**/vssq/api/v1.1/GetBannerads
* method: POST
*  请求消息示例:

	```
	{
	      "imei": "395125050989799",
	      "app_version": "1.0.6",
          "channel": "godinsec"
	}
	```

	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
    channel: 应用渠道
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
	{
	    "body": [
	        {
	            "ad_id": 1,
	            "carousel": 1,
	            "carousel_interval": 2,
	            "display_number": 1,
	            "end_time": "2017-07-11 16: 38: 15",
	            "icon": "http://10.0.5.10/AvatarPhoto/bannerads/15.jpg",
	            "icon_dest_link": "",
	            "name": "ad",
	            "ad_number": "BANNER1500291792",
	            "position": 0,
	            "source": 0,
                "refresh_count": 1,
                "refresh_time": "12:00~18:00",
	            "start_time": "2017-06-26 16: 38: 21"
	        },
	        {
	            "ad_id": 2,
	            "carousel": 1,
	            "carousel_interval": 3,
	            "display_number": 2,
	            "end_time": "2017-08-04 11: 40: 01",
	            "icon": "http://10.0.5.10/AvatarPhoto/bannerads/13_1.jpg",
	            "icon_dest_link": "http://www.baidu.com",
	            "name": "111",
	            "ad_number": "BANNER1500291790",
	            "position": 3,
	            "source": 1,
                "refresh_count": 0,
                "refresh_time": "12:00~18:00",
	            "start_time": "2017-06-26 11: 39: 58"
	        }
	    ],
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}
	```
	##### 参数说明:
	```
	ad_id: 广告id
	carousel: 0 不轮播, 1 轮播
	carousel_interval: 轮播间隔时间秒
	display_number: 广告每天每人的展示数
	end_time: 合作结束时间
	icon: 广告图标
	icon_dest_link: 广告图标链接地址
	name: 广告名称
	position: # 位置 0 优化加速, 1 主桌面, 2 倒三角页面
	source: 0 自有广告 1 外接广告
	start_time: 合作开始时间
	ad_number: 广告编号
    refresh_count: 刷新广告次数
    refresh_time: 刷新广告时间段, 客户端在该时间段内随即访问
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 内部错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000016",
	        "statusmsg": "internal error"
	    }
	}
	```

### **23. 获取开屏广告信息:**

* url: https://**server_addr**/vssq/api/v1.1/GetOpenads
* method: POST
*  请求消息示例:

	```
	{
	      "imei": "395125050989799",
	      "app_version": "1.0.6",
          "channel": "huwawei"
	}
	```

	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
    channel: 应用渠道
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
	{
	    "body": [
	        {
	            "ad_id": 1,
	            "display_number": 3,
	            "end_time": "2017-07-19 17:05:23",
	            "icon": "http://127.0.0.1/AvatarPhoto/OpenScrrenAdsIcon/test_1499677533.jpg",
	            "name": "首页",
	            "ad_number": "OPENSCREEN1500291507",
	            "position": 0,
	            "skip_time": 3,
	            "source": 0,
	            "skip_count": 0,
                "refresh_time": "00:00~00:00",
                "refresh_count": 0
	            "sort": 100,
                "app_link":'',
	            "start_time": "2017-07-10 17:05:22"
	        },
	        {
	            "ad_id": 2,
	            "display_number": 3,
	            "end_time": "2017-07-25 14:37:55",
	            "icon": "http://127.0.0.1/AvatarPhoto/OpenScrrenAdsIcon/fire03_1499755085.png",
	            "name": "new",
	            "ad_number": "OPENSCREEN1500291505",
	            "position": 0,
	            "skip_time": 3,
	            "skip_count": 2,
                "refresh_time": "08:00~13:00",
                "refresh_count": 2
	            "source": 0,
	            "sort": 1000,
                "app_link": "http://apk.bjzqb.com/chess_10370.apk",
	            "start_time": "2017-07-11 14:37:54"
	        },
	        {
	            "ad_id": 3,
	            "display_number": 3,
	            "end_time": "2017-07-12 11:44:00",
	            "icon": "http://127.0.0.1/AvatarPhoto/OpenScrrenAdsIcon/qr_code_product_1499831056.png",
	            "name": "小花秀",
	            "ad_number": "OPENSCREEN1500291504",
	            "position": 1,
	            "skip_time": 3,
	            "skip_count": 3,
	            "source": 1,
	            "sort": 128,
                "refresh_time": "00:00~00:00",
                "refresh_count": 0
                "app_link":'',
	            "start_time": "2017-07-12 11:43:59"
	        }
	    ],
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}
	```
	##### 参数说明:
	```
	body 字段在有数据时返回，为一个数组。 无数据没有此字段

	ad_id: 广告id
	name: 广告名称
	source: 广告来源  0: '自有广告', 1: '外接SDK'
	position: 广告位置 0: '开屏首页', 1: '应用启动页', 2: '应用更新'
	display_number: 广告每天每人的展示数
	skip_time： 跳过时间
	start_time: 合作开始时间
	end_time: 合作结束时间
	icon: 广告图
	ad_number: 广告编号
	skip_count: 主要控制点击跳过 0 跳过广告，直接进入应用, 其它值如2则有两次点击进入广告，次数超过后进入应用
	sort: 返回排序的数字,此数字是单价转化分后的整数
    app_link: 应用下载链接, 不存在时此值是空字符串
    refresh_time: 广告刷新时间段， 本时间段内客户端随即刷新
    refresh_count: 当前用户刷新次数
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 内部错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000016",
	        "statusmsg": "internal error"
	    }
	}
	```

### **24. 获取默认广告图:**

* url: https://**server_addr**/vssq/api/v1.1/GetAdsIcon
* method: POST
*  请求消息示例:
    ```
	{
	    "imei": "395125050989799",
	    "app_version": "1.0.6"
	}
	```
	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	```
    {
        "body": {
            "ads_icon": [
                {
                    "icon_link": "http://127.0.0.1/AvatarPhoto/AdsIcon/new02_1510659489.png",
                    "jump_link": "http://112.126.81.177",
                    "position": 0
                },
                {
                    "icon_link": "http://127.0.0.1/AvatarPhoto/AdsIcon/qr_code_test_1510659681.png",
                    "jump_link": "",
                    "position": 1
                }
            ],
            "ads_strategy": 3
        },
        "head": {
            "statuscode": "000000",
            "statusmsg": "success"
        }
    }
	```
	##### 参数说明:
	```
	body: body无数据返回空数组
	icon_link: 默认广告图
	jump_link: 图片跳转链接
	position: 默认广告图位置 1 第三方应用开屏, 2 Banner游戏乐园, 3 Banner社交频道, 4 Banner备忘录, 5 Banner密友, 6 Banner微信伪装, 7 Banner优化加速
    ads_strategy: 广告展示策略，eg: 3代表每3次展示一次广告
	```
    
	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}

	
### **25. 获取VIP服务协议:**

* url: https://**server_addr**/vssq/api/v1.1/VipServiceProtocol
* http请求头部添加: Authorization: Basic MTUwMTEzMjkwNTU6MTExMTEx(此处为base64编码数据，数据内容为(token值:""))

* method: POST
*  请求消息示例:

	```
	{
	    "imei": "395125050989799",
	    "app_version": "1.0.6"
	}
	```
	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	```
	{
	    "body": {
        "content": "\u662f\u5927\u5927\u5927\u4ed8\u4ed8\u4ed8\u4ed8\u591a\u591a\u6240\u6240\u6240\u6240"
        },
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}
	```
	##### 参数说明:
	```
	content: 服务协议内容
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: token认证失败, HTTP状态码为401
	```
	HTTP/1.0 401 UNAUTHORIZED
	WWW-Authenticate: Basic realm="Authentication Required"	```
	```
	##### fail-6: 没有vip服务协议内容, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000033",
	        "statusmsg": "vip not service protocol"
	    }
	}
	```
	
### **25. 激活手动添加VIP用户:**

* url: https://**server_addr**/vssq/api/v1.1/ActivateVipMember
* http请求头部添加: Authorization: Basic MTUwMTEzMjkwNTU6MTExMTEx(此处为base64编码数据，数据内容为(token值:""))
* method: POST
*  请求消息示例:

	```
	{
	    "imei": "395125050989799",
	    "app_version": "1.0.6",
	    "godin_id": '18835d61df97bdb626705f2'
	}
	```
	
	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	godin_id: 用户的国鼎ID
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}
    ```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: token认证失败, HTTP状态码为401
	```
	HTTP/1.0 401 UNAUTHORIZED
	WWW-Authenticate: Basic realm="Authentication Required"	```
	```
	##### fail-6: 会员商品不存在, HTTP状态码为200
	```
	{
	    "head": {
            "statuscode": "000020",
            "statusmsg": "ware not exist"
        }
	}

### **26. 按渠道获取VIP商品:**

* url: https://**server_addr**/vssq/api/v1.1/GetChannelVipWare
* method: POST
*  请求消息示例:

	```
	{
	    "imei": "395125050989799",
	    "app_version": "1.0.6",
	    "channel": 'huawei'
	    "status": '0'
	    "godin_id": "4c59396301ab6274bd7892f0b31df36e"
	}
	```
	
	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	channel: 商品渠道
	status: '0' 表示查询黄金会员, '1' 表示查询铂金会员
	godin_id: 用户的国鼎ID
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	     "body": {
            "ware_list": [
                {
                    "category": 0,
                    "channel": "huawei",
                    "days": 30,
                    "description": "\u5c11\u65f6\u8bf5\u8bd7\u4e66",
                    "discount": 0.8,
                    "discount_price": 800.0,
                    "id": "16",
                    "name": "\u534e\u4e3a\u6708\u5361",
                    "price": 1000,
                    "priority": 0,
                    "picture": ""
                },
                {
                    "category": 1,
                    "channel": "moren",
                    "days": 120,
                    "description": "\u4f1a\u5458\u5b63\u4f1a\u5458\u5b63",
                    "discount": 0.5,
                    "discount_price": 500.0,
                    "id": "12",
                    "name": "\u4f1a\u5458\u5b63",
                    "price": 1000,
                    "priority": 1,
                    "picture": ""
                },
                {
                    "category": 2,
                    "channel": "moren",
                    "days": 180,
                    "description": "\u4f1a\u5458\u534a\u5e74\u5361\u4f1a\u5458\u534a\u5e74",
                    "discount": 0.7,
                    "discount_price": 700.0,
                    "id": "13",
                    "name": "\u4f1a\u5458\u534a\u5e74\u5361",
                    "price": 1000,
                    "priority": 0,
                    "picture": "http://10.0.5.10/AvatarPhoto/vip_ware/22.png"
                }
        ]
    },
    "head": {
        "statuscode": "000000",
        "statusmsg": "success"
    }
	}
	```
	##### 参数说明:
	```
	category: 商品分类
	channel: 商品渠道
	days: 商品有效天数
	description: 商品描述
	discount: 商品折扣
	discount_price: 折扣后价格
	id: 商品编号
	name: 商品名称
	price: 商品价格
	priority: 是否推荐 0 普通, 1 推荐
	picture: 会员推荐图标  
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: token认证失败, HTTP状态码为401
	```
	HTTP/1.0 401 UNAUTHORIZED
	WWW-Authenticate: Basic realm="Authentication Required"	```
	```
### **28. 获取微信特征文件:**

* url: https://**server_addr**/vssq/api/v1.1/GetWeChatFeature
* method: POST
*  请求消息示例:

	```
	{
		"imei": "123456789012345",
		"app_version": "1.0.6",
		"frame_version_code": "1"
		"wechat_version": "6.5.4"
    }
	```

	##### 参数说明:
	```
	app_version: 框架版本名称，
	imei: 用户唯一设备标识，imei,
	frame_version_code: 框架版本号
	wechat_version: 微信版本号
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
	{
	    "body": {
	        "url": "http://server_addr/AvatarApk/WeChatFeature/WeChatFeature_6.5.4.json"
	    },
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 已经是最新版本, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000007",
	        "statusmsg": "already last version"
	    }
	}
	```

### **29. 获取交流群信息:**

* url: https://**server_addr**/vssq/api/v1.1/GetGroup
* method: POST
*  请求消息示例:

	```
	{
	    "imei": "123456789012345",
	    "app_version": "1.0.6"
	}
	```
	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本

	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
    {
        "body": {
            "group_info": [
                {
                    "group_key": "ssa",
                    "group_number": "sss",
                    "type": 0
                },
                {
                    "group_key": "ssssssss",
                    "group_number": "sssssss",
                    "type": 1
                }
            ]
        },
        "head": {
            "statuscode": "000000",
            "statusmsg": "success"
        }
    }
	```
	##### 参数说明:
	```
    当数据库无信息时只返回head
	body:
	group_number: 群号
	group_key: 群key
	type: 0 微商神器交流群, 其它交流取后续支持
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```

### **30. 获取微信特征文件:**

* url: https://**server_addr**/api/v1.1/Feature
* method: POST
*  请求消息示例:

	```
	{
		"imei": "123456789012345",
		"app_version": "1.0.6",
		"frame_version_code": "1",
		"version": "6.5.4",
        "version_code": 1
	}
	```

	##### 参数说明:
	```
	    app_version: 框架版本名称，
	    imei: 用户唯一设备标识，imei,
	    frame_version_code: 框架版本号
        version: 微信版本名称
        version_code: 微信特征文件递增版本号
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
	{
	    "body": {
	        "url": "http://server_addr/AvatarApk/WeChatFeature/Feature_6.5.4.jar",
            "version_code": 2
	    },
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}
	```

	##### 参数说明:
	```
        url: 最新下载地址
        version_code: 最新递增版本号
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 已经是最新版本, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000007",
	        "statusmsg": "already last version"
	    }
	}
	```
	##### fail-6: 不支持该版本, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000043",
            "statusmsg": "version code is not supported"
	    }
	}
	```
	
### **31. 判断是否进去填写授权码页面:**

* url: https://**server_addr**/api/v1.1/JudgeAddKey?num=123&imei=862534031404101&app_version=1.0.6
* method: Get
*  请求消息示例:

	```
	{
		"imei": "862534031404101",
        "app_version": "1.0.6",
        "num": "123"
	}
	```

	##### 参数说明:
	```
	    app_version: 框架版本名称，
	    imei: 用户唯一设备标识，imei,
	    num: 前端传入的字符串
	```
	#### 响应消息及错误码:
	##### success 不需要进入授权码页面, HTTP状态码为200:

	```
	{
	    "body": {"num": "123"}
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}
	```

	##### 参数说明:
	```
        num: 前端传入的字符串
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 需要进入填写邀请码页面, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000040",
	        "statusmsg": "enter page"
	    }
	}
	```
	
### **32. 检查是否可用激活授权码:**

* url: https://**server_addr**/api/v1.1/CheckKey
* method: POST
*  请求消息示例:

	```
	{
		"imei": "861504034843978",
        "app_version": "1.0.6",
        "key_id": "key1529571617747rSwp"
	}
	```

	##### 参数说明:
	```
	    app_version: 框架版本名称，
	    imei: 用户唯一设备标识，imei,
	    key_id: 授权码
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
	{
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}

	```
	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 授权码无效, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000036",
            "statusmsg": "key invalid"
	    }
	}
	```
	##### fail-6: imei已经绑定激活状态中的授权码,不能再次绑定新的授权码, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000042",
            "statusmsg": "imei has key, can not binding new key"
	    }
	}
	```
	
### **33. 购买key:**

* url: https://**server_addr**/api/v1.1/Buykey
* method: POST
*  请求消息示例:

	```
	{
		"imei": "861504034843978",
        "app_version": "1.0.6",
        "channel": "vssq"
	}
	```

	##### 参数说明:
	```
	    app_version: 框架版本名称，
	    imei: 用户唯一设备标识，imei
	    channel: 渠道
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
	{
        "body": {
            "appid": "wx7a54c43b8eb67489",
            "noncestr": "jnwDd8Ivh9iH4qXm7fEoCNc2JFKBRzO5",
            "order_number": "key20180623160444fO4RiZUMIw9bFeq",
            "package": "Sign=WXPay",
            "partnerid": "1492581822",
            "prepayid": "wx231605408546592f5ce7f5a33617921943",
            "price": 29900,
            "sign": "2B33E3098ABC81422AE745B995E0BE73",
            "timestamp": "1529741085"
        },
        "head": {
            "statuscode": "000000",
            "statusmsg": "success"
        }
    }
	```
	##### 参数说明:
	```
        字段为调起微信支付客户端所需要的参数
        appid: 微信支付账号的应用id
        noncestr: 随机字符串
        package: 该字段固定使用"Sign=WXPay"
        partnerid: 商户号
        prepayid: 预支付编号
        sign: 签名
        timestamp: 时间戳
        order_number: 订单号
        price: 商品的价格，单位为分
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 有可用授权码，不能再次购买, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000037",
            "statusmsg": "key is exist"
	    }
	}
	```
	
### **34. key订单查询:**

* url: https://**server_addr**/vssq/wxpay/OrderQuery
* method: POST
*  请求消息示例:

	```
	{
	      "imei": "395125050989799",
	      "app_version": "1.0.6",
          "out_trade_no": 'DSDSDSDSDSD'
	}
	```

	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	out_trade_no: 订单号
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
	{
        "body": {
                "key_id": "key2222222222222dddd"
        },
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 订单支付失败, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000038",
	        "statusmsg": "pay failure"
	    }
	}
	```

### **35. X分身框架更新:**	

* url: https://**server_addr**/vssq/api/v1.1/ChannelFrameUpdate
* method: POST
*  请求消息示例:

	```
	{
		"app_version": "1.0.1",
		"imei": "123456789012345",  
		"frames": [{'number': 1, 'version_code': 1}],
		"channel": 'gind'
	}
	```
	
	##### 参数说明:
	```
	app_version: 应用版本
	imei: 用户唯一设备标识，imei
	frames: number 框架编号, version_code 版本号
	channel: 渠道
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	    "body": [
            {
                "number": 1,
                "package_name": "com.godinsec.godinsec_private_space01",
                "status": 1,
                "c_status": 1
            }
        ],
        "head": {
            "statuscode": "000000",
            "statusmsg": "success"
        }
	}
	```
	##### 参数说明:
 	```
	number: 编号
	package_name: 包名
	status: 0 普通更新 1 强制更新
	c_status: 0 普通更新 1 强制更新 (以后不使用)
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 已经是最新版本, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000007",
	        "statusmsg": "already last version"
	    }
	}
	```
	##### fail-6: app_type错误，对应的app不存在, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000008",
	        "statusmsg": "app not exists"
	    }
	}
	```
	##### fail-7: 推广渠道不存在, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000039",
	        "statusmsg": "channel speard manage not exist"
	    }
	}
	```
	
### **36. 插件更新:**	

* url: https://**server_addr**/vssq/api/v1.1/ChannelPluginUpdate
* method: POST
*  请求消息示例:

	```
	{
		"frame_version_code": "1",
		"imei": "123456789012345",
		"app_version": "1.0.6",
		"plugins": [
			{"package_name": "com.godinsec.launcher", "version_code": "1"}, 
			{"package_name": "com.godinsec.settings", "version_code": "5"}
			]，
		"channel": 'gind'
	}
	```
	
	##### 参数说明:
	```
	app_version: 应用版本
	imei: 用户唯一设备标识，imei
	frame_version_code: 框架版本号
	plugins: 插件的报名及版本号列表
    channel: 渠道
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	    "body": {
	        "url": [
            "//data//66.3.apk"
        	]
	    },
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}
	```
	##### 参数说明:
 	```
	url: 新版本插件的下载地址列表
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 已经是最新版本, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000007",
	        "statusmsg": "already last version"
	    }
	}
	```
	##### fail-6: 推广渠道不存在, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000039",
	        "statusmsg": "channel speard manage not exist"
	    }
	}
	```

### **37. 按渠道制作分身:**

* url: https://**server_addr**/api/v1.1/AvatarChannelAppUrl
   
* method: POST
*  请求消息示例:
 
	```
	{
	    "imei": "123456789012345",
        "app_version": "1.0.6",
        "version_code": 5,
        "number": 5,
        "app_name": 'fs4,
        "channel": 'gind'
    }
	```
	
	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	version_code: 版本号
	number: 编号
	app_name: 应用名称
	channel: 渠道
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	   "body": {
            "down_addr": "http://127.0.0.1/WeApk/WeXavtar/5/20171122022741/we_xavatar5.apk"
            },
        "head": {
            "statuscode": "000000",
            "statusmsg": "success"
        }
	}
	```
	##### 参数说明:
	```
	down_url: 下载地址
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 分身基础版不存在, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000034",
            "statusmsg": "avatar version not exist"
	    }
	}
	```
	##### fail-6: 推广渠道不存在, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000039",
	        "statusmsg": "channel speard manage not exist"
	    }
	}
	```
	
### **38. 微商神器检查更新:**	

* url: https://**server_addr**/vssq/api/v1.1/ChannelAppUpdate
* method: POST
*  请求消息示例:

	```
	{
		"app_type": "8",
		"app_version": "1.0.1",
		"imei": "123456789012345",  
		"version_code": "1",
		"channel": 'godin'
	}
	```
	##### 参数说明:
	```
	app_type: app类型， 必须为8
	app_version: 应用版本
	imei: 用户唯一设备标识，imei
	version_code: 框架版本号
	channel: 渠道
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	```
    {
	    "body": {
	        "update_msg": "this is a new version",
	        "url": "/data/xx.apk",
	        "version_name": "1.0.1",
	        "status": 1
	    },
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}
	```
	##### 参数说明:
 	```
	update_msg: 更新消息内容
	url: 新版本框架的下载地址
	version_name: 版本名称
	status: 0 普通更新 1 强制更新
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 已经是最新版本, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000007",
	        "statusmsg": "already last version"
	    }
	}
	```
	##### fail-6: app_type错误，对应的app不存在, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000008",
	        "statusmsg": "app not exists"
	    }
	}
	```
	##### fail-6: 推广渠道不存在, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000039",
	        "statusmsg": "channel speard manage not exist"
	    }
	}
	```
	
### **39. 根据type获取交流群信息:**

* url: https://**server_addr**/vssq/api/v1.1/GetCommGroup?g_type=1&app_version=1.0.1&imei=123456789012345
* method: GET
*  请求消息示例:

	```
	{
	    "g_type": 1,
        "app_version": "1.0.1",
        "imei": "123456789012345"
	}
	```
	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	g_type: 0 微商神器交流群  1 微商神器交流群

	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
    {
        "body": {
            "group_info": [
                {
                    "group_key": "22",
                    "group_number": "2",
                    "type": 1
                }
            ]
        },
        "head": {
            "statuscode": "000000",
            "statusmsg": "success"
        }
    }
	```
	##### 参数说明:
	```
    当数据库无信息时只返回head
	body:
	group_number: 群号
	group_key: 群key
	type: 0 微商神器交流群 1 微商神器交流群, 其它交流取后续支持
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```

### **40. 获取key渠道信息:**

* url: https://**server_addr**/vssq/api/v1.1/GetCh?channel=huawei&imei=123456789012345&app_version=1.0.1
* method: GET
*  请求消息示例:

	```
	{
	    "channel": "huawei",
        "app_version": "1.0.1",
        "imei": "123456789012345"
	}
	```
	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	channel: 渠道

	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
    {
        "body": {
            "channel": "huawei",
            "msg": "\u4f1a\u54583.5\u5143111",
            "price": 350
        },
        "head": {
            "statuscode": "000000",
            "statusmsg": "success"
        }
    }
	```
	##### 参数说明:
	```
    当数据库无信息时只返回head
	body:
	channel: 渠道
	price: 价铬分
	msg: 说明信息
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	
### **41. 获取活动信息:**

* url: https://**server_addr**/vssq/api/v1.1/GetActivity?app_version=1.0.6&godin_id=429a2d57e70bb09c2080d7b029ab14dc&imei=123456789012345
* method: GET
*  请求消息示例:

	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
    godin_id: 国鼎id
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
    {
        "body": [
            {
                "activity_id": 2,
                "content": "gfdgdgfdg",
                "icon": "http://127.0.0.1/SuperData/SuperPhoto/activity/15336443385711.png",
                "link": "fgfgfgfgfg",
                "name": "\u6b64\u5361",
                "number": "000003",
                "share_description": "dgfdgfg",
                "share_icon": "http://127.0.0.1/SuperData/SuperPhoto/activity/15337303337722.png",
                "share_link": "fghfghgh",
                "share_title": "fgfgfg"
            }
        ],
        "head": {
            "statuscode": "000000",
            "statusmsg": "success"
        }
    }
	```
	##### 参数说明:
	```
	body 字段在有数据时返回，为一个数组。 无数据没有此字段

	activity_id: 活动id
	name: 活动名称
	number: 活动编号000001 签到领会员 
    content: 备注
	icon: 活动图标
	link: 活动链接
    share_description: 分享描述
    share_icon: 分享图标
    share_link: 分享链接
    share_title: 分享标题
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 用户不存在, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000018",
	        "statusmsg": "user not exist"
	    }
	}
	```
	
### **42. 各种活动功能统一接口:**

* url: server_addr/swsd/api/v1.1/ac_func
* method: POST
*  请求消息示例:
    ```
    json_req = {
            "godin_id": "fa54a842ed1ab94b8334f3c318296e21",
            "imei": "395125050989799",
            "app_version": "1.0.6",
            "activity_id": 1,
            "number": '000003',
            "event": "100004",
            "attach": {}
    }
    ```
    ```
	##### 参数说明:
	imei: 用户唯一设备标识
	app_version: 应用版本
    godin_id: 国鼎id
    activity_id: 活动id   
    number: 活动编号  000003 签到领会员
    event: 事件   100004 签到领会员
    attach: 附加参数  100004 {}
    
    ```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
    {
        "head": {
            "statuscode": "000000",
            "statusmsg": "success"
        },
        "status": 0
    }
	```
    ```
    参数说明
    status: 0 不需要i激活会员， 1 需要激活会员 适用分享和签到活动
    ```
	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 用户不存在, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000018",
	        "statusmsg": "user not exist"
	    }
	}
	```
	##### fail-6: 活动不存在, HTTP状态码为200
	```
	{
	    "head": {
            "statuscode": "000023",
            "statusmsg": "activity not exist"
        }
	}
	```
	##### fail-11: 内部错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000016",
	        "statusmsg": "internal error"
	    }
	}
	```

### **43. 微商客获取key信息:**

* url: https://**server_addr**/vssq/api/v1.1/we_key?we_key_id=2222222222&user_id=15011329055
* method: GET
*  请求消息示例:
	##### 参数说明:
	```
    user_id: 手机号
    we_key_id: key记录id
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
    {
        "body": [
            {
                "key_id": "key1534409074022ECVv",
                "status": 0
            },
            {
                "key_id": "key1534409074023bTNE",
                "status": 0
            },
            {
                "key_id": "key1534409074023fxbR",
                "status": 0
            }
        ],
        "head": {
            "statuscode": "000000",
            "statusmsg": "success"
        }
    }

	```
	##### 参数说明:
	```
	body 字段在有数据时返回，为一个数组。 无数据没有此字段

	key_id: key id
	status: 0 未激活 1 激活
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: 成功, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}
	```

### **44. 微商客制造key:**

* url: https://**server_addr**/vssq/api/v1.1/m_key
* method: POST
*  请求消息示例:
    ```
    {
       "user_id": "15011329055",
       "key_count": 24,
       "ad_time": 3,
       "we_key_id": "2222222222"
    }
    ```

	##### 参数说明:
	```
	ad_time: 免广告时间
	key_count: key数量
    user_id: 手机号
    we_key_id: key记录id
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
    {
        "head": {
            "statuscode": "000000",
            "statusmsg": "success"
        }
    }

	```
	##### fail-1: json格式不合法, HTTP状态码为400

	##### fail-2: 成功, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}
	```
	##### fail-3: 内部错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000016",
	        "statusmsg": "internal error"
	    }
	}
	```
	
### **45. 获取通知信息:**

* url: server_addr/api/v1.1/notice?flag_id=1&app_version=1.0.1&imei=862534031404101
* method: GET
*  请求消息示例:

	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
    flag_id: 标识id
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
    {
        "body": {
            "max_id": 3,
            "notices": [
                {
                    "content": "\u7684\u4f46\u4e8b\u5b9e\u4e0a",
                    "end_time": "2018-08-31",
                    "flag_id": 2,
                    "id": "n20180822163147",
                    "oeprator": "jlcaaa",
                    "remarks": "s\u8bf4\u8bf4",
                    "start_time": "2018-07-30",
                    "title": "\u95fb\u95fb\u5473"
                },
                {
                    "content": "\u8bf4\u4e86\u8038\u4e86\u8038\u80a9\r\n\u5927\u53e3\u5927\u53e3\u4e1c\u5927\u8857\r\n\u5341\u5757ski\u65b9\u6cd5",
                    "end_time": "2018-08-31",
                    "flag_id": 3,
                    "id": "n20180822163218",
                    "oeprator": "jlcaaa",
                    "remarks": "\u7684\u90fd\u662f\u8003\u8bd5\u53ef\r\n\u5927\u53e3\u5927\u53e3\u591a\u6269\u591a\u591a\u591a\u591a\u591a\r\n\u662f\u5f00\u59cb\u8003\u8bd5",
                    "start_time": "2018-07-30",
                    "title": "\u901a\u77e5222"
                }
            ]
        },
        "head": {
            "statuscode": "000000",
            "statusmsg": "success"
        }
    }
	```
	##### 参数说明:
	```
	id: 通知id
	title: 通知标题
	content: 通知内容
	flag_id: 标识id
    remarks: 备注
	oeprator: 操作人
	start_time: 开始时间
    end_time: 结束时间
    max_id: 通知信息最大id
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	
### **46. 已读通知信息:**

* url: server_addr/api/v1.1/read_notice?imei=123456789012345&notice_id=n20180822163030&app_version=1.0.1
* method: GET
*  请求消息示例:

	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
    notice_id: 通知信息id
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
    {
        "head": {
            "statuscode": "000000",
            "statusmsg": "success"
        }
    }
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
### **47. 获取服务协议:**

* url: https://**server_addr**/vssq/api/v1.1/ser_pro

* method: POST
*  请求消息示例:

	```
	{
	    "imei": "395125050989799",
	    "app_version": "1.0.6",
	    "category": 2
	}
	```
	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	category:  0 会员协议 1 开屏广告展示策略, 涉及第三方 2 软件服务使用协议
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	```
	{
	    "body": {
        "content": "\u662f\u5927\u5927\u5927\u4ed8\u4ed8\u4ed8\u4ed8\u591a\u591a\u6240\u6240\u6240\u6240"
        },
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}
	```
	##### 参数说明:
	```
	content: 服务协议内容
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: token认证失败, HTTP状态码为401
	```
	HTTP/1.0 401 UNAUTHORIZED
	WWW-Authenticate: Basic realm="Authentication Required"	```
	```
	##### fail-6: 没有vip服务协议内容, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000044",
	        "statusmsg": "not service protocol"
	    }
	}
	```

### **48. 微商客破解版制造key:**

* url: https://**server_addr**/vssq/api/v1.1/cm_key
* method: POST
*  请求消息示例:
    ```
    {
       "user_id": "15011329055",
       "key_count": 24,
       "ad_time": 3,
       "we_key_id": "2222222222"
    }
    ```

	##### 参数说明:
	```
	ad_time: 免广告时间
	key_count: key数量
    user_id: 手机号
    we_key_id: key记录id
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
    {
        "head": {
            "statuscode": "000000",
            "statusmsg": "success"
        }
    }

	```
	##### fail-1: json格式不合法, HTTP状态码为400

	##### fail-2: 成功, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}
	```
	##### fail-3: 内部错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000016",
	        "statusmsg": "internal error"
	    }
	}
	```

### **49. 分身订单查询:**

* url: https://**server_addr**/vssq/wxpay/q_order
* method: POST
*  请求消息示例:

	```
	{
	      "imei": "395125050989799",
	      "app_version": "1.0.6",
          "out_trade_no": 'DSDSDSDSDSD'
	}
	```

	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	out_trade_no: 订单号
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
	{
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 订单支付失败, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000038",
	        "statusmsg": "pay failure"
	    }
	}
	```

### **50. 分身购买VIP商品:**

* url: https://**server_addr**/vssq/api/v1.1/ava_b_vip
* http请求头部添加: Authorization: Basic MTUwMTEzMjkwNTU6MTExMTEx(此处为base64编码数据，数据内容为(token值:""))
* method: POST
*  请求消息示例:

	```
	{
	    "imei": "395125050989799",
	    "app_version": "1.0.6",
	    "godin_id": "0c8350eca41fc087ea4c4cb4fdbe24fe",
	    "ware_id": "10001"
	}
	```
	
	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	godin_id: 用户的国鼎ID
	ware_id: VIP 商品编号
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	     "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	     },
	     "body:" {
	        "appid": "wx643b87be508f1eaa",
	        "noncestr": "gTr6Pdv251c8LNiuOkpqxRYQ0hAXG9wH",
	        "package": "Sign=WXPay",
	        "partnerid": "1424058002",
	        "prepayid": "wx2017030115342949a37158c60913162114",
	        "sign": "60FEAC74E49D7435741FF6311D2A054C",
	        "timestamp": "1488353669"
	        "order_number": "ava20181010174324o5rpCWRfZwv61IG",
	        "price": 400
	     }
	}
	```
	##### 参数说明:
	```
	字段为调起微信支付客户端所需要的参数
	appid: 微信支付账号的应用id
	noncestr: 随机字符串
	package: 该字段固定使用"Sign=WXPay"
	partnerid: 商户号
	prepayid: 预支付编号
	sign: 签名
	timestamp: 时间戳
	order_number: 订单号
	price: 商品的价格，单位为分
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 内部错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000016",
	        "statusmsg": "internal error"
	    }
	}
	```
	##### fail-6: 订单过期, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000032",
	        "statusmsg": "order expired"
	    }
	}
	```
	##### fail-7: 订单非法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000031",
	        "statusmsg": "order invalid"
	    }
	}
	```
	##### fail-8: token认证失败, HTTP状态码为401
	```
	HTTP/1.0 401 UNAUTHORIZED
	WWW-Authenticate: Basic realm="Authentication Required"	```
	

### **51. 判断授权码页面:**

* url: https://**server_addr**/api/v1.1/judge_k
* method: Post
*  请求消息示例:

	```
	{
		"imei": ["862534031404101","sdfdsfdfdf"],
        "app_version": "1.0.6",
        "num": "123"
	}
	```

	##### 参数说明:
	```
	    app_version: 框架版本名称，
	    imei: 用户唯一设备标识，imei列表,
	    num: 前端传入的字符串
	```
	#### 响应消息及错误码:
	##### success 不需要进入授权码页面, HTTP状态码为200:

	```
	{
	    "body": {"num": "123", 'imei': '12121212121'}
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}
	```

	##### 参数说明:
	```
        num: 前端传入的字符串
        imei: 验证通过的imei
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 需要进入填写邀请码页面, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000040",
	        "statusmsg": "enter page"
	    }
	}
	```
	
### **52. 激活授权码:**

* url: https://**server_addr**/api/v1.1/check_k
* method: POST
*  请求消息示例:

	```
	{
		"imei": ["861504034843978", "761504034843978"]
        "app_version": "1.0.6",
        "key_id": "key1529571617747rSwp"
	}
	```

	##### 参数说明:
	```
	    app_version: 框架版本名称，
	    imei: 用户唯一设备标识，imei列表
	    key_id: 授权码
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
	{
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}

	```
	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 授权码无效, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000036",
            "statusmsg": "key invalid"
	    }
	}
	```
	##### fail-6: imei已经绑定激活状态中的授权码,不能再次绑定新的授权码, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000042",
            "statusmsg": "imei has key, can not binding new key"
	    }
	}
	```

	
### **53. 版本检测:**

* url: https://**server_addr**/api/v1.1/check_app
* method: POST
*  请求消息示例:

	```
	{
		"versioncode": 1,
        "versionname": "1.0.2",
        "md5": "sssssssss",
        "build_time": "sssssssqqqq",
        "build_rev": "www"
	}

	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
	{
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    },
	    "body": {
	        "status": 1
	    }
	}
	```
    ##### 参数说明:
	```
        status: 1 成功  0 失败
	```
	
	##### fail-1: json格式不合法, HTTP状态码为400
	
	
### **54. 素材库登录验证:**

* url: https://**server_addr**/api/v1.1/verify
* method: POST
*  请求消息示例:

	```
	{
		"godin_id": '429a2d57e70bb09c2080d7b029ab14dc'
	}

	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
	{
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    },
	    "body": {
	        "phone_num": "18911359056"
	    }
	}
	```
    ##### 参数说明:
	```
        phone_num: 手机号
	```
	
	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: 用户不存在, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000018",
	        "statusmsg": "user not exist"
	    }
	}
	```

### **55. 购买智能vip:**

* url: https://**server_addr**/vssq/api/v1.1/buy
* http请求头部添加: Authorization: Basic MTUwMTEzMjkwNTU6MTExMTEx(此处为base64编码数据，数据内容为(token值:""))
* method: POST
*  请求消息示例:

	```
	{
	    "imei": "395125050989799",
	    "app_version": "1.0.6",
	    "godin_id": "0c8350eca41fc087ea4c4cb4fdbe24fe",
	    "ware_id": "10001"
	}
	```
	
	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	godin_id: 用户的国鼎ID
	ware_id: VIP 商品编号
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	     "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	     },
	     "body:" {
	        "appid": "wx643b87be508f1eaa",
	        "noncestr": "gTr6Pdv251c8LNiuOkpqxRYQ0hAXG9wH",
	        "package": "Sign=WXPay",
	        "partnerid": "1424058002",
	        "prepayid": "wx2017030115342949a37158c60913162114",
	        "sign": "60FEAC74E49D7435741FF6311D2A054C",
	        "timestamp": "1488353669"
	        "order_number": "HJHQJGLTQBYRYJRVPS20170215151210",
	        "price": 400
	     }
	}
	```
	##### 参数说明:
	```
	字段为调起微信支付客户端所需要的参数
	appid: 微信支付账号的应用id
	noncestr: 随机字符串
	package: 该字段固定使用"Sign=WXPay"
	partnerid: 商户号
	prepayid: 预支付编号
	sign: 签名
	timestamp: 时间戳
	order_number: 订单号
	price: 商品的价格，单位为分
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 内部错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000016",
	        "statusmsg": "internal error"
	    }
	}
	```
	##### fail-6: 订单过期, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000032",
	        "statusmsg": "order expired"
	    }
	}
	```
	##### fail-7: 订单非法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000031",
	        "statusmsg": "order invalid"
	    }
	}
	```
	##### fail-8: token认证失败, HTTP状态码为401
	```
	HTTP/1.0 401 UNAUTHORIZED
	WWW-Authenticate: Basic realm="Authentication Required"	```


### **56. 智能vip状态:**

* url: https://**server_addr**/vssq/api/v1.1/status
* http请求头部添加: Authorization: Basic MTUwMTEzMjkwNTU6MTExMTEx(此处为base64编码数据，数据内容为(token值:""))
* method: POST
*  请求消息示例:

	```
	{
	    "imei": "395125050989799",
	    "app_version": "1.0.6",
	    "godin_id": "0c8350eca41fc087ea4c4cb4fdbe24fe",
        "status": 0
	}
	```
	
	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	godin_id: 用户的国鼎ID
    status: 0 获取会员时间 1 获取图标
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	    "body": {
	        "remain_days": 22,
	        "valid_time": "2017-09-30 11:33:22",
            "recommend_sttaus": 0,
            "recommend": {
                "ware_id": "23232323",
                "icon": "http://godinsec.cn/1.png",
                "ware_name": '商品名称'
	    },  }
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}	
	```
	##### 参数说明:
	```
	remain_days: 会员剩余天数，int型，剩余天数为正，表示会员有效，剩余天数为0或者负数，表示已过期。
	valid_time: 会员到期时间， 日期格式参见相应消息示例
    status = 1 时相关信息
    ware_id: 商品id
    ware_name: 商品名字
    icon: 推荐图标
    recommend_status: 0 没有recommend信息 1 有recommend信息
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 用户不是VIP, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000029",
	        "statusmsg": "user is not vip"
	    }
	}
	```
	##### fail-6: token认证失败, HTTP状态码为401
	```
	HTTP/1.0 401 UNAUTHORIZED
	WWW-Authenticate: Basic realm="Authentication Required"	```


### **59. 获取好友接口:

* url: https://**server_addr**/vssq/api/v1.1/ids
* http请求头部添加: Authorization: Basic MTUwMTEzMjkwNTU6MTExMTEx(此处为base64编码数据，数据内容为(token值:""))
* method: POST
*  请求消息示例:

	```
	{
	    "imei": "395125050989799",
	    "app_version": "1.0.6",
	    "godin_id": "0c8350eca41fc087ea4c4cb4fdbe24fe",
	    "id": "10001dddddddd".
	    "number": 3
	}
	```

	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	godin_id: 用户的国鼎ID
	id: 微信id
	number: 获取好友数量
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
	{
	     "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	     },
	     "body:" {
	        "ids":[
                {
                    "we_id": "wx643b87be508f1eaa",
                    "we_mark": "sdsads"
                },
                {
	                "we_id": "wx643b87be508f1eab",
                    "we_mark": ""
                },
                {
	                "we_id": "wx643b87be508f1eac",
                    "we_mark": "fdfdsfd"
                }
	        ]
	     }
	}
	```
	##### 参数说明:
	```
	we_id: 微信id
    we_mark: 微信标识
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错-误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 内部错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000016",
	        "statusmsg": "internal error"
	    }
	}
	```
	##### fail-6: 用户不存在, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000026",
	        "statusmsg": "user not exist"
	    }
	}
	```
    ##### fail-7: token认证失败, HTTP状态码为401
	```
	HTTP/1.0 401 UNAUTHORIZED
	WWW-Authenticate: Basic realm="Authentication Required"	```


### **61. 新获取开屏广告信息:**

* url: https://**server_addr**/vssq/api/v1.1/open_screen
* method: POST
*  请求消息示例:

	```
	{
	      "imei": "395125050989799",
	      "app_version": "1.0.6",
          "channel": "huwawei"
	}
	```

	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
    channel: 应用渠道
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
	{
	    "body": [
	        {
	            "ad_id": 1,
	            "display_number": 3,
	            "end_time": "2017-07-19 17:05:23",
	            "icon": "http://127.0.0.1/AvatarPhoto/OpenScrrenAdsIcon/test_1499677533.jpg",
	            "name": "首页",
	            "ad_number": "OPENSCREEN1500291507",
	            "position": 0,
	            "skip_time": 3,
	            "source": 0,
	            "virtual_status": 0,
                "refresh_time": "00:00~00:00",
                "refresh_count": 0
	            "sort": 100,
                "app_link":'',
	            "start_time": "2017-07-10 17:05:22",
	            "skip_count": 5
	        },
	        {
	            "ad_id": 2,
	            "display_number": 3,
	            "end_time": "2017-07-25 14:37:55",
	            "icon": "http://127.0.0.1/AvatarPhoto/OpenScrrenAdsIcon/fire03_1499755085.png",
	            "name": "new",
	            "ad_number": "OPENSCREEN1500291505",
	            "position": 0,
	            "skip_time": 3,
	            "virtual_status": 0,
                "refresh_time": "08:00~13:00",
                "refresh_count": 2
	            "source": 0,
	            "sort": 1000,
                "app_link": "http://apk.bjzqb.com/chess_10370.apk",
	            "start_time": "2017-07-11 14:37:54",
	            "skip_count": 5
	        },
	        {
	            "ad_id": 3,
	            "display_number": 3,
	            "end_time": "2017-07-12 11:44:00",
	            "icon": "http://127.0.0.1/AvatarPhoto/OpenScrrenAdsIcon/qr_code_product_1499831056.png",
	            "name": "小花秀",
	            "ad_number": "OPENSCREEN1500291504",
	            "position": 1,
	            "skip_time": 3,
	            "virtual_status": 1,
	            "source": 1,
	            "sort": 128,
                "refresh_time": "00:00~00:00",
                "refresh_count": 0
                "app_link":'',
	            "start_time": "2017-07-12 11:43:59",
	            "skip_count": 5
	        }
	    ],
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}
	```
	##### 参数说明:
	```
	body 字段在有数据时返回，为一个数组。 无数据没有此字段

	ad_id: 广告id
	name: 广告名称
	source: 广告来源  0: '自有广告', 1: '外接SDK'
	position: 广告位置 0: '开屏首页', 1: '应用启动页'
	display_number: 广告每天每人的展示数
	skip_time： 跳过时间
	start_time: 合作开始时间
	end_time: 合作结束时间
	icon: 广告图
	ad_number: 广告编号
	skip_count: 主要控制点击跳过 0 跳过广告，直接进入应用, 其它值如2则有两次点击进入广告，次数超过后进入应用
	sort: 返回排序的数字,此数字是单价转化分后的整数
    app_link: 应用下载链接, 不存在时此值是空字符串
    refresh_time: 广告刷新时间段， 本时间段内客户端随即刷新
    refresh_count: 当前用户刷新次数
    virtual_status:  0 不需要虚拟点击, 1 需要虚拟点击
    skip_count: 用户点击跳过次数
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 内部错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000016",
	        "statusmsg": "internal error"
	    }
	}
	```
	
### **62. 新统计开屏展示数和点击量和真实点击:**

* url: https://**server_addr**/vssq/api/v1.1/open_statistics
* method: POST
*  请求消息示例:

	```
	{
	      "imei": "395125050989799",
	      "app_version": "1.0.6",
	      "ad_info":[
	                {'ad_id': 2, 'type': 0},
	                {'ad_id': 2, 'type': 1}
	                ]
	}
	```
	
	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	ad_info: 统计的广告
   ad_id: 开屏广告id
   type:操作类型   0 展示  1 点击 2 真实点击
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	    "body": {
            "ad_info": [
            {
                "ad_id": 6,
                "virtual_status": 1
            },
            {
                "ad_id": 13,
                "virtual_status": 0
            }
        ],

	        "status": 0
	    },
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}	
	```
	##### 参数说明:
	```
	status: 0 广告id都存在, 1 部分广告id不存在
    ad_id: 广告id
    virtual_status: 虚拟点击, 0 不需要虚拟点击， 1 需要虚拟点击
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 内部错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000016",
	        "statusmsg": "internal error"
	    }
	}
	```
	
### **63. 获取通知信息新接口:**

* url: server_addr/api/v1.1/n_notice?flag_id=1&app_version=1.0.1&imei=862534031404101
* method: GET
*  请求消息示例:

	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
    flag_id: 标识id
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
    {
        "body": {
            "max_id": 3,
            "notices": [
                {
                    "content": "\u7684\u4f46\u4e8b\u5b9e\u4e0a",
                    "end_time": "2018-08-31",
                    "flag_id": 2,
                    "id": "n20180822163147",
                    "oeprator": "jlcaaa",
                    "remarks": "s\u8bf4\u8bf4",
                    "start_time": "2018-07-30",
                    "notice_type": 1,
                    "icon": “http://godinsec.cn/1.png”,
                    "icon_link": "www.baidu.com",
                    "title": "\u95fb\u95fb\u5473",
                    "notice_user": 0
                },
                {
                    "content": "\u8bf4\u4e86\u8038\u4e86\u8038\u80a9\r\n\u5927\u53e3\u5927\u53e3\u4e1c\u5927\u8857\r\n\u5341\u5757ski\u65b9\u6cd5",
                    "end_time": "2018-08-31",
                    "flag_id": 3,
                    "id": "n20180822163218",
                    "oeprator": "jlcaaa",
                    "remarks": "\u7684\u90fd\u662f\u8003\u8bd5\u53ef\r\n\u5927\u53e3\u5927\u53e3\u591a\u6269\u591a\u591a\u591a\u591a\u591a\r\n\u662f\u5f00\u59cb\u8003\u8bd5",
                    "start_time": "2018-07-30",
                    "notice_type": 0,
                    "icon": “http://godinsec.cn/1.png”,
                    "icon_link": "www.baidu.com",
                    "title": "\u901a\u77e5222",
                    "notice_user": 12
                }
            ]
        },
        "head": {
            "statuscode": "000000",
            "statusmsg": "success"
        }
    }
	```
	##### 参数说明:
	```
	id: 通知id
	title: 通知标题
	content: 通知内容
	flag_id: 标识id
    remarks: 备注
	oeprator: 操作人
	start_time: 开始时间
    end_time: 结束时间
    max_id: 通知信息最大id
    notice_type: 0 普通消息 1 图片消息
    icon: 图片地址
    icon_link: 点击图片跳转地址
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```

### **64. 获得免费会员:

* url: https://**server_addr**/vssq/api/v1.1/f_vip
* http请求头部添加: Authorization: Basic MTUwMTEzMjkwNTU6MTExMTEx(此处为base64编码数据，数据内容为(token值:""))
* method: POST
*  请求消息示例:

	```
	{
	    "imei": "395125050989799",
	    "app_version": "1.0.6",
	    "godin_id": "0c8350eca41fc087ea4c4cb4fdbe24fe"
	}
	```

	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	godin_id: 用户的国鼎ID
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
	{
	     "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	     },
	}
	```
	##### 参数说明:
	```
	ids: 一组微信id
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错-误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	##### fail-5: 内部错误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000016",
	        "statusmsg": "internal error"
	    }
	}
	```
	##### fail-6: 用户不存在, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000026",
	        "statusmsg": "user not exist"
	    }
	}
	```
    ##### fail-7: token认证失败, HTTP状态码为401
	```
	HTTP/1.0 401 UNAUTHORIZED
	WWW-Authenticate: Basic realm="Authentication Required"	```


### **65. 微商助理(过期):

* url: https://**server_addr**/vssq/api/v1.1/b_assistant
* method: POST
*  请求消息示例:

	```
	{
	    "imei": "395125050989799",
	    "app_version": "1.0.6"
	}
	```

	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
	{
	     "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	     },
	     "body": {
	        "link": ""
	        "we_id": "sskskk222", 
			"we_customer_service": "sdf"
	        "we_public": "ssss1113333"}
	}
	```
	##### 参数说明:
	```
	link: 跳转链接
	we_id: 客服微信号
	we_customer_service：  微信客服号昵称
	we_public:公众号
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错-误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```


### **66. 微课堂:

* url: https://**server_addr**/vssq/api/v1.1/b_link
* method: POST
*  请求消息示例:

	```
	{
	    "imei": "395125050989799",
	    "app_version": "1.0.6"
	}
	```

	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:

	```
	{
	     "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	     },
	     "body": {
	        "link": "", 
	     }
	}
	```
	##### 参数说明:
	```
	link: 跳转链接
	```

	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	##### fail-3: imei在黑名单中, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000014",
	        "statusmsg": "imei in black list"
	    }
	}
	```
	##### fail-4: app版本错-误, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000015",
	        "statusmsg": "app version is invalid"
	    }
	}
	```
	
### **67. 微商助理:

* url: https://**server_addr**/vssq/api/v1.1/vszl_search
* method: post
*  请求消息示例:

	```
	{
	    "imei": "395125050989799",
	    "app_version": "1.0.6",
	    "wx": "tudi1997"
	}
	```

	##### 参数说明:
	```
	wx: 用户微信
	imei: 用户唯一设备标识
	app_version: 应用版本
	```
	#### 响应消息及错误码:
	##### success-1, HTTP状态码为200:

	```
	{
	     "head": {
	        "statuscode": "000047",
	        "statusmsg": "already bind"
	     }
	}
	```
	##### success-1: wx未查询到, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000046",
	        "statusmsg": "no bind"
	    }
	}
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	```
    {
        "message": {
            "imei": "param missing"
        }
    }
    ```
    ##### fail-2: json格式不合法, HTTP状态码为400
	```
    {
        "message": {
            "app_version": "param missing"
        }
    }
    ```
* url: https://**server_addr**/vssq/api/v1.1/vszl_add
* method: post
*  请求消息示例:
    ```
	{
	    "imei": "395125050989799",
	    "app_version": "1.0.6",
	    "wx": "tudi1997"
	}
	```

	##### 参数说明:
	```
	wx: 用户微信
	imei: 用户唯一设备标识
	app_version: 应用版本
	```
	#### 响应消息及错误码:
	##### success-1, HTTP状态码为200:

	```
	{
	     "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	     },
	     "body": {
            "link": "www.baidu.com",
            "nickname": "bcd",
            "service_wx": "wx2",
            "we_public": "1234567"
         }
	}
	```
	##### success-2, HTTP状态码为200:

	```
	{
	     "head": {
            "statuscode": "000048",
            "statusmsg": "can not repeat add"
         },
	     "body": {
            "link": "www.baidu.com",
            "nickname": "bcd",
            "service_wx": "wx2",
            "we_public": "1234567"
         }
	}
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	```
    {
        "message": {
            "imei": "param missing"
        }
    }
    ```
    ##### fail-2: json格式不合法, HTTP状态码为400
	```
    {
        "message": {
            "app_version": "param missing"
        }
    }
    ```
### **68. 免费体验Vip:
* url: https://**server_addr**/vssq/api/v1.1/experience_status
* 获取当前用户是否有免费体验的资格
* method: post
*  请求消息示例:

	```
	{
	    "imei": "395125050989799",
	    "app_version": "1.0.6",
	    "godin_id": "4c59396301ab6274bd7892f0b31df36e",
	}
	```

	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	godin_id: 用户的国鼎ID
	```
	#### 响应消息及错误码:
	##### success-1, 用户有免费体验资格, HTTP状态码为200:

	```
	{
	     "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	     }
	}
	```
	##### success-2: 用户没有免费体验资格, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000049",
	        "statusmsg": "already experience"
	    }
	}
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	```
    {
        "message": {
            "imei": "param missing"
        }
    }
    ```
    ##### fail-2: json格式不合法, HTTP状态码为400
	```
    {
        "message": {
            "app_version": "param missing"
        }
    }
    ```
* url: https://**server_addr**/vssq/api/v1.1/free_experience
* 当前用户已体验
* method: post
*  请求消息示例:
    ```
	{
	    "imei": "395125050989799",
	    "app_version": "1.0.6",
	    "godin_id": "4c59396301ab6274bd7892f0b31df36e",
	}
	```

	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	godin_id: 用户的国鼎ID
	```
	#### 响应消息及错误码:
	##### success, 用户已经体验, HTTP状态码为200:

	```
	{
	     "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	     }
	}
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	```
    {
        "message": {
            "imei": "param missing"
        }
    }
    ```
    ##### fail-2: json格式不合法, HTTP状态码为400
	```
    {
        "message": {
            "app_version": "param missing"
        }
    }
    ```
### **69. 倒三角功能配置的获取接口:**

* url: https://**server_addr**/vssq/api/v1.1/get_triangle
* method: POST
*  请求消息示例:

	```
	{
	      "imei": "395125050989799",
	      "app_version": "1.0.6",
	}
	```
	
	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	    "body": {
            "set_fun": "goumaivip,keduoduo,weiketang,weishangzhuli"
        } 
	    ,
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}	
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	```
    {
        "message": {
            "imei": "param missing"
        }
    }
    ```
    ##### fail-2: json格式不合法, HTTP状态码为400
	```
    {
        "message": {
            "app_version": "param missing"
        }
    }
    ```
### **70. 功能视频的获取接口:**

* url: https://**server_addr**/vssq/api/v1.1/function_video
* method: POST
*  请求消息示例:

	```
	{
	      "imei": "395125050989799",
	      "app_version": "1.0.6",
	      "video_name": "zidongqianghongbao"
	}
	```
	
	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	video_name: 视频名称
	```
	#### 响应消息及错误码:
	##### success1, HTTP状态码为200:
	
	```
	{
	    "body": {
            "link": "http://10.0.5.126/WePhoto/WeVideo/2019051818015292a967d3046e4123b1152ece183c2ff2.mp4"
        } 
	    ,
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}	
	```
	##### success2, HTTP状态码为200:
	
	```
	{
	    
	    "head": {
	        "statuscode": "000048",
	        "statusmsg": "Resource not found"
	    }
	}	
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	```
    {
        "message": {
            "imei": "param missing"
        }
    }
    ```
    ##### fail-2: json格式不合法, HTTP状态码为400
	```
    {
        "message": {
            "app_version": "param missing"
        }
    }
    ```
### **71. 微店铺链接地址获取接口:**

* url: https://**server_addr**/vssq/api/v1.1/GetMicroStoreUrlApi
* method: POST
*  请求消息示例:

	```
	{
	      "imei": "395125050989799",
	      "app_version": "1.0.6",
	}
	```
	
	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	    "body": {
            "link": "www.baidu.com"
        } 
	    ,
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}	
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	```
    {
        "message": {
            "imei": "param missing"
        }
    }
    ```
    ##### fail-2: json格式不合法, HTTP状态码为400
	```
    {
        "message": {
            "app_version": "param missing"
        }
    }
    ```


### **72. 邀请链接获取接口:**

* url: https://**server_addr**/vssq/api/v1.1/GetInviteLink
* method: POST
*  请求消息示例:

	```
	{
	    "imei": "395125050989799",
	    "app_version": "1.0.6",
	    "godin_id": "4c59396301ab6274bd7892f0b31df36e",
	}
	```

	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	godin_id: 用户的国鼎ID
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	    "body": {
            "link": "http://www.godin.cn/eb1e3ff9fbf7ced0",
            "register_person_num": 1,
            "pay_person_num": 1,
            "account_award": 10,
            "account_balance": 0
        } 
	    ,
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}	
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	```
    {
        "message": {
            "imei": "param missing"
        }
    }
    ```
    ##### fail-2: json格式不合法, HTTP状态码为400
	```
    {
        "message": {
            "app_version": "param missing"
        }
    }
    ```
    
    
### **73. 邀请输入手机号的调用接口:**

* url: https://**server_addr**/vssq/api/v1.1/invite
* method: POST
*  请求消息示例:

	```
	{
	    "imei": "395125050989799",
	    "app_version": "1.0.6",
	    "phone_num": "18610379194",
	    "current_url": "http://www.godin.cn/eb1e3ff9fbf7ced0"
	}
	```

	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	phone_num: 被邀请用户输入的手机号
	current_url: 当前邀请页面的 url
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "Success"
	    }
	}	
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	```
    {
        "message": {
            "imei": "param missing"
        }
    }
    ```
    ##### fail-2: 当前 url 错误, HTTP状态码为200
	```
    {
	    "head": {
	        "statuscode": "000050",
	        "statusmsg": "url is error"
	    }
	}
    ```
    ##### fail-3: 当前用户已被邀请过, HTTP状态码为200
	```
    {
	    "head": {
	        "statuscode": "000051",
	        "statusmsg": "already invited"
	    }
	}
    ```


### **74. 每日一淘链接地址获取接口:**

* url: https://**server_addr**/vssq/api/v1.1/GetEveryWashUrl
* method: POST
*  请求消息示例:

	```
	{
	      "imei": "395125050989799",
	      "app_version": "1.0.6",
	}
	```
	
	##### 参数说明:
	```
	imei: 用户唯一设备标识
	app_version: 应用版本
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200:
	
	```
	{
	    "body": {
            "link": "www.baidu.com"
        } 
	    ,
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}	
	```
	##### fail-1: json格式不合法, HTTP状态码为400
	```
    {
        "message": {
            "imei": "param missing"
        }
    }
    ```
    ##### fail-2: json格式不合法, HTTP状态码为400
	```
    {
        "message": {
            "app_version": "param missing"
        }
    }
    ```
    
### **75. 检测IMEI是否为新用户:**
* url: https://**server_addr**/api/v1.1/check_imel
* method: POST
*  请求消息示例:

	```
	{
		"imei": ["861504034843978", "761504034843978"]
        "app_version": "1.0.6",
	}
	```

	##### 参数说明:
	```
	    app_version: 框架版本名称，
	    imei: 用户唯一设备标识，imei列表
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200, 代表是新用户, 有免费试用一天的权限:

	```
	{
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}

	```
	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```

### **76. 免费试用一天:**
* url: https://**server_addr**/api/v1.1/free_trial
* method: POST
*  请求消息示例:

	```
	{
		"imei": ["861504034843978", "761504034843978"]
        "app_version": "1.0.6",
	}
	```

	##### 参数说明:
	```
	    app_version: 框架版本名称，
	    imei: 用户唯一设备标识，imei列表
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200, 成功添加免费试用一天:

	```
	{
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    }
	}

	```
	##### fail-1: json格式不合法, HTTP状态码为400
	##### fail-2: imei格式不合法, HTTP状态码为200
	```
	{
	    "head": {
	        "statuscode": "000013",
	        "statusmsg": "imei invalid"
	    }
	}
	```
	

### **77. 功能小红点:**
* url: https://**server_addr**/api/v1.1/get_hot_dot
* method: POST
*  请求消息示例:

	```
	{
		"imei": "861504034843978"
        "app_version": "1.0.6",
        "type": 0
	}
	```

	##### 参数说明:
	```
	    app_version: 框架版本名称，
	    imei: 用户唯一设备标识，imei列表
	    type: 0 倒三角 1 主应用
	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200, 成功添加免费试用一天:

	```
	{
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    },
	    "body": "1,2,5"
	}

	```
	##### fail-1: json格式不合法, HTTP状态码为400
	```
    {
        "message": {
            "imei": "param missing"
        }
    }
    ```

### **78. 语音盒子上传视频:**
* url: https://**server_addr**/api/v1.1/upload_voice
* method: POST
*  请求消息示例:

	```
	{
		"voice_name": "123.mp3"
	}
	```

	##### 参数说明:
	```
	    voice_name: 要上传的音频文件

	```
	#### 响应消息及错误码:
	##### success, HTTP状态码为200, 成功添加免费试用一天:

	```
	{
	    "head": {
	        "statuscode": "000000",
	        "statusmsg": "success"
	    },
	    "body": {"url": "http://wemiyao/vssq/share/voice?voice_name=1564390559.mp3"}
	}

	```
	##### fail-1: 音频文件格式错误, HTTP状态码为200
	```
    {
	    "head": {
	        "statuscode": "000053",
	        "statusmsg": "file format error"
	    }
	}
    ```
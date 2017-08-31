#!/usr/bin/python3  
# -*- coding: utf-8 -*-
# ----------------------------
# |   Author:sml2h3          |
# |   Email:sml2h3@gmail.com |
# ----------------------------
import time
import requests
from System.Wechat.Common import Common
import json
import base64


class Login(object):
    def __init__(self):
        self.base_url = "https://login.wx.qq.com"
        self.common = Common.Common()

    def get_qrcode(self):
        url = "%(base)s/jslogin?appid=wx782c26e4c19acffb" \
              "&redirect_uri=https%%3A%%2F%%2Fwx.qq.com%%2Fcgi-bin%%2Fmmwebwx-bin%%2Fwebwxnewloginpage" \
              "&fun=new" \
              "&lang=zh_CN" \
              "&_=%(timestamp)s"
        url_param = {
            'base': self.base_url,
            'timestamp': self.common.get_timestamp()
        }
        url = url % url_param
        result = dict()
        try:
            qrcode = requests.get(url)
            if qrcode and qrcode.status_code == 200:
                qrcode = self.common.response_deal_by_fh(qrcode.text)
                if qrcode['code'] == '200':
                    uuid = qrcode['uuid']
                    qrcode_stream = self.__download_qrcode(uuid=uuid)
                    result['code'] = 200
                    result['uuid'] = uuid
                    result['qrcode'] = qrcode_stream
                    return result
                else:
                    return
            else:

                return
        except requests.ConnectionError as e:
            return

    # 检查二维码状态 400验证码失效/408等待扫码/200登陆成功
    def check_login_status(self, uuid, status=0):
        # status:tip
        if status in [0, 1]:
            url = "%(base)s/cgi-bin/mmwebwx-bin/login?loginicon=true" \
                  "&uuid=%(uuid)s" \
                  "&tip=%(status)s" \
                  "&r=-74290061" \
                  "&_=%(timestamp)s"
            url_param = {
                'base': self.base_url,
                'uuid': uuid,
                'status': status,
                'timestamp': self.common.get_timestamp()
            }
            url = url % url_param
            result = dict()
            try:
                status = requests.get(url, timeout=30)
                if status and status.status_code == 200:
                    status = self.common.response_deal_by_fh(status.text)
                    code = status['code']
                    if code == "408":
                        # 继续等待
                        result['code'] = 408
                    if code == "400":
                        # 超时
                        result['code'] = 400
                    if code == "201":
                        # 登录成功
                        result['code'] = 201
                        result['avatar'] = status['userAvatar']
                    if code == "200":
                        result['code'] = 200
                        result['info'] = self.__real_login(url=status['redirect_uri'])
                    return result
                else:
                    return
            except requests.ConnectionError:
                # connect error
                return
            except requests.ConnectTimeout:
                result['code'] = 408
                return result
        else:
            # status error
            return

    def __real_login(self, url):
        try:
            login_result = requests.get(url + "&fun=new&version=v2&lang=zh_CN")
            if login_result and login_result.status_code == 200:
                login_cookies = login_result.cookies
                login_result = login_result.text
                login_dict = self.common.xml_to_dict(login_result)
                wxsid = login_dict['error']['wxsid']
                wxskey = login_dict['error']['skey']
                wxpass_ticket = login_dict['error']['pass_ticket']
                wxuin = login_dict['error']['wxuin']
                wxinfo = self.__wx_init(wxpass_ticket, wxsid, wxskey, wxuin, login_cookies)
                nickname = wxinfo['User']['NickName']
                nickname = self.common.wx_decode(nickname)
                username = wxinfo['User']['UserName']
                avatar = wxinfo['User']['HeadImgUrl']
                # 加载头像，此处后期需要进行异常处理
                avatar = requests.get("https://wx2.qq.com" + avatar, cookies=login_cookies).content
                avatar = base64.b64encode(avatar).decode()
                return {
                    'nickname': nickname,
                    'avatar':  'data:img/jpg;base64,' + avatar,
                    'uin': wxuin
                }
            else:
                return
        except ConnectionError:
            return
        return

    def __wx_init(self, pass_ticket, sid, skey, uin, cookies):
        try:
            url = "https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r=-100877003&lang=zh_CN&pass_ticket=" + pass_ticket
            data = '{"BaseRequest":{"Uin":"%(uin)s","Sid":"%(sid)s","Skey":"%(skey)s","DeviceID":"e026433316256963"}}'
            data_param = {
                'uin': uin,
                'sid': sid,
                'skey': skey,
            }
            data = data % data_param
            result_init = requests.post(url, data=data, cookies=cookies)
            if result_init and result_init.status_code == 200:
                return json.loads(result_init.text)
            else:
                return
        except ConnectionError:
            return

    def __download_qrcode(self, uuid):
        url = "%(base)s/qrcode/%(uuid)s"
        url_param = {
            'base': self.base_url,
            'uuid': uuid
        }
        url = url % url_param
        try:
            qrcode = requests.get(url)
            if qrcode and qrcode.status_code == 200:
                return qrcode.content
            else:
                return
        except requests.ConnectionError as e:
            return


if __name__ == '__main__':
    open('logo.jpg', 'wb')
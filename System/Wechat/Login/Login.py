#!/usr/bin/python3  
# -*- coding: utf-8 -*-
# ----------------------------
# |   Author:sml2h3          |
# |   Email:sml2h3@gmail.com |
# ----------------------------
import time
import requests
from System.Wechat.Common import Common


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

    #检查二维码状态 400验证码失效/408等待扫码/200登陆成功
    def check_login_status(self, uuid, status=0):
        #status:tip
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
                        #继续等待
                        result['code'] = 408
                    if code == "400":
                        #超时
                        result['code'] = 400
                    if code == "201":
                        #登录成功
                        result['code'] = 201
                        result['avatar'] = status['userAvatar']
                    if code == "200":
                        result['code'] = 200
                        result['redirect_uri'] = status['redirect_uri']
                    return result
                else:
                    return
            except requests.ConnectionError:
                #connect error
                return
            except requests.ConnectTimeout:
                result['code'] = 408
                return result
        else:
            #status error
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
    Login().get_qrcode()
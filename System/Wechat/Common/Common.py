#!/usr/bin/python3  
# -*- coding: utf-8 -*-
# ----------------------------
# |   Author:sml2h3          |
# |   Email:sml2h3@gmail.com |
# ----------------------------
import time


class Common(object):
    '''
        处理类似
        window.QRLogin.code = 200; window.QRLogin.uuid = "4eCV36wbOQ==";
        这样的响应文本
        返回dict类型
        {
            "code": 200,
            "uuid": "4eCV36wbOQ=="
        }
    '''

    def response_deal_by_fh(self, response):
        text_tmp = response
        if text_tmp[-1] == ';':
            text_tmp = text_tmp[:-1]
        text_split_tmp = text_tmp.split('; ')
        if len(text_split_tmp) < 2:
            text_split_tmp = text_tmp.split(';w')
        result = dict()
        for text_single in text_split_tmp:
            if text_single == '':
                continue
            else:
                if ' = ' in text_single:
                    text_single_split_tmp = text_single.split(' = ')
                else:
                    text_single_split_tmp = text_single.split('=')
                value_tmp = text_single_split_tmp[1].lstrip().replace('"', '').replace("'", '')
                key_split_tmp = text_single_split_tmp[0].split('.')
                key_tmp = key_split_tmp[-1].lstrip().replace('"', '').replace("'", '')
                result[key_tmp.lstrip()] = value_tmp.lstrip()
        return result
    '''
        取毫秒级时间戳
    '''
    def get_timestamp(self):
        return int(time.time() * 1000)
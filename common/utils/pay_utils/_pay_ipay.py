"""
Module: _pay_trip
Author: Ciwei
Date: 2024-11-05

Description:
    This module provides functionalities for ...
"""
import urllib.parse

from common.models import ProxyInfoModel
from common.utils.http_utils import CurlHttpUtil


class Ipay:
    def __init__(self, proxy_info: ProxyInfoModel):
        self.__http_utils = CurlHttpUtil()
        self.__http_utils.initialize_http_util(proxy_info=proxy_info)
        self.__user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
        self.timeout = 100

    def pay_form_url(self, redirect_info):
        headers = {
            'User-Agent': self.__user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Origin': 'https://th.vietjetair.com',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Dest': 'document',
            'Referer': 'https://th.vietjetair.com/',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        json_data = redirect_info['form_data']
        response = self.__http_utils.post(
            url=redirect_info['form_url'],
            headers=headers,
            data=urllib.parse.urlencode(json_data),
            timeout=self.timeout
        )
        return response.text

"""
Module: _pay_trip
Author: Ciwei
Date: 2024-11-05

Description:
    This module provides functionalities for ...
"""
import urllib.parse

from common.errors import HttpModuleError, HttpModuleErrorStateEnum
from common.models import ProxyInfoModel
from common.utils.http_utils import CurlHttpUtil


class Yapikredi:
    def __init__(self, proxy_info: ProxyInfoModel):
        self.__http_utils = CurlHttpUtil(auth_manage_cookie=False)
        self.__http_utils.initialize_http_util(proxy_info=proxy_info)
        self.__user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0'
        self.timeout = 100

    def ykb_payment_service(self, req_data: dict):
        headers = {
            'User-Agent': self.__user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "max-age=0",
            "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "Origin": "https://www.turkishairlines.com",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "iframe",
            "Sec-Fetch-Storage-Access": "active",
            "Referer": "https://www.turkishairlines.com/",
            "Accept-Language": "en-US,en;q=0.9"
        }

        response = self.__http_utils.post(url='https://posnet.yapikredi.com.tr/3DSWebService/YKBPaymentService',
                                          headers=headers, data=urllib.parse.urlencode(req_data), timeout=100)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)

        return response.text, self.__http_utils.get_cookie_all()

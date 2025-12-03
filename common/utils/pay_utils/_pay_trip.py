"""
Module: _pay_trip
Author: Ciwei
Date: 2024-11-05

Description: 
    This module provides functionalities for ...
"""
from common.errors import HttpModuleErrorStateEnum, HttpModuleError
from common.models import ProxyInfoModel
from common.utils import StringUtil
from common.utils.http_utils import CurlHttpUtil


class PayTrip:
    def __init__(self, proxy_info: ProxyInfoModel):
        self.__http_utils = CurlHttpUtil()
        self.__http_utils.initialize_http_util(proxy_info=proxy_info)

    def method_url(self, method_data: str):
        headers = {
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "Origin": "https://geo.cardinalcommerce.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "iframe",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9"
        }

        response = self.__http_utils.post(
            url="https://trip-challenge.triplinkintl.com/challenge/brw/methodUrl",
            headers=headers,
            data=f'threeDSMethodData={method_data}',
            auth_redirect=True
        )

        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)

        data = StringUtil.extract_between(response.text, 'name="threeDSMethodData" type="hidden" value="', '"')
        url = StringUtil.extract_between(response.text, '<form action="', '"')
        return url, data

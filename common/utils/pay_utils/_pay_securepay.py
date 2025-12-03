import json
import urllib.parse
import uuid
from typing import Optional

from common.errors import HttpModuleError, HttpModuleErrorStateEnum, ServiceError, ServiceStateEnum
from common.models import ProxyInfoModel
from common.utils.http_utils import CurlHttpUtil


class Securepay:
    def __init__(self, proxy_info: Optional[ProxyInfoModel], user_agent: str):
        self.__http_utils = CurlHttpUtil()
        self.__http_utils.initialize_http_util(proxy_info=proxy_info)
        self.user_agent = user_agent
        self.timeout = 60

    def payment_1(self, data, origin: str, referer: str):
        """

        Args:
            referer:
            origin:
            data:

        Returns:

        """
        headers = {
            'Host': 'securepay.e-ghl.com',
            'cache-control': 'max-age=0',
            'origin': origin,
            'content-type': 'application/x-www-form-urlencoded',
            'upgrade-insecure-requests': '1',
            'user-agent': self.user_agent,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': referer,
            'accept-language': 'en,zh-CN;q=0.9,zh;q=0.8',
            'priority': 'u=0, i',
        }
        response_post = self.__http_utils.post(url='https://securepay.e-ghl.com/IPG/Payment.aspx',
                                               data=urllib.parse.urlencode(data),
                                               headers=headers, timeout=self.timeout)
        if response_post.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response_post.status)
        return response_post.text

    def get_host_routing(self, paymentdata):
        """

        Args:
            paymentdata:

        Returns:

        """
        headers = {
            "Host": "securepay.e-ghl.com",
            "user-agent": self.user_agent,
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.5",
            "accept-encoding": "gzip, deflate, br, zstd",
            "content-type": "application/json",
            "x-requested-with": "XMLHttpRequest",
            "origin": "https://securepay.e-ghl.com",
            "referer": "https://securepay.e-ghl.com/IPG/Payment.aspx",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "priority": "u=0",
            "te": "trailers"
        }
        response = self.__http_utils.post(
            url='https://securepay.e-ghl.com/eGHL3DSAuthentication/Internal/GetHostRouting',
            data=json.dumps(paymentdata),
            headers=headers, timeout=self.timeout)
        if response.status != 200 and response.json['status'] != 0:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

    def payment_2(self, data):
        """

        Args:
            data:

        Returns:

        """
        headers = {
            "Host": "securepay.e-ghl.com",
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://securepay.e-ghl.com",
            "Connection": "keep-alive",
            "Referer": "https://securepay.e-ghl.com/IPG/Payment.aspx",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=0, i",
            "TE": "trailers"
        }
        response = self.__http_utils.post(url='https://securepay.e-ghl.com/IPG/Payment.aspx',
                                          data=urllib.parse.urlencode(data),
                                          headers=headers, timeout=self.timeout)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def response_pbb3(self, data):
        """

        Args:
            data:

        Returns:

        """
        headers = {
            "Host": "securepay.e-ghl.com",
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Referer": "https://secureacceptance.cybersource.com/",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://secureacceptance.cybersource.com",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Priority": "u=0, i",
            "TE": "trailers"
        }
        response = self.__http_utils.post(
            url='https://securepay.e-ghl.com/ipg/response_pbb3.aspx',
            data=urllib.parse.urlencode(data),
            headers=headers, timeout=self.timeout)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

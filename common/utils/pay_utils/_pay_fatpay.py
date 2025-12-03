"""
Module: _pay_trip
Author: Ciwei
Date: 2024-11-05

Description:
    This module provides functionalities for ...
"""
import urllib.parse

from common.errors import HttpModuleErrorStateEnum, HttpModuleError
from common.models import ProxyInfoModel
from common.utils.http_utils import CurlHttpUtil


class Fatpay:
    def __init__(self, proxy_info: ProxyInfoModel):
        self.__http_utils = CurlHttpUtil()
        self.__http_utils.initialize_http_util(proxy_info=proxy_info)
        self.__user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
        self.timeout = 60

    def pay_url_data(self, redirect_info):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://dv.websky.aero',
            'priority': 'u=0, i',
            'referer': 'https://dv.websky.aero/',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'cross-site',
            'upgrade-insecure-requests': '1',
            'user-agent': self.__user_agent,
        }
        json_data = {
            'CountryCode': redirect_info['CountryCode'],
            'LanguageCode': redirect_info['LanguageCode'],
            'OrderNumber': redirect_info['OrderNumber'],
            'MerchantReturnData': redirect_info['MerchantReturnData'],
            'TransactionID': redirect_info['TransactionID'],
            'MerchantAccountCode': redirect_info['MerchantAccountCode'],
            'SuccessURL': 'https://ipe-pmt.prod.sabre.com/ipe/standardpsp?supplierID=FPAY&pwsStatus=AUTHORIZED',
            'PendingURL': 'https://ipe-pmt.prod.sabre.com/ipe/standardpsp?supplierID=FPAY&pwsStatus=PENDING',
            'FailureURL': 'https://ipe-pmt.prod.sabre.com/ipe/standardpsp?supplierID=FPAY&pwsStatus=REFUSED',
            'CancelURL': 'https://ipe-pmt.prod.sabre.com/ipe/standardpsp?supplierID=FPAY&pwsStatus=CANCELLED',
        }
        response = self.__http_utils.post(
            url=redirect_info['fatpay_url'],
            headers=headers,
            data=urllib.parse.urlencode(json_data),
            timeout=self.timeout
        )
        return response.text

    def make_payment(self, referer, payment_form_data):
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://fatpay.net',
            'priority': 'u=1, i',
            'referer': referer,
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': self.__user_agent,
            'x-requested-with': 'XMLHttpRequest',
        }

        response = self.__http_utils.post(url='https://fatpay.net/makepayment', headers=headers,
                                          data=urllib.parse.urlencode(payment_form_data),
                                          timeout=self.timeout)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

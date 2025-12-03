"""
Module: _pay_trip
Author: Ciwei
Date: 2024-11-05

Description:
    This module provides functionalities for ...
"""
import base64
import json
from urllib.parse import urlencode

from lxml import etree

from common.errors import HttpModuleErrorStateEnum, HttpModuleError
from common.models import ProxyInfoModel
from common.utils import StringUtil
from common.utils.http_utils import CurlHttpUtil


class Midtrans:
    def __init__(self, proxy_info: ProxyInfoModel):
        self.__http_utils = CurlHttpUtil()
        self.__http_utils.initialize_http_util(proxy_info=proxy_info)
        self.__user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
        self.timeout = 60

    def midtrans_3ds(self, url: str):
        headers = {
            'User-Agent': self.__user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'referer': 'https://secure2.lionair.co.id/',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'priority': 'u=0, i',
        }
        response = self.__http_utils.get(url=url, headers=headers)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)

        trip_challenge_url, trip_challenge_data, = self.trip_challenge_url(response.text)
        midtrans_callback_url, midtrans_callback_data = self.get_from_auction_url(response.text, "veritrans")

        return trip_challenge_url, {
            "threeDSMethodData": trip_challenge_data}, midtrans_callback_url, midtrans_callback_data

    def trip_challenge_brw(self, url: str, data: dict) -> str:

        headers = {
            'User-Agent': self.__user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Content-Type': 'application/x-www-form-urlencoded',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'origin': 'https://api.midtrans.com',
            'upgrade-insecure-requests': '1',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-dest': 'iframe',
            'sec-fetch-storage-access': 'active',
            'referer': 'https://api.midtrans.com/',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'priority': 'u=0, i',
        }

        response = self.__http_utils.post(url=url, headers=headers, data=urlencode(data))
        if response.status != 302:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.location

    def method_notification(self, url):
        headers = {
            'User-Agent': self.__user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-dest': 'iframe',
            'sec-fetch-storage-access': 'active',
            'referer': 'https://api.midtrans.com/',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'priority': 'u=0, i',
        }

        response = self.__http_utils.get(url=url, headers=headers)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)

        method_response_url, method_response_data = self.get_from_auction_url(response.text, "")
        return method_response_url, method_response_data

    def method_response(self, url, data):

        headers = {
            'User-Agent': self.__user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            # 'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/x-www-form-urlencoded',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'origin': 'https://triplink-acs-3ds-sgp.triplinkintl.com',
            'upgrade-insecure-requests': '1',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-dest': 'iframe',
            'referer': 'https://triplink-acs-3ds-sgp.triplinkintl.com/',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'priority': 'u=0, i',
        }

        response = self.__http_utils.post(url=url, headers=headers, data=urlencode(data))
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)

    def midtrans_callback(self, url):

        headers = {
            'User-Agent': self.__user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            # 'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/x-www-form-urlencoded',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'origin': 'https://api.midtrans.com',
            'upgrade-insecure-requests': '1',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-dest': 'document',
            'referer': 'https://api.midtrans.com/v2/3ds/redirect/06685262-2812-4943-a3e3-c12623f9a472',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'priority': 'u=0, i',
        }

        response = self.__http_utils.post(url=url, headers=headers)

        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)

    def callback_3ds(self, url, data):

        headers = {
            'User-Agent': self.__user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Content-Type': 'application/x-www-form-urlencoded',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'origin': 'https://api.midtrans.com',
            'upgrade-insecure-requests': '1',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-dest': 'document',
            'referer': 'https://api.midtrans.com/v2/3ds/redirect/06685262-2812-4943-a3e3-c12623f9a472',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'priority': 'u=0, i',
        }
        browser_config = {"browserAcceptHeader": "*/*", "browserScreenWidth": 2560, "browserScreenHeight": 1440,
                          "browserColorDepth": 24,
                          "browserUserAgent": self.__user_agent,
                          "browserTZ": -480, "browserLanguage": "zh-CN", "browserJavaEnabled": False,
                          "browserJavascriptEnabled": True}
        data['BrowserInfo'] = base64.b64encode(
            json.dumps(browser_config, separators=(',', ':')).encode()).decode().strip("=")

        response = self.__http_utils.post(url=url, data=urlencode(data), headers=headers)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        result_url, result_completion_data = self.result_completion_url(response.text)
        return result_url, result_completion_data

    def result_completion(self, url, data):

        headers = {
            'User-Agent': self.__user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            # 'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/x-www-form-urlencoded',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'origin': 'https://api.midtrans.com',
            'upgrade-insecure-requests': '1',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-dest': 'document',
            # 'referer': 'https://api.midtrans.com/v2/3ds/callback/54346410-0169-06685262-2812-4943-a3e3-c12623f9a472',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'priority': 'u=0, i',
        }

        response = self.__http_utils.post(url=url,
                                          headers=headers,
                                          data=urlencode(data)
                                          )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)

        midtrans_callback_url, midtrans_callback_data = self.get_from_auction_url(response.text, "veritrans")
        pnr = json.loads(midtrans_callback_data.get("response")).get("order_id").split("-")[2]
        return midtrans_callback_url, midtrans_callback_data, pnr

    @staticmethod
    def trip_challenge_url(html_str: str):
        trip_url = StringUtil.extract_between(html_str, "init3DSMethod('", "',")
        trip_challenge_data = StringUtil.extract_between(html_str, "/methodUrl', '", "', iframe")

        return trip_url, trip_challenge_data

    @staticmethod
    def result_completion_url(html_str: str):

        result_url = StringUtil.extract_between(html_str, '"action", "', '");')
        result_completion_data = StringUtil.extract_between(html_str, '"ares", "', '");')
        return result_url, {"ares": result_completion_data}

    @staticmethod
    def get_from_auction_url(html_str: str, form_id: str):
        tree = etree.HTML(html_str)
        if form_id:
            form_action = tree.xpath(f'//form[@id="{form_id}"]/@action')[0]
            inputs = tree.xpath(f'//form[@id="{form_id}"]//input[@type="hidden"]')
        else:
            form_action = tree.xpath(f'//form/@action')[0]
            inputs = tree.xpath(f'//form[1]//input[@type="hidden"]')

        data = {input_el.attrib['name']: input_el.attrib.get('value') for input_el in inputs}

        return form_action, data

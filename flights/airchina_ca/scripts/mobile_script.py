import json
import random
import urllib.parse
from typing import Optional

from common.errors import HttpModuleError, HttpModuleErrorStateEnum, ApiStateEnum, \
    APIError
from common.models import ProxyInfoModel
from common.utils.http_utils import CurlHttpUtil
from flights.airchina_ca.config import AirchinaConfig


class MobileScript:

    def __init__(self, proxy_info: Optional[ProxyInfoModel] = None):
        proxy_list = ['hk', 'tw', 'mo', 'vn']
        if proxy_info:
            proxy_info.region = random.choice(proxy_list)
        self.__http_util = CurlHttpUtil(proxy_info=proxy_info, auth_manage_cookie=False)
        self.__ua = AirchinaConfig.USER_AGENT

    def initialize_http(self):
        self.__http_util.initialize_http_util(impersonate="chrome136")

    def proxy(self):
        return self.__http_util.proxy_info.get_proxy_info_string()

    def close___(self):
        self.__http_util.close()

    def add_cookie(self, key, value):
        self.__http_util.add_cookie(key, value)

    def get_cookie(self, key):
        return self.__http_util.get_cookie(key)

    def get_cookie_all(self):
        return self.__http_util.get_cookie_all()

    def home(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            "Accept-Encoding": "gzip, deflate, br, zstd",
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        response = self.__http_util.get(
            url=f"https://m.airchina.com.cn/",
            headers=headers)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)

        return response.text

    def do(self, url, params):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            "Accept-Encoding": "gzip, deflate, br, zstd",
            'Param': params,
            'Pragma': 'no-cache',
            'Referer': 'https://m.airchina.com.cn/c/invoke/booking/showFlights@pg',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.__ua,
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        response = self.__http_util.get(
            url=url,
            headers=headers)

        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

    def login(self, data):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=UTF-8',
            'Origin': 'https://m.airchina.com.cn',
            'Pragma': 'no-cache',
            'Referer': 'https://m.airchina.com.cn/c/invoke/login@pg',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.__ua,
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        response = self.__http_util.post(
            url=f"https://m.airchina.com.cn/c/loginN",
            headers=headers, data=data)
        a = self.__http_util
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

    def logout(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Referer': 'https://m.airchina.com.cn/c/invoke/index@pg',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.__ua,
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        response = self.__http_util.get(
            url=f"https://m.airchina.com.cn/ac/c/logout",
            headers=headers)

        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def get_account(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Referer': 'https://m.airchina.com.cn/a                                                                                                                                                       c/c/invoke/index@pg',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.__ua,
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        response = self.__http_util.get(
            url=f"https://m.airchina.com.cn/ac/c/invoke/account@pg",
            headers=headers)

        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def view_login(self, data, params):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=UTF-8',
            'Origin': 'https://m.airchina.com.cn',
            'Pragma': 'no-cache',
            'Referer': 'https://m.airchina.com.cn/ac/c/invoke/account@pg',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.__ua,
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        response = self.__http_util.post(
            url=f"https://m.airchina.com.cn/ac/b/invoke.json?{urllib.parse.urlencode(params)}",
            headers=headers, data=data)

        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

    def get_token(self):
        import requests
        data = {
            "proxy": "http://030b68d24c4ed4241080__cr.hk:093031a774fac4d7@gw.dataimpulse.com:823"
        }
        headers = {
            'Content-Type': 'application/json; charset=UTF-8',
        }
        url = 'http://38.246.252.230:6000/process-request/'
        try:
            response = requests.post(url, timeout=60, headers=headers, json={
                "proxy": "http://030b68d24c4ed4241080__cr.hk:093031a774fac4d7@gw.dataimpulse.com:823"})
        except requests.exceptions.Timeout:
            raise APIError(ApiStateEnum.DX_SOLUTION_FAILURE)
        if response.status_code == 200:
            data = response.json()
            pretty_data = json.dumps(data, indent=4, ensure_ascii=False)
            return data
        else:
            raise APIError(ApiStateEnum.DX_SOLUTION_FAILURE)

    def show_flights(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Referer': 'https://m.airchina.com.cn/c/invoke/qryFlights@pg',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            "Accept-Encoding": "gzip, deflate, br, zstd",
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.__ua,
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        response = self.__http_util.get(
            url=f"https://m.airchina.com.cn/c/invoke/booking/showFlights@pg",
            headers=headers)

        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def search_invoke(self, data, params):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            "Accept-Encoding": "gzip, deflate, br, zstd",
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=UTF-8',
            'Origin': 'https://m.airchina.com.cn',
            'Pragma': 'no-cache',
            'Referer': 'https://m.airchina.com.cn/c/invoke/booking/showFlightDetail@pg',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.__ua,
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        response = self.__http_util.post(
            url=f"https://m.airchina.com.cn/g/invoke.json?{urllib.parse.urlencode(params)}",
            headers=headers, data=data, timeout=60)

        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

    def invoke(self, data, params):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=UTF-8',
            'Origin': 'https://m.airchina.com.cn',
            'Pragma': 'no-cache',
            'Referer': 'https://m.airchina.com.cn/c/invoke/booking/showFlightDetail@pg',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.__ua,
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        response = self.__http_util.post(
            url=f"https://m.airchina.com.cn/ac/g/invoke.json?{urllib.parse.urlencode(params)}",
            headers=headers, data=data, timeout=60)

        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

    def risky_invoke(self, data, params):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=UTF-8',
            'Origin': 'https://m.airchina.com.cn',
            'Pragma': 'no-cache',
            'Referer': 'https://m.airchina.com.cn/ac/c/invoke/booking/showFlights@pg',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.__ua,
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'X-Tingyun': 'c=B|P_GM9l-4Ts0;x=c1ca2811c283418f',

        }
        response = self.__http_util.post(
            url=f"https://m.airchina.com.cn/ac/g/invoke.json?{urllib.parse.urlencode(params)}",
            headers=headers, data=data)

        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

    def invoke_b(self, data, params):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=UTF-8',
            'Origin': 'https://m.airchina.com.cn',
            'Pragma': 'no-cache',
            'Referer': 'https://m.airchina.com.cn/b/invoke/booking/addOrderPassenger@pg',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.__ua,
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        response = self.__http_util.post(
            url=f"https://m.airchina.com.cn/b/invoke.json?{urllib.parse.urlencode(params)}",
            headers=headers, data=data)

        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

    def invoke_c(self, data, params, referer="'https://m.airchina.com.cn/c/invoke/booking/showFlightDetail@pg'"):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=UTF-8',
            'Origin': 'https://m.airchina.com.cn',
            'Pragma': 'no-cache',
            'Referer': referer,
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.__ua,
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        response = self.__http_util.post(
            url=f"https://m.airchina.com.cn/c/invoke.json?{urllib.parse.urlencode(params)}",
            headers=headers, data=data)

        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

    def invoke_h(self, data, params):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=UTF-8',
            'Origin': 'https://m.airchina.com.cn',
            'Pragma': 'no-cache',
            'Referer': 'https://m.airchina.com.cn/ac/b/invoke/showOrders@pg',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.__ua,
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        response = self.__http_util.post(
            url=f"https://m.airchina.com.cn/ac/h/invoke.json?{urllib.parse.urlencode(params)}",
            headers=headers, data=data)

        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

    def invoke_g(self, data, params):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=UTF-8',
            'Origin': 'https://m.airchina.com.cn',
            'Pragma': 'no-cache',
            'Referer': 'https://m.airchina.com.cn/ac/b/invoke/showOrders@pg',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.__ua,
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        response = self.__http_util.post(
            url=f"https://m.airchina.com.cn/g/invoke.json?{urllib.parse.urlencode(params)}",
            headers=headers, data=data)

        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

    def pay(self, data, params):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=UTF-8',
            'Origin': 'https://m.airchina.com.cn',
            'Pragma': 'no-cache',
            'Referer': 'https://m.airchina.com.cn/c/invoke/cardPay@pg?countdown=355',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.__ua,
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        response = self.__http_util.post(
            url=f"https://m.airchina.com.cn/c/invoke.json?{urllib.parse.urlencode(params)}",
            headers=headers, data=data)

        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

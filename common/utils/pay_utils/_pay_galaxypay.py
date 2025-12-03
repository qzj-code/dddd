import urllib.parse
from typing import Optional

from common.errors import HttpModuleError, HttpModuleErrorStateEnum
from common.models import ProxyInfoModel
from common.utils.http_utils import TlsClientHttpUtil


class Paygalaxypay:

    def __init__(self, proxy_info: Optional[ProxyInfoModel]):

        self.__http_utils = TlsClientHttpUtil()
        self.__http_utils.initialize_http_util(proxy_info=proxy_info)
        self.__timeout = 60
        self.x_xsrf_cookie = None
        self.x_xsrf_token = None
        self.referer = None

    def pay_get(self, url, referer):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': referer,
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'cross-site',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }
        response = self.__http_utils.get(
            url=url,
            headers=headers, timeout=self.__timeout)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

    def international_setup(self, referer, transaction_id):
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://payment.galaxypay.vn',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': referer,
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        data = {
            "transactionID": transaction_id,
            "paymentSource": "MASTER"
        }
        response = self.__http_utils.post(url='https://payment.galaxypay.vn/international/setup',
                                          headers=headers, data=data, timeout=self.__timeout)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

    def international_pay(self, transaction_id, reference_id, referer):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://payment.galaxypay.vn',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': referer,
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }
        data = {
            'transactionID': transaction_id,
            'referenceID': reference_id,
            'paymentSource': 'MASTER',
        }
        response = self.__http_utils.post(url=f'https://payment.galaxypay.vn/international/pay/{transaction_id}',
                                          headers=headers, data=urllib.parse.urlencode(data, doseq=True),
                                          timeout=self.__timeout)
        if response.status != 302 and response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def pay(self, url, data):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://payment.galaxypay.vn',
            'Pragma': 'no-cache',
            'Referer': 'https://payment.galaxypay.vn/',
            'Sec-Fetch-Dest': 'iframe',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-site',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        response = self.__http_utils.post(url=url,
                                          headers=headers, data=urllib.parse.urlencode(data, doseq=True),
                                          timeout=self.__timeout)
        if response.status != 200 and response.status != 302:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def paymentv2_get(self, url):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': 'https://www.vietjetair.com/',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'iframe',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-storage-access': 'active',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        }
        response = self.__http_utils.get(
            url=url,
            headers=headers, timeout=self.__timeout)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

    def token(self, referer):
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': referer,
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-storage-access': 'active',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        }
        response = self.__http_utils.get(
            url='https://paymentv2.galaxypay.vn/antiforgery/token',
            headers=headers, timeout=self.__timeout)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

    def paymentv2_query_checkout(self, data, referer, x_xsrf_cookie, x_xsrf_token):
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://paymentv2.galaxypay.vn',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': referer,
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-storage-access': 'active',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'x-xsrf-cookie': x_xsrf_cookie,
            'x-xsrf-token': x_xsrf_token,
        }
        response = self.__http_utils.post(
            url='https://paymentv2.galaxypay.vn/api/v1.0/secure/QueryCheckout', data=data,
            headers=headers, timeout=self.__timeout)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        self.x_xsrf_cookie = x_xsrf_cookie
        self.x_xsrf_token = x_xsrf_token
        self.referer = referer
        return response.json

    def paymentv2_create_payment(self, data):
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://paymentv2.galaxypay.vn',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': self.referer,
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-storage-access': 'active',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'x-xsrf-cookie': self.x_xsrf_cookie,
            'x-xsrf-token': self.x_xsrf_token,
        }
        response = self.__http_utils.post(
            url='https://paymentv2.galaxypay.vn/api/v1.0/secure/CreatePayment', data=data,
            headers=headers, timeout=self.__timeout)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

    def query_payment(self, data):
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://paymentv2.galaxypay.vn',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': self.referer,
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-storage-access': 'active',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'x-xsrf-cookie': self.x_xsrf_cookie,
            'x-xsrf-token': self.x_xsrf_token,
        }
        response = self.__http_utils.post(
            url='https://paymentv2.galaxypay.vn/api/v1.0/secure/queryPayment', data=data,
            headers=headers, timeout=self.__timeout)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

    def init_payment(self, data):
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://paymentv2.galaxypay.vn',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': self.referer,
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-storage-access': 'active',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'x-xsrf-cookie': self.x_xsrf_cookie,
            'x-xsrf-token': self.x_xsrf_token,
        }
        response = self.__http_utils.post(
            url='https://paymentv2.galaxypay.vn/api/v1.0/secure/initPayment', data=data,
            headers=headers, timeout=self.__timeout)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

    def check_payment_enrollment(self, data):
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://paymentv2.galaxypay.vn',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': self.referer,
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-storage-access': 'active',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'x-xsrf-cookie': self.x_xsrf_cookie,
            'x-xsrf-token': self.x_xsrf_token,
        }
        response = self.__http_utils.post(
            url='https://paymentv2.galaxypay.vn/api/v1.0/secure/checkPaymentEnrollment', data=data,
            headers=headers, timeout=self.__timeout)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

    def negotiate(self, referer):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'referer': referer,
            'x-requested-with': 'XMLHttpRequest',
            'x-signalr-user-agent': 'Microsoft SignalR/7.0 (7.0.14; Unknown OS; Browser; Unknown Runtime Version)',
            'origin': 'https://paymentv2.galaxypay.vn',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'priority': 'u=4',
            'cache-control': 'max-age=0',
        }
        response = self.__http_utils.post(
            url='https://paymentv2.galaxypay.vn/Hubs/DataHub/negotiate?negotiateVersion=1', data={},
            headers=headers, timeout=self.__timeout)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

    def process_result(self, data):
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://paymentv2.galaxypay.vn',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': self.referer,
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-storage-access': 'active',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'x-xsrf-cookie': self.x_xsrf_cookie,
            'x-xsrf-token': self.x_xsrf_token,
        }
        response = self.__http_utils.post(
            url='https://paymentv2.galaxypay.vn/api/v1.0/secure/processResult', data=data,
            headers=headers, timeout=self.__timeout)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

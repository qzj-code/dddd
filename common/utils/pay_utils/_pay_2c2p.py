import json
import urllib.parse
from typing import Optional

from common.errors import HttpModuleError, HttpModuleErrorStateEnum, ServiceStateEnum, ServiceError
from common.models import ProxyInfoModel
from common.utils.http_utils import RequestsHttpUtil


class Pay2c2p:

    def __init__(self, proxy_info: ProxyInfoModel,
                 user_agent: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                 timeout: int = 60):

        self.__http_utils = RequestsHttpUtil()
        self.__http_utils.initialize_http_util(proxy_info=proxy_info)
        self.__user_agent = user_agent
        self.timeout = timeout

    def api_redirect(self, data):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://nokair-api.ezypayment.sabre.com',
            'Pragma': 'no-cache',
            'Referer': 'https://nokair-api.ezypayment.sabre.com/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        encoded_params = Pay2c2p.dict_to_data_text(data, True)
        response = self.__http_utils.post(
            url='https://pays.2c2p.com/nokair/api/redirect',
            headers=headers,
            data=encoded_params
        )
        if response.status != 302:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def redirect_accept(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Referer': 'https://nokair-api.ezypayment.sabre.com/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        response = self.__http_utils.get(
            url="https://pays.2c2p.com/nokair/api/redirect/Accept",
            headers=headers
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def check_promotion(self, data):
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://pays.2c2p.com',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': 'https://pays.2c2p.com/nokair/api/redirect/Accept',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        response = self.__http_utils.post(
            url='https://pays.2c2p.com/nokair/api/redirect/CheckPromotion',
            headers=headers,
            data=data
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def api_redirect_accept(self, data):
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://pays.2c2p.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://pays.2c2p.com/nokair/api/redirect/Accept',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        response = self.__http_utils.post(
            url='https://pays.2c2p.com/nokair/api/redirect/Accept',
            headers=headers,
            data=data
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

    def twoc_twop(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-site"
        }
        response = self.__http_utils.get(
            url='https://pays.2c2p.com/nokair/api/Redirect/TwoCTwoP',
            headers=headers,
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def authpayment(self, payment_request):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-site"
        }
        data = {
            'paymentRequest': payment_request,
        }
        encoded_params = Pay2c2p.dict_to_data_text(data, True)

        response = self.__http_utils.post(
            url="https://t.2c2p.com/storedcardpaymentv2/authpayment.aspx",
            headers=headers,
            data=encoded_params
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def pgw_return_url(self, payment_response):
        headers = {
            "Host": "pays.2c2p.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://pays.2c2p.com",
            "Connection": "keep-alive",
            "Referer": "https://pays.2c2p.com/nokair/api/redirect/Accept",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1"
        }
        data = {
            'paymentResponse': payment_response,
        }
        encoded_params = Pay2c2p.dict_to_data_text(data, True)
        response = self.__http_utils.post(
            url="https://pays.2c2p.com/NokAir/API/Callback/PGWReturnUrl",
            headers=headers,
            data=encoded_params
        )
        if response.status != 302:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def ccresult(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Referer': 'https://t.2c2p.com/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-site',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        response = self.__http_utils.get(
            url="https://pays.2c2p.com/nokair/api/Redirect/CCResult",
            headers=headers
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    @classmethod
    def dict_to_data_text(cls, data: dict, use_url_encoding: Optional[bool] = False) -> str:
        """
        Dict对象转data
        :param data:
        :param use_url_encoding:
        :return:
        """

        def process_value(value, use_url_encoding):
            if isinstance(value, dict):
                value = json.dumps(value)
                if use_url_encoding:
                    value = urllib.parse.quote(value)
            elif use_url_encoding and not isinstance(value, (int, float)):
                value = urllib.parse.quote(value)
            return value

        return "&".join(
            [f"{key}={process_value(value, use_url_encoding)}" for key, value in data.items()]
        )

    def token(self, url):
        """

        Args:
            url:https://pgw-ui.2c2p.com/payment/4.1/#/token/kSAops9Zwhos8hSTSeLTUQaSFTekQRhwA2Dxk4ZmIMv5yMd5QoCEWl6I2FSt1WVV25eGQeUVoa4X8PUq9KUBsTdLXhdqN8hrB%2fC1bcyV199xL0ZOW%2bF0LuIZKwbJdHOn

        Returns:

        """
        headers = {
            "User-Agent": self.__user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Connection": "keep-alive",
            "Referer": "https://tnu-sapaygw.crane.aero/",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Priority": "u=0, i"
        }
        response = self.__http_utils.get(url=url, headers=headers)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def post_pay(self, payment_token: str, client_ip: str, client_id: str, payment_data: dict,
                 update_headers: dict = None):
        """

        Args:
            update_headers:
            payment_token:
            client_ip:
            client_id:
            payment_data:

        Returns:

        """
        headers = {
            "User-Agent": self.__user_agent,
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Origin": "https://pgw-ui.2c2p.com",
            "Connection": "keep-alive",
            "Referer": "https://pgw-ui.2c2p.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Priority": "u=0",
            "TE": "trailers"
        }
        if update_headers:
            headers.update(update_headers)
        data = {
            "paymentToken": payment_token,
            "clientIP": client_ip,
            'locale': 'en',
            "responseReturnUrl": "https://pgw-ui.2c2p.com/payment/4.1/#/info/",
            "clientID": client_id,
            "payment": {
                "code": {
                    "channelCode": "CC"
                },
                "data": payment_data
            }
        }
        response = self.__http_utils.post(url="https://pgw.2c2p.com/payment/4.1/Payment", headers=headers,
                                          data=data, timeout=60)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        if response.json.get('respCode', "") != "2000":
            raise ServiceError(ServiceStateEnum.BOOKING_PAYMENT_DECLINED)
        return response.json

    def transaction_status(self, payment_token, client_id, update_headers: dict = None):
        """

        Args:
            payment_token:
            client_id:
            update_headers:

        Returns:

        """
        headers = {
            "User-Agent": self.__user_agent,
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Origin": "https://pgw-ui.2c2p.com",
            "Connection": "keep-alive",
            "Referer": "https://pgw-ui.2c2p.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site"
        }
        if update_headers:
            headers.update(update_headers)
        data = {
            "paymentToken": payment_token,
            "additionalInfo": True,
            "clientID": client_id
        }
        response = self.__http_utils.post(url="https://pgw.2c2p.com/payment/4.1/transactionStatus",
                                          headers=headers,
                                          data=data)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        if response.json.get('respCode', "") != "2000":
            raise ServiceError(ServiceStateEnum.BOOKING_PAYMENT_DECLINED)
        return response.json

    def payment_auth(self, data):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://search.lionairthai.com',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': 'https://search.lionairthai.com/',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'cross-site',
            'upgrade-insecure-requests': '1',
            'user-agent': self.__user_agent,
        }
        response = self.__http_utils.post(url='https://t.2c2p.com/SecurePayment/PaymentAuth.aspx',
                                          headers=headers, data=data, timeout=60)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def auth_payment(self, data):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://search.lionairthai.com',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': 'https://search.lionairthai.com/',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'cross-site',
            'upgrade-insecure-requests': '1',
            'user-agent': self.__user_agent,
        }
        response = self.__http_utils.post(url='https://pgwv2-a.2c2p.com/storedCardPaymentV2/AuthPayment.aspx',
                                          headers=headers, data=data, auth_redirect=True, timeout=60)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def get_now_ip(self):

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'origin': 'https://pgw-ui.2c2p.com',
            'priority': 'u=1, i',
            'referer': 'https://pgw-ui.2c2p.com/',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': self.__user_agent,
        }

        response = self.__http_utils.get(url='https://api.ipify.org/?format=json', headers=headers,
                                         timeout=self.timeout)
        if not response.json.get("ip"):
            raise ServiceError(ServiceStateEnum.SERVICE_ERROR, "当前ip地址获取失败")

        return response.json

    def user_preference(self, data: dict):
        """

        Args:
            data:请求体

        Returns:

        """
        headers = {
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9',
            'access-control-allow-origin': '*',
            'content-type': 'application/json',
            'origin': 'https://pgw-ui.2c2p.com',
            'priority': 'u=1, i',
            'referer': 'https://pgw-ui.2c2p.com/',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': self.__user_agent,
            'x-pgw-api-type': 'UI',
            'x-pgw-client-additional-info': '{"browserLanguage":"zh-CN","browserScreenWidth":2560,"browserScreenHeight":1440,"browserColorDepth":24,"browserTZ":-480,"browserJavaEnabled":false,"browserJavaScriptEnabled":true}',
            'x-pgw-client-os': 'chrome 137.0.0-Windows 10',
            'x-pgw-client-type': 'WEB',
            'x-pgw-client-version': '4.1',
        }

        response = self.__http_utils.post(url='https://pgw.2c2p.com/payment/4.1/UserPreference', headers=headers,
                                          data=json.dumps(data), timeout=self.timeout)

        if response.json.get("respDesc", "") != "Success":
            raise ServiceError(ServiceStateEnum.SERVICE_ERROR, "支付初始化失败,user_preference")

        return response.json

    def payment_option(self, data):

        headers = {
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9',
            'access-control-allow-origin': '*',
            'content-type': 'application/json',
            'origin': 'https://pgw-ui.2c2p.com',
            'priority': 'u=1, i',
            'referer': 'https://pgw-ui.2c2p.com/',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': self.__user_agent,
            'x-pgw-api-type': 'UI',
            'x-pgw-client-additional-info': '{"browserLanguage":"zh-CN","browserScreenWidth":2560,"browserScreenHeight":1440,"browserColorDepth":24,"browserTZ":-480,"browserJavaEnabled":false,"browserJavaScriptEnabled":true}',
            'x-pgw-client-os': 'chrome 137.0.0-Windows 10',
            'x-pgw-client-type': 'WEB',
            'x-pgw-client-version': '4.1',
        }

        response = self.__http_utils.post(url='https://pgw.2c2p.com/payment/4.1/PaymentOption', headers=headers,
                                          data=json.dumps(data), timeout=self.timeout)
        if response.json.get("respDesc", "") != "Success":
            raise ServiceError(ServiceStateEnum.SERVICE_ERROR, "支付初始化失败,payment_option")

        return response.json

    def apmmcc_exchangerate(self, data):

        headers = {
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9',
            'access-control-allow-origin': '*',
            'content-type': 'application/json',
            'origin': 'https://pgw-ui.2c2p.com',
            'priority': 'u=1, i',
            'referer': 'https://pgw-ui.2c2p.com/',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': self.__user_agent,
            'x-pgw-api-type': 'UI',
            'x-pgw-client-additional-info': '{"browserLanguage":"zh-CN","browserScreenWidth":2560,"browserScreenHeight":1440,"browserColorDepth":24,"browserTZ":-480,"browserJavaEnabled":false,"browserJavaScriptEnabled":true}',
            'x-pgw-client-os': 'chrome 137.0.0-Windows 10',
            'x-pgw-client-type': 'WEB',
            'x-pgw-client-version': '4.1',
        }

        response = self.__http_utils.post(url='https://pgw.2c2p.com/payment/4.1/ExchangeRate/apmmccexchangerate',
                                          headers=headers, data=json.dumps(data), timeout=self.timeout)
        return response.json

    def pay_initialization(self, data):
        headers = {
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9',
            'access-control-allow-origin': '*',
            # 'content-length': '0',
            'origin': 'https://pgw-ui.2c2p.com',
            'priority': 'u=1, i',
            'referer': 'https://pgw-ui.2c2p.com/',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': self.__user_agent,
            'x-pgw-api-type': 'UI',
            'x-pgw-client-additional-info': '{"browserLanguage":"zh-CN","browserScreenWidth":2560,"browserScreenHeight":1440,"browserColorDepth":24,"browserTZ":-480,"browserJavaEnabled":false,"browserJavaScriptEnabled":true}',
            'x-pgw-client-os': 'chrome 137.0.0-Windows 10',
            'x-pgw-client-type': 'WEB',
            'x-pgw-client-version': '4.1',
        }

        response = self.__http_utils.post(url='https://pgw.2c2p.com/payment/4.1/Initialization', headers=headers,
                                          timeout=self.timeout)
        return response.json

    def card_token_info(self, data):

        headers = {
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9',
            'access-control-allow-origin': '*',
            'content-type': 'application/json',
            'origin': 'https://pgw-ui.2c2p.com',
            'priority': 'u=1, i',
            'referer': 'https://pgw-ui.2c2p.com/',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': self.__user_agent,
            'x-pgw-api-type': 'UI',
            'x-pgw-client-additional-info': '{"browserLanguage":"zh-CN","browserScreenWidth":2560,"browserScreenHeight":1440,"browserColorDepth":24,"browserTZ":-480,"browserJavaEnabled":false,"browserJavaScriptEnabled":true}',
            'x-pgw-client-os': 'chrome 137.0.0-Windows 10',
            'x-pgw-client-type': 'WEB',
            'x-pgw-client-version': '4.1',
        }

        response = self.__http_utils.post(url='https://pgw.2c2p.com/payment/4.1/CardTokenInfo', headers=headers,
                                          data=json.dumps(data), timeout=self.timeout)
        return response.json

    def exchange_rate(self, data):
        headers = {
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9',
            'access-control-allow-origin': '*',
            'content-type': 'application/json',
            'origin': 'https://pgw-ui.2c2p.com',
            'priority': 'u=1, i',
            'referer': 'https://pgw-ui.2c2p.com/',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': self.__user_agent,
            'x-pgw-api-type': 'UI',
            'x-pgw-client-additional-info': '{"browserLanguage":"zh-CN","browserScreenWidth":2560,"browserScreenHeight":1440,"browserColorDepth":24,"browserTZ":-480,"browserJavaEnabled":false,"browserJavaScriptEnabled":true}',
            'x-pgw-client-os': 'chrome 137.0.0-Windows 10',
            'x-pgw-client-type': 'WEB',
            'x-pgw-client-version': '4.1',
        }

        response = self.__http_utils.post(url='https://pgw.2c2p.com/payment/4.1/ExchangeRate', headers=headers,
                                          data=json.dumps(data), timeout=self.timeout)
        return response.json

    def payment_option_details(self, data):
        headers = {
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9',
            'access-control-allow-origin': '*',
            'content-type': 'application/json',
            'origin': 'https://pgw-ui.2c2p.com',
            'priority': 'u=1, i',
            'referer': 'https://pgw-ui.2c2p.com/',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': self.__user_agent,
            'x-pgw-api-type': 'UI',
            'x-pgw-client-additional-info': '{"browserLanguage":"zh-CN","browserScreenWidth":2560,"browserScreenHeight":1440,"browserColorDepth":24,"browserTZ":-480,"browserJavaEnabled":false,"browserJavaScriptEnabled":true}',
            'x-pgw-client-os': 'chrome 137.0.0-Windows 10',
            'x-pgw-client-type': 'WEB',
            'x-pgw-client-version': '4.1',
        }

        response = self.__http_utils.post(url='https://pgw.2c2p.com/payment/4.1/PaymentOptionDetails', headers=headers,
                                          data=json.dumps(data), timeout=self.timeout)
        return response.json

    def send_pay(self, data):

        headers = {
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9',
            'access-control-allow-origin': '*',
            'content-type': 'application/json',
            'origin': 'https://pgw-ui.2c2p.com',
            'priority': 'u=1, i',
            'referer': 'https://pgw-ui.2c2p.com/',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': self.__user_agent,
            'x-pgw-api-type': 'UI',
            'x-pgw-client-additional-info': '{"browserLanguage":"zh-CN","browserScreenWidth":2560,"browserScreenHeight":1440,"browserColorDepth":24,"browserTZ":-480,"browserJavaEnabled":false,"browserJavaScriptEnabled":true}',
            'x-pgw-client-os': 'chrome 137.0.0-Windows 10',
            'x-pgw-client-type': 'WEB',
            'x-pgw-client-version': '4.1',
        }

        response = self.__http_utils.post(url='https://pgw.2c2p.com/payment/4.1/Payment', headers=headers,
                                          data=json.dumps(data), timeout=self.timeout)
        if response.json.get("respCode") != "2000":
            raise ServiceError(ServiceStateEnum.SERVICE_ERROR, "提交支付失败,send_pay")
        return response.json

    def trans_action_status(self, data):
        headers = {
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9',
            'access-control-allow-origin': '*',
            'content-type': 'application/json',
            'origin': 'https://pgw-ui.2c2p.com',
            'priority': 'u=1, i',
            'referer': 'https://pgw-ui.2c2p.com/',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': self.__user_agent,
            'x-pgw-api-type': 'UI',
            'x-pgw-client-additional-info': '{"browserLanguage":"zh-CN","browserScreenWidth":2560,"browserScreenHeight":1440,"browserColorDepth":24,"browserTZ":-480,"browserJavaEnabled":false,"browserJavaScriptEnabled":true}',
            'x-pgw-client-os': 'chrome 137.0.0-Windows 10',
            'x-pgw-client-type': 'WEB',
            'x-pgw-client-version': '4.1',
        }

        response = self.__http_utils.post(url='https://pgw.2c2p.com/payment/4.1/transactionStatus', headers=headers,
                                          data=json.dumps(data), timeout=self.timeout)
        return response.json

    def payment_response(self, data):
        headers = {
            'User-Agent': self.__user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Content-Type': 'application/x-www-form-urlencoded',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'origin': 'https://pgw-ui.2c2p.com',
            'upgrade-insecure-requests': '1',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://pgw-ui.2c2p.com/',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'priority': 'u=0, i',
        }
        response = self.__http_utils.post(
            url='https://th.vietjetair.com/payment/2c2p/standard/paymentresponse',
            headers=headers,
            data=urllib.parse.urlencode(data),
            timeout=self.timeout
        )

    def ref_xindex(self, json_data: dict):
        headers = {
            "user-agent": self.__user_agent,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "accept-language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "accept-encoding": "gzip, deflate, br, zstd",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://ibooking.thaiairways.com",
            "referer": "https://ibooking.thaiairways.com/",
            "upgrade-insecure-requests": "1",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "cross-site",
            "sec-fetch-user": "?1",
            "priority": "u=0, i",
            "te": "trailers"
        }
        response = self.__http_utils.post(
            url='https://tgpayment.2c2p.com/redirect/Payment/RefXIndex',
            headers=headers,
            timeout=self.timeout, data=urllib.parse.urlencode(json_data), auth_redirect=False
        )
        if response.status != 302:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def get_payment_accept(self):
        headers = {
            "user-agent": self.__user_agent,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "accept-language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "accept-encoding": "gzip, deflate, br, zstd",
            "referer": "https://ibooking.thaiairways.com/",
            "upgrade-insecure-requests": "1",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "cross-site",
            "sec-fetch-user": "?1",
            "priority": "u=0, i",
            "te": "trailers"
        }
        response = self.__http_utils.get(
            url='https://tgpayment.2c2p.com/redirect/Payment/Accept',
            headers=headers,
            timeout=self.timeout
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def get_server_public_key(self):
        headers = {
            "user-agent": self.__user_agent,
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "accept-encoding": "gzip, deflate, br, zstd",
            "content-type": "application/json; charset=utf-8",
            "x-requested-with": "XMLHttpRequest",
            "referer": "https://tgpayment.2c2p.com/redirect/Payment/Accept",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "priority": "u=0",
            "te": "trailers"
        }
        response = self.__http_utils.get(
            url='https://tgpayment.2c2p.com/redirect/Payment/GetServerPublicKey',
            headers=headers,
            timeout=self.timeout
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status
                                  )
        return response.json

    def get_card_type(self, json_data: dict):
        headers = {
            "user-agent": self.__user_agent,
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "accept-encoding": "gzip, deflate, br, zstd",
            "content-type": "application/json",
            "x-requested-with": "XMLHttpRequest",
            "origin": "https://tgpayment.2c2p.com",
            "referer": "https://tgpayment.2c2p.com/redirect/Payment/Accept",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "priority": "u=0",
            "te": "trailers"
        }
        response = self.__http_utils.post(
            url='https://tgpayment.2c2p.com/redirect/Payment/GetCardType',
            headers=headers,
            data=json.dumps(json_data),
            timeout=self.timeout
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status
                                  )
        return response.json

    def post_payment_accept(self, json_data: dict):
        headers = {
            "user-agent": self.__user_agent,
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "accept-encoding": "gzip, deflate, br, zstd",
            "content-type": "application/json",
            "x-requested-with": "XMLHttpRequest",
            "origin": "https://tgpayment.2c2p.com",
            "referer": "https://tgpayment.2c2p.com/redirect/Payment/Accept",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "priority": "u=0",
            "te": "trailers"
        }
        response = self.__http_utils.post(
            url='https://tgpayment.2c2p.com/redirect/Payment/Accept',
            headers=headers,
            data=json.dumps(json_data),
            timeout=self.timeout
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status
                                  )
        return response.json

    def do_two_ct_wop(self, redirect_url):
        """

        Args:
            redirect_url:

        Returns:

        """
        headers = {
            "user-agent": self.__user_agent,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "accept-language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "accept-encoding": "gzip, deflate, br, zstd",
            "referer": "https://tgpayment.2c2p.com/redirect/Payment/Accept",
            "upgrade-insecure-requests": "1",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "priority": "u=0, i",
            "te": "trailers"
        }
        response = self.__http_utils.get(
            url="https://tgpayment.2c2p.com" + redirect_url,
            headers=headers,
            timeout=self.timeout
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def auth_payment_aspx(self, url: str, request_data: dict):
        """

        Args:
            request_data: paymentRequest
            url:"https://t.2c2p.com/storedcardpaymentv2/authpayment.aspx"

        Returns:

        """
        headers = {
            "user-agent": self.__user_agent,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "accept-language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "accept-encoding": "gzip, deflate, br, zstd",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://tgpayment.2c2p.com",
            "referer": "https://tgpayment.2c2p.com/",
            "upgrade-insecure-requests": "1",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-site",
            "priority": "u=0, i",
            "te": "trailers"
        }
        response = self.__http_utils.post(
            url=url,
            headers=headers,
            timeout=self.timeout, data=urllib.parse.urlencode(request_data)
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def pgw_return(self, url: str, response_data: dict):
        """

        Args:
            response_data: paymentResponse
            url:"https://tgpayment.2c2p.com/Redirect/Payment/PGWReturnUrl"

        Returns:

        """
        headers = {
            "user-agent": self.__user_agent,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "accept-language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "accept-encoding": "gzip, deflate, br, zstd",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://t.2c2p.com",
            "referer": "https://t.2c2p.com/",
            "upgrade-insecure-requests": "1",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-site",
            "priority": "u=0, i",
            "te": "trailers"
        }
        response = self.__http_utils.post(
            url=url,
            headers=headers,
            timeout=self.timeout, data=urllib.parse.urlencode(response_data), auth_redirect=True
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def success_result_call(self):
        headers = {
            "user-agent": self.__user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Connection": "keep-alive",
            "Referer": "https://tgpayment.2c2p.com/redirect/Payment/CCResult",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=0, i",
            "TE": "trailers"
        }
        response = self.__http_utils.get(
            url="https://tgpayment.2c2p.com/redirect/Payment/SuccessResultCallConfirmationURL",
            headers=headers,
            timeout=self.timeout
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def payment_pgw(self, url: str, request_data: dict):
        """

        Args:
            request_data: paymentRequest
            url:"https://pgwv2-a.2c2p.com/storedCardPaymentV2/MiGS25/PaymentPGW.aspx?CXID="

        Returns:

        """
        headers = {
            "user-agent": self.__user_agent,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "accept-language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "accept-encoding": "gzip, deflate, br, zstd",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://secure.ccavenue.com",
            "referer": "https://secure.ccavenue.com/",
            "upgrade-insecure-requests": "1",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "cross-site",
            "priority": "u=0, i",
            "te": "trailers"
        }
        response = self.__http_utils.post(
            url=url,
            headers=headers,
            timeout=self.timeout, data=urllib.parse.urlencode(request_data), auth_redirect=True
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

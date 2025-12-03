from common.errors import HttpModuleError, HttpModuleErrorStateEnum, ServiceError, ServiceStateEnum
from common.models import ProxyInfoModel
from common.utils.http_utils import CurlHttpUtil


class PayAliPay:
    def __init__(self, proxy_info: ProxyInfoModel, user_agent):
        self.__http_utils = CurlHttpUtil()
        self.__http_utils.initialize_http_util(proxy_info=None)
        self.__user_agent = user_agent

    def token(self, url):
        """

        Args:
            url:https://pgw-ui.dp.alipay.com/payment/4.1/?%23/token/kSAops9Zwhos8hSTSeLTUXcizS1jeKspr8SmlLApW2vFARMGu5ftZ2stjKnFZoORIkx1h4PANN29cbGitgAKTbiqtgfnAV2Pb0tJZeSmpPsqbEBLeMq20nmh%2BwBd6f%2FldaQ8KOwHu4IqTVgdH0ROEA%3D%3D

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
            "Origin": "https://pgw-ui.dp.alipay.com",
            "Connection": "keep-alive",
            "Referer": "https://pgw-ui.dp.alipay.com/",
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
            "responseReturnUrl": "https://pgw-ui.dp.alipay.com/payment/4.1/#/info/",
            "clientID": client_id,
            "payment": {
                "code": {
                    "channelCode": "CC"
                },
                "data": payment_data
            }
        }
        response = self.__http_utils.post(url="https://pgw.dp.alipay.com/payment/4.1/Payment", headers=headers,
                                          data=data, timeout=60)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        if response.json.get('respCode', "") != "2000":
            raise ServiceError(ServiceStateEnum.BOOKING_PAYMENT_DECLINED)
        return response.json

    def transaction_status(self, payment_token, client_id, update_headers: dict = None):
        headers = {
            "User-Agent": self.__user_agent,
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Origin": "https://pgw-ui.dp.alipay.com",
            "Connection": "keep-alive",
            "Referer": "https://pgw-ui.dp.alipay.com/",
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
        response = self.__http_utils.post(url="https://pgw.dp.alipay.com/payment/4.1/transactionStatus",
                                          headers=headers,
                                          data=data)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

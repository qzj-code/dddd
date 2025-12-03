import urllib.parse
import uuid
from typing import Optional

from common.errors import HttpModuleError, HttpModuleErrorStateEnum, ServiceStateEnum, ServiceError
from common.models import ProxyInfoModel
from common.utils.http_utils import CurlHttpUtil


class SecureAcceptance():
    def __init__(self, proxy_info: Optional[ProxyInfoModel], user_agent: str):
        self.__http_utils = CurlHttpUtil()
        self.__http_utils.initialize_http_util(proxy_info=proxy_info)
        self.user_agent = user_agent
        self.timeout = 60

    def silent_pay(self, data):
        """

        Args:
            data:

        Returns:

        """
        headers = {
            "Host": "secureacceptance.cybersource.com",
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://securepay.e-ghl.com",
            "Connection": "keep-alive",
            "Referer": "https://securepay.e-ghl.com/",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Priority": "u=0, i"
        }
        if type(data) is dict:
            data = urllib.parse.urlencode(data)
        response = self.__http_utils.post(url='https://secureacceptance.cybersource.com/silent/pay',
                                          data=data,
                                          headers=headers, auth_redirect=True, timeout=self.timeout)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def hybrid(self, cca_session_id, authenticity_token):
        """

        Args:
            cca_session_id:
            authenticity_token:
        Returns:

        """
        headers = {
            "Host": "secureacceptance.cybersource.com",
            "User-Agent": self.user_agent,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Referer": "https://secureacceptance.cybersource.com/silent/payer_authentication/hybrid?ccaAction=load",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://secureacceptance.cybersource.com",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "TE": "trailers"
        }

        data = {
            'ccaAction': 'check',
            'ccaSessionId': cca_session_id,
            'ccaClientSessionId': f"0_{str(uuid.uuid4())}",
            'ccaTiming': '4336',
            'authenticity_token': authenticity_token,
            'customer_browser_color_depth': '30',
            'customer_browser_language': 'en-US',
            'customer_browser_java_enabled': 'false',
            'customer_browser_screen_height': '1440',
            'customer_browser_screen_width': '2560',
            'customer_browser_time_difference': '-480',
            '__inner_width': '1043',
            '__inner_height': '1302',
        }
        response = self.__http_utils.post(
            url='https://secureacceptance.cybersource.com/silent/payer_authentication/hybrid',
            data=urllib.parse.urlencode(data),
            headers=headers, timeout=self.timeout)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        if 'CompleteEarly' not in response.text:
            raise ServiceError(ServiceStateEnum.BOOKING_PAYMENT_DECLINED)

    def hybrid_2(self, authenticity_token):
        """

        Args:
            authenticity_token:

        Returns:

        """
        headers = {
            "Host": "secureacceptance.cybersource.com",
            "User-Agent": self.user_agent,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Referer": "https://secureacceptance.cybersource.com/silent/payer_authentication/hybrid?ccaAction=load",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://secureacceptance.cybersource.com",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "TE": "trailers"
        }
        data = {
            'authenticity_token': authenticity_token,
            'ccaAction': 'completeEarly',
            'ccaErrorsHandled': '[]',
        }
        response = self.__http_utils.post(
            url='https://secureacceptance.cybersource.com/silent/payer_authentication/hybrid',
            data=urllib.parse.urlencode(data),
            headers=headers, timeout=self.timeout)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

import urllib.parse

from common.errors import HttpModuleError, HttpModuleErrorStateEnum, ServiceError, ServiceStateEnum
from common.utils._dict_utils import DictUtils
from common.utils.http_utils import CurlHttpUtil


class PayDoku:

    def __init__(self, http_utils: CurlHttpUtil, user_agent: str):
        self.__referer = None
        self.__http_utils = http_utils
        self.__ua = user_agent

    def receive(self, data: dict, origin: str):
        headers = {
            "Host": "pay.doku.com",
            "User-Agent": self.__ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": origin,
            "Connection": "keep-alive",
            "Referer": f"{origin}/",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
            "Priority": "u=0, i"
        }
        response = self.__http_utils.post(
            url="https://pay.doku.com/Suite/Receive",
            headers=headers,
            data=DictUtils.urlencode_flat_dict(data)
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status
                                  )
        if "DOKU Payment Page - Redirect" not in response.text:
            raise ServiceError(ServiceStateEnum.BOOKING_FAILURE_PAYMENT_RESULT_STATE_NOT_PASS,
                               "receive failed")

    def process_payment(self, mall_id: str, chain_merchant: str, inv: str):
        headers = {
            "Host": "pay.doku.com",
            "User-Agent": self.__ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://pay.doku.com",
            "Connection": "keep-alive",
            "Referer": "https://pay.doku.com/Suite/Receive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=0, i"
        }
        data = {
            "MALLID": mall_id,
            "CHAINMERCHANT": chain_merchant,
            "INV": inv
        }
        response = self.__http_utils.post(
            url=f"https://pay.doku.com/Suite/ProcessPayment?" + urllib.parse.urlencode(data),
            headers=headers, data=urllib.parse.urlencode({})
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status
                                  )
        if "DOKU Payment Page - Redirect" not in response.text:
            raise ServiceError(ServiceStateEnum.BOOKING_FAILURE_PAYMENT_RESULT_STATE_NOT_PASS,
                               "process_payment failed")
        self.__referer = f"https://pay.doku.com/Suite/ProcessPayment?" + urllib.parse.urlencode(data)
        return response.text

    def redirect_3ds2r(self, data: dict):
        headers = {
            "Host": "pay.doku.com",
            "User-Agent": self.__ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://pay.doku.com",
            "Connection": "keep-alive",
            "Referer": self.__referer,
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=0, i"
        }
        response = self.__http_utils.post(
            url=f"https://pay.doku.com/MPG/3DS2Redirect",
            headers=headers, data=urllib.parse.urlencode(data)
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status
                                  )
        if "MPG REDIRECT TO 3DS" not in response.text:
            raise ServiceError(ServiceStateEnum.BOOKING_FAILURE_PAYMENT_RESULT_STATE_NOT_PASS,
                               "redirect_3ds2r failed")
        return response.text

    def check_enrollment_cybersource(self, data):
        headers = {
            "Host": "pay.doku.com",
            "User-Agent": self.__ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://pay.doku.com",
            "Connection": "keep-alive",
            "Referer": "https://pay.doku.com/MPG/3DS2Redirect",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=0, i"
        }

        response = self.__http_utils.post(
            url=f"https://pay.doku.com/MPG/CheckEnrollmentCybersource",
            headers=headers, data=urllib.parse.urlencode(data)
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status
                                  )
        if "Submit Auth" not in response.text:
            raise ServiceError(ServiceStateEnum.BOOKING_FAILURE_PAYMENT_RESULT_STATE_NOT_PASS,
                               "check_enrollment_cybersource failed")
        return response.text

    def auth_acs(self, data: dict):
        headers = {
            "Host": "pay.doku.com",
            "User-Agent": self.__ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://pay.doku.com",
            "Connection": "keep-alive",
            "Referer": "https://pay.doku.com/MPG/CheckEnrollmentCybersource",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=0, i"
        }
        response = self.__http_utils.post(
            url=f"https://pay.doku.com/Suite/AuthACS",
            headers=headers, data=urllib.parse.urlencode(data)
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status
                                  )
        if "DOKU Payment Page - Redirect" not in response.text:
            raise ServiceError(ServiceStateEnum.BOOKING_FAILURE_PAYMENT_RESULT_STATE_NOT_PASS,
                               "auth_acs failed")
        return response.text

    def process_3ds_payment(self, url: str):
        """

        Args:
            url:https://pay.doku.com/Suite/Process3DSPayment?MALLID=10798266&CHAINMERCHANT=0&INV=6NSCAV16045875

        Returns:

        """
        headers = {
            "Host": "pay.doku.com",
            "User-Agent": self.__ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://pay.doku.com",
            "Connection": "keep-alive",
            "Referer": "https://pay.doku.com/Suite/AuthACS",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=0, i"
        }
        response = self.__http_utils.post(
            url=url,
            headers=headers, data=""
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        if "DOKU Payment Page - Redirect" not in response.text:
            raise ServiceError(ServiceStateEnum.BOOKING_FAILURE_PAYMENT_RESULT_STATE_NOT_PASS,
                               "process_3ds_payment failed")
        self.__referer = url
        return response.text

    def go_back(self, url: str, data: dict):
        """
        https://pay.doku.com/Suite/GoBack
        Args:
            data:
            url:

        Returns:

        """
        headers = {
            "Host": "pay.doku.com",
            "User-Agent": self.__ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://pay.doku.com",
            "Connection": "keep-alive",
            "Referer": self.__referer,
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=0, i"
        }
        response = self.__http_utils.post(
            url=url,
            headers=headers, data=urllib.parse.urlencode(data)
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        if "DOKU Payment Page" not in response.text:
            if "DOKU Payment Page - Redirect" not in response.text:
                raise ServiceError(ServiceStateEnum.BOOKING_FAILURE_PAYMENT_RESULT_STATE_NOT_PASS,
                                   "go_back(2) failed")
            raise ServiceError(ServiceStateEnum.BOOKING_FAILURE_PAYMENT_RESULT_STATE_NOT_PASS,
                               "go_back(1) failed")
        return response.text

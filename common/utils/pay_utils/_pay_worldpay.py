import urllib.parse
from typing import Optional

from common.errors import HttpModuleErrorStateEnum, HttpModuleError
from common.models import ProxyInfoModel
from common.utils.http_utils import CurlHttpUtil


class WorldPay:
    def __init__(self, proxy_info: Optional[ProxyInfoModel], user_agent: str):
        self.__http_utils = CurlHttpUtil()
        self.__http_utils.initialize_http_util(proxy_info=proxy_info)
        self.__user_agent = user_agent
        self.__timeout = 60

    def corporate(self, url, data):
        """
        https://hpp.worldpay.com/app/hpp/integration/wpg/corporate?OrderKey=HKAIRWEBAUD%5E2025052903884978WA&Ticket=001748916843384020v86VIhGyVEh3rNDuRPARA7S_nev532Ho8-a3s&source=https%3A%2F%2Fsecure.worldpay.com%2Fsc7
        Returns:

        """
        headers = {
            "user-agent": self.__user_agent,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.5",
            "accept-encoding": "gzip, deflate, br, zstd",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://easypay.travelsky.com.cn",
            "referer": "https://easypay.travelsky.com.cn/",
            "upgrade-insecure-requests": "1",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "cross-site",
            "priority": "u=0, i",
            "te": "trailers"
        }
        response = self.__http_utils.post(
            url=url,
            headers=headers, data=urllib.parse.urlencode(data), timeout=self.__timeout)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def cardtypes(self, base_url, card_number: str):
        headers = {
            "user-agent": self.__user_agent,
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.5",
            "accept-encoding": "gzip, deflate, br, zstd",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest",
            "origin": "https://hpp.worldpay.com",
            "referer": "https://hpp.worldpay.com/app/hpp/143-0/payment/start",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "te": "trailers"
        }
        response = self.__http_utils.post(
            url=f"{base_url}/rest/cardtypes",
            headers=headers, data=f"cardNumber={card_number}", timeout=self.__timeout)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def process(self, base_url, data: dict):
        headers = {
            "user-agent": self.__user_agent,
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.5",
            "accept-encoding": "gzip, deflate, br, zstd",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-hpp-ajax": "1",
            "x-requested-with": "XMLHttpRequest",
            "origin": "https://hpp.worldpay.com",
            "referer": "https://hpp.worldpay.com/app/hpp/143-0/payment/start",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "te": "trailers"
        }

        response = self.__http_utils.post(url=f"{base_url}/payment/multicard/process",
                                          data=urllib.parse.urlencode(data), headers=headers)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

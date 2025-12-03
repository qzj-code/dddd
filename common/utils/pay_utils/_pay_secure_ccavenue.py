import urllib.parse

from common.errors import HttpModuleError, HttpModuleErrorStateEnum
from common.models import ProxyInfoModel
from common.utils.http_utils import CurlHttpUtil


class PaySecureCcavenue:
    def __init__(self, proxy_info: ProxyInfoModel,
                 user_agent: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                 timeout: int = 60):
        self.__http_utils = CurlHttpUtil(auth_manage_cookie=False)
        self.__http_utils.initialize_http_util(proxy_info=proxy_info)
        self.__user_agent = user_agent
        self.__timeout = timeout

    def transaction_do(self, data: dict):
        headers = {
            "User-Agent": self.__user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://t.2c2p.com",
            "Connection": "keep-alive",
            "Referer": "https://t.2c2p.com/",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Priority": "u=0, i"
        }
        response = self.__http_utils.post(
            url='https://secure.ccavenue.com/transaction/transaction.do?command=initiateTransaction',
            headers=headers,
            data=urllib.parse.urlencode(data)
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def update_transaction(self, json_data: dict):
        headers = {
            "User-Agent": self.__user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://secure.ccavenue.com",
            "Connection": "keep-alive",
            "Referer": "https://secure.ccavenue.com/transaction/transaction.do?command=initiateTransaction",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Priority": "u=0, i"
        }
        response = self.__http_utils.post(
            url='https://secure.ccavenue.com/updateTransaction',
            headers=headers,
            data=urllib.parse.urlencode(json_data)
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def transaction_do_2(self, json_data: dict):
        headers = {
            "User-Agent": self.__user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://secure.ccavenue.com",
            "Connection": "keep-alive",
            "Referer": "https://secure.ccavenue.com/updateTransaction",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=0, i"
        }
        response = self.__http_utils.post(
            url='https://secure.ccavenue.com/transaction.do',
            headers=headers,
            data=urllib.parse.urlencode(json_data)
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

"""
Module: _danli_tls_util
Author: likanghui
Date: 2024-09-24

Description:
    This module provides functionalities for ...
"""
import json
import time
import traceback
from typing import Optional

import requests

from common.errors import RiskError, RiskStateEnum, HttpModuleError, \
    HttpModuleErrorStateEnum
from common.global_variable import GlobalVariable
from common.models import ProxyInfoModel
from common.models import ResponseData
from common.utils import LogUtil
from ._root_http_abstract import RootHttpAbstract
from ...decorators.http_log_decorator import http_log_decorator


class DanLiTlsUtils(RootHttpAbstract):

    def _cookie_update(self, **kwargs):
        pass

    def _headers_tuple_to_dict(self, **kwargs) -> dict:
        pass

    def _build_headers(self, **kwargs) -> dict:
        pass

    def __init__(self, url: str, proxy_info: Optional[ProxyInfoModel] = None,
                 auth_manage_cookie: Optional[bool] = False):
        super().__init__(proxy_info, auth_manage_cookie)
        self.__log = LogUtil("danLiTlsUtils")
        self.__url = url
        self.__proxy = {
            'proxy_ip': '',
            'proxy_port': 0,
            'proxy_user': ''
        }

    @http_log_decorator()
    def get(self, url: str, headers: dict, timeout: int = 60, redirect: bool = False, **keywords):
        return self.__execute_request(
            method="GET",
            url=url,
            headers=headers,
            timeout=timeout,
            redirect=redirect,
            **keywords
        )

    @http_log_decorator()
    def post(self, url: str, headers: dict, timeout: int = 60, data: Optional[any] = None, redirect: bool = False,
             **keywords):
        return self.__execute_request(
            method="POST",
            url=url,
            headers=headers,
            timeout=timeout,
            data=data,
            redirect=redirect,
            **keywords
        )

    @http_log_decorator()
    def delete(self, url: str, headers: dict, timeout: int = 60, data: Optional[any] = None, redirect: bool = False,
               **keywords):
        return self.__execute_request(
            method="DELETE",
            url=url,
            headers=headers,
            timeout=timeout,
            data=data,
            redirect=redirect,
            **keywords
        )

    @http_log_decorator()
    def put(self, url: str, headers: dict, timeout: int = 60, data: Optional[any] = None, redirect: bool = False,
            **keywords):
        return self.__execute_request(
            method="PUT",
            url=url,
            headers=headers,
            timeout=timeout,
            data=data,
            redirect=redirect,
            **keywords
        )

    @http_log_decorator()
    def patch(self, url: str, headers: dict, timeout: int = 60, data: Optional[any] = None, **keywords):
        pass

    def initialize_http_util(self, proxy_info: Optional[ProxyInfoModel] = None, **keywords):
        use_proxy = None
        if bool(proxy_info):
            if not bool(proxy_info.session):
                raise HttpModuleError(HttpModuleErrorStateEnum.SET_PROXY_FLIGHT,
                                      HttpModuleErrorStateEnum.PROXY_SESSION_CANNOT_BE_EMPTY.value)
            use_proxy = proxy_info
        else:
            if self._initialize_proxy_info():
                use_proxy = self.proxy_info

        if use_proxy:
            self.__proxy['proxy_ip'] = use_proxy.host
            self.__proxy['proxy_port'] = use_proxy.port
            self.__proxy['proxy_user'] = f'{use_proxy.get_proxy_username()}:{use_proxy.password}'

        _session = requests.session()
        _session.verify = False
        self.set_session(_session)

    def update_cookie(self, cookies):
        for i in cookies:
            self.add_cookie_string(i)

    def get_akm_cookie(self, url: str,
                       us_version: Optional[str] = "126.0.0.0",
                       succ_flag: Optional[str] = "~0~",
                       use_proxy: Optional[bool] = False):

        __data = {
            "appid": "m05cmm7ub8vm1pgasjpo8sdp9tl6mkzp",
            "jsUrl": url,
            "uaVersion": us_version,
            "succFlag": succ_flag,
            "isPost": False
        }

        if use_proxy:
            __data["proxyIp"] = self.proxy_dict[GlobalVariable.PROXY_HOST]
            __data["proxyPort"] = self.proxy_dict[GlobalVariable.PROXY_PORT]
            __data[
                "proxyAuth"] = f"{self.proxy_dict[GlobalVariable.PROXY_USERNAME]}:{self.proxy_dict[GlobalVariable.PROXY_PASSWORD]}"

        response = self.__session.request(
            url=f"{self.__url}/abck",
            method="POST",
            headers={
                'Content-Type': 'application/json'
            },
            json=__data,
            timeout=20
        )

        response_json = response.json()
        if response_json['code'] != "0":
            return False

        self.add_cookie_string(response_json['data'])
        return True

    def __execute_request(self, method: str, **keywords):
        """
        请求执行
        :param keywords:
        :return:
        """

        start_time = time.time()
        try:

            if keywords.get('data') is None:
                keywords['data'] = ''
            else:
                keywords['data'] = json.dumps(keywords['data'], separators=(',', ':'),
                                              ensure_ascii=False) if isinstance(keywords['data'], (dict, list)) else \
                    keywords['data']

            self.add_headers_cookie(headers=keywords['headers'])
            __data = {
                "method": method,
                "url": keywords['url'],
                "headers": keywords['headers'],
                "userAgent": "",
                "body": keywords['data'],
                "redirect": keywords['redirect'],
                "timeOut": keywords['timeout'],
                "appid": "m05cmm7ub8vm1pgasjpo8sdp9tl6mkzp"
            }
            if self.__proxy['proxy_ip'] is not None:
                __data["proxyIp"] = self.__proxy['proxy_ip']
                __data["proxyPort"] = self.__proxy['proxy_port']
                __data["proxyAuth"] = self.__proxy['proxy_user']

            # print(__data)
            response = self.get_session.request(
                url=f"{self.__url}/tls",
                method="POST",
                headers={
                    "accept-encoding": "gzip, deflate, br",
                    'Content-Type': 'application/json'
                },
                json=__data,
                timeout=keywords['timeout'] + 10  # 让TLs先超时
            )

            # print(response.text)
            response_json = response.json()
            if not response_json.get('httpCode') and response_json['code'] != "0":
                self.logger.error(response.json(), "第三方响应错误")
                raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_UNKNOWN_ABNORMAL)
            if int(response_json['httpCode']) == 0:
                self.logger.error(traceback.format_exc())
                if response.text.find("EOF") != -1:
                    raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_CONNECT_EOF)
                elif response.text.find("Timeout") != -1:
                    raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESULT_TIMEOUT)
                else:
                    raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_UNKNOWN_ABNORMAL)

            if 'cookies' in response_json:
                self.update_cookie(response_json['cookies'])
            if (response_json['httpCode'] == 428 and response_json['result'].find("verify_url") != -1 or
                    response_json['httpCode'] == 403 and response_json['result'].find("Access Denied") != -1):
                raise RiskError(RiskStateEnum.AKM_CHECK_FAILURE)
            if response_json['httpCode'] == 403 and response.text.find("_Incapsula_Resource") != -1:
                raise RiskError(RiskStateEnum.INCAPSULA_CHECK_FAILURE)
            if response.status_code == 403 and response_json['result'].find("Attention Required") != -1:
                raise RiskError(RiskStateEnum.CLOUD_FLARE_CHECK_FAILURE)
            if response_json['httpCode'] == 429 and response_json.get('headers').get('X-Kpsdk-Ct') is not None:
                raise RiskError(RiskStateEnum.KASADA_CHECK_FAILURE)
            return ResponseData(url=keywords['url'],
                                status=int(response_json['httpCode']),
                                headers=response_json["headers"],
                                text=response_json["result"],
                                body=response_json['result'])
        except Exception as e:
            raise e

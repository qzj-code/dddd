import traceback
from typing import Optional, Union, Literal

import requests
import requests.exceptions

from common.decorators.http_log_decorator import http_log_decorator
from common.errors import HttpModuleError, HttpModuleErrorStateEnum, RiskError, RiskStateEnum
from common.models import ProxyInfoModel, ResponseData
from common.utils import StringUtil
from common.utils.http_utils._root_http_abstract import RootHttpAbstract


class RequestsHttpUtil(RootHttpAbstract):

    @http_log_decorator()
    def delete(self, url: str, headers: dict, auth_redirect: Optional[bool] = False,
               data: Optional[Union[str, dict]] = None, timeout: int = 20) -> ResponseData:
        return self.__request(method='DELETE', url=url, data=data, headers=headers, auth_redirect=auth_redirect,
                              timeout=timeout)

    def _cookie_update(self, cookies):
        if self.auth_manage_cookie:
            return

        for key in cookies:
            self.add_cookie(key, cookies[key])

    def _headers_tuple_to_dict(self, headers) -> dict:
        headers_dict = {}
        for item in headers:
            if item == "set-cookies":
                headers_dict[StringUtil.to_pascal_case(item)] = self._cookies_to_string(headers[item])
                continue

            headers_dict[item] = headers[item]

        return headers_dict

    def _build_headers(self, headers) -> dict:
        """
            构建最终协议头
        Args:
            **kwargs:

        Returns:

        """

        # Cookie是否手动管理
        if self.auth_manage_cookie:
            return headers

        # 清除HttpCookie，使协议头Cookie生效
        self.session.cookies.clear()

        # 是否已存在Cookie关键字
        if "cookie" in headers or "Cookie" in headers:
            return headers

        # # 清除HttpCookie，使协议头Cookie生效
        # self.session.cookies.clear()
        cookie = self.get_cookies_string()
        if cookie and cookie != "":
            headers["Cookie"] = cookie
        return headers

    @http_log_decorator()
    def get(self, url: str, headers: dict, auth_redirect: Optional[bool] = False, timeout: int = 20) -> ResponseData:
        return self.__request(method='GET', url=url, headers=headers, auth_redirect=auth_redirect, timeout=timeout)

    @http_log_decorator()
    def post(self, url: str, headers: dict, data: Optional[Union[str, dict, list]] = None,
             json: Optional[Union[str, dict, list]] = None,
             auth_redirect: Optional[bool] = False, timeout: int = 20) -> ResponseData:
        return self.__request(method='POST', url=url, headers=headers, data=data, auth_redirect=auth_redirect,
                              timeout=timeout, json=json)

    @http_log_decorator()
    def patch(self, url: str, headers: dict, data: Optional[Union[str, dict]] = None,
              auth_redirect: Optional[bool] = False, timeout: int = 20) -> ResponseData:
        return self.__request(method='PATCH', url=url, headers=headers, data=data, auth_redirect=auth_redirect,
                              timeout=timeout)

    @http_log_decorator()
    def put(self, url: str, headers: dict, data: Optional[Union[str, dict]] = None,
            auth_redirect: Optional[bool] = False, timeout: int = 20) -> ResponseData:
        return self.__request(method='PUT', url=url, headers=headers, data=data, auth_redirect=auth_redirect,
                              timeout=timeout)

    def __request(self, method: Literal["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "TRACE", "PATCH"], url: str,
                  headers: dict,
                  data: Optional[Union[str, dict]] = None,
                  json: Optional[Union[str, dict]] = None,
                  auth_redirect: Optional[bool] = False, timeout: int = 20) -> ResponseData:
        headers = self._build_headers(headers)

        # submit_data = data if isinstance(data, str) else json.dumps(data, separators=(',', ':')) if data else ""

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                allow_redirects=auth_redirect,
                timeout=timeout,
                json=json
            )
            response_data = self.__response_to_data(response)
            self._cookie_update(response.cookies.get_dict())
            return response_data

        except requests.exceptions.Timeout:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESULT_TIMEOUT)
        except requests.exceptions.RequestException as e:
            self.logger.error(traceback.format_exc())
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_UNKNOWN_ABNORMAL)

    def __response_to_data(self, response):
        response_data: ResponseData = ResponseData(
            url=response.url,
            headers=self._headers_tuple_to_dict(response.headers),
            text=response.text,
            body=response.content,
            status=response.status_code
        )
        if response.status_code == 428 and response.text.find("verify_url") != -1:
            raise RiskError(RiskStateEnum.AKM_CHECK_FAILURE)
        elif response.status_code == 403 and response.text.find("Access Denied") != -1:
            raise RiskError(RiskStateEnum.AKM_CHECK_FAILURE)
        elif response.status_code == 403 and response.text.find("Just a moment") != -1:
            raise RiskError(RiskStateEnum.CLOUD_FLARE_CHECK_FAILURE)
        elif response.status_code == 403 and response.text.find("Attention Required") != -1:
            raise RiskError(RiskStateEnum.CLOUD_FLARE_CHECK_FAILURE)
        if response.status_code == 403 and response.text.find("_Incapsula_Resource") != -1:
            raise RiskError(RiskStateEnum.INCAPSULA_CHECK_FAILURE)
        if response.status_code == 403 and response.text.find("appId") != -1:
            raise RiskError(RiskStateEnum.PX_CHECK_FAILUR)
        return response_data

    def initialize_http_util(self, proxy_info: Optional[ProxyInfoModel] = None, proxy_type: str = "http", **kwargs):
        """
            This function is used to initialize the http util
        Args:
            proxy_type:
            proxy_info:
            **kwargs:

        Returns:

        """
        use_proxy = None
        if bool(proxy_info):
            if not bool(proxy_info.session):
                raise HttpModuleError(HttpModuleErrorStateEnum.SET_PROXY_FLIGHT,
                                      HttpModuleErrorStateEnum.PROXY_SESSION_CANNOT_BE_EMPTY.value)
            use_proxy = proxy_info
        else:
            if self._initialize_proxy_info():
                use_proxy = self.proxy_info

        self.session = requests.Session()
        if use_proxy:
            self.session.proxies.update({
                'http': f'{proxy_type}://{use_proxy.get_proxy_info_string()}',
                'https': f'{proxy_type}://{use_proxy.get_proxy_info_string()}'
            })
            if use_proxy.get_proxy_info_string().find('127.0.0.1') != -1:
                self.session.verify = False

        else:
            self.logger.warning(message="未设置代理信息")

    def __init__(self,
                 proxy_info: Optional[ProxyInfoModel] = None,
                 auth_manage_cookie: bool = True):
        super().__init__(proxy_info=proxy_info, auth_manage_cookie=auth_manage_cookie)

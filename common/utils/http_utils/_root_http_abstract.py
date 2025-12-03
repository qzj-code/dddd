"""
Module: _base_http
Author: Ciwei
Date: 2024-09-13

Description:
    HTTP接口基础类，HTTP组件实现，继承此类
"""

import copy
from abc import ABC, abstractmethod
from typing import Optional, Union

from common.models import ProxyInfoModel, ResponseData
from common.utils import StringUtil, LogUtil


class RootHttpAbstract(ABC):

    def __init__(self,
                 proxy_info: Optional[ProxyInfoModel] = None,
                 auth_manage_cookie: bool = True):
        """

        Args:
            proxy_info: 代理信息
            auth_manage_cookie: 自动管理Cookie，如果为False手动管理，为True组件内部处理
        """
        self.__session = None
        self.__proxy_info = copy.deepcopy(proxy_info) if proxy_info is not None else None
        self.__proxy_dict: Optional[dict] = None
        self.__auth_manage_cookie = auth_manage_cookie
        self.__cookie_dict = {}
        self.__log = LogUtil("HttpUtil")

    def close(self):
        if self.__session:
            self.__session.close()

    @property
    def auth_manage_cookie(self):
        return self.__auth_manage_cookie

    @property
    def logger(self):
        return self.__log

    @property
    def proxy_info(self):
        return self.__proxy_info

    def add_cookie_string(self, cookies_str):
        for i in cookies_str.split(";"):
            t = i.strip()
            key = StringUtil.extract_last_between(t, "=")
            if key is None:
                continue
            value = t[len(key) + 1:]
            if key and value:
                self.__cookie_dict[key] = value

    def add_headers_cookie(self, headers: dict):
        """
        添加Cookie字符串到headers
        :param headers:
        :return:
        """
        if not self.__auth_manage_cookie and 'Cookie' not in headers:
            headers['Cookie'] = self.get_cookies_string()

    @property
    def get_session(self):
        """
        获取Session对象
        :return:
        """
        return self.__session

    @abstractmethod
    def get(self, url: str, headers: dict, auth_redirect: Optional[bool] = False, timeout: int = 20) -> ResponseData:
        """
            get方法
        Args:
            auth_redirect: 是否自动重定向
            url: URL地址
            headers: 协议头

        Returns:

        """
        pass

    @abstractmethod
    def delete(self, url: str, headers: dict, auth_redirect: Optional[bool] = False,
               data: Optional[Union[str, dict]] = None, timeout: int = 20) -> ResponseData:
        """
            delete方法
        Args:
            auth_redirect: 是否自动重定向
            url: URL地址
            headers: 协议头
            data: 提交数据 str dict
        Returns:

        """
        pass

    @abstractmethod
    def post(self,
             url: str,
             headers: dict,
             data: Optional[Union[str, dict]] = None,
             auth_redirect: Optional[bool] = False, timeout: int = 20) -> ResponseData:
        """
            POST方法
        Args:
            auth_redirect:
            url: URL地址
            headers:  协议头
            data: 提交数据 str dict

        Returns:

        """
        pass

    @abstractmethod
    def put(self, url: str, headers: dict, data: Optional[Union[str, dict]] = None,
            auth_redirect: Optional[bool] = False, timeout: int = 20) -> ResponseData:
        pass

    def set_proxy_dict(self, value):
        """
        设置 ProxyDict 对象

        :param value: 包含代理配置信息的字典
        :return: None
        """
        self.__proxy_dict = value

    @property
    def proxy_dict(self) -> dict:
        """
        获取ProxyDict对象
        :return:
        """
        return self.__proxy_dict

    def set_session(self, value):
        """
        设置Session对象
        :param value:
        :return:
        """
        self.__session = value

    @abstractmethod
    def initialize_http_util(self, proxy_info: Optional[ProxyInfoModel] = None, **kwargs):
        pass

    @abstractmethod
    def _build_headers(self, **kwargs) -> dict:
        pass

    @abstractmethod
    def _headers_tuple_to_dict(self, **kwargs) -> dict:
        pass

    @abstractmethod
    def _cookie_update(self, **kwargs):
        pass

    def _cookies_to_string(self, cookie_string):
        """
            转换Cookie为字符串格式
        Args:
            cookie_string:

        Returns:

        """
        # 分割逗号分隔的 cookies
        cookies = cookie_string.split(',')
        cookie_dict = {}

        for cookie in cookies:
            # 分割 key=value 对
            key_value = cookie.split(';')[0].strip()
            if '=' in key_value:
                key, value = key_value.split('=', 1)
                cookie_dict[key.strip()] = value.strip()

        # 将字典转化为字符串，格式 key=value
        return ', '.join([f"{key}={value}" for key, value in cookie_dict.items()])

    def _initialize_proxy_info(self) -> bool:
        """
        初始化代理信息
        Returns:

        """
        if self.proxy_info is None:
            return False
        self.proxy_info.session = StringUtil.generate_random_string(10, True)
        return True

    def get_cookies_string(self):
        """
            获取Cookies 字符串形式
        Returns:

        """

        return ";".join([f"{key}={value}" for key, value in self.__cookie_dict.items()])

    def get_cookie(self, value):
        """
            获取单个Cookie
        Args:
            value:

        Returns:

        """
        return self.__cookie_dict[value]

    def add_cookie(self, key, value):
        if self.auth_manage_cookie:
            return False

        self.__cookie_dict[key] = value

    def add_cookies_string(self, cookies_string) -> bool:
        """
            添加Cookie，以字符串形式
        Args:
            cookies_string:

        Returns:

        """

        if self.auth_manage_cookie:
            return False

        cookies_array = cookies_string.split(';')
        for cookie in cookies_array:
            if cookie.find('=') == -1:
                continue
            key_value = cookie.split('=')[0]
            value = cookie.split('=')[1]
            self.__cookie_dict[key_value] = value

        return True

    def del_cookie(self, key):
        if self.auth_manage_cookie:
            return False

        del self.__cookie_dict[key]

    def clear_cookies(self):
        self.__cookie_dict.clear()

    def get_cookie_all(self):
        """
            获取所有Cookie
        Args:
            value:

        Returns:

        """
        return self.__cookie_dict

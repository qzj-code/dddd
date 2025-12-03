"""
Module: _response_data_util
Author: Ciwei
Date: 2024-09-24

Description: 
    HTTP响应数据
"""
import json
from typing import Optional


class ResponseData(object):

    def __init__(self,
                 url: str,
                 status: int,
                 headers: Optional[dict] = None,
                 text: Optional[str] = None,
                 body: Optional[bytes] = None):
        self.__url = url
        self.__headers = headers
        self.__text = text
        self.__body = body
        self.__status = status
        self.__error = None

    def set_error(self, error):
        self.__error = error

    @property
    def error(self):
        return self.__error

    @property
    def url(self) -> str:
        return self.__url

    @property
    def headers(self) -> dict:
        return self.__headers

    @property
    def text(self) -> str:
        return self.__text

    @property
    def json(self) -> Optional[dict]:
        """
            获取JSON格式响应
        Returns: 为JSON返回dict，不为Json返回None

        """
        try:
            return json.loads(self.__text)
        except json.decoder.JSONDecodeError:
            return None

    @property
    def body(self) -> bytes:
        return self.__body

    @property
    def status(self) -> int:
        return self.__status

    @property
    def location(self):
        location_address = next((value for key, value in self.__headers.items() if key == "Location" or key == "location"), None)
        return location_address

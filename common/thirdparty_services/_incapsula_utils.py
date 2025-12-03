from typing import Optional

import httpx

from common.errors import HttpModuleError, HttpModuleErrorStateEnum, APIError, ApiStateEnum
from common.models import ResponseData


class IncapsulaUtils:

    def __init__(self, http_utils, appid: str):
        self._http_utils = http_utils
        self.__appid = appid

    def auth_capsolver_reese84(self, url: str, aws: bool, user_agent: Optional[str] = None) -> ResponseData:
        """
        reese84 解决方案

        Args:
            url (str): 84js地址。
            aws (bool):
            user_agent (Optional[str]):

        Returns:
            Tuple[str, dict]: 返回 reese84 token 和 cookies 字典。
        """
        submit_data_84 = self._get_incapsula_84_data(url=url, user_agent=user_agent, aws=aws)

        reese84_response = self._post_reese84_data(
            url=url,
            reese84_data=submit_data_84,
            user_agent=user_agent,
        )
        if reese84_response.status != 200:
            HttpModuleError(
                HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                reese84_response.status,
            )

        return reese84_response.json['token']

    def _get_incapsula_84_data(self, url: str, aws: bool, user_agent: Optional[str] = None) -> ResponseData:
        """
        获取 Incapsula 计算数据

        Args:
            url (str): reese84 的文本 URL。
            aws (bool):
            user_agent (Optional[str]):


        Returns:
            dict: 返回 reese84 认证所需的计算数据。
        """

        data = {
            'url': url,
            'appid': self.__appid
        }

        if user_agent is not None:
            data['ua'] = user_agent

        response = httpx.post(url="http://api.zjdanli.com/incapsula/reese84",
                              timeout=httpx.Timeout(20), json=data)
        if response.status_code != 200:
            HttpModuleError(
                HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                response.status_code,
            )
        print(response.json())
        response_json = response.json()
        if response_json['code'] != 200:
            HttpModuleError(
                HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                response_json['code'],
            )
        if not response_json.get('succ', False):
            raise APIError(ApiStateEnum.INCAPSULA_SOLUTION_FAILURE)
        return response_json['data']

    def _post_reese84_data(self, url: str, reese84_data: dict, user_agent: str) -> ResponseData:
        """
        获取84tk
        Args:
            url (str): 请求的 URL。
            reese84_data (dict): 需要提交的 reese84 数据。
            user_agent (Optional[str]): 自定义的 User-Agent 头部信息。

        Returns:
            httpx.Response: 服务器返回的 HTTP 响应。
        """
        headers = {
            "Connection": "keep-alive",
            "sec-ch-ua-platform": "\"Windows\"",
            "User-Agent": user_agent,
            "Accept": "application/json; charset=utf-8",
            "Content-Type": "text/plain; charset=utf-8",
            "sec-ch-ua-mobile": "?0",
            "Origin": "https://booking.vietnamairlines.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "es,en-US;q=0.9,en;q=0.8"
        }

        response = self._http_utils.post(
            url=url,
            headers=headers,
            data=reese84_data,
            timeout=60
        )
        if response.status != 200:
            raise APIError(ApiStateEnum.INCAPSULA_SOLUTION_FAILURE)
        return response

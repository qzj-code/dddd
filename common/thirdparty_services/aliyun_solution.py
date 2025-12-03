"""
@Project     : zhongyi_flight
@Author      : ciwei
@Date        : 2024/8/3 10:03
@Description :
@versions    : 1.0.0.0
"""
import json
from typing import Optional

import requests

from common.errors import HttpModuleError, HttpModuleErrorStateEnum
from common.errors import APIError, ApiStateEnum
from common.models import ProxyInfoModel
from common.utils import StringUtil


class AliSlidingUtils:

    def __init__(self, proxy_info: Optional[ProxyInfoModel] = None):
        self.__session = requests.session()
        self.__session.verify = False
        if proxy_info:
            self.__session.proxies = {
                "http": f"http://{proxy_info.get_proxy_info_string()}",
                "https": f"http://{proxy_info.get_proxy_info_string()}"
            }

        else:
            self.__session.proxies = None

    def get_227(self):
        response = requests.get(url="http://47.242.223.131:3000/get227", timeout=60)
        response_json = response.json()

        data = {
            "a": response_json['a'],
            "t": response_json['t'],
            "n": response_json['n'],
            "p": "{\"ncbtn\":\"88.4749984741211|183|41.60000228881836|33.60000228881836|183|216.60000228881836|88.4749984741211|130.07500076293945\",\"umidToken\":\"T2gAOQ0FKm5feVjBZ6CHlXNTnQV7R5jT69dYWOZKkF1B7Go8ZoTrD7WFN-J2MLaMnDE=\",\"ncSessionID\":\"895d449c02a\",\"et\":\"1\"}",
            "scene": "nc_login",
            "asyn": "0",
            "lang": "cn",
            "v": "1",
            "callback": "jsonp_07163892427464109"
        }
        return self.analyze(data)

    def analyze(self, data):
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Referer": "https://booking.hkexpress.com/zh-CN/members/register",
            "Sec-Fetch-Dest": "script",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
            "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Microsoft Edge\";v=\"126\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }

        url = "https://cf.aliyun.com/nocaptcha/analyze.jsonp"
        response = self.__session.post(
            url=url,
            headers=headers,
            data=data, timeout=60
        )

        if response.status_code != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status_code)

        response_text = StringUtil.extract_between(response.text, "jsonp_07163892427464109(", ")")
        response_json = json.loads(response_text)
        if response_json['result']['code'] != 0:
            raise APIError(
                ApiStateEnum.ALI_SLIDING_SOLUTION_FAILURE
            )
        return response_json['result']['csessionid'], response_json['result']['value'], data['t']

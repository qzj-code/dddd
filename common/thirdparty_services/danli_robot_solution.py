import requests

from common.errors import APIError, ApiStateEnum
from common.utils import LogUtil


class AkamaiApi:

    def __init__(self, appid: str):
        self.appid = appid
        self._log = LogUtil("AkamaiApi")

    def akamai_ck_get(self, api_name: str):
        """
        发送一个POST请求到丹里Akamai API
        Args:
            api_name: API名称(对应网站)，用于构造URL的一部分。

        Returns:
            dict: 返回API的响应内容。

        """
        data = {
            'appid': self.appid,
        }
        headers = {
            'Content-Type': 'application/json;charset=UTF-8'
        }
        response = requests.post(f"http://api-usa.zjdanli.com/akamai/cookie/{api_name}",
                                 json=data, headers=headers)
        self._log.info(response.text)
        if response.json()['code'] != "0":
            raise APIError(ApiStateEnum.ERROR_INFO, response.json()['msg'])
        return response.json()


class KasadaApi:
    def __init__(self, appid: str):
        self.appid = appid
        self._log = LogUtil("KasadaApi")

    def kasada_ct_get(self, site_url: str):
        data = {
            'appid': self.appid,
            'siteUrl': site_url
        }
        headers = {
            'Content-Type': 'application/json;charset=UTF-8'
        }
        response = requests.post(f"http://api-ksd.zjdanli.com/kasada/ct",
                                 json=data, headers=headers)
        self._log.info(response.text)
        if response.json()['code'] != "0":
            raise APIError(ApiStateEnum.ERROR_INFO, response.json()['msg'])
        return response.json()

    def kasada_cd_get(self, st: str, ct: str):
        data = {
            'appid': self.appid,
            'st': st,
            'ct': ct
        }
        headers = {
            'Content-Type': 'application/json;charset=UTF-8'
        }
        response = requests.post(f"http://api-ksd.zjdanli.com/kasada/cd",
                                 json=data, headers=headers)
        self._log.info(response.text)
        if response.json()['code'] != "0":
            raise APIError(ApiStateEnum.ERROR_INFO, response.json()['msg'])
        return response.json()


class CloudFlareApi:
    def __init__(self, appid: str):
        self.appid = appid
        self._log = LogUtil("CloudFlareApi")

    def cloud_flare(self, host: str):
        data = {
            'appid': self.appid,
            'host': host
        }
        headers = {
            'Content-Type': 'application/json;charset=UTF-8'
        }
        response = requests.post(f"http://api-cf.zjdanli.com/cloudflare/getCookie",
                                 json=data, headers=headers)
        self._log.info(response.text)
        if response.json()['code'] != "0":
            raise APIError(ApiStateEnum.ERROR_INFO, response.json()['msg'])
        return response.json()['data']

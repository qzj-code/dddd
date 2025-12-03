import requests

from common.utils import LogUtil


class AkamaiApi:
    def __init__(self, http_util):
        self.__http_utils = http_util
        self._log = LogUtil("AkamaiApi")

    def primp_normal_test(self, ua: str, akm_url: str, requests_url: str):
        headers = {
            "sec-ch-ua-platform": "\"Windows\"",
            "user-agent": ua,
            "sec-ch-ua": '"Not A(Brand";v="99", "Chromium";v="133", "Google Chrome";v="133"',
            "content-type": "text/plain;charset=UTF-8",
            "sec-ch-ua-mobile": "?0",
            "accept": "*/*",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "accept-language": "zh-CN,zh;q=0.9",
            "priority": "u=1, i",
        }
        response = self.__http_utils.get(url=akm_url, headers=headers, )
        bm_sz = self.__http_utils.get_cookie('bm_sz')
        _abck = self.__http_utils.get_cookie('_abck')
        js_code = response.text
        data = {
            'url': requests_url,
            "bm_sz": bm_sz,
            # "ua": ua,  # 可以指定，如果不指定，就随机返回
            "js_text": js_code,
            "abck": _abck
        }
        result = requests.post("https://api.sakura-luo.top/get_sensor_data?token=test", json=data).json()
        ua = result.pop("ua", None)
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': "en-SG,en;q=0.9,en-US;q=0.8",
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://booking.flyscoot.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': ua,
        }
        response = self.__http_utils.post(url=akm_url, headers=headers, data=result)
        abck = self.__http_utils.get_cookie('_abck')
        return {'_abck': abck, 'bm_sz': bm_sz, 'ua': ua}

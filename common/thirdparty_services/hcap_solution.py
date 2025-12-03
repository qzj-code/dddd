import copy
import time
from random import randint
from urllib.parse import urlencode

from curl_cffi import requests

from common.decorators.retry_decorator import retry_decorator
from common.errors import ApiStateEnum, APIError
from common.models import ProxyInfoModel
from common.utils.http_utils import CurlHttpUtil


class HcaptchaUtils:
    def __init__(self, proxy_info: ProxyInfoModel):
        t = copy.deepcopy(proxy_info)
        t.region = "sg"
        self.__http_utils = CurlHttpUtil(t)
        self.__http_utils.initialize_http_util()

    @retry_decorator(retry_service_error_list=[(ApiStateEnum.ERROR_INFO, '')])
    def hcaptcha_get_token(self, site_key, host, v):
        headers = {
            "Host": "api.hcaptcha.com",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
            "Accept": "application/json",
            "Content-Type": "text/plain",
            "sec-ch-ua-mobile": "?0",
            "Origin": "https://newassets.hcaptcha.com",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://newassets.hcaptcha.com/",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-SG,en;q=0.9,en-US;q=0.8"
        }
        url = f"https://api.hcaptcha.com/checksiteconfig?v={v}&host={host}&sitekey={site_key}&sc=1&swa=1&spst=1"
        response = self.__http_utils.post(
            url=url, headers=headers)
        if response.json is None or response.json.get('c') is None or response.json.get('c').get('req') is None:
            raise APIError(ApiStateEnum.ERROR_INFO, 'generated_pass_UUID')
        req = response.json['c']['req']
        res = self.hcaptcha_getn(req, site_key, host)
        get_captcha_response = self._get_captcha(res,site_key)
        if get_captcha_response.get('generated_pass_UUID') is None:
            raise APIError(ApiStateEnum.ERROR_INFO, 'generated_pass_UUID')
        return get_captcha_response['generated_pass_UUID']

    def hcaptcha_getn(self, req, site_key, host):
        data = {
            "req": req,
            "langs": ["en-SG","en","en-US"],
            'siteKey': site_key,
            'host': host
        }
        url = 'https://mmbx7544jhfvbcgx74ub57yvju0swgqo.lambda-url.ap-east-1.on.aws/hcaptcha/getN'
        res = requests.post(url=url, json=data)
        return res.json()

    def _get_captcha(self, res,site_key):
        headers = {
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
            "sec-ch-ua-mobile": "?0",
            "Origin": "https://newassets.hcaptcha.com",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://newassets.hcaptcha.com/",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-SG,en;q=0.9,en-US;q=0.8"
        }

        url = f"https://api.hcaptcha.com/getcaptcha/{site_key}"
        response = self.__http_utils.post(url=url, headers=headers, data=urlencode(res['data']))
        return response.json


class Hcap:
    def __init__(self, http_utils):
        self.__http_utils = http_utils

    @retry_decorator(retry_service_error_list=[(ApiStateEnum.ERROR_INFO, '')])
    def hcap_req_get(self, site_key, host, v):
        headers = {
            "accept": "application/json",
            "accept-language": "en",
            "content-type": "text/plain",
            "origin": "https://newassets.hcaptcha.com",
            "referer": "https://newassets.hcaptcha.com/",
            "sec-ch-ua": "\"Chromium\";v=\"130\", \"Microsoft Edge\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
        }
        url = "https://api.hcaptcha.com/checksiteconfig"
        params = {
            "v": v,
            "host": host,
            "sitekey": site_key,
            "sc": "1",
            "swa": "1",
            "spst": "1"
        }
        cookies = {
            "session": "ed0ddf5c-af15-42df-a6d9-0693552c0d13",
            "ph_phc_fhS1E6ysPjT3r9Q1EO1kehh905Xla2NweqvcLnIYjO3_posthog": "%7B%22distinct_id%22%3A%2218f0dbdfe5ccb-059c6e81f57825-26031e51-100200-18f0dbdfe5d164d%22%2C%22%24device_id%22%3A%2218f0dbdfe5ccb-059c6e81f57825-26031e51-100200-18f0dbdfe5d164d%22%2C%22%24user_state%22%3A%22anonymous%22%2C%22%24sesid%22%3A%5B1714124786536%2C%2218f19cbcd19cc-0e393b862fb7f98-26031e51-100200-18f19cbcd1a659%22%2C1714124737817%5D%2C%22%24session_recording_enabled_server_side%22%3Afalse%2C%22%24autocapture_disabled_server_side%22%3Afalse%2C%22%24active_feature_flags%22%3A%5B%5D%2C%22%24enabled_feature_flags%22%3A%7B%7D%2C%22%24feature_flag_payloads%22%3A%7B%7D%7D",
            "hmt_id": "7b8b164c-29e4-4ffc-b97e-b105e48d98c5"
        }
        response = requests.post(url=url, headers=headers, params=params,cookies=cookies)
        if response.json() is None or response.json().get('c') is None or response.json().get('c').get('req') is None:
            raise APIError(ApiStateEnum.ERROR_INFO, 'generated_pass_UUID')
        req = response.json()['c']['req']
        res = self.hcaptcha_getn(response,req)
        response = self.getcaptcha(res,req)
        txn_token = response.json()['generated_pass_UUID']
        return txn_token



    def hcaptcha_getn(self,response,req):
        u = 'http://204.194.66.142:2000/getHcpData'
        data = {
            'href': 'https://booking.flyscoot.com/book/flight/one-way/SIN/2024-09-22/BNE?adult=1&child=0&infant=0',
            'hcpdata': req,
            'ua': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
        }
        headers = {
            'X-API-KEY': 'd791eddc440c9cfe973d16e0ffefecdd'
        }

        res = requests.post(url=u, headers=headers, json=data).json()
        return res

    def getcaptcha(self,res,req):
        n = res['data']
        motion_data = res['motion_data']
        ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
        headers = {
            "authority": "hcaptcha.com",
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "content-type": "application/x-www-form-urlencoded",
            "referer": "https://newassets.hcaptcha.com/",
            "sec-ch-ua": "\"Chromium\";v=\"130\", \"Microsoft Edge\";v=\"130\", \"Not)A=Brand\";v=\"99\"",
            "user-agent": ua
        }

        url = "https://hcaptcha.com/getcaptcha/81e02ccc-8862-41be-a7fe-c3f04ba0eb8c"
        data = {
            "v": "8524269",
            "sitekey": "81e02ccc-8862-41be-a7fe-c3f04ba0eb8c",
            "host": "booking.flyscoot.com",
            "hl": "zh",
            "motionData": motion_data,
            "pdc": "{\"s\":" + str(int(time.time() * 1000)) + ",\"n\":0,\"p\":1,\"gcs\":" + str(
                randint(2100, 5410)) + "}",
            "pem": "{\"csc\":" + str(randint(210, 541)) + ".30000019073486}",
            "n": n,
            "c": '{"type":"hsw","req":"' + req + '"}',
            "pst": False
        }
        response = requests.post(url=url, headers=headers, data=data)
        return response
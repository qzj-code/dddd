import hashlib
import json
import random
import time
import uuid
from typing import Optional
from urllib import parse

from common.errors import HttpModuleError, HttpModuleErrorStateEnum, ApiStateEnum, \
    APIError
from common.models import ProxyInfoModel
from common.utils import LogUtil
from common.utils.http_utils import CurlHttpUtil
from flights.airchina_ca.common import init_utils

LOG = LogUtil("AirchinaSearch")


class AppScript:

    def __init__(self, proxy_info: Optional[ProxyInfoModel] = None):
        self.book_obj = {}
        proxy_list = ['hk', 'tw', 'mo', 'vn']
        if proxy_info:
            proxy_info.region = random.choice(proxy_list)
        self.__http_util = CurlHttpUtil(proxy_info=proxy_info, auth_manage_cookie=False)
        self.mobile_type = 'Android'
        self.mobilesysver = '29'
        self.gt_token = '544877a3788fda492c4601797f4e0bd8'
        self.device_model = 'Google Pixel 5a'
        self.main_app_version = '73800'
        self.user_id = ''
        self.info_id = ''
        self.app_ver = '7.38.0'
        self.sys_ver = '29'
        self.mobile_type_extra = 'App'
        self.device_id = str(uuid.uuid4()).replace('-', '') + str(int(time.time() * 1000))
        self.ua = f'AirChina/{self.app_ver} (Android:{self.sys_ver})'
        self.sign_token1 = None
        self.sign_token2 = None
        self.session_id = None
        self.sign_ts_first = None
        self.aes_key = None
        self.token = hashlib.md5(self.device_id.encode(encoding='UTF-8')).hexdigest()
        self.dis_count_type = ''
        self.check_token = None

    def initialize_http(self):
        self.__http_util.initialize_http_util()

    def add_cookie(self, key, value):
        self.__http_util.add_cookie(key, value)

    def get_token(self):
        import requests
        headers = {
            'Content-Type': 'application/json; charset=UTF-8',
        }
        # url = 'http://38.246.252.230:6000/process-request/'
        url = 'http://154.9.24.141:6000/process-request/'
        try:
            response = requests.post(url, timeout=10, headers=headers, json={
                "proxy": "http://030b68d24c4ed4241080__cr.hk:093031a774fac4d7@gw.dataimpulse.com:823"})
        except requests.exceptions.Timeout:
            raise APIError(ApiStateEnum.DX_SOLUTION_FAILURE)
        if response.status_code == 200:
            data = response.json()
            pretty_data = json.dumps(data, indent=4, ensure_ascii=False)
            if not data or data.get('data') is None or data.get('data').get('token') is None:
                raise APIError(ApiStateEnum.DX_SOLUTION_FAILURE)
            self.check_token = data['data']['token']
            return data
        else:
            raise APIError(ApiStateEnum.DX_SOLUTION_FAILURE)

    def init_token(self):
        url = 'https://m.airchina.com.cn/airchina/gateway/v2.0/auth/registryInitSecretKey'
        req = {"IOSSYSTEMDATE": init_utils.make_io_ssystem_date()}
        req_json_string = json.dumps(req, separators=(',', ':'))
        data = {
            'deviceType': self.mobile_type,
            'mobileSysVer': self.mobilesysver,
            'appChannel': 'CA_AIR',
            'token': self.gt_token,
            'dxRiskToken': '',
            'userInfo4': init_utils.make_user_info4(req_json_string),
            'userInfo3': init_utils.make_user_info3(),
            'deviceModel': self.device_model,
            'userInfo2': init_utils.get_user_info2(self.gt_token, self.main_app_version),
            'userInfo1': self.main_app_version,
            'lang': 'zh_CN',
            'req': req_json_string,
            'mobileTypeExtra': self.mobile_type_extra,
            'timestamp': str(int(time.time() * 1000)),
        }
        s = init_utils.generate_canonical_string(data)
        first = hashlib.md5(s.encode(encoding='UTF-8')).hexdigest().upper()

        t = f'first-sign-token={first}&secretKey='
        t = hashlib.md5(t.encode(encoding='UTF-8')).hexdigest().upper()

        header = {
            'gtToken': self.gt_token,
            'infoID': self.info_id,
            'deviceType': self.mobile_type,
            'mobileType': self.mobile_type,
            'mobileTypeExtra': self.mobile_type_extra,
            'mainAppVersion': self.main_app_version,
            'deviceId': self.device_id,
            'User-Agent': self.ua,
            'sign-token': t,
            'sessionId': '',
            'securityToken': init_utils.make_init_security_token0(self.device_id),
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
            'Host': 'm.airchina.com.cn',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }

        response = self.__http_util.post(url=url, data=data, headers=header, timeout=10)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        self.sign_token1 = response.json['signToken']
        self.session_id = response.json['sessionId']
        self.sign_ts_first = self.sign_token1 + "-/-" + self.session_id

    def get_dynamic_secret_key(self):
        url = 'https://m.airchina.com.cn/airchina/gateway/v2.0/auth/getDynamicSecretKey'

        req = {"IOSSYSTEMDATE": init_utils.make_io_ssystem_date()}

        req_json_string = json.dumps(req, separators=(',', ':'))

        data = {
            'deviceType': self.mobile_type,
            'mobileSysVer': self.mobilesysver,
            'appChannel': 'CA_AIR',
            'token': self.gt_token,
            'dxRiskToken': '',
            'userInfo4': init_utils.make_user_info4(req_json_string),
            'userInfo3': init_utils.make_user_info3(),
            'deviceModel': self.device_model,
            'userInfo2': init_utils.get_user_info2(self.gt_token, self.main_app_version),
            'userInfo1': self.main_app_version,
            'lang': 'zh_CN',
            'req': req_json_string,
            'mobileTypeExtra': self.mobile_type_extra,
            'timestamp': str(int(time.time() * 1000)),
        }

        s = init_utils.generate_canonical_string(data)
        first = hashlib.md5(s.encode(encoding='UTF-8')).hexdigest().upper()

        t = f'first-sign-token={first}&secretKey='
        t = hashlib.md5(t.encode(encoding='UTF-8')).hexdigest().upper()
        header = {
            'gtToken': self.gt_token,
            'infoID': self.info_id,
            'deviceType': self.mobile_type,
            'mobileType': self.mobile_type,
            'mobileTypeExtra': self.mobile_type_extra,
            'mainAppVersion': self.main_app_version,
            'deviceId': self.device_id,
            'User-Agent': self.ua,
            'sign-token': t,
            'sessionId': self.session_id,
            'securityToken': init_utils.make_dynamic_secret_key_token1(self.session_id, self.sign_token1),
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
            'Host': 'm.airchina.com.cn',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }

        response = self.__http_util.post(url=url, data=data, headers=header, timeout=10)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        self.sign_token2 = response.json['signToken']
        self.aes_key = hashlib.md5(
            (self.sign_token1 + ';' + self.sign_token2).encode(encoding='UTF-8')).hexdigest().upper()[8:24]

    def get_external_home_page(self):
        req = {"newBannerUptime": "", "size": "M", "city": "PEK", "IOSSYSTEMDATE": init_utils.make_io_ssystem_date()}

        result = self.get_service('ACCommon', 'getExternalHomePage', req, {
            'deviceType': self.mobile_type,
            'mobileSysVer': self.mobilesysver,
            'appChannel': 'CA_AIR',
            'token': self.gt_token,
            'dxRiskToken': '',
            'userInfo4': '',
            'userInfo3': init_utils.make_user_info3(),
            'deviceModel': self.device_model,
            'userInfo2': init_utils.get_user_info2(self.gt_token, self.main_app_version),
            'userInfo1': self.main_app_version,
            'lang': 'zh_CN',
            'req': '',
            'mobileTypeExtra': self.mobile_type_extra,
            'timestamp': '',
        })
        return result

    def get_param_value(self):
        req = {
            "IOSSYSTEMDATE": init_utils.make_io_ssystem_date(),
            "keyId": "83"
        }
        send_data = {
            'deviceType': self.mobile_type,
            'mobileSysVer': self.mobilesysver,
            'appChannel': 'CA_AIR',
            'token': self.gt_token,
            'dxRiskToken': '',
            'userInfo4': '',
            'userInfo3': init_utils.make_user_info3(),
            'deviceModel': self.device_model,
            'userInfo2': init_utils.get_user_info2(self.gt_token, self.main_app_version),
            'userInfo1': self.main_app_version,
            'lang': 'zh_CN',
            'req': '',
            'mobileTypeExtra': self.mobile_type_extra,
            'timestamp': '',
        }
        result = self.get_service('ACCommon', 'getParamValue', req, send_data)
        return result

    def get_service(self, adapter, procedure, req, send_data):
        url = 'https://m.airchina.com.cn/airchina/gateway/v2.0/api/services/'

        req_json_string = json.dumps(req, separators=(',', ':'))

        data = send_data
        data['req'] = req_json_string
        data['userInfo4'] = init_utils.make_user_info4(req_json_string)
        data['timestamp'] = str(int(time.time() * 1000))
        string_to_sign = init_utils.generate_canonical_string(data)
        first = hashlib.md5(string_to_sign.encode(encoding='UTF-8')).hexdigest().upper()
        s = f'first-sign-token={first}&secretKey={self.sign_token2}'
        t = hashlib.md5(s.encode(encoding='UTF-8')).hexdigest().upper()
        data['req'] = parse.quote(req_json_string)
        header = {
            'adapter': adapter,
            'procedure': procedure,
            'gtToken': self.gt_token,
            'infoID': self.info_id,
            'deviceType': self.mobile_type,
            'mobileType': self.mobile_type,
            'mobileTypeExtra': self.mobile_type_extra,
            'mainAppVersion': self.main_app_version,
            'deviceId': self.device_id,
            'User-Agent': self.ua,
            'captchaClientToken': self.check_token + ":" if self.check_token else self.check_token,
            'captchatype': '1',
            'sign-token': t,
            'sessionId': self.session_id,
            'securityToken': init_utils.make_server_securityToken2(self.session_id, self.user_id, self.sign_token1,
                                                                   self.sign_token2),
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
            'Host': 'm.airchina.com.cn',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }
        LOG.info(data)
        query_string = init_utils.dict_to_custom_querystring(data)
        encrypt_data = init_utils.aes_encrypt(query_string, self.aes_key)
        html = self.__http_util.post(url=url, data=encrypt_data, headers=header, timeout=60)

        if 'ACCESS DENIED' in html.text:
            print('访问被拒绝，ERROR: ACCESS DENIED')
            result = {'code': '9', 'msg': 'ACCESS DENIED'}
            return result

        result = html.json
        if 'securityCode' in result:
            if result['securityCode'] == '2001':  # 需要重置token
                self.device_id = str(uuid.uuid4()).replace('-', '') + str(
                    int(time.time() * 1000 - 100000000))
                self.init_token()
                self.get_dynamic_secret_key()
                html = self.__http_util.post(url=url, data=data, headers=header, timeout=60)
                result = html.json
            elif result['securityCode'] == '3001':  # 需要重置deviceID
                self.device_id = str(uuid.uuid4()).replace('-', '') + str(
                    int(time.time() * 1000 - 100000000))
                self.init_token()
                self.get_dynamic_secret_key()
                html = self.__http_util.post(url=url, data=data, headers=header, timeout=60)
                result = html.json
            elif result['securityCode'] != '0000':
                print(f"未知错误，错误代码：{result['securityCode']}")
                return

        try:
            resp = parse.unquote_plus(init_utils.aes_decrypt(result['resp'], self.aes_key))
            LOG.info(resp)
            self.check_token = ""
            return json.loads(resp)
        except Exception as e:
            print(e)

    def search(self, airport_data, adult_count: int, child_count: int):
        t = int(time.time() * 1000)
        req = {
            "date": airport_data[0][2],
            "inf": "0",
            "isRecommend": "",
            "cnn": str(child_count),
            "flag": "0",
            "dst": airport_data[0][1],
            "org": airport_data[0][0],
            "airTransportType": "",
            "pwdMwd": "",
            "cabin": "Economy",
            "airTransportflag": "1",
            "version": "4",
            "token": self.token,
            "adt": str(adult_count),
            "transAmount": "",
            "airDepTransport": "",
            "isAutoQuery": "0",
            "ifstudent2020": "0",
            "mileageFlag": "0",
            "backDate": "",
            "layersPeople": self.dis_count_type,
            "airArrTransport": "",
            "IOSSYSTEMDATE": init_utils.make_io_ssystem_date(),
            "timestamp": str(t)
        }
        self.book_obj = {'dep': airport_data[0][0], 'arr': airport_data[0][1], 'dep_date': airport_data[0][2],
                         'adt': adult_count, 'cnn': child_count}
        send_data = {
            'deviceType': self.mobile_type,
            'mobileSysVer': self.mobilesysver,
            'appChannel': 'CA_AIR',
            'token': self.token,
            "captchaClientToken": self.check_token + ":",
            'dxRiskToken': '689db536xiIGhzv3SjhPhfC40QSzQoJLJw87Bsk3',
            'userInfo4': '',
            "captchatype": "1",
            'userInfo3': init_utils.make_user_info3(),
            'deviceModel': self.device_model,
            'userInfo2': init_utils.get_user_info2(self.gt_token, self.main_app_version),
            'userInfo1': self.main_app_version,
            'lang': 'zh_CN',
            'req': '',
            'mobileTypeExtra': self.mobile_type_extra,
            'timestamp': '',
        }
        url = 'https://m.airchina.com.cn/airchina/gateway/v2.0/api/services/'
        req_json_string = json.dumps(req, separators=(',', ':'))
        data = send_data
        data['req'] = req_json_string
        data['userInfo4'] = init_utils.make_user_info4(req_json_string)
        data['timestamp'] = str(int(time.time() * 1000))
        string_to_sign = init_utils.generate_canonical_string(data)
        first = hashlib.md5(string_to_sign.encode(encoding='UTF-8')).hexdigest().upper()
        s = f'first-sign-token={first}&secretKey={self.sign_token2}'
        t = hashlib.md5(s.encode(encoding='UTF-8')).hexdigest().upper()
        data['req'] = parse.quote(req_json_string)
        header = {
            'adapter': 'ACFlight',
            'procedure': 'getACEInfomationTwo',
            'gtToken': self.gt_token,
            'infoID': self.info_id,
            'deviceType': self.mobile_type,
            'mobileType': self.mobile_type,
            'mobileTypeExtra': self.mobile_type_extra,
            'mainAppVersion': self.main_app_version,
            'deviceId': self.device_id,
            'User-Agent': self.ua,
            'captchaClientToken': self.check_token,
            'captchatype': '1',
            'sign-token': t,
            'sessionId': self.session_id,
            'securityToken': init_utils.make_server_securityToken2(self.session_id, self.user_id, self.sign_token1,
                                                                   self.sign_token2),
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
            'Host': 'm.airchina.com.cn',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }
        LOG.info(json.dumps(data))
        query_string = init_utils.dict_to_custom_querystring(data)
        encrypt_data = init_utils.aes_encrypt(query_string, self.aes_key)
        response = self.__http_util.post(url=url, data=encrypt_data, headers=header, timeout=60)

        result = response.json
        if 'securityCode' in result:
            if result['securityCode'] == '2001':  # 需要重置token
                self.device_id = str(uuid.uuid4()).replace('-', '') + str(
                    int(time.time() * 1000 - 100000000))
                self.init_token()
                self.get_dynamic_secret_key()
                response = self.__http_util.post(url=url, data=encrypt_data, headers=header, timeout=60)
                result = response.json
            elif result['securityCode'] == '3001':  # 需要重置deviceID
                self.device_id = str(uuid.uuid4()).replace('-', '') + str(
                    int(time.time() * 1000 - 100000000))
                self.init_token()
                self.get_dynamic_secret_key()
                response = self.__http_util.post(url=url, data=encrypt_data, headers=header, timeout=60)
                result = response.json
            elif result['securityCode'] != '0000':
                print(f"未知错误，错误代码：{result['securityCode']}")
                return

        resp = parse.unquote_plus(init_utils.aes_decrypt(result['resp'], self.aes_key))
        LOG.info(resp)
        return json.loads(resp)

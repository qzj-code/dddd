import decimal
import json
import time
import urllib.parse
from datetime import datetime
from typing import Optional, List

import redis

from common.decorators.retry_decorator import retry_decorator
from common.enums import CabinLevelEnum, PassengerTypeEnum
from common.errors import ServiceError, ServiceStateEnum, HttpModuleErrorStateEnum, ApiStateEnum, APIError
from common.global_variable import GlobalVariable
from common.models import ProxyInfoModel
from common.models.interior_service import BundleInfoModel, PriceInfoModel, PassengerInfoModel
from common.models.task import ContactInfo, VccInfoModel
from common.utils import LogUtil, StringUtil
from common.utils.ciphering import RsaCiphering
from flights.airchina_ca.common.flight_parse import FlightParser
from flights.airchina_ca.common.order_detail_parse import OrderDetailParser
from flights.airchina_ca.common.search_utils import get_server_time_from_string, get_feca, generate_lid, encod_constId, \
    simulate_device_memory, generate_random_md5_like_string, simulate_webgl_info
from flights.airchina_ca.config import AirchinaConfig
from flights.airchina_ca.scripts.mobile_script import MobileScript

LOG = LogUtil("AirchinaSearch")


class MobileService:

    def __init__(self, proxy_info: Optional[ProxyInfoModel] = None):
        self.__mobile_script = MobileScript(proxy_info=proxy_info)
        self.__mobile_script.initialize_http()
        self.__log = LogUtil("MobileService")
        self.check_token = None
        self.__fecu = None
        self.timestamp = None
        self.udidtk = None
        self.fecw = None
        self.result = None
        self.search_id = None
        self.user_id = ""
        self.info_id = ""
        self.m_id = None
        self.identity_no = None
        self.__redis_user_key = None
        self.__cache_key = None
        self.__redis_state_key = None
        self.__redis_tax_key = None
        self.__login_cookie = None
        self.ziyinno = None
        self.if_vip_price = 1
        self.__redis_client = redis.StrictRedis(host=GlobalVariable.REDIS_HOST, port=GlobalVariable.REDIS_PORT,
                                                db=GlobalVariable.REDIS_TASK_RESULT_DB,
                                                password=GlobalVariable.REDIS_PASSWORD,
                                                decode_responses=True)

    def initialize_http(self):
        self.__mobile_script.initialize_http()

    @retry_decorator(retry_service_error_list=[(ServiceStateEnum.ROBOT_CHECK, None),
                                               (ApiStateEnum.DX_SOLUTION_FAILURE, None)],
                     retry_max_number=3)
    def init_token(self):
        # self.c_do()
        # self.check_token = fetch_token()
        data = self.__mobile_script.get_token()
        if not data or data.get('data') is None or data.get('data').get('token') is None:
            raise APIError(ApiStateEnum.DX_SOLUTION_FAILURE)
        self.check_token = data['data']['token']
        if not self.check_token:
            raise APIError(ApiStateEnum.DX_SOLUTION_FAILURE)
        self.__mobile_script.add_cookie("_dx_captcha_vid", self.check_token)

    def close(self):
        self.__mobile_script.close___()

    @retry_decorator(retry_service_error_list=[(ServiceStateEnum.ROBOT_CHECK, initialize_http),
                                               (HttpModuleErrorStateEnum.HTTP_UNKNOWN_ABNORMAL, initialize_http),
                                               (HttpModuleErrorStateEnum.HTTP_RESULT_TIMEOUT, initialize_http)],
                     retry_max_number=3)
    def init_home(self):
        home_text = self.__mobile_script.home()
        token_str = StringUtil.extract_between(home_text, '.js">', "</script>")
        self.result = get_server_time_from_string(token_str)
        self.timestamp = self.result['server_time']
        self.fecw = self.__mobile_script.get_cookie('FECW')
        feca = get_feca(self.fecw, AirchinaConfig.USER_AGENT, self.result['start_time'], self.result['server_time'])
        self.__mobile_script.add_cookie("FECA", feca)
        self.__fecu = urllib.parse.quote(feca, safe='')

    def initialization(self):
        self.initialize_http()
        self.init_home()

    @retry_decorator(retry_service_error_list=[(ServiceStateEnum.ROBOT_CHECK, None),
                                               (HttpModuleErrorStateEnum.HTTP_RESULT_TIMEOUT, None)],
                     retry_max_number=3)
    def c_do(self):
        content1 = json.dumps({
            "lid": generate_lid(),
            "lidType": "0",
            "cache": True,
            "userId": "qryFlightDyns",
            "appKey": "0b63fe72f957e59d8a9fb50157dd8475"
        }, ensure_ascii=True, separators=(',', ':'))
        param = encod_constId(content1, 'S0DOZN9bBJyPV-qczRa3oYvhGlUMrdjW7m2CkE5_FuKiTQXnwe6pg8fs4HAtIL1x=')
        params = {
            '_r': int(time.time() * 1000),
            'FECU': get_feca(self.fecw, AirchinaConfig.USER_AGENT, self.result['start_time'],
                             self.result['server_time']),
        }
        url = f'https://m.airchina.com.cn/c/udid/c.do?{urllib.parse.urlencode(params)}'
        response = self.__mobile_script.do(url, param)

        onlid = response["data"]
        content2 = json.dumps({
            "lid": onlid,  #
            "lidType": 1,
            "pro": -1,
            "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
            "np": "Win32",
            "dm": simulate_device_memory(),  #
            "cc": "unknown",
            "hc": 32,
            "ce": 1,
            "cd": 30,
            "res": "1920;1080",
            "ar": "1920;1040",
            "to": -480,
            "pr": 1.5,
            "ls": 1,
            "ss": 1,
            "ind": 1,
            "ab": 0,
            "od": 0,
            "ts": "0;false;false",
            "web": generate_random_md5_like_string(32),  #
            "gi": simulate_webgl_info(),  #
            "hlb": False,
            "hlo": False,
            "hlr": False,
            "hll": False,
            "hl": 2,
            "vs": "1261;615",
            "ws": "1277;710",
            "db": 0,
            "sm": 0,
            "ct": 141,  #
            "userId": "qryFlightDyns",
            "appKey": "0b63fe72f957e59d8a9fb50157dd8475"
        }, ensure_ascii=True, separators=(',', ':'))

        param = encod_constId(content2, 'S0DOZN9bBJyPV-qczRa3oYvhGlUMrdjW7m2CkE5_FuKiTQXnwe6pg8fs4HAtIL1x=')
        params = {
            '_r': int(time.time() * 1000),
            'FECU': get_feca(self.fecw, AirchinaConfig.USER_AGENT, self.result['start_time'],
                             self.result['server_time']),
        }
        url = f'https://m.airchina.com.cn/c/udid/c.do?{urllib.parse.urlencode(params)}'
        response = self.__mobile_script.do(url, param)
        if not response:
            raise ServiceError(ServiceStateEnum.ROBOT_CHECK)
        self.udidtk = response['data']

    def redis_login(self):
        account_number_list = AirchinaConfig.ACCOUNT_NUMBER
        for account_number in account_number_list:
            username = account_number['user']
            password = account_number['password']
            self.__redis_user_key = f"login_cookie:{username}"
            self.__redis_state_key = f"state:{username}"
            # self.__redis_client.delete(self.__redis_user_key)
            # self.__redis_client.delete(self.__redis_state_key)
            state = self.__redis_client.get(self.__redis_state_key)
            # if state and state != b'null':
            #     if state == 1 or state == '1':
            #         continue
            login_cookie = self.__redis_client.get(self.__redis_user_key)
            self.__log.info(f"命中 Redis 登录池: {self.__redis_user_key} -> {login_cookie}")
            if login_cookie and login_cookie != b'null':
                login_cookie = json.loads(login_cookie)
                cookies = json.loads(login_cookie['cookies'])
                for key, value in cookies.items():
                    # 把取到的cookie加到缓存
                    self.__mobile_script.add_cookie(key=key, value=value)
                self.user_id = login_cookie['user_id']
                self.info_id = login_cookie['info_id']
                self.m_id = login_cookie['m_id']
                self.ziyinno = login_cookie['ziyinno']
                self.udidtk = login_cookie['udidtk']
                self.timestamp = login_cookie['timestamp']
                self.result = login_cookie['result']
                self.fecw = login_cookie['fecw']
                # 发请求验证登录是否有效
                view_login_response = self.view_login()
                # 无效的话，就删除缓存
                if view_login_response and view_login_response['resp']['code'] != "00000000":
                    self.__redis_client.delete(self.__redis_state_key)
                    self.__redis_client.delete(self.__redis_user_key)
                    continue
                self.__login_cookie = login_cookie
                self.__redis_client.setex(self.__redis_state_key, 900, 1)
                break
            else:
                self.init_home()
                self.__redis_client.setex(self.__redis_state_key, 900, 1)
                public_key_pem = AirchinaConfig.WEB_RSA_KEY
                card_detail = RsaCiphering(public_key_pem, 3).encrypt(password)
                req = {
                    "loginName": username,
                    "password": card_detail,
                    "encryptType": "1",
                    "mobileType": "H5",
                    "version": "1",
                    "registerType": "0",
                    "operType": "0",
                    "loginType": "3",
                    "mainDeviceType": "H5",
                    "appVer": "6.7.0",
                    "mainVersion": "73800",
                    "lang0001": "zh_CN",
                    "lang": "zh_CN"
                }
                data = {
                    'm': {
                        'req': json.dumps(req, separators=(',', ':')),
                        'type': 'init',
                        'udidtk': self.udidtk,
                        'token': 'h5001',
                        'lang': 'zh_CN',
                        'userInfo1': '73800',
                        'deviceType': 'H5',
                    },
                    'a': '5',
                    'p': '9',
                }
                response = self.__mobile_script.login(data)
                if response.get('code') != '00000000':
                    if response['risky']:
                        self.init_token()
                        card_detail = RsaCiphering(public_key_pem, 3).encrypt(password)
                        req = {
                            "loginName": username,
                            "password": card_detail,
                            "encryptType": "1",
                            "mobileType": "H5",
                            "version": "1",
                            "registerType": "0",
                            "operType": "0",
                            "loginType": "3",
                            "mainDeviceType": "H5",
                            "appVer": "6.7.0",
                            "mainVersion": "73800",
                            "lang0001": "zh_CN",
                            "lang": "zh_CN"
                        }
                        data = {
                            'm': {
                                'req': json.dumps(req, separators=(',', ':')),
                                'type': 'check',
                                'udidtk': self.udidtk,
                                'token': 'h5001',
                                'lang': 'zh_CN',
                                'userInfo1': '73800',
                                'deviceType': 'H5',
                                'checkToken': self.check_token
                            },
                            'a': '5',
                            'p': '9',
                        }
                        response = self.__mobile_script.login(data)
                        if response['code'] != '00000000':
                            raise ServiceError(ServiceStateEnum.SERVICE_ERROR, "账户登录失败")
                self.user_id = json.loads(response['account'])['userId']
                self.info_id = json.loads(response['account'])['InfoId']
                self.m_id = json.loads(response['account'])['mId']
                self.ziyinno = json.loads(response['account'])['ziYinNo']
                self.__login_cookie = {
                    "cookies": json.dumps(self.__mobile_script.get_cookie_all(), separators=(',', ':')),
                    "user_id": self.user_id,
                    "info_id": self.info_id,
                    "m_id": self.m_id,
                    "ziyinno": self.ziyinno,
                    "fecw": self.fecw,
                    "result": self.result,
                    "udidtk": self.udidtk,
                    "timestamp": self.timestamp,
                }
                break

    def add_redis_tax(self, value):
        self.__redis_client.setex(self.__redis_tax_key, 2592000, json.dumps(value))

    def redis_tax(self, dep, arr):
        self.__redis_tax_key = "CA" + dep + arr
        tax_dict: str = self.__redis_client.get(self.__redis_tax_key)
        if tax_dict:
            return json.loads(tax_dict)
        else:
            return False

    def get_tax(self, journeys, adt_count, chd_count):
        for journey in journeys:
            if journey.segment_list[0].carrier != 'CA':
                continue
            flight_key = journey.key
            req = {
                "searchId": self.search_id,
                "flightID": flight_key,
                "org": journey.segment_list[0].dep_airport,
                "dst": journey.segment_list[-1].arr_airport,
                "adultNum": str(adt_count),
                "airline": journey.segment_list[0].carrier,
                "arrivedate": journey.segment_list[-1].arr_time.strftime('%Y-%m-%dT%H:%M'),
                "childNum": str(chd_count),
                "flag": "0",
                "flightno": journey.segment_list[0].flight_number[2:],
                "infantNum": "0",
                "takeoffdate": journey.segment_list[0].dep_time.strftime('%Y-%m-%dT%H:%M'),
                "iszj": "1",
                "isgap": "0",
                "istworeq": "1",
                "acePageReq": "1",
                "classDesc": journey.segment_list[0].id
            }
            data = {
                "m": {
                    "req": json.dumps(req, separators=(',', ':')),
                    "token": "h5001",
                    "lang": "zh_CN",
                    "page": "qryFlights",
                    "userID": self.user_id,
                    "infoID": self.info_id,
                    "GeeTested": "no",
                    "userInfo1": "73800",
                    "deviceType": "H5",
                    "primaryTierName": "Normal"
                },
                "a": "3",
                "p": "7"
            }
            search_response = self.fliter_search(data)
            for index, value in enumerate(search_response['resp']['FFCabins']):
                req = {
                    "searchId": value['cabinFfNew']['searchId'],
                    "index": value['index'],
                    "flag": "0",
                    "backsearchId": "",
                    "backindex": "",
                    "goBackFlag": "0",
                    "timestamp": self.timestamp,
                    "selectedCabin": value['ffcabinId'],
                    "selectedPrice": value['price'],
                    "nextCabin": value['nextCabin'],
                    "nextPrice": search_response['resp']['FFCabins'][index + 1]['price'],
                    "upsellFlag": "0",
                    "upsellIndex": search_response['resp']['FFCabins'][index + 1]['index'],
                    "iszj": value['iszj'],
                    "back_zj": "0",
                    "memberNumber": "",
                    "classDesc": value['classDesc'],
                    "userTravels": f"go:{journey.segment_list[0].dep_airport}-{journey.segment_list[-1].arr_airport}",
                    "inf": "0",
                    "adt": str(adt_count),
                    "cnn": str(chd_count),
                    "userId": self.user_id,
                    "mId": self.m_id,
                    "isgap": "0",
                    "flyBindingShopingId": "",
                    "flightSpaceId": value['flightSpaceId'],
                    "airRedeemQual": "N"
                }
                data = {
                    "m": {
                        "req": json.dumps(req, separators=(',', ':')),
                        "token": "h5001",
                        "lang": "zh_CN",
                        "userID": self.user_id,
                        "userInfo1": "73800",
                        "layersPeople": "",
                        "crmMemberId": "",
                        "deviceType": "H5"
                    },
                    "a": "3",
                    "p": "16"
                }
                select_flight_response = self.fliter_search(data, 'c')
                if select_flight_response['resp']['code'] != '00000000':
                    raise ServiceError(ServiceStateEnum.SERVICE_ERROR, "选择航班失败")

                flight = value['cabinFfNew']['flight'][0]
                dt = datetime.fromisoformat(
                    select_flight_response['resp']['CountPrice']['tripSegmentList'][0]['departureDate'])
                flight_list = []
                for f in value['cabinFfNew']['flight']:
                    flight_list.append({
                        "date": f['date'],
                        "IsShare": f['isShared'],
                        "dst": f['dst'],
                        "org": f['org'],
                        "cabin": f['cabin'],
                        "roundType": f['roundType']
                    })
                self.ffcabin = value['ffcabin']
                tax_dict = {}
                for i, v in select_flight_response['resp']['CountPrice']['tripList'].items():
                    if v['quantity'] == '0':
                        continue
                    passenger_type = "CHD" if v['code'] == 'CNN' else v['code']
                    tax_dict[passenger_type] = {}
                    tax = 0
                    oifee = 0
                    for taxes in v['taxesFeesList']:
                        if taxes['taxFeeType'] == 'CN':
                            tax = taxes['taxFeePrice']
                            tax_dict[passenger_type]['tax'] = tax
                        elif taxes['taxFeeType'] == 'YQ':
                            oifee = taxes['taxFeePrice']
                            tax_dict[passenger_type]['oifee'] = oifee
                return tax_dict

    def setex(self):
        if self.__redis_state_key:
            self.__redis_client.setex(self.__redis_state_key, 900, 0)
        if self.__login_cookie:
            self.__redis_client.setex(self.__redis_user_key, 900, json.dumps(self.__login_cookie))

    def view_login(self):
        self.__mobile_script.get_account()
        req = {
            "userId": self.user_id
        }
        data = {
            "m": {
                "req": json.dumps(req, separators=(',', ':')),
                "token": "h5001",
                "lang": "zh_CN",
                "userInfo1": "73800",
                "userId": self.user_id,
                "userID": self.user_id,
                "ziYinNo": self.ziyinno,
                "deviceType": "H5"
            },
            "a": "28",
            "p": "156"
        }
        params = {
            'FECU': get_feca(self.fecw, AirchinaConfig.USER_AGENT, self.result['start_time'],
                             self.result['server_time']),
        }
        view_login_response = self.__mobile_script.view_login(data, params)
        return view_login_response

    def login(self, username: str, password: str):
        public_key_pem = AirchinaConfig.WEB_RSA_KEY
        card_detail = RsaCiphering(public_key_pem, 3).encrypt(password)
        req = {
            "loginName": username,
            "password": card_detail,
            "encryptType": "1",
            "mobileType": "H5",
            "version": "1",
            "registerType": "0",
            "operType": "0",
            "loginType": "3",
            "mainDeviceType": "H5",
            "appVer": "6.7.0",
            "mainVersion": "73800",
            "lang0001": "zh_CN",
            "lang": "zh_CN"
        }
        data = {
            'm': {
                'req': json.dumps(req, separators=(',', ':')),
                'type': 'init',
                'udidtk': self.udidtk,
                'token': 'h5001',
                'lang': 'zh_CN',
                'userInfo1': '73800',
                'deviceType': 'H5',
            },
            'a': '5',
            'p': '9',
        }

        response = self.__mobile_script.login(data)
        if response.get('code') != '00000000':
            if response['risky']:
                self.c_do()
                self.init_token()
                card_detail = RsaCiphering(public_key_pem, 3).encrypt(password)
                req = {
                    "loginName": username,
                    "password": card_detail,
                    "encryptType": "1",
                    "mobileType": "H5",
                    "version": "1",
                    "registerType": "0",
                    "operType": "0",
                    "loginType": "3",
                    "mainDeviceType": "H5",
                    "appVer": "6.7.0",
                    "mainVersion": "73800",
                    "lang0001": "zh_CN",
                    "lang": "zh_CN"
                }
                data = {
                    'm': {
                        'req': json.dumps(req, separators=(',', ':')),
                        'type': 'check',
                        'udidtk': self.udidtk,
                        'token': 'h5001',
                        'lang': 'zh_CN',
                        'userInfo1': '73800',
                        'deviceType': 'H5',
                        'checkToken': self.check_token
                    },
                    'a': '5',
                    'p': '9',
                }
                response = self.__mobile_script.login(data)
                if response['code'] != '00000000':
                    raise ServiceError(ServiceStateEnum.SERVICE_ERROR, "账户登录失败")
        self.user_id = json.loads(response['account'])['userId']
        self.info_id = json.loads(response['account'])['InfoId']
        self.m_id = json.loads(response['account'])['mId']
        self.identity_no = json.loads(response['account']).get('identityNo')
        self.ziyinno = json.loads(response['account']).get('ziYinNo')
        return response

    def logout(self):
        self.__mobile_script.logout()

    @retry_decorator(retry_service_error_list=[(ServiceStateEnum.ROBOT_CHECK, initialization)],
                     retry_max_number=3)
    def search(self, airport_data, adult_count: int, child_count: int, currency: str, promo_code: str = "",
               task_type: str = "search"):
        self.c_do()
        req = {
            "backDate": "",
            "version": "4",
            "org": airport_data[0][0],
            "dst": airport_data[0][1],
            "timestamp": self.timestamp,
            "flag": "0",
            "inf": "0",
            "geeflag": "qryFlights",
            "date": airport_data[0][2],
            "adt": str(adult_count),
            "cnn": str(child_count),
            "cabin": "Economy",
            "tabFlag": "0",
            "isgap": "0",
            "layersPeople": "",
            "userId": self.user_id,
            "mId": self.m_id,
            "checknum": False,
        }
        data = {
            'm': {
                'req': json.dumps(req, separators=(',', ':')),
                'type': 'init',
                'token': 'h5001',
                'lang': 'zh_CN',
                'udidtk': self.udidtk,
                'page': 'qryFlights',
                'userID': self.user_id,
                'infoID': self.info_id,
                'GeeTested': 'no',
                'userInfo1': '73800',
                'layersPeople': '',
                'deviceType': 'H5',
                'latitude': '',
                'longitude': '',
                'primaryTierName': 'Normal',
                'checkToken': self.check_token,
            },
            'a': '3',
            'p': '6',
        }
        params = {
            'FECU': get_feca(self.fecw, AirchinaConfig.USER_AGENT, self.result['start_time'],
                             self.result['server_time']),
        }
        if task_type == 'search' or task_type == 'verify':
            search_response = self.__mobile_script.search_invoke(data, params)
        else:
            search_response = self.__mobile_script.invoke(data, params)
        if search_response.get('risky') and (task_type == 'search' or task_type == 'verify'):
            raise ServiceError(ServiceStateEnum.ROBOT_CHECK)
        if search_response.get('risky'):
            self.c_do()
            self.init_token()
            req = {
                "backDate": "",
                "version": "4",
                "org": airport_data[0][0],
                "dst": airport_data[0][1],
                "timestamp": self.timestamp,
                "flag": "0",
                "inf": "0",
                "geeflag": "qryFlights",
                "date": airport_data[0][2],
                "adt": str(adult_count),
                "cnn": str(child_count),
                "cabin": "Economy",
                "tabFlag": "0",
                "isgap": "0",
                "layersPeople": "",
                "userId": self.user_id,
                "mId": self.m_id,
                "checknum": False
            }
            data = {
                "m": {
                    "req": json.dumps(req, separators=(',', ':')),
                    "type": "check",
                    "token": "h5001",
                    "lang": "zh_CN",
                    "udidtk": self.udidtk,
                    "page": "qryFlights",
                    "userID": self.user_id,
                    "infoID": self.info_id,
                    "GeeTested": "no",
                    "userInfo1": "73800",
                    "layersPeople": "",
                    "deviceType": "H5",
                    "latitude": "",
                    "longitude": "",
                    "primaryTierName": "Normal",
                    "checkToken": self.check_token
                },
                "a": "3",
                "p": "6"
            }
            params = {
                'FECU': get_feca(self.fecw, AirchinaConfig.USER_AGENT, self.result['start_time'],
                                 self.result['server_time']),
            }
            search_response = self.__mobile_script.risky_invoke(data, params)
            if not search_response or search_response.get('risky'):
                raise ServiceError(ServiceStateEnum.ROBOT_CHECK)
        if search_response['resp']['code'] == '01020200' or search_response['resp']['code'] == '00000001':
            raise ServiceError(ServiceStateEnum.NO_FLIGHT_DATA)
        self.search_id = search_response['resp']['goto']['searchID']
        response = FlightParser.parse_flight_data(search_response, child_count)
        return response

    def fliter(self, journeys, adt_count, chd_count, task_type: str = ""):
        counts = 0
        tags = ['随机立减', '限时优惠', '会员直减', '限时特惠', '定立减', '同行惠']
        # 根据价格排序，从小到大
        journeys = sorted(journeys, key=lambda x: x.bundle_list[0].price_info[0].fare)
        for journey in journeys:
            bundles = []
            if counts > 7:
                break
            for i in journey.bundle_list:
                if (not any(tag
                            in i.price_tag for tag in tags) or i.cabin_level.value != 'Y') and task_type == 'search':
                    continue
                counts += 1
                flight_key = journey.key
                req = {
                    "searchId": self.search_id,
                    "flightID": flight_key,
                    "org": journey.segment_list[0].dep_airport,
                    "dst": journey.segment_list[-1].arr_airport,
                    "adultNum": str(adt_count),
                    "airline": journey.segment_list[0].carrier,
                    "arrivedate": journey.segment_list[-1].arr_time.strftime('%Y-%m-%dT%H:%M'),
                    "childNum": str(chd_count),
                    "flag": "0",
                    "flightno": journey.segment_list[0].flight_number[2:],
                    "infantNum": "0",
                    "takeoffdate": journey.segment_list[0].dep_time.strftime('%Y-%m-%dT%H:%M'),
                    "iszj": "1",
                    "isgap": "0",
                    "istworeq": "1",
                    "acePageReq": "1",
                    "classDesc": journey.segment_list[0].id
                }

                data = {
                    "m": {
                        "req": json.dumps(req, separators=(',', ':')),
                        "token": "h5001",
                        "lang": "zh_CN",
                        "page": "qryFlights",
                        "userID": self.user_id,
                        "infoID": self.info_id,
                        "GeeTested": "no",
                        "userInfo1": "73800",
                        "deviceType": "H5",
                        "primaryTierName": ""
                    },
                    "a": "3",
                    "p": "7"
                }
                search_response = self.fliter_search(data)
                for j in search_response['resp']['FFCabins']:
                    price_info = []
                    passenger_type_list = [PassengerTypeEnum.ADT] if chd_count == 0 else [PassengerTypeEnum.ADT,
                                                                                          PassengerTypeEnum.CHD]
                    if j['vip_price'] == '':
                        discount = 0
                    else:
                        discount = decimal.Decimal(j['priceN']) - decimal.Decimal(j['vip_price'])
                    # j['vip_price'] 优惠后的价格 , j['priceN'] 优惠前的价格
                    price_tag = []
                    for lable_name in j['serviceInfo']['lableNameList']:
                        price_tag.append(lable_name['acivity_Name'])
                    if '会员直减' in price_tag and j.get('zjActivityDesc') == '<p>会员登录购票享95折优惠，优惠前儿童旅客为五折儿童票价则不享受直减优惠。</p>':
                        fare = int(float(j['priceN']) * 0.95)
                    else:
                        fare = j['vip_price'] if j['vip_price'] else j['priceN']
                    for passenger_type in passenger_type_list:
                        price_info.append(PriceInfoModel.model_validate({
                            'passengerType': passenger_type,
                            'fare': fare,
                            'tax': 0,
                            'currency': "CNY",
                            'ext': {
                                "priceTag": ','.join(price_tag),
                                "discount": discount
                            }
                        }))
                    cabin = j['ffcabinId']
                    product_tag = j['price']
                    available_count = j.get('surplusTicket') if j.get('surplusTicket') else 9
                    baggage_list = []
                    cabin_level = CabinLevelEnum.ECONOMY if j['cabinClassName'] == '经济舱' else CabinLevelEnum.BUSINESS

                    bundles.append(BundleInfoModel.model_validate({
                        'priceInfo': price_info,
                        'cabin': cabin,
                        'productTag': cabin,
                        'availableCount': available_count,
                        'baggageList': baggage_list,
                        'cabinLevel': cabin_level,
                        'priceTag': price_tag,
                        'id': product_tag
                    }))
            if bundles:
                journey.bundle_list = bundles

    @retry_decorator(retry_service_error_list=[(HttpModuleErrorStateEnum.HTTP_UNKNOWN_ABNORMAL, None),
                                               (HttpModuleErrorStateEnum.HTTP_RESULT_TIMEOUT, None)],
                     retry_max_number=3)
    def fliter_search(self, data, invoke_str: str = "g", referer=""):
        params = {
            'FECU': get_feca(self.fecw, AirchinaConfig.USER_AGENT, self.result['start_time'],
                             self.result['server_time']),
        }
        if invoke_str == 'g':
            search_response = self.__mobile_script.invoke(data, params)
        elif invoke_str == 'b':
            search_response = self.__mobile_script.invoke_b(data, params)
        else:
            search_response = self.__mobile_script.invoke_c(data, params, referer)
        return search_response

    def select_flight(self, journeys, adt_count, chd_count, use_bundle_info: BundleInfoModel):
        journey = journeys[0]
        flight_key = journey.key
        req = {
            "searchId": self.search_id,
            "flightID": flight_key,
            "org": journey.segment_list[0].dep_airport,
            "dst": journey.segment_list[-1].arr_airport,
            "adultNum": str(adt_count),
            "airline": journey.segment_list[0].carrier,
            "arrivedate": journey.segment_list[-1].arr_time.strftime('%Y-%m-%dT%H:%M'),
            "childNum": str(chd_count),
            "flag": "0",
            "flightno": journey.segment_list[0].flight_number[2:],
            "infantNum": "0",
            "takeoffdate": journey.segment_list[0].dep_time.strftime('%Y-%m-%dT%H:%M'),
            "iszj": "1",
            "isgap": "0",
            "istworeq": "1",
            "acePageReq": "1",
            "classDesc": journey.segment_list[0].id
        }
        data = {
            "m": {
                "req": json.dumps(req, separators=(',', ':')),
                "token": "h5001",
                "lang": "zh_CN",
                "page": "qryFlights",
                "userID": self.user_id,
                "infoID": self.info_id,
                "GeeTested": "no",
                "userInfo1": "73800",
                "deviceType": "H5",
                "primaryTierName": "Normal"
            },
            "a": "3",
            "p": "7"
        }
        search_response = self.fliter_search(data)
        product_tag = use_bundle_info.product_tag
        for index, value in enumerate(search_response['resp']['FFCabins']):
            if value['price'] == product_tag:
                req = {
                    "searchId": value['cabinFfNew']['searchId'],
                    "index": value['index'],
                    "flag": "0",
                    "backsearchId": "",
                    "backindex": "",
                    "goBackFlag": "0",
                    "timestamp": self.timestamp,
                    "selectedCabin": value['ffcabinId'],
                    "selectedPrice": value['price'],
                    "nextCabin": value['nextCabin'],
                    "nextPrice": search_response['resp']['FFCabins'][index + 1]['price'],
                    "upsellFlag": "0",
                    "upsellIndex": search_response['resp']['FFCabins'][index + 1]['index'],
                    "iszj": value['iszj'],
                    "back_zj": "0",
                    "memberNumber": "",
                    "classDesc": value['classDesc'],
                    "userTravels": f"go:{journey.segment_list[0].dep_airport}-{journey.segment_list[-1].arr_airport}",
                    "inf": "0",
                    "adt": str(adt_count),
                    "cnn": str(chd_count),
                    "userId": self.user_id,
                    "mId": self.m_id,
                    "isgap": "0",
                    "flyBindingShopingId": "",
                    "flightSpaceId": value['flightSpaceId'],
                    "airRedeemQual": "N"
                }
                data = {
                    "m": {
                        "req": json.dumps(req, separators=(',', ':')),
                        "token": "h5001",
                        "lang": "zh_CN",
                        "userID": self.user_id,
                        "userInfo1": "73800",
                        "layersPeople": "",
                        "crmMemberId": "",
                        "deviceType": "H5"
                    },
                    "a": "3",
                    "p": "16"
                }
                select_flight_response = self.fliter_search(data, 'c')
                if select_flight_response['resp']['code'] != '00000000':
                    raise ServiceError(ServiceStateEnum.SERVICE_ERROR, "选择航班失败")
                flight = value['cabinFfNew']['flight'][0]
                dt = datetime.fromisoformat(
                    select_flight_response['resp']['CountPrice']['tripSegmentList'][0]['departureDate'])
                flight_list = []
                for f in value['cabinFfNew']['flight']:
                    flight_list.append({
                        "date": f['date'],
                        "IsShare": f['isShared'],
                        "dst": f['dst'],
                        "org": f['org'],
                        "cabin": f['cabin'],
                        "roundType": f['roundType']
                    })
                self.ffcabin = value['ffcabin']
                req = {
                    "org": flight['org'],
                    "dst": flight['dst'],
                    "cabinId": flight['cabin'],
                    "out": "0",
                    "tcCode": "NO",
                    "lang": "zh_CN",
                    "date": flight['date'],
                    "depTime": dt.strftime('%H:%M'),
                    "childType": value['childType'],
                    "adtNumber": str(adt_count),
                    "infNumber": "0",
                    "childNumber": str(chd_count),
                    "ff_type": "1",
                    "cabinFfNew": {
                        "flight": flight_list,
                        "oneTripDate": flight['date'],
                        "isRt": "OW"
                    }
                }
                data = {
                    "m": {
                        "req": json.dumps(req, separators=(',', ':')),
                        "token": "h5001",
                        "lang": "zh_CN",
                        "userInfo1": "62800"
                    },
                    "a": "17",
                    "p": "353"
                }
                select_price_response = self.fliter_search(data, 'c')
                for i, v in select_flight_response['resp']['CountPrice']['tripList'].items():
                    if v['quantity'] == '0':
                        continue
                    passenger_type = "CHD" if v['code'] == 'CNN' else v['code']
                    tax = 0
                    oifee = 0
                    for taxes in v['taxesFeesList']:
                        if taxes['taxFeeType'] == 'CN':
                            tax = taxes['taxFeePrice']
                        elif taxes['taxFeeType'] == 'YQ':
                            oifee = taxes['taxFeePrice']
                    for p in use_bundle_info.price_info:
                        if p.passenger_type.value == passenger_type:
                            p.tax = tax
                            p.ext['oiFee'] = oifee
                return select_flight_response, select_price_response
        else:
            raise ServiceError(ServiceStateEnum.SERVICE_ERROR, "未匹配到价格key")

    def add_passenger(self, passengers_list: List[PassengerInfoModel], select_flight_response: dict, ):
        self.identity_no = \
            select_flight_response['resp']['CountPrice']['passengerInfos']['passengerInfos'][0]['identityInfos'][0][
                'identityNo']
        # 先添加乘机人
        for index, value in enumerate(passengers_list):
            req = {
                "userId": self.user_id,
                "cnFirstName": value.first_name(),
                "cnLastName": value.last_name(),
                "firstName": "",
                "lastName": "",
                "nationalityId": value.nationality,
                "birthday": value.birthday.strftime('%Y-%m-%d'),
                "gender": value.gender.value,
                "passengerPhone": value.mobile,
                "areaCode": value.mob_country_code,
                "identityInfos": [
                    {
                        "cnorenName": value.issue_place,
                        "identityKind": "C",
                        "identityName": "身份证/港澳台居民居住证/户口本",
                        "identityNo": value.card_number,
                        "identityValidDate": "",
                        "passportCountry": "",
                        "passportCountryName": "",
                        "ifValid": "1",
                        "validityType": "0",
                        "credentialId": "1-19BLPB5C"  # 随便取一个联系人的id
                    }
                ],
                "cardInfos": [],
                "isSelf": "0",
                "version": "73800"
            }
            data = {
                "m": {
                    "req": json.dumps(req, separators=(',', ':')),
                    "type": "init",
                    "token": "h5001",
                    "lang": "zh_CN",
                    "userID": self.user_id,
                    "userInfo1": "73800"
                },
                "a": "1",
                "p": "42"
            }
            add_passenger_response = self.fliter_search(data)
            if add_passenger_response['resp']['code'] == '06040004':
                self.__log.info(add_passenger_response['resp']['msg'])
                continue
            if add_passenger_response['resp']['code'] != "00000000":
                raise ServiceError(ServiceStateEnum.SERVICE_ERROR,
                                   f"添加联系人失败:{add_passenger_response['resp']['msg']}")

    def select_passenger(self, passengers_list: List[PassengerInfoModel], select_flight_response: dict, user: str):
        """
        选择乘机人请求
        Args:
            passengers_list: 乘机人列表
            contact_info: 联系人列表
            select_flight_response: 选择价格的响应

        Returns: 乘机人查询结果列表

        """
        departure = select_flight_response['resp']['CountPrice']['tripSegmentList'][0]['departureDate']
        departure_date = datetime.fromisoformat(departure).date().strftime('%Y-%m-%d')
        check_service_rule = select_flight_response['resp']['CountPrice']['checkServiceRule']

        # 查询乘机人列表
        req = {
            "mId": self.m_id,
            "type": "1",
            "userFlag": "0",
            "USER_ID": self.user_id,
            "userId": self.user_id,
            "travelDate": departure_date,
            "isDisabledJP": "2",
            "currentPage": "1",
            "pageSize": "30",
            "ifAlieneeInfo": "1",
            "isTicket": "1",
            "registerType": "0",
            "reqPassengers": {}
        }
        data = {
            'm': {
                'req': json.dumps(req, separators=(',', ':')),
                'token': 'h5001',
                'lang': 'zh_CN',
                'userID': self.user_id,
                'userInfo1': '73800',
            },
            'a': '1',
            'p': '41',
        }
        search_passenger_list = self.fliter_search(data, 'g')

        total_price = '0'  # 总票价
        total_price_pre = '0'
        flight_list = []
        for i in select_flight_response['resp']['CountPrice']['tripSegmentList']:
            flight_line = i['originCode'] + '-' + i['destinationCode']
            start_date = datetime.fromisoformat(i['departureDate']).strftime("%Y-%m-%d %H:%M:%S")
            flight_no = i['marketingAirline'] + i['flightNumber']
            flight_list.append({
                "flightLine": flight_line,
                "startDate": start_date,
                "flightNo": flight_no,
                "cabbinId": i['bookingClass'],
                "chdCabbinId": i['childBookingClass'],
                "airline": i['marketingAirline'],
                "odNumber": i['odNumber'],
                "odCouponNumber": i['odCouponNumber']
            })

        select_passenger_list = []
        for index, value in enumerate(passengers_list):
            for i in search_passenger_list['resp']['passengerInfos']:
                if i['identityInfos'][0]['identityNo'] != value.card_number:
                    continue
                person_id = i['identityInfos'][0]['identityId']
                ticket_price = '0'  # 乘机人单人票价
                ticket_price_pre = '0'
                select_passenger_list.append({
                    "passCrNo": value.card_number,
                    "passType": value.passenger_type.value,
                    "birthday": value.birthday.strftime('%Y-%m-%d'),
                    "personId": person_id,
                    "ticketPrice": ticket_price,
                    "ticketPricePre": ticket_price_pre,
                    "passCrId": "C",  # 证件类型
                    "passFirstName": value.first_name(),
                    "passLastName": value.last_name()
                })
        if len(select_passenger_list) != len(passengers_list):
            raise ServiceError(ServiceStateEnum.SERVICE_ERROR, f"选择乘机人数量错误，{user}")

        # 选择乘机人
        req = {
            "mId": self.m_id,
            "userId": self.user_id,
            "memLevel": "Normal",
            "memCrId": "C",  # 证件类型
            "memCrNo": self.identity_no,
            "totalPrice": total_price,
            "totalPricePre": total_price_pre,
            "interFlag": "0",
            "isBack": "0",
            "productType": "1",
            "version": "1",
            "shareFlag": "0",
            "flightList": flight_list,
            "departureCityCode": select_flight_response['resp']['CountPrice']['tripSegmentList'][0]['originCode'],
            "arrivalCityCode": select_flight_response['resp']['CountPrice']['tripSegmentList'][-1][
                'destinationCode'],
            "passengerList": select_passenger_list,
            "mid": self.m_id,
            "openJawFlag": "0",
            "openJawList": [
                {
                    "od": f"{select_flight_response['resp']['CountPrice']['tripSegmentList'][0]['originCode']}-{select_flight_response['resp']['CountPrice']['tripSegmentList'][-1]['destinationCode']}"
                }
            ],
            "subType": "",
            "studentCoupon": "",
            "studentFlag": "",
            "checkServiceRule": check_service_rule
        }
        data = {
            "m": {
                "req": json.dumps(req, separators=(',', ':')),
                "token": "h5001",
                "infoID": self.info_id,
                "userID": self.user_id,
                "deviceType": "H5",
                "lang": "zh_CN",
                "userInfo1": "73800",
                "ziYinNo": self.ziyinno
            },
            "a": "9",
            "p": "17"
        }
        response_9_17 = self.fliter_search(data, 'b')
        if response_9_17.get('resp').get('code') != "00000000":
            raise ServiceError(ServiceStateEnum.SERVICE_ERROR, f"选择乘机人失败，{user}")
        return search_passenger_list

    def go_pay(self, select_flight_response: dict, contact_info: ContactInfo, search_passenger_list: dict,
               passenger_infos: [PassengerInfoModel], user: str):
        """
        跳转支付页面
        Args:
            select_flight_response: 航班信息
            contact_info: 联系人信息
            search_passenger_list: 网站乘机人列表 里面有网站乘机人对应的id
            passenger_infos: 原始乘机人列表

        Returns: 订单详情、总价格

        """
        if len(passenger_infos) > 1:
            if_pnr_separate = "1"
        else:
            if_pnr_separate = ""
        telephones = []
        api_ss = []
        travelers = []
        fares = []
        flights = []
        index = 0
        preferential_price = 0  # 优惠价格
        if select_flight_response['resp']['CountPrice'].get('discountListGo'):
            for i in select_flight_response['resp']['CountPrice']['discountListGo']:
                preferential_price += int(i['price'])
        pre_total_price = 0
        for key, value in select_flight_response['resp']['CountPrice']['tripList'].items():
            index += 1
            if value['quantity'] == '0':
                continue
            if pre_total_price == 0:
                pre_total_price = str(int(value['totalFareAmount']) - preferential_price)
            taxs = []
            fare_infos = []
            tax_amount = 0
            for i in value['taxesFeesList']:
                tax_amount += int(i['taxFeePrice'])
                taxs.append({
                    "Amount": i['taxFeePrice'],
                    "Designator": i['taxFeeType']
                })

            currency_code = value['baseFareCurrency']
            for iii, vvv in enumerate(select_flight_response['resp']['CountPrice']['tripSegmentList']):
                departure_date = datetime.fromisoformat(vvv['departureDate']).strftime('%Y-%m-%d')
                fare_infos.append({
                    "FareBasisCode": "",
                    "ArrivalCode": vvv['destinationCode'],
                    "DepartureCode": vvv['originCode'],
                    "DepartureDate": departure_date,
                    "RelatedSegments": {
                        "ArrivalCode": vvv['destinationCode'],
                        "DepartureCode": vvv['originCode'],
                        "DepartureDate": departure_date,
                        "SegmentIDRef": f"F{iii + 1}",
                        "AirlineCode": vvv['marketingAirline'],
                        "BaggageAllowance": vvv['freeBaggageAllow'],
                        "ClassOfService": vvv['bookingClass']
                    },
                    "fareComponent": {
                        "taxs": taxs,
                        "CurrencyCode": currency_code,
                        "Taxes_Amount": str(tax_amount),
                        "Amount": str(int(value['baseFareAmount']) - preferential_price),
                        "Total": str(int(value['totalFareAmount']) - preferential_price)
                    }
                })
            for i in range(0, int(value['quantity'])):
                fare_dict = {
                    "TravelerIDRef": f"T{index}",
                    "Taxes_Amount": str(tax_amount),
                    "BaseFare_Amount": str(int(value['baseFareAmount']) - preferential_price),
                    "Type": "CHD" if value['code'] == 'CNN' else value['code'],
                    "fareInfos": fare_infos,
                    "taxs": taxs,
                    "IfPcPay": "0",
                    "IfEcPay": "0",
                    "IfMorePc": "0",
                    "IfEvPay": "0",
                    "IfJlPay": "0",
                    "evFeeEach": "0",
                    "jlFeeEach": "0",
                    "exst_taxs": []
                }
                if key == "ADT":
                    fare_dict['teenager'] = ""
                if select_flight_response['resp']['CountPrice'].get('discountListGo'):
                    fare_dict['discountList'] = select_flight_response['resp']['CountPrice']['discountListGo']
                    self.if_vip_price = 0
                fares.append(fare_dict)
        adt_count = 0
        chd_count = 0
        for index, value in enumerate(passenger_infos):
            if value.passenger_type.value == 'ADT':
                adt_count += 1
            elif value.passenger_type.value == 'CHD':
                chd_count += 1
            for i in search_passenger_list['resp']['passengerInfos']:
                if value.card_number != i['identityInfos'][0]['identityNo']:
                    continue
                person_id = i['personId']
                telephones.append({
                    "TelephoneNumber": value.mobile,
                    "TravelerIDRef": f"T{index + 1}",
                    "Type": value.gender.value,
                    "areaCode": value.mob_country_code
                })
                api_ss.append({
                    "DateOfBirth": value.birthday.strftime('%Y-%m-%d'),
                    "DocNumber": value.card_number,
                    "DocType": "C",
                    "GivenName": value.first_name(),
                    "GivenNameEn": "",
                    "IdentityId": i['identityInfos'][0]['identityId'],
                    "Surname": value.last_name(),
                    "SurnameEn": "",
                    "TravelerIDRef": f"T{index + 1}",
                    "validityType": i['identityInfos'][0]['validityType']
                })
                travelers.append({
                    "AssociationID": f"T{index + 1}",
                    "CardId": "",
                    "DateOfBirth": value.birthday.strftime('%Y-%m-%d'),
                    "GivenName": value.first_name(),
                    "GivenNameEn": "",
                    "Surname": value.last_name(),
                    "SurnameEn": "",
                    "Type": value.passenger_type.value,
                    "passengerId": person_id,
                    "vipCard": "",
                    "vipCardGrade": ""
                })
        for index, trip_segment in enumerate(select_flight_response['resp']['CountPrice']['tripSegmentList']):
            departure_date = datetime.fromisoformat(trip_segment['departureDate']).date().strftime('%Y-%m-%d')
            arrival_date = datetime.fromisoformat(trip_segment['arrivalDate']).date().strftime('%Y-%m-%d')
            departure_time = datetime.fromisoformat(trip_segment['departureDate']).strftime('%H:%M:%S')
            arrival_time = datetime.fromisoformat(trip_segment['arrivalDate']).strftime('%H:%M:%S')
            flights.append({
                "Carrier_FlightNumber": trip_segment['flightNumber'],
                "Carrier_AirlineCode": trip_segment['marketingAirline'],
                "ClassOfService": trip_segment['bookingClass'],
                "AssociationID": f"F{index + 1}",
                "Arrival_AirportCode": trip_segment['destinationCode'],
                "Arrival_Date": arrival_date,
                "Departure_Date": departure_date,
                "Real_AirlineCode": trip_segment['marketingAirline'],
                "Real_FlightNumer": "",
                "Departure_Time": departure_time,
                "Arrival_Time": arrival_time,
                "Departure_AirportCode": trip_segment['originCode'],
                "Arrival_Terminal": "",
                "Departure_Terminal": "",
                "NumberInParty": len(passenger_infos),
                "flightType": trip_segment['equipmentCode'],
                "ChildClassOfService": trip_segment['childBookingClass'],
                "BaseFare_Mileage_Amount": "",
                "BaseFare_Amount_Cost": "",
                "flightModel": "",
                "foodType": "",
                "planeCompanyName": "",
                "totalTime": trip_segment['totalFlightDuration'],
                "flightModelType": "",
                "classDesc": select_flight_response['resp']['CountPrice']['classDesc'],
                "preClassOfService": "",
                "netFlag": ""
            })
        trip_id = select_flight_response['resp']['CountPrice']['tripId']
        origin_code = select_flight_response['resp']['CountPrice']['tripSegmentList'][0]['originCode']
        booking_class = select_flight_response['resp']['CountPrice']['tripSegmentList'][0]['bookingClass']
        destination_code = select_flight_response['resp']['CountPrice']['tripSegmentList'][-1]['destinationCode']
        go = f"{origin_code}_{destination_code};{booking_class[0]};"
        commodity_id = select_flight_response['resp']['CountPrice']['tripSegmentList'][0]['marketingAirline'] + \
                       select_flight_response['resp']['CountPrice']['tripSegmentList'][0]['flightNumber']
        req = {
            "fares": fares,
            "telephones": telephones,
            "APISs": api_ss,
            "journeySheet": {
                "type": "0"
            },
            "flights": flights,
            "travelers": travelers,
            "insurances": [],
            "contactPhone": contact_info.mobile,
            "contactUser": contact_info.name.replace('/', ''),
            "mobileSysVer": "8.1",
            "transitflag": 0,
            "upsale": "0",
            "upsale_fee": 0,
            "ticketType": "0",
            "stopflag": 0,
            "mobileIp": "0.0.0.0",
            "tripId": trip_id,
            "International_Flag": 1,
            "segmentflag": "0",
            "mobileType": "H5",
            "departAirport": origin_code,
            "arrivalAirport": destination_code,
            "userId": self.user_id,
            "ifVipPrice": self.if_vip_price,
            "vipFee": "0",
            "goFareFamilyId": self.ffcabin,
            "backFareFamilyId": "",
            "searchId": self.search_id,
            "mId": self.m_id,
            "frequentTravelerGroups": [],
            "ifPNRSeparate": if_pnr_separate,
            "checkPriceMap": {
                "tripInfo": {
                    "idflag": "0",
                    "zj_number": "0",
                    "tripType": "OW",
                    "go": go,
                    "back": ""
                },
                "isgap": "0",
                "tripId": trip_id,
                "classDesc": select_flight_response['resp']['CountPrice']['classDesc']
            },
            "preTotalPrice": pre_total_price,
            "vipCard": self.ziyinno,
            "searchIdGapGo": self.search_id,
            "searchIdGapBack": "",
            "acceptWay": "1",
            "ifMailConnPerson": "1",
            "isDoubleSeat": "0",
            "memLevel": "Normal",
            "memCrId": "C",
            "memCrNo": self.identity_no,
            "email": contact_info.email,
            "areaCode": contact_info.mobile_country_code,
            "userAreaCode": contact_info.mobile_country_code,
            "flyBindingShopingId": "",
            "firstTicketInfo": select_flight_response['resp']['CountPrice']['firstTicketInfo'],
            "updatePriceInfo": {}
        }
        data = {
            "m": {
                "req": json.dumps(req, separators=(',', ':')),
                "type": "init",
                "token": "h5001",
                "lang": "zh_CN",
                "udidtk": self.udidtk,
                "page": "addOrderPassenger",
                "userID": self.user_id,
                "infoID": self.info_id,
                "GeeTested": "no",
                "userInfo1": "73800",
                "current_url": "https://m.airchina.com.cn/b/invoke/booking/addOrderPassenger@pg",
                "phone_number": contact_info.mobile,
                "commodity_id": commodity_id,
                "ext_passenger_phone": contact_info.mobile,
                "deviceType": "H5",
                "latitude": "",
                "longitude": ""
            },
            "a": "0",
            "p": "32"
        }
        self.c_do()
        go_pay_response = self.fliter_search(data, 'c',
                                             'https://m.airchina.com.cn/b/invoke/booking/addOrderPassenger@pg')
        if go_pay_response.get('risky'):
            self.c_do()
            self.init_token()
            data = {
                'm': {
                    'req': json.dumps(req, separators=(',', ':')),
                    'type': 'check',
                    'token': 'h5001',
                    'lang': 'zh_CN',
                    'udidtk': self.udidtk,
                    'page': 'addOrderPassenger',
                    'userID': self.user_id,
                    'infoID': self.info_id,
                    'GeeTested': 'no',
                    'userInfo1': '73800',
                    'current_url': 'https://m.airchina.com.cn/b/invoke/booking/addOrderPassenger@pg',
                    'phone_number': contact_info.mobile,
                    'commodity_id': 'CA1334',
                    'ext_passenger_phone': contact_info.mobile,
                    'deviceType': 'H5',
                    'latitude': '',
                    'longitude': '',
                    'checkToken': self.check_token,
                },
                'a': '0',
                'p': '32',
            }
            go_pay_response = self.fliter_search(data, 'c',
                                                 'https://m.airchina.com.cn/b/invoke/booking/addOrderPassenger@pg')
        if not go_pay_response:
            self.logout()
            raise ServiceError(ServiceStateEnum.SERVICE_ERROR, f"下单失败，账号封禁，更换账号重试{user}")
        if go_pay_response.get('resp').get('code') != "00000000":
            raise ServiceError(ServiceStateEnum.SERVICE_ERROR,
                               f"跳转支付异常,{go_pay_response.get('resp').get('msg')}")
        return go_pay_response, select_flight_response['resp']['CountPrice']['totalPriceAmount']

    def pay(self, go_pay_response: dict, vcc_info: VccInfoModel, total_price_amount: str):
        order_id = go_pay_response['resp']['orderId']
        req = {
            "orderId": order_id,
            "orderAmount": int(total_price_amount),
            "cardHolderIdType": "C",
            "cardHolderIdNo": "110107195706290408",
            "areaCode": "86",
            "cardHolderTel": "17606141652",
            "cardHolderName": vcc_info.full_name().replace(' ', ''),
            "cardHolderCardNo": vcc_info.card_number,
            "validdate": '20' + vcc_info.card_expire.split('/')[1] + vcc_info.card_expire.split('/')[0],
            "cvv": vcc_info.security_code,
            "bankcode": "ICBC",
            "banktype": "MPAY",
            "paytype": "0",
            "userid": self.user_id,
            "firstname": "三",
            "lastname": "张",
            "address": "",
            "creditCardType": "credit"
        }
        data = {
            'm': {
                'req': json.dumps(req, separators=(',', ':')),
                'token': 'h5001',
                'lang': 'zh_CN',
                'userInfo1': '73800',
            },
            'a': '18',
            'p': '34',
        }
        pay_response = self.fliter_search(data, 'c')
        print(pay_response)

    def select_order(self, order_no):
        req = {
            "pageNo": "1",
            "orderStatus": "DZF",
            "pageSize": "10",
            "registerType": "TICKET",
            "ifThreeMouth": "0",
            "userId": self.user_id,
            "mId": self.m_id,
            "endDate": "",
            "beginDate": ""
        }
        data = {
            "m": {
                "req": json.dumps(req, separators=(',', ':')),
                "token": "h5001",
                "lang": "zh_CN",
                "userID": self.user_id,
                "userInfo1": "73800",
                "ziYinNo": self.ziyinno
            },
            "a": "5",
            "p": "9"
        }
        params = {
            'FECU': get_feca(self.fecw, AirchinaConfig.USER_AGENT, self.result['start_time'],
                             self.result['server_time']),
        }
        response = self.__mobile_script.invoke_h(data, params)
        for i in response['resp']['orderList']:
            if i['MAIN_ORDERNO'] == order_no:
                req = {
                    "orderNumber": order_no,
                    "version": "3",
                    "loginFlag": "1",
                    "userId": self.user_id,
                    "mId": self.m_id
                }
                data = {
                    "m": {
                        "req": json.dumps(req, separators=(',', ':')),
                        "token": "11",
                        "lang": "zh_CN",
                        "userInfo1": "73800",
                        "ziYinNo": self.ziyinno,
                        "userID": self.user_id
                    },
                    "a": "5",
                    "p": "14"
                }
                params = {
                    'FECU': get_feca(self.fecw, AirchinaConfig.USER_AGENT, self.result['start_time'],
                                     self.result['server_time']),
                }
                go_pay_response = self.__mobile_script.invoke_g(data, params)

                # 提交支付
                req = {
                    "orderId": order_no,
                    "orderAmount": go_pay_response['resp']['resbean']['orderPrices'],
                    "cardHolderIdType": "C",
                    "cardHolderIdNo": "152826197405070423",
                    "areaCode": "86",
                    "cardHolderTel": "13634788827",
                    "cardHolderName": "沈红",
                    "cardHolderCardNo": "5309900012104632",  # TODO 业务要求卡号写死
                    "validdate": "202804",
                    "cvv": "998",
                    "bankcode": "ICBC",
                    "banktype": "MPAY",
                    "paytype": "0",
                    "userid": self.user_id,
                    "firstname": "红",
                    "lastname": "沈",
                    "address": "",
                    "internationflag": "1",
                    "creditCardType": "credit"
                }
                data = {
                    "m": {
                        "req": json.dumps(req, separators=(',', ':')),
                        "token": "h5001",
                        "lang": "zh_CN",
                        "userInfo1": "73800"
                    },
                    "a": "18",
                    "p": "34"
                }
                params = {
                    'FECU': get_feca(self.fecw, AirchinaConfig.USER_AGENT, self.result['start_time'],
                                     self.result['server_time']),
                }
                pay_response = self.__mobile_script.pay(data, params)

                # 输入验证码支付
                serial_number = pay_response['resp']['yeePayVerifyOrderNo']
                req = {
                    "orderId": order_no,
                    "areaCode": "86",
                    "orderNo": pay_response['resp']['yeePayVerifyOrderNo'],
                    "type": "2",
                    "userId": self.user_id,
                    "cardHolderTel": "8827",
                    "verifyCode": "970417",
                    "deviceType": "H5",
                    "ipAddress": ""
                }
                data = {
                    'm': {
                        'req': json.dumps(req, separators=(',', ':')),
                        'lang': 'zh_CN',
                        'token': 'h5001',
                        'userID': self.user_id,
                        'userInfo1': '73800',
                    },
                    'a': '14',
                    'p': '82',
                }
                params = {
                    'FECU': get_feca(self.fecw, AirchinaConfig.USER_AGENT, self.result['start_time'],
                                     self.result['server_time']),
                }
                response = self.__mobile_script.invoke_g(data, params)
                if not response:
                    raise ServiceError(ServiceStateEnum.BOOKING_PAYMENT_DECLINED)
                if response.get('resp').get('code') != "00000000":
                    raise ServiceError(ServiceStateEnum.BOOKING_PAYMENT_DECLINED)
                return response, serial_number, go_pay_response

    def order_detail(self, order_no):
        req = {
            "orderNumber": order_no,
            "version": "3",
            "loginFlag": "1",
            "userId": self.user_id,
            "mId": "1-14A2H0F6"
        }
        data = {
            "m": {
                "req": json.dumps(req, separators=(',', ':')),
                "token": "11",
                "lang": "zh_CN",
                "userInfo1": "73800",
                "ziYinNo": self.ziyinno,
                "userID": self.user_id
            },
            "a": "5",
            "p": "14"
        }
        params = {
            'FECU': get_feca(self.fecw, AirchinaConfig.USER_AGENT, self.result['start_time'],
                             self.result['server_time']),
        }
        response = self.__mobile_script.invoke_g(data, params)
        order_data = OrderDetailParser.parse_order_detail(response)
        return order_data

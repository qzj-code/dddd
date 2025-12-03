import decimal
import json
from datetime import datetime
from typing import Optional, List

import redis

from common.decorators.retry_decorator import retry_decorator
from common.enums import CabinLevelEnum, PassengerTypeEnum
from common.errors import ServiceError, ServiceStateEnum, ApiStateEnum, APIError
from common.global_variable import GlobalVariable
from common.models import ProxyInfoModel
from common.models.interior_service import BundleInfoModel, PriceInfoModel, PassengerInfoModel
from common.models.task import ContactInfo
from common.utils import LogUtil
from flights.airchina_ca.common import init_utils
from flights.airchina_ca.common.flight_parse import FlightParser
from flights.airchina_ca.common.order_detail_parse_app import OrderDetailParser
from flights.airchina_ca.scripts.app_script import AppScript

LOG = LogUtil("AirchinaSearch")


class AppService():

    def __init__(self, proxy_info: Optional[ProxyInfoModel] = None):
        self.__app_script = AppScript(proxy_info=proxy_info)
        self.__app_script.initialize_http()
        self.check_token = None
        self.vice_card_no = None
        self.ziyin_no = None
        self.phone = None
        self.info_id = None
        self.user_id = None
        self.m_id = None
        self.search_id = None
        self.identity_no = None
        self.ffcabin = None
        self.if_vip_price = "0"
        self.__redis_client = redis.StrictRedis(host=GlobalVariable.REDIS_HOST, port=GlobalVariable.REDIS_PORT,
                                                db=GlobalVariable.REDIS_TASK_RESULT_DB,
                                                password=GlobalVariable.REDIS_PASSWORD,
                                                decode_responses=True)

    def initialize_http(self):
        self.__app_script.initialize_http()

    def initialize_token_and_key(self):
        self.__app_script.init_token()
        self.__app_script.get_dynamic_secret_key()
        self.__app_script.get_param_value()
        self.init_token()

    @retry_decorator(retry_service_error_list=[(ServiceStateEnum.ROBOT_CHECK, None),
                                               (ApiStateEnum.DX_SOLUTION_FAILURE, None)],
                     retry_max_number=10)
    def init_token(self):
        data = self.__app_script.get_token()
        if not data or data.get('data') is None or data.get('data').get('token') is None:
            raise APIError(ApiStateEnum.DX_SOLUTION_FAILURE)
        self.check_token = data['data']['token']
        if not self.check_token:
            raise APIError(ApiStateEnum.DX_SOLUTION_FAILURE)

    def redis_tax(self, dep, arr):
        self.__redis_tax_key = "CA" + dep + arr
        tax_dict: str = self.__redis_client.get(self.__redis_tax_key)
        if tax_dict:
            return json.loads(tax_dict)
        else:
            return False

    def add_redis_tax(self, value):
        self.__redis_client.setex(self.__redis_tax_key, 2592000, json.dumps(value))

    def get_tax(self, journeys, adt_count, chd_count):
        for journey in journeys:
            if journey.segment_list[0].carrier != 'CA' or len(journey.segment_list) > 1:
                continue
            flight_key = journey.key
            req = {
                "date": journey.segment_list[0].dep_time.strftime('%Y-%m-%d'),
                "takeoffdate": journey.segment_list[0].dep_time.strftime('%Y-%m-%dT%H:%M'),
                "flag": "0",
                "adultNum": f"{adt_count}",
                "childNum": f"{chd_count}",
                "dst": journey.segment_list[-1].arr_airport,
                "org": journey.segment_list[0].dep_airport,
                "onesearchId": "",
                "istworeq": "1",
                "flightID": flight_key,
                "iszj": "1",
                "classDesc": journey.segment_list[0].id,
                "isgap": "0",
                "flightno": journey.segment_list[0].flight_number[2:],
                "mileageFlag": "0",
                "searchId": self.search_id,
                "backDate": "",
                "infantNum": "0",
                "airline": "CA",
                "IOSSYSTEMDATE": init_utils.make_io_ssystem_date(),
                "arrivedate": journey.segment_list[-1].arr_time.strftime('%Y-%m-%dT%H:%M')
            }
            send_data = {
                "deviceType": self.__app_script.mobile_type,
                "mobileSysVer": self.__app_script.sys_ver,
                "appChannel": "CA_AIR",
                "token": self.__app_script.token,
                "dxRiskToken": "",
                "userInfo4": "",
                "userInfo3": init_utils.make_user_info3(),
                "deviceModel": self.__app_script.device_model,
                "userInfo2": init_utils.get_user_info2(self.__app_script.gt_token, self.__app_script.main_app_version),
                "userInfo1": "73800",
                "lang": "zh_CN",
                "req": "",
                "mobileTypeExtra": "App",
                "timestamp": ""
            }
            search_response = self.__app_script.get_service("ACFlight", "getACEFlightSpaceTwo", req, send_data)
            for index, value in enumerate(search_response['FFCabins']):
                self.ffcabin = value['ffcabin']
                req = {
                    "moreZjDesc": "",
                    "flag": "0",
                    "back_zj": "",
                    "upsellIndex": search_response['FFCabins'][index + 1]['index'],
                    "goBackFlag": "0",
                    "nextCabin": value['nextCabin'],
                    "classDesc": value['classDesc'],
                    "selectedPrice": value['price'],
                    "searchId": value['cabinFfNew']['searchId'],
                    "zjTrain": "",
                    "IOSSYSTEMDATE": init_utils.make_io_ssystem_date(),
                    "timestamp": "",
                    "airRedeemQual": "N",
                    "inf": "0",
                    "bookReqInfo": "",
                    "cnn": f"{chd_count}",
                    "upsellFlag": "0",
                    "userTravels": f"go:{journey.segment_list[0].dep_airport}-{journey.segment_list[-1].arr_airport}",
                    "flyBindingShopingId": "",
                    "index": value['index'],
                    "iszj": value['iszj'],
                    "smeNo": "",
                    "flightSpaceId": value['flightSpaceId'],
                    "nextPrice": search_response['FFCabins'][index + 1]['price'],
                    "selectedCabin": "N",
                    "adt": f"{adt_count}",
                    "memberNumber": self.vice_card_no
                }
                data = {
                    "deviceType": self.__app_script.mobile_type,
                    "mobileSysVer": self.__app_script.sys_ver,
                    "appChannel": "CA_AIR",
                    "token": self.__app_script.token,
                    "dxRiskToken": "",
                    "userInfo4": "",
                    "userInfo3": init_utils.make_user_info3(),
                    "deviceModel": self.__app_script.device_model,
                    "userInfo2": init_utils.get_user_info2(self.__app_script.gt_token,
                                                           self.__app_script.main_app_version),
                    "userInfo1": "73800",
                    "lang": "zh_CN",
                    "req": "",
                    "mobileTypeExtra": "App",
                    "timestamp": ""
                }
                select_flight_response = self.__app_script.get_service("ACFlight", "qryPriceTotal", req, data)
                if not select_flight_response.get('code') or select_flight_response.get('code') != '00000000':
                    raise ServiceError(ServiceStateEnum.SERVICE_ERROR, "选择价格失败")
                tax_dict = {}
                for i, v in select_flight_response['CountPrice']['tripList'].items():
                    if v['quantity'] == '0':
                        continue
                    passenger_type = "CHD" if v['code'] == 'CNN' else v['code']
                    tax_dict[passenger_type] = {}
                    for taxes in v['taxesFeesList']:
                        if taxes['taxFeeType'] == 'CN':
                            tax = taxes['taxFeePrice']
                            tax_dict[passenger_type]['tax'] = tax
                        elif taxes['taxFeeType'] == 'YQ':
                            oifee = taxes['taxFeePrice']
                            tax_dict[passenger_type]['oifee'] = oifee
                return tax_dict

    def login(self, user, password):
        req = {
            "password": password,
            "loginType": "3",
            "appVer": self.__app_script.app_ver,
            "loginName": user,
            "mobileType": self.__app_script.mobile_type,
            "sysVer": self.__app_script.sys_ver,
            "registerType": "0",
            "operType": "0",
            "version": "1",
            "IOSSYSTEMDATE": init_utils.make_io_ssystem_date(),
            "mobileTypeExtra": self.__app_script.mobile_type_extra
        }
        send_data = {
            'deviceType': self.__app_script.mobile_type,
            'latitude': '39.785063463879084',
            'mobileSysVer': self.__app_script.sys_ver,
            'appChannel': 'CA_AIR',
            'token': self.__app_script.gt_token,
            'captchaClientToken': '',
            'dxRiskToken': '',
            'userInfo4': '',
            'userInfo3': init_utils.make_user_info3(),
            'deviceModel': self.__app_script.device_model,
            'userInfo2': init_utils.get_user_info2(self.__app_script.gt_token, self.__app_script.main_app_version),
            'userInfo1': self.__app_script.main_app_version,
            'lang': 'zh_CN',
            'req': '',
            'mobileTypeExtra': self.__app_script.mobile_type_extra,
            'timestamp': '',
            'longitude': '116.32555941312754'
        }

        response = self.__app_script.get_service('ACLogin', 'login', req, send_data)
        if response.get('code') and response.get('code') != '00000000':
            raise ServiceError(ServiceStateEnum.INVALID_DATA, f"{response.get('msg')},{user}")
        self.user_id = response['userId']
        self.info_id = response['InfoId']
        self.m_id = response['mId']
        self.vice_card_no = response['viceCardNo']
        self.ziyin_no = response['ziYinNo']
        self.phone = response['phone']
        self.__app_script.info_id = self.info_id
        self.__app_script.user_id = self.user_id
        req = {"flag": "1", "mobileNo": user, "userId": self.user_id,
               "IOSSYSTEMDATE": init_utils.make_io_ssystem_date()}
        data = {
            "deviceType": "Android",
            "mobileSysVer": "29",
            "appChannel": "CA_AIR",
            "token": self.__app_script.token,
            "dxRiskToken": "",
            "userInfo4": "",
            "userInfo3": init_utils.make_user_info3(),
            "deviceModel": "LGE LM-G820",
            "userInfo2": init_utils.get_user_info2(self.__app_script.gt_token, self.__app_script.main_app_version),
            "userInfo1": "73800",
            "lang": "zh_CN",
            "req": "",
            "mobileTypeExtra": "App",
            "timestamp": ""
        }
        response = self.__app_script.get_service("ACMCommon", "queryBannerList", req, data)

    @retry_decorator(retry_service_error_list=[(ServiceStateEnum.ROBOT_CHECK, initialize_http)],
                     retry_max_number=3)
    def search(self, airport_data, adult_count: int, child_count: int, currency: str, promo_code: str = "",
               task_type: str = "search"):
        self.init_token()
        response = self.__app_script.search(airport_data, adult_count, child_count)
        response_1 = {
            "resp": {
                "goto": response['goto']
            }
        }
        self.search_id = response['goto']['flightInfomationList'][0]['flightSegmentList'][0]['searchId']
        result = FlightParser.parse_flight_data(response_1, child_count)
        return result

    def fliter(self, journeys, adt_count, chd_count, task_type: str = ""):
        counts = 0
        tags = ['随机立减', '限时优惠', '会员直减', '限时特惠', '定立减', '同行惠']
        for journey in journeys:
            bundles = []
            if counts > 5:
                break
            for i in journey.bundle_list:
                if (not any(tag
                            in i.price_tag for tag in tags) or i.cabin_level.value != 'Y') and task_type == 'search':
                    continue
                counts += 1
                flight_key = journey.key
                req = {
                    "date": journey.segment_list[0].dep_time.strftime('%Y-%m-%d'),
                    "takeoffdate": journey.segment_list[0].dep_time.strftime('%Y-%m-%dT%H:%M'),
                    "flag": "0",
                    "adultNum": f"{adt_count}",
                    "childNum": f"{chd_count}",
                    "dst": journey.segment_list[-1].arr_airport,
                    "org": journey.segment_list[0].dep_airport,
                    "onesearchId": "",
                    "istworeq": "1",
                    "flightID": flight_key,
                    "iszj": "1",
                    "classDesc": journey.segment_list[0].id,
                    "isgap": "0",
                    "flightno": journey.segment_list[0].flight_number[2:],
                    "mileageFlag": "0",
                    "searchId": self.search_id,
                    "backDate": "",
                    "infantNum": "0",
                    "airline": "CA",
                    "IOSSYSTEMDATE": init_utils.make_io_ssystem_date(),
                    "arrivedate": journey.segment_list[-1].arr_time.strftime('%Y-%m-%dT%H:%M')
                }
                send_data = {
                    "deviceType": self.__app_script.mobile_type,
                    "mobileSysVer": self.__app_script.sys_ver,
                    "appChannel": "CA_AIR",
                    "token": self.__app_script.token,
                    "dxRiskToken": "689d9ab4r0HojFSxonMQaABQTNRi7tlZYiuyV223",
                    "userInfo4": "",
                    "userInfo3": init_utils.make_user_info3(),
                    "deviceModel": self.__app_script.device_model,
                    "userInfo2": init_utils.get_user_info2(self.__app_script.gt_token,
                                                           self.__app_script.main_app_version),
                    "userInfo1": "73800",
                    "lang": "zh_CN",
                    "req": "",
                    "mobileTypeExtra": "App",
                    "timestamp": ""
                }
                response = self.__app_script.get_service("ACFlight", "getACEFlightSpaceTwo", req, send_data)
                for j in response['FFCabins']:
                    new_vip_price = 0
                    if j['moreZjDesc']:
                        for i in json.loads(j['moreZjDesc']):
                            if i['morePcname'] == '同行惠' and int(i['num'][0]) > 1 and (adt_count + chd_count) > 1:
                                if chd_count == 0 and int(i['mustExistChd']) == 0:
                                    new_vip_feeId = i['id']
                                    new_vip_price = int(i['price'])
                                    break
                                elif chd_count > 0 and int(i['mustExistChd']) > 0:
                                    new_vip_feeId = i['id']
                                    new_vip_price = int(i['price'])
                                    break
                                else:
                                    pass
                    price_info = []
                    passenger_type_list = [PassengerTypeEnum.ADT] if chd_count == 0 else [PassengerTypeEnum.ADT,
                                                                                          PassengerTypeEnum.CHD]
                    if j['vip_price'] == '':
                        discount = 0
                    else:
                        discount = decimal.Decimal(j['price']) - decimal.Decimal(j['vip_price'])
                    # j['vip_price'] 优惠后的价格 , j['priceN'] 优惠前的价格
                    price_tag = []
                    for lable_name in j['serviceInfo']['lableNameList']:
                        price_tag.append(lable_name['acivity_Name'])
                    for lable_name in j['serviceInfo']['lableNameList']:
                        price_tag.append(lable_name['acivity_Name'])
                    if '会员直减' in price_tag and j.get('zjActivityDesc') == '<p>会员登录购票享95折优惠，优惠前儿童旅客为五折儿童票价则不享受直减优惠。</p>':
                        fare = int(float(j['price']) * 0.95)
                    else:
                        fare = float(j['vip_price']) - new_vip_price if j['vip_price'] else float(j['price']) - new_vip_price
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

    def select_flight(self, journey_infos, adult_count, child_count, use_bundle_info: BundleInfoModel):
        journey = journey_infos[0]
        flight_key = journey.key
        req = {
            "date": journey.segment_list[0].dep_time.strftime('%Y-%m-%d'),
            "takeoffdate": journey.segment_list[0].dep_time.strftime('%Y-%m-%dT%H:%M'),
            "flag": "0",
            "adultNum": f"{adult_count}",
            "childNum": f"{child_count}",
            "dst": journey.segment_list[-1].arr_airport,
            "org": journey.segment_list[0].dep_airport,
            "onesearchId": "",
            "istworeq": "1",
            "flightID": flight_key,
            "iszj": "1",
            "classDesc": journey.segment_list[0].id,
            "isgap": "0",
            "flightno": journey.segment_list[0].flight_number[2:],
            "mileageFlag": "0",
            "searchId": self.search_id,
            "backDate": "",
            "infantNum": "0",
            "airline": "CA",
            "IOSSYSTEMDATE": init_utils.make_io_ssystem_date(),
            "arrivedate": journey.segment_list[-1].arr_time.strftime('%Y-%m-%dT%H:%M:%S')
        }
        send_data = {
            "deviceType": self.__app_script.mobile_type,
            "mobileSysVer": self.__app_script.sys_ver,
            "appChannel": "CA_AIR",
            "token": self.__app_script.token,
            "dxRiskToken": "",
            "userInfo4": "",
            "userInfo3": init_utils.make_user_info3(),
            "deviceModel": self.__app_script.device_model,
            "userInfo2": init_utils.get_user_info2(self.__app_script.gt_token, self.__app_script.main_app_version),
            "userInfo1": "73800",
            "lang": "zh_CN",
            "req": "",
            "mobileTypeExtra": "App",
            "timestamp": ""
        }
        search_response = self.__app_script.get_service("ACFlight", "getACEFlightSpaceTwo", req, send_data)
        price_id = use_bundle_info.id
        for index, value in enumerate(search_response['FFCabins']):
            if value['price'] == price_id:
                self.ffcabin = value['ffcabin']
                book_req_info = ""
                if value.get('bookReqInfo'):
                    book_req_info = value.get('bookReqInfo')
                req = {
                    "moreZjDesc": value['moreZjDesc'],
                    "flag": "0",
                    "back_zj": "",
                    "upsellIndex": search_response['FFCabins'][index + 1]['index'],
                    "goBackFlag": "0",
                    "nextCabin": value['nextCabin'],
                    "classDesc": value['classDesc'],
                    "selectedPrice": value['price'],
                    "searchId": value['cabinFfNew']['searchId'],
                    "zjTrain": "",
                    "IOSSYSTEMDATE": init_utils.make_io_ssystem_date(),
                    "timestamp": "",
                    "airRedeemQual": "N",
                    "inf": "0",
                    "bookReqInfo": book_req_info,
                    "cnn": f"{child_count}",
                    "upsellFlag": "0",
                    "userTravels": f"go:{journey.segment_list[0].dep_airport}-{journey.segment_list[-1].arr_airport}",
                    "flyBindingShopingId": "",
                    "index": value['index'],
                    "iszj": value['iszj'],
                    "smeNo": "",
                    "flightSpaceId": value['flightSpaceId'],
                    "nextPrice": search_response['FFCabins'][index + 1]['price'],
                    "selectedCabin": "N",
                    "adt": f"{adult_count}",
                    "memberNumber": self.vice_card_no
                }
                data = {
                    "deviceType": self.__app_script.mobile_type,
                    "mobileSysVer": self.__app_script.sys_ver,
                    "appChannel": "CA_AIR",
                    "token": self.__app_script.token,
                    "dxRiskToken": "",
                    "userInfo4": "",
                    "userInfo3": init_utils.make_user_info3(),
                    "deviceModel": self.__app_script.device_model,
                    "userInfo2": init_utils.get_user_info2(self.__app_script.gt_token,
                                                           self.__app_script.main_app_version),
                    "userInfo1": "73800",
                    "lang": "zh_CN",
                    "req": "",
                    "mobileTypeExtra": "App",
                    "timestamp": ""
                }
                select_flight_response = self.__app_script.get_service("ACFlight", "qryPriceTotal", req, data)
                if not select_flight_response.get('code') or select_flight_response.get('code') != '00000000':
                    raise ServiceError(ServiceStateEnum.SERVICE_ERROR, "选择价格失败")
                for i, v in select_flight_response['CountPrice']['tripList'].items():
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
                return select_flight_response, search_response

    def add_passenger(self, passengers_list: List[PassengerInfoModel], select_flight_response: dict, ):
        """
                选择乘机人请求
                Args:
                    passengers_list: 乘机人列表
                    contact_info: 联系人列表
                    select_flight_response: 选择价格的响应

                Returns: 乘机人查询结果列表

                """
        departure = select_flight_response['CountPrice']['tripSegmentList'][0]['departureDate']
        departure_date = datetime.fromisoformat(departure).date().strftime('%Y-%m-%d')
        check_service_rule = select_flight_response['CountPrice']['checkServiceRule']

        # 查询乘机人列表
        req = {
            "userFlag": "0",
            "isDisabledJP": "2",
            "onlyAdult": "1",
            "mId": self.m_id,
            "pageSize": "30",
            "registerType": "0",
            "ifAlieneeInfo": "0",
            "totalRows": "-1",
            "type": "1",
            "travelDate": departure_date,
            "filterIdentityKind": "",
            "currentPage": "1",
            "IOSSYSTEMDATE": init_utils.make_io_ssystem_date(),
        }
        data = {
            "deviceType": self.__app_script.mobile_type,
            "mobileSysVer": self.__app_script.sys_ver,
            "appChannel": "CA_AIR",
            "token": self.__app_script.token,
            "dxRiskToken": "",
            "userInfo4": "",
            "userInfo3": init_utils.make_user_info3(),
            "deviceModel": self.__app_script.device_model,
            "userInfo2": init_utils.get_user_info2(self.__app_script.gt_token, self.__app_script.main_app_version),
            "userInfo1": "73800",
            "lang": "zh_CN",
            "req": "",
            "mobileTypeExtra": "App",
            "timestamp": ""
        }
        search_passenger_list = self.__app_script.get_service("ACPassenger", "qryNewPassengers", req, data)

        # self.identity_no = \
        #     select_flight_response['CountPrice']['passengerInfos']['passengerInfos'][0]['identityInfos'][0][
        #         'identityNo']
        self.identity_no = select_flight_response['CountPrice']['passengerInfos']['oneSelf']['identityInfos'][0]
        # 先添加乘机人
        for index, value in enumerate(passengers_list):
            req = {
                "birthday": value.birthday.strftime('%Y-%m-%d'),
                "areaCode": value.mob_country_code,
                "passengerPhone": value.mobile,
                "gender": value.gender.value,
                "cnLastName": value.last_name(),
                "nationalityId": value.nationality,
                "identityInfos": [
                    {
                        "cnorenName": value.issue_place,
                        "identityKind": "C",
                        "identityNo": value.card_number,
                        "isAdd": False,
                        "isSelected": False
                    }
                ],
                "cardInfos": [],
                "cnFirstName": value.first_name(),
                "userId": self.user_id,
                "IOSSYSTEMDATE": init_utils.make_io_ssystem_date(),
            }
            data = {
                "deviceType": self.__app_script.mobile_type,
                "mobileSysVer": self.__app_script.sys_ver,
                "appChannel": "CA_AIR",
                "token": self.__app_script.token,
                "dxRiskToken": "",
                "userInfo4": "",
                "userInfo3": init_utils.make_user_info3(),
                "deviceModel": self.__app_script.device_model,
                "userInfo2": init_utils.get_user_info2(self.__app_script.gt_token, self.__app_script.main_app_version),
                "userInfo1": "73800",
                "lang": "zh_CN",
                "req": "",
                "mobileTypeExtra": "App",
                "timestamp": ""
            }
            add_passenger_response = self.__app_script.get_service("ACPassenger", "addNewPassengers", req, data)
            if add_passenger_response['code'] == '06040004':
                LOG.info(add_passenger_response['msg'])
                continue
            if add_passenger_response['code'] != "00000000":
                raise ServiceError(ServiceStateEnum.SERVICE_ERROR,
                                   f"添加联系人失败:{add_passenger_response['msg']}")

    def select_passenger(self, passengers_list: List[PassengerInfoModel], select_flight_response: dict, user: str):
        """
        选择乘机人请求
        Args:
            passengers_list: 乘机人列表
            contact_info: 联系人列表
            select_flight_response: 选择价格的响应

        Returns: 乘机人查询结果列表

        """
        departure = select_flight_response['CountPrice']['tripSegmentList'][0]['departureDate']
        departure_date = datetime.fromisoformat(departure).date().strftime('%Y-%m-%d')
        check_service_rule = select_flight_response['CountPrice']['checkServiceRule']

        # 查询乘机人列表
        req = {
            "userFlag": "0",
            "isDisabledJP": "2",
            "onlyAdult": "1",
            "mId": self.m_id,
            "pageSize": "1000",
            "registerType": "0",
            "ifAlieneeInfo": "0",
            "totalRows": "-1",
            "type": "1",
            "travelDate": departure_date,
            "filterIdentityKind": "",
            "currentPage": "1",
            "IOSSYSTEMDATE": init_utils.make_io_ssystem_date(),
        }
        data = {
            "deviceType": self.__app_script.mobile_type,
            "mobileSysVer": self.__app_script.sys_ver,
            "appChannel": "CA_AIR",
            "token": self.__app_script.token,
            "dxRiskToken": "",
            "userInfo4": "",
            "userInfo3": init_utils.make_user_info3(),
            "deviceModel": self.__app_script.device_model,
            "userInfo2": init_utils.get_user_info2(self.__app_script.gt_token, self.__app_script.main_app_version),
            "userInfo1": "73800",
            "lang": "zh_CN",
            "req": "",
            "mobileTypeExtra": "App",
            "timestamp": ""
        }
        search_passenger_list = self.__app_script.get_service("ACPassenger", "qryNewPassengers", req, data)
        total_price = '0'  # 总票价
        total_price_pre = '0'
        flight_list = []
        for i in select_flight_response['CountPrice']['tripSegmentList']:
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
            for i in search_passenger_list['passengerInfos']:
                if i['identityInfos'] == []:
                    continue
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
            raise ServiceError(ServiceStateEnum.SERVICE_ERROR, f"选择乘机人数量错误,{user}")
        trip_id = select_flight_response['CountPrice']['tripId']
        req = {
            "arrivalCityCode": select_flight_response['CountPrice']['tripSegmentList'][-1]['destinationCode'],
            "openJawList": [
                {
                    "od": f"{select_flight_response['CountPrice']['tripSegmentList'][0]['originCode']}-{select_flight_response['CountPrice']['tripSegmentList'][-1]['destinationCode']}"
                }
            ],
            "memCrNo": self.identity_no,
            "totalPrice": total_price,
            "shareFlag": "0",
            "mId": self.m_id,
            "studentFlag": "0",
            "tripId": trip_id,
            "userId": self.user_id,
            "version": "1",
            "interFlag": "0",
            "openJawFlag": "0",
            "isBack": "0",
            "totalPricePre": total_price_pre,
            "flightList": flight_list,
            "departureCityCode": select_flight_response['CountPrice']['tripSegmentList'][0]['originCode'],
            "checkServiceRule": check_service_rule,
            "memLevel": "Normal",
            "passengerList": select_passenger_list,
            "IOSSYSTEMDATE": init_utils.make_io_ssystem_date(),
            "productType": "1",
            "memCrId": "C"
        }
        data = {
            "deviceType": self.__app_script.mobile_type,
            "mobileSysVer": self.__app_script.sys_ver,
            "appChannel": "CA_AIR",
            "token": self.__app_script.token,
            "dxRiskToken": "",
            "userInfo4": "",
            "userInfo3": init_utils.make_user_info3(),
            "deviceModel": self.__app_script.device_model,
            "userInfo2": init_utils.get_user_info2(self.__app_script.gt_token, self.__app_script.main_app_version),
            "userInfo1": "73800",
            "lang": "zh_CN",
            "req": "",
            "mobileTypeExtra": "App",
            "timestamp": ""
        }
        response_9_17 = self.__app_script.get_service("ACCoupon", "qryUsableCoupons", req, data)
        if response_9_17.get('code') != "00000000":
            raise ServiceError(ServiceStateEnum.SERVICE_ERROR, "选择乘机人失败")
        return search_passenger_list

    def go_pay(self, select_flight_response: dict, contact_info: ContactInfo, search_passenger_list: dict,
               passenger_infos: [PassengerInfoModel], user: str, search_response: dict):
        """
        跳转支付页面
        Args:
            select_flight_response: 航班信息
            contact_info: 联系人信息
            search_passenger_list: 网站乘机人列表 里面有网站乘机人对应的id
            passenger_infos: 原始乘机人列表

        Returns: 订单详情、总价格

        """
        adult_count = sum([1 for x in passenger_infos if x.passenger_type == PassengerTypeEnum.ADT])
        child_count = sum([1 for x in passenger_infos if x.passenger_type == PassengerTypeEnum.CHD])
        new_vip_feeId = None
        new_vip_price = 0
        if search_response['FFCabins'][0]['moreZjDesc']:
            for i in json.loads(search_response['FFCabins'][0]['moreZjDesc']):
                if i['morePcname'] == '同行惠' and int(i['num'][0]) > 1 and (adult_count + child_count) > 1:
                    if child_count == 0 and int(i['mustExistChd']) == 0:
                        new_vip_feeId = i['id']
                        new_vip_price = int(i['price'])
                        break
                    elif child_count > 0 and int(i['mustExistChd']) > 0:
                        new_vip_feeId = i['id']
                        new_vip_price = int(i['price'])
                        break
                    else:
                        pass
        book_req_info = ""
        if search_response['FFCabins'][0].get('bookReqInfo'):
            book_req_info = search_response['FFCabins'][0].get('bookReqInfo')
        if len(passenger_infos) > 1:
            if_pnr_separate = "1"
        else:
            if_pnr_separate = ""
        trip_id = select_flight_response['CountPrice']['tripId']
        telephones = []
        api_ss = []
        travelers = []
        fares = []
        flights = []
        index = 0
        preferential_price = 0  # 优惠价格
        if select_flight_response['CountPrice'].get('discountListGo'):
            for i in select_flight_response['CountPrice']['discountListGo']:
                preferential_price += int(i['price'])
        pre_total_price = 0
        for key, value in select_flight_response['CountPrice']['tripList'].items():
            index += 1
            if value['quantity'] == '0':
                continue
            total_fare_amount = int(value['totalFareAmount'])
            if value.get('preDiscountList'):
                for i in value['preDiscountList']:
                    total_fare_amount += int(i['discountPrice'])
            pre_total_price += total_fare_amount * int(value['quantity'])
            # pre_total_price = str(int(value['totalFareAmount']) - preferential_price)
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
            for iii, vvv in enumerate(select_flight_response['CountPrice']['tripSegmentList']):
                departure_date = datetime.fromisoformat(vvv['departureDate']).strftime('%Y-%m-%d')
                fare_infos.append({
                    "FareBasisCode": select_flight_response['CountPrice']['flightFareList'][0]['fareBasisCode'],
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
                    "classDesc": select_flight_response['CountPrice']['classDesc'],
                    "fareComponent": {
                        "taxs": taxs,
                        "Taxes_Amount": str(tax_amount),
                        "Amount": str(int(value['baseFareAmount'])),
                        "Total": str(int(value['totalFareAmount']))
                        # "Amount": str(int(value['baseFareAmount']) - preferential_price - new_vip_price),
                        # "Total": str(int(value['totalFareAmount']) - preferential_price - new_vip_price)
                    },
                    "tripId": trip_id
                })
            if key == 'ADT':
                quantity = adult_count
            else:
                quantity = child_count
            for i in range(0, quantity):
                fare_dict = {
                    "TravelerIDRef": f"T{i + 1}",
                    "Taxes_Amount": str(tax_amount),
                    "BaseFare_Amount": str(int(value['baseFareAmount']) - preferential_price - new_vip_price),
                    "Type": "CHD" if value['code'] == 'CNN' else value['code'],
                    "fareInfos": fare_infos,
                    "taxs": taxs,
                    "IfPcPay": "0",
                    "IfEcPay": "0",
                    "IfMorePc": "0" if new_vip_price == 0 else "1",
                    "IfEvPay": "0",
                    "IfJlPay": "0",
                    "evFeeEach": "0",
                    "jlFeeEach": "0",
                    "exst_taxs": []
                }
                if key == "ADT":
                    fare_dict['teenager'] = "0"
                    fare_dict['umFee'] = "0"
                if select_flight_response['CountPrice'].get('discountListGo'):
                    fare_dict['discountList'] = select_flight_response['CountPrice']['discountListGo']
                    # if fare_dict['discountList'][0].get('lay_people') is not None:
                    #     del fare_dict['discountList'][0]['lay_people']
                    #     del fare_dict['discountList'][0]['priceFence']
                    #     fare_dict['discountList'][0]['discountPrice'] = ''
                    #     fare_dict['discountList'][0]['isZjTrainList'] = False
                    if select_flight_response['CountPrice']['discountListGo'][0]['discountName'] in ['随机立减',
                                                                                                     '限时优惠',
                                                                                                     '会员直减',
                                                                                                     '限时特惠',
                                                                                                     '定立减',
                                                                                                     '同行惠']:
                        self.if_vip_price = 1
                    else:
                        self.if_vip_price = 0
                fares.append(fare_dict)
        adt_count = 0
        chd_count = 0
        for index, value in enumerate(passenger_infos):
            if value.passenger_type.value == 'ADT':
                adt_count += 1
            elif value.passenger_type.value == 'CHD':
                chd_count += 1
            for i in search_passenger_list['passengerInfos']:
                if i['identityInfos'] == []:
                    continue
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
                    "DocExpirationDate": "",
                    "Gender": value.gender.value,
                    "GivenName": value.first_name(),
                    "GivenNameEn": "",
                    "IdentityId": i['identityInfos'][0]['identityId'],
                    "Surname": value.last_name(),
                    "SurnameEn": "",
                    "IssueCountry": "",
                    "NationalityCountry": value.nationality,
                    "TravelerIDRef": f"T{index + 1}",
                    "validityType": i['identityInfos'][0]['validityType']
                })
                travelers.append({
                    "AssociationID": f"T{index + 1}",
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
        for index, trip_segment in enumerate(select_flight_response['CountPrice']['tripSegmentList']):
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
                "flightModel": "",
                "foodType": "",
                "planeCompanyName": "",
                "totalTime": trip_segment['totalFlightDuration'],
                "flightModelType": "",
                "classDesc": select_flight_response['CountPrice']['classDesc'],
                "preClassOfService": "",
                "netFlag": ""
            })

        origin_code = select_flight_response['CountPrice']['tripSegmentList'][0]['originCode']
        booking_class = select_flight_response['CountPrice']['tripSegmentList'][0]['bookingClass']
        destination_code = select_flight_response['CountPrice']['tripSegmentList'][-1]['destinationCode']
        go = f"{origin_code}_{destination_code};{booking_class[0]};"
        commodity_id = select_flight_response['CountPrice']['tripSegmentList'][0]['marketingAirline'] + \
                       select_flight_response['CountPrice']['tripSegmentList'][0]['flightNumber']
        req = {
            "mobileIp": "",
            "acceptWay": "1",
            "evTotalPrice": 0,
            "memCrNo": self.identity_no,
            "mobileSysVer": "29",
            "International_Flag": "1",
            "transitflag": "0",
            "password": "",
            "searchId": self.search_id,
            "isDoubleSeat": "0",
            "smeNoType": "0",
            "frequentTravelerGroups": [],
            "searchIdGapGo": self.search_id,
            "IOSSYSTEMDATE": init_utils.make_io_ssystem_date(),
            "insurances": [],
            "veriCode": "",
            "segmentflag": "0",
            "firstTicketInfo": select_flight_response['CountPrice'].get('firstTicketInfo'),
            "travelers": travelers,
            "goFareFamilyId": self.ffcabin,
            "areaCode": contact_info.mobile_country_code,
            "smeNoFlag": "0",
            "mileageFlag": "0",
            "jlTotalPrice": 0,
            "memLevel": "Normal",
            "arrivalAirport": destination_code,
            "checkPriceMap": {
                "isgap": "0",
                "tripId": trip_id,
                "tripInfo": {
                    "tripType": "OW",
                    "go": go,
                    "idflag": "0",
                    "back": "",
                    "zj_number": "0"
                },
                "classDesc": select_flight_response['CountPrice']['classDesc']
            },
            "APISs": api_ss,
            "upsale_fee": 0,
            "searchIdGapBack": "",
            "telephones": telephones,
            "tripId": trip_id,
            "fares": fares,
            "stopflag": "0",
            "ifVipPrice": self.if_vip_price,
            "vipCard": self.ziyin_no,
            "email": contact_info.email,
            "memCrId": "C",
            "bookReqInfo": book_req_info,
            "upPrefee": "",
            "upsale": "0",
            "userAreaCode": contact_info.mobile_country_code,
            "flyBindingShopingId": "",
            "mobileType": "Android",
            "mId": self.m_id,
            "journeySheet": {
                "type": "0",
                "version": "1"
            },
            "ticketType": "1",
            "registerMemberReq": [],
            "userId": self.user_id,
            "departAirport": origin_code,
            "rClassLinkageId": "",
            "preTotalPrice": pre_total_price,
            "ifMailConnPerson": "0",
            "contactUser": contact_info.name.replace('/', ''),
            "flights": flights,
            "contactPhone": contact_info.mobile,
            "vipFee": "0"
        }
        if new_vip_feeId:
            req['newVipFeeId'] = new_vip_feeId
        data = {
            "deviceType": self.__app_script.mobile_type,
            "mobileSysVer": self.__app_script.sys_ver,
            "appChannel": "CA_AIR",
            "token": self.__app_script.token,
            "dxRiskToken": "",
            "userInfo4": "",
            "userInfo3": init_utils.make_user_info3(),
            "deviceModel": self.__app_script.device_model,
            "userInfo2": init_utils.get_user_info2(self.__app_script.gt_token, self.__app_script.main_app_version),
            "userInfo1": "73800",
            "lang": "zh_CN",
            "req": "",
            "mobileTypeExtra": "App",
            "timestamp": ""
        }
        go_pay_response = self.__app_script.get_service("ACBuyTicket", "subTicketOrder", req, data)
        if go_pay_response.get('msg') and go_pay_response.get('msg') == '请求存在风险，被拦截':
            self.init_token()
            data = {
                "deviceType": self.__app_script.mobile_type,
                "mobileSysVer": self.__app_script.sys_ver,
                "appChannel": "CA_AIR",
                "token": self.__app_script.token,
                "captchaClientToken": self.check_token + ":",
                "dxRiskToken": "",
                "userInfo4": "",
                "captchatype": "1",
                "userInfo3": init_utils.make_user_info3(),
                "deviceModel": self.__app_script.device_model,
                "userInfo2": init_utils.get_user_info2(self.__app_script.gt_token, self.__app_script.main_app_version),
                "userInfo1": "73800",
                "lang": "zh_CN",
                "req": "",
                "mobileTypeExtra": "App",
                "timestamp": ""
            }
            go_pay_response = self.__app_script.get_service("ACBuyTicket", "subTicketOrder", req, data)
        if not go_pay_response.get('orderId'):
            raise ServiceError(ServiceStateEnum.INVALID_DATA,
                               f"""{go_pay_response.get('msg', "提交订单失败")},{user}""")
        return go_pay_response, select_flight_response['CountPrice']['totalPriceAmount']

    def logout(self):
        req = {
            "userId": self.user_id,  # 要退出账号的userId
            "IOSSYSTEMDATE": init_utils.make_io_ssystem_date()
        }
        data = {
            "deviceType": self.__app_script.mobile_type,
            "mobileSysVer": self.__app_script.sys_ver,
            'appChannel': 'CA_AIR',
            "token": self.__app_script.token,
            'dxRiskToken': '',
            'userInfo4': '',
            'userInfo3': init_utils.make_user_info3(),
            "deviceModel": self.__app_script.device_model,
            "userInfo2": init_utils.get_user_info2(self.__app_script.gt_token, self.__app_script.main_app_version),
            'userInfo1': "73800",
            'lang': 'zh_CN',
            'req': '',
            'mobileTypeExtra': "App",
            'timestamp': '',
        }
        response = self.__app_script.get_service('ACPayWallet', 'checkIfOpenWallet', req, data)

        req = {
            "MemberId": self.m_id,
            "UserId": self.user_id,
            "IOSSYSTEMDATE": init_utils.make_io_ssystem_date()
        }
        data = {
            "deviceType": self.__app_script.mobile_type,
            "mobileSysVer": self.__app_script.sys_ver,
            'appChannel': 'CA_AIR',
            "token": self.__app_script.token,
            'dxRiskToken': '',
            'userInfo4': '',
            'userInfo3': init_utils.make_user_info3(),
            "deviceModel": self.__app_script.device_model,
            "userInfo2": init_utils.get_user_info2(self.__app_script.gt_token, self.__app_script.main_app_version),
            'userInfo1': "73800",
            'lang': 'zh_CN',
            'req': '',
            'mobileTypeExtra': "App",
            'timestamp': '',
        }
        response = self.__app_script.get_service('ACAccount', 'qryMileageSummary', req, data)

        req = {
            "userId": self.user_id,  # 要退出账号的userId
            "IOSSYSTEMDATE": init_utils.make_io_ssystem_date()
        }
        data = {
            "deviceType": self.__app_script.mobile_type,
            "mobileSysVer": self.__app_script.sys_ver,
            'appChannel': 'CA_AIR',
            "token": self.__app_script.token,
            'dxRiskToken': '',
            'userInfo4': '',
            'userInfo3': init_utils.make_user_info3(),
            "deviceModel": self.__app_script.device_model,
            "userInfo2": init_utils.get_user_info2(self.__app_script.gt_token, self.__app_script.main_app_version),
            'userInfo1': "73800",
            'lang': 'zh_CN',
            'req': '',
            'mobileTypeExtra': "App",
            'timestamp': '',
        }
        response = self.__app_script.get_service("ACActivity", "queryPersonalProtect", req, data)

        req = {
            "USER_ID": self.user_id,  # 要退出账号的userId
            "IOSSYSTEMDATE": init_utils.make_io_ssystem_date()
        }

        self.user_id = ''
        self.info_id = ''  # 清空infoID 和 userID
        self.__app_script.info_id = ""
        self.__app_script.user_id = ""
        data = {
            "deviceType": self.__app_script.mobile_type,
            "mobileSysVer": self.__app_script.sys_ver,
            'appChannel': 'CA_AIR',
            "token": self.__app_script.token,
            "dxRiskToken": "",
            "userInfo4": "",
            'userInfo3': init_utils.make_user_info3(),
            "deviceModel": self.__app_script.device_model,
            "userInfo2": init_utils.get_user_info2(self.__app_script.gt_token, self.__app_script.main_app_version),
            "userInfo1": "73800",
            "lang": "zh_CN",
            "req": "",
            "mobileTypeExtra": "App",
            "timestamp": ""
        }
        response = self.__app_script.get_service("ACLogin", "logout", req, data)
        return True

    def select_order(self, order_no: str):
        req = {
            "registerType": "TICKET",
            "orderStatus": "QB",
            "beginDate": "",
            "endDate": "",
            "ifThreeMouth": "0",
            "pageNo": "1",
            "pageSize": "10",
            "IOSSYSTEMDATE": init_utils.make_io_ssystem_date(),
        }
        data = {
            "deviceType": self.__app_script.mobile_type,
            "mobileSysVer": self.__app_script.sys_ver,
            'appChannel': 'CA_AIR',
            "token": self.__app_script.token,
            "dxRiskToken": "",
            "userInfo4": "",
            'userInfo3': init_utils.make_user_info3(),
            "deviceModel": self.__app_script.device_model,
            "userInfo2": init_utils.get_user_info2(self.__app_script.gt_token, self.__app_script.main_app_version),
            "userInfo1": "73800",
            "lang": "zh_CN",
            "req": "",
            "mobileTypeExtra": "App",
            "timestamp": ""
        }
        response = self.__app_script.get_service("ACOrder", "newOrderList", req, data)
        if response.get('code') and response.get('code') == '00000000':
            for i in response['orderList']:
                if i['MAIN_ORDERNO'] == order_no:
                    show_order_prices = i['SHOWORDERPRICES']
                    req = {
                        "regNo": order_no,
                        "payNum": show_order_prices,
                        "userId": self.user_id,
                        "IOSSYSTEMDATE": init_utils.make_io_ssystem_date()
                    }
                    data = {
                        "deviceType": self.__app_script.mobile_type,
                        "mobileSysVer": self.__app_script.sys_ver,
                        'appChannel': 'CA_AIR',
                        "token": self.__app_script.token,
                        "dxRiskToken": "",
                        "userInfo4": "",
                        'userInfo3': init_utils.make_user_info3(),
                        "deviceModel": self.__app_script.device_model,
                        "userInfo2": init_utils.get_user_info2(self.__app_script.gt_token,
                                                               self.__app_script.main_app_version),
                        "userInfo1": "73800",
                        "lang": "zh_CN",
                        "req": "",
                        "mobileTypeExtra": "App",
                        "timestamp": ""
                    }
                    response = self.__app_script.get_service("ACOrder", "newOrderList", req, data)
                    req = {
                        "cvv": "123",
                        "firstname": "鹏磊",
                        "address": "",
                        "orderId": order_no,
                        "cardHolderName": "高鹏磊",
                        "banktype": "MPAY",
                        "creditCardType": "credit",
                        "userid": self.user_id,
                        "lastname": "高",
                        "cardHolderTel": "持卡人手机号",
                        "validdate": "203501",
                        "areaCode": "86",
                        "orderAmount": show_order_prices,
                        "inputMode": "0",
                        "cardHolderIdNo": "持卡人身份证",
                        "cardHolderIdType": "C",
                        "internationflag": "1",
                        "paytype": "0",
                        "IOSSYSTEMDATE": init_utils.make_io_ssystem_date(),
                        "cardHolderCardNo": "6258101728953508",
                        "bankcode": "ICBC"
                    }
                    data = {
                        "deviceType": self.__app_script.mobile_type,
                        "mobileSysVer": self.__app_script.sys_ver,
                        'appChannel': 'CA_AIR',
                        "token": self.__app_script.token,
                        "dxRiskToken": "",
                        "userInfo4": "",
                        'userInfo3': init_utils.make_user_info3(),
                        "deviceModel": self.__app_script.device_model,
                        "userInfo2": init_utils.get_user_info2(self.__app_script.gt_token,
                                                               self.__app_script.main_app_version),
                        "userInfo1": "73800",
                        "lang": "zh_CN",
                        "req": "",
                        "mobileTypeExtra": "App",
                        "timestamp": ""
                    }
                    # 提交支付信息
                    pay_response = self.__app_script.get_service("ACPayByNetBank", "payByNetBank", req, data)
                    serial_number = pay_response['yeePayVerifyOrderNo']
                    req = {
                        "areaCode": "86",
                        "orderNo": serial_number,
                        "verifyCode": "970417",
                        "orderId": order_no,
                        "type": "2",
                        "userid": self.user_id,
                        "IOSSYSTEMDATE": init_utils.make_io_ssystem_date(),
                    }
                    data = {
                        "deviceType": self.__app_script.mobile_type,
                        "mobileSysVer": self.__app_script.sys_ver,
                        'appChannel': 'CA_AIR',
                        "token": self.__app_script.token,
                        "dxRiskToken": "",
                        "userInfo4": "",
                        'userInfo3': init_utils.make_user_info3(),
                        "deviceModel": self.__app_script.device_model,
                        "userInfo2": init_utils.get_user_info2(self.__app_script.gt_token,
                                                               self.__app_script.main_app_version),
                        "userInfo1": "73800",
                        "lang": "zh_CN",
                        "req": "",
                        "mobileTypeExtra": "App",
                        "timestamp": ""
                    }
                    response = self.__app_script.get_service("ACPayByNetBank", "yeepayverifycode", req, data)
                    if response.get('code') and response.get('code') == '00000000':
                        return response, serial_number, show_order_prices
                    else:
                        raise ServiceError(ServiceStateEnum.BOOKING_FAILURE_PAYMENT_STATE_CHECK_NOT_PASS, f"{response}")

    def order_detail(self, order_no):
        req = {
            "registerType": "TICKET",
            "orderStatus": "QB",
            "beginDate": "",
            "endDate": "",
            "ifThreeMouth": "0",
            "pageNo": "1",
            "pageSize": "10",
            "IOSSYSTEMDATE": init_utils.make_io_ssystem_date(),
        }
        data = {
            "deviceType": self.__app_script.mobile_type,
            "mobileSysVer": self.__app_script.sys_ver,
            'appChannel': 'CA_AIR',
            "token": self.__app_script.token,
            "dxRiskToken": "",
            "userInfo4": "",
            'userInfo3': init_utils.make_user_info3(),
            "deviceModel": self.__app_script.device_model,
            "userInfo2": init_utils.get_user_info2(self.__app_script.gt_token, self.__app_script.main_app_version),
            "userInfo1": "73800",
            "lang": "zh_CN",
            "req": "",
            "mobileTypeExtra": "App",
            "timestamp": ""
        }
        # response = self.__app_script.get_service("ACOrder", "newOrderList", req, data)

        req = {
            "orderNumber": order_no,
            "loginFlag": "1",
            "version": "3",
            "IOSSYSTEMDATE": init_utils.make_io_ssystem_date(),
        }
        data = {
            "deviceType": self.__app_script.mobile_type,
            "mobileSysVer": self.__app_script.sys_ver,
            'appChannel': 'CA_AIR',
            "token": self.__app_script.token,
            "dxRiskToken": "",
            "userInfo4": "",
            'userInfo3': init_utils.make_user_info3(),
            "deviceModel": self.__app_script.device_model,
            "userInfo2": init_utils.get_user_info2(self.__app_script.gt_token, self.__app_script.main_app_version),
            "userInfo1": "73800",
            "lang": "zh_CN",
            "req": "",
            "mobileTypeExtra": "App",
            "timestamp": ""
        }
        response = self.__app_script.get_service("ACOrder", "newOrderDetail", req, data)
        order_data = OrderDetailParser.parse_order_detail(response)
        return order_data

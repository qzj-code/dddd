"""
Module: _flight_util
Author: Ciwei
Date: 2024-10-07

Description: 
    This module provides functionalities for ...
"""
import copy
import json
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from itertools import product

from common.enums import CabinLevelEnum, SegmentTypeEnum, PassengerTypeEnum
from common.errors import ServiceStateEnum, ServiceError
from common.global_variable import GlobalVariable
from common.models.interior_service import JourneyInfoModel, PriceInfoModel, BundleInfoModel, SegmentInfoModel
from common.models.task import FareInfoModel, PriceInfoModel as TaskPriceInfoModel, BaggageInfoModel
from common.utils.__log_util import LogUtil
from common.utils._date_util import DateUtil
from common.utils._redis_utils import RedisUtils

_Log = LogUtil("FlightUtil")


class FlightUtil:
    @classmethod
    def filtration_cabin_level(cls,
                               journey_info_list: List[JourneyInfoModel],
                               select_cabin_levels: List[CabinLevelEnum]) -> List[JourneyInfoModel]:
        """
            过滤获取包含在选项中的舱级
        Args:
            journey_info_list: 行程列表
            select_cabin_levels: 目标舱级

        Returns:

        """
        result_journey_info_list = []
        for journey_info in journey_info_list:

            bundles = [x for x in journey_info.bundle_list if x.cabin_level in select_cabin_levels]
            if bundles:  # 如果筛选后的 bundles 非空
                journey_info.bundle_list = bundles
                result_journey_info_list.append(journey_info)

        return result_journey_info_list

    @classmethod
    def filtration_max_connection(cls,
                                  journey_info_list: List[JourneyInfoModel],
                                  max_connection: int) -> List[JourneyInfoModel]:
        """
            过滤最大中转航班
        Args:
            journey_info_list:
            max_connection:

        Returns:

        """

        result_journey_info_list = []
        for journey_info in journey_info_list:
            # 定义要检查的航程类型
            trip_types = [SegmentTypeEnum.TRIP, SegmentTypeEnum.RETURN_TRIP]

            # 循环处理每种航程类型
            add_data_bool = True
            for trip_type in trip_types:
                segment_type_count = sum([1 for x in journey_info.segment_list if x.segment_type == trip_type])
                if segment_type_count > (max_connection + 1):
                    add_data_bool = False
                    break

            if add_data_bool:
                result_journey_info_list.append(journey_info)

        return result_journey_info_list

    @classmethod
    def filtration_carrier(cls,
                           journey_info_list: List[JourneyInfoModel],
                           select_carriers: List[str]) -> List[JourneyInfoModel]:
        """
            过滤获取包含在选项列表中的航司
        Args:
            journey_info_list:
            select_carriers:

        Returns:

        """
        if not select_carriers:
            return journey_info_list

        result_journey_info_list = []
        for journey_info in journey_info_list:
            t = next((x for x in journey_info.segment_list if x.carrier in select_carriers), None)
            if t:
                result_journey_info_list.append(journey_info)

        return result_journey_info_list

    @classmethod
    def filtration_flights(cls, journey_info_list: List[JourneyInfoModel], flights: str):

        result_journey_info_list = []
        for journey_info in journey_info_list:
            flights_text = "^".join([x.flight_number for x in journey_info.segment_list])
            if flights_text == flights:
                result_journey_info_list.append(journey_info)

        return result_journey_info_list

    @classmethod
    def get_flight_journey_segment(cls, segments: List[SegmentInfoModel]):
        """
            获取行程维度航班号
        Args:
            segments:

        Returns:

        """
        result_flight_journey_segment = []
        for index in range(2):
            segment_infos = [x for x in segments if x.segment_type.value == index + 1]
            if not segment_infos:
                continue

            result_flight_journey_segment.append([x for x in segment_infos])

        return result_flight_journey_segment

    @classmethod
    def journey_infos_to_fare_data(cls,
                                   journey_info_list: List[JourneyInfoModel],
                                   data_source: str,
                                   connect_office: str,
                                   office: str,
                                   passenger_count: int,
                                   private_code: Optional[str] = '') -> List[FareInfoModel]:

        result_fare_data_list = []

        for journey_info in journey_info_list:
            t = FareInfoModel.model_validate({
                'fareKey': journey_info.key,
                'currency': '',
                'dataSource': data_source,
                'office': office,
                'connectOffice': connect_office,
                'priceType': 'Published',
                'privateCode': "",
                'productTag': '',
                'ticketCarrier': '',
                'priceTag': [],
                'changePnr': False,
                'refundInfo': '',
                'changeInfo': '',
                'priceList': [],
                'segmentList': [x.to_api_segment_model() for x in journey_info.segment_list],
                'taxDetail': [],
                'ext': {}
            })
            for bundle_info in journey_info.bundle_list:
                b = copy.deepcopy(t)
                for index, segment_info in enumerate(b.segment_list):
                    if index == 0:
                        b.ticket_carrier = segment_info.carrier
                    segment_info.segment_index = index + 1
                    segment_info.baggage_list = [copy.deepcopy(x) for x in bundle_info.baggage_list if
                                                 x.flight_number.find(f'{segment_info.flight_number}') != -1]

                segment_info_list = copy.deepcopy(b.segment_list)
                if not all([cls.__segment_info_set(segment_info_list, x[0], x[1])
                            for x in [(bundle_info.cabin, 1), (bundle_info.fare_basis, 2)]]):
                    break

                for segment_index, value in enumerate(segment_info_list):
                    value.cabin_level = bundle_info.cabin_level

                    if bundle_info.available_count == -1:
                        value.seat_num = passenger_count
                    else:
                        value.seat_num = bundle_info.available_count
                b.private_code = bundle_info.private_code
                b.segment_list = segment_info_list
                b.product_tag = bundle_info.product_tag
                b.currency = bundle_info.price_info[0].currency
                b.price_tag = bundle_info.price_tag
                b.price_list = [TaskPriceInfoModel.model_validate({
                    'passengerType': x.passenger_type,
                    'fare': x.fare,
                    'tax': x.tax,
                    "integral": x.integral,
                    'ext': x.ext
                }) for x in bundle_info.price_info]
                b.ext = bundle_info.ext

                result_fare_data_list.append(b)
        return result_fare_data_list

    @staticmethod
    def bundle_filter(response: list[FareInfoModel]):
        pass
        reserve_bundle_name = GlobalVariable.RESERVE_BUNDLE_NAME
        if reserve_bundle_name == '1':  # 1 代表不过滤，方便本地测试
            return response
        reserve_list = reserve_bundle_name.upper().split('|')
        response_list = []
        for fare in response:
            if fare.product_tag.upper() not in reserve_list:
                continue
            response_list.append(fare)

        return response_list

    @classmethod
    def __segment_info_set(cls, segment_info_list, data: str, set_type: int) -> bool:

        segment_count = len(set([x.segment_type for x in segment_info_list]))

        # 拆解 fareBasis
        data_info_list = data.split('^')  # 一次拆解，按航段维度

        # 校验航段数量是否一致
        if len(data_info_list) != segment_count:
            _Log.warning('航段信息不一致，过滤！')
            return False

        # 遍历每个航段的数据
        for index, value in enumerate(data_info_list):
            data_index_info_list = value.split('|')  # 二次拆解，按航班维度

            # 获取出所有航班信息
            segment_flight_info_list = [x for x in segment_info_list if x.segment_type.value == index + 1]
            # 处理航班维度数据
            if len(data_index_info_list) == 1:
                for segment_flight_info in segment_flight_info_list:
                    if set_type == 1:
                        segment_flight_info.cabin = data_index_info_list[0]
                    else:
                        segment_flight_info.fare_basis = data_index_info_list[0]
            else:
                if len(data_index_info_list) != len(segment_flight_info_list):
                    _Log.warning('航段信息不一致，过滤！')
                    return False

                for segment_index, segment_flight_info in enumerate(segment_flight_info_list):
                    if set_type == 1:
                        segment_flight_info.cabin = data_index_info_list[segment_index]
                    else:
                        segment_flight_info.fare_basis = data_index_info_list[segment_index]

        return True

    @classmethod
    def flight_link(cls,
                    journey_info_list: List[List["JourneyInfoModel"]],
                    permit_interval: int) -> List["JourneyInfoModel"]:
        """
        连接多程航班信息（使用 itertools.product 实现）
        ------------------------------------------------
        Args:
            journey_info_list: [[去程列表], [回程列表]]
            permit_interval: 允许的最小衔接时间（分钟）
        Returns:
            List[JourneyInfoModel]: 拼接后的行程组合
        """

        if not journey_info_list:
            return []

        assert len(journey_info_list) == 2, "ErrorLength"

        result_journeys = []

        # 🔹 用 itertools.product 替代双循环（惰性生成组合）
        for trip_journey, return_journey in product(*journey_info_list):

            # 🔸 判断去回衔接时间（小于间隔则跳过）
            if DateUtil.get_time_difference_points(
                    trip_journey.arr_time, return_journey.dep_time
            ) < permit_interval:
                continue

            # 🔸 拼接行程信息
            merged_segments = trip_journey.segment_list + return_journey.segment_list
            merged_bundles = cls.bundle_link(return_journey, trip_journey)

            if not merged_bundles:
                continue

            # 🔸 构造新的行程模型
            merged_journey = JourneyInfoModel.model_validate({
                'depAirport': trip_journey.dep_airport,
                'arrAirport': return_journey.arr_airport,
                'depTime': trip_journey.dep_time,
                'arrTime': return_journey.arr_time,
                'key': None if not all([trip_journey.key, return_journey.key])
                else '^'.join([trip_journey.key, return_journey.key]),
                'segmentList': merged_segments,
                'bundleList': merged_bundles,
                'correlation_id': None if not all(
                    [trip_journey.correlation_id, return_journey.correlation_id])
                else '^'.join([trip_journey.correlation_id, return_journey.correlation_id])
            })

            result_journeys.append(merged_journey)

        return result_journeys

    @staticmethod
    def bundle_link(return_journey, trip_journey):
        """

        Args:
            return_journey:
            trip_journey:

        Returns:

        """
        result_bundles = []
        for bundle_info in trip_journey.bundle_list:
            return_bundle_info = next(
                (x for x in return_journey.bundle_list if x.product_tag == bundle_info.product_tag), None)
            if return_bundle_info is None:
                continue

            price_info = [
                PriceInfoModel.model_validate({
                    'passengerType': trip_price.passenger_type,
                    'fare': trip_price.fare + return_price.fare,
                    'tax': trip_price.tax + return_price.tax,
                    'currency': trip_price.currency,
                    'integral': trip_price.integral + return_price.integral,
                    'ext': (
                        {'serviceFee': trip_service_fee + return_service_fee}
                        if trip_service_fee or return_service_fee
                        else {}
                    )
                })
                for trip_price in bundle_info.price_info
                for return_price in [
                    next((x for x in return_bundle_info.price_info if x.passenger_type == trip_price.passenger_type),
                         None)]
                if return_price
                for trip_service_fee in [trip_price.ext.get('serviceFee', 0)]
                for return_service_fee in [return_price.ext.get('serviceFee', 0)]

            ]

            if len(price_info) != len(bundle_info.price_info):
                _Log.warning('{} != {} 价格数量不一致，过滤'.format(len(price_info), len(bundle_info.price_info)))
                continue

            # TODO 增加行李航班号后，此过滤无效
            # if bundle_info.baggage_list != return_bundle_info.baggage_list:
            #     _Log.warning('行李信息不一致，过滤'.format(len(price_info), len(bundle_info.price_info)))
            #     continue

            up_bundle_info = BundleInfoModel.model_validate({
                'priceInfo': price_info,
                'cabinLevel': bundle_info.cabin_level,
                'cabin': '^'.join([bundle_info.cabin, return_bundle_info.cabin]),
                'fareBasis': '^'.join([bundle_info.fare_basis, return_bundle_info.fare_basis]),
                'productTag': bundle_info.product_tag,
                'productCode': bundle_info.product_code,
                'privateCode': bundle_info.private_code if bundle_info.private_code else return_bundle_info.private_code,
                'availableCount': min(bundle_info.available_count, return_bundle_info.available_count),
                'baggageList': bundle_info.baggage_list + return_bundle_info.baggage_list,
                'seatList': bundle_info.seat_list + return_bundle_info.seat_list,
                'cateringList': bundle_info.catering_list + return_bundle_info.catering_list,
                'key': None if not all([bundle_info.key, return_bundle_info.key]) else "^".join(
                    [bundle_info.key, return_bundle_info.key]),
                'id': None if not all([bundle_info.id, return_bundle_info.id]) else '^'.join(
                    [bundle_info.id, return_bundle_info.id]),
            })

            result_bundles.append(up_bundle_info)

        return result_bundles

    @classmethod
    def check_flight(
            cls,
            flight_data: List[JourneyInfoModel],
            flight_fare: FareInfoModel,
            cabin_level: CabinLevelEnum,
            limit_cabin: str,
            flight_change_time_threshold: str = "0-0",
    ) -> JourneyInfoModel:
        """
        在 flight_data 中查找和 flight_fare 对应的航班；匹配成功后校验基础信息。
        """

        target_numbers = cls.extract_flight_numbers(flight_fare)
        last_error: Optional[ServiceError] = None

        for journey in flight_data:

            # 1) 航班号匹配
            if [seg.flight_number for seg in journey.segment_list] != target_numbers:
                continue

            # 2) 基础校验
            try:
                cls.check_flight_basics_data(
                    journey_info_data=journey,
                    flight_fare=flight_fare,
                    flight_change_time_threshold=flight_change_time_threshold,
                )
            except ServiceError as err:
                last_error = err
                _Log.error(f"航班 {target_numbers} 基础信息校验失败：{err}")
                continue

            # 3) 套餐/舱位筛选
            journey.bundle_list = cls._filter_bundles(
                journey.bundle_list,
                cabin_level=cabin_level,
                limit_cabin=limit_cabin,
                target_fare=flight_fare
            )

            return journey

        # 4) 无匹配航班情况
        if last_error:
            raise last_error

        raise ServiceError(ServiceStateEnum.NO_FLIGHT_DATA)

    @staticmethod
    def _filter_bundles(
            bundles: List[BundleInfoModel],
            cabin_level: CabinLevelEnum,
            limit_cabin: str,
            target_fare: FareInfoModel
    ):
        """
        根据 cabin_level / limit_cabin / product_tag 过滤 bundle 列表
        """

        # 1) 过滤 cabin_level
        filtered = [b for b in bundles if b.cabin_level == cabin_level]
        if not filtered:
            raise ServiceError(
                ServiceStateEnum.BOOKING_FLIGHT_INFO_WEB_AND_OTA_DISCREPANCY,
                "舱等",
                cabin_level,
                [b.cabin_level for b in bundles],
            )

        # 2) 限制舱位（limit_cabin == '1'）
        if limit_cabin == '1':
            target_cabin = target_fare.segment_list[0].cabin
            filtered_by_cabin = [b for b in filtered if b.cabin == target_cabin]

            if not filtered_by_cabin:
                raise ServiceError(
                    ServiceStateEnum.BOOKING_FLIGHT_INFO_WEB_AND_OTA_DISCREPANCY,
                    "舱位",
                    target_cabin,
                    [b.cabin for b in filtered],
                )

            filtered = filtered_by_cabin

        # 3) 非经济舱 → product_tag 必须一致
        if cabin_level != CabinLevelEnum.ECONOMY:
            target_tag = target_fare.product_tag
            filtered_by_tag = [b for b in filtered if b.product_tag == target_tag]

            if not filtered_by_tag:
                raise ServiceError(
                    ServiceStateEnum.BOOKING_FLIGHT_INFO_WEB_AND_OTA_DISCREPANCY,
                    "品牌名",
                    target_tag,
                    [b.product_tag for b in filtered],
                )

            filtered = filtered_by_tag

        return filtered

    @classmethod
    def extract_flight_numbers(cls, flight_data: FareInfoModel) -> List[str]:
        """
        从航班数据中提取所有航段的航班号。

        @param flight_data: 航班数据字典
        @return: 航班号列表
        """
        flight_numbers = [segment.flight_number for segment in flight_data.segment_list]
        return flight_numbers

    @classmethod
    def extract_journey_flight_number(cls, segment_list: List[SegmentInfoModel]) -> List[str]:
        """
            提取行程维度航班号
        Args:
            segment_list:

        Returns:

        """

        result_number_infos = []
        # 解析各行程所有航班号
        for index, value in enumerate([SegmentTypeEnum.TRIP, SegmentTypeEnum.RETURN_TRIP]):
            # 使用列表推导式直接过滤符合条件的航班号
            _flight_numbers = [segment.flight_number for segment in segment_list if
                               segment.segment_type == value]
            if not _flight_numbers:
                continue
            result_number_infos.append('$'.join(_flight_numbers))

        return result_number_infos

    @classmethod
    def check_flight_basics_data(cls,
                                 journey_info_data: JourneyInfoModel,
                                 flight_fare: FareInfoModel,
                                 flight_change_time_threshold: str):
        """
            验证航班信息
        Args:
            journey_info_data:
            flight_fare:
            flight_change_time_threshold:

        Returns:

        """

        # 验证航班出发地，目的地
        order_dep_and_arr = ','.join([f'{x.dep_airport}-{x.arr_airport}' for x in flight_fare.segment_list])
        data_source_dep_and_arr = ','.join([f'{x.dep_airport}-{x.arr_airport}' for x in journey_info_data.segment_list])

        if order_dep_and_arr != data_source_dep_and_arr:
            raise ServiceError(ServiceStateEnum.BOOKING_FLIGHT_INFO_WEB_AND_OTA_DISCREPANCY,
                               '行程', order_dep_and_arr, data_source_dep_and_arr)

        for index, value in enumerate(journey_info_data.segment_list):
            # dep_time可能带有时区信息，需要去掉时区信息，才能比较
            dep_time_seg = value.dep_time
            if dep_time_seg.tzinfo:
                dep_time_seg = dep_time_seg.replace(tzinfo=None)
            time_difference = abs((dep_time_seg - flight_fare.segment_list[index].dep_time).total_seconds()) / 60
            if time_difference < int(flight_change_time_threshold.split('-')[0]) or time_difference > int(
                    flight_change_time_threshold.split('-')[1]):
                raise ServiceError(ServiceStateEnum.BOOKING_FLIGHT_INFO_WEB_AND_OTA_DISCREPANCY,
                                   '行程时间', flight_fare.segment_list[index].dep_time, dep_time_seg)

    @classmethod
    def matching_bundle_data(cls, fare_data: FareInfoModel, journey_info_data: JourneyInfoModel) -> JourneyInfoModel:
        """
        根据航段列表拼接 fare_basis，并在 data 中的 bundle_list 内部保留匹配的票价信息。

        参数：
            fear_data：OTA采购信息 (FareInfoModel): 包含航段完整数据结构。
            journey_info_data：官网航段信息 (JourneyInfoModel)。

        返回：
            dict: 修改后的完整数据结构，只保留匹配票价的 bundle_list。
        """
        # 筛选 bundle_list 中匹配的票价组合
        filtered_bundles = [
            bundle for bundle in journey_info_data.bundle_list
            if bundle.product_tag == fare_data.product_tag
        ]
        journey_info_data.bundle_list = filtered_bundles

        if len(journey_info_data.bundle_list) != 1:
            raise ServiceError(ServiceStateEnum.INVALID_DATA, '费用信息异常')
        return journey_info_data

    @classmethod
    def check_flight_fare(cls,
                          fare_infos: List[PriceInfoModel],
                          order_fare_infos: List[PriceInfoModel],
                          source_baggage_fare_infos: List[BaggageInfoModel] = None,
                          order_baggage_fare_infos: List[BaggageInfoModel] = None,
                          price_thres_hold: Optional[int] = 1):
        """
            验证航班费用数据
        Args:
            fare_infos:
            order_fare_infos:
            source_baggage_fare_infos:
            order_baggage_fare_infos:
            price_thres_hold:

        Returns:

        """

        source_total = Decimal(0)
        ota_total = Decimal(0)
        # 渠道总票价
        source_ticket_price = sum([fare.fare + fare.tax for fare in fare_infos])
        ota_ticket_price = sum([fare.fare + fare.tax for fare in order_fare_infos])

        if len(source_baggage_fare_infos) != len(order_baggage_fare_infos):
            raise ServiceError(ServiceStateEnum.INVALID_DATA, 'baggageFare')

        source_total += source_ticket_price

        ota_total += ota_ticket_price
        ota_total += price_thres_hold
        if source_total > ota_total:
            raise ServiceError(ServiceStateEnum.BOOKING_FLIGHT_FARE_INFO_WEB_AND_OTA_DISCREPANCY)

    @classmethod
    def check_passenger_type(cls,
                             response: List[FareInfoModel],
                             adult_number: int,
                             child_number: int = 0,
                             infant_number: int = 0):
        """
        根据指定的乘客类型数量过滤价格列表，移除数量为 0 的乘客类型。

        Args:
            response (List[FareInfoModel]): 航班价格信息列表。
            adult_number (int): 成人数量。
            child_number (int): 儿童数量。
            infant_number (int): 婴儿数量。

        Returns:
            List[FareInfoModel]: 过滤后的航班价格信息列表。
        """
        # 根据传入数量为 0 的类型动态移除价格
        remove_types = []
        if adult_number == 0:
            remove_types.append(PassengerTypeEnum.ADT)
        if child_number == 0:
            remove_types.append(PassengerTypeEnum.CHD)
        if infant_number == 0:
            remove_types.append(PassengerTypeEnum.INF)

        # 过滤价格列表
        for fare_info in response:
            fare_info.price_list = [
                fare for fare in fare_info.price_list if fare.passenger_type not in remove_types
            ]

        return response

    @classmethod
    def flight_fare_cache(cls,
                          date: datetime,
                          dep_airport: str,
                          arr_airport: str,
                          flight_number: str,
                          bundle_list: List[BundleInfoModel],
                          redis_util: RedisUtils,
                          ex: int):
        """
            航班价格缓存
        Args:
            date: 航班日期
            dep_airport: 出发地
            arr_airport: 目的地
            flight_number: 航班号
            bundle_list: 套餐信息
            redis_util: redis链接信息
            ex: 缓存过期时间

        Returns:

        """

        key = f"{date.strftime('%Y%m%d')}-{flight_number}-{dep_airport}-{arr_airport}-{bundle_list[0].cabin}"
        for i in bundle_list:
            cache_data = redis_util.get(key + i.product_tag)
            if cache_data is None:
                redis_util.set(key + i.product_tag, i.model_dump_json(), ex)
            else:
                cache_json = json.loads(cache_data)
                if i.product_tag != cache_json['product_tag']:
                    continue

                cache_total = Decimal(cache_json['price_info'][0]['tax'] + cache_json['price_info'][0]['fare'])
                cache_total = cache_total.quantize(Decimal('0.00'))
                bundle_total = i.price_info[0].fare + i.price_info[0].tax
                print(i.product_tag, bundle_total, cache_total)
                if bundle_total < cache_total:
                    redis_util.set(key + i.product_tag, i.model_dump_json(), ex)
                    break

"""
Module: booking_util
Author: Ciwei
Date: 2024-10-26

Description: 
    This module provides functionalities for ...
"""
import copy
import decimal
import itertools
from typing import List, Union

from common.enums import BaggageTypeEnum, AncillariesTypeEnum
from common.errors import ServiceError, ServiceStateEnum
from common.models.interior_service import (
    BaggageInfoModel, PassengerInfoModel, BundleInfoModel,
    PriceInfoModel, SegmentInfoModel, SeatInfoModel, JourneyInfoModel
)
from common.models.task import (
    PassengerInfoModel as ApiPassengerInfoModel,
)
from common.models.task.order import RequestOrderInfoModel
from common.utils.flight_util import FlightUtil


class BookingUtil:

    @classmethod
    def check_fare(cls,
                   bundle: BundleInfoModel,
                   passenger_list: List[PassengerInfoModel],
                   order_data: RequestOrderInfoModel):
        # 采购价
        source_total_price = cls.compute_all_passenger_price(bundle.price_info, passenger_list)
        source_curreny = bundle.price_info[0].currency
        # 进单价格
        order_total_price = cls.compute_all_passenger_price(order_data.fare.price_list,
                                                            order_data.passenger_list)
        order_curreny = order_data.fare.currency

        # 采购积分
        source_total_points = cls.compute_all_passenger_points(bundle.price_info, passenger_list)
        # 进单积分
        order_total_points = cls.compute_all_passenger_points(order_data.fare.price_list,
                                                              order_data.passenger_list)
        if source_curreny != order_curreny:
            raise ServiceError(ServiceStateEnum.BOOKING_FAILURE_CURRENCY_MISMATCH_ERROR, order_curreny, source_curreny)
        if source_total_price > (order_total_price - decimal.Decimal(order_data.price_threshold)):
            raise ServiceError(ServiceStateEnum.BOOKING_FAILURE_PRICE_CHECK_NOT_PASS,
                               order_total_price, source_curreny,
                               source_total_price, order_curreny,
                               order_total_price - source_total_price, order_curreny)
        if source_total_points > order_total_points:
            raise ServiceError(ServiceStateEnum.BOOKING_FAILURE_PRICE_CHECK_NOT_PASS,
                               order_total_points, "积分",
                               source_total_points, "积分",
                               source_total_points - order_total_points, "积分")

    @classmethod
    def check_baggage_flight(cls, passenger_list: List[PassengerInfoModel], segments: List[SegmentInfoModel]):

        journey_flight_segments = [x for x in FlightUtil.get_flight_journey_segment(segments=segments)]

        for passenger_info in passenger_list:
            baggage_infos = passenger_info.get_purchasing_baggage()
            for baggage_info in baggage_infos:
                if baggage_info.flight_number in ['$'.join([v.flight_number for v in x]) for x in
                                                  journey_flight_segments]:
                    continue
                raise ServiceError(ServiceStateEnum.INVALID_DATA, 'baggageFlight')

    @classmethod
    def find_best_baggage_combination(cls, baggage_list: List[BaggageInfoModel], required_weight, max_combinations):
        """

        Args:
            baggage_list:
            required_weight:
            max_combinations:

        Returns:

        """
        # 存储最优组合结果
        best_combination = None
        min_total_amount = float('inf')

        # 遍历所有可能的组合，从1到max_combinations个行李的组合

        for i in range(max_combinations):
            for combination in itertools.combinations_with_replacement(baggage_list, i + 1):
                total_weight = sum(item.total_weight for item in combination)
                total_amount = sum(item.amount for item in combination)

                # 只考虑总重量 >= 需要的重量 且 总金额最小的组合
                if total_weight >= required_weight and total_amount < min_total_amount:
                    min_total_amount = total_amount
                    best_combination = combination

        # 如果找到了符合条件的组合，返回它们的重量
        if best_combination:
            return [item.total_weight for item in best_combination]
        else:
            return None  # 没有找到符合条件的组合

    @classmethod
    def baggage_compute_min_price(cls,
                                  bundles: List[BundleInfoModel],
                                  passengers: List[PassengerInfoModel],
                                  source_baggage_infos: List[List[BaggageInfoModel]],
                                  journey_segments: List[List[SegmentInfoModel]],
                                  max_combinations_route: dict):
        """

        Args:
            bundles:    费用列表
            passengers: 乘客列表
            source_baggage_infos: 数据源行李列表
            journey_segments: 行程列表
            max_combinations_route: 最大组合次数

        Returns:

        """

        all_passengers = {}
        for bundle_info in bundles:
            error_detected = False  # 每个套餐初始化正常
            # 循环行程
            b_passengers = copy.deepcopy(passengers)
            for index, journey_segment in enumerate(journey_segments):
                if error_detected:
                    break
                # 循环乘机人，用来确定是否双行程行李
                for passenger_info in b_passengers:

                    flight_number = '$'.join([x.flight_number for x in journey_segment])
                    use_baggage = []
                    # 计算除免费行李后，所需添加行李重量
                    buy_baggage_weight = passenger_info.get_purchasing_baggage_weight(flight_number=flight_number, )
                    free_baggage = next((x for x in bundle_info.baggage_list if
                                         x.baggage_type == BaggageTypeEnum.HAULING_BAGGAGE and x.total_weight != 0),
                                        None)

                    # 先添加免费行李
                    if free_baggage:
                        buy_baggage_weight -= free_baggage.total_weight
                    # TODO 转换接口模型无法判断行李类型
                    #     use_baggage.append(copy.deepcopy(free_baggage))

                    if buy_baggage_weight > 0:
                        # 计算最优行李组合
                        min_baggage_info = cls.find_best_baggage_combination(
                            source_baggage_infos[index],
                            required_weight=buy_baggage_weight,
                            max_combinations=max_combinations_route[bundle_info.product_tag]
                        )

                        if min_baggage_info is None:
                            error_detected = True  # 标记为异常
                            break
                        # 后添加收费行李
                        for baggage_weight in min_baggage_info:
                            baggage_info = next(
                                (x for x in source_baggage_infos[index] if x.total_weight == baggage_weight), None)

                            if baggage_info.flight_number != flight_number:
                                raise ServiceError(ServiceStateEnum.INVALID_DATA, 'baggageFlight')
                            # 获取已使用的行李数据中，是否有相同重量数据
                            # t = next((x for x in use_baggage if x.total_weight == baggage_weight and x.amount > 0),
                            #          None)
                            use_baggage.append(copy.deepcopy(baggage_info))

                    for baggage in use_baggage:
                        passenger_info.add_ancillaries_data(baggage,
                                                            ancillaries_type=AncillariesTypeEnum.LUGGAGE,
                                                            purchasing=False)
            if not error_detected:
                all_passengers[bundle_info.product_tag] = b_passengers

        # 计算所有套餐价格
        min_computes = {}
        for key, value in all_passengers.items():
            bundle = next((x for x in bundles if x.product_tag == key))
            min_computes[key] = [cls.compute_all_passenger_price(bundle.price_info, value), bundle]

        if not min_computes:
            raise ServiceError(ServiceStateEnum.SERVICE_ERROR, '无法匹配行李重量')
        # 计算最小价格
        min_price = min(min_computes.items(), key=lambda item: item[1][0])

        use_bundle = min_price[1][1]
        result_passenger = next(
            (value for key, value in all_passengers.items() if key == min_price[0]),
            None
        )
        return result_passenger, use_bundle

    @classmethod
    def compute_all_passenger_price(cls,
                                    price_infos: List[PriceInfoModel],
                                    passengers: Union[List[PassengerInfoModel], List[ApiPassengerInfoModel]]):

        total_amount = decimal.Decimal(0)

        for passenger in passengers:

            price_info = next((x for x in price_infos if x.passenger_type == passenger.passenger_type), None)
            if price_info is None:
                raise ServiceError(ServiceStateEnum.NECESSARY_DATA_MISSING, 'priceInfo')

            baggage_price = passenger.get_total_price()
            total_amount += baggage_price + price_info.fare + price_info.tax

        return total_amount

    @classmethod
    def compute_all_passenger_points(cls,
                                     price_infos: List[PriceInfoModel],
                                     passengers: Union[List[PassengerInfoModel], List[ApiPassengerInfoModel]]):
        total_points = decimal.Decimal(0)

        for passenger in passengers:

            price_info = next((x for x in price_infos if x.passenger_type == passenger.passenger_type), None)
            if price_info is None:
                raise ServiceError(ServiceStateEnum.NECESSARY_DATA_MISSING, 'priceInfo')

            total_points += price_info.integral

        return total_points

    @classmethod
    def compute_all_passenger_seat(cls, passengers: List[PassengerInfoModel], seats: List[SeatInfoModel]):

        seat_check_list = cls.allocate_seats([f'{x.row}{x.column}' for x in seats], len(passengers))

        for i in passengers:
            seat_data = next((x for x in seats if f'{x.row}{x.column}' == seat_check_list[0]), None)
            if seat_data is None:
                raise ServiceError(ServiceStateEnum.NECESSARY_DATA_MISSING, 'seatData')
            del seat_check_list[0]

            i.add_ancillaries_data(SeatInfoModel.model_validate({
                'column': seat_data.column,
                'row': seat_data.row,
                'flightNumber': seat_data.flight_number,
                'sellKey': seat_data.sell_key
            }), AncillariesTypeEnum.SEAT, purchasing=False)

    @classmethod
    def allocate_seats(cls, seat_list, num_people):
        # 按排号和列号（A、B、C 等）排序
        sorted_seats = sorted(seat_list, key=lambda x: (int(x[:-1]), x[-1]))

        # 建立座位图，每排一个列表，按列号排序
        seat_map = {}
        columns = set()
        for seat in sorted_seats:
            row = int(seat[:-1])
            col = seat[-1]
            columns.add(col)  # 收集所有列
            if row not in seat_map:
                seat_map[row] = []
            seat_map[row].append(seat)

        # 将列按字母顺序排序
        columns = sorted(columns, key=lambda x: ord(x))

        # 1. 优先查找同排完全连续的座位
        def find_consecutive_seats(seats, required):
            for i in range(len(seats) - required + 1):
                group = seats[i:i + required]
                # 检查是否完全连续
                if all(ord(group[j][-1]) == ord(group[0][-1]) + j for j in range(required)):
                    return group
            return None

        # 优先查找同排完全连续的座位
        for row in sorted(seat_map.keys()):
            row_seats = seat_map[row]
            consecutive_seats = find_consecutive_seats(row_seats, num_people)
            if consecutive_seats:
                return consecutive_seats

        # 2. 如果找不到完全连续的座位，跨排选择缺失最少的组合
        min_total_gaps = float('inf')
        best_seats = []

        # 尝试从每一排开始跨排组合
        for start_row in sorted(seat_map.keys()):
            current_seats = []
            total_gaps = 0
            previous_col = None

            # 从起始排往下逐排累积座位，直到满足人数要求
            for row in range(start_row, max(seat_map.keys()) + 1):
                if row not in seat_map:  # 检查当前排是否存在
                    continue

                row_seats = seat_map[row]
                seats_needed = num_people - len(current_seats)

                # 累积座位
                for seat in row_seats:
                    if seats_needed == 0:
                        break
                    current_col = seat[-1]
                    if previous_col is not None:
                        gap = ord(current_col) - ord(previous_col) - 1
                        total_gaps += max(0, gap)
                    current_seats.append(seat)
                    seats_needed -= 1
                    previous_col = current_col

                # 检查是否已找到足够的座位
                if len(current_seats) >= num_people:
                    break

            # 更新缺失最少的组合
            if len(current_seats) == num_people and total_gaps < min_total_gaps:
                min_total_gaps = total_gaps
                best_seats = current_seats
        # 返回找到的最佳组合
        return best_seats if best_seats else []

    @classmethod
    def filter_bundles(cls, selected_bundle, flight_info: JourneyInfoModel, bundle_priority: List[str]):
        """
        适用于不得降套餐时，将低套餐删除
        Args:
            bundle_priority: 套餐等级，从大到小排序
            selected_bundle:进单选定的套餐名
            flight_info(JourneyInfoModel):航班详情

        Returns:

        """

        # 获取所选套餐的优先级索引
        if selected_bundle in bundle_priority:
            selected_index = bundle_priority.index(selected_bundle)

            # 保留所选套餐及其更高级的套餐，删除其以下的套餐
            flight_info.bundle_list = [
                bundle for bundle in flight_info.bundle_list
                if bundle.product_tag in bundle_priority[:selected_index + 1]
            ]

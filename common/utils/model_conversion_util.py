"""
Module: model_conversion_util
Author: Ciwei
Date: 2024-10-26

Description: 
    This module provides functionalities for ...
"""
from typing import Union, List

from common.enums import AncillariesTypeEnum, BaggageTypeEnum, SegmentTypeEnum
from common.models.interior_service import (
    PassengerInfoModel as InteriorPassengerInfoModel, BaggageInfoModel as InteriorBaggageInfoModel,
    PriceInfoModel as InteriorPriceInfoModel,
)
from common.models.task import (
    PassengerInfoModel, BaggageInfoModel, PriceInfoModel,
    AncillaryBaggageInfoModel, SegmentInfoModel, SeatInfoModel
)


class ModelConversionUtil:
    @staticmethod
    def api_passenger_to_interior_passenger_model(passenger_infos: List[PassengerInfoModel],
                                                  segment_infos: List[SegmentInfoModel],
                                                  purchasing: bool = False) -> List[InteriorPassengerInfoModel]:
        """
            将订单信息转到乘机人中
        Args:
            passenger_infos:
            segment_infos:
            purchasing:

        Returns:

        """
        free_baggage = []

        for t in [SegmentTypeEnum.TRIP, SegmentTypeEnum.RETURN_TRIP]:
            segments = [x for x in segment_infos if x.segment_type == t]
            if not segments:
                continue

            flight_number = '$'.join([x.flight_number for x in segments])
            for i in segments[0].baggage_list:
                baggage_info = next(
                    (x for x in free_baggage if x.total_weight == i.total_weight and x.flight_number == flight_number and x.passenger_type == i.passenger_type),
                    None)
                if baggage_info:
                    continue

                if i.baggage_type != BaggageTypeEnum.HAULING_BAGGAGE:
                    continue

                if i.total_weight <= 0:
                    continue

                free_baggage.append(AncillaryBaggageInfoModel.model_validate({
                    'passengerType': i.passenger_type,
                    'baggageType': i.baggage_type,
                    'pieces': i.pieces,
                    'totalWeight': i.total_weight,
                    'flightNumber': flight_number,
                }))

        result_passenger_infos = []

        for passenger_info in passenger_infos:

            passenger_data = InteriorPassengerInfoModel.model_validate({
                "passengerType": passenger_info.passenger_type,
                "name": passenger_info.name,
                "gender": passenger_info.gender,
                "birthday": passenger_info.birthday,
                "cardType": passenger_info.card_type,
                "cardNumber": passenger_info.card_number,
                "cardExpired": passenger_info.card_expired,
                "issuePlace": passenger_info.issue_place,
                "mobCountryCode": passenger_info.mob_country_code,
                "mobile": passenger_info.mobile,
                "nationality": passenger_info.nationality,
                "email": passenger_info.email,
                "ticketInfoList": passenger_info.ticket_info_list,
            })

            baggage_infos = []
            for i in free_baggage:
                if i.passenger_type != passenger_info.passenger_type:
                    continue
                if i.baggage_type != BaggageTypeEnum.HAULING_BAGGAGE:
                    continue

                baggage_infos.append(ModelConversionUtil.api_baggage_to_interior_baggage_model(i))

            if passenger_info.baggage_list:
                for i in passenger_info.baggage_list:
                    baggage_infos.append(ModelConversionUtil.api_baggage_to_interior_baggage_model(i))

            for i in baggage_infos:
                passenger_data.add_ancillaries_data(data=i, ancillaries_type=AncillariesTypeEnum.LUGGAGE,
                                                    purchasing=purchasing)

            result_passenger_infos.append(passenger_data)

        return result_passenger_infos

    @classmethod
    def api_ancillaries_baggage_to_interior_baggage_model(cls,
                                                          baggage_info: BaggageInfoModel) -> InteriorBaggageInfoModel:
        """

        Args:
            baggage_info:

        Returns:

        """

        return InteriorBaggageInfoModel.model_validate({
            'passengerType': baggage_info.passenger_type,
            'baggageType': baggage_info.baggage_type,
            'pieces': baggage_info.pieces,
            'totalWeight': baggage_info.total_weight,
            'weightUnit': baggage_info.weight_unit,
            'flightNumber': baggage_info.flight_number,
            'amount': baggage_info.amount
        })

    @classmethod
    def api_baggage_to_interior_baggage_model(cls, baggage_info: Union[
        BaggageInfoModel, AncillaryBaggageInfoModel]) -> InteriorBaggageInfoModel:
        """

        Args:
            baggage_infos:

        Returns:

        """
        return InteriorBaggageInfoModel.model_validate({
            'passengerType': baggage_info.passenger_type,
            'baggageType': baggage_info.baggage_type,
            'pieces': baggage_info.pieces,
            'totalWeight': baggage_info.total_weight,
            'weightUnit': baggage_info.weight_unit,
            'flightNumber': baggage_info.flight_number if isinstance(baggage_info, AncillaryBaggageInfoModel) else None,
            'amount': baggage_info.amount if isinstance(baggage_info, AncillaryBaggageInfoModel) else 0
        })

    @classmethod
    def interior_passenger_to_api_passenger_model(cls, passenger_infos: List[InteriorPassengerInfoModel]):

        result_passenger_infos = []
        for passenger_info in passenger_infos:
            passenger_data = PassengerInfoModel.model_validate({
                "passengerType": passenger_info.passenger_type,
                "name": passenger_info.name,
                "gender": passenger_info.gender,
                "birthday": passenger_info.birthday,
                "cardType": passenger_info.card_type,
                "cardNumber": passenger_info.card_number,
                "cardExpired": passenger_info.card_expired,
                "issuePlace": passenger_info.issue_place,
                "mobCountryCode": passenger_info.mob_country_code,
                "mobile": passenger_info.mobile,
                "nationality": passenger_info.nationality,
                "email": passenger_info.email,
                "ticketInfoList": passenger_info.ticket_info_list,
                "baggageList": cls.interior_baggage_to_api_baggage_model(passenger_info.get_baggage_infos(), 0),
                'seatInfoList': [SeatInfoModel.model_validate({
                    'seatCode': x.column,
                    'seatRow': str(x.row),
                    'flightNumber': x.flight_number,
                }) for x in passenger_info.get_ancillaries(AncillariesTypeEnum.SEAT)],
            })

            result_passenger_infos.append(passenger_data)

        return result_passenger_infos

    @staticmethod
    def interior_baggage_to_api_ancillaries_baggage_model(cls, baggage_infos: List[InteriorBaggageInfoModel]):
        """

        Args:
            cls:
            baggage_infos:

        Returns:

        """

        return BaggageInfoModel.model_validate({})

    @staticmethod
    def interior_baggage_to_api_baggage_model(baggage_infos: List[InteriorBaggageInfoModel],
                                              filtration_type: int = 0, flight_number: str = None) -> Union[
        List[BaggageInfoModel], List[AncillaryBaggageInfoModel]]:
        """
            内部行李模型转接口行李模型
        Args:
            baggage_infos:
            filtration_type: 0收费行李，1免费行李

        Returns:

        """

        result_baggage_infos = []
        for baggage in baggage_infos:
            # TODO 转换接口模型无法判断行李类型
            # if filtration_type == 0 and baggage.amount <= 0:
            #     continue
            #
            # if filtration_type == 1 and baggage.amount > 0:
            #     continue
            if flight_number is not None:
                if flight_number not in baggage.flight_number:
                    continue
            if filtration_type == 0:
                result_baggage_infos.append(AncillaryBaggageInfoModel.model_validate({
                    # 'passengerType': baggage.passenger_type,
                    'baggageType': baggage.baggage_type,
                    'pieces': baggage.pieces,
                    'totalWeight': baggage.total_weight,
                    'weightUnit': baggage.weight_unit,
                    'flightNumber': baggage.flight_number,
                    'amount': baggage.amount
                }))
            elif filtration_type == 1:
                result_baggage_infos.append(BaggageInfoModel.model_validate({
                    'passengerType': baggage.passenger_type,
                    'baggageType': baggage.baggage_type,
                    'pieces': baggage.pieces,
                    'totalWeight': baggage.total_weight,
                    'weightUnit': baggage.weight_unit,
                }))

        return result_baggage_infos

    @staticmethod
    def interior_price_info_to_api_price_ino_model(price_info_model: InteriorPriceInfoModel) -> PriceInfoModel:

        return PriceInfoModel.model_validate({
            'passengerType': price_info_model.passenger_type,
            'fare': price_info_model.fare,
            'tax': price_info_model.tax,
            'ext': price_info_model.ext
        })

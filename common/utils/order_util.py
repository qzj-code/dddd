"""
Module: order_util
Author: Ciwei
Date: 2024-10-20

Description: 
    This module provides functionalities for ...
"""
from common.errors import ServiceError, ServiceStateEnum
from common.models.interior_service import OrderInfoModel
from common.models.task.order import ResponseOrderInfoModel
from common.utils.model_conversion_util import ModelConversionUtil


class OrderUtil:

    @classmethod
    def order_info_to_request_order_info(cls, order_info: OrderInfoModel, session_id: str):
        """

        Args:
            order_info:
            session_id:

        Returns:

        """

        if order_info.segments:
            if order_info.bundle_info is None:
                raise ServiceError(ServiceStateEnum.NECESSARY_DATA_MISSING, 'bundleInfo')
        cabin_parts = order_info.bundle_info.cabin.split("|") if order_info.bundle_info else []
        return ResponseOrderInfoModel.model_validate({
            'sessionId': session_id,
            'sign': '',
            'orderNo': order_info.order_no,
            'orderState': order_info.order_state,
            'currency': order_info.currency,
            'issued': order_info.issued,
            'createTime': order_info.create_time,
            'lastTicketTime': order_info.last_ticket_time,
            'ticketTime': order_info.ticket_time,
            'productTag': order_info.bundle_info.product_tag if order_info.bundle_info else '',
            'pnr': order_info.pnr,
            'airlinePnr': order_info.airline_pnr,
            'ticketCarrier': order_info.ticket_carrier,
            'officeInfo': order_info.office_info,
            'passengerList': ModelConversionUtil.interior_passenger_to_api_passenger_model(order_info.passengers),
            'priceList': [ModelConversionUtil.interior_price_info_to_api_price_ino_model(x) for x in (
                order_info.bundle_info.price_info if order_info.bundle_info and order_info.bundle_info.price_info else [])],
            'segmentList': [
                value.to_api_segment_model(
                    cabin_level=order_info.bundle_info.cabin_level,
                    cabin=(cabin_parts[index] if index < len(cabin_parts) else order_info.bundle_info.cabin),
                    baggage_info='',
                    baggage_list=ModelConversionUtil.interior_baggage_to_api_baggage_model(
                        order_info.bundle_info.baggage_list, 1, value.flight_number),
                    segment_index=index + 1
                )
                for index, value in enumerate(order_info.segments)
            ] if order_info.segments else [],
            'payInfo': order_info.payment_info,
            'ext': order_info.ext,
            'totalPrice': order_info.total_price,
        })

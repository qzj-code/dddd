from common.enums import SegmentTypeEnum, CabinLevelEnum, OrderStateEnum, PassengerTypeEnum
from common.errors import ServiceError, ServiceStateEnum
from common.models.interior_service import SegmentInfoModel, OrderInfoModel, BundleInfoModel, PassengerInfoModel, \
    JourneyInfoModel, PriceInfoModel
from common.models.task import TicketInfoModel
from common.utils import DateUtil
from common.utils.flight_util import FlightUtil


class OrderDetailParser:

    @classmethod
    def parse_order_detail(cls, order_data) -> OrderInfoModel:
        journeys = []
        if not order_data['resp']['resbean'].get('ticketList'):
            raise ServiceError(ServiceStateEnum.TICKET_NUMBER_INFO_MISTAKE)
        segment_list = cls.parse_segments(order_data['resp']['resbean']['ticketList'][0])
        bundles = cls.parse_bundlel(order_data['resp']['resbean'])
        passenger_infos = cls.parse_passenger_info(order_data['resp']['resbean'])
        dep_airport = segment_list[0].dep_airport
        arr_airport = segment_list[-1].arr_airport
        dep_date = segment_list[0].dep_time
        arr_date = segment_list[-1].arr_time
        flight_number = '$'.join([i.flight_number for i in segment_list])
        journeys.append([
            JourneyInfoModel.model_validate({
                'depAirport': dep_airport,
                'arrAirport': arr_airport,
                'depTime': dep_date,
                'arrTime': arr_date,
                'segmentList': segment_list,
                'bundleList': bundles,
            })
        ])
        if len(journeys) > 1:
            journey = FlightUtil.flight_link(journey_info_list=journeys, permit_interval=0)
        else:
            if len(journeys) == 0:
                journey = None
            else:
                journey = journeys[0]
        if order_data['resp']['resbean']['orderStatus'] == 3:
            order_state = OrderStateEnum.OPEN_FOR_USE
        else:
            order_state = OrderStateEnum.UNKNOWN
        if not passenger_infos[0].ticket_info_list:
            issued = False
        else:
            issued = True
        pnr = order_data['resp']['resbean']['ticketList'][0]['travelerlist'][0]['pnr']
        amount = order_data['resp']['resbean']['showOrderPrices']
        ticket_carrier = order_data['resp']['resbean']['ticketList'][0]['flightCom']
        return OrderInfoModel.model_validate({
            'orderState': order_state,
            'currency': "CNY",
            'issued': issued,
            'pnr': pnr,
            'airlinePnr': pnr,
            'passengers': passenger_infos,
            'ticketCarrier': ticket_carrier,
            'segments': journey[0].segment_list if journey and journey[0].segment_list else None,
            'bundleInfo': journey[0].bundle_list[0] if journey and journey[0].bundle_list else None,
            'totalPrice': amount
        })

    @classmethod
    def parse_segments(cls, ticket_info):
        segment_type = SegmentTypeEnum.TRIP
        segment_list = []
        dep_airport = ticket_info['departureAirport']
        arr_airport = ticket_info['arrivalAirport']
        dep_time = DateUtil.string_to_date_auto(ticket_info['departureDate'] + ' ' + ticket_info['departureTime'])
        arr_time = DateUtil.string_to_date_auto(ticket_info['arrivalDate'] + ' ' + ticket_info['arrivalTime'])
        flight_number = ticket_info['flightCom'] + ticket_info['flightNumber']
        flight_time = DateUtil.get_time_difference_points(dep_time, arr_time)
        segment_list.append(SegmentInfoModel.model_validate({
            'depAirport': dep_airport,
            'arrAirport': arr_airport,
            'depTime': dep_time,
            'codeShare': False,
            'arrTime': arr_time,
            'flightNumber': flight_number,
            'carrier': ticket_info['flightCom'],
            'flightTime': flight_time,
            'segmentType': segment_type,
        }))
        return segment_list

    @classmethod
    def parse_bundlel(cls, resbean):
        price_info = []
        adt_fare = 0
        adt_tax = 0
        adt_fee = 0
        chd_fare = 0
        chd_tax = 0
        chd_fee = 0
        for i in resbean['feeList']:
            if i['passengerType'] == 'ADT':
                if i['spendType'] == 'WASQ':
                    adt_fare = i['spendFee']
                elif i['spendType'] == 'CN':
                    adt_tax = i['spendFee']
                elif i['spendType'] == 'YQ':
                    adt_fee = i['spendFee']
            else:
                if i['spendType'] == 'WASQ':
                    chd_fare = i['spendFee']
                elif i['spendType'] == 'CN':
                    chd_tax = i['spendFee']
                elif i['spendType'] == 'YQ':
                    chd_fee = i['spendFee']
        if adt_fare > 0:
            price_info.append(PriceInfoModel.model_validate({
                "currency": "CNY",
                "passengerType": PassengerTypeEnum.ADT,
                "fare": adt_fare,
                "tax": adt_tax,
                "ext": {
                    "oiFee": adt_fee
                }
            }))
        if chd_fare > 0:
            price_info.append(PriceInfoModel.model_validate({
                "currency": "CNY",
                "passengerType": PassengerTypeEnum.CHD,
                "fare": chd_fare,
                "tax": chd_tax,
                "ext": {
                    "oiFee": chd_fee
                }
            }))
        cabin = resbean['ticketList'][0]['seatlevel']
        return [
            BundleInfoModel.model_validate({
                'cabinLevel': CabinLevelEnum.ECONOMY,  # 舱位等级
                'cabin': cabin,  # 舱位
                'availableCount': 0,
                "priceInfo": price_info
            })
        ]

    @classmethod
    def parse_passenger_info(cls, passenger_detail):
        passenger_list = []
        for i in passenger_detail['ticketList']:
            ticket_info_list = []
            for j in i['travelerlist']:
                pnr = j['pnr']
                ticket_no = j['ticketNumber']
                ticket_info_list.append(TicketInfoModel.model_validate({
                    'pnr': pnr,
                    'airlinePnr': pnr,
                    'ticketNo': ticket_no,
                }))
            last_name = i['travelerlist'][0]['lastName']
            first_name = i['travelerlist'][0]['firstName']
            passenger_type = i['travelerlist'][0]['travelType']
            passenger_list.append(PassengerInfoModel.model_validate({
                'passengerType': passenger_type,
                'name': last_name + '/' + first_name,
                'ticketInfoList': ticket_info_list,
            }))
        return passenger_list

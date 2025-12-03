from common.enums import PassengerTypeEnum, BaggageTypeEnum, \
    SegmentTypeEnum, CabinLevelEnum
from common.models.interior_service import SegmentInfoModel, BundleInfoModel, JourneyInfoModel, PriceInfoModel, \
    BaggageInfoModel
from common.utils.flight_util import FlightUtil, DateUtil


class FlightParser:
    @staticmethod
    def parse_flight_data(flight_data: dict, child_count: int):
        journeys = []
        t = []
        for flight in flight_data['resp']['goto']['flightInfomationList']:
            segment_type = SegmentTypeEnum.TRIP
            segments = FlightParser.parse_segment(flight['flightSegmentList'], segment_type)
            flight_number = '$'.join([i.flight_number for i in segments])
            bundles = FlightParser.parse_bundles(fare_list=flight, child_count=child_count, flight_number=flight_number,
                                                 price_tag_list=flight['acivityNameListLeft'])
            key = flight['flightID']
            t.append(JourneyInfoModel.model_validate({
                'depAirport': segments[0].dep_airport,
                'arrAirport': segments[-1].arr_airport,
                'depTime': segments[0].dep_time,
                'arrTime': segments[-1].arr_time,
                'segmentList': segments,
                'bundleList': bundles,
                'key': key,
            }))
        journeys.append(t)
        # 单程航班直接响应
        if len(journeys) == 1:
            return journeys[0]
            # 往返多程航班进行拼接
        return FlightUtil.flight_link(journey_info_list=journeys, permit_interval=60 * 12)

    @classmethod
    def parse_segment(cls, segments, segment_type):
        segment_list = []
        for i in segments:
            dep_airport = i['flightDep']
            arr_airport = i['flightArr']
            dep_time = DateUtil.string_to_date_auto(
                i['flightDepdatePlan'] + ' ' + i['flightDeptimePlan'].split('+')[0].replace('.000', ''))
            arr_time = DateUtil.string_to_date_auto(
                i['flightArrdatePlan'] + ' ' + i['flightArrtimePlan'].split('+')[0].replace('.000', ''))
            carrier = i['airlineIntf']
            flight_number = i['flightNo']
            operating_carrier = carrier
            code_share = True if carrier != operating_carrier else False
            operating_flight_number = flight_number
            flight_time = DateUtil.get_time_difference_points(dep_time, arr_time)
            aircraft = i['flightModelIntf']
            dep_terminal = i['flightTerminal']
            arr_terminal = i['flightHTerminal']
            segment_list.append(SegmentInfoModel.model_validate({
                'depAirport': dep_airport,
                'arrAirport': arr_airport,
                'depTime': dep_time,
                'arrTime': arr_time,
                'flightNumber': flight_number,
                'codeShare': code_share,
                'carrier': carrier,
                'operatingCarrier': operating_carrier,
                'operatingFlightNumber': operating_flight_number,
                'flightTime': flight_time,
                'segmentType': segment_type,
                'aircraft': aircraft,
                'depTerminal': dep_terminal,
                'arrTerminal': arr_terminal,
                'id': i['classDesc']
            }))
        return segment_list

    @classmethod
    def parse_bundles(cls, fare_list, child_count, flight_number, price_tag_list, currency="CNY"):
        bundle_list = []

        passenger_type_list = [PassengerTypeEnum.ADT] if child_count == 0 else [PassengerTypeEnum.ADT,
                                                                                PassengerTypeEnum.CHD]
        for key, value in fare_list['priceClassInfo'].items():
            price_info = []
            price_tag = []
            for j in price_tag_list:
                price_tag.append(j['acivity_Name'])

            for i in passenger_type_list:
                if key == 'firstlyInfo':
                    fare = fare_list['firstlyPrice']
                else:
                    fare = fare_list['secondPrice']
                price_info.append(PriceInfoModel.model_validate({
                    'passengerType': i,
                    'fare': fare,
                    'tax': 0,
                    'currency': currency,
                    'ext': {
                        "priceTag": ','.join(price_tag)
                    }
                }))
            baggage_list = []
            if key == 'firstlyInfo':
                cabin = fare_list['lowClassEconomy']
                product_tag = "经济舱"
                cabin_level = CabinLevelEnum.ECONOMY
                for i in passenger_type_list:
                    baggage_list.append(BaggageInfoModel.model_validate({
                        "passengerType": i,
                        "baggageType": BaggageTypeEnum.HAND_LUGGAGE,
                        "pieces": 1,
                        "totalWeight": 5,
                        "flightNumber": flight_number,
                    }))
                    baggage_list.append(BaggageInfoModel.model_validate({
                        "passengerType": i,
                        "baggageType": BaggageTypeEnum.HAULING_BAGGAGE,
                        "pieces": 1,
                        "totalWeight": 20,
                        "flightNumber": flight_number,
                    }))
            else:
                cabin = fare_list['lowClassBusiness']
                product_tag = '公务舱'
                cabin_level = CabinLevelEnum.BUSINESS
                for i in passenger_type_list:
                    baggage_list.append(BaggageInfoModel.model_validate({
                        "passengerType": i,
                        "baggageType": BaggageTypeEnum.HAND_LUGGAGE,
                        "pieces": 1,
                        "totalWeight": 8,
                        "flightNumber": flight_number,
                    }))
                    baggage_list.append(BaggageInfoModel.model_validate({
                        "passengerType": i,
                        "baggageType": BaggageTypeEnum.HAULING_BAGGAGE,
                        "pieces": 1,
                        "totalWeight": 30,
                        "flightNumber": flight_number,
                    }))
            available_count = -1

            bundle_list.append(BundleInfoModel.model_validate({
                'priceInfo': price_info,
                'cabin': cabin,
                'productTag': cabin,
                'availableCount': available_count,
                'baggageList': baggage_list,
                'cabinLevel': cabin_level,
                'priceTag': price_tag,
                'id': product_tag,
                'ext': {
                    "priceTag": ','.join(price_tag)
                }
            }))
        return bundle_list

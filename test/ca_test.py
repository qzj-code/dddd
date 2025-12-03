import requests

false = False
true = True
null = None


def search():
    data = {
        "adultNum": 1,
        "cabinLevel": [
            "Y"
        ],
        "cacheLevel": "B",
        "carrier": [
            "CA"
        ],
        "childNum": 0,
        "connectOffice": "CAmobile",
        "currency": "CNY",
        "dataSource": "CAmobile",
        "depDate": "2025-12-30",
        "destination": "SZX",
        "ext": {
            "async": false,
            "callbackUrl": "http://47.116.13.161:29886/task/callBack"
        },
        "maxConnection": 0,
        "office": "CAmobile",
        "orderSessionId": null,
        "origin": "PEK",
        "passengerCode": [],
        "privateCode": [],
        "retDate": "",
        "sessionId": "1981923713193463808",
        "taskId": "1981450691610308620",
        "transAirport": null,
        "tripType": "1"
    }
    # url = 'http://127.0.0.1:8090/CAmobile/search'
    url = 'http://127.0.0.1:8090/CAapp/search'
    response = requests.post(url, json=data).json()
    print(response)


if __name__ == '__main__':
    search()

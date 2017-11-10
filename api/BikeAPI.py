import requests
from BasicAPI import BasicAPI


class BikeAPI(BasicAPI):

    type_name = 'bike'

    def __init__(self, user_lat, user_lon, search_distance=BasicAPI.proximity_threshold):
        super(BikeAPI, self).__init__(user_lat, user_lon, search_distance)
        self.get_obike_response()
        self.get_mobike_response()
        self.get_ofo_response()

    def get_bike_result(self):
        bike_result = self.get_concat_result(['mobike', 'obike', 'ofo'],
                                             [self.get_mobike_data, self.get_obike_data, self.get_ofo_data], 'bike')
        return bike_result

    def get_obike_response(self):
        payload = {
            'latitude': self.user_lat,
            'longitude': self.user_lon
        }
        bike_obike = requests.get("https://mobile.o.bike/api/v1/bike/list", params=payload)
        self.raw_response['obike'] = bike_obike

    def get_mobike_response(self):
        headers = {
            "Referer": "https://servicewechat.com/"
        }
        payload = {
            'latitude': self.user_lat,
            'longitude': self.user_lon
        }
        bike_mobike = requests.request("POST", "https://mwx.mobike.com/mobike-api/rent/nearbyBikesInfo.do",
                                       headers=headers, params=payload)
        self.raw_response['mobike'] = bike_mobike

    def get_ofo_response(self):
        headers = {
            "host": "one.ofo.com",
            "connection": "keep-alive",
            "accept": "*/*",
            "user-agent": "ofoBike/1.1.9 (iPhone; iOS 11.0; Scale/3.00)",
            "accept-language": "ja-JP;q=1, en-JP;q=0.9, zh-Hant-JP;q=0.8, zh-Hans-JP;q=0.7, ko-JP;q=0.6, de-JP;q=0.5",
            "content-length": "839",
            "accept-encoding": "gzip, deflate"
        }
        payload = {
            "countryCode": "SG",
            "languageArea": "SG",
            "languageCode": "en",
            "lat": self.user_lat,
            "lng": self.user_lon,
            "scale": 3,
            "source": 1,
            "source-version": 50,
            "token": "3e9133f0-a27b-11e7-882a-5937e108b29a"  # User token generated through mobile registration
        }
        session = requests.Session()
        session.headers.update(headers)
        response = session.post("https://one.ofo.com/nearbyofoCar", data=payload)
        self.raw_response['ofo'] = response

    def get_obike_data(self, bike_response):
        if bike_response.status_code == 404:
            return {
                'bike': [
                    {
                        'success': False,
                        'brand': 'obike'
                    }
                ]
            }
        bike_obike = bike_response.json()
        try:
            return {
                'bike': [
                    {
                        'lat': bike_dict['latitude'],
                        'lon': bike_dict['longitude'],
                        'dist': self.get_distance((self.user_lat, self.user_lon),
                                                  (bike_dict['latitude'], bike_dict['longitude'])),
                        'code': bike_dict['id'],
                        'brand': 'obike',
                        'type': 'bike'
                    }
                    for bike_dict in bike_obike['data']['list']],
                'success': True
            }
        except KeyError:
            return {
                'bike': [
                    {
                        'success': False,
                        'brand': 'obike'
                    }
                ]
            }

    def get_mobike_data(self, bike_response):
        if bike_response.status_code == 404:
            return {
                'bike': [
                    {
                        'success': False,
                        'brand': 'mobike'
                    }
                ]
            }
        bike_mobike = bike_response.json()
        try:
            return {
                'bike': [
                    {
                        'lat': bike_dict['distY'],
                        'lon': bike_dict['distX'],
                        'dist': self.get_distance((self.user_lat, self.user_lon),
                                                  (bike_dict['distY'], bike_dict['distX'])),
                        'code': bike_dict['bikeIds'],
                        'brand': 'mobike',
                        'type': 'bike'
                    }
                    for bike_dict in bike_mobike['object']],
                'success': True
            }
        except KeyError:
            return {
                'bike': [
                    {
                        'success': False,
                        'brand': 'mobike'
                    }
                ]
            }

    def get_ofo_data(self, bike_response):
        if bike_response.status_code == 404:
            return {
                'bike': [
                    {
                        'success': False,
                        'brand': 'ofo'
                    }
                ]
            }
        bike_ofo = bike_response.json()
        try:
            data = bike_ofo['values']['cars']
            return {
                'bike': [
                    {
                        'lat': bike_dict['lat'],
                        'lon': bike_dict['lng'],
                        'dist': self.get_distance((self.user_lat, self.user_lon), (bike_dict['lat'], bike_dict['lng'])),
                        'code': bike_index,
                        'brand': 'ofo',
                        'type': 'bike'
                    }
                    for bike_dict, bike_index in zip(data, range(len(data)))],
                'success': True
            }
        except KeyError:
            return {
                'bike': [
                    {
                        'success': False,
                        'brand': 'ofo'
                    }
                ]
            }

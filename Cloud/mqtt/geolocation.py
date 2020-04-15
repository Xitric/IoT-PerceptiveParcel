from typing import Tuple
import os
import requests

BASE_URL = 'https://www.googleapis.com/geolocation/v1/geolocate'

def coordinates_from_mac(stations: [Tuple[str, int]]):
    """
    Performs a geoloction request to Google using the provided array of station
    scans. The array must contain tuples of MAC addresses and signal strengths
    for a given scan.
    """
    url = '{}?key={}'.format(BASE_URL, os.environ['API_KEY_GEOLOCATION'])
    payload = __make_request_body(stations)
    headers = { 'Connection': 'close' }

    response = requests.post(url, json=payload, headers=headers)
    return __handle_response(response)

def __handle_response(response: requests.Response):
    if response.status_code == 200:
        json = response.json()
        if json:
            return (json['location']['lat'], json['location']['lng'], json['accuracy'])
    
    print('{}: {}'.format(response.status_code, response.reason))
    return None

def __make_request_body(stations: [Tuple[str, int]]):
    return {
        'considerIp': 'false',
        'wifiAccessPoints': [
            {
                "macAddress": station[0],
                "signalStrength": station[1],
                "signalToNoiseRatio": 0
            } for station in stations
        ]
    }

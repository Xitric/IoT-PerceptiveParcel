import paho.mqtt.client as paho
from mqtt import geolocation
from repository import db_context
import time
import json
import re

# Topics for pushing setpoint values and assigning packages
TOPIC_MOTION_SETPOINT = 'hcklI67o/package/{}/setpoint/motion'
TOPIC_TEMPERATURE_SETPOINT = 'hcklI67o/package/{}/setpoint/temperature'
TOPIC_HUMIDITY_SETPOINT = 'hcklI67o/package/{}/setpoint/humidity'
TOPIC_DEVICE_PACKAGE = 'hcklI67o/device/{}/package'
TEST = 'hcklI67o/device/30aea4ddc98c/package'

# Topics for receiving sensor values from devices
TOPIC_MOTION_PUBLISH = 'hcklI67o/package/+/motion'
TOPIC_TEMPERATURE_PUBLISH = 'hcklI67o/package/+/temperature'
TOPIC_HUMIDITY_PUBLISH = 'hcklI67o/package/+/humidity'
TOPIC_MACLOCATION_PUBLISH = 'hcklI67o/package/+/maclocation'

# Topics for publishing transformed data from cloud
TOPIC_COORDINATES_PUBLISH = 'hcklI67o/package/{}/coordinates'
TOPIC_PACKAGEID_PUBLISH = 'hcklI67o/device/{}/package'

# Topics to ping packages
TOPIC_PING = 'hcklI67o/package/{}/ping'

MILLENNIUM_SECONDS = 946681200

client = paho.Client()

def start():
    client.connect_async('broker.hivemq.com')
    client.loop_start()  # Starts the client in a background thread

def stop():
    client.loop_stop()
    client.disconnect()

def __on_connect(client, userdata, flags, rc):
    print('Connected: {}'.format(rc))
    client.subscribe(TOPIC_MOTION_PUBLISH, qos=1)
    client.subscribe(TOPIC_TEMPERATURE_PUBLISH, qos=1)
    client.subscribe(TOPIC_HUMIDITY_PUBLISH, qos=1)
    client.subscribe(TOPIC_MACLOCATION_PUBLISH, qos=1)
    client.subscribe(TEST, qos=1)

def __on_publish(client, userdata, mid):
    print('Published mid: {}'.format(mid))

def __on_subscribe(client, userdata, mid, qos):
    print('Subscribed: {} qos={}'.format(mid, qos))

def __on_message(client, userdata, msg):
    print('{}: {} {}'.format(msg.topic, msg.qos, msg.payload))

    package_id = __extract_package_id(msg.topic)
    if not package_id:
        return

    if __matches_topic(msg.topic, TOPIC_MOTION_PUBLISH):
        __handle_motion_exceeding(package_id, msg.payload)
    elif __matches_topic(msg.topic, TOPIC_TEMPERATURE_PUBLISH):
        __handle_temperature_exceeding(package_id, msg.payload)
    elif __matches_topic(msg.topic, TOPIC_HUMIDITY_PUBLISH):
        __handle_humidity_exceeding(package_id, msg.payload)
    elif __matches_topic(msg.topic, TOPIC_MACLOCATION_PUBLISH):
        __handle_mac_scan(package_id, msg.payload)

def __extract_package_id(topic):
    id_groups = re.search(r'package/(\w+)/', topic).groups()
    if len(id_groups) is not 1:
        return None

    return id_groups[0]

def __matches_topic(input_topic, reference_topic):
    pattern = '^{}$'.format(reference_topic.replace('+', r'\w+'))
    return bool(re.match(pattern, input_topic))

def __handle_mac_scan(package_id, stations_payload):
    json_stations = json.loads(stations_payload.decode())
    if len(json_stations) < 2:
        return

    stations = [(__to_mac_address(station[0]), station[1]) for station in json_stations]
    time = json_stations[0][2] + MILLENNIUM_SECONDS
    coordinates = geolocation.coordinates_from_mac(stations)

    if coordinates:
        # save location in db
        db_context.insert_location(package_id=package_id, timestamp=time, latitude=coordinates[0],
                                   longitude=coordinates[1],
                                   accuracy=coordinates[2])

def __to_mac_address(string):
    mac = ''
    for i, ch in enumerate(string):
        if i % 2 == 0 and i is not 0:
            mac += ':'
        mac += ch
    return mac

def __handle_temperature_exceeding(package_id, temperature_payload):
    time_temperature = json.loads(temperature_payload.decode())
    print("Handle temperature " + str(time_temperature))
    temperature = time_temperature["temperature"]
    timestamp = time_temperature["time"]
    if timestamp and temperature:
        # save temperature with time in db
        timestamp = timestamp + MILLENNIUM_SECONDS
        db_context.insert_temperature_exceeding(package_id=package_id, timestamp=timestamp, temperature=temperature)

def __handle_humidity_exceeding(package_id, humidity_payload):
    time_humidity = json.loads(humidity_payload.decode())
    print("Handle humidity " + str(time_humidity))
    humidity = time_humidity["humidity"]
    timestamp = time_humidity["time"]
    if timestamp and humidity:
        # save humidity with time in db
        timestamp = timestamp + MILLENNIUM_SECONDS
        db_context.insert_humidity_exceeding(package_id=package_id, timestamp=timestamp, humidity=humidity)

def __handle_motion_exceeding(package_id, motion_payload):
    time_motion = json.loads(motion_payload.decode())
    print("Handle motion " + str(time_motion))
    motion = time_motion["motion"]
    timestamp = time_motion["time"]

    if timestamp and motion:
        # save motion with time in db
        timestamp = timestamp + MILLENNIUM_SECONDS
        db_context.insert_motion_exceeding(package_id=package_id, timestamp=timestamp, motion=motion)

def set_motion_setpoint(package_id, setpoint):
    client.publish(TOPIC_MOTION_SETPOINT.format(package_id), setpoint, qos=1, retain=True)

def set_temperature_setpoint(package_id, setpoint):
    client.publish(TOPIC_TEMPERATURE_SETPOINT.format(package_id), setpoint, qos=1, retain=True)

def set_humidity_setpoint(package_id, setpoint):
    client.publish(TOPIC_HUMIDITY_SETPOINT.format(package_id), setpoint, qos=1, retain=True)

def set_package_id(device_id, package_id):
    client.publish(TOPIC_DEVICE_PACKAGE.format(device_id), package_id, qos=1, retain=True)

def ping_package(package_id):
    client.publish(TOPIC_PING.format(package_id), '0', qos=2, retain=False)

client.on_connect = __on_connect
client.on_publish = __on_publish
client.on_subscribe = __on_subscribe
client.on_message = __on_message

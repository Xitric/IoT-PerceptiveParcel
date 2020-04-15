import time
import paho.mqtt.client as paho
import json
import re
import geolocation as geo

# Topics for pushing setpoint values
TOPIC_MOTION_SETPOINT = 'hcklI67o/package/{}/setpoint/motion'
TOPIC_TEMPERATURE_SETPOINT = 'hcklI67o/package/{}/setpoint/temperature'
TOPIC_HUMIDITY_SETPOINT = 'hcklI67o/package/{}/setpoint/humidity'

# Topics for receiving sensor values from devices
TOPIC_MOTION_PUBLISH = 'hcklI67o/package/+/motion'
TOPIC_TEMPERATURE_PUBLISH = 'hcklI67o/package/+/temperature'
TOPIC_HUMIDITY_PUBLISH = 'hcklI67o/package/+/humidity'
TOPIC_MACLOCATION_PUBLISH = 'hcklI67o/package/+/maclocation'

# Topics for publishing transformed data from cloud
TOPIC_COORDINATES_PUBLISH = 'hcklI67o/package/{}/coordinates'
TOPIC_PACKAGEID_PUBLISH = 'hcklI67o/device/{}/package'

class MqttService:
    """
    A service for communicating with devices through an MQTT broker. It handles
    publishing of setpoint values as well as receiving sensor values and
    persisting them in the cloud.
    """

    def __init__(self):
        self.client = paho.Client()
        self.client.on_connect = self.__on_connect
        self.client.on_publish = self.__on_publish
        self.client.on_subscribe = self.__on_subscribe
        self.client.on_message = self.__on_message

    def start(self):
        self.client.connect_async('broker.hivemq.com')
        self.client.loop_start()  # Starts the client in a background thread

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

    def __on_connect(self, client, userdata, flags, rc):
        print('Connected: {}'.format(rc))
        self.client.subscribe(TOPIC_MOTION_PUBLISH, qos=1)
        self.client.subscribe(TOPIC_TEMPERATURE_PUBLISH, qos=1)
        self.client.subscribe(TOPIC_HUMIDITY_PUBLISH, qos=1)
        self.client.subscribe(TOPIC_MACLOCATION_PUBLISH, qos=1)

    def __on_publish(self, client, userdata, mid):
        print('Published mid: {}'.format(mid))

    def __on_subscribe(self, client, userdata, mid, qos):
        print('Subscribed: {} qos={}'.format(mid, qos))

    def __on_message(self, client, userdata, msg):
        print('{}: {} {}'.format(msg.topic, msg.qos, msg.payload))

        package_id = self.__extract_package_id(msg.topic)
        if not package_id:
            return
        
        if self.__matches_topic(msg.topic, TOPIC_MOTION_PUBLISH):
            pass  # TODO
        elif self.__matches_topic(msg.topic, TOPIC_TEMPERATURE_PUBLISH):
            pass  # TODO
        elif self.__matches_topic(msg.topic, TOPIC_HUMIDITY_PUBLISH):
            pass  # TODO
        elif self.__matches_topic(msg.topic, TOPIC_MACLOCATION_PUBLISH):
            self.__handle_mac_scan(package_id, msg.payload)
    
    def __extract_package_id(self, topic):
        id_groups = re.search(r'package/(\w+)/', topic).groups()
        if len(id_groups) is not 1:
            return None
        
        return id_groups[0]

    def __matches_topic(self, input_topic, reference_topic):
        pattern = '^{}$'.format(reference_topic.replace('+', r'\w+'))
        return bool(re.match(pattern, input_topic))

    def __handle_mac_scan(self, package_id, stations_payload):
        json_stations = json.loads(stations_payload.decode())
        if len(json_stations) < 2:
            print("Too few, baah")
            return
        
        stations = [(self.__to_mac_address(station[0]), station[1]) for station in json_stations]
        time = json_stations[0][2]
        coordinates = geo.coordinates_from_mac(stations)

        if coordinates:
            print('{}: {}'.format(time, coordinates))

        # TODO: Publish as json to MQTT broker

    def __to_mac_address(self, string):
        mac = ''
        for i, ch in enumerate(string):
            if i % 2 == 0 and i is not 0:
                mac += ':'
            mac += ch
        return mac

    def set_motion_setpoint(self, package_id, setpoint):
        self.client.publish(TOPIC_MOTION_SETPOINT.format(package_id), setpoint, qos=1, retain=True)

    def set_temperature_setpoint(self, package_id, setpoint):
        self.client.publish(TOPIC_TEMPERATURE_SETPOINT.format(package_id), setpoint, qos=1, retain=True)

    def set_humidity_setpoint(self, package_id, setpoint):
        self.client.publish(TOPIC_HUMIDITY_SETPOINT.format(package_id), setpoint, qos=1, retain=True)

if __name__ == '__main__':
    mqtt = MqttService()
    mqtt.start()
    time.sleep(3600)

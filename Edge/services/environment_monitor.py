from thread import Thread
from drivers import HTS221
from machine import Pin, I2C
from connection import MessagingService, Wifi, MqttConnection
import utime
import sys

TOPIC_TEMPERATURE_SETPOINT = 'hcklI67o/package/pkg123/setpoint/temperature'
TOPIC_HUMIDITY_SETPOINT = 'hcklI67o/package/pkg123/setpoint/humidity'
TOPIC_TEMPERATURE_PUBLISH = 'hcklI67o/package/pkg123/temperature'
TOPIC_HUMIDITY_PUBLISH = 'hcklI67o/package/pkg123/humidity'

class EnvironmentMonitor:
    """
    A service for monitoring the temperature and humidity around the device,
    and notifying the cloud service when setpoint values are exceeded. It also
    receives events from the cloud when setpoint values change.
    """

    def __init__(self, wifi: Wifi, mqtt: MqttConnection, messaging: MessagingService):
        self.wifi = wifi
        self.mqtt = mqtt
        self.messaging = messaging
        self.thread = Thread(self.__run, "EnvironmentThread")

        self.temperature_setpoint = None
        self.humidity_setpoint = None

        self.sensor = HTS221(I2C(-1, Pin(26, Pin.IN), Pin(25, Pin.OUT)))

    def start(self):
        self.thread.start()

    def __run(self, thread: Thread):
        self.mqtt.subscribe(TOPIC_TEMPERATURE_SETPOINT, self._on_temperature_setpoint, 1)
        self.mqtt.subscribe(TOPIC_HUMIDITY_SETPOINT, self._on_humidity_setpoint, 1)
        self.wifi.deactivate(False)
        self.messaging.notify()

        while thread.active:
            did_transmit = False

            if self.temperature_setpoint:
                if self.__check_temperature():
                    did_transmit = True
            
            if self.humidity_setpoint:
                if self.__check_humidity():
                    did_transmit = True
            
            if did_transmit:
                # TODO: Move to budget manager
                print("Notified messaging service of pending data")
                self.messaging.notify()

            utime.sleep(10)  # Reduce energy footprint?

    def __check_temperature(self) -> bool:
        temperature = self.sensor.read_temp()
        print("Read temperature: {}".format(temperature))
        if temperature > self.temperature_setpoint:
            self.mqtt.publish(TOPIC_TEMPERATURE_PUBLISH, temperature, qos=1)
            return True
        return False

    def __check_humidity(self) -> bool:
        humidity = self.sensor.read_humi()
        print("Read humidity: {}".format(humidity))
        if humidity > self.humidity_setpoint:
            self.mqtt.publish(TOPIC_HUMIDITY_PUBLISH, humidity, qos=1)
            return True
        return False

    def _on_temperature_setpoint(self, topic, msg):
        self.temperature_setpoint = float(msg)
        print('Received temperature {}'.format(msg))

    def _on_humidity_setpoint(self, topic, msg):
        self.humidity_setpoint = float(msg)
        print('Received humidity {}'.format(msg))

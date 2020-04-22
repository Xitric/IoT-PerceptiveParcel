from thread import Thread
from drivers import HTS221
from machine import Pin, I2C
from connection import MessagingService, Wifi, MqttConnection
import ubinascii
import machine
import utime
import sys

TOPIC_DEVICE_PACKAGE = 'hcklI67o/device/{}/package'
TOPIC_TEMPERATURE_SETPOINT = 'hcklI67o/package/{}/setpoint/temperature'
TOPIC_HUMIDITY_SETPOINT = 'hcklI67o/package/{}/setpoint/humidity'
TOPIC_TEMPERATURE_PUBLISH = 'hcklI67o/package/{}/temperature'
TOPIC_HUMIDITY_PUBLISH = 'hcklI67o/package/{}/humidity'

class EnvironmentMonitor:
    """
    A service for monitoring the temperature and humidity around the device,
    and notifying the cloud service when setpoint values are exceeded. It also
    receives events from the cloud when setpoint values change.
    """

    def __init__(self, wifi: Wifi, mqtt: MqttConnection, messaging: MessagingService, oled):
        self.wifi = wifi
        self.mqtt = mqtt
        self.messaging = messaging
        self.oled = oled
        self.thread = Thread(self.__run, "EnvironmentThread")

        self.temperature_setpoint = None
        self.humidity_setpoint = None

        self.sensor = HTS221(I2C(-1, Pin(26, Pin.IN), Pin(25, Pin.OUT)))

    def start(self):
        self.thread.start()

    def __run(self, thread: Thread):
        device_id = ubinascii.hexlify(machine.unique_id()).decode()
        self.mqtt.subscribe(TOPIC_DEVICE_PACKAGE.format(device_id), self._on_package_id, 1)
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
            self.mqtt.publish(TOPIC_TEMPERATURE_PUBLISH.format(self.messaging.package_id), temperature, qos=1)
            return True
        return False

    def __check_humidity(self) -> bool:
        humidity = self.sensor.read_humi()
        print("Read humidity: {}".format(humidity))

        if humidity > self.humidity_setpoint:
            self.mqtt.publish(TOPIC_HUMIDITY_PUBLISH.format(self.messaging.package_id), humidity, qos=1)
            return True
        return False

    def _on_package_id(self, topic, msg):
        print('Received package id {}'.format(msg))
        self.oled.push_line("PID: {}".format(msg))
        self.messaging.set_package_id(msg)
        # TODO: Unsubscribe from old id - umqttsimple does not support this!
        self.mqtt.subscribe(TOPIC_TEMPERATURE_SETPOINT.format(self.messaging.package_id), self._on_temperature_setpoint, 1)
        self.mqtt.subscribe(TOPIC_HUMIDITY_SETPOINT.format(self.messaging.package_id), self._on_humidity_setpoint, 1)
        self.messaging.notify()

    def _on_temperature_setpoint(self, topic, msg):
        self.temperature_setpoint = float(msg)
        print('Received temperature {}'.format(msg))

    def _on_humidity_setpoint(self, topic, msg):
        self.humidity_setpoint = float(msg)
        print('Received humidity {}'.format(msg))

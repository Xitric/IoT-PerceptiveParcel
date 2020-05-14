import math

from thread import Thread
from drivers import MPU6050, HTS221
from machine import Pin, I2C
from connection import MessagingService, Wifi, MqttConnection, BudgetManager, config
import ubinascii
import machine
import utime
import ujson
import sys

TOPIC_DEVICE_PACKAGE = 'hcklI67o/device/{}/package'

TOPIC_TEMPERATURE_SETPOINT = 'hcklI67o/package/{}/setpoint/temperature'
TOPIC_HUMIDITY_SETPOINT = 'hcklI67o/package/{}/setpoint/humidity'
TOPIC_MOTION_SETPOINT = 'hcklI67o/package/{}/setpoint/motion'
TOPIC_TEMPERATURE_PUBLISH = 'hcklI67o/package/{}/temperature'
TOPIC_HUMIDITY_PUBLISH = 'hcklI67o/package/{}/humidity'
TOPIC_MOTION_PUBLISH = 'hcklI67o/package/{}/motion'


class PackageMonitor:

    def __init__(self, mqtt: MqttConnection, messaging: MessagingService, budget_manager: BudgetManager):
        self.mqtt = mqtt
        self.messaging = messaging
        self.budget_manager = budget_manager

        self.environment_thread = Thread(self.__run_environment, "EnvironmentThread")
        self.motion_thread = Thread(self.__run_motion, "MotionThread")

        self.temperature_setpoint = config.get_float("temperature_setpoint")
        self.humidity_setpoint = config.get_float("humidity_setpoint")
        self.motion_setpoint = config.get_float("motion_setpoint")

        self.last_z = 0
        self.last_y = 0
        self.last_x = 0

        self.environment_sensor = HTS221(I2C(-1, Pin(26, Pin.IN), Pin(25, Pin.OUT)))
        self.motion_sensor = MPU6050(I2C(-1, Pin(26, Pin.IN), Pin(25, Pin.OUT)))

    def __subscribe_package_id(self):
        self.mqtt.subscribe(TOPIC_DEVICE_PACKAGE.format(self.mqtt.device_id), self._on_package_id, 1)
        self.messaging.notify()

    def _on_package_id(self, topic, package_id):
        # We should unsubscribe from the old id, but umqttsimple does not support this!
        self.mqtt.subscribe(TOPIC_TEMPERATURE_SETPOINT.format(package_id), self._on_temperature_setpoint, 1)
        self.mqtt.subscribe(TOPIC_HUMIDITY_SETPOINT.format(package_id), self._on_humidity_setpoint, 1)
        self.mqtt.subscribe(TOPIC_MOTION_SETPOINT.format(package_id), self._on_motion_setpoint, 1)
        self.messaging.notify()

    def start(self):
        self.__subscribe_package_id()
        self.environment_thread.start()
        self.motion_thread.start()

    def __run_environment(self, thread: Thread):
        while thread.active:
            did_transmit = False

            if self.temperature_setpoint:
                if self.__check_temperature():
                    did_transmit = True

            if self.humidity_setpoint:
                if self.__check_humidity():
                    did_transmit = True

            if did_transmit:
                print("Notified messaging service of pending data")
                self.messaging.notify()

            utime.sleep(10)

    def __run_motion(self, thread: Thread):
        while thread.active:
            did_transmit = False

            if self.motion_setpoint:
                if self.__check_motion():
                    did_transmit = True

            if did_transmit:
                print("Notified messaging service of pending data")
                self.messaging.notify()

            utime.sleep_ms(100)

    def __check_temperature(self) -> bool:
        temperature = self.environment_sensor.read_temp()
        print("Read temperature: {}".format(temperature))

        if temperature > self.temperature_setpoint:
            time = utime.localtime()
            self.budget_manager.enqueue(TOPIC_TEMPERATURE_PUBLISH.format(self.messaging.package_id), time, temperature, self.temperature_setpoint)
            return True
        return False

    def __check_humidity(self) -> bool:
        humidity = self.environment_sensor.read_humi()
        print("Read humidity: {}".format(humidity))

        if humidity > self.humidity_setpoint:
            time = utime.localtime()
            self.budget_manager.enqueue(TOPIC_HUMIDITY_PUBLISH.format(self.messaging.package_id), time, humidity, self.humidity_setpoint)
            return True
        return False

    def __check_motion(self) -> bool:
        values = self.motion_sensor.get_values()

        z = values['AcZ']
        y = values['AcY']
        x = values['AcX']

        motion = math.fabs(z + y + x - self.last_z - self.last_y - self.last_x)

        self.last_z = z
        self.last_y = y
        self.last_x = x

        if motion > self.motion_setpoint: #20000
            time = utime.time()
            self.budget_manager.enqueue(TOPIC_MOTION_PUBLISH.format(self.messaging.package_id), time, motion, self.motion_setpoint)
            return True

        return False

    def _on_temperature_setpoint(self, topic, msg):
        self.temperature_setpoint = float(msg)
        # We can't do this, because of the stupid recursion depth
        # config.set_value("temperature_setpoint", self.temperature_setpoint)
        print('Received temperature setpoint {}'.format(msg))

    def _on_humidity_setpoint(self, topic, msg):
        self.humidity_setpoint = float(msg)
        # We can't do this, because of the stupid recursion depth
        # config.set_value("humidity_setpoint", self.humidity_setpoint)
        print('Received humidity setpoint {}'.format(msg))

    def _on_motion_setpoint(self, topic, msg):
        self.motion_setpoint = float(msg)
        # We can't do this, because of the stupid recursion depth
        # config.set_value("motion_setpoint", self.motion_setpoint)
        print('Received motion setpoint {}'.format(msg))

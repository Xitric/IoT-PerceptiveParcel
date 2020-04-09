from thread import Thread
from drivers import HTS221
from machine import Pin, I2C
from connection import Wifi, MqttConnection
import utime

TOPIC_TEMPERATURE_SETPOINT = 'hcklI67o/package/id123/setpoint/temperature'
TOPIC_HUMIDITY_SETPOINT = 'hcklI67o/package/id123/setpoint/humidity'
TOPIC_TEMPERATURE_PUBLISH = 'hcklI67o/package/id123/temperature'
TOPIC_HUMIDITY_PUBLISH = 'hcklI67o/package/id123/humidity'

class EnvironmentMonitor:
    """
    A service for monitoring the temperature and humidity around the device,
    and notifying the cloud service when setpoint values are exceeded.
    """

    def __init__(self, wifi: Wifi, mqtt: MqttConnection):
        self.thread = Thread(self.__run, "ThreadEnvironment")

        self.wifi = wifi
        self.mqtt = mqtt

        self.mqtt.subscribe(TOPIC_TEMPERATURE_SETPOINT, self.on_temperature_setpoint, 0)
        self.mqtt.subscribe(TOPIC_HUMIDITY_SETPOINT, self.on_humidity_setpoint, 0)
        self.wifi.deactivate()
        # self.temperature_setpoint = None
        # self.humidity_setpoint = None
        self.temperature_setpoint = 12
        self.humidity_setpoint = None

        self.sensor = HTS221(I2C(-1, Pin(26, Pin.IN), Pin(25, Pin.OUT)))

    def start(self):
        self.thread.start()

    def __run(self, thread: Thread):
        while thread.active:
            if self.temperature_setpoint:
                self.__check_temperature()
            
            if self.humidity_setpoint:
                self.__check_humidity()
            
            utime.sleep(10)  # Reduce energy footprint?

    def __check_temperature(self):
        temperature = self.sensor.read_temp()
        print("Read temperature: {}".format(temperature))
        if temperature > self.temperature_setpoint:
            self.mqtt.publish(TOPIC_TEMPERATURE_PUBLISH, str(temperature).encode(), qos=1)

    def __check_humidity(self):
        humidity = self.sensor.read_humi()
        print("Read humidity: {}".format(humidity))
        if humidity > self.humidity_setpoint:
            self.mqtt.publish(TOPIC_HUMIDITY_PUBLISH, str(humidity).encode(), qos=1)

    def on_temperature_setpoint(self, topic, msg):
        self.temperature_setpoint = float(msg)
        print('Received temperature {}'.format(msg))

    def on_humidity_setpoint(self, topic, msg):
        self.humidity_setpoint = float(msg)
        print('Received humidity {}'.format(msg))

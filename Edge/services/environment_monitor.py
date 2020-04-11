import _thread
from drivers import HTS221
from machine import Pin, I2C
from connection import MessagingService, Wifi, MqttConnection
import utime
import sys

TOPIC_TEMPERATURE_SETPOINT = 'hcklI67o/package/id123/setpoint/temperature'
TOPIC_HUMIDITY_SETPOINT = 'hcklI67o/package/id123/setpoint/humidity'
TOPIC_TEMPERATURE_PUBLISH = 'hcklI67o/package/id123/temperature'
TOPIC_HUMIDITY_PUBLISH = 'hcklI67o/package/id123/humidity'

class EnvironmentMonitor:
    """
    A service for monitoring the temperature and humidity around the device,
    and notifying the cloud service when setpoint values are exceeded. It also
    receives events from the cloud when setpoint values change.
    """

    def __init__(self, wifi: Wifi, mqtt: MqttConnection, messaging: MessagingService):
        self.thread = _thread.start_new_thread(self.__run, ())

        self.wifi = wifi
        self.mqtt = mqtt
        self.messaging = messaging

        self.mqtt.subscribe(TOPIC_TEMPERATURE_SETPOINT, self._on_temperature_setpoint, 1)
        self.mqtt.subscribe(TOPIC_HUMIDITY_SETPOINT, self._on_humidity_setpoint, 1)
        self.wifi.deactivate(False)

        # TODO: Testing
        # self.temperature_setpoint = None
        # self.humidity_setpoint = None
        self.temperature_setpoint = 12
        self.humidity_setpoint = None

        self.sensor = HTS221(I2C(-1, Pin(26, Pin.IN), Pin(25, Pin.OUT)))

    def __run(self):
        try:
            while True:
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
        except (KeyboardInterrupt, SystemExit):
            pass
        except BaseException as e:
            sys.print_exception(e)

    def __check_temperature(self) -> bool:
        temperature = self.sensor.read_temp()
        print("Read temperature: {}".format(temperature))
        if temperature > self.temperature_setpoint:
            self.mqtt.publish(TOPIC_TEMPERATURE_PUBLISH, str(temperature).encode(), qos=1)
            return True
        return False

    def __check_humidity(self) -> bool:
        humidity = self.sensor.read_humi()
        print("Read humidity: {}".format(humidity))
        if humidity > self.humidity_setpoint:
            self.mqtt.publish(TOPIC_HUMIDITY_PUBLISH, str(humidity).encode(), qos=1)
            return True
        return False

    def _on_temperature_setpoint(self, topic, msg):
        self.temperature_setpoint = float(msg)
        print('Received temperature {}'.format(msg))

    def _on_humidity_setpoint(self, topic, msg):
        self.humidity_setpoint = float(msg)
        print('Received humidity {}'.format(msg))

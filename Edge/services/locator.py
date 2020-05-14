from connection import MqttConnection, MessagingService
from machine import Pin, PWM
import utime

TOPIC_DEVICE_PACKAGE = 'hcklI67o/device/{}/package'
TOPIC_PING = 'hcklI67o/package/{}/ping'

class Locator:

    def __init__(self, mqtt: MqttConnection, messaging: MessagingService):
        self.mqtt = mqtt
        self.messaging = messaging

        self.buzzer = Pin(27, Pin.OUT)
        self.ledAzure = Pin(33, Pin.OUT)
        self.ledWifi = Pin(32, Pin.OUT)
    
    def start(self):
        self.__subscribe_package_id()

    def __subscribe_package_id(self):
        self.mqtt.subscribe(TOPIC_DEVICE_PACKAGE.format(self.mqtt.device_id), self._on_package_id, 1)
        self.messaging.notify()

    def _on_package_id(self, topic, package_id):
        # We should unsubscribe from the old id, but umqttsimple does not support this!
        self.mqtt.subscribe(TOPIC_PING.format(package_id), self._on_ping, 1)
        self.messaging.notify()

    def _on_ping(self, topic, msg):
        beeper = PWM(self.buzzer, freq=300, duty=512)
        self.ledAzure.on()
        self.ledWifi.on()
        utime.sleep_ms(200)

        beeper.freq(500)
        self.ledAzure.off()
        self.ledWifi.off()
        utime.sleep_ms(200)

        beeper.freq(400)
        self.ledAzure.on()
        self.ledWifi.on()
        utime.sleep_ms(200)

        beeper.freq(600)
        self.ledAzure.off()
        self.ledWifi.off()
        utime.sleep_ms(200)

        beeper.deinit()

from connection import MessagingService, Wifi, MqttConnection
from services import Ntp, EnvironmentMonitor, Triangulation
from drivers import SSD1306_I2C
from machine import I2C, Pin

# OLED, width (128) might be incorrect
i2c = I2C(-1, Pin(26, Pin.IN), Pin(25, Pin.OUT))
oled = SSD1306_I2C(128, 32, i2c)

wifi = Wifi("AndroidAP", "vaqz2756")
mqtt = MqttConnection("broker.hivemq.com", wifi, oled)

messaging_service = MessagingService(wifi, oled)
messaging_service.add_channel(mqtt)
messaging_service.start()

ntp_service = Ntp(wifi, oled)
environment_service = EnvironmentMonitor(wifi, mqtt, messaging_service, oled)
triangulation_service = Triangulation(wifi, mqtt, messaging_service, oled)
ntp_service.start()
environment_service.start()
triangulation_service.start()
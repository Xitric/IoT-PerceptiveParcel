from connection import MessagingService, Wifi, MqttConnection
from services import Ntp, EnvironmentMonitor, Triangulation

wifi = Wifi("AndroidAP", "vaqz2756")
mqtt = MqttConnection("broker.hivemq.com", wifi)

messaging_service = MessagingService(wifi)
messaging_service.add_channel(mqtt)

ntp_service = Ntp(wifi)
environment_service = EnvironmentMonitor(wifi, mqtt, messaging_service)
triangulation_service = Triangulation(wifi, mqtt, messaging_service)

# OLED, width (128) might be incorrect
# from machine import I2C, Pin
# i2c = I2C(-1, Pin(26, Pin.IN), Pin(25, Pin.OUT))
# disp = SSD1306_I2C(128, 32, i2c)

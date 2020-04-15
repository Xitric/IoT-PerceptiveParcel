from connection import MessagingService, Wifi, MqttConnection
from services import Ntp, EnvironmentMonitor, Triangulation

wifi = Wifi("AndroidAP", "vaqz2756")
mqtt = MqttConnection("broker.hivemq.com", wifi)

messaging_service = MessagingService(wifi)
messaging_service.add_channel(mqtt)

ntp_service = Ntp(wifi)
environment_service = EnvironmentMonitor(wifi, mqtt, messaging_service)
triangulation_service = Triangulation(wifi, mqtt, messaging_service)

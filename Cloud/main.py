from mqtt import MqttService
from web import start_flask

mqtt = MqttService()
mqtt.start()

start_flask()

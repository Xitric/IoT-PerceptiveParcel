from connection import Wifi, MqttConnection
from services import Triangulation, EnvironmentMonitor, Ntp
import thread

wifi = Wifi("AndroidAP", "vaqz2756")
mqtt = MqttConnection("broker.hivemq.com", wifi)
location = Triangulation(wifi, mqtt)
location.start()
environment = EnvironmentMonitor(wifi, mqtt)
environment.start()
time = Ntp(wifi)
time.start()

thread.join([
    location.thread,
    environment.thread,
    time.thread
])

wifi.deactivate()
print("Goodbye :)")

import utime
from network import WLAN, STA_IF
from machine import Pin, I2C
from micropython import const
from umqttsimple import MQTTClient
from hts221 import HTS221

ssid = "WIFI-NAME"
pw = "PASSWORD"

max_temperature = 0
max_humidity = 0
received_temperature = False
received_humidity = False

station = WLAN(STA_IF)
station.active(True)

I2C0_SCL = const(26)
I2C0_SDA = const(25)
scl = Pin(I2C0_SCL, Pin.IN)
sda = Pin(I2C0_SDA, Pin.OUT)
address = 0x5F
i2c = I2C(-1, scl=scl, sda=sda)
sensor = HTS221(i2c=i2c, address=address)


def topic_contains(topic, text):
    return text in topic.decode()


def on_receive(topic, msg):
    # if (received_temperature and received_humidity):
    #    client.disconnect()
    topic_decoded = topic.decode()
    msg_decoded = msg.decode()

    # print(topic_decoded)
    # print(msg_decoded)

    global max_temperature, max_humidity, received_temperature, received_humidity

    if not received_temperature and topic_decoded == "iotproject123qwe/esp/maxTemperature":
        max_temperature = float(msg_decoded)
        received_temperature = True
        print("received temperature " + str(max_temperature))
    if not received_humidity and topic_decoded == "iotproject123qwe/esp/maxHumidity":
        max_humidity = float(msg_decoded)
        received_humidity = True
        print("received humidity " + str(max_humidity))


while not station.isconnected():
    print("Trying to connect to WiFi")
    station.connect(ssid, pw)
    utime.sleep(5)
print("Connected to wifi")

client = MQTTClient("client_id_420", "broker.hivemq.com")
client.connect()

client.set_callback(on_receive)
client.subscribe("iotproject123qwe/esp/maxTemperature", qos=1)
client.subscribe("iotproject123qwe/esp/maxHumidity", qos=1)

while True:
    msg = client.wait_msg()

    if received_temperature:
        temperature = sensor.read_temp()
        print("Reading: temperature: " + str(temperature))
        utime.sleep(1)
        if received_temperature and temperature > max_temperature:
            print("Publish: temperature " + str(temperature) + ">" + str(max_temperature))
            client.publish("iotproject123qwe/esp/maxTemperatureReached", str(temperature), qos=1)

    if received_humidity:
        humidity = sensor.read_humi()
        print("Reading: humidity: " + str(humidity))
        utime.sleep(1)
        if received_humidity and humidity > max_humidity:
            print("Publish: humidity " + str(humidity) + ">" + str(max_humidity))
            client.publish("iotproject123qwe/receive/maxHumidityReached", str(humidity), qos=1)

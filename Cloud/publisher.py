import time

import paho.mqtt.client as paho
import binascii
import mysql.connector

hostname = 'localhost'
username = 'root'
password = ''
database = 'location'
myConnection = mysql.connector.connect(host=hostname, user=username, passwd=password, db=database)


def get_location(address):
    cur = myConnection.cursor()

    cur.execute("SELECT latitude, longitude FROM location WHERE address = %s", [address])

    for latitude, longitude in cur.fetchall():
        return latitude, longitude


def on_connect(client, userdata, flags, rc):
    print("Connected: {}".format(rc))
    # client.subscribe("iotproject123qwe/esp/maxTemperatureReached", qos=1)
    # client.subscribe("iotproject123qwe/esp/maxHumidityReached", qos=1)
    client.subscribe("hcklI67o/package/123/maclocation")


def on_publish(client, userdata, mid):
    print("on_publish")
    # bytes = b'[["a06391209e70", -61, 233232], ["74da883a7f5e", -88, 233232], ["74da883a7f5d", -88, 233232]]'


def on_subscribe(client, userdata, mid, qos):
    print("Subscribed: {} {}".format(mid, qos))


def on_message(client, userdata, msg):
    print("{}: {} {}".format(msg.topic, msg.qos, msg.payload))

    signals = msg.payload.decode()
    signals = signals[2:-2].replace('\"', '')
    tuples = []
    for s in signals.split('], ['):
        signal = s.split(', ')
        tuples.append((signal[0], int(signal[1]), int(signal[2])))

    avg_lat = 0
    avg_lon = 0
    for t in tuples:
        location = get_location(t[0])
        avg_lat = avg_lat + location[0]
        avg_lon = avg_lon + location[1]

    avg_lat = avg_lat / 3
    avg_lon = avg_lon / 3

    client.publish("iotproject123qwe/esp/location/latitude", avg_lat, qos=1)
    client.publish("iotproject123qwe/esp/location/longitude", avg_lon, qos=1)


mysql.connector.connect()

client = paho.Client()
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_publish = on_publish
client.on_message = on_message
client.connect_async("broker.mqttdashboard.com")

client.loop_start()
while True:
    client.publish("iotproject123qwe/esp/maxTemperature", 26.8, qos=1)
    client.publish("iotproject123qwe/esp/maxHumidity", 40, qos=1)
    time.sleep(1)

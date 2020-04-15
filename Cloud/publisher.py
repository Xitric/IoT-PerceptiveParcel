import time
import paho.mqtt.client as paho

def on_connect(client, userdata, flags, rc):
    print('Connected: {}'.format(rc))
    client.subscribe('hcklI67o/package/+/maclocation', qos=1)
    client.subscribe('hcklI67o/package/+/temperature', qos=1)
    client.subscribe('hcklI67o/package/+/humidity', qos=1)

def on_publish(client, userdata, mid):
    print('Published mid: {}'.format(mid))

def on_subscribe(client, userdata, mid, qos):
    print('Subscribed: {} qos={}'.format(mid, qos))

def on_message(client, userdata, msg):
    print('{}: {} {}'.format(msg.topic, msg.qos, msg.payload))


client = paho.Client()
client.on_connect = on_connect
client.on_publish = on_publish
client.on_subscribe = on_subscribe
client.on_message = on_message

client.connect_async('broker.hivemq.com')
client.loop_forever()
# while True:
#     client.publish('iotproject123qwe/esp/maxTemperature', 26.8, qos=1)
#     client.publish('iotproject123qwe/esp/maxHumidity', 40, qos=1)
#     time.sleep(1)

from connection import Wifi, MQTTClient, ConnectionLostError, ServiceUnreachableError
import ubinascii
import machine

EHOSTUNREACH = 113

class MqttConnection(MQTTClient):
    
    # "broker.hivemq.com"
    def __init__(self, broker: str, wifi: Wifi):
        super().__init__(ubinascii.hexlify(machine.unique_id()), broker)
        self.wifi = wifi

    def connect(self, clean_session=True):
        self.wifi.connect()
        if not clean_session and self.sock:
            self.sock.close()
        super().connect(clean_session)

    def publish(self, topic: bytes, msg: bytes, retain=False, qos=0):
        while True:
            try:
                return super().publish(topic, msg, retain, qos)
            except OSError as osErr:
                if osErr.args[0] in [EHOSTUNREACH]:
                    print("Lost connection to broker")
                    self.connect(False)
                else:
                    raise  # Rethrow

    def receive(self, topic: str) -> bytes:
        pass

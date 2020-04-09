from connection import Wifi, MQTTClient
import ubinascii
import machine
import os

EHOSTUNREACH = 113
BUFFER_FILE = 'mqtt-buffer.txt'
BUFFER_FILE_COPY = 'mqtt-buffer-copy.txt'

class MqttConnection(MQTTClient):

    def __init__(self, broker: str, wifi: Wifi):
        super().__init__(ubinascii.hexlify(machine.unique_id()), broker)
        self.wifi = wifi
        self.wifi.add_wifi_listener(self.on_wifi)

        self._subscribers = {}
        self._pending_subscriptions = []
        super().set_callback(self.__on_receive)

    # TODO: Thread safe callback with locks
    def on_wifi(self):
        print("Device reconnected to Wifi")
        self.__publish_buffer()
        self.__handle_pending_subscriptions()
    
    def __publish_buffer(self):
        if BUFFER_FILE not in os.listdir():
            print("No buffer, nothing to do")
            return

        current_position = 0
        with open(BUFFER_FILE, 'r') as buffer:
            while True:
                current_position = buffer.tell()
                meta = buffer.readline()
                if not meta:
                    self.__retain_buffer(None)
                    return

                meta_elements = meta.split(";")
                topic = meta_elements[0]
                retain = bool(meta_elements[1])
                qos = int(meta_elements[2])
                msg = buffer.readline()

                if not self.__publish(topic, msg, retain, qos):
                    print("Couldn't publish message, even after reconnecting!?")
                    break
        
        self.__retain_buffer(current_position)

    def __retain_buffer(self, begin: int):
        if begin is None:
            print("Deleting buffer")
            os.remove(BUFFER_FILE)
            return
        
        if begin is 0:
            print("Buffer unaffected")
            return
        
        with open(BUFFER_FILE, 'r') as buffer:
            buffer.seek(begin)
            with open(BUFFER_FILE_COPY, 'w') as buffer_copy:
                for line in buffer:
                    buffer_copy.write(line)
        os.remove(BUFFER_FILE)
        os.rename(BUFFER_FILE_COPY, BUFFER_FILE)

    def __handle_pending_subscriptions(self):
        pending_count = len(self._pending_subscriptions)

        for i in range(pending_count):
            next = self._pending_subscriptions[pending_count - i - 1]
            if self.__subscribe(next[0], next[1]):
                self._pending_subscriptions.pop()
            else:
                print("Unable to subscribe even after reconnect")
                return

    def reconnect(self):
        if self.sock is None:
            print("Connecting")
            self.connect()
        else:
            print("Reconnecting")
            self.sock.close()
            super().connect(False)

    def publish(self, topic: bytes, msg: bytes, retain=False, qos=0) -> bool:
        if self.wifi.connect():
            if self.__publish(topic, msg, retain, qos):
                return True
            
        self.__buffer(topic, msg, retain, qos)
        return False
    
    def __publish(self, topic: bytes, msg: bytes, retain=False, qos=0) -> bool:
        if self.sock is None:
            self.connect()

        for retry in range(2):
            try:
                super().publish(topic, msg, retain, qos)
                print("Successfully published {}".format(msg))
                return True
            except OSError as osErr:
                if osErr.args[0] is EHOSTUNREACH and retry is 0:
                    self.reconnect()
        return False
    
    def __buffer(self, topic: bytes, msg: bytes, retain=False, qos=0):
        with open(BUFFER_FILE, 'a') as buffer:
            buffer.write('{};{};{}\n'.format(topic, retain, qos))
            buffer.write('{}\n'.format(msg))
        print("Buffered {}".format(msg))
    
    def subscribe(self, topic, callback, qos=0):
        if topic in self._subscribers:
            self._subscribers[topic].append(callback)
        else:
            self._subscribers[topic] = [callback]
        
        if self.wifi.connect():
            if self.__subscribe(topic, qos):
                return
        print('Unable to contact broker with subscription')
        self._pending_subscriptions.append((topic, qos))
    
    def __subscribe(self, topic, qos=0) -> bool:
        if self.sock is None:
            self.connect()

        for retry in range(2):
            try:
                super().subscribe(topic, qos)
                print("Successfully subscribed to {}".format(topic))
                return True
            except OSError as osErr:
                if osErr.args[0] is EHOSTUNREACH and retry is 0:
                    self.reconnect()
        return False
    
    def __on_receive(self, topic, msg):
        topic_decoded = topic.decode()
        msg_decoded = msg.decode()

        for subscriber in self._subscribers[topic_decoded]:
            subscriber(topic_decoded, msg_decoded)

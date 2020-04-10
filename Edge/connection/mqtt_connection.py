from connection import Wifi, MQTTClient
import ubinascii
import machine
import os
import _thread

EHOSTUNREACH = 113
BUFFER_FILE = 'mqtt-buffer.txt'
BUFFER_FILE_COPY = 'mqtt-buffer-copy.txt'

class MqttConnection(MQTTClient):

    def __init__(self, broker: str, wifi: Wifi):
        super().__init__(ubinascii.hexlify(machine.unique_id()), broker)
        self.wifi = wifi

        self._subscribers = {}
        self._pending_subscriptions = []
        super().set_callback(self.__on_receive)

        self.sync_lock = _thread.allocate_lock()

    def has_pending_messages(self):
        return len(self._pending_subscriptions) > 0 or BUFFER_FILE in os.listdir()

    def transmit(self):
        self.sync_lock.acquire()
        try:
            if self.wifi.connect():
                print("Device reconnected to Wifi")
                self.__transmit_buffer()
                self.__handle_pending_subscriptions()
        finally:
            self.sync_lock.release()
    
    def __transmit_buffer(self):
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

                if not self.__transmit_message(topic, msg, retain, qos):
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

    def __transmit_message(self, topic: bytes, msg: bytes, retain=False, qos=0) -> bool:
        if self.sock is None:
            self.connect()

        for retry in range(2):
            try:
                super().publish(topic, msg, retain, qos)
                print("Successfully published {}".format(msg))
                return True
            except OSError as osErr:
                if osErr.args[0] is EHOSTUNREACH and retry is 0:
                    self.__reconnect()
        return False

    def __handle_pending_subscriptions(self):
        pending_count = len(self._pending_subscriptions)

        for i in range(pending_count):
            next = self._pending_subscriptions[pending_count - i - 1]
            if self.__handle_subscription(next[0], next[1]):
                self._pending_subscriptions.pop()
            else:
                print("Unable to subscribe even after reconnect")
                return
    
    def __handle_subscription(self, topic, qos=0) -> bool:
        if self.sock is None:
            self.connect()

        for retry in range(2):
            try:
                super().subscribe(topic, qos)
                print("Successfully subscribed to {}".format(topic))
                return True
            except OSError as osErr:
                if osErr.args[0] is EHOSTUNREACH and retry is 0:
                    self.__reconnect()
        return False

    def __reconnect(self):
        if self.sock is None:
            print("Connecting")
            self.connect()
        else:
            print("Reconnecting")
            self.sock.close()
            self.connect(False)

    def publish(self, topic: bytes, msg: bytes, retain=False, qos=0):
        self.sync_lock.acquire()
        try:
            with open(BUFFER_FILE, 'a') as buffer:
                buffer.write('{};{};{}\n'.format(topic, retain, qos))
                buffer.write('{}\n'.format(msg))
            print("Buffered {}".format(msg))
        finally:
            self.sync_lock.release()
    
    def subscribe(self, topic, callback, qos=0):
        self.sync_lock.acquire()
        try:
            if topic in self._subscribers:
                self._subscribers[topic].append(callback)
            else:
                self._subscribers[topic] = [callback]
            
            self._pending_subscriptions.append((topic, qos))
        finally:
            self.sync_lock.release()
    
    def __on_receive(self, topic, msg):
        topic_decoded = topic.decode()
        msg_decoded = msg.decode()

        self.sync_lock.acquire()
        try:
            for subscriber in self._subscribers[topic_decoded]:
                subscriber(topic_decoded, msg_decoded)
        finally:
            self.sync_lock.release()

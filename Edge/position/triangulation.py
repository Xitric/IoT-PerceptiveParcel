import utime
from thread import Thread
from connection import Wifi, MqttConnection
import ujson
from ubinascii import hexlify
import os

class RssiTable:

    def __init__(self):
        self.table = {}
    
    def add(self, ssid: bytes, ss: int):
        self.table[ssid] = (ss, utime.time())

    def clean_table(self):
        for entry in self.table:
            time_added = self.table[entry][1]
            if utime.time() - time_added > 60:
                del self.table[entry]
    
    def snapshot(self, limit: int = -1):
        now = utime.time()
        scans = [(ssid, data[0], now) for ssid, data in self.table.items()]
        if limit == -1:
            return scans
        
        sorted_scans = sorted(scans, key=self.signal_strength, reverse=True)
        return sorted_scans[:limit]
    
    @staticmethod
    def signal_strength(scan):
        return scan[1]


class LocationTriangulation():

    def __init__(self, wifi: Wifi, mqtt: MqttConnection):
        self.thread = Thread(self.run, "ThreadLocation")
        # self.thread.start()

        self.table = RssiTable()
        self.wifi = wifi
        self.mqtt = mqtt

    def run(self, thread: Thread):
        print("Connecting to mqtt")
        self.mqtt.connect()
        # while thread.active:
        while True:
            print("Disconnecting to scan networks")
            self.wifi.disconnect()
            stations = self.wifi.scan()
            print("Got {}".format(stations))

            for station in stations:
                self.table.add(hexlify(station[1]), station[3])
            self.table.clean_table()

            self.send_location_fix(self.table.snapshot(3))
            utime.sleep(10)
            # payload = ujson.dumps(self.table.snapshot(2))
            # print(self.table.snapshot(3))
            # print("Trying to send message")
            # self.mqtt.publish(b'hcklI67o/package/123/maclocation', payload.encode("utf-8"))

    def send_location_fix(self, stations):
        payload = ujson.dumps(stations)
        if self.wifi.try_connect():
            if 'location-fixes.txt' in os.listdir(''):
                with open('location-fixes.txt', 'r') as buffer:
                    for line in buffer:
                        print("Sending {}".format(line))
                        self.mqtt.publish(b'hcklI67o/package/123/maclocation', line.encode("utf-8"))
                        buffer_empty = False
                os.remove('location-fixes.txt')

            print("Sending {}".format(payload))
            self.mqtt.publish(b'hcklI67o/package/123/maclocation', payload.encode("utf-8"))
        else:
            with open('location-fixes.txt', 'a') as buffer:
                print("Buffering {}".format(payload))
                buffer.write('{}\n'.format(payload))

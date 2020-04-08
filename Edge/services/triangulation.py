import utime
from thread import Thread
from connection import Wifi, MqttConnection
import ujson
import ubinascii

class RssiTable:
    """
    A class for keeping track of access points detected within the last minute.
    This is necessary, since the set of reported access points is highly
    volatile, even when the device is stationary.
    """

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


class Triangulation:
    """
    A service for determining the relative location of a device with respect to
    nearby Wifi access points.
    """

    def __init__(self, wifi: Wifi, mqtt: MqttConnection):
        self.thread = Thread(self.__run, "ThreadTriangulation")

        self.table = RssiTable()
        self.wifi = wifi
        self.mqtt = mqtt
    
    def start(self):
        self.thread.start()

    def __run(self, thread: Thread):
        while thread.active:
            self.wifi.disconnect()
            stations = self.wifi.scan()
            print("Got {}".format(stations))

            for station in stations:
                self.table.add(ubinascii.hexlify(station[1]), station[3])
            self.table.clean_table()

            self.send_location_fix(self.table.snapshot(3))
            self.wifi.disconnect()
            utime.sleep(10)

    def send_location_fix(self, stations):
        payload = ujson.dumps(stations)
        self.mqtt.publish(b'hcklI67o/package/123/maclocation', payload.encode("utf-8"))

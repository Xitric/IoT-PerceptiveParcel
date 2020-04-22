import utime
from thread import Thread
from connection import MessagingService, Wifi, MqttConnection
import ujson
import ubinascii
import sys

TOPIC_MACLOCATION_PUBLISH = 'hcklI67o/package/{}/maclocation'

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
            if utime.time() - time_added > 70:
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

    def __init__(self, wifi: Wifi, mqtt: MqttConnection, messaging: MessagingService, oled):
        self.table = RssiTable()
        self.wifi = wifi
        self.mqtt = mqtt
        self.messaging = messaging
        self.thread = Thread(self.__run, "LocationThread")
        self.oled = oled

        self.previous_snapshot = []
    
    def start(self):
        self.thread.start()

    def __unique_sets(self, a, b):
        for (a_elem, _, _) in a:
            for (b_elem, _, _) in b:
                if a_elem == b_elem:
                    return False
        return True

    def __run(self, thread: Thread):
        while thread.active:
            if self.messaging.package_id:
                # We cannot scan if we are connected to an access point
                self.wifi.disconnect()
                self.wifi.acquire()

                try:
                    stations = self.wifi.scan()
                    print("Got {}".format(stations))
                finally:
                    self.wifi.release()
                    self.wifi.deactivate(False)

                for station in stations:
                    # Filter out mobile network used while testing
                    if station[0] != b"AndroidAP":
                        self.table.add(ubinascii.hexlify(station[1]), station[3])
                self.table.clean_table()

                new_snapshot = self.table.snapshot(2)

                if len(stations) >= 2 and self.__unique_sets(new_snapshot, self.previous_snapshot):
                    self.previous_snapshot = new_snapshot
                    payload = ujson.dumps(self.previous_snapshot)
                    self.mqtt.publish(TOPIC_MACLOCATION_PUBLISH.format(self.messaging.package_id), payload)
                    self.messaging.notify()
                    self.oled.push_line("Got location")

            utime.sleep(27)
            
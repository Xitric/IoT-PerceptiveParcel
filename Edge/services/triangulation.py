import utime
import _thread
from connection import MessagingService, Wifi, MqttConnection
import ujson
import ubinascii
import sys

# TODO
from drivers import display
from machine import Pin, PWM

BUZ_IO27 = 27
buzzer = Pin(BUZ_IO27, Pin.OUT)
delay = 12

def beep(tone=440):
    beeper = PWM(buzzer, freq=tone, duty=512)
    utime.sleep_ms(500)
    beeper.deinit()

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

    def __init__(self, wifi: Wifi, mqtt: MqttConnection, messaging: MessagingService):
        self.table = RssiTable()
        self.wifi = wifi
        self.mqtt = mqtt
        self.messaging = messaging

        self.previous_snapshot = []

        self.thread = _thread.start_new_thread(self.__run, ())
    
    def start(self):
        self.thread.start()

    def __unique_sets(self, a, b):
        for (a_elem, _, _) in a:
            for (b_elem, _, _) in b:
                if a_elem == b_elem:
                    return False
        return True

    def __run(self):
        try:
            while True:
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
                    if station[0] == b"AndroidAP":
                        continue
                    self.table.add(ubinascii.hexlify(station[1]), station[3])
                self.table.clean_table()

                new_snapshot = self.table.snapshot(3)
                display([station[0] for station in new_snapshot])

                if len(stations) >= 2 and self.__unique_sets(new_snapshot, self.previous_snapshot):
                    self.previous_snapshot = new_snapshot
                    payload = ujson.dumps(self.previous_snapshot)
                    self.mqtt.publish('hcklI67o/package/123/maclocation', payload)
                    self.messaging.notify()
                    beep()

                utime.sleep(30)

        except (KeyboardInterrupt, SystemExit):
            pass
        except BaseException as e:
            sys.print_exception(e)

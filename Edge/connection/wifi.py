from connection import ConnectionLostError
from network import WLAN, STA_IF
import utime

class Wifi:

    def __init__(self, ssid: str, pw: str):
        super().__init__()
        self.station = WLAN(STA_IF)
        self.ssid = ssid
        self.pw = pw

    def activate(self):
        if not self.station.active():
            self.station.active(True)

    def deactivate(self):
        self.disconnect()
        self.station.active(False)

    def is_connected(self):
        return self.station.isconnected()

    def connect(self):
        while True:
            try:
                return self._connect()
            except ConnectionLostError:
                pass

    def try_connect(self) -> bool:
        try:
            self._connect()
            return True
        except ConnectionLostError:
            pass
        return False

    def _connect(self):
        self.activate()

        print("Trying to connect to WiFi")
        self.station.connect(self.ssid, self.pw)
        utime.sleep(2)

        if not self.station.isconnected():
            print("Failed to reach Wifi")
            raise ConnectionLostError
        else:
            print("WiFi enabled")

    def disconnect(self):
        self.station.disconnect()
    
    def scan(self):
        return self.station.scan()

from network import WLAN, STA_IF
import utime

class Wifi:

    def __init__(self, ssid: str, pw: str):
        self._station = WLAN(STA_IF)
        self._ssid = ssid
        self._pw = pw

    def activate(self):
        if not self._station.active():
            self._station.active(True)

    def deactivate(self):
        self.disconnect()
        self._station.active(False)

    def connect(self) -> bool:
        self.activate()

        if self._station.isconnected():
            return True
        
        self._station.connect(self._ssid, self._pw)
        utime.sleep(2)  # Allow the radio some time to connect
        if self._station.isconnected():
            return True
        
        self._station.disconnect()
        return False

    def is_connected(self):
        return self._station.isconnected()

    def disconnect(self):
        if self.is_connected():
            self._station.disconnect()
    
    def scan(self):
        self.activate()
        return self._station.scan()

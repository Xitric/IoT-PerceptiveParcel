# Since the standard implementation is clearly broken, this is adapted from:
# https://github.com/micropython/micropython/blob/master/ports/esp8266/modules/ntptime.py
from connection import Wifi
from thread import Thread
import socket
import socket
import struct
import utime
import machine

NTP_DELTA = 3155673600
HOST = "dk.pool.ntp.org"

class Ntp:
    """
    A service for synchronizing the local clock with an NTP service once a day,
    if possible.
    """

    def __init__(self, wifi: Wifi):
        self.thread = Thread(self.__run, "ThreadNtp")
        self.wifi = wifi

    def start(self):
        self.thread.start()
    
    def __run(self, thread: Thread):
        while thread.active:
            if self.wifi.connect():
                self.__settime()
            else:
                self.wifi.add_wifi_listener(self.on_wifi)
            
            utime.sleep(60 * 60 * 24)
    
    def on_wifi(self):
        self.__settime()
        self.wifi.remove_wifi_listener(self.on_wifi)

    def __time(self):
        ntp_query = bytearray(48)
        ntp_query[0] = 0x1B
        addr = socket.getaddrinfo(HOST, 123)[0][-1]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.settimeout(1)
            _ = s.sendto(ntp_query, addr)
            msg = s.recv(48)
        finally:
            s.close()

        val = struct.unpack("!I", msg[40:44])[0]
        return val - NTP_DELTA


    def __settime(self):
        t = utime.localtime(self.__time())
        machine.RTC().init((t[0], t[1], t[2], 0, t[3] + 1, t[4], t[5], t[6]))

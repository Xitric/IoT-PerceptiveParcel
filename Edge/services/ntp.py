# Since the standard implementation is clearly broken, this is adapted from:
# https://github.com/micropython/micropython/blob/master/ports/esp8266/modules/ntptime.py
# We also made it more resilient to connection issues, and converted it into a
# background service
from connection import Wifi
from thread import Thread
import socket
import struct
import utime
import machine
import sys

NTP_DELTA = 3155673600
HOST = "dk.pool.ntp.org"

class Ntp:
    """
    A service for synchronizing the local clock with an NTP service once a day.
    If the NTP service is unavailable, this service will retry synchronization
    every hour.
    """

    def __init__(self, wifi: Wifi, oled):
        self.wifi = wifi
        self.oled = oled
        self.thread = Thread(self.__run, "NtpThread")

    def start(self):
        self.thread.start()
    
    def __run(self, thread: Thread):
        while thread.active:
            self.wifi.acquire()
            try:
                if self.wifi.connect():
                    utime.sleep(5)  # Sometimes it fails if we are too fast?
                    self.__settime()
                    print("Updated clock with NTP")
                    self.oled.push_line("Updated clock")
                    continue
            except IndexError:
                # TODO: I have no idea why this happens sometimes
                print("Failed to update clock")
                pass
            finally:
                self.wifi.release()
                self.wifi.deactivate(False)
                utime.sleep(60 * 60 * 24)
            
            # Retry in an hour
            utime.sleep(60 * 60)
    
    def __time(self):
        ntp_query = bytearray(48)
        ntp_query[0] = 0x1B
        addr = socket.getaddrinfo(HOST, 123)[0][-1]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            for _ in range(5):
                try:
                    s.settimeout(1)
                    _ = s.sendto(ntp_query, addr)
                    msg = s.recv(48)
                    break
                except OSError:
                    pass
        finally:
            s.close()

        val = struct.unpack("!I", msg[40:44])[0]
        return val - NTP_DELTA


    def __settime(self):
        t = utime.localtime(self.__time())
        machine.RTC().init((t[0], t[1], t[2], 0, t[3] + 1, t[4], t[5], t[6]))

# Since the standard implementation is clearly broken, this is adapted from:
# https://github.com/micropython/micropython/blob/master/ports/esp8266/modules/ntptime.py
# We also made it more resilient to connection issues
from connection import Wifi
import _thread
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

    def __init__(self, wifi: Wifi):
        self.wifi = wifi
        self.thread = _thread.start_new_thread(self.__run, ())

    def start(self):
        self.thread.start()
    
    def __run(self):
        try:
            while True:
                self.wifi.acquire()
                try:
                    if self.wifi.connect():
                        utime.sleep(5)  # Sometimes it fails if we are too fast?
                        self.__settime()
                        continue
                except IndexError:
                    # TODO: I have no idea why this happens sometimes
                    pass
                finally:
                    self.wifi.release()
                    self.wifi.deactivate(False)
                    print("Updated clock with NTP")
                    utime.sleep(60 * 60 * 24)
                
                # Retry in an hour
                utime.sleep(60 * 60)

        except (KeyboardInterrupt, SystemExit):
            pass
        except BaseException as e:
            sys.print_exception(e)
    
    def __time(self):
        ntp_query = bytearray(48)
        ntp_query[0] = 0x1B
        addr = socket.getaddrinfo(HOST, 123)[0][-1]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            for _ in range(2):
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

from connection import Connection, ConnectionLostError, ServiceUnreachableError
from socket import socket
from network import WLAN, STA_IF
import utime

# Error codes that can occur during WiFi connections
ECONNRESET = 104
EHOSTUNREACH = 113
ENONETWORK = 118

class WifiConnection(Connection):

    def __init__(self, ssid: str, pw: str, service: str, port: int):
        super().__init__()
        self.station = WLAN(STA_IF)
        self.ssid = ssid
        self.pw = pw
        self.service = service
        self.port = port
        self.connection = None

    def _connect(self):
        if not self.station.active():
            self.station.active(True)

        print("Trying to connect to WiFi")
        self.station.connect(self.ssid, self.pw)
        utime.sleep(1)

        if not self.station.isconnected():
            print("Failed to reach Wifi")
            raise ConnectionLostError
        else:
            print("WiFi enabled")

    def __renew_connection(self):
        if self.connection:
            self.connection.close()

        self.connection = socket()
        self.connection.settimeout(5)

    def _connect_service(self):
        self.__renew_connection()
        print("Connecting to service")
        try:
            self.connection.connect((self.service, self.port))
            print("Connection established")
        except OSError as osErr:
            if osErr.args[0] == ENONETWORK:
                print("Lost network")
                raise ConnectionLostError
            elif osErr.args[0] in [EHOSTUNREACH, ECONNRESET]:
                print("Couldn't connect to service " + str(osErr.args[0]))
                utime.sleep(1)
                raise ServiceUnreachableError
            raise  # Rethrow

    def disconnect(self):
        # Disconnect from host
        self.connection.close()
        self.connection = None

        # Disconnect from Wifi
        self.station.disconnect()
        self.station.active(False)

    def _send(self, topic: str, payload: bytes):
        try:
            self.connection.sendall("Hello, world!".encode("utf-8"))
        except OSError as osErr:
            if osErr.args[0] in [EHOSTUNREACH, ECONNRESET]:
                print("Lost connection to host")
                raise ServiceUnreachableError
            raise  # Rethrow

    def _receive(self, topic: str, callback):
        pass

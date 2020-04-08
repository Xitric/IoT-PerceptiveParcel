from socket import socket
from network import WLAN, STA_IF
import utime

# Error codes that can occur during WiFi connections
ECONNRESET = 104
EHOSTUNREACH = 113
ENONETWORK = 118

# More meaningful errors
class ConnectionError(Exception):
    pass

class ConnectionLostError(ConnectionError):
    pass

class ServiceUnreachableError(ConnectionError):
    pass

class WifiConnection:

    def __init__(self, ssid: str, pw: str, service: str, port: int):
        super().__init__()
        self.station = WLAN(STA_IF)
        self.ssid = ssid
        self.pw = pw
        self.service = service
        self.port = port
        self.connection = None

    def activate(self):
        if not self.station.active():
            self.station.active(True)

    def deactivate(self):
        self.disconnect()
        self.station.active(False)

    def connect(self):
        successful = False

        while not successful:
            try:
                self.__retry_connect()  # Does not throw any exceptions
                self.__retry_connect_service()  # May throw a ConnectionLostError
                successful = True
            except ConnectionLostError:
                pass

    def __retry_connect(self):
        connected = False
        while not connected:
            try:
                self._connect()
                connected = True
            except ConnectionLostError:
                pass
    
    def __retry_connect_service(self):
        connected = False
        while not connected:
            try:
                self._connect_service()
                connected = True
            except ServiceUnreachableError:
                pass

    def _connect(self):
        self.activate()

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
                print("Couldn't connect to service")
                utime.sleep(1)
                raise ServiceUnreachableError
            raise  # Rethrow

    def disconnect(self):
        # Disconnect from host
        self.connection.close()
        self.connection = None

        # Disconnect from Wifi
        self.station.disconnect()

    def send(self, topic: str, payload: bytes):
        successful = False

        while not successful:
            try:
                self._send(topic, payload)
                successful = True
            except ConnectionLostError:
                self.connect()
            except ServiceUnreachableError:
                try:
                    self.__retry_connect_service()
                except ConnectionLostError:
                    self.connect()

    def _send(self, topic: str, payload: bytes):
        try:
            self.connection.sendall("{}: ".format(topic)
                                        .encode("utf-8")
                                        + payload)
        except OSError as osErr:
            if osErr.args[0] in [EHOSTUNREACH, ECONNRESET]:
                print("Lost connection to host")
                raise ServiceUnreachableError
            raise  # Rethrow
    
    def scan(self):
        return self.station.scan()

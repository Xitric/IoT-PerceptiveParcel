class ConnectionError(Exception):
    pass

class ConnectionLostError(ConnectionError):
    pass

class ServiceUnreachableError(ConnectionError):
    pass

class Connection:
    """Super class for abstracting connections over e.g. WiFi and serial."""

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
        pass

    def _connect_service(self):
        pass

    def disconnect(self):
        pass

    def send(self, topic: str, payload: bytes):
        successful = False

        while not successful:
            try:
                self._send(topic, payload)
                successful = True
                print("Success! OH!")
            except ConnectionLostError:
                print("Lost connection")
                self.connect()
            except ServiceUnreachableError:
                try:
                    print("Handling failed send")
                    self.__retry_connect_service()
                except ConnectionLostError:
                    self.connect()

            # except ConnectionError as connErr:
            #     print("WTH?!")
            #     if connErr is ConnectionLostError:
                    
            #     elif connErr is ServiceUnreachableError:
                    
            #     else:
            #         print(str(type(connErr)))

    def _send(self, topic: str, payload: bytes):
        pass

    def receive(self, topic: str, callback):
        # TODO
        self._receive(topic, callback)

    def _receive(self, topic: str, callback):
        pass

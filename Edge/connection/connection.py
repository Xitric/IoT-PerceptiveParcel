class ConnectionError(Exception):
    pass

class ConnectionLostError(ConnectionError):
    pass

class ServiceUnreachableError(ConnectionError):
    pass

from network import WLAN, STA_IF
import utime
import _thread

class Wifi:
    """
    A module for controlling the Wifi radio of the device. The methods in this
    module are permissive. For instance, if the Wifi radio is not yet
    activated, it will automatically be turned on when connecting to an access
    point.

    In order to save battery, the Wifi radio should be turned off through a
    call to `deactivate()` whenever possible.

    Since this module is shared by multiple threads, there is a potential risk
    in one thread turning off the Wifi radio when it is used by another. Thus,
    whenever a thread uses the Wifi radio, it should inform the wifi module
    first. It is also vital to inform the Wifi module when done using the Wifi
    radio - otherwise it may never be possile to deactivate it again. Other
    threads are not able to disable Wifi when it is in use. However, threads
    are free to enable Wifi at any time.

    The Wifi locking mechanism used in this module is a simple readers-writer
    lock using the Raynal method. Thus, the technique prefers users of the Wifi
    radio.
    """

    def __init__(self, ssid: str, pw: str):
        self._station = WLAN(STA_IF)
        self._ssid = ssid
        self._pw = pw

        # Readers-writer lock for activation/deactivation
        self.__readers_lock = _thread.allocate_lock()
        self.__global_lock = _thread.allocate_lock()
        self.__clients = []

    def activate(self):
        """Turn on the Wifi radio if it is off."""
        if not self._station.active():
            self._station.active(True)

    def deactivate(self, blocking=True):
        """
        Turn off the Wifi radio. This will also disconnect from the access
        point, if connected. If the Wifi radio is used by other threads, this
        method will block until Wifi can be deactivated. Alternatively, the the
        client can pass `False` to the `blocking` parameter to return
        immediately if the radio is used by others. This is useful if
        deactivation of the radio is not a hard requirement, but simply a hint.
        """
        if self.__global_lock.acquire(1 if blocking else 0):
            try:
                if self._station.isconnected():
                    self.__disconnect()
                if self._station.active():
                    self._station.active(False)
            finally:
                self.__global_lock.release()

    def connect(self) -> bool:
        """
        Connect to the access point if not already connected. This method will
        also ativate the Wifi radio if it is not currently on. However, if the
        method fails, it will not turn off the radio again.
        """
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
        """Check if currently connected to the access point."""
        return self._station.isconnected()

    def disconnect(self, blocking=True):
        """
        Disconnect from the access point if currently connected. If the Wifi
        radio is currently used by other threads, this method will block until
        it is possible to disconnect. Alternatively, the the client can pass
        `False` to the `blocking` parameter to return immediately if the radio 
        is used by others. This is useful if deactivation of the radio is not a
        hard requirement, but simply a hint.
        """
        if self.__global_lock.acquire(1 if blocking else 0):
            try:
                self.__disconnect()
            finally:
                self.__global_lock.release()
    
    def __disconnect(self):
        if self.is_connected():
            self._station.disconnect()
    
    def scan(self):
        """
        Scan for nearby access points. If the Wifi radio is not on, it will
        automatically be enabled.
        """
        self.activate()
        for _ in range(3):
            try:
                return self._station.scan()
            except RuntimeError:
                utime.sleep(1)  # Give radio time to turn on

    def acquire(self):
        """
        Inform the Wifi module that a thread wishes to use the Wifi radio. It
        is vital to match each call to this method with a similar call to
        `release()`. Each thread will be registered only once, regardless of
        how many times it calls this method.
        """
        self.__readers_lock.acquire()
        try:
            tid = _thread.get_ident()
            if not tid in self.__clients:
                self.__clients.append(tid)
                self.__global_lock.acquire(0)
        finally:
            self.__readers_lock.release()

    def release(self):
        """
        Inform the Wifi module that a client is done using the Wifi radio. If
        the calling thread has not been registered by a previous call to
        `acquire()`, then calling this method has no effect. Furthermore, it
        has no effect if a thread calls this method multiple times in
        succession.
        """
        self.__readers_lock.acquire()
        try:
            tid = _thread.get_ident()
            if tid in self.__clients:
                self.__clients.remove(tid)
                if len(self.__clients) == 0 and self.__global_lock.locked():
                    self.__global_lock.release()
        finally:
            self.__readers_lock.release()

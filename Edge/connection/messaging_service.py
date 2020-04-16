from connection import Wifi
from thread import Thread, ReentrantLock
import _thread
import ujson
import sys
import os

CONFIG_FILE = "config.json"

class MessagingService:
    """
    For transmitting messages out of the device, and buffering them locally in
    case a transmission channel is unavailable - such as missing Wifi.

    The messaging service can be in one of two possible states:
    - Waiting: The service is dormant, waiting for new messages or a channel to
    become available.
    - Transmitting: The service is currently transmitting messages.

    When the local message buffer is empty, the messaging service will enter
    the waiting state until explicitly notified of new messages. If any
    messages are available, the service will attempt to transmit them every ten
    minutes, or sooner if explicitly notified.

    Channels are themselves reponsible for ensuring thread safety. For
    instance, a channel might disallow buffering new messages during an active
    transmission.
    """

    def __init__(self, wifi: Wifi):
        self.wifi = wifi
        self.channels = []
        self.thread = Thread(self.__messaging_loop, "MessageThread")
        
        # TODO: Generalize and store setpoint values too?
        # Then we should extract it to a file like config.py
        if CONFIG_FILE in os.listdir():
            config = self.__read_config()
            self.package_id = config["package_id"]
        else:
            self.package_id = None
        
        # Semaphore for signaling the messaging service
        self._message_semaphore = _thread.allocate_lock()

        # Lock for protecting critical regions
        self._sync_lock = ReentrantLock()
    
    def start(self):
        self.thread.start()

    def notify(self):
        """
        Notify the messaging service to begin transmitting messages again. If
        the messaging service is currently in a waiting state, calling this
        method will restart it. The messaging service will return to a waiting
        state as soon as all pending messages have been transmitted, or
        channels become unavailable.
        """
        if self._message_semaphore.locked():
            self._message_semaphore.release()
    
    def set_package_id(self, package_id: str):
        self.package_id = package_id

        if not CONFIG_FILE in os.listdir():
            config = {}
        else:
            config = self.__read_config()

        config["package_id"] = package_id

        with open(CONFIG_FILE, "w") as config_file:
            config_file.write(ujson.dumps(config))
    
    def __read_config(self):
        with open(CONFIG_FILE, "r") as config_file:
            return ujson.loads("".join(config_file.readlines()))

    def __messaging_loop(self, thread: Thread):
        # This exception handling is necessary in order for background threads
        # to be affected by keyboard interrupts and to print stack traces in
        # case of exceptions.
        while thread.active:
            # There is no concept of a thread holding a lock with the _thread
            # library. A lock is either locked or unlocked, and if the same
            # thread attempts to acquire the same lock twice, it will block
            # itself until someone else calls release on the lock.

            if self.__has_pending_messages():
                # While there are pending messages, retry every ten minutes
                self._message_semaphore.acquire(1, 10 * 60)
            else:
                # Otherwise wait for an explicit signal
                self._message_semaphore.acquire()
            
            self._sync_lock.acquire()
            try:
                if not self.__has_pending_messages():
                    continue

                for channel in self.channels:
                    channel.transmit()
            finally:
                # In case Wifi was enabled, deactivate it now to save energy
                self.wifi.deactivate()
                self._sync_lock.release()
    
    def __has_pending_messages(self) -> bool:
        """Check if any channels have pending messages. Not thread safe."""
        for channel in self.channels:
            if channel.has_pending_messages:
                return True
        return False

    def add_channel(self, channel):
        """
        Add a new object to be used for transmitting messages out of the
        device.
        """
        self._sync_lock.acquire()
        try:
            self.channels.append(channel)
        finally:
            self._sync_lock.release()

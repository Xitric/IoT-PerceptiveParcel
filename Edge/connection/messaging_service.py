from connection import Wifi
import _thread
import sys

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
        
        # Semaphore for signaling the messaging service
        self._message_semaphore = _thread.allocate_lock()

        # Lock for protecting critical regions
        self._sync_lock = _thread.allocate_lock()

        self.thread = _thread.start_new_thread(self.__messaging_loop, ())

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

    def __messaging_loop(self):
        # This exception handling is necessary in order for background threads
        # to be affected by keyboard interrupts and to print stack traces in
        # case of exceptions.
        try:
            while True:
                # There is no concept of a thread holding a lock with this
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
        
        except (KeyboardInterrupt, SystemExit):
            pass
        except BaseException as e:
            sys.print_exception(e)
    
    def __has_pending_messages(self) -> bool:
        """Check if any channels have pending messages. Not thread safe."""
        for channel in self.channels:
            if channel.has_pending_messages:
                return True
        return False

    # TODO: Handle input, especially over MQTT
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

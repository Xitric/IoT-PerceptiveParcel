from connection import Wifi
import _thread
import sys

class MessagingService:
    """
    For transmitting messages over Wifi, and buffering them locally in case no
    internet is available.

    The messaging service can be in one of two possible states:
    - Waiting: The service is dormant, waiting for new messages or network to
    become available.
    - Transmitting: The service is currently transmitting messages over the
    network.

    Since messages are only sent on rare occasions, it is not possible to
    publish new messages while the messaging service is in the transmitting
    state. In this case, the publishing thread goes into a blocking wait, until
    the messaging service returns to the waiting state.
    """

    def __init__(self, wifi: Wifi):
        self.wifi = wifi
        self.channels = []
        self.thread = _thread.start_new_thread(self.__messaging_loop, ())
        
        # Semaphore for signaling the messaging service
        self._message_semaphore = _thread.allocate_lock()

        # Lock for protecting critical regions
        self._sync_lock = _thread.allocate_lock()

    def notify(self):
        """
        Notify the messaging service to begin transmitting messages again. If
        the messaging service is currently in a waiting state, calling this
        method will restart it. The messaging service will return to a waiting
        state as soon as all pending messages have been transmitted, or the
        network connection is lost.
        """
        if self._message_semaphore.locked():
            self._message_semaphore.release()

    def __messaging_loop(self):
        # This exception handling is necessary in order for background threads
        # to be affected by keyboard interrupts and to print stack traces in
        # case of exceptions.
        try:
            while True:
                # Try to acquire the semaphore. This will block the thread until the
                # semaphore is released by the scheduler. The scheduler can release the
                # semaphore to signal the messaging service when new data is ready to
                # be transmitted.
                # Do keep in mind that there is no concept of a thread holding a lock
                # with this library. A lock is either locked or unlocked, and if the
                # same thread attempts to acquire the same lock twice, it will block
                # itself until someone else calls release on the lock.

                if self.__has_pending_messages():
                    # While there are pending messages, retry every ten minutes
                    self._message_semaphore.acquire(1, 10 * 60)
                else:
                    # Otherwise wait for a signal
                    self._message_semaphore.acquire()
                
                self._sync_lock.acquire()

                try:
                    if not self.__has_pending_messages():
                        continue

                    for channel in self.channels:
                        channel.transmit()
                finally:
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

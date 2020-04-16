import _thread
import sys
try:
    import utime
except ModuleNotFoundError:
    import time as utime

class Thread:
    """
    An implementation of a thread built on top of the very basic _thread
    library available in MicroPython. This class provides utility wrappers for
    reducing the need for repeating basic interrupt handling, as well as for
    naming threads.
    """
    
    next_id = 1

    def __init__(self, run, name=None):
        self.id = None
        self.active = False
        self.__run = run

        if name:
            self.name = name
        else:
            self.name = "Thread" + str(Thread.next_id)
            Thread.next_id += 1

    def start(self):
        if self.active:
            raise RuntimeError("Thread is already running")
        if self.id:
            raise RuntimeError("Thread already completed")
        self.active = True
        self.id = _thread.start_new_thread(self.__start, ())
    
    def __start(self):
        try:
            self.__run(self)
        except (KeyboardInterrupt, SystemExit):
            pass
        except BaseException as e:
            sys.print_exception(e)
        finally:
            print("Stopped " + str(self.name))
            self.active = False
            _thread.exit()
    
    def interrupt(self):
        self.active = False

class ReentrantLock:
    """
    Implementation of a lock that allows for the same thread to acquire it
    multiple times without deadlocking. This is built on top of the very basic
    _thread library available in MicroPython.
    """

    def __init__(self):
        self.__internal_lock = _thread.allocate_lock()
        self.__owner = None
        self.__lock_count = 0
    
    def acquire(self, wait=1, timeout=-1):
        """
        Attempt to acquire this lock. If the current thread already holds the
        lock, the method returns immediately, after having incremented the lock
        count. Otherwise, the thread may wait until it is able to acquire the
        lock. It is vital to release the lock the same number of times as it
        was acquired to prevent deadlocks.

        If the `wait` parameter is `0`, the lock is only acquired if it can be
        done without waiting. If it is `1` (default), the thread will wait if
        necessary.

        If the `timeout` parameter is positive, it specifies how long, in
        seconds, the thread will wait for the lock. If it is `-1` (default),
        the thread will wait as long as necessary. The `timeout` can only be
        used when `wait` is set to `1`.

        This method returns `True` if the lock is held by the current thread,
        and `False` if the method returned without acquiring the lock.
        """

        # If we have already acquired the lock, then updating internal state is
        # safe
        ident = _thread.get_ident()
        if ident is self.__owner:
            self.__lock_count += 1
            return True
        
        # Otherwise, we must try to acquire the lock
        if self.__internal_lock.acquire(wait, timeout):
            self.__owner = ident
            self.__lock_count += 1
            return True

        return False

    def release(self):
        """
        If the current thread holds this lock, calling this method will
        decrement the lock count. When the lock count reaches zero (released as
        many times as it was acquired), the lock is released completely.

        A thread cannot release a lock that it does not hold.
        """

        ident = _thread.get_ident()
        if ident is not self.__owner:
            raise RuntimeError("Attempting to release lock without ownership")

        # By now, we know that we must be holding the lock, so updating
        # internal state is safe
        self.__lock_count -= 1
        if self.__lock_count is 0:
            self.__owner = None
            self.__internal_lock.release()

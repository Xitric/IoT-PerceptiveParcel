import _thread
try:
    import utime
except ModuleNotFoundError:
    import time as utime

class ThreadException(Exception):
    pass

class Thread:
    
    next_id = 1

    def __init__(self, run, name=None):
        self.state_lock = _thread.allocate_lock()
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
            raise ThreadException("Thread is already running")
        if self.id:
            raise ThreadException("Thread already completed")
        self.active = True
        self.id = _thread.start_new_thread(self.__start, [])
    
    def __start(self):
        try:
            self.state_lock.acquire()
            self.__run(self)
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            print("Stopped " + str(self.name))
            self.active = False
            self.state_lock.release()
            _thread.exit()
    
    def interrupt(self):
        self.active = False

def join(threads: [Thread]):
    try:
        for thread in threads:
            complete = False
            while not complete:
                thread.state_lock.acquire()
                thread.state_lock.release()
                if thread.active:
                    utime.sleep(0.1)
                else:
                    complete = True
    except (KeyboardInterrupt, SystemExit):
        for thread in threads:
            thread.interrupt()

def stop_current():
    _thread.exit()

def make_lock():
    return _thread.allocate_lock()

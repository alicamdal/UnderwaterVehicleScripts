import time
import threading
try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident


class eventClass(object):
    """An Event-like class that signals all active clients when a new data is
    available.
    """
    def __init__(self):
        self.events = {}

    def wait(self):
        """Invoked from each client's thread to wait for the next data."""
        ident = get_ident()
        if ident not in self.events:
            # this is a new client
            # add an entry for it in the self.events dict
            # each entry has two elements, a threading.Event() and a timestamp
            self.events[ident] = [threading.Event(), time.time()]
        return self.events[ident][0].wait()

    def set(self):
        """Invoked by the camera thread when a new data is available."""
        now = time.time()
        remove = None
        for ident, event in self.events.items():
            if not event[0].isSet():
                # if this client's event is not set, then set it
                # also update the last set timestamp to now
                event[0].set()
                event[1] = now
            else:
                # if the client's event is already set, it means the client
                # did not process a previous data
                # if the event stays set for more than 5 seconds, then assume
                # the client is gone and remove it
                if now - event[1] > 5:
                    remove = ident
        if remove:
            del self.events[remove]

    def clear(self):
        """Invoked from each client's thread after a data was processed."""
        self.events[get_ident()][0].clear()


class generator(object):
    thread = None  # background thread that reads data from camera
    data = None  # current data is stored here by background thread
    last_access = 0  # time of last client access to the camera
    event = eventClass()

    def __init__(self):
        """Start the background sourcec thread if it isn't running yet."""
        if generator.thread is None:
            generator.last_access = time.time()

            # start background data thread
            generator.thread = threading.Thread(target=self._thread)
            generator.thread.start()

            # wait until first data is available
            generator.event.wait()

    def get_frame(self):
        """Return the current camera data."""
        generator.last_access = time.time()

        # wait for a signal from the source thread
        generator.event.wait()
        generator.event.clear()

        return generator.data

    @staticmethod
    def data():
        """"Generator that returns data from the source."""
        raise RuntimeError('Must be implemented by subclasses.')

    @classmethod
    def _thread(cls):
        """Background thread."""
        print('Starting thread.')
        data_iterator = cls.data()
        for data in data_iterator:
            generator.data = data
            generator.event.set()  # send signal to clients
            time.sleep(0)

            # if there hasn't been any clients asking for data in
            # the last 10 seconds then stop the thread
            if time.time() - generator.last_access > 1:
                data_iterator.close()
                print('Stopping thread due to inactivity.')
                break
        generator.thread = None

import time
import threading
import datetime

import os

import flashcam.config as config



try:
    from greenlet import getcurrent as get_ident
except ImportError:
    print("i... error importing from greenlet ............")
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident





class CameraEvent(object):
    """An Event-like class that signals all active clients when a new frame is
    available.
    """

    def __init__(self):
        self.events = {}

    def wait(self):
        """Invoked from each client's thread to wait for the next frame."""
        ident = get_ident()
        if ident not in self.events:
            # this is a new client
            # add an entry for it in the self.events dict
            # each entry has two elements, a threading.Event() and a timestamp
            self.events[ident] = [threading.Event(), time.time()]
        return self.events[ident][0].wait()

    def set(self):
        """Invoked by the camera thread when a new frame is available."""
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
                # did not process a previous frame
                # if the event stays set for more than 5 seconds, then assume
                # the client is gone and remove it
                if now - event[1] > 5:
                    remove = ident
        if remove:
            del self.events[remove]

    def clear(self):
        """Invoked from each client's thread after a frame was processed."""
        self.events[get_ident()][0].clear()







class BaseCamera(object):
    """

    """
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera
    event = CameraEvent()
    nframes = 0
    kill = False # fo classmethod i should have it

    #actual_dm_conf = {}

    def __init__(self):
        """Start the background camera thread if it isn't running yet.
        all the parameters on cmdline will go to Thread and thread is launched
        """

        #--------------------------- TRYING TO CHANGE THE PARAMETER'S passage
        # config.load_config()  THIS IS IN WEB.PY

        # self.actual_dm_conf = {'target_frame':config.CONFIG['target_frame'],
        #         'average':  config.CONFIG['average'],
        #         'threshold':config.CONFIG['threshold'],
        #         'blur':     config.CONFIG['blur']}
        # print("i... basecamera2",  self.actual_dm_conf )



        if BaseCamera.thread is None:
            BaseCamera.last_access = time.time()

            # start background frame thread - the classmethod _thread
            print("D.. launching _thread")
            BaseCamera.thread = threading.Thread(target=self._thread   )
            BaseCamera.thread.start()

            # wait until frames are available
            while self.get_frame() is None:
                time.sleep(0)

    def get_frame(self):
        """Return the current camera frame."""
        BaseCamera.last_access = time.time()

        # wait for a signal from the camera thread
        BaseCamera.event.wait()
        BaseCamera.event.clear()

        return BaseCamera.frame

    @staticmethod
    def frames( ):
        """"Generator that returns frames from the camera."""
        raise RuntimeError('Must be implemented by subclasses.')

    #
    # this is where thisclass really starts to work when viewrConnects.
    #   calling .frames() => returns an iterator/generator
    #
    @classmethod
    def killme(cls):
        cls.kill = True



    @classmethod
    def _thread(cls):
        """Camera background thread.
        I try to get all neede parametaers here.
        """

        # print("i... inside _thread:", framekind, average, blur)
        frames_iterator = cls.frames( )
        cls.kill = False

        for frame in frames_iterator:
            # leave on error, i mean it permanent
            if (frame is None) or (len(frame)<100):
                # BaseCamera.thread = None
                print("X... no frame in _thread")
                # return
            BaseCamera.frame = frame
            BaseCamera.event.set()  # send signal to clients
            time.sleep(0)

            #print("D... kill of cls ==", cls.kill )
            # if there hasn't been any clients asking for frames in
            # the last 10 seconds then stop the thread
            # if time.time() - BaseCamera.last_access > 5:
            if False:
                print('X... Stopping camera thread due to inactivity.')
                frames_iterator.close()
                break
            if cls.kill:
                print("D... killing self in base_cam")
                break
        BaseCamera.thread = None
        print("X... leaving _thread")

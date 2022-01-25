import threading, time
import logging as logging_module
logging = logging_module.getLogger(__name__)

def startWhatapThread():
    def __whatap_jobs():
        from whatap.conf.configure import Configure as conf
        from whatap.net.udp_session import UdpSession
        UdpSession.read_timeout = conf.session_read_timeout
        UdpSession.udp()

        def __udp_recv():
            UdpSession.get()

        def __config_load():
            now = time.time()
            if now - conf.last_loaded > conf.init_load_interval / 1000:
                conf.init(False)

        while True:
            for job in (__udp_recv, __config_load):
                try:
                    job()
                    time.sleep(0)
                except Exception as e:
                    logging.debug(e, extra={'id': 'WA914'}, exc_info=True)
                    time.sleep(0.05)

    t = threading.Thread(target=__whatap_jobs)
    t.setDaemon(True)
    t.start()


    def __debug():
        from whatap.conf.configure import Configure as conf
        import whatap.util.debug_util as debug_util
        while True:
            
            if conf.debug_stack_enabled:
                debug_util.printAllStack()
            time.sleep(10)
    t = threading.Thread(target=__debug)
    t.setDaemon(True)
    t.start()


startWhatapThread()
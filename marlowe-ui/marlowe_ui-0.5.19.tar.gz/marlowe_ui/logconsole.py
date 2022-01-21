import tkinter as tk
import tkinter.scrolledtext
import queue

import logging

logger = logging.getLogger(__name__)


def getLogConsoleWindow(name):
    """create logging window, which is available by
    logging.getLogger(name)  (or name + .suffix)
    returns toplevel window object
    """
    logger = logging.getLogger(name)

    # prepare widget
    logwin = tk.Toplevel()
    # disable 'WM_DELETE_WINDOW' but iconify
    logwin.protocol('WM_DELETE_WINDOW', lambda: logwin.iconify())
    logtext = tkinter.scrolledtext.ScrolledText(logwin)
    # expose console.widget to Toplevel window
    logtext.pack(expand=True)


    # h -> QueueHandler -> log_queue
    log_queue = queue.Queue()
    h = QueueHandler(log_queue)
    # register handler and formatter
    h.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
    logger.addHandler(h)

    # log_queue -> logtext
    LogConsoleBinder(logtext, log_queue)

    return logwin



# from http://stackoverflow.com/questions/13318742/python-logging-to-tkinter-text-widget
class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(self.format(record))


class LogConsoleBinder():
    def __init__(self, scrolledtext, log_queue):
        self.scrolledtext = scrolledtext
        self.scrolledtext.config(state='disabled')

        self.log_queue = log_queue

        self.scrolledtext.after(100, self.poll_log_queue)

    def display(self, record):
        self.scrolledtext.config(state='normal')
        # Append message (record) to the scrolledtext
        self.scrolledtext.insert(tk.END, record + '\n')
        self.scrolledtext.see(tk.END)  # Scroll to the bottom
        self.scrolledtext.config(state='disabled')

    def poll_log_queue(self):
        while True:
            try:
                record = self.log_queue.get(False)
            except queue.Empty:
                break
            else:
                self.display(record)

        self.scrolledtext.after(100, self.poll_log_queue)



if __name__ == '__main__':
    import time
    import threading

    app = tk.Tk()

    # widgets
    # scrolledtext for message
    scrolledtext = tk.scrolledtext.ScrolledText(app)
    scrolledtext.pack(expand=True)

    # control logging level
    def on_logging_level(v):
        # dumper.logger.setLevel(logging.getLevelName(v))
        # old_dumper.logger.setLevel(logging.getLevelName(v))

        logging.getLogger().setLevel(v)

        logger.info(f'default logging level is {v}')

        # print all loggers
        # for name in logging.root.manager.loggerDict:
        #     lo = logging.getLogger(name)
        #     print(name, lo.getEffectiveLevel(), lo.propagate)

    logging_level_var = tk.StringVar(app, 'WARNING')
    logging_level = tk.OptionMenu(app, logging_level_var,
            'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', command=on_logging_level)
    logging_level.pack()


    # count thread
    class Countup(threading.Thread):
        def __init__(self):
            super().__init__()
            self.count = 0
            self.running = False

        def run(self):
            while True:
                if self.running:
                    logger.info(f'{self.count}')
                    self.count += 1
                time.sleep(1)

    countup = Countup()
    countup.daemon = True
    countup.start()

    # control button
    def action():
        if countup.running:
            # stop countup
            countup.running = False
            button.config(text='start counting')
        else:
            # start countup
            countup.running = True
            button.config(text='stop counting')

    button = tk.Button(app, text='start counting', command=action)
    button.pack()

    # bind root_handler -> QueHandler -> log_queue -> LogConsole -> scrolledtext
    log_queue = queue.Queue()
    # bind console and quele
    LogConsoleBinder(scrolledtext, log_queue)
    # logging hander connected to log_queue
    consolehandler = QueueHandler(log_queue)
    logging.getLogger().addHandler(consolehandler)

    app.mainloop()

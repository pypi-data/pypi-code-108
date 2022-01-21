"""
Various Application Adapters
"""

import os

from theming.absl_color_help import setup_colorized_help


def adapt_gevent_pywsgi(server, logger):
    """
    Make gevent's pywsgi log to structlog.

    server = log_to_structlog(
         gevent.pywsgi.WSGIServer((host, port)), logger=structlog.get_logger('..')
    )
    """

    def log_4_gevent_pywsgi(self, logger=logger):
        """(Pdb) self
        <gevent.pywsgi.WSGIHandler object at 0x7f482697ba20>
        """
        length = self.response_length or '-'
        if isinstance(self.client_address, tuple):
            ip = {'ip': self.client_address[0], 'port': self.client_address[1]}
        else:
            ip = {'ip': self.client_address or '-'}
        if self.time_finish:
            ip['dt'] = int((self.time_finish - self.time_start) * 1000)
        logger.info(
            self.requestline or '',
            length=self.response_length or '-',
            status=(self._orig_status or self.status or '000').split()[0],
            **ip
        )

    server.handler_class.log_request = log_4_gevent_pywsgi
    return server


def absl_run(mod_name, main, write_pid=True):
    def do_write_pid():
        try:
            fn = FLAGS.pidfile
        except:
            # only when he gave the flag
            return
        os.makedirs(os.path.dirname(fn), exist_ok=True)
        with open(fn, 'w') as fd:
            fd.write(str(os.getpid()))

    # legacy call, use devapp runner

    setup_colorized_help(main)
    if write_pid:
        do_write_pid()
    app.run(main)


# .

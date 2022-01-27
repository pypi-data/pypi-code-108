from typing import Callable
import signal
import logging
from time import sleep
from pathlib import Path
from ..core import Server, RunServer
from ..stm import HpsServer, StmServer
from ..ui import LayoutServer
from ...time_series import utctime_now, time


def start_service(*, model_root: str, log_file: str, port_base: int, web_ip: str, create_layout_srv: Callable[[str], LayoutServer] = None) -> None:
    """
    This function starts the model-repository services for
    core, and stm hps, stm and ui-layout models.

    It starts the socket-servers on ports
    port_base+0 (core)
    port_base+1 (stm_hps)
    port_base+2 (stm_sys)
    port_base+3 (run)
    port_base+4 (ui-layout)
    port_base+5 (ui-layout/web-api)

    :param model_root: points to the root directory
    :param log_file: log-file
    :param port_base: using port_base ..  port_base + 5
    :param web_ip: the ui-layout/web-api listening port
    :param create_layout_srv: a callable customization point to allow pythonized callbacks in the layout-server
    :return: None
    """
    _configure_logger(log_file)
    log = logging.getLogger('')

    root_path = Path(model_root)
    if not root_path.exists():
        root_path.mkdir()

    def mk_service(name: str, srv, sub_dir: str, port: int):
        m_root = root_path/Path(sub_dir)
        log.info(f'{name} at port {port}, model_root={m_root}')
        _ms = srv(str(m_root))
        _ms.set_listening_port(port)
        return name, _ms

    create_layout_srv = LayoutServer or create_layout_srv  # allow override from outside here
    log.info("starting services")
    ui_name = "(ui-layout) ui layout models"
    services = [mk_service("(core) energy-market -ltm- models", Server, 'core_mdl', port_base),
                mk_service("(hps)hydro-power system models", HpsServer, 'stm_hps', port_base + 1),
                mk_service("(stm)short-term system models", StmServer, 'stm_sys', port_base + 2),
                mk_service("(run)run models", RunServer, 'run', port_base + 3),
                mk_service(ui_name, create_layout_srv, "ui", port_base + 4)
                ]
    for _, s in services:
        s.start_server()
    # the ui layout service also have web-api
    uis = services[-1][1]
    w_root = root_path/Path("ui.www")
    if not w_root.exists():
        w_root.mkdir()

    uis.start_web_api(web_ip, port_base + 5, str(w_root), fg_threads=2, bg_threads=4)
    log.info(f'{ui_name}/web_api {web_ip}@{port_base + 5} doc_root={w_root}')
    ex = Exit()
    t_report = utctime_now()
    report_interval = time(1*60)  # emmit log entry every x min
    while True:
        sleep(1)
        if ex.now:
            break
        if utctime_now() - t_report > report_interval:
            srv_status = [s.is_running() for _, s in services]
            log.info(f'service_status_running:{srv_status}')
            t_report = utctime_now()
    log.info(f'terminating services ...')
    for name, ms in services:
        log.info(f'terminate {name}@{ms.get_listening_port()} ')
        ms.stop_server(1000)
    log.info(f'terminate ui/web-api')
    uis.stop_web_api()
    log.info('done')


def _configure_logger(filename: str = None, filemode: str = "w", level: int = logging.DEBUG,
                      log_format: str = '[%(asctime)s] %(name)-12s %(levelname)-8s %(message)s',
                      datefmt: str = '%m-%d %H:%M:%S'):
    for h in logging.root.handlers[:]:
        logging.root.removeHandler(h)
    logging.basicConfig(level=level,
                        format=log_format,
                        datefmt=datefmt,
                        filename=filename,
                        filemode=filemode)
    if filename is not None:
        console = logging.StreamHandler()
        console.setLevel(level)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)-8s: %(name)-12s %(message)s',
                                      datefmt='%m-%d %H:%M:%S')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)


class Exit:
    """
    A small helper-class to raise a flag if SIGTERM is received
    """
    now: bool = False  # signal handler sets this to True, and poll loop above terminates in controlled fashion

    def __init__(self):
        signal.signal(signal.SIGTERM, self.exit)

    @staticmethod
    def exit(signum, frame):
        Exit.now = True

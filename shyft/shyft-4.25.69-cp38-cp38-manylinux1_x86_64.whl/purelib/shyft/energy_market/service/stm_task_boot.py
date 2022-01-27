from shyft.energy_market import stm
import logging
import time
from shyft.energy_market.service.boot import _configure_logger, Exit


def start_service(*,
                  web_ip: str,
                  port_num: int,
                  api_port_num: int,
                  doc_root: str,
                  model_root: str,
                  log_file: str
                  ):
    """
    This function start the DStmServer instance for StmSystems.
    :param web_ip: Ip address to listen to 0.0.0.0 listen on all interfaces
    :param port_num: Port number to serve StmSystems
    :param doc_root: Path to root directory for web documents.
    :param api_port_num: Port number for the web API.
    :param log_file: Log file
    :return: None
    """
    _configure_logger(log_file)
    log = logging.getLogger('')

    log.info(f'Starting server on port {port_num}.')
    srv = stm.StmTaskServer(model_root)
    srv.set_listening_port(port_num)
    srv.start_server()
    log.info(f'Starting web API on port {api_port_num} listening on {web_ip} doc_root={doc_root}')
    srv.start_web_api(host_ip=web_ip, port=api_port_num, doc_root=doc_root, fg_threads=4, bg_threads=4)

    ex = Exit()
    while True:
        time.sleep(1)
        if ex.now:
            break

    log.info(f'terminating')
    srv.stop_web_api()
    srv.stop_server()
    log.info(f'done.')

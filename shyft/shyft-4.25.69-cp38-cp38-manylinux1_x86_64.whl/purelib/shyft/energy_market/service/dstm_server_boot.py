from shyft.energy_market import stm
from typing import Dict
import logging
import time
from shyft.energy_market.service.boot import _configure_logger, Exit


def create_server(web_ip: str,
                  port_num: int,
                  doc_root: str,
                  api_port_num: int,
                  server_log_root: str,
                  containers: Dict[str, str] = {}):
    """
    Function to create an instance of DStmServer
    :param web_ip: Address to listen to. 0.0.0.0 for all, 127.0.0.1 local &c.
    :param port_num: Port number to serve StmSystems
    :param doc_root: Path to root directory for web documents
    :param api_port_num: Port number for the web API.
    :param server_log_root: Directory where the server should store log files from optimizaation runs &c.
    :param containers: Dictionary of containers to add to the dtss owned by the server.
        Keys: Container name
        Values: Path to container directory.
    :return: Instance of server. Started and listening on provided port numbers.
    """
    srv = stm.DStmServer()
    srv.set_listening_port(port_num)
    for cname, cpath in containers.items():
        srv.add_container(cname, cpath)
    srv.start_server()
    srv.start_web_api(host_ip=web_ip, port=api_port_num, doc_root=doc_root)
    return srv


def start_service(web_ip: str,
                  port_num: int,
                  doc_root: str,
                  api_port_num: int,
                  log_file: str,
                  server_log_root: str,
                  containers: Dict[str, str] = {}):
    """
    This function start the DStmServer instance for StmSystems.
    :param web_ip: Ip address to listen to 0.0.0.0 listen on all interfaces
    :param port_num: Port number to serve StmSystems
    :param doc_root: Path to root directory for web documents.
    :param api_port_num: Port number for the web API.
    :param log_file: Log file
    :param server_log_root: Directory where the server should store log files from optimization runs &c.
    :return: None
    """
    _configure_logger(log_file)
    log = logging.getLogger('')

    srv = create_server(web_ip, port_num, doc_root, api_port_num, server_log_root, containers)
    log.info(f'Starting server on port {port_num}.')
    log.info(f'Starting web API on port {api_port_num}, listening on {web_ip}.')

    ex = Exit()
    while True:
        time.sleep(1)
        if ex.now:
            break

    log.info(f'terminating services')
    srv.stop_web_api()
    srv.close()

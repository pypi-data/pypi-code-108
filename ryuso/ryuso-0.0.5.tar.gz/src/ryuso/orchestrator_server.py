import json
import socket
import logging
import traceback

from ryuso import Orchestrator


MAX_BYTES_RECV = 100000000 # 100MB


class OrchestratorServer:
    '''
    OrchestratorServer: The server for a particular RYU spec

    This class takes a RYU Orchestrator and manages its external connections and
    requests.

    In its current state, this server is totally sequential and not concurrent.
    '''
    def __init__(self, orch: Orchestrator, host: str='0.0.0.0', port: int=60856, q: int=512):
        self.orchestrator = orch
        self.host = host
        self.port = port
        self.queue_len = q

    def do_run_task(self, task: dict):
        if self.orchestrator.validate_task(task):
            return self.orchestrator.run_task(task)

    def start_server(self):
        logging.info(
            'RYUSO server is starting with host %s, port %s, queue len %s',
            self.host,
            self.port,
            self.queue_len
        )
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        self.s.listen(self.queue_len)

        while True:
            has_sent = False
            conn, addr = self.s.accept()

            with conn:
                try:
                    data, _adata, _flags, _addr = conn.recvmsg(MAX_BYTES_RECV)

                    task = json.loads(data.decode())

                    logging.debug('Server received task: %s', task)

                    result = self.do_run_task(task)

                    logging.debug('Task successful, results are: %s', result)

                    # Send the results back to the client
                    conn.sendto(json.dumps(result).encode(), addr)
                    has_sent = True

                    logging.debug('Successfully returned results to client')
                except UnicodeDecodeError:
                    err = 'Could not decode the message provided'
                    logging.error('Data could not be decoded: {}'.format(data))
                except json.JSONDecodeError:
                    err = 'Message provided was not valid JSON'
                    logging.error('Bad JSON provided: {}'.format(data))
                except KeyboardInterrupt:
                    has_sent = True
                    logging.info('Caught SIGTERM on server, closing gracefully')
                    break
                except:
                    err = 'Unknown error'
                    logging.critical('An unknown error occurred:\n%s', traceback.format_exc())
                    break
                finally:
                    if not has_sent:
                        conn.sendto(json.dumps({'_server_error' : err}).encode(), addr)
        logging.info('RYUSO successfulyl exited main loop')

    def __del__(self):
        self.s.close()
        logging.debug('Successfully closed the socket')

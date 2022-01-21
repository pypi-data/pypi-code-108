import socket
import logging


class Client:
    def __init__(self, host: str = 'localhost', port: int = 3001, id: str = 'SCR', episodes: int = 1,
                 steps: int = 0, track: str = None, stage: int = 3, verbosity: int = 2):
        """
        Parameters:
            host (str)      Host IP address.
            port (int)      Host port number.
            id (str)        Robot ID.
            episodes (int)  Maximum number of learning episodes.
            steps (int)     Maximum number of steps.
            track (str)     Track name.
            stage (int)     Stage type [0: Warm-Up, 1: Qualifying, 2: Race, 3: Unknown].
            verbosity (int) Verbosity level of information messages.
        """
        self.logger = logging.getLogger(__name__)
        self.driver = None
        self.server = (host, port)
        self.id = id
        self.episodes = episodes
        self.steps = steps
        self.track = track
        self.stage = stage

        if verbosity > 1:
            self.logger.setLevel(logging.DEBUG)
        elif verbosity > 0:
            self.logger.setLevel(logging.INFO)
        else:
            self.logger.setLevel(logging.WARNING)

    def run(self, driver: type, angles: [float] = None):
        """
        Start the TORCS SCR client.

        Parameters:
            driver (type)   Class, inherited from the `Driver` class.
            angles (list)   Desired angles (w.r.t. the car axis) of all the 19 range finder sensors.
                            If None, span by 10 degrees.
        """
        self.logger.info(f'Connecting to server: {self.server}')
        self.logger.info(f'Robot ID: {self.id}')
        self.logger.info(f'Maximum episodes: {self.episodes}')
        self.logger.info(f'Maximum steps: {self.steps}')
        self.logger.info(f'Track: {self.track}')
        self.logger.info(f'Stage: {self.stage}')

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except OSError as error:
            self.logger.error(f'Cannot make a socket: {error}')
            return
        s.settimeout(1)

        self.driver = driver(self.stage)

        # By default, the sensors sample the space in front of the car every 10 degrees,
        # spanning clockwise from -90 degrees up to +90 degrees with respect to the car axis.
        if angles is None:
            angles = [x for x in range(-90, 100, 10)]

        episode = 0
        shutdown = False

        while not shutdown:
            self.logger.warning(f'Establishing connection to: {self.server}')
            while True:
                angles = ' '.join(map(str, angles))
                buffer = f'{self.id}-(init {angles})'
                self.logger.info(f'Sending initial string: {buffer}')
                buffer = buffer.encode()

                try:
                    s.sendto(buffer, self.server)
                except OSError as error:
                    self.logger.error(f'Cannot send data: {error}')
                    return

                try:
                    buffer, _ = s.recvfrom(1000)
                except OSError as error:
                    self.logger.error(f'Got no response from the server: {error}')

                if buffer.decode().find('***identified***') >= 0:
                    self.logger.debug(f'Received: {buffer}')
                break

            self.logger.warning('Established connection')

            step = 0

            while True:
                buffer = None
                try:
                    buffer, _ = s.recvfrom(1000)
                    buffer = buffer.decode()
                except OSError as error:
                    self.logger.warning(f'Got no response from the server: {error}')

                self.logger.debug(f'Received: {buffer}')

                if buffer is not None and buffer.find('***shutdown***') >= 0:
                    self.driver.on_shutdown()
                    shutdown = True
                    self.logger.warning('Shutting down the client')
                    break

                if buffer is not None and buffer.find('***restart***') >= 0:
                    self.driver.on_restart()
                    self.logger.warning('Restarting the client')
                    break

                step += 1

                if step != self.steps:
                    if buffer is not None:
                        buffer = self.driver.tick(buffer)
                else:
                    buffer = '(meta 1)'

                self.logger.debug(f'Sending: {buffer}')

                if buffer is not None:
                    try:
                        s.sendto(buffer.encode(), self.server)
                    except OSError as error:
                        self.logger.error(f'Cannot send data: {error}')
                        return

            episode += 1

            if episode == self.episodes:
                shutdown = True

        s.close()

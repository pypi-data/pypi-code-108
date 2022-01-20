import json
import subprocess


class NgrokContextManager:
    def __init__(self, ngrok_path, port=None):
        self.ngrok_path = ngrok_path
        self.port = port
        self.remote_addr = None
        self._process = None

    def init(self):
        self.process = process = subprocess.Popen(
            [
                self.ngrok_path,
                'http',
                str(self.port),
                '--log=stdout',
                "--log-format=json",
                "--log-level=debug"
            ],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.PIPE
        )

        # Detecting public address by grepping log
        while True:
            for line in process.stdout:
                data = json.loads(line.decode('utf-8'))
                if 'resp' in data and 'URL' in data['resp']:
                    self.remote_addr = data['resp']['URL']
                    return self.remote_addr
            else:
                try:
                    process.wait(0.5)
                except subprocess.TimeoutExpired:
                    continue
                else:
                    return

    def stop(self):
        if self.process:
            self.process.kill()
        self.process = None
        self.remote_addr = None

    def __call__(self, port=None):
        self.port = port or self.port
        if not self.port:
            raise AssertionError("Port required!")
        self.init()
        return self

    @property
    def url(self):
        return self.remote_addr

    def __str__(self):
        return self.remote_addr

    def __add__(self, other):
        return self.remote_addr + other

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

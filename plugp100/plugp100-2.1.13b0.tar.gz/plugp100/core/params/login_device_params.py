from dataclasses import dataclass


@dataclass
class LoginDeviceParams(object):
    password: str
    username: str

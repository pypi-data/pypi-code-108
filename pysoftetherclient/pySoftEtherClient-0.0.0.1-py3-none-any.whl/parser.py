import re


class Regrex:
    def __init__(self) -> None:
        self.nic_list = re.compile(
            '^Virtual[A-Za-z0-9 X]*\|(\w+)\n[A-Za-z0-9 X]*\|(\w+)\n[A-Za-z0-9 X]+\|([A-Za-z0-9 \-]+)\n[A-Za-z0-9 X]*\|([0-9 .]+)', re.MULTILINE)
        self.account_list = re.compile(
            '^VPN Connection[A-Za-z0-9 X]*\|(\w+)\n[A-Za-z0-9 X]*\|(\w+)\n[A-Za-z0-9 X]*\|([0-9]+.[0-9]+.[0-9]+.[0-9]+:[0-9]+)[A-Za-z0-9 X\(\)\/]+\n[A-Za-z0-9 X]*\|(\w+)\n[A-Za-z0-9 X]*\|(\w+)', re.MULTILINE)

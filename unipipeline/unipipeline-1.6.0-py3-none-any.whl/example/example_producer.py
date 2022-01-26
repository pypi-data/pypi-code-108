import os.path
import sys
from time import sleep

CWD = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.dirname(CWD))

from unipipeline.modules.uni import Uni
from example.args import args

u = Uni(f"{CWD}/dag-{args.type}.yml")

u.init_producer_worker('input_worker')

u.initialize()

for i in range(args.produce_count):
    u.send_to("input_worker", dict(value=i, some="Привет World"))
    sleep(1)

# u.exit()

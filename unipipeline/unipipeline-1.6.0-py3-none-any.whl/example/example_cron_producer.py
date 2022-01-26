import os.path
import sys

CWD = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.dirname(CWD))

from unipipeline.modules.uni import Uni
from example.args import args

u = Uni(f"{CWD}/dag-{args.type}.yml")

u.initialize_cron_producer_workers()

u.initialize()

u.start_cron()

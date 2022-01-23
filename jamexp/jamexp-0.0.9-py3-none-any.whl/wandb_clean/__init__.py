import os

import wandb

from .filters import if_notag, if_stale
from .utils import delete_run, delete_run_from_url, get_run_from_url

WANDB_USER = os.environ["WANDB_ENTITY"] or False
WANDB_KEY = os.environ["WANDB_API_KEY"] or False
WANDB_AVAIL = WANDB_USER and WANDB_KEY
if not WANDB_AVAIL:
    print("WANDB NON AVAIL, please set environment")
    exit(1)


def get_proj_runs(proj: str):
    api = wandb.Api()
    runs = api.runs(f"{WANDB_USER}/{proj}")
    return runs

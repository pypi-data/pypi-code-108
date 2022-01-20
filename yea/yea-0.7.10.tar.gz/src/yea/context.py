"""yea context."""

import datetime
import logging
import os

from yea import config, plugins


class YeaContext:
    def __init__(self, *, args):
        self._args = args
        self._cachedir = None
        self._covfile = None
        self._now = datetime.datetime.now()
        self._ts = self._now.strftime("%Y%m%dT%H%M%S")
        self._pid = os.getpid()
        self._setup_env()
        self._cfg = config.Config()
        self._setup_cachedir()
        self._setup_logging()
        self._plugs = plugins.Plugins(yc=self)

    def _setup_env(self):
        self._covfile = os.environ.get("COVERAGE_FILE")

    def _setup_cachedir(self):
        root = self._cfg._cfroot
        p = root.joinpath(".yea_cache")
        if not p.exists():
            p.mkdir()
        self._cachedir = p

    def _setup_logging(self):
        logger = logging.getLogger("yea")
        logger.propogate = False
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(fmt="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        logfname = "debug-{}-{}.log".format(self._ts, self._pid)
        lf = self._cachedir.joinpath(logfname)
        fh = logging.FileHandler(lf)
        fh.setFormatter(formatter)
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)
        logger.info("started")

    def is_live(self):
        return self._args.live

    def monitors_inform(self, tlist):
        self._plugs.monitors_inform(tlist)

    def monitors_init(self):
        self._plugs.monitors_init()

    def monitors_start(self):
        self._plugs.monitors_start()

    def monitors_stop(self):
        self._plugs.monitors_stop()

    def monitors_reset(self):
        self._plugs.monitors_reset()

    def test_prep(self, yt):
        # wandb_dir_safe_cleanup()
        self._plugs.test_prep(yt)

    def test_done(self, yt):
        # wandb_dir_safe_cleanup()
        self._plugs.test_done(yt)

    def test_check(self, yt):
        # ctx = self._backend.get_state()
        result_list = self._plugs.test_check(yt)
        return result_list

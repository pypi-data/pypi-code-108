import argparse
import importlib
import os
import secrets
import signal
import socket
import subprocess
import sys
import time
import platform
import pkg_resources
import io
import sentry_sdk  # NOTE: the runner does not have its own requirements.txt, so we're piggy-backing off of Rygg/Kernel having sentry as a dependency

SENTRY_DSN = "https://254212f937004cd7bb07d72e779a6eb5@o283802.ingest.sentry.io/6149913"


sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[],
    send_default_pii=True,
    environment="prod"
)    


PYTHON = sys.executable

IS_WIN = platform.system().lower().startswith("win")

class bcolors:
    KERNEL = '\033[95m'
    PERCEPTILABS = '\033[94m'
    RYGG = '\033[92m'
    ERROR = '\033[31m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    if IS_WIN:
        try:
            import colorama
            colorama.init()
        except:
            KERNEL = ''
            PERCEPTILABS = ''
            RYGG = ''
            WARNING = ''
            FAIL = ''
            ENDC = ''
            BOLD = ''
            UNDERLINE = ''

# We're assuming everything is running locally
HOST = "127.0.0.1"

PORTS = {
    "rendering-kernel": 5001,
    "rygg": 8000,
    "frontend": 8080,
}

MIGRATION_CMD = [PYTHON, "-m", "django", "migrate", "--settings", "rygg.settings"]
SERVICE_CMDS = [
    [PYTHON, "-m", "perceptilabs"],
    [PYTHON, "-m", "django", "runserver", f"{HOST}:{PORTS['rygg']}", "--settings", "rygg.settings", "--noreload"],
    [PYTHON, "-m", "django", "runserver", f"{HOST}:{PORTS['frontend']}", "--settings", "static_file_server.settings", "--noreload"],
    [PYTHON, "-c", "from static_file_server import website_launcher; website_launcher.launchAndKeepAlive()"],
]

TUTORIAL_DATA_PATH = pkg_resources.resource_filename('perceptilabs', 'tutorial_data')

def which_cmd():
    return "where" if IS_WIN else "which"

def check_for_git():

    try:
        from git import Repo
        return
    except:
        pass

    # ok, so we can't import git. Likely because there's no git installed
    has_git_exe = os.system(f"{which_cmd()} git") == 0
    if has_git_exe:
        print(f"{bcolors.WARNING}PerceptiLabs:{bcolors.ENDC} We're having trouble talking to git, so interactions with GitHub may not be available")
    else:
        print(f"{bcolors.WARNING}PerceptiLabs:{bcolors.ENDC} Your environment does not have git installed, so interactions with GitHub will not be available")

    time.sleep(1)

def do_migration(pipes, api_token):
    env = os.environ.copy()
    env["PL_FILE_SERVING_TOKEN"] = api_token
    migtate_proc = subprocess.run(MIGRATION_CMD, env=env, **pipes)
    if migtate_proc.returncode != 0:
        print(f"{bcolors.ERROR}Error:{bcolors.ENDC} Unable to upgrade your perceptilabs database.", file=sys.stderr)
        sys.exit(1)


def start_one(cmd, pipes, api_token):
    env = os.environ.copy()
    env["PL_FILE_SERVING_TOKEN"] = api_token

    return subprocess.Popen(cmd, **pipes, env=env)


def stop_one(proc, wait_secs=5):
    print(f"{bcolors.PERCEPTILABS}PerceptiLabs:{bcolors.ENDC} Stopping process {proc.pid}")
    try:
        proc.kill()
        proc.wait(wait_secs)
    except:
        print(f"{bcolors.PERCEPTILABS}PerceptiLabs:{bcolors.ENDC} No response. Terminating process {proc.pid}")
        proc.terminate()


def stop(procs):
    for proc in procs:
        stop_one(proc)


def is_alive(proc):
    proc.communicate()
    return proc.returncode == None


def are_all_alive(procs):
    return all([is_alive(p) for p in procs])


def watch(procs, interval_secs=1):
    while True:
        time.sleep(interval_secs)
        if not are_all_alive(procs):
            break

    stop(procs)


def get_pipes(verbosity):
    return {
        "stdout": subprocess.DEVNULL if verbosity < 2 else None,
        "stderr": subprocess.DEVNULL if verbosity < 1 else None,
        "stdin": subprocess.DEVNULL,
    }


class PortPoller:
    @staticmethod    
    def is_port_live(port):
        with socket.socket() as s:
            rc = s.connect_ex((HOST, port))
            return rc == 0

    @staticmethod        
    def get_unresponsive_ports():
        return [
            (name, port)
            for name, port in PORTS.items()
            if not PortPoller.is_port_live(port)
        ]

    @classmethod
    def wait_for_ports(cls, interval_secs=3, max_attempts=20):
        count = 0
        while True:
            unresponsive = cls.get_unresponsive_ports()
            if not any(unresponsive):
                return 

            count += 1
            if count > 1:
                if count < max_attempts:
                    cls._print_unresponsive(unresponsive)
                else:
                    cls._print_timeout(unresponsive, interval_secs, max_attempts)
                    raise SystemExit("One or more ports didn't respond")
                    
            time.sleep(interval_secs)

    @staticmethod            
    def _print_unresponsive(unresponsive):
        print(f"{bcolors.PERCEPTILABS}PerceptiLabs:{bcolors.ENDC} Waiting for services to listen on these ports:")
        for s, p in unresponsive:
            print(f"{bcolors.PERCEPTILABS}PerceptiLabs:{bcolors.ENDC}    {s} on port {p}")

    @staticmethod
    def _print_timeout(unresponsive, interval_secs, max_attempts):
        print(f"{bcolors.ERROR}PerceptiLabs:{bcolors.ENDC} The following services did not start correctly:")
        for s, p in unresponsive:
            print(f"{bcolors.ERROR}PerceptiLabs:{bcolors.ENDC}    {s} on port {p}")

        print(
            f"{bcolors.ERROR}One or more services failed to start within {interval_secs*max_attempts} seconds. {bcolors.ENDC}"
            f"{bcolors.ERROR}Verify that other applications aren't blocking the ports above. {bcolors.ENDC}"
            f"{bcolors.ERROR}If the problem persists, please get in touch at https://forum.perceptilabs.com/{bcolors.ENDC}"
        )            
        
def start(verbosity):
    # give the handler closure the shared procs variable
    procs = []

    def handler(signum, frame):
        print(f"{bcolors.PERCEPTILABS}PerceptiLabs:{bcolors.ENDC} Received SIGINT (Stop signal)")
        stop(procs)
        sys.exit(0)

    try:
        check_for_git()
        pipes = get_pipes(verbosity)
        api_token = secrets.token_urlsafe()
        do_migration(pipes, api_token)
        procs = list([start_one(cmd, pipes, api_token) for cmd in SERVICE_CMDS])
        print(f"{bcolors.PERCEPTILABS}PerceptiLabs:{bcolors.ENDC} Starting")
        PortPoller.wait_for_ports()
        print(f"{bcolors.PERCEPTILABS}PerceptiLabs:{bcolors.ENDC} PerceptiLabs Started")
        print(f"{bcolors.PERCEPTILABS}PerceptiLabs:{bcolors.ENDC} PerceptiLabs is running at http://localhost:8080/?token={api_token}")
        print(f"{bcolors.PERCEPTILABS}PerceptiLabs:{bcolors.ENDC} Use Control-C to stop this server and shut down all PerceptiLabs processes.")
        signal.signal(signal.SIGINT, handler)
        watch(procs)
    except Exception as e:
        print(e)
        sentry_sdk.capture_exception(e)
        stop(procs)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbosity", help="set output verbosity (0,1, or 2)", type=int, default=0)
    return parser.parse_args()


def main():
    args = get_args()
    start(args.verbosity)


if __name__ == "__main__":
    main()

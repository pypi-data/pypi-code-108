from dofast.flask.core import produce_cn_app
import subprocess
app = produce_cn_app('linux_work')


@app.task
def unlock_device() -> str:
    cmd = "/bin/loginctl unlock-session"
    subprocess.Popen(cmd, shell=True)
    return 'DONE'


@app.task
def lock_device() -> str:
    cmd = "/bin/loginctl lock-session"
    subprocess.Popen(cmd, shell=True)
    return 'DONE'

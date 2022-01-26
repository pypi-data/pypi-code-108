import subprocess

# 执行代码
def execute(code, target_type='py'):
    return subprocess.call(['python', '-c', code])

def check():
    try:
        import pgzrun
        return True
    except:
        return False
  	

def repair_pgzero():
	if check():
		print("pgzrun正常")
		return
	# pgzrun检查有问题
	print("pgzrun异常，正在尝试修复中，大约需要1-2分钟，请耐心等候")
	import os
	import subprocess
	import sys
	import shutil
	module_path = os.path.expanduser("~/学而思直播/code/site-packages")
	pgzero_path = os.path.join(module_path, "pgzero")
	# 删除旧的pgzero文件夹，因为可能为空
	if os.path.exists(pgzero_path):
		shutil.rmtree(pgzero_path)
	subprocess.check_output([sys.executable, "-m", "pip", "install", "pgzero==1.2.1", "-t", module_path])
	if (check()):
		print("pgzrun修复成功")
	else:
		print("pgzrun修复失败，请联系班主任")
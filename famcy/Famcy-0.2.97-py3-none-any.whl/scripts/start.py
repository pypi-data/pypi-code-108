import subprocess
import Famcy

def main(args):
	famcy_id = args[0]
	if "--dev" in args:
		_ = subprocess.check_output(["export", "FLASK_ENV=development"]) 
	_ = subprocess.check_output(["bash", Famcy.famcy_dir+"/scripts/bash/"+"run.sh", Famcy.famcy_dir, famcy_id]) 
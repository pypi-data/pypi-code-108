import subprocess
import Famcy

def main(args):
	famcy_id = args[0]
	init_script_output = subprocess.check_output(["bash", Famcy.famcy_dir+"/scripts/bash/"+"init.sh", famcy_id]) 
	print("[Famcy Init] ", init_script_output.decode())
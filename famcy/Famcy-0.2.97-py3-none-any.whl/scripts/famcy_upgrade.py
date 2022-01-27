import subprocess
import pkg_resources
import Famcy

def main(args):
	famcy_id = args[0]
	script_output = subprocess.check_output(["bash", Famcy.famcy_dir+"/scripts/bash/"+"upgrade.sh", Famcy.famcy_dir, famcy_id]) 
	print("[Famcy Upgrade] ", script_output.decode())
	print("Famcy version after upgrade: ", pkg_resources.require("Famcy")[0].version)
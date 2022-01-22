
import sys
import os 
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '__package_layer__'))

def main():
    import sys;import pkm_cli.main;sys.exit(pkm_cli.main.main())

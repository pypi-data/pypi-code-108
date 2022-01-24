import sys, os

demo_dir = os.path.dirname(__file__)
sys.path[0:0] = [demo_dir]

import Main

def _main():
    Main.main()

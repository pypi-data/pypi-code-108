"""
Tiny puthon script for running the setup MeqQuert bash script
for first time users.
"""
import subprocess as sub

def run_setup():
    sub.call(['sh', '.medqueryInit.sh'])

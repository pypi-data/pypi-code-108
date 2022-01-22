
import sys
import os 

package_layer_path = os.path.join(os.path.dirname(__file__), '__package_layer__')
sys.path.insert(0, package_layer_path)

if 'PYTHONPATH' in os.environ:
    os.environ['PYTHONPATH'] = package_layer_path + os.pathsep + os.environ['PYTHONPATH']
else:
    os.environ['PYTHONPATH'] = package_layer_path

def main():
    import sys;import pkm_cli.main;sys.exit(pkm_cli.main.main())

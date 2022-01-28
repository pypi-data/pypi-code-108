import os
import sys
import json
import getopt

from jinja2 import Environment, PackageLoader, select_autoescape
from ryuso import util


HELP = '''RYU Sequential Orchestrator Factory

Command-line interface for building a working sequential orchestrator from a
RYU spec.

OPTIONS:
    -h --help
        Help. Print this message and exit.

    -o DIR
        Output directory. This is the directory in which RYUSO will create a
        subdirectory containing the package to be built. DIR defaults to ./

    -s SPEC_FILE
        The path to the RYU spec to be built. By default SPEC_FILE
        is ./ryu_spec.json

AUTHOR:
    Written by Marcus Belcastro

SEE ALSO:
    Source code: https://gitlab.com/delta1512/ryu-sequential-orchestrator
'''

spec_file = './ryu_spec.json'
out_dir = './'


opts, args = getopt.getopt(sys.argv[1:], 'ho:s:', ['help'])

for opt, arg in opts:
    if opt == '-h' or opt == '--help':
        print(HELP)
        sys.exit(0)
    elif opt == '-o':
        out_dir = arg
    elif opt == '-s':
        spec_file = arg


env = Environment(
    loader=PackageLoader('ryuso'),
    autoescape=select_autoescape()
)

# Fetch the RYU spec
with open(spec_file, 'r') as ryu_spec_f:
    ryu_spec_str = ryu_spec_f.read() # So that we can copy it later
    ryu_spec = json.loads(ryu_spec_str)

assert util.validate_spec(ryu_spec), 'The spec provided contains errors.'

pkg_name = ryu_spec.get('name').lower().replace(' ', '_')

# First build the directory structure
os.makedirs(os.path.join(out_dir, pkg_name, 'hooks'))
pkg_root = os.path.join(out_dir, pkg_name)

# Next build main
t = env.get_template('__main__.py.temp')

with open(os.path.join(pkg_root, '__main__.py'), 'w') as main_f:
    main_f.write(t.render(pkg_name=pkg_name))

# Then init
t = env.get_template('__init__.py.temp')
hook_files = set()

for h in ryu_spec.get('hooks'):
    # Get the second to last object in the reference (this is the .py file)
    # where the hooks will be contained.
    # TODO: Make this generalised so we can have any hierarchy
    ref = ryu_spec.get('hooks').get(h).get('reference').split('.')[-2]
    hook_files.add(ref)

with open(os.path.join(pkg_root, '__init__.py'), 'w') as main_f:
    main_f.write(t.render(pkg_name=pkg_name, hook_files=hook_files))

# Then build the hook stubs
t = env.get_template('func_defs.py.temp')

for hf in hook_files:
    with open(os.path.join(pkg_root, 'hooks', '{}.py'.format(hf)), 'w') as hfd:
        hfd.write(t.render(current_parent=hf, hooks=ryu_spec.get('hooks')))

# Add an init for the hooks
with open(os.path.join(pkg_root, 'hooks', '__init__.py'), 'w') as _:
    pass

# Finally, copy the spec over
with open(os.path.join(pkg_root, 'ryu_spec.json'), 'w') as ryu_spec_f:
    ryu_spec_f.write(ryu_spec_str)

print('Done.')

#!/usr/bin/env python
import argparse
import distutils.core
import os
import sys


parser = argparse.ArgumentParser(description="Display 'mlpiper' dependencies")
parser.add_argument(
    "--with-sagemaker",
    dest="with_sagemaker",
    action="store_true",
    help="Display also the dependencies for the extra option: sagemaker",
)
args = parser.parse_args()

mlpiper_root = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")

sys.path.insert(0, mlpiper_root)
setup = distutils.core.run_setup(os.path.join(mlpiper_root, "setup.py"))

all_deps = []

all_deps.extend(setup.install_requires)
if args.with_sagemaker:
    sagemaker_deps = []
    sagemaer_deps_with_constraints = []
    for key, deps in setup.extras_require.items():
        # Note that it is important to keep the order of dependencies
        if key.startswith("sagemaker"):
            if ":" in key:
                parts = key.split(":")
                const = parts[1].replace(" ", "")
                for d in deps:
                    sagemaer_deps_with_constraints.append("{};{}".format(d, const))
            else:
                sagemaker_deps = deps

    all_deps.extend(sagemaer_deps_with_constraints)
    all_deps.extend(sagemaker_deps)

print("\n".join(all_deps))

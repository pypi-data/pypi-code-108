import subprocess
import os

# Install coverage.
subprocess.check_call(["python", "-m", "pip", "install", "coverage==5.2"])

curdir = os.path.dirname(os.path.abspath(__file__))

# Run coverage analysis
subprocess.check_call(["coverage", "run", os.path.join(curdir, "run_unit_tests_using_tox.py")])

# Combine coverage reports
subprocess.check_call(["coverage", "combine"])

# Generate html report
subprocess.check_call(["coverage", "html"])

# Open a browser tab with the coverage report
os.system("start htmlcov/index.html")

# Print coverage report to stdout
subprocess.check_call(["coverage", "report"])

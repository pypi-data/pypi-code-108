"""
Increment the version number and deploy to PyPi.
"""
import os
import glob
import re
import sys
import subprocess

try:
    import twine
except ImportError:
    print("Please install twine first:   pip install twine")
    raise


def incr_version(v: str):
    v0 = tuple(int(part) for part in v.split("."))
    v1 = v0[:-1] + (v0[-1] + 1,)
    return ".".join(str(_) for _ in v1)


def replace_version(code: str, match, new_v: str):
    v_start, v_end = match.regs[1]
    return code[:v_start] + new_v + code[v_end:]


# parse options
increment = True
write = True
for arg in sys.argv:
    if arg == "--no-increment":
        increment = False
    if arg == "--no-write":
        write = False

# determine version from setup.py
fn1 = "setup.py"
fn2 = "dslibrary/__init__.py"
ptn_version1 = re.compile(r'\n\s*version\s*=\s*"([\d.]+)",\s*\n')
ptn_version2 = re.compile(r'\n__version__\s*=\s*"([\d.]+)"\s*\n')
with open(fn1, "r") as f_r:
    code1 = f_r.read()
with open(fn2, "r") as f_r:
    code2 = f_r.read()
m1 = ptn_version1.search(code1)
if not m1:
    raise KeyError(f"Could not find version number in {fn1}")
old_version = m1.group(1)
m2 = ptn_version2.search(code2)
if not m2:
    raise KeyError(f"Could not find version number in {fn2}")
print(f"OLD VERSION: {old_version}")

# work out next version number
new_version = old_version
if increment:
    new_version = incr_version(old_version)
print(f"NEW VERSION: {new_version}")

# modify code
code1 = replace_version(code1, m1, new_version)
code2 = replace_version(code2, m2, new_version)
if write:
    with open(fn1, "w") as f_w:
        f_w.write(code1)
    with open(fn2, "w") as f_w:
        f_w.write(code2)

# remove old distribution files
if write:
    for fn in glob.glob("dist/*"):
        os.remove(fn)

# build
if write:
    subprocess.run([sys.executable, "setup.py", "sdist", "bdist_wheel"], check=True)

# upload
#  -- prompts for username and password
if write:
    print("UPLOADING... (PyPi username & password will be needed)")
    subprocess.run(["twine", "upload", "dist/*"])

exit(0)

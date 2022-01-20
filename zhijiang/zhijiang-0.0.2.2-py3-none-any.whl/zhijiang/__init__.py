import os
from termcolor import cprint
import fire
import zhijiang as pkg


pkg_installed_path = pkg.__path__[0]


def setup_rc_files(dry_run=True):
    """dry_run can be True or False"""
    assert isinstance(dry_run, bool), "dry_run should be a boolean, so its value can only by True or False"
    rc_files_path = os.path.join(pkg_installed_path, "data/rc_files")
    for root, dirs, files in os.walk(rc_files_path):
       for f in files:
          rc_file = os.path.join(root, f)
          dst = f"~/.{f}"
          if dry_run:
              print(f"copy {rc_file} to {dst}")
          else:
              os.system(f"sudo cp {rc_file} {dst}")


def info():
    """print help info"""
    cprint("if you want tab completion, please 'zhijiang -- --completion > ~/.zhijiang; echo source  ~/.zhijiang >> ~/.bashrc'", "red")
    cprint(f"there are many shell scripts in {os.path.join(pkg_installed_path, 'scripts')}, you could modify PATH to make them as command shell command", "red")


def main():
    fire.Fire({
               "setup_rc_files": setup_rc_files,
               "info": info
              })


if __name__ == "__main__":
    main()

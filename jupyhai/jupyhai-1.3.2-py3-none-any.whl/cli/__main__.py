import argparse
import platform
from typing import Optional

from notebook import nbextensions, serverextensions


def determine_symlink_mode(symlink_arg: Optional[str]) -> bool:
    if symlink_arg == 'yes':
        return True
    elif symlink_arg == 'no':
        return False
    # When in auto mode, use symlinks when not on Windows
    return platform.system() != 'Windows'


def main() -> None:
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='action')
    install_sp = sp.add_parser('install')
    install_sp.add_argument('--symlink', choices=('auto', 'yes', 'no'), default='auto')
    args = ap.parse_args()
    if args.action == 'install':
        symlink_mode = determine_symlink_mode(args.symlink)
        try:
            from jupyterlab import labextensions
            print("Installing Jupyhai lab extension...")
            labextensions.enable_extension('jupyhai')
            print("Jupyhai lab extension installed successfully.")
        except ImportError:
            pass  # No lab installed, that's ok!

        print(
            "Installing Jupyhai notebook extension ({using_symlinks})...".format(
                using_symlinks=(
                    "using symlinks" if symlink_mode else "without symlinks"
                ),
            )
        )
        serverextensions.toggle_serverextension_python('jupyhai', enabled=True)
        nbextensions.install_nbextension_python(
            'jupyhai', symlink=symlink_mode, user=True
        )
        nbextensions.enable_nbextension_python('jupyhai')
        print("Jupyhai notebook extension installed successfully.")
    else:
        print("Use 'jupyhai install' to install the notebook extension.")


if __name__ == "__main__":
    main()

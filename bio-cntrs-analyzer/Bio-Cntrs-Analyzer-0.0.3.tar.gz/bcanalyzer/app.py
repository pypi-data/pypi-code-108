
import sys
import os
import argparse
import ctypes
import logging
from bcanalyzer.common.const import APP_NAME
from bcanalyzer.gui.controllers.main_controller import MainController


def main():
    if os.name == 'nt':
        myappid = 'digiratory.bcanalyzer_app'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    """Application entry point"""
    parser = argparse.ArgumentParser(description="Microscopy image analyzer")

    try:
        MainController().run()
    except Exception as e:
        logging.exception(str(e))


if __name__ == "__main__":
    main()

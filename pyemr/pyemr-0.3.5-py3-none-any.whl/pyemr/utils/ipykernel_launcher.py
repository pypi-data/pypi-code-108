"""Entry point for launching an IPython kernel with s3 mocking."""
import sys


if __name__ == "__main__":
    sys.path += sys.argv[1].split(",")
    from pyemr.utils.poetry import set_spark_home

    set_spark_home()
    from pyemr.utils.mocking import launch_kernelapp

    if sys.path[0] == "":
        del sys.path[0]

    launch_kernelapp()

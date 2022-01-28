import os
import sys
import time
from pprint import pprint

from libreflow.session import BaseCLISession


def main(args):
    runner = args[0]
    oid = args[1]
    function_name = args[2]
    session = BaseCLISession(
        session_name="%s(pid=%i)" % (
            runner, os.getpid()
        ),
        debug=True,
    )
    
    session.cmds.Cluster.connect_from_env()
    session.cmds.Flow.call(oid, function_name, args={}, kwargs={})
    session.close()


if __name__ == "__main__":
    main(sys.argv[1:])

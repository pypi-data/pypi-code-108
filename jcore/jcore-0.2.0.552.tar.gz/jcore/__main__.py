import jcore
import platform
import asyncio
import sys


def show_version():
    entries = []

    entries.append('- Python v{0.major}.{0.minor}.{0.micro}-{0.releaselevel}'.format(sys.version_info))
    version_info = jcore.version_info
    entries.append('- jarviscore v{0.major}.{0.minor}.{0.micro}-{0.releaselevel}'.format(version_info))
    
    entries.append('- asyncio v{0.__version__}'.format(asyncio))
    uname = platform.uname()
    entries.append('- system info: {0.system} {0.release} {0.version}'.format(uname))
    print('\n'.join(entries))

def core(parser, args):
    if args.version:
        show_version()
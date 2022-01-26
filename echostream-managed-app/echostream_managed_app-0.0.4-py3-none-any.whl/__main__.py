import aiorun

from . import main

if __name__ == "__main__":
    aiorun.run(main(), stop_on_unhandled_errors=True, use_uvloop=True)

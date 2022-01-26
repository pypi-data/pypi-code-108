#!/usr/bin/env python3
"""
sleeep is a better sleep

LICENSE
   MIT (https://mit-license.org/)

COPYRIGHT
   © 2022 Steffen Brinkmann <s-b@mailbox.org>
"""

import argparse
import os
import sys
from queue import Empty, Queue
from threading import Event, Thread
from time import localtime, sleep, strftime, time

from sleeep import LolCat, __version__, bar, nonblocking, raw, styles


def _parse_arguments(argv=None):
    """parse the command line options"""
    parser = argparse.ArgumentParser(
        description="""A better sleep.
Use as a drop in replacement for sleep.
""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "time",
        type=str,
        help="The time to sleep, e.g. '1800s', '1800', '30m', '0.5h', '.0208333d' "
        "(these all translate to half an hour).",
    )
    parser.add_argument(
        "-s",
        "--style",
        type=str,
        default="blocks",
        help=f"The style of the bar. One of {', '.join(styles.keys())}",
    )
    parser.add_argument(
        "-f",
        "--frequency",
        type=float,
        default=30,
        help="The update frequency of the bar in frames per second.",
    )
    parser.add_argument(
        "-w",
        "--width",
        type=int,
        help="The width of the bar including the information. "
        "If omitted, the bar will fill the terminal width.",
    )
    parser.add_argument(
        "-t",
        "--transient",
        action="store_true",
        help="Delete the progress bar after completion.",
    )
    parser.add_argument(
        "-n",
        "--no-color",
        action="store_true",
        help="Switch off colorful display.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the version of this software",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Switch off text output except for error messages. This will overwrite -v.",
    )
    return parser.parse_args(argv)


def check_term(c: str) -> int | None:
    """Check whether the program should be terminated.
    Return None if unrecognized character
    Return the status code otherwise
    """
    # print(f"|{c}|")
    if c in ["q", "Q"]:
        print("\nSleeep was interrupted by pressing 'q'")
        return 2
    if c in ["f", "F"]:
        print("\nSleeep was fast-forwarded by pressing 'f'")
        return 0
    return None


def keyboard_listener(q: Queue, e: Event):
    """Listen to keyboard input"""
    with raw(sys.stdin), nonblocking(sys.stdin):
        while not e.is_set():
            try:
                c = sys.stdin.read(1)
                if c:  # pragma: no cover
                    q.put(c)
            except IOError:  # pragma: no cover
                print("not ready")
            sleep(0.1)


def get_bar_width(args: argparse.Namespace, leave_space: int = 0) -> int:
    """Get the desired bar width"""
    if args.width:
        terminal_w = args.width
    else:
        try:
            terminal_w = os.get_terminal_size()[0]
        except OSError:  # pragma: no cover
            terminal_w = 80
    w = terminal_w - leave_space
    return w


def get_time(args_time: str) -> float:
    """get the time in seconds from an args string like "24h" or 2d"""

    if args_time[-1] == "s":
        return float(args_time[:-1])
    elif args_time[-1] == "m":
        return float(args_time[:-1]) * 60
    elif args_time[-1] == "h":
        return float(args_time[:-1]) * 3600
    elif args_time[-1] == "d":
        return float(args_time[:-1]) * 86400

    return float(args_time)


def output(q: Queue, args: argparse.Namespace):
    """Print the progress bar and information"""

    t_start = time()
    t = get_time(args.time)
    t_goal = t_start + t

    w = old_w = get_bar_width(args, 32)
    lc = LolCat(spread=w / 60)

    while True:
        try:
            w = get_bar_width(args, 32)
            if w != old_w:  # pragma: no cover
                sleep(0.5)
                w = get_bar_width(args, 32)
                lc = LolCat(spread=w / 60)
                old_w = w

            now = time() + 0.01
            if w <= 0:
                if now >= t_goal:
                    break
                continue

            offset = -(now - t_start) / t * w - 13
            rem_h = max((t_goal - now), 0) // 3600
            rem_m = max((t_goal - now), 0) // 60 - rem_h * 60
            rem_s = int(max((t_goal - now), 0)) % 60
            if now >= t_goal:
                if not args.quiet:
                    if args.transient:
                        sys.stdout.write("\r\033[K")
                    else:
                        bar_str = f"{bar(1, w, args.style):<{w}}"
                        if not args.no_color:
                            bar_str = lc.get_str(bar_str, offset)
                        print(
                            "\r\033[K",
                            # f"{now - t_start:.2f}    |"
                            strftime("%H:%M:%S|", localtime(t_start)),
                            f"{(now - t_start) / t * 100:3.0f}%|",
                            bar_str,
                            f"|{rem_h:02.0f}:{rem_m:02.0f}:{rem_s:02.0f}",
                            strftime("|%H:%M:%S", localtime(t_goal)),
                            end="",
                            sep="",
                            flush=True,
                        )
                break
            try:  # pragma: no cover
                c = q.get(block=False)
                status = check_term(c)
                if status is not None:
                    return status
            except Empty:
                pass

            if not args.quiet:
                bar_str = f"{bar((now - t_start) / t, w, args.style):<{w}}"
                if not args.no_color:
                    bar_str = lc.get_str(bar_str, offset)
                print(
                    "\r\033[K",
                    # f"{now - t_start:5.2f}|{t_goal - now:5.2f}|"
                    strftime("%H:%M:%S|", localtime(t_start)),
                    f"{(now - t_start) / t * 100:3.0f}%|",
                    # lc.get_str(f"{bar((now - t_start) / t, w, args.style):<{w}}", -i),
                    bar_str,
                    f"|{rem_h:02.0f}:{rem_m:02.0f}:{rem_s:02.0f}",
                    strftime("|%H:%M:%S", localtime(t_goal)),
                    end="",
                    sep="",
                    flush=True,
                )
            sleep(1 / args.frequency)
        except Exception as e:  # pragma: no cover
            print("An error ocurred: ", e)


def run(argv: list = None):
    """The command line tool. Please use the ``--help`` option to get help."""

    # switch off blinking cursor
    sys.stdout.write("\x1b[?25l")

    # parse the command line options
    args = _parse_arguments(argv)
    # print(args)

    # Create the shared queue, the termination event and the communication thread
    term_event = Event()
    q: Queue = Queue()
    comm = Thread(target=keyboard_listener, args=(q, term_event))

    try:
        # start the communication thread and the output
        comm.start()
        status = output(q, args)
    except KeyboardInterrupt:  # pragma: no cover
        sys.stderr.write("\nSleeep was stopped by a keyboard interrupt (Ctrl-C).\n")
        status = 120
    except Exception as e:  # pragma: no cover
        raise e
    finally:
        # switch on blinking cursor
        sys.stdout.write("\x1b[?25h")

        # Reset colours
        # LolCat().reset()
        sys.stdout.write("\x1b[0m")

        # notify the keyboard listener
        term_event.set()
        return status


if __name__ == "__main__":
    sys.exit(run() or 0)

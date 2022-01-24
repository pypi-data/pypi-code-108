import threading
import time
from queue import Queue
from typing import Callable


class ThreadPool:
    def __init__(self, threads: int = 8):
        self.queue = Queue()
        self.threads = threads
        self.total_tasks = 0
        self.start_at = 0

    def add_task(self, data):
        self.total_tasks = self.total_tasks + 1
        self.queue.put(data)

    def start(self, worker: Callable):
        self.start_at = time.time()
        for i in range(self.threads):
            threading.Thread(target=worker, args=(self.queue,), daemon=True).start()

    def get_process_time(self):
        process_time = int(time.time() - self.start_at)
        second = process_time % 60
        minute = process_time // 60
        return f"{minute}:{second:02d}"

    def print_progress(self, formatter: str, remain: int):
        format_args = dict()
        format_args["time"] = self.get_process_time()
        format_args["total"] = self.total_tasks
        format_args["remain"] = remain
        format_args["finished"] = format_args["total"] - format_args["remain"]
        format_args["pct_float"] = format_args["finished"] / format_args["total"]
        format_args["pct"] = f"{format_args['pct_float']:.1%}"
        format_args["bar"] = f"[{'=' * int(format_args['pct_float'] * 20 - 1) + '>':<20}]"
        print(formatter.format(**format_args), " " * 8, end="\r", flush=True)

    def wait_complete(self, formatter: str, end_text: str = "任务完成"):
        self.print_progress(formatter, self.total_tasks)
        while not self.queue.empty():
            self.print_progress(formatter, self.queue.qsize())
            time.sleep(1)
        self.queue.join()
        self.print_progress(formatter, 0)
        print("\n" + end_text)

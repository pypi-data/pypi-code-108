#!/usr/bin/env python

import sys, time
from datetime import timedelta

__author__      = 'Luca Baronti'
__maintainer__  = 'Luca Baronti'
__license__     = 'MIT'
__version__     = '1.0.3'

class Stopwatch(object):
  def __init__(self, task_name='', verbosity=2, streams=[sys.stdout]):
    self.start_time = None
    self.streams = streams
    self.task_name = task_name
    self.verbosity = verbosity
    self.__enter__()

  def __str__(self):
    return str(Stopwatch.time_from_seconds(self.get_elapsed_time()))

  def _print_on_streams(self, message):
    for strm in self.streams:
      strm.write(message)

  def reset_time(self):
    self.start_time = time.time()

  def get_elapsed_time(self):
    return time.time() - self.start_time

  def print_elapsed_time(self):
    if self.verbosity>=2:
      if self.task_name!='':
        self._print_on_streams(f"{self.task_name} complete. ")
      self._print_on_streams(f"Elapsed time {Stopwatch.time_from_seconds(self.get_elapsed_time())}\n")
    else:
      self._print_on_streams(f"{Stopwatch.time_from_seconds(self.get_elapsed_time())}\n")

  def time_from_seconds(seconds):
    return timedelta(seconds=seconds)

  def __enter__(self):
    self.reset_time()

  def __exit__(self, exc_type, exc_val, exc_tb):
    if self.verbosity>=1:
      self.print_elapsed_time()

"""Defines functionality for scheduling periodic scans for serialzied protos."""

import threading

from masterful_gui.backend.apps.api import policy_search_task_scanner

# Interval for periodic scanning.
_INTERVAL_SEC = 60.0


def schedule_scan(reschedule: bool, interval: float = _INTERVAL_SEC) -> None:
  """Schedules a scan for serialized protos.

  Args:
    reschedule: Whether to reschedule a new scan upon execution.
    interval: The duration in seconds.    
  """
  kwargs = dict(reschedule=reschedule)
  timer = threading.Timer(interval, _scan, None, kwargs)
  timer.start()
  return


def _scan(reschedule: bool) -> None:
  """Scans for serialized protos.
  
  Args:
    reschedule: Whether to reschedule a scan upon execution.
  """
  try:
    policy_search_task_scanner.scan()
  except Exception as e:
    print(f'Scanning for serialized protos failed: {str(e)}')

  print("Scanning for serialized protos completed.")

  if reschedule:
    schedule_scan(reschedule)
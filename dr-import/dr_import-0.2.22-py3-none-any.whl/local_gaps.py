#!/usr/bin/python3

import argparse
import datetime
from dateutil.parser import parse
import os

import lzma
import pytz
import tqdm
import math
import ipaddress
import subprocess
import json

from collections import defaultdict

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('directory')
  parser.add_argument("--threshold-mins", default=2, type=int)
  args = parser.parse_args()

  
  by_camera=defaultdict(lambda:[])
  for root, dirs, files in os.walk(args.directory):
    for folder in dirs:
      camera = os.path.basename(root)
      try:
        check = ipaddress.ip_address(camera)
      except:
        continue
      print(f'Processing {camera}/{folder}')
      start_time = parse(folder.replace('_',':'))
      path = os.path.join(root, folder, "720.mp4")
      try:
        proc = subprocess.run(f"ffprobe -v error -print_format json -show_entries stream -select_streams v:0 {path}".split(' '),
                              stdout=subprocess.PIPE)

        value = json.loads(proc.stdout)['streams'][0]
        seconds = float(value.get('duration'))
        end_time = start_time+datetime.timedelta(seconds=seconds)
        by_camera[camera].append((start_time,end_time))
      except Exception as e:
        print(f"Skipping incomplete file... {e}")
        continue
  print("")
  print("")
  for camera, valid_times in by_camera.items():
    print(f"Results for {camera}")
    # Process valid_times for gaps
    valid_times.sort(key=lambda e: e[0])
    print(f"\tStarted at {valid_times[0][0]}")
    print(f"\tFinished at {valid_times[-1][1]}")
    for idx,time in enumerate(valid_times):
      if idx+1 == len(valid_times):
        continue
      next_time = valid_times[idx+1][0]
      delta = next_time - time[1]
      if delta > datetime.timedelta(minutes=args.threshold_mins):
        print(f"\tGap between {time[1]} and {next_time} ({delta})")

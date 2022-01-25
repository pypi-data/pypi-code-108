#!/usr/bin/python3

import argparse
import datetime
from dateutil.parser import parse
import os

import pynmea2
import lzma
import pytz
import tqdm
import math

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('directory')
  args = parser.parse_args()

  all_files = os.listdir(args.directory)
  def is_gps_file(x):
    return x.startswith('gps') or x.startswith('aux_gps')
  gps_files = [x for x in all_files if is_gps_file(x)]
  print(gps_files)
  gps_data_raw=[]
  print(f"Processing {len(gps_files)} GPS files")
  for gps_file in gps_files:
    gps_file = os.path.join(args.directory, gps_file)
    try:
      # fix the data by forcing the file to have the
      # end of stream marker
      with lzma.open(gps_file,'a') as fp:
        fp.write(b'')
      with lzma.open(gps_file, 'r') as fp:
        lines = fp.readlines()
        gps_data_raw.extend(lines)
    except Exception as e:
      print(f"Unable to process {gps_file} {e}")
      print(f"msgs={len(gps_data_raw)}")

  states = []
  total_media_ids = set()
  total_medias = []

  valid_times = []
  def process_message(msg):
    try:
      date = datetime.datetime.combine(msg['rmc'].datestamp,
                                       msg['rmc'].timestamp)
    except:
      return
    date = pytz.utc.localize(date)

    seconds = int(date.timestamp())

    # Reduce the amount of states, 1 per minute
    if round(seconds) % 60 != 0:
      return

    if int(msg['gga'].num_sats) > 0:
      valid_times.append(date)

  print(f"Imported {len(gps_data_raw)} NMEA messages")
  #gps_data_raw=gps_data_raw[:4]
  latest_msg = {"gga": False,
                "rmc": False}
  for raw_gps in tqdm.tqdm(gps_data_raw):
    try:
      msg = pynmea2.parse(raw_gps.decode())
    except:
      # File boundary
      latest_msg = {"gga": False,
                    "rmc": False}
      continue
    msg_type = msg.sentence_type
    if msg_type == 'GGA':
      latest_msg['gga'] = msg
    elif msg_type == 'RMC':
      latest_msg['rmc'] = msg
    if latest_msg['gga'] and latest_msg['rmc']:
      process_message(latest_msg)
      # reset state machine
      latest_msg = {"gga": False,
                    "rmc": False}


  # Process valid_times for gaps
  valid_times.sort()
  print(f"Started at {valid_times[0]}")
  print(f"Finished at {valid_times[-1]}")
  print(f"Total messages/minutes: {len(valid_times)}")
  for idx,time in enumerate(valid_times):
    if idx+1 == len(valid_times):
      continue
    next_time = valid_times[idx+1]
    delta = next_time - time
    if delta > datetime.timedelta(minutes=2):
      print(f"Gap between {time} and {next_time} ({delta})")

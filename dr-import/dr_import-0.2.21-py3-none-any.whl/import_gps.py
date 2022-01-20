#!/usr/bin/python3

import argparse
import datetime
from dateutil.parser import parse
import os
import tator

import pynmea2
import lzma
import pytz
import tqdm
import math

from collections import defaultdict

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--host', type=str, default='https://www.tatorapp.com')
  parser.add_argument('--token', type=str, required=True)
  parser.add_argument('--type-id', type=int, required=True)
  parser.add_argument('--multi-media-type-id', type=int, help="Use this by itself to search for multi-medias and look at the files it points to")
  parser.add_argument('--section-id', type=int, help="Used in conjunction with multi-media-type-id")
  parser.add_argument('--trip-id', type=str, help="Supersedes mult-media-type-id ")
  parser.add_argument('--media-type-id', type=str, help="Used in conjunction with trip-id. Video media dtype.")
  parser.add_argument('--dry-run', action="store_true", help="Don't apply GPS states to media")
  parser.add_argument('directory')
  args = parser.parse_args()

  api = tator.get_api(args.host, args.token)
  type_obj = api.get_state_type(args.type_id)
  project = type_obj.project

  if args.trip_id:
    process_list = api.get_media_list(project,
                                      type=args.media_type_id,
                                      search=f"Trip:\"{args.trip_id}\"")

  else:
    section = api.get_section(id=args.section_id)
    multis = api.get_media_list(project=project, type=args.multi_media_type_id, section=section.id)

    process_list = []
    for multi in multis:
      for single in multi.media_files.ids:
          process_list.append(api.get_media(single))

  print(f"Generating time map for {len(process_list)} media elements")
  time_map = []
  utc = pytz.timezone('Etc/UTC')
  for media in process_list:
    if media.fps is None:
      continue
    # Load file name as UTC date time
    date_str = os.path.splitext(media.name)[0]
    start = parse(date_str.replace('_',':'))
    start = utc.localize(start)
    seconds = media.num_frames / media.fps
    end = start+datetime.timedelta(seconds=seconds)
    #print(f"{start} to {end} ({seconds}s)")
    time_map.append({"start": start,
                     "end": end,
                     "media": media})
    print(f"{media.id} {media.name}: {start} {end}")


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
      with lzma.open(gps_file) as fp:
        lines = fp.readlines()
        gps_data_raw.extend(lines)
    except Exception as e:
      print(f"Unable to process {gps_file} {e}")

  total_media_ids = set()
  total_medias = []

  msg_count = 0
  pending_states = defaultdict(lambda: [])
  def associate_to_media(msg):
    global msg_count
    try:
      date = datetime.datetime.combine(msg['rmc'].datestamp,
                                       msg['rmc'].timestamp)
    except:
      print(f"Couldn't parse date {msg['rmc']}")
      return
    date = utc.localize(date)
    start_lookup = defaultdict(lambda:[])
    for media in time_map:
      if date >= media['start'] and date <= media['end']:
        if media['media'].id not in total_media_ids:
          total_medias.append(media['media'])
        total_media_ids.add(media['media'].id)
        start_lookup[media['start']].append(media['media'])

    if len(start_lookup) == 0:
      return
    
    for start, matching_media in start_lookup.items():
      seconds = (date-start).total_seconds()

      # Reduce the amount of states, 1 per minute
      if round(seconds) % 60 != 0:
        continue

      # Debounce from Aux/Primary GPS
      # If there's a matching datetime or a datetime within 5 seconds of the existing value,
      # pick the GPS with the highest satellite count.
      datetime_key = round(date.timestamp())
      nearest_date = None
      for pending_states_date in pending_states:
        if abs(pending_states_date - datetime_key) < 6:
          if pending_states[pending_states_date][0]["Satellite Count"] > int(msg['gga'].num_sats):
            continue
          else:
            nearest_date = pending_states_date
            break

      if nearest_date is not None:
        del pending_states[nearest_date]

      seconds = (date-start).total_seconds()
      frame = int(round(seconds * matching_media[0].fps))
      try:
        geopos = [msg['gga'].longitude,
                  msg['gga'].latitude]
      except:
        continue
      knots = 0.0
      heading = 0.0

      if msg['rmc'].spd_over_grnd:
        knots = msg['rmc'].spd_over_grnd
      if msg['rmc'].true_course:
        heading = msg['rmc'].true_course

      attributes={"Satellite Count": int(msg['gga'].num_sats),
                  "Datecode": date.isoformat(),
                  "Position": geopos,
                  "Knots": knots,
                  "Heading": heading}
      # make state object
      state={'frame':frame,
            'media_ids':[x.id for x in matching_media],
            'project': project,
            'type': args.type_id,
            **attributes}
      pending_states[datetime_key].append(state)

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
      associate_to_media(latest_msg)
      # reset state machine
      latest_msg = {"gga": False,
                    "rmc": False}

  states = []
  for key,pstates in pending_states.items():
    states.extend(pstates)
  print(f"{len(states)} states to import to {len(total_media_ids)} medias")
  for media in total_medias:
    print(media.name)

  if not args.dry_run:

    total_media_ids=list(total_media_ids)
    chunk_size = 20
    chunks = math.ceil(len(total_media_ids)/chunk_size)
    print("Deleting any old gps data.")
    for x in tqdm.tqdm(total_media_ids):
      existing=api.get_state_list(project,media_id=[x],
                                  type=args.type_id)
      if len(existing) > 0:
        print(f"Found {len(existing)} on media.. clearing out first.")
        api.delete_state_list(project,media_id=[x],
                              type=args.type_id)

    print("Uploading new data")
    created_ids = []
    total=math.ceil(len(states)/500)
    print(total)

    for response in tqdm.tqdm(tator.util.chunked_create(api.create_state_list,
                                                        project,
                                                        state_spec=states),
                              total=total):
      created_ids.extend(response.id)

    print(f"{len(created_ids)} imported.")

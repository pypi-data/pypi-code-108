#!/usr/bin/python3

import argparse
import datetime
from dateutil.parser import parse
import os
import tator
import pandas as pd

import pynmea2
import lzma
import pytz
import tqdm
import math

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--host', type=str, default='https://www.tatorapp.com')
  parser.add_argument('--token', type=str, required=True)
  parser.add_argument('--type-id', type=int, required=True)
  parser.add_argument('--multi-media-type-id', type=int, help="Use this by itself to search for multi-medias and look at the files it points to")
  parser.add_argument('--section-id', type=int, help="Used in conjunction with multi-media-type-id")
  parser.add_argument('--media-type-id', type=str, help="Used in conjunction with trip-id. Video media dtype.")
  parser.add_argument('--dry-run', action="store_true", help="Don't apply GPS states to media")
  parser.add_argument('input_file')
  args = parser.parse_args()

  trip_id = os.path.splitext(args.input_file)[0].split('_')[1]
  print(f"Processing {trip_id}")


  api = tator.get_api(args.host, args.token)
  type_obj = api.get_state_type(args.type_id)
  project = type_obj.project

  process_list = api.get_media_list(project,
                                      type=args.media_type_id,
                                      search=f"Trip:\"{trip_id}\"")

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


  total_media_ids = set()
  total_medias = []
  states=[]
  msg_count = 0
  def associate_to_media(msg):
    global msg_count
    date = msg['datetime']
    matching_media = []
    start = None
    for media in time_map:
      if date >= media['start'] and date <= media['end']:
        matching_media.append(media['media'])
        if media['media'].id not in total_media_ids:
          total_medias.append(media['media'])
        total_media_ids.add(media['media'].id)
        if start is None:
          start = media['start']

    if len(matching_media) == 0:
      return
    
    media_ids = [x.id for x in matching_media]
    seconds = (date-start).total_seconds()

    frame = int(round(seconds * matching_media[0].fps))

    geopos = [msg['Longitude'],
              msg['Latitude']]

    knots = msg['Knots']
    if msg['Heading'] != ' ':
      heading = float(msg['Heading'])
    else:
      heading = None

    attributes={"Satellite Count": msg['NumSats'],
                "Datecode": date.isoformat(),
                "Position": geopos,
                "Knots": float(knots)}
    if heading:
      attributes.update({"Heading": heading})
    # make state object
    state={'frame':frame,
           'media_ids':media_ids,
           'project': project,
           'type': args.type_id,
           **attributes}
    states.append(state)

  
  df = pd.read_csv(args.input_file, index_col=False,header=0,names=["Date","Time", "Latitude", "Longitude", "Knots", "Heading", "Fix", "NumSats","Blank"])
  for idx, msg in df.iterrows():
    d = [int(x) for x in msg['Date'].split('/')]
    t = [int(x) for x in msg['Time'].split(':')]
    msg['datetime'] = utc.localize(datetime.datetime(year=d[2], month=d[0], day=d[1], hour=t[0], minute=t[1], second=t[2]))
    degrees = float(msg['Latitude'].split()[0][:2])
    minutes = float(msg['Latitude'].split()[0][2:])/60.0
    msg['Latitude'] = degrees+minutes
    degrees = float(msg['Longitude'].split()[0][:3])
    minutes = float(msg['Longitude'].split()[0][3:])/60.0
    msg['Longitude'] = 0.0 - (degrees+minutes)
    associate_to_media(msg)

  print(f"{len(states)} states to import to {len(total_media_ids)} medias")

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

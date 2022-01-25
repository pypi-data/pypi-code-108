#!/usr/bin/python3

import argparse
import tator
from collections import defaultdict
from dateutil.parser import parse
import os
from pprint import pprint
import datetime
import tqdm
import uuid
import math
import multiprocessing
import time

if __name__=="__main__":
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--host', type=str,default='https://www.tatorapp.com')
  parser.add_argument('--token', type=str,required=True)
  parser.add_argument('--multi-type-id', type=int, required=True)
  parser.add_argument('--quality', default=360, type=int)
  parser.add_argument('--trip-id', required=True)
  parser.add_argument('--dest-trip-id', required=True)
  parser.add_argument('--tolerance', default=1, type=int)
  parser.add_argument('--layout', default='2x2',type=str)
  parser.add_argument('--dry-run', action='store_true')
  parser.add_argument('--sort-by', default='Camera', type=str)
  parser.add_argument('--enforce-match', action='store_true')
  parser.add_argument('--parallel', default=4, type=int)
  args = parser.parse_args()

  api = tator.get_api(args.host, args.token)

  media_type = api.get_media_type(args.multi_type_id)
  project = media_type.project

  # e.g. 2x2 into [2,2]
  layout = [int(x) for x in args.layout.split('x')]

  media_list = api.get_media_list(project, search=f"Trip:\"{args.trip_id}\"")

  media_ids = [x.id for x in media_list]

  print(len(media_ids))
  # First step is clone existing media elements
  clone_ids = []
  generator = tator.util.clone_media_list(api,
                                          {'project': project,
                                           'media_id':media_ids},
                                           dest_section=f"Single View {args.dest_trip_id}",
                                           dest_project=project)
  for _,_,response,_ in generator:
    print(response.id)
    clone_ids += response.id
    
  print(clone_ids)
  print("Sleeping...")
  time.sleep(20)
  api.update_media_list(project, {"attributes": {"Trip": args.dest_trip_id}}, media_id=clone_ids)

  # Use clones to make trip
  media_list = api.get_media_list(project,media_id=clone_ids)
                                          
  time_joined=defaultdict(lambda:[])
  print(f"Processing {len(media_list)} media files")
  for media in tqdm.tqdm(media_list):
    try:
      video_start_str=os.path.splitext(media.name)[0].replace('_',':')
      date = parse(video_start_str)
    except:
      print(f"Bad Date {media.attributes.get('Date',None)}")
      continue
    # Round to the nearest whole second
    video_start = parse(video_start_str)
    seconds = int(datetime.datetime.timestamp(video_start))
    video_start = datetime.datetime.fromtimestamp(seconds)
    if len(time_joined) == 0:
      time_joined[video_start].append(media)
    else:
      existing_times = [x for x in time_joined.keys()]
      closest_match = None
      for x in existing_times:
        if abs(x-video_start) <= datetime.timedelta(seconds=args.tolerance):
          closest_match = x
          break

      if closest_match is None:
        time_joined[video_start].append(media)
      else:
        time_joined[closest_match].append(media)

  print("Linking up")

  def process_row(process_row):
    linked_count = 0
    name,medias = process_row
    # Sort by IP address
    medias.sort(key=lambda x:x.attributes[args.sort_by])
    media_ids = [x.id for x in medias]
    if args.enforce_match and len(medias) != layout[0]*layout[1]:
      print(f"Skipping non-matched video {name} / {media_ids}")
      return 0
    linked_count += len(medias)
    if args.dry_run == True:
      print(f"Would have made multi for {media_ids} for {name}")
    else:
      print(f"Making multi for {name} of {media_ids}")
      tator.util.make_multi_stream(api,
                                   args.multi_type_id,
                                   layout,
                                   name.isoformat(),
                                   media_ids,
                                   section=args.dest_trip_id,
                                   quality=args.quality)
    return linked_count


  linked_count = 0
  if args.parallel == 1:
    for row in time_joined.items():
      linked_count += process_row(row)
  else:
    pool = multiprocessing.Pool(processes=args.parallel)
    work_queue = [x for x in time_joined.items()]
    print(type(work_queue))
    linked_counts = pool.map(process_row, work_queue)
    for count in linked_counts:
      linked_count += count

  print("Link Stats:")
  print(f"Total scanned media: {len(media_list)}")
  print(f"Matched media: {linked_count}")

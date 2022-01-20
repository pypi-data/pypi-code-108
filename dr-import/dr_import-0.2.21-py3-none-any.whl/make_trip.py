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
import traceback

if __name__=="__main__":
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--host', type=str,default='https://www.tatorapp.com')
  parser.add_argument('--token', type=str,required=True)
  parser.add_argument('--multi-type-id', type=int, required=True)
  parser.add_argument('--quality', default=360, type=int)
  parser.add_argument('--trip-id', required=True)
  parser.add_argument('--tolerance', default=1, type=int)
  parser.add_argument('--layout', default='2x2',type=str)
  parser.add_argument('--dry-run', action='store_true')
  parser.add_argument('--sort-by', default='Camera', type=str)
  parser.add_argument('--enforce-match', action='store_true')
  parser.add_argument('--parallel', default=1, type=int)
  parser.add_argument('--image-type-id', type=int, default=58)
  parser.add_argument('--no-summary-image', action='store_true')
  args = parser.parse_args()

  api = tator.get_api(args.host, args.token)

  media_type = api.get_media_type(args.multi_type_id)
  project = media_type.project

  # e.g. 2x2 into [2,2]
  layout = [int(x) for x in args.layout.split('x')]

  media_list = api.get_media_list(project, search=f"Trip:\"{args.trip_id}\"")
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
    video_start = video_start.replace(microsecond=0)
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
      existing = api.get_media_list(project,
                                    type=args.multi_type_id,
                                    name=f"{name.isoformat()}.multi")
      if existing:
        sections = api.get_section_list(project,
                                        name=args.trip_id)
        if sections:
          existing = api.get_media_list(project,
                                        type=args.multi_type_id,
                                        section=sections[0].id,
                                        name=f"{name.isoformat()}.multi")
          if existing:
            print(f"Found existing for '{name.isoformat()}'")
            return 0
      try:
        print(f"Making multi for {name} of {media_ids}")
        tator.util.make_multi_stream(api,
                                     args.multi_type_id,
                                     layout,
                                     name.isoformat(),
                                     media_ids,
                                     section=args.trip_id,
                                     quality=args.quality)
      except Exception as e:
        print(f"Warning: {e} on '{name.isoformat()}'")
        traceback.print_exc()
        sections = api.get_section_list(project,
                                        name=args.trip_id)
        existing = api.get_media_list(project,
                                      type=args.multi_type_id,
                                      section=sections[0].id,
                                      name=f"{name.isoformat()}.multi")
        if not existing:
            print(f"ERROR: Failed to make '{name.isoformat()}'")
            return 0
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

  if not args.no_summary_image:
    try:
      # Fetch the section UUID to place the trip image into
      sections = api.get_section_list(project, name=args.trip_id)
      tator_user_sections = sections[0].tator_user_sections

      # Upload the trip image
      summary_image = os.path.join(os.path.dirname(__file__),
                                  "trip_summary.png")
      for progress, response in tator.util.upload_media(
          api=api,
          type_id=args.image_type_id,
          fname="00_trip_summary.png",
          path=summary_image):
        continue
      summary_image_id = response.id

      summary_media = api.get_media(summary_image_id)
      media_update_spec = {"attributes": summary_media.attributes}
      media_update_spec["attributes"]["tator_user_sections"] = tator_user_sections
      response = api.update_media(id=summary_image_id, media_update=media_update_spec)
      print("Uploaded trip summary image (trip_summary.png)")
    except Exception as e:
      print(f"Error: {e}: Could not Upload trip_summary.png")

  print("Link Stats:")
  print(f"Total scanned media: {len(media_list)}")
  print(f"Matched media: {linked_count}")

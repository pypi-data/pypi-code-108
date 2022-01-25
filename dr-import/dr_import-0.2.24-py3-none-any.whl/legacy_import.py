#!/usr/bin/python3

import argparse

import boto3
import tator
import sys
import os
import zipfile
import datetime
import pytz
from pprint import pprint

from collections import defaultdict
import tempfile

import time
import uuid
import pandas as pd
import tqdm
import math

if __name__=="__main__":
  parser = argparse.ArgumentParser(__doc__)
  parser.add_argument("--bucket", default="im-to-nemm-transfer", type=str)
  parser.add_argument("--evtr-id", type=str, required=True,
                      help="EVTR number to use for trip id")
  parser.add_argument("--object-name", type=str, required=True,
                      help="Name of zip file, excluding extension")
  parser.add_argument("--media-type", type=int,
                      help="Type id for media import",
                      required=True)
  parser.add_argument("--gps-type", type=int,
                      help="Type id for gps import",
                      required=True)
  parser.add_argument("--fps", type=int,default=5)
  parser.add_argument("--media-length", type=int, default=60)
  parser.add_argument("--dry-run", action="store_true")
  parser = tator.get_parser(parser)
  args = parser.parse_args()

  if args.token is None:
    print("legacy_import.py: error: Must supply '--token'")
    parser.print_help()
    sys.exit(255)

  s3 = boto3.client('s3')
  response = s3.list_buckets()
  names = [bucket['Name'] for bucket in response['Buckets']]
  print(f"Looking for bucket '{args.bucket}'")
  print("Available Buckets:")
  for bucket in names:
    print(f"\t- {bucket}")

  if args.bucket not in names:
    print(f"Couldn't find '{args.bucket}'")
    sys.exit(255)

  filename = f"{args.object_name}.zip"
  print(f"Name: {filename}")
  if not os.path.exists(filename):
    print("Downloading file, this may take some time.")
    # Download file locally
    s3.download_file(args.bucket, f"trips/{filename}", filename)
  else:
    print(f"Found '{filename}' locally")


  # Make time map
  zip_obj = zipfile.ZipFile(filename)
  contents = zip_obj.namelist()
  gps_file = None
  timemap=defaultdict(lambda: [])
  for name in contents:
    comps = os.path.splitext(name)
    if comps[1] == ".txt":
      gps_file = name
    elif comps[1] == ".mp4":
      time_str = comps[0].split('-')[-1]
      try:
        video_start = datetime.datetime.strptime(time_str, "%y%m%d_%H%M%S_000")
      except Exception as e:
        print(e)
        sys.exit(255)
      timemap[video_start].append(name)

  print(f"GPS = {gps_file}")

  pprint(timemap)
  # Upload to tator
  api = tator.get_api(token=args.token)

  gps_map=defaultdict(lambda: [])

  media_type = api.get_media_type(args.media_type)
  project = media_type.project

  gid = uuid.uuid4()
  for video_time in timemap.keys():
    print(f"Processing {video_time}")
    for video in timemap[video_time]:
      safe_name = video_time.isoformat().replace(':', '_')
      safe_name += ".mp4"
      comps = video.split('-')
      attributes = {"Camera": comps[1],
                    "Trip": args.evtr_id,
                    "Date": video_time.date().isoformat(),
                    "Time": video_time.time().isoformat()}
      media_id = None 
      existing = api.get_media_list(project,
                                    name=safe_name,
                                    attribute=[f"Trip::{args.evtr_id}",f"Camera::{comps[1]}"])
      if existing:
        print(f"{comps[1]}: Already uploaded to server ({existing[0].id})")
        media_id = existing[0].id
      elif args.dry_run:
        print(f"{comps[1]}: Not found on server, but dry-run is enabled")
      else:
        with tempfile.TemporaryDirectory() as td:
          print("")
          zip_obj.extract(video, td)
          for progress,response in tator.util.upload_media(api,
                                                           args.media_type,
                                                           os.path.join(td,video),
                                                           fname=safe_name,
                                                           attributes=attributes,
                                                           upload_gid=str(gid)):
            print(f"\r{comps[1]}:\t{progress}",end='')
          while media_id is None:
            time.sleep(1)
            print("Waiting for media_id...")
            media = api.get_media_list(project,
                                         uid=response.uid,
                                         gid=str(gid))
            if media:
              media_id = media[0].id
          print(f"\r{comps[1]}:\tComplete ({media[0].id})")

      gps_map[video_time].append(media_id)
        
  # Upload GPS
  gps_objects = []
  total_media_ids = set()
  with tempfile.TemporaryDirectory() as td:
    zip_obj.extract(gps_file, td)
    gps_data = pd.read_csv(os.path.join(td,gps_file))
    for _,data in gps_data.iterrows():
      try:
        date_obj = datetime.datetime.strptime(str(int(data['Date'])), "%y%m%d")
        time_obj = datetime.datetime.strptime(str(int(data['Time'])), "%H%M%S")
      except Exception as e:
        print(e)
        print(data)
      full_date = datetime.datetime.combine(date_obj,time_obj.time())
      obj={"Datecode": full_date.isoformat(),
           "Position": [data['Longitude'],data['Latitude']],
           "Knots": data['Speed'],
           "Heading": data['Heading'],
           "media_ids": [],
           "type": args.gps_type}

      media_length = datetime.timedelta(minutes=args.media_length)
      for media_start,ids in gps_map.items():
        delta = full_date - media_start
        if delta < media_length and delta > datetime.timedelta(0):
          total_media_ids.update(ids)
          obj['media_ids'] = ids
          obj['frame'] = int(delta.total_seconds() * args.fps)
      gps_objects.append(obj)

  if not args.dry_run:
    total_media_ids=list(total_media_ids)
    chunk_size = 20
    chunks = math.ceil(len(total_media_ids)/chunk_size)
    print("Deleting any old gps data.")
    for x in tqdm.tqdm(total_media_ids):
      existing=api.get_state_list(project,media_id=[x],
                                  type=args.gps_type)
      if existing:
        print(f"Found {len(existing)} on media.. clearing out first.")
        api.delete_state_list(project,media_id=[x],
                              type=args.gps_type)

    # trim out gps objects with no associated media
    print(f"Total of {len(gps_objects)}")
    gps_objects = [x for x in gps_objects if x['media_ids']]
    print(f"Importing {len(gps_objects)}")
    created_ids = []
    total=math.ceil(len(gps_objects)/500)
    print(total)
    
    for response in tqdm.tqdm(tator.util.chunked_create(api.create_state_list,
                                                        project,
                                                        state_spec=gps_objects),
                              total=total):
      created_ids.extend(response.id)
    
    print(f"{len(created_ids)} imported.")
  
  
  # Make the trip

  

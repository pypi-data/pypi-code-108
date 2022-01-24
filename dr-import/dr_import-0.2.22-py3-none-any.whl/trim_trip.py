#!/usr/bin/python3

import argparse
import tator
from collections import defaultdict
from dateutil.parser import parse
import os
from pprint import pprint
import datetime
import tqdm
import traceback

if __name__=="__main__":
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--host', type=str,default='https://www.tatorapp.com')
  parser.add_argument('--token', type=str,required=True)
  parser.add_argument('--trip-id', required=True)
  parser.add_argument('--type-id', required=True)
  parser.add_argument('--gap-tolerance', default=1.0, type=float)
  parser.add_argument('--dry-run', action='store_true')
  args = parser.parse_args()

  api = tator.get_api(args.host, args.token)

  media_type = api.get_media_type(args.type_id)
  project = media_type.project

  media_list = api.get_media_list(project,
                                  type=args.type_id,
                                  search=f"Trip:\"{args.trip_id}\"")

  by_camera=defaultdict(lambda:[])
  print(f"Processing {len(media_list)} media files")
  for media in tqdm.tqdm(media_list):
    length = media.num_frames / media.fps
    camera = media.attributes.get('Camera','Unknown')
    by_camera[camera].append(media)

  gaps=defaultdict(lambda:dict())
  print("Overage Analysis")
  for camera,medias in by_camera.items():
    medias.sort(key= lambda x: x.name)
    for idx,media in enumerate(medias):
      if idx != len(medias)-1:
        camera = media.attributes.get('Camera', 'Unknown')
        next_media = medias[idx+1]
        end_name = media.name
        end_start_time = os.path.splitext(end_name)[0].replace('_',':')
        end_start_time = parse(end_start_time)
        this_frames = media.attributes.get('_orig_num_frames',-1)
        if this_frames == -1:
          this_frames = media.num_frames
        end_length = datetime.timedelta(seconds=this_frames/next_media.fps)
        end_end_time = end_start_time + end_length
        this_start_time = os.path.splitext(next_media.name)[0].replace('_',':')
        this_start_time = parse(this_start_time)
        delta = this_start_time - end_end_time
        overage = delta.total_seconds() + args.gap_tolerance
        if overage < args.gap_tolerance:
          gaps[this_start_time][camera] = (media,overage)

  for time,gap in gaps.items():
    print(f"Overage in {time}")
    for camera,info in gap.items():
      print(f"\t{camera}\t{info[0].id}\t{info[1]}")
      this_frames = info[0].attributes.get('_orig_num_frames',-1)
      if this_frames == -1:
        this_frames = info[0].num_frames
      new_frames = round(this_frames + (info[1]*info[0].fps))
      new_length = new_frames / info[0].fps
      new_length = datetime.timedelta(seconds=new_length)
      msg = f"Triming {info[0].name} to {new_frames} from {this_frames}. New length = {new_length}"
      if not args.dry_run:
        print(msg)
        api.update_media(info[0].id, 
                         {"num_frames":new_frames, 
                          "attributes": {"_orig_num_frames": this_frames}
                         })
      else:
        print(f"Dry-run: {msg}")
        
      
  

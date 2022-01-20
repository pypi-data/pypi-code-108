#!/usr/bin/env python3

import argparse
import os
import subprocess
import tator
import tqdm
import tempfile

from tator.util._upload_file import _upload_file
from tator.transcode.make_thumbnails import make_thumbnails
from tator.transcode.transcode import make_video_definition
from tator.transcode.make_fragment_info import make_fragment_info
from tator.openapi.tator_openapi.models import CreateResponse

if __name__=="__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', type=str,default='https://www.tatorapp.com')
    parser.add_argument('--token', type=str)
    parser.add_argument('--type-id', type=int)
    parser.add_argument('--target-fps', type=int, default=15)
    parser.add_argument('--workflow-mode', action='store_true')
    parser.add_argument('media_id', type=int, nargs="*")
    args = parser.parse_args()

    if args.workflow_mode:
        api = tator.get_api("https://www.tatorapp.com",
                            os.getenv('TATOR_AUTH_TOKEN'))
    else:
        api = tator.get_api(args.host, args.token)

    if args.workflow_mode:
        # Infer arguments from workflow env
        media_ids_str = os.getenv('TATOR_MEDIA_IDS')
        media_ids = [int(m) for m in media_ids_str.split(',')]
        print(media_ids_str)
        print(media_ids)
        media_first = api.get_media(media_ids[0])
        media_type_id = media_first.meta
        media_type = api.get_media_type(media_type_id)
        project = os.getenv('TATOR_PROJECT_ID')
        media_list = api.get_media_list(project, type=args.type_id, media_id=media_ids)
    else:
        media_type = api.get_media_type(args.type_id)
        project = media_type.project
        media_list = api.get_media_list(project,
                                        type=args.type_id,
                                        media_id=args.media_id)

    work = media_list

    #print(f"Bad fps: {len(bad_fps)}")
    print(f"NeedsTranscode: {len(work)}")

    for video in tqdm.tqdm(work):
        with tempfile.TemporaryDirectory() as td:
            source_file = os.path.join(td, "source.mp4")
            print(f"Downloading {video.name}")
            for progress in tator.util.download_media(api, video, source_file):
                print(f"\r{progress}%",end='')

            for resolution in [144,360,720]:
                transcoded_file = os.path.join(td, f"{resolution}.mp4")
                segments_file = os.path.join(td, "segments_{resolution}.json")
                cmd = [
                    "ffmpeg", "-y",
                    "-i", source_file,
                    "-an",
                    "-metadata:s", "handler_name=tator",
                    "-g", "25",
                    "-preset", "fast",
                    "-movflags",
                    "faststart+frag_keyframe+empty_moov+default_base_moof",
                    "-tune", "fastdecode",
                    "-vcodec", "libx264",
                    "-crf", "28",
                    "-pix_fmt", "yuv420p",
                    "-vf", f"scale=-2:{resolution}",
                    transcoded_file
                ]

                subprocess.run(cmd)
                
                make_fragment_info(transcoded_file, segments_file)
                for _, upload_info in _upload_file(api, project, transcoded_file,
                                                   media_id=video.id,
                                                   filename=f"{resolution}_fastdecode.mp4"):
                    pass
                for _, segment_info in _upload_file(api, project, segments_file,
                                                    media_id=video.id,
                                                    filename=f"{resolution}_fastdecode.json"):
                    pass
                media_def = {**make_video_definition(transcoded_file),
                             'path': upload_info.key,
                             'segment_info': segment_info.key}
                response = api.create_video_file(video.id, role='streaming',
                                                 video_definition=media_def)

                media = api.get_media(video.id)
                # Delete old one if present
                if media.media_files:
                    streaming = media.media_files.streaming
                else:
                    streaming = []
                available = [x.resolution[0] for x in streaming]
                # If we have duplicate resolutions, delete the first one
                while available.count(resolution) >= 2:
                    print("Deleting duplicative resolution")
                    api.delete_video_file(video.id,role='streaming',
                                          index=available.index(resolution))
                    media = api.get_media(video.id)
                    # Delete old one if present
                    if media.media_files:
                        streaming = media.media_files.streaming
                    else:
                        streaming = []
                    available = [x.resolution[0] for x in streaming]


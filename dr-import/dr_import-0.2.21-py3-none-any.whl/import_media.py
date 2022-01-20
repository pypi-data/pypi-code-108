#!/usr/bin/python3

import os
from datetime import datetime,timedelta
from dateutil.parser import parse
import tempfile
import time
import uuid
import yaml
import subprocess

import tator
from tator.util._upload_file import _upload_file
from tator.transcode.make_thumbnails import make_thumbnails
from tator.transcode.transcode import make_video_definition
from tator.transcode.make_fragment_info import make_fragment_info
from tator.openapi.tator_openapi.models import CreateResponse
import pytz

def check_file_is_valid(path):
    proc = subprocess.run(f"ffprobe {path}".split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return proc.returncode == 0
def filenameToTime(path):
    """Assuming filename is {uuid}.ext convert to datetime """
    filename=os.path.basename(path)
    uuid_str=os.path.splitext(filename)[0].split('_')[-1]
    uid=uuid.UUID(uuid_str)
    date=datetime(1582, 10, 15) + timedelta(microseconds=uid.time//10)
    return date

def upload_path(api,project,full_path):
    """ Handles uploading either archival or streaming format """
    path = os.path.basename(full_path)
    file_type = os.path.splitext(path)[0]
    if file_type == "archival":
        if args.skip_archival is True:
            return True
        filename = os.path.basename(path)
        for _, upload_info in _upload_file(api, project, full_path,
                                           media_id=media_id, filename=filename, chunk_size=0x04000000):
            pass
        media_def = {**make_video_definition(full_path),
                     'path': upload_info.key}
        # Patch in video file with the api.
        response = api.create_video_file(media_id, role='archival',
                                         video_definition=media_def)
    else:
        filename = os.path.basename(path)
        for _, upload_info in _upload_file(api, project, full_path,
                                           media_id=media_id, filename=filename, chunk_size=0x04000000):
            pass
        with tempfile.TemporaryDirectory() as td:
            filename = f"{uuid.uuid4()}.json"
            segments_path = os.path.join(td, filename)
            make_fragment_info(full_path, segments_path)
            for _, segment_info in _upload_file(api, project, segments_path,
                                                media_id=media_id, filename=filename, chunk_size=0x04000000):
                pass
        # Construct create video file spec.
        media_def = {**make_video_definition(full_path),
                     'path': upload_info.key,
                     'segment_info': segment_info.key}
        response = api.create_video_file(media_id, role='streaming',
                                         video_definition=media_def)

    print(f"{path}: Upload as {time_str} to {section} -- {attributes}")
    return True

if __name__=="__main__":
    parser = tator.get_parser()
    parser.add_argument("--type-id",
                        required=True,
                        type=int)
    parser.add_argument("--section-lookup",
			type=str)
    parser.add_argument("--skip-archival",
                        action="store_true")
    parser.add_argument("--trip-id",
                        required=True,
                        type=str)
    parser.add_argument('--date-start',
                        type=str,
                        required=True)
    parser.add_argument('--date-end',
                        type=str,
                        required=True)
    parser.add_argument("--timezone",
                        type=str,
                        required=False)

    parser.add_argument("directory")
    args = parser.parse_args()
    start_date = parse(args.date_start)
    end_date = parse(args.date_end)
    api = tator.get_api(args.host, args.token)

    media_type = api.get_media_type(args.type_id)
    project = media_type.project

    uploaded_count = 0
    skipped_count = 0
    error_list = []
    start_time = datetime.now()
    upload_gid = str(uuid.uuid1())
    section_lookup = {}
    if args.section_lookup:
        with open(args.section_lookup,'r') as fp:
            section_lookup = yaml.safe_load(fp)

    print(f"Processing {args.directory}")

    all_media = api.get_media_list(project, type=args.type_id)
    print(f"Downloaded {len(all_media)} records")
    for root, dirs,files in os.walk(args.directory):
        if root.find('$RECYCLE.BIN') > 0:
            print("Skipping recycle bin")
            continue
        # Disable direct saves for now
        looking_for=['encode.json']
        found = set(looking_for).intersection(set(files))

        # For now 1080 files are assumed to be hevc and need cloud transcodes
        looking_for=['1080.mp4',
                     '720.mp4',
                     'archival.mp4',
                     'streaming.mp4',
                     '960.mp4',
                     '1440.mp4']
        found_uploadable = set(looking_for).intersection(set(files))
        print(f"Found = {found}")
        print(f"Found Uploadable = {found_uploadable}")
        if len(found) == 0 and len(found_uploadable) == 0:
            print(f"No streaming/archival/uploadable found in {root}")
            continue
        if found:
            media_files = [m for m in files if m.endswith('.mp4')]
            media_file = media_files[0]
            found_uploadable=None
        else:
            media_file = list(found_uploadable)[0]
        media_path = os.path.join(root,media_file)
        this_camera = os.path.basename(os.path.dirname(root))
        time_str=os.path.basename(root)
        recording_date = parse(time_str.replace('_',':'))
        if recording_date < start_date or recording_date > end_date:
            print(f"Skipping {time_str}")
            continue

        sensor=os.path.basename(os.path.dirname(root))
        # Format = [pk_]YYYY-MM-DDTHH_MM_SS.ZZZZZ
        encoded=time_str
        date_code = encoded.split('T')[0]
        time_code = encoded.split('T')[1]
        date_comps = date_code.split('_')[-1].split('-')
        time_comps = time_code.split('_')
        date=datetime(year=int(date_comps[0]),
                      month=int(date_comps[1]),
                      day=int(date_comps[2]),
                      hour=int(time_comps[0]),
                      minute=int(time_comps[1]),
                      second=int(float(time_comps[2])))
        if args.timezone:
            timezone = pytz.timezone(args.timezone)
            date = timezone.normalize(pytz.utc.localize(date))
            date_code = date.date().isoformat()
            time_code = date.time().isoformat()

        fname = f"{date.isoformat()}.mp4"

        # Assign section name based on alias rules.
        if sensor in section_lookup:
            section=section_lookup[sensor]
        else:
            section=sensor

        existing=False
        for previous in all_media:
            camera = previous.attributes.get('Camera',
                                             None)
            if previous.name == fname and camera == this_camera:
                existing=True

        if existing:
            print(f"{media_path}: Found Existing")
            skipped_count+=1
            continue

        attributes={"Camera": this_camera,
                    "Date": date_code,
                    "Time": time_code,
                    "Trip": args.trip_id}

        if found_uploadable:
            print("Uploading file for transcode.")
            print("")
            video_fp = os.path.join(root,media_file)
            if check_file_is_valid(video_fp) is False:
                print(f"Warning: {video_fp} is not a valid media file.")
                error_list.append(video_fp)
                continue
            media_response = api.create_media(project, {'attributes': attributes,
                                                        'gid': upload_gid,
                                                        'name':fname,
                                                        'section': section,
                                                        'type': args.type_id,
                                                        'md5': tator.util.md5sum(video_fp)})
            media_id = media_response.id
            for p,_ in tator.util.upload_media(api,
                                               args.type_id,
                                               video_fp,
                                               upload_gid=upload_gid,
                                               media_id=media_id,
                                               chunk_size=0x04000000):
                print(f"\r{p}%",end='')
            print("\rComplete")
        else:
            print("Local transcode path")
            # This path is for locally transcoded files.
            md5sum = tator.util.md5sum(media_path)
            spec ={
                'type': args.type_id,
                'section': section,
                'name': fname,
                'md5': md5sum,
                'gid': upload_gid,
                'uid': str(uuid.uuid1())
            }
            if attributes:
                spec.update({'attributes': attributes})

            # Make media element to get ID
            response = api.create_media(project, media_spec=spec)
            assert isinstance(response, CreateResponse)
            media_id = response.id

            try:
                with tempfile.TemporaryDirectory() as td:
                    try:
                        thumb_path = os.path.join(td,f"{uuid.uuid4()}.jpg")
                        thumb_gif_path = os.path.join(td, f"{uuid.uuid4()}.gif")
                        make_thumbnails(args.host, args.token, media_id,
                                    media_path, thumb_path,thumb_gif_path)
                    except Exception as e:
                        print(f"Thumbnail error: {e}")
                        # Delete stale media
                        api.delete_media(media_id)
                        continue
            except Exception as e:
                print("WARNING: Could not delete file..")
                print(e)
            # Now process each file
            # Fault tolerant loop
            for idx,path in enumerate(files):
                done = False
                if os.path.splitext(path)[-1] == ".mp4":
                    count = 0
                    while not done and count < 5:
                        try:
                            count += 1
                            done = upload_path(api, project, os.path.join(root,path))
                        except Exception as exception:
                            print(f"Encountered error ({exception}), sleeping and retrying. CNT={count}/5")
                            time.sleep(5)

        # Increment uploaded count after success
        uploaded_count+=1


    print(f"Skipped {skipped_count} files")
    print(f"Uploaded {uploaded_count} files")
    if error_list:
        print(f"Incomplete media files ({len(error_list)}):")
        for idx,p in enumerate(error_list):
            print(f"{idx+1}: {p}")

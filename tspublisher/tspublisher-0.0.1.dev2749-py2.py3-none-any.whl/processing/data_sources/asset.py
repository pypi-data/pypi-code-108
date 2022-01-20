from __future__ import absolute_import, division, print_function, unicode_literals

import subprocess
import os.path
import sys
from shutil import copyfile
import json

try:
    from PIL import Image
except ImportError:
    Image = None

from publisher.exceptions import ContentMissingError
from publisher.processing.data_sources.step import get_csv_info
from publisher.processing.data_sources.utils import delete_misc_files, copy_assets
import publisher.settings as settings

ffmpegExe = 'ffmpeg'

ffmpegDefaults = [ffmpegExe,
                  # Input format
                  '-f', 'image2',
                  # Input framerate
                  '-r', '25',
                  # Insert position for input frames to be overwritten
                  'INPUT_SETTINGS',
                  # Video codec for the output
                  '-codec:v', 'libx264',
                  # Use veryslow preset to get best quality for bitrate not massive overall hit on conversion time
                  '-preset', 'veryslow',
                  # Set Constant Rate Factor for lower bitrate. Default = 23 higher value -> lower bitrate
                  '-crf', '27',
                  # Disables some advanced features but provides for better compatibility with iOS/Android
                  '-profile:v', 'baseline',
                  # Must set colorspace format compatible with x264
                  '-pix_fmt', 'yuv420p',
                  # H.264 level setting
                  '-level:v', '3.0',
                  # Disable CABAC
                  '-coder', '0',
                  # Video filter graph
                  'SCALE_SETTINGS',
                  # Output framerate
                  '-r', '25',
                  # Logging level
                  '-loglevel', 'panic']


def is_ffmpeg_installed():
    p = subprocess.Popen([ffmpegExe, '-h'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()
    rt = p.poll()
    return rt == 0


def get_pip_dir(module_dir):
    return os.path.join(module_dir, "pipSource")


def get_widget_dir(module_dir):
    return os.path.join(module_dir, "widgetGraphics")


def get_graphics_dir(module_dir, version):
    asset_dir = os.path.join(module_dir, "graphics")

    if version == "latest":
        return get_latest_version_directory(asset_dir)
    else:
        return os.path.join(asset_dir, version)


def get_phase_directory(phase_code, vbs):
    if not vbs:
        dir_name = os.path.join(settings.CG_APP5_ROOT, phase_code)
    else:
        dir_name = os.path.join(settings.VBS_ROOT, phase_code)

    if not os.path.isdir(dir_name):
        raise ContentMissingError('Source folder not found for %s at %s' % (phase_code, dir_name))

    return dir_name


def get_latest_version_directory(dir_name):
    path, dirs, files = next(os.walk(dir_name))

    if len(dirs) == 0:
        raise EOFError("No asset versions found for: %s" % dir_name)

    return os.path.join(path, dirs[-1])


def convert_files(phase, phase_directory, graphics_version="latest", pip_graphics_version={},
                  update_widget_graphics=True, vbs=False, csv_version=None):
    if not is_ffmpeg_installed():
        print("Error: no ffmpeg executable found at: ", ffmpegExe)
        sys.exit(2)

    latest_phase_directory = get_phase_directory(phase.code, vbs)

    if graphics_version:
        graphics_dir = get_graphics_dir(latest_phase_directory, graphics_version)
        graphics_files = get_file_list(graphics_dir)

        if not graphics_files:
            raise ContentMissingError('Source frames not found for {0}'.format(phase.code))

        copy_graphics_files(phase.code, graphics_dir, phase_directory, csv_version)

    pip_directory = get_pip_dir(latest_phase_directory)
    if pip_graphics_version is not None and os.path.isdir(pip_directory):
        copy_pip_files(phase.code, pip_directory, phase_directory, pip_graphics_version, csv_version)

    widget_directory = get_widget_dir(latest_phase_directory)
    if update_widget_graphics and os.path.isdir(widget_directory):
        copy_widget_files(widget_directory, phase_directory)


def copy_graphics_files(phase_code, source_directory, dest_dir, csv_version):
    file_list = get_file_list(source_directory)

    headers, rows = get_csv_info(phase_code, csv_version)

    frame_numbers = []
    test_frame_numbers = []
    missing_frames = []
    prefix = "image"
    test_prefix = "test_image"

    for row in rows:
        first_frame = int(row["firstImageId"])

        if row["lastImageId"]:
            last_frame = int(row["lastImageId"])
        else:
            last_frame = first_frame

        frame_numbers.append([first_frame, last_frame])

        for i in range(first_frame, last_frame + 1):
            image_name = "%s%05d.jpg" % (prefix, i)

            # Check for missing frames in step
            if image_name not in file_list:
                missing_frames.append(image_name)

        if "testFirstImageId" in row and row["testFirstImageId"]:
            test_first_frame = int(row["testFirstImageId"])

            if "testLastImageId" in row and row["testLastImageId"]:
                test_last_frame = int(row["testLastImageId"])
            else:
                test_last_frame = test_first_frame

            test_frame_numbers.append([test_first_frame, test_last_frame])

            for i in range(test_first_frame, test_last_frame + 1):
                image_name = "%s%05d.jpg" % (test_prefix, i)

                # Check for missing frames in step
                if image_name not in file_list:
                    missing_frames.append(image_name)

    # Error out if missing frames were found
    if missing_frames:
        raise EOFError("Missing frames: %s" % str(missing_frames))

    print("\n-- Converting image files --")
    copy_files(frame_numbers, source_directory, dest_dir, prefix, "%05d")
    copy_files(test_frame_numbers, source_directory, dest_dir, test_prefix, "%05d")


def copy_pip_files(phase_code, source_directory, dest_directory, versions, csv_version):
    path, dirs, files = next(os.walk(source_directory))

    pip_folders = {}

    for pip_name in dirs:
        pip_folder = os.path.join(path, pip_name)
        if isinstance(versions, dict) and pip_name in versions:
            pip_version_folder = os.path.join(pip_folder, versions[pip_name])
        else:
            pip_version_folder = get_latest_version_directory(pip_folder)
        file_list = get_file_list(pip_version_folder)

        pip_folders[pip_name] = {
            "folder": pip_version_folder,
            "files": file_list
        }

    headers, rows = get_csv_info(phase_code, csv_version)

    if "pip_sim2dData" not in headers:
        return

    frame_numbers = {}
    missing_frames = {}

    for row in rows:

        pip_info = row["pip_sim2dData"]

        if pip_info and not pip_info == "{}":
            pip_load = json.loads(pip_info)
            pip_name = pip_load["view"]

            if pip_load["sequence"]:
                first_frame = int(row["firstImageId"])
                if row["lastImageId"]:
                    last_frame = int(row["lastImageId"])
                else:
                    last_frame = first_frame

                if pip_name not in frame_numbers:
                    frame_numbers[pip_name] = []

                frame_numbers[pip_name].append([first_frame, last_frame])

                for i in range(first_frame, last_frame):
                    image_name = "%s%05d.jpg" % (pip_name, i)

                    # Check for missing frames in step
                    if image_name not in pip_folders[pip_name]["files"]:
                        if pip_name not in missing_frames:
                            missing_frames[pip_name] = []

                        missing_frames[pip_name].append(image_name)

                # Error out if missing frames were found
                if missing_frames:
                    raise EOFError("Missing frames: %s" % str(missing_frames))

                print("\n-- Converting pip files step: %s --" % row["stepId"])
                for pip in frame_numbers:
                    copy_files(frame_numbers[pip], pip_folders[pip]["folder"], dest_directory, pip, "%05d")

            else:
                image_name = "%s_image%s" % (pip_name, pip_load["ext"])
                pip_files = pip_folders[pip_name]["files"]

                if len(pip_files) > 1:
                    raise EOFError("Too many files for non sequence pip: %s" % str(pip_folders[pip_name]["folder"]))
                elif len(pip_files) < 1:
                    raise EOFError("Missing pip images in: %s" % str(pip_folders[pip_name]["folder"]))

                asset_dir = os.path.join(dest_directory, "assets")
                dest_file = os.path.join(asset_dir, image_name)
                source_file = os.path.join(pip_folders[pip_name]["folder"], pip_files[0])

                print("\n-- Copying pip files step: %s --" % row["stepId"])
                copyfile(source_file, dest_file)


def copy_widget_files(source_directory, dest_directory):
    print("\n-- Copying widget files --")
    asset_dir = os.path.join(dest_directory, "assets")
    copy_assets(source_directory, asset_dir)


def copy_files(frame_numbers, source_dir, dest_dir, prefix, padding):
    if not Image:
        raise Exception("PIL was not imported")
    asset_dir = os.path.join(dest_dir, "assets")

    for frames in frame_numbers:
        # Copy first and last image
        for frame in frames:
            frame_number = padding % frame
            frame_file = "%s%s.jpg" % (prefix, frame_number)

            source_file = os.path.join(source_dir, frame_file)
            dest_file = os.path.join(asset_dir, frame_file)

            copyfile(source_file, dest_file)

        # Convert sequence to video file
        if not frames[1] == frames[0]:
            frame_number_start = padding % frames[0]
            frame_number_end = padding % frames[1]
            video_file_name = "video-%s%s-%s%s.mp4" % (prefix, frame_number_start, prefix, frame_number_end)
            input_name = prefix + "%s.jpg" % padding
            input_image_path = os.path.join(source_dir, input_name)
            output_video_path = os.path.join(asset_dir, video_file_name)
            frame_count = str(frames[1] - frames[0] + 1)

            ffmpeg_options = list(ffmpegDefaults)

            # Insert settings in list - FFMPEG requires a specific order to the arguments
            input_index = ffmpeg_options.index("INPUT_SETTINGS")
            ffmpeg_options[input_index:input_index + 1] = [
                # Set starting frame for image sequence
                "-start_number", str(frames[0]),
                # Force overwrite
                "-y",
                # Add input file range in image0000... format
                "-i", input_image_path,
                # Set frame count for video
                "-frames:v", frame_count]

            # Get resolution of source file if pip
            if prefix != "image":
                frame_number = padding % frames[0]
                image_name = "%s%s.jpg" % (prefix, frame_number)
                image_path = os.path.join(source_dir, image_name)
                im = Image.open(image_path)
                width, height = im.size
                width = width + (width % 2)  # h264 requires width to be multiple of 2
                height = height + (height % 2)  # h264 requires height to be multiple of 2
                # Set the video scale
                scale_settings = "scale='%d:%d'" % (width, height)
            else:
                # Set the video scale
                scale_settings = settings.DEFAULT_SCALE

            scale_index = ffmpeg_options.index("SCALE_SETTINGS")
            ffmpeg_options[scale_index:scale_index + 1] = [
                # Filtergraph option (lets you set scale, pixel aspect, etc.)
                "-vf",
                scale_settings]

            # Set output video location
            ffmpeg_options.append(output_video_path)

            print("-- Converting frame range %d - %d --" % (frames[0], frames[1]))
            print("{}".format(ffmpeg_options))
            subprocess.call(ffmpeg_options)

            if not os.path.exists(output_video_path):
                raise Exception("Failed to create %s" % output_video_path)

        delete_misc_files(asset_dir)


def get_file_list(directory_name):
    path, dirs, files = next(os.walk(directory_name))

    # Remove thumbnail file from list
    if "Thumbs.db" in files:
        files.remove("Thumbs.db")

    return files

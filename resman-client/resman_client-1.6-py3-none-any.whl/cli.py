import json
import logging
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Set, List, Iterable

import chardet
import click

from resman_client.client import ResmanClient, VideoList, ImageList, Novel
from resman_client.ffmpeg_util import convert_video_to_h264

log = logging.getLogger("Resman Client")


def pretty_size(size_in_bytes: int, to: str = None, bsize: int = 1024):
    """
    Modified from https://gist.github.com/shawnbutts/3906915
    """
    a = {'k': 1, 'm': 2, 'g': 3, 't': 4, 'p': 5, 'e': 6}
    if to is None:
        to = "k"
        for t, o in a.items():
            if (bsize ** o) <= size_in_bytes <= (bsize ** (o + 1)):
                to = t
                break
    r = float(size_in_bytes)
    for i in range(a[to]):
        r = r / bsize
    return f"{r:.3f} {to}b"


def read_file(filepath: str) -> Iterable[str]:
    with open(filepath, "rb") as fp:
        encoding_info = chardet.detect(fp.read())
    if "encoding" in encoding_info and encoding_info.get("confidence", 0) > 0.9:
        encoding = encoding_info["encoding"]
        log.debug(f"Reading {filepath} with encoding={encoding}")
        with open(filepath, "r", encoding=encoding, errors="ignore") as fp:
            yield from fp.readlines()
    else:
        log.warning(f"File {filepath} skipped caused by encoding info is fuzzy: {json.dumps(encoding_info)}")


@click.group()
@click.option('--debug/--no-debug', default=False)
def main(debug: bool):
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)


@main.group()
def auth(): pass


@auth.command("create")
@click.option("--endpoint", default=None, help="Endpoint of the config")
@click.option("--server-name", default=None, help="Name of the config")
@click.option("--user", default=None, help="User of the config")
@click.option("--pass", default=None, help="Password of the config")
def create_auth(
        **kwargs
):
    params = {}
    for k, v in kwargs.items():
        if v is None:
            v = click.prompt(f"Please input {k}")
        params[k] = v
    config_path = os.path.expanduser("~/.config/resman/")
    if not os.path.isdir(config_path):
        os.makedirs(config_path)
    config_file = os.path.expanduser(f"~/.config/resman/{params['server_name']}.json")
    log.debug(f"Saving config to {config_file}")
    if (not os.path.isfile(config_file)) or click.confirm("Config existed, cover it?"):
        with open(config_file, "w") as fp:
            json.dump(params, fp)


@main.group()
@click.option("--server-name", required=True, help="Which config to use.")
@click.pass_context
def upload(ctx, server_name: str):
    config_file = os.path.expanduser(f"~/.config/resman/{server_name}.json")
    log.debug(f"Loading config from {config_file}")
    with open(config_file, "r") as fp:
        data = json.load(fp)
    ctx.obj = ResmanClient(
        endpoint=data["endpoint"],
        user=data["user"],
        password=data["pass"]
    )


def search_file_in_path(path: str, suffix_set: Set[str]) -> List[str]:
    result = []
    path = os.path.expanduser(path)
    if os.path.isfile(path):
        if Path(path).suffix.lower() in suffix_set:
            result.append(path)
    elif os.path.isdir(path):
        for d, _, fs in os.walk(path):
            for f in fs:
                if Path(f).suffix.lower() in suffix_set:
                    result.append(os.path.join(d, f))
    return result


@upload.command("video")
@click.option("--title", help="Title of the video set")
@click.option("--description", help="Detail of this video set")
@click.option("--like/--no-like", default=False, help="Set like to this set")
@click.option("--path", help="Search path of mp4 files")
@click.option("-y/-n", default=False, help="Do not confirm before uploading")
@click.pass_obj
def upload_video(
        rc: ResmanClient,
        title: str,
        description: str,
        like: bool,
        path: str,
        y: bool
):
    path = path or click.prompt("Input path of the file(s)")

    video_files = search_file_in_path(path, {".mp4", ".avi", ".mkv", ".wmv", ".3gp", ".mdf"})
    if len(video_files) <= 0:
        raise Exception(f"Can't find file in path {path}")
    video_files = sorted(video_files)

    print(f"Title: {title}\nDescription: {description}\nSet Like: {like}")
    print("Files:")
    sum_size = 0
    for video_file in video_files:
        file_size = os.path.getsize(video_file)
        sum_size += file_size
        size_str = pretty_size(file_size)
        print(f"File: {video_file} Size: {size_str}")
    print(f"Sum of the files size: {pretty_size(sum_size)}")

    title = title or click.prompt("Input title of the video", default=(
        Path(video_files[0]).stem if len(video_files) == 1 else Path(path).stem
    ))
    description = description or click.prompt("Input description of the video", default="\n".join(video_file))

    if y or click.confirm("Upload these files?"):
        log.info(f"Creating the video list...")
        vl = rc.create_video_list(VideoList(
            title=title,
            description=description,
            data={
                "upload_filenames": video_files
            }
        ))
        if like:
            vl.reaction = True
        with TemporaryDirectory() as td:
            log.debug(f"Converting files to {td}")
            for i, video_file in enumerate(video_files):
                filename_h264 = os.path.join(td, f"{i}.mp4")
                convert_video_to_h264(video_file, filename_h264)
                vl.upload_mp4_video(filename_h264, i)
        log.info("Videos uploaded successfully, please check {}".format(
            rc.make_url(f"videolist/{vl.object_id}")
        ))


@upload.command("image")
@click.option("--title", help="Title of the image set")
@click.option("--description", help="Detail of this image set")
@click.option("--like/--no-like", default=False, help="Set like to this set")
@click.option("--path", help="Search path of image files")
@click.option("-y/-n", default=False, help="Do not confirm before uploading")
@click.pass_obj
def upload_image(
        rc: ResmanClient,
        title: str,
        description: str,
        like: bool,
        path: str,
        y: bool
):
    path = path or click.prompt("Input path of the file(s)")
    image_files = search_file_in_path(path, {".png", ".jpeg", ".jpg", ".gif", ".bmp"})
    if len(image_files) <= 0:
        raise Exception(f"Can't find file in path {path}")
    image_files = sorted(image_files)
    title = title or click.prompt("Input title of the image", default=(
        Path(image_files[0]).stem if len(image_files) == 1 else Path(path).stem
    ))
    description = description or click.prompt("Input description of the image", default="")

    print(f"Title: {title}\nDescription: {description}\nSet Like: {like}")
    print("Files:")
    sum_size = 0
    for i, image_file in enumerate(image_files):
        file_size = os.path.getsize(image_file)
        sum_size += file_size
        size_str = pretty_size(file_size)
        print(f"{i}. {image_file} Size: {size_str}")
    print(f"Sum of the files size: {pretty_size(sum_size)}")
    if y or click.confirm("Upload these files?"):
        log.info(f"Creating the image list...")
        il = rc.create_image_list(ImageList(
            title=title,
            description=description,
            data={
                "upload_filenames": image_files
            }
        ))
        if like:
            il.reaction = True
        il.upload_images(image_files, 0)
        log.info("Images uploaded successfully, please check {}".format(
            rc.make_url(f"imagelist/{il.object_id}")
        ))


@upload.command("novels")
@click.option("--like/--no-like", default=False, help="Set like to this set")
@click.option("--path", help="Search path of image files")
@click.option("-y/-n", default=False, help="Do not confirm before uploading")
@click.pass_obj
def upload_novels(
        rc: ResmanClient,
        like: bool,
        path: str,
        y: bool
):
    path = path or click.prompt("Input path of the file(s)")
    novel_files = sorted(search_file_in_path(path, {".txt"}))
    if len(novel_files) <= 0:
        raise Exception(f"Can't find file in path {path}")
    for novel_file in novel_files:
        title = Path(novel_file).stem
        print(f"Title: {title}\nSet Like: {like}File:\n{novel_file} Size:{pretty_size(os.path.getsize(novel_file))}")

    if y or click.confirm("Upload these files?"):
        log.info(f"Creating the novels...")
        for novel_file in novel_files:
            try:
                title = Path(novel_file).stem
                text = "\n".join(read_file(novel_file))
                n = rc.create_novel(Novel(
                    title=title,
                    data={"upload_filename": novel_file},
                ), text=text)
                if like:
                    n.reaction = True
                log.info("Novel uploaded successfully, please check {}".format(rc.make_url(f"novel/{n.object_id}")))
            except Exception as ex:
                log.error(f"Error while processing {novel_file}", exc_info=ex)


@upload.command("novel")
@click.option("--title", help="Title of the image set")
@click.option("--like/--no-like", default=False, help="Set like to this set")
@click.option("--path", help="Search path of image files")
@click.option("-y/-n", default=False, help="Do not confirm before uploading")
@click.pass_obj
def upload_novel(
        rc: ResmanClient,
        title: str,
        like: bool,
        path: str,
        y: bool
):
    path = path or click.prompt("Input path of the file(s)")
    novel_files = search_file_in_path(path, {".txt"})
    if len(novel_files) <= 0:
        raise Exception(f"Can't find file in path {path}")
    elif len(novel_files) > 1:
        raise Exception(f"We found {len(novel_files)} files, you can only upload one file once")
    novel_file = novel_files[0]
    title = title or click.prompt("Input title of the image", default=Path(novel_file).stem)

    print(f"Title: {title}\nSet Like: {like}File:\n{novel_file} Size:{pretty_size(os.path.getsize(novel_file))}")

    if y or click.confirm("Upload these files?"):
        log.info(f"Creating the novel...")
        n = rc.create_novel(Novel(
            title=title,
            data={"upload_filename": novel_file},
        ), text="\n".join(read_file(novel_file)))
        if like:
            n.reaction = True
        log.info("Novel uploaded successfully, please check {}".format(rc.make_url(f"novel/{n.object_id}")))


@main.group()
@click.option("--server-name", required=True, help="Which config to use.")
@click.pass_context
def convert(ctx, server_name: str):
    config_file = os.path.expanduser(f"~/.config/resman/{server_name}.json")
    log.debug(f"Loading config from {config_file}")
    with open(config_file, "r") as fp:
        data = json.load(fp)
    ctx.obj = ResmanClient(
        endpoint=data["endpoint"],
        user=data["user"],
        password=data["pass"]
    )


@convert.command("video")
@click.argument("vid", type=int)
@click.option("-remove/-keep", default=True, help="Remove video list after successfully converted")
@click.pass_obj
def upload_video(
        rc: ResmanClient,
        vid: int,
        remove: bool,
):
    video_list = rc.get_video_list(vid)
    video_list_data = video_list.data
    new_video_list = rc.create_video_list(VideoList(
        title=video_list_data["title"],
        description=video_list_data["description"],
        data=video_list_data["data"],
    ))
    new_video_list.reaction = video_list.reaction
    try:
        log.info(f"Converting video list {vid} -> {new_video_list.object_id}")
        with TemporaryDirectory() as td:
            log.debug(f"Converting files to {td}")
            for i, video_id in enumerate(video_list_data["videos"]):
                log.info(f"Downloading video #{i}: {video_id}")
                downloaded_file = os.path.join(td, f"{i}.mp4")
                converted_file = os.path.join(td, f"{i}_h264.mp4")
                with open(downloaded_file, "wb") as fp:
                    with rc.get(f"/api/video/{video_id}", stream=True) as resp:
                        resp.raise_for_status()
                        for chunk in resp.iter_content(chunk_size=1024 * 1024):
                            if chunk:
                                fp.write(chunk)
                log.info(f"Converting to correct codec...")
                convert_video_to_h264(downloaded_file, converted_file)
                log.info(f"Uploading...")
                new_video_list.upload_mp4_video(converted_file, i)
    except BaseException as ex:
        new_video_list.destroy()
        log.error(f"Error while converting video list {vid} caused by:", exc_info=ex)
        raise ex
    if remove:
        video_list.destroy()


if __name__ == '__main__':
    main()

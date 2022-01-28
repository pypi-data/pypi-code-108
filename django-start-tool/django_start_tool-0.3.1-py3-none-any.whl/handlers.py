import os
import shutil
from pathlib import Path
from urllib.request import urlretrieve
from zipfile import is_zipfile
from zipfile import ZipFile

from .utils import get_content
from .utils import get_subdir_name
from .utils import is_url


def handle_template(
    project_name,
    target,
    template,
    files_patterns,
    context
):
    args = [
        template,
        target,
        project_name,
        files_patterns
    ]
    if is_url(template):
        files = handle_url(*args)
    elif is_zipfile(template):
        files = handle_zip(*args)
    else:
        files = handle_tree(*args)

    for file in files:
        content = get_content(file, context)
        file.write_text(content)


def handle_tree(
    path,
    target,
    project_name,
    patterns
):
    path = Path(path).resolve()
    to_render = []
    os.makedirs(target, exist_ok=True)

    for entity in path.iterdir():
        dst = target / entity.name

        if entity.is_file():
            for pattern in patterns:
                if entity.match(pattern):
                    dst = dst.with_name(dst.name.replace('-tpl', ''))
                    to_render.append(dst)
            shutil.copyfile(entity, dst)
        if entity.is_dir():
            if entity.match('project_name'):
                dst = dst.with_name(project_name)
            to_render.extend(handle_tree(entity, dst, project_name, patterns))

    return to_render


def handle_url(
    url,
    target,
    project_name,
    patterns
):
    content, _ = urlretrieve(url)

    with ZipFile(content) as archive:
        archive.extractall()

    # There is subdir in the GitHub repository zip archive
    # like this: django-start-tool-main -- '{repo}-{branch}'.
    # It is necessary to extract all the contents and delete this subdir.
    subdir_name = get_subdir_name(url)
    files = handle_tree(subdir_name, target, project_name, patterns)
    shutil.rmtree(subdir_name)
    return files


def handle_zip(
    path,
    target,
    project_name,
    patterns
):
    tmp = target / 'tmp'

    with ZipFile(path) as archive:
        archive.extractall(tmp)

    files = handle_tree(tmp, target, project_name, patterns)
    shutil.rmtree(tmp)
    return files

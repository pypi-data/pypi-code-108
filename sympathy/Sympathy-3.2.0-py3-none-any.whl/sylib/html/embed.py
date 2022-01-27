# This file is part of Sympathy for Data.
# Copyright (c) 2021, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import base64
import bs4
import mimetypes
import os.path
import pathlib
import urllib.parse
import sys
from sympathy.platform.hooks import request_http

_parser = 'lxml'


class HtmlError(Exception):
    pass


class UnhandledURL(HtmlError):
    pass


def _guess_mime_type(url: str):
    mime_type, encoding = mimetypes.guess_type(url)
    return mime_type or '', encoding or 'utf-8'


def _get_http_data(url: str) -> (bytes, str, str):
    mime_type, encoding = _guess_mime_type(url)
    request = request_http.value.get(url)
    data = request.content
    if 'Content-Type' in request.headers:
        mime_type = request.headers['Content-Type']
    encoding = request.encoding or 'utf-8'
    return data, mime_type, encoding


def _get_local_data(filename: str) -> (bytes, str, str):
    mime_type, encoding = _guess_mime_type(filename)
    with open(filename, 'rb') as f:
        data = f.read()
    return data, mime_type, encoding


def _embed_data_in_uri(data: bytes, mime_type: str, encoding: str) -> str:
    mime_type = mime_type
    if mime_type == ' ' or mime_type.startswith('text/'):
        encoded_data = urllib.parse.quote(data.decode(encoding))
    else:
        mime_type = f'{mime_type};base64'
        encoded_data = base64.b64encode(data).decode(encoding)
    res = f'data:{mime_type},{encoded_data}'
    return res


def _is_windows_drive_letter(scheme):
    return scheme and len(scheme) == 1 and (
        'a' <= scheme.lower() and scheme.lower() <= 'z')


def _is_windows_path(path):
    # /C:...
    # Result of urlparse('file:///C:').path
    return (path and len(path) > 2 and path[2] == ':' and
            _is_windows_drive_letter(path[1]))


def _localpath(path: str) -> str:
    return path.replace('/', os.path.sep)


def _posixpath(path: str) -> str:
    return path.replace('\\', '/')


_tag_attrs = {
    'img':  'src',
    'link': 'href',
    'script': 'src',
}


def _supported_tag(tag):
    name = tag.name
    res = False
    if name in _tag_attrs:
        res = True
        if name == 'link':
            res = 'stylesheet' in tag['rel']
    return res


def _get_url(tag):
    attr = _tag_attrs[tag.name]
    return tag.attrs.get(attr)


def _set_url(tag, value):
    attr = _tag_attrs[tag.name]
    tag[attr] = value


def _get_url_tags(soup):
    tags = []
    for tag_name in _tag_attrs.keys():
        for tag in soup(tag_name):
            if _supported_tag(tag):
                url = _get_url(tag)
                if url:
                    tags.append((url, tag))
    return tags


def _join_remote_tags(url, tags):
    for tag_url, tag in tags:
        yield (urllib.parse.urljoin(url, tag_url), tag)


def _join_local_tags(filename, tags):
    path = pathlib.PurePath(filename).parent
    for tag_url, tag in tags:
        yield (path / tag_url, tag)


def _remote_tags(tags):
    for tag_url, tag in tags:
        scheme = urllib.parse.urlparse(tag_url).scheme
        if scheme and scheme.lower() in ['http', 'https']:
            yield (tag_url, tag)


def _local_tags(tags):
    for tag_url, tag in tags:
        parsed = urllib.parse.urlparse(tag_url)
        scheme = parsed.scheme
        if _is_windows_drive_letter(scheme) or not scheme:
            yield (tag_url, tag)
        elif scheme == 'file':
            netloc = parsed.netloc
            path = parsed.path
            if netloc:
                # Assume UNC.
                path = f'//{netloc}{path}'
            elif _is_windows_path(path):
                path = path[1:]
            yield (path, tag)


def _download_http_and_set(download: dict, url: str):
    try:
        download[url] = _get_http_data(url)
    except Exception as e:
        print(f'Failed to download {url} due to {e}.', file=sys.stderr)


def _read_local_and_set(download: dict, url: str):
    try:
        download[url] = _get_local_data(url)
    except Exception as e:
        print(f'Failed to read {url} due to {e}.', file=sys.stderr)


def _downloaded_tags(tags, downloads):
    for tag_url, tag in tags:
        if tag_url in downloads:
            yield (tag_url, tag)


def _download_remote_html(url: str) -> dict:
    html_data = _get_http_data(url)
    soup = bs4.BeautifulSoup(html_data[0], _parser)
    download = {url: html_data}
    tags = list(_join_remote_tags(url, _remote_tags(_get_url_tags(soup))))
    for tag_url, tag in tags:
        _download_http_and_set(download, tag_url)
    return soup, tags, download


def _download_local_html(filename: str, content: bytes = None) -> dict:
    if content is None:
        html_data = _get_local_data(filename)
    else:
        encoding, mime_type = _guess_mime_type(filename)
        html_data = (content, mime_type, encoding)
    soup = bs4.BeautifulSoup(html_data[0], _parser)
    download = {filename: html_data}
    tags = _get_url_tags(soup)
    remote = list(_remote_tags(tags))
    local = list(_join_local_tags(filename, _local_tags(tags)))

    for tag_url, tag in remote:
        _download_http_and_set(download, tag_url)
    for tag_url, tag in local:
        _read_local_and_set(download, tag_url)
    return soup, remote + local, download


def download_remote_html_to_directory(url: str, root: str):
    """
    Download URL and its embeddable resources to `root` folder.

    Parameters
    ----------
    url
        HTTP(s) URL address to HTML page.
    root
        Folder where files will be downloaded.

    Returns
    -------
    Path to downloaded HTML page.
    """
    soup, tags, download = _download_remote_html(url)
    root_path = pathlib.PurePath(root)

    for tag_url, tag in _downloaded_tags(tags, download):
        parsed = urllib.parse.urlparse(tag_url)
        rel_path = pathlib.PurePosixPath(parsed.path).relative_to('/')
        rooted_path = pathlib.PurePosixPath(
            root_path.as_posix()) / parsed.netloc / rel_path
        path = pathlib.Path(rooted_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('wb') as f:
            f.write(download[tag_url][0])
        _set_url(tag, f'{pathlib.PurePosixPath(parsed.netloc) / rel_path}')

    index = pathlib.Path(root_path / 'index.html')
    with index.open('w') as f:
        f.write(str(soup))
    return str(index)


def embed_remote_html(url: str) -> str:
    """
    Download URL and its resources and output HTML with resources embedded.

    Parameters
    ----------
    url
        HTTP(s) URL address to HTML page.

    Returns
    -------
    HTML content.
    """
    soup, tags, download = _download_remote_html(url)
    for tag_url, tag in _downloaded_tags(tags, download):
        _set_url(tag, _embed_data_in_uri(*download[tag_url]))
    return str(soup)


def embed_local_html(filename: str, content: bytes = None) -> str:
    """
    Open file and its resources and output HTML with resources embedded.

    Parameters
    ----------
    filename
        Local HTML page.

    Returns
    -------
    HTML content.
    """
    soup, tags, download = _download_local_html(filename, content)
    for tag_url, tag in _downloaded_tags(tags, download):
        _set_url(tag, _embed_data_in_uri(*download[tag_url]))
    return str(soup)

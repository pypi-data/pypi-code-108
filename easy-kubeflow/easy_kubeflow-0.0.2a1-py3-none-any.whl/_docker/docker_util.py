import base64
import os
import time
from time import sleep
from typing import Optional

import docker

try:
    from IPython.display import display, HTML
except ImportError:
    print("ModuleNotFoundError: No module named 'IPython'")
import pandas as pd
import re
import requests
from tqdm import tqdm

from easy_kubeflow.utils import MyLogger

RepoTags = 'RepoTags'
Id = 'Id'
Created = 'Created'
Size = 'Size'
Names = 'Names'
Image = 'Image'
Command = 'Command'
Status = 'Status'
Ports = 'Ports'

NODE_HOST = '172.17.0.1'
Registry = 'harbor.stonewise.cn/kubeflow/'
USER_NAME = b'bGl1d2VpYmlu'
PASSWORD = b'U3RvbmV3aXNlQDIwMjExMA=='

namespace = os.environ["NB_PREFIX"].split("/")[-2]
notebook_name = os.environ["NB_PREFIX"].split("/")[-1]
pod_name = notebook_name + "-0"
my_container_name = notebook_name + "_" + pod_name + "_" + namespace

DEFAULT_DATA_CHUNK_SIZE = 1024 * 1024 * 100  # default chunk size 100MB
DEFAULT_TIMEOUT_SECONDS = 600  # default timeout for 10min

pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', 150)

_logger = MyLogger()


def _sub_str(character, start=0, lenght=None):
    try:
        if lenght:
            return character[start:start + lenght]
        else:
            return character[start:]
    except TypeError as te:
        print(te)
        return character


def _bit_convert_disk(bit_size):
    """
    convert bit to Mbit Gbit in disk
    base in disk is 1000 not 1024
    :param bit_size:
    :return:
    """
    try:
        if bit_size < 1000:
            return '{} B'.format(round(float(bit_size), 1))
        elif bit_size >= 1000 and bit_size < 1000000:
            return '{} KB'.format(round(float(bit_size / 1000), 1))
        elif bit_size >= 1000000 and bit_size < 1000000000:
            return '{} MB'.format(round(float(bit_size / 1000000), 1))
        else:
            return '{} GB'.format(round(float(bit_size / 1000000000), 1))
    except TypeError as te:
        print(te)
        return ''


def _str_convert_bit():
    pass


def _name_or_id(character):
    if _sub_str(character, start=0, lenght=7) == 'sha256:':
        return _sub_str(character, start=7, lenght=12)
    else:
        return character


def _select_iamge_info(dictionary):
    tag = dictionary.get(RepoTags)
    id = dictionary.get(Id)
    created = dictionary.get(Created)
    size = dictionary.get(Size)
    return {'REPOSITORY + TAG': tag, 'IMAGE ID': _sub_str(id, start=7, lenght=12),
            'CREATED': _sub_str(created, lenght=23), 'SIZE': _bit_convert_disk(bit_size=size)}


def _select_containers_info(dictionary):
    id = dictionary.get(Id)
    container_names = dictionary.get(Names)
    image_names = dictionary.get(Image)
    command = dictionary.get(Command)
    created = dictionary.get(Created)
    status = dictionary.get(Status)
    ports = dictionary.get(Ports)
    return {'CONTAINER ID': _sub_str(id, start=0, lenght=12),
            'CREATED': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(created)), 'STATUS': status,
            'PORTS': '' if ports == [] else ports[0], 'IMAGE': _name_or_id(image_names), 'COMMAND': command,
            'CONTAINER NAME': container_names[0].strip('/')}


def _docker_progress(stream):
    stream_list = list(stream)
    _value = "initial"
    success = True
    for i in tqdm(range(len(stream_list))):
        value = list(stream_list[i].values())[0]
        if value.__class__.__name__ == 'str':
            value = value.strip('\n').strip('\r')
        if 'errorDetail' in stream_list[i].keys():
            success = False
            _logger.error(value)
        else:
            if value == _value:
                continue
            else:
                _value = value
                _logger.info(value)
        sleep(0.1)
    return success


def _del_contin_repeat_str(character, repeat):
    flag = False
    res = ''
    if character:
        for cha in character:
            if flag:
                if cha == repeat:
                    continue
                else:
                    res += cha
                    flag = False
            else:
                res += cha
                if cha == repeat:
                    flag = True
        return res
    else:
        return res


def _standard_dir(character):
    if character:
        if character[-1] != '/':
            _character = character + '/'
        else:
            _character = character
        return _del_contin_repeat_str(_character, '/')
    else:
        return ''


def _grep_match(character, string):
    matched = re.search(pattern=character, string=string, flags=0)
    if matched:
        return True
    else:
        return False


class EasyDocker(object):
    """Simple way to use docker in python"""

    def __init__(self, host: str = NODE_HOST, port: int = 8082, version: Optional[str] = "auto",
                 timeout: int = DEFAULT_TIMEOUT_SECONDS):
        self.host = host
        self.port = port
        self.base_url = "tcp://{host}:{port}".format(host=self.host, port=self.port)
        self.client = docker.DockerClient(base_url=self.base_url, version=version, timeout=timeout)
        self.client.login(username=base64.b64decode(USER_NAME).decode('ascii'),
                          password=base64.b64decode(PASSWORD).decode('ascii'),
                          registry='harbor.stonewise.cn')  # add authentication
        _logger.info("Connected to host docker successfully !")

    def close(self):
        """Closes all adapters and as such the session"""
        self.client.close()
        _logger.info("Closes all adapters and as such the session successfully !")

    def show_images(self, grep: Optional[str] = None):
        """
        Similar to cmd line ``docker images | grep xxx``.
        when name none, show all images
        :param grep: the item for grep. like `tensorflow/tensorflow:1.8.0` for simple match or
                     multiple repositories match like `tensorflow`, or multiple tags match like `1.8.0`...
        """
        images = self.client.images.list(name=None)
        res = [_select_iamge_info(_image.attrs) for _image in images]
        try:
            df = pd.DataFrame(res)
            df = df.explode("REPOSITORY + TAG").reset_index(drop=True)
            # filter NaN in dataframe
            df = df.dropna(axis=0, how='any')  # drop all rows that have any NaN values
            if grep:
                df = df[df["REPOSITORY + TAG"].apply(lambda x: _grep_match(character=grep, string=x))]
            if df.empty:
                _logger.warning("No matched repository or tag !")
        except KeyError:
            df = pd.DataFrame(columns=['REPOSITORY + TAG', 'IMAGE ID', 'CREATED', 'SIZE'])
            _logger.warning("No matched repository or tag !")
        return display(HTML(df.to_html(index=False)))

    def pull_images(self, repository: Optional[str] = None, tag: Optional[str] = None):
        """
        pull images from cluster's own Registry: harbor.stonewise.cn/kubeflow/
        Similar to cmd line ``docker pull``.
        :param repository: you'd better add Registry in your repository
        :param tag: Notice!!! if tag `None`, will push all tags repository from Registry
        """
        if repository:
            if _sub_str(repository, lenght=29) == Registry:
                _repository = repository
            else:
                _repository = Registry + repository
                _logger.warning("Remember to add registry name in your repository, next time !")
            try:
                res = self.client.api.pull(repository=_repository, tag=tag, stream=True, decode=True)
                flag = _docker_progress(res)
                if flag:
                    _logger.info("Pull image successfully !")
                else:
                    _logger.error("Failed to pull image !")
            except requests.exceptions.HTTPError as e:
                print(e)
                _logger.error("Can't find repository in Registry !")
        else:
            _logger.error("You should at least input a repository !")

    def push_images(self, repository: Optional[str] = None, tag: Optional[str] = None):
        """
        push images to cluster's own Registry: harbor.stonewise.cn/kubeflow/
        Similar to cmd line ``docker push``.
        :param repository: you'd better add Registry in your repository
        :param tag: Notice!!! if tag `None`, will push all tags repository from Registry
        :return:
        """
        if repository:
            if _sub_str(repository, lenght=29) == Registry:
                _repository = repository
            else:
                _repository = Registry + repository
                _logger.warning("Remember to add registry name in your repository, next time !")
            res = self.client.api.push(repository=_repository, tag=tag, stream=True, decode=True)
            flag = _docker_progress(res)
            if flag:
                _logger.info("Push image successfully !")
            else:
                _logger.error("Failed to push image !")
        else:
            _logger.error("You should at least input a repository !")

    def build_images(self, path: Optional[str] = None, dockerfile: Optional[str] = None,
                     repository: Optional[str] = None, tag: Optional[str] = None, rm: bool = True,
                     fileobj: Optional[object] = None, push_image: bool = False):
        """
        build remote repository by local config, dockerfile ...
        Similar to the ``docker build`` command.
        Either ``path`` or ``fileobj``
        needs to be set. ``path`` can be a local path (to a directory
        containing a Dockerfile) or a remote URL. ``fileobj`` must be a
        readable file-like object to a Dockerfile.

        :param path: Path to the directory containing the Dockerfile
        :param dockerfile: name of docker file.
        :param repository: the repository to build
        :param tag: the tag to tag
        :param rm: Remove intermediate containers. The ``docker build``
                   command now defaults to ``--rm=true``, but we have kept the old
                   default of `False` to preserve backward compatibility
        :param fileobj: A file object to use as the Dockerfile. (Or a file-like
                        object)
        :param push_image: push repository to Registry, default false.
        """
        if repository:
            if _sub_str(repository, lenght=29) == Registry:
                _repository = repository
            else:
                _repository = Registry + repository
                _logger.warning("Remember to add registry name in your repository, next time !")
            if tag:
                _tag = tag
            else:
                _tag = 'latest'
                _logger.warning("add latest as default tag !")
            streamer = self.client.api.build(path=path, dockerfile=dockerfile, tag=_repository + ':' + _tag, rm=rm,
                                             fileobj=fileobj, decode=True)
            flag = _docker_progress(streamer)
            if flag:
                _logger.info("Build image successfully !")
            else:
                _logger.error("Failed to build image !")
            if push_image:
                self.push_images(repository=repository, tag=tag)  # push built image, just now to Registry
        else:
            _logger.error("You should at least input a repository !")

    def tag_images(self, original_repository: Optional[str] = None, original_tag: Optional[str] = None,
                   target_repository: Optional[str] = None, target_tag: Optional[str] = None, force: bool = False):
        """
        Tag an image into a repository. Similar to the ``docker tag`` command.
        if target_repository target_tag both `None`, default tagged Registry + original_repository:original_tag
        :param original_repository:
        :param original_tag:
        :param target_repository:
        :param target_tag:
        :param force: force tag, default false
        """
        if target_repository:
            _target_tag = target_tag
            if _sub_str(target_repository, lenght=29) == Registry:
                _target_repository = target_repository
            else:
                _target_repository = Registry + target_repository
                _logger.warning("Remember to add registry name in your target repository, next time !")
        else:
            try:
                if _sub_str(original_repository, lenght=29) == Registry:
                    _target_repository = original_repository
                else:
                    _target_repository = Registry + original_repository
                _logger.warning("Use original repository as default target repository !")
            except TypeError:
                _target_repository = None
            if target_tag:
                _target_tag = target_tag
            else:
                _target_tag = original_tag

        if original_repository:
            if original_tag:
                _original = original_repository + ':' + original_tag
            else:
                _original = original_repository
            self.client.api.tag(image=_original, repository=_target_repository, tag=_target_tag, force=force)
            _logger.info("Tag repository successfully !")
        else:
            _logger.error("You should have an original repository !")

    def remove_images(self, repository: Optional[str] = None, tag: Optional[str] = None, image_id: Optional[str] = None,
                      force: bool = False):
        """
        Two options to remove image: use `repository:tag` or `image id`.
        Similar to the ``docker rmi `` command.
        :param repository:
        :param tag:
        :param image_id:
        :param force: remove image by force, default false
        """
        if repository:
            if tag:
                _image = repository + ':' + tag
            else:
                _image = repository
        else:
            if image_id:
                _image = image_id
            else:
                _image = None
        if _image:
            try:
                self.client.api.remove_image(image=_image, force=force)
                _logger.info("Remove image {image} successfully !".format(image=_image))
            except requests.exceptions.HTTPError as ex:
                _logger.error(ex)
        else:
            _logger.error("You should at least input a repository or image id!")

    def save_images(self, repository: Optional[str] = None, tag: Optional[str] = None,
                    chunk_size: Optional[int] = DEFAULT_DATA_CHUNK_SIZE, save_dir: Optional[str] = None,
                    file_name: Optional[str] = None):
        """
        Save an image as tar file in container's pv. Similar to the ``docker save`` command.
        :param repository:
        :param tag:
        :param chunk_size: The number of bytes returned by each iteration
                           of the generator. If ``None``, data will be streamed as it is
                           received. Default: 100 MB
        :param save_dir: if None, the dir script exist
        :param file_name: xxx.tar or xxx.tar.gz, default name `default.tar.gz`
        :return:
        """
        if repository:
            _repository = repository
            if tag:
                _tag = tag
            else:
                _tag = 'latest'
                _logger.warning("add `latest` as default tag !")
            _image = _repository + ":" + _tag

            if file_name:
                _file_name = file_name
            else:
                _file_name = 'default.tar.gz'
                _logger.warning(
                    "Use default file name `default.tar.gz` remember to add tar file name for saving image, next time !")
            if save_dir:
                if os.path.isdir(save_dir):
                    _save_dir = _standard_dir(save_dir)
                else:
                    _save_dir = ''
            else:
                _save_dir = ''  # use current dir
            _save_file = _save_dir + _file_name
            raw_data = self.client.api.get_image(image=_image, chunk_size=chunk_size)
            try:
                with open(_save_file, 'wb') as image_tar:
                    for chunk in raw_data:
                        image_tar.write(chunk)
                _logger.info("Saved image tar file {file} to dir: {dir} successfully !".format(file=_file_name,
                                                                                               dir=_save_dir if _save_dir else 'current dir'))
            except requests.exceptions.HTTPError:
                _logger.error("No such image {repository}:{tag} !".format(repository=_repository, tag=_tag))
        else:
            _logger.error("You should at least input a repository !")

    def load_images(self, file_name: Optional[str] = None, file_dir: str = './'):
        """
        Similar to ``docker load``.
        :param file_name:
        :param file_dir: you'd better user absolute dir, default './'
        """
        path = file_dir + file_name
        with open(path, 'br') as binary_file:
            res = self.client.api.load_image(binary_file)
        flag = _docker_progress(res)
        if flag:
            _logger.info("Load image successfully !")
        else:
            _logger.error("Failed to load image !")

    def show_containers(self, all: bool = False, limit: int = -1, filters: Optional[dict] = {"name":my_container_name}):
        """
        List containers. Similar to the ``docker ps`` command.
        :param all: Show all containers. Only running containers are shown
                    by default
        :param limit: Show `limit` last created containers, include
                      non-running ones
        :param filters: Filters to be processed on the image list.
                Available filters:

                - `exited` (int): Only containers with specified exit code
                - `status` (str): One of ``restarting``, ``running``,
                    ``paused``, ``exited``
                - `label` (str|list): format either ``"key"``, ``"key=value"``
                    or a list of such.
                - `id` (str): The id of the container.
                - `name` (str): The name of the container.
                - `ancestor` (str): Filter by container ancestor. Format of
                    ``<image-name>[:tag]``, ``<image-id>``, or
                    ``<image@digest>``.
                - `before` (str): Only containers created before a particular
                    container. Give the container name or id.
                - `since` (str): Only containers created after a particular
                    container. Give container name or id.

                A comprehensive list can be found in the documentation for
                `docker ps
                <https://docs.docker.com/engine/reference/commandline/ps>`_.
        """
        try:
            containers = self.client.api.containers(all=all, limit=limit, filters=filters)
            res = [_select_containers_info(_container) for _container in containers]
        except requests.exceptions.HTTPError:
            _logger.error("Wrong use of params ！")
            res = []
        if res == []:
            df = pd.DataFrame(
                columns=['CONTAINER ID', 'CREATED', 'STATUS', 'PORTS', 'IMAGE', 'COMMAND', 'CONTAINER NAME'])
            _logger.warning("Can't find select containers !")
        else:
            df = pd.DataFrame(res)
        return display(HTML(df.to_html(index=False)))

    def commit_containers(self, container: Optional[str] = Names, repository: Optional[str] = None,
                          tag: Optional[str] = None, push_image: bool = False):
        """
        Commit a container to an image. Similar to the ``docker commit`` command.
        :param container: container id
        :param repository: The repository to push the image to (you'd better add Registry in your repository)
        :param tag: The tag to push
        ":param push_image: push repository to Registry, default false.
        """
        if repository:
            if _sub_str(repository, lenght=29) == Registry:
                _repository = repository
            else:
                _repository = Registry + repository
                _logger.warning("Remember to add registry name in your repository, next time !")
            if tag:
                _tag = tag
            else:
                _tag = 'latest'
                _logger.warning("add latest as default tag !")
            try:
                self.client.api.commit(container=container, repository=_repository, tag=_tag)
                _logger.info("Commit container sucessfully !")
                if push_image:
                    self.push_images(repository=_repository, tag=_tag)  # push commited image, just now to Registry
            except requests.exceptions.HTTPError:
                _logger.error("No such container: {container}".format(container=container))
        else:
            _logger.error("You should at least input a repository !")

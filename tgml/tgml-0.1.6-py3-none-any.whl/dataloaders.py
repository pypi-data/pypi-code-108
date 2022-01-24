import io
import logging
import math
import os
from queue import Empty, Queue
from threading import Event, Thread
from typing import NoReturn
from urllib.parse import urlparse
from zipfile import ZipFile

import numpy as np
import pandas as pd
import torch
from dotenv import load_dotenv
from pandas import DataFrame

from .data import TigerGraph
from .extras.utilities import (download_from_gcs, download_from_s3,
                               random_string)

__all__ = ["VertexLoader", "EdgeLoader", "GraphLoader", "NeighborLoader"]
__pdoc__ = {"VertexLoader.start_reader": False,
            "GraphLoader.start_reader": False,
            "GraphLoader.start_requester": False,
            "NeighborLoader.start_reader": False,
            "NeighborLoader.start_requester": False}


class BaseLoader:
    def __init__(self,
                 graph: TigerGraph,
                 local_storage_path: str,
                 cloud_storage_path: str,
                 buffer_size: int,
                 output_format: str,
                 num_batches: int,
                 cache_id: str = None,
                 aws_access_key_id: str = None,
                 aws_secret_access_key: str = None):
        """Base Class for data loaders.

        The job of a data loader is to pull data from the TigerGraph database. 
        It can either stream data directly from the server or cache data on the cloud. 
        For the latter, data will be moved to a cloud storage first and then downloaded 
        to local, so it will be slower compared to streaming directly from the server. 
        However, when there are multiple consumers of the same data such as when trying 
        out different models in parallel or tuning hyperparameters, the cloud caching 
        would reduce workload of the server, and consequently it might be faster than 
        hitting the server from multiple consumers at the same time. 

        If using cloud caching, cloud storage access keys need to be provided. For AWS
        s3, `aws_access_key_id` and `aws_secret_access_key` are required.  

        For the first time you initialize the loader on a graph in TigerGraph, 
        the initialization might take half a minute as it installs the corresponding 
        query to the database and optimizes it. However, the query installation only 
        needs to be done once, so it will take no time when you initialize the loader 
        on the same TG graph again.

        Note: For the data loader to work, the *Graph Data Processing Service* has to be 
        running on the TigerGraph server.

        Args:
            graph (TigerGraph): Connection to the TigerGraph database.
            local_storage_path (str): Place to store data locally.
            cloud_storage_path (str): S3 used for cloud caching.
            buffer_size (int): Number of data batches to prefetch and store in memory.
            output_format (str): Format of the output data of the loader.
            num_batches (int): Number of batches to split the whole dataset.
            aws_access_key_id (str, optional): AWS access key. Defaults to None.
            aws_secret_access_key (str, optional): AWS access key secret. Defaults to None.
        """
        self._graph = graph
        if (not cloud_storage_path) or (not cache_id):
            self.cache_id = random_string(6)
        else:
            self.cache_id = cache_id
        self._iterations = 0
        self._payload = {"graph": graph.graph_name,
                         "cloud_storage_path": cloud_storage_path,
                         "num_batches": num_batches,
                         "cache_id": self.cache_id,
                         "iterations": self._iterations}
        self.output_format = output_format
        self.num_batches = num_batches
        self.fulfilled_batches = 0
        # Resolve paths
        self._local_storage_path = local_storage_path
        self._cloud_storage_path = cloud_storage_path
        self._buffer_size = buffer_size
        os.makedirs(local_storage_path, exist_ok=True)
        self._base_endpoint = "{}:8000".format(graph.host)
        # Thread to call database
        self._requester = None
        # Threads to download and load data
        self._downloader = None
        self._reader = None
        # Queues to store tasks and data
        self._request_task_q = None
        self._download_task_q = None
        self._read_task_q = None
        self._data_q = None
        # Exit signal to terminate threads
        self._exit_event = None
        # In-memory data cache. Only used if num_batches=1
        self._data = None
        # Resolve cloud storage keys if cloud storage is used
        self._cloud_keys = None
        if cloud_storage_path:
            if urlparse(cloud_storage_path).scheme == "s3":
                load_dotenv()
                if not aws_access_key_id:
                    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
                if not aws_secret_access_key:
                    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
                if not (aws_access_key_id and aws_secret_access_key):
                    raise Exception("AWS access keys not found")
                self._cloud_keys = aws_access_key_id+' '+aws_secret_access_key

    @staticmethod
    def _request(exit_event: Event, in_q: Queue, out_q: Queue,
                 endpoint: str, params: dict, tgraph: TigerGraph,
                 headers: dict = None, tuple_resp: bool = False) -> NoReturn:
        _params = {}
        _params.update(params)
        while not exit_event.is_set():
            task = in_q.get()
            if task is None:
                in_q.task_done()
                out_q.put(None)
                break
            batch_id, num_batches = task
            _params["batch_id"] = batch_id
            _params["num_batches"] = num_batches
            try:
                resp = tgraph._rest_session.get(endpoint, params=_params,
                                                headers=headers)
            except:
                logging.warning(
                    "Encountered Connection Error. Retry batch {} later.".format(batch_id))
                in_q.task_done()
                in_q.put((batch_id, num_batches))
                continue

            if _params["cloud_storage_path"]:
                # Data are cached in cloud. Put them into download queue.
                resp_json = resp.json()
                if tuple_resp:
                    cloud_file_path = (
                        resp_json["vertex_file"], resp_json["edge_file"])
                else:
                    cloud_file_path = resp_json["file_path"]
                out_q.put(cloud_file_path)
            else:
                # Data are returned in the response.
                if tuple_resp:
                    zip_io = ZipFile(io.BytesIO(resp.content))
                    out_q.put(zip_io)
                else:
                    out_q.put(resp.content)
            in_q.task_done()

    @staticmethod
    def _download_from_cloud(exit_event: Event, in_q: Queue, out_q: Queue,
                             local_dir: str, cloud_keys: str) -> NoReturn:
        def parse_and_download(cloud_url, local_dir, cloud_keys):
            parsed_cloud_url = urlparse(cloud_url)
            if parsed_cloud_url.scheme == "gs":
                local_file = download_from_gcs(cloud_url, local_dir)
            elif parsed_cloud_url.scheme == "s3":
                try:
                    aws_access_key_id, aws_secret_access_key = cloud_keys.split(
                        ' ')
                except:
                    raise Exception("AWS access keys not found")
                local_file = download_from_s3(
                    cloud_url, local_dir, aws_access_key_id, aws_secret_access_key)
            else:
                raise NotImplementedError
            return local_file

        while not exit_event.is_set():
            cloud_url = in_q.get()
            if cloud_url is None:
                in_q.task_done()
                out_q.put(None)
                break
            if isinstance(cloud_url, tuple) and len(cloud_url) == 2:
                # There is a pair of files (edges, vertices) to download
                v_url, e_url = cloud_url
                v_file = parse_and_download(v_url, local_dir, cloud_keys)
                e_file = parse_and_download(e_url, local_dir, cloud_keys)
                out_q.put((v_file, e_file))
            else:
                # There is only one file to download
                local_file = parse_and_download(
                    cloud_url, local_dir, cloud_keys)
                out_q.put(local_file)
            in_q.task_done()

    @staticmethod
    def _read_file(exit_event: Event,
                   in_q: Queue,
                   out_q: Queue,
                   out_format: str = "dataframe",
                   v_in_feats: str = "",
                   v_out_labels: str = "",
                   v_extra_feats: str = "",
                   add_self_loop: bool = False,
                   reindex: bool = False) -> NoReturn:

        def _parse_csv(data,
                       sep: str = ',',
                       headers: list = None,
                       out_format: str = "dataframe"):
            if out_format.lower() == "dataframe":
                if headers:
                    df = pd.read_csv(data, sep=sep, header=None, names=headers)
                else:
                    df = pd.read_csv(data, sep=sep, header=None)
            else:
                raise NotImplementedError
            return df

        def attr_to_tensor(attributes: str, df: pd.DataFrame) -> torch.Tensor:
            x = []
            for attr in attributes.split(','):
                if ':' in attr:
                    col, dtype = attr.split(':')
                    dtype = dtype.lower()
                else:
                    col, dtype = attr, "float32"
                if df[col].dtype == "object":
                    x.append(df[col].str.split(
                        expand=True).to_numpy().astype(dtype))
                else:
                    x.append(
                        df[[col]].to_numpy().astype(dtype))
            return torch.tensor(np.hstack(x).squeeze())

        attributes = [j.split(':')[0] for i in filter(
            None, (v_in_feats, v_out_labels, v_extra_feats)) for j in i.split(',')]
        headers = ["primary_id"] + attributes if attributes else None

        while not exit_event.is_set():
            raw = in_q.get()
            if raw is None:
                in_q.task_done()
                out_q.put(None)
                break
            if isinstance(raw, bytes):
                # Data is an in-memory file
                data = _parse_csv(io.BytesIO(
                    raw), headers=headers, out_format=out_format)
            elif isinstance(raw, str):
                # Data is in a file on disk
                data = _parse_csv(raw, headers=headers, out_format=out_format)
            elif isinstance(raw, ZipFile):
                # Data is in a pair of files (edges, vertices) in a zipfile
                with raw.open("vertices.csv") as infile:
                    vertices = _parse_csv(
                        infile, headers=headers, out_format="dataframe")
                with raw.open("edges.csv") as infile:
                    edges = _parse_csv(
                        infile, headers=["source", "target"], out_format="dataframe")
                raw.close()
                data = (vertices, edges)
            elif isinstance(raw, tuple):
                # Data is in a pair of files (e_file, v_file) on disk
                v_file, e_file = raw
                edges = _parse_csv(
                    e_file, headers=["source", "target"], out_format="dataframe")
                vertices = _parse_csv(
                    v_file, headers=headers, out_format="dataframe")
                data = (vertices, edges)
            else:
                raise NotImplementedError

            if out_format.lower() == "pyg" or out_format.lower() == "dgl":
                if out_format.lower() == "dgl":
                    try:
                        import dgl
                        mode = "dgl"
                    except ImportError:
                        raise ImportError(
                            "DGL is not installed. Please install DGL to use DGL format.")
                elif out_format.lower() == "pyg":
                    try:
                        from torch_geometric.data import Data as pygData
                        from torch_geometric.utils import add_self_loops
                        mode = "pyg"
                    except ImportError:
                        raise ImportError(
                            "PyG is not installed. Please install PyG to use PyG format.")
                else:
                    raise NotImplementedError
                # Reformat as a graph.
                # Need to have a pair of tables for edges and vertices.
                # Deal with edgelist first
                if reindex:
                    vertices["tmp_id"] = range(len(vertices))
                    id_map: DataFrame = vertices[["primary_id", "tmp_id"]]
                    edges: DataFrame = edges.merge(
                        id_map, left_on="source", right_on="primary_id")
                    edges.drop(columns=["source", "primary_id"], inplace=True)
                    edges: DataFrame = edges.merge(
                        id_map, left_on="target", right_on="primary_id")
                    edges.drop(columns=["target", "primary_id"], inplace=True)
                    edges: DataFrame = edges[["tmp_id_x", "tmp_id_y"]]
                else:
                    vertices.sort_values("primary_id", inplace=True)
                if mode == "dgl":
                    edges = torch.tensor(edges.to_numpy().T, dtype=torch.long)
                    data = dgl.graph(data=(edges[0], edges[1]))
                    if add_self_loop:
                        data = dgl.add_self_loop(data)
                elif mode == "pyg":
                    data = pygData()
                    edges = torch.tensor(edges.to_numpy().T, dtype=torch.long)
                    if add_self_loop:
                        edges = add_self_loops(edges)[0]
                    data["edge_index"] = edges
                del edges
                # Deal with vertex attributes next
                if v_in_feats:
                    if mode == "dgl":
                        data.ndata["feat"] = attr_to_tensor(v_in_feats, vertices)
                    elif mode == "pyg":
                        data["x"] = attr_to_tensor(v_in_feats, vertices)
                if v_out_labels:
                    if mode == "dgl":
                        data.ndata["label"] = attr_to_tensor(v_out_labels, vertices)
                    elif mode == "pyg":
                        data['y'] = attr_to_tensor(v_out_labels, vertices)
                if v_extra_feats:
                    for attr in v_extra_feats.split(','):
                        if ':' in attr:
                            col, dtype = attr.split(':')
                            dtype = dtype.lower()
                        else:
                            col, dtype = attr, "float32"
                        if vertices[col].dtype == "object":
                            if mode == "dgl":
                                data.ndata[col] = torch.tensor(vertices[col].str.split(
                                    expand=True).to_numpy().astype(dtype))
                            elif mode == "pyg":
                                data[col] = torch.tensor(vertices[col].str.split(
                                    expand=True).to_numpy().astype(dtype))
                        else:
                            if mode == "dgl":
                                data.ndata[col] = torch.tensor(
                                    vertices[col].to_numpy().astype(dtype))
                            elif mode == "pyg":
                                data[col] = torch.tensor(
                                    vertices[col].to_numpy().astype(dtype))
                del vertices 
            elif out_format.lower() == "dataframe":
                pass
            else:
                raise NotImplementedError
            out_q.put(data)
            in_q.task_done()

    def start_requester(self, out_q: Queue) -> None:
        args = (self._exit_event,
                self._request_task_q,
                out_q,
                self._base_endpoint+"/run",
                self._payload,
                self._graph,
                {"cloud-keys": self._cloud_keys})
        self._requester = Thread(target=self._request, args=args)
        self._requester.start()

    def start_downloader(self) -> None:
        self._downloader = Thread(target=self._download_from_cloud,
                                  args=(self._exit_event,
                                        self._download_task_q,
                                        self._read_task_q,
                                        self._local_storage_path,
                                        self._cloud_keys))
        self._downloader.start()

    def start_reader(self) -> None:
        self._reader = Thread(target=self._read_file,
                              args=(self._exit_event,
                                    self._read_task_q,
                                    self._data_q))

        self._reader.start()

    def start(self) -> None:
        self._request_task_q = Queue()
        self._read_task_q = Queue()
        self._data_q = Queue(self._buffer_size)
        self._exit_event = Event()
        if self._cloud_storage_path:
            self._download_task_q = Queue()
            request_out_q = self._download_task_q
            self.start_downloader()
        else:
            request_out_q = self._read_task_q

        self.start_requester(request_out_q)
        self.start_reader()

        # Populate request queue with the batches to get.
        for i in range(self.num_batches):
            self._request_task_q.put((i, self.num_batches))

    def __iter__(self):
        if self.num_batches == 1:
            return iter([self.data])
        self.reset()
        self.start()
        self._iterations += 1
        self._payload["iterations"] = self._iterations
        return self

    def __next__(self):
        if not self._data_q:
            raise StopIteration
        data = self._data_q.get()
        if data is None:
            raise StopIteration
        self.fulfilled_batches += 1
        if self.fulfilled_batches == self.num_batches:
            # Signal for stop
            self._request_task_q.put(None)
            self.fulfilled_batches = 0
        return data

    @property
    def data(self):
        if self.num_batches == 1:
            if self._data is None:
                self.reset()
                self.start()
                self._data = self._data_q.get()
                self._request_task_q.put(None)
            return self._data
        else:
            return self

    def reset(self) -> None:
        if self._exit_event:
            self._exit_event.set()
        if self._request_task_q:
            self._request_task_q.put(None)
        if self._download_task_q:
            self._download_task_q.put(None)
        if self._read_task_q:
            self._read_task_q.put(None)
        if self._data_q:
            while True:
                try:
                    self._data_q.get(block=False)
                except Empty:
                    break
        logging.debug("Shutting down previous iterator threads")
        if self._requester:
            self._requester.join()
        if self._downloader:
            self._downloader.join()
        if self._reader:
            self._reader.join()
        del self._request_task_q, self._download_task_q, self._read_task_q, self._data_q
        self._exit_event = None
        self._requester, self._downloader, self._reader = None, None, None
        self._request_task_q, self._download_task_q, self._read_task_q, self._data_q = None, None, None, None
        logging.debug("Successfully terminated previous iterator threads")


class EdgeLoader(BaseLoader):
    def __init__(self,
                 graph: TigerGraph,
                 batch_size: int = None,
                 num_batches: int = 1,
                 local_storage_path: str = "./tmp",
                 cloud_storage_path: str = None,
                 buffer_size: int = 4,
                 output_format: str = "dataframe",
                 cache_id: str = None,
                 aws_access_key_id: str = None,
                 aws_secret_access_key: str = None) -> None:
        """Data loader that pulls either the whole edgelist or batches of edges from database. 
        Edge attributes are not supported.

        **Note**: For the first time you initialize the loader on a graph in TigerGraph, 
        the initialization might take half a minute as it installs the corresponding 
        query to the database and optimizes it. However, the query installation only 
        needs to be done once, so it will take no time when you initialize the loader 
        on the same TG graph again. For the data loader to work, the *Graph Data Processing Service* 
        has to be running on the TigerGraph server.

        There are two ways to use the data loader. 
        See [here](https://github.com/tg-bill/mlworkbench-docs/blob/main/tutorials/basics/2_dataloaders.ipynb) 
        for examples.

        * First, it can be used as an iterator, which means you can loop through 
          it to get every batch of data. If you load all edges at once (`num_batches=1`), 
          there will be only one batch (of all the edges) in the iterator.
        * Second, you can access the `data` property of the class directly. If there is 
          only one batch of data to load, it will give you the batch directly instead 
          of an iterator, which might make more sense in that case. If there are 
          multiple batches of data to load, it will return the loader again.

        It can either stream data directly from the server or cache data on the cloud. 
        Set `cloud_storage_path` to turn on cloud cache. This way data will be moved to 
        a cloud storage first and then downloaded to local, so it will be slower compared 
        to streaming directly from the server. However, when there are multiple consumers 
        of the same data such as when trying out different models in parallel or tuning 
        hyperparameters, the cloud caching would reduce workload of the server, and 
        consequently it might be faster overall. If using cloud caching, cloud storage access 
        keys need to be provided. For AWS s3, `aws_access_key_id` and `aws_secret_access_key` 
        are required. However, the class can read from environment variables `AWS_ACCESS_KEY_ID` 
        and `AWS_SECRET_ACCESS_KEY`, and again it is recommended to store those credentials 
        in the `.env` file instead of hardcoding them. 

        Args:
            graph (TigerGraph): Connection to the TigerGraph database.
            batch_size (int, optional): Size of each batch. If given, `num_batches` 
                will be recalculated based on batch size. Defaults to None.
            num_batches (int, optional): Number of batches to split the whole dataset. 
                Defaults to 1.
            local_storage_path (str, optional): Place to store data locally. 
                Defaults to "./tmp".
            cloud_storage_path (str, optional): S3 path used for cloud caching. If not None, cloud caching will be used.
                Defaults to None.
            buffer_size (int, optional): Number of data batches to prefetch and store 
                in memory. Defaults to 4.
            output_format (str, optional): Format of the output data of the loader. 
                Only pandas dataframe is supported. Defaults to "dataframe".
            cache_id (str, optional): An identifier associated to data from this loader. If none, a random string will be used automatically. Defaults to None.
            aws_access_key_id (str, optional): AWS access key for cloud storage. Defaults to None.
            aws_secret_access_key (str, optional): AWS access key secret for cloud storage. Defaults to None.
        """
        super().__init__(graph, local_storage_path, cloud_storage_path,
                         buffer_size, output_format, num_batches, cache_id,
                         aws_access_key_id, aws_secret_access_key)
        # If batch_size is given, calculate the number of batches
        if batch_size:
            self.batch_size = batch_size
            self.num_batches = math.ceil(
                self._graph.number_of_edges()/batch_size)
        else:
            self.num_batches = num_batches
            self.batch_size = math.ceil(
                self._graph.number_of_edges()/num_batches)
        # Initialize the exporter
        self._base_endpoint += "/export/edges"
        self._payload["num_batches"] = self.num_batches
        self._graph._mixed_session.get(
            self._base_endpoint+"/init", params=self._payload)


class VertexLoader(BaseLoader):
    def __init__(self,
                 graph: TigerGraph,
                 batch_size: int = None,
                 num_batches: int = 1,
                 attributes: str = "",
                 local_storage_path: str = "./tmp",
                 cloud_storage_path: str = None,
                 buffer_size: int = 4,
                 output_format: str = "dataframe",
                 cache_id: str = None,
                 aws_access_key_id: str = None,
                 aws_secret_access_key: str = None) -> None:
        """Data loader that pulls either all the vertices or batches of vertices from database. 

        **Note**: For the first time you initialize the loader on a graph in TigerGraph, 
        the initialization might take half a minute as it installs the corresponding 
        query to the database and optimizes it. However, the query installation only 
        needs to be done once, so it will take no time when you initialize the loader 
        on the same TG graph again. For the data loader to work, the *Graph Data Processing Service* 
        has to be running on the TigerGraph server.

        There are two ways to use the data loader.

        * First, it can be used as an iterator, which means you can loop through 
          it to get every batch of data. If you load all vertices at once (`num_batches=1`), 
          there will be only one batch (of all the vertices) in the iterator.
        * Second, you can access the `data` property of the class directly. If there is 
          only one batch of data to load, it will give you the batch directly instead 
          of an iterator, which might make more sense in that case. If there are 
          multiple batches of data to load, it will return the loader again.

        It can either stream data directly from the server or cache data on the cloud. 
        Set `cloud_storage_path` to turn on cloud cache. This way data will be moved to 
        a cloud storage first and then downloaded 
        to local, so it will be slower compared to streaming directly from the server. 
        However, when there are multiple consumers of the same data such as when trying 
        out different models in parallel or tuning hyperparameters, the cloud caching 
        would reduce workload of the server, and consequently it might be faster overall. 
        If using cloud caching, cloud storage access keys need to be provided. For AWS s3, 
        `aws_access_key_id` and `aws_secret_access_key` are required. However, the class 
        can read from environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`, 
        and hence it is recommended to store those credentials in the `.env` file instead of hardcoding them.  

        Args:
            graph (TigerGraph): Connection to the TigerGraph database.
            batch_size (int, optional): Size of each batch. If given, `num_batches` 
                will be recalculated based on batch size. Defaults to None.
            num_batches (int, optional): Number of batches to split the whole dataset. 
                Defaults to 1.
            attributes (str, optional): Vertex attributes to get, separated by comma. 
                Defaults to "".
            local_storage_path (str, optional): Place to store data locally. 
                Defaults to "./tmp".
            cloud_storage_path (str, optional): S3 path used for cloud caching. If not None, cloud caching will be used.
                Defaults to None.
            buffer_size (int, optional): Number of data batches to prefetch and store 
                in memory. Defaults to 4.
            output_format (str, optional): Format of the output data of the loader. 
                Only pandas dataframe is supported. Defaults to "dataframe".
            cache_id (str, optional): An identifier associated to data from this loader. If none, a random string will be used automatically. Defaults to None.
            aws_access_key_id (str, optional): AWS access key for cloud storage. Defaults to None.
            aws_secret_access_key (str, optional): AWS access key secret for cloud storage. Defaults to None.
        """
        super().__init__(graph, local_storage_path, cloud_storage_path,
                         buffer_size, output_format, num_batches, cache_id,
                         aws_access_key_id, aws_secret_access_key)
        self.attributes = attributes
        # If batch_size is given, calculate the number of batches
        if batch_size:
            self.batch_size = batch_size
            self.num_batches = math.ceil(
                self._graph.number_of_vertices()/batch_size)
        else:
            self.num_batches = num_batches
            self.batch_size = math.ceil(
                self._graph.number_of_vertices()/num_batches)
        # Initialize the exporter
        self._base_endpoint += "/export/vertices"
        self._payload["num_batches"] = self.num_batches
        self._payload["attributes"] = attributes
        self._graph._mixed_session.get(
            self._base_endpoint+"/init", params=self._payload)

    def start_reader(self) -> None:
        self._reader = Thread(target=self._read_file,
                              args=(self._exit_event,
                                    self._read_task_q,
                                    self._data_q,
                                    self.output_format,
                                    self.attributes))
        self._reader.start()


class GraphLoader(BaseLoader):
    def __init__(self,
                 graph: TigerGraph,
                 v_in_feats: str = "",
                 v_out_labels: str = "",
                 v_extra_feats: str = "",
                 add_self_loop: bool = False,
                 local_storage_path: str = "./tmp",
                 cloud_storage_path: str = None,
                 buffer_size: int = 4,
                 output_format: str = "PyG",
                 num_batches: int = 1,
                 cache_id: str = None,
                 reindex: bool = False,
                 aws_access_key_id: str = None,
                 aws_secret_access_key: str = None) -> None:
        """Data loader that pulls the whole graph from database. 

        **Note**: For the first time you initialize the loader on a graph in TigerGraph, 
        the initialization might take half a minute as it installs the corresponding 
        query to the database and optimizes it. However, the query installation only 
        needs to be done once, so it will take no time when you initialize the loader 
        on the same TG graph again. For the data loader to work, the *Graph Data Processing Service* 
        has to be running on the TigerGraph server.

        There are two ways to use the data loader. See [here](https://github.com/tg-bill/mlworkbench-docs/blob/main/tutorials/basics/2_dataloaders.ipynb) for examples.

        * First, it can be used as an iterator, which means you can loop through it to get every batch of data. Since this loader loads the whole graph at once, there will be only one batch of data (of the whole graph) in the iterator.
        * Second, you can access the `data` property of the class directly. Since there is only one batch of data (the whole graph), it will give you the batch directly instead of an iterator.

        It can either stream data directly from the server or cache data on the cloud. 
        Set `cloud_storage_path` to turn on cloud cache. This way data will be moved to 
        a cloud storage first and then downloaded 
        to local, so it will be slower compared to streaming directly from the server. 
        However, when there are multiple consumers of the same data such as when trying 
        out different models in parallel or tuning hyperparameters, the cloud caching 
        would reduce workload of the server, and consequently it might be faster overall. 
        If using cloud caching, cloud storage access keys need to be provided. For AWS s3, 
        `aws_access_key_id` and `aws_secret_access_key` are required. However, the class 
        can read from environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`, 
        and hence it is recommended to store those credentials in the `.env` file instead of hardcoding them. 

        Args:
            graph (TigerGraph): Connection to the TigerGraph database.
            v_in_feats (str, optional): Attributes to be used as input features and their types. Attributes should be seperated by ',' and an attribute and its type should be separated by ':'. The type of an attrbiute can be omitted together with the separator ':', and the attribute will be default to type "float32". Defaults to "".
            v_out_labels (str, optional): Attributes to be used as labels for prediction. It follows the same format as 'v_in_feats'. Defaults to "".
            v_extra_feats (str, optional): Other attributes to get such as indicators of train/test data. It follows the same format as 'v_in_feats'. Defaults to "".
            add_self_loop (bool, optional): Whether to add self-loop edges. 
                Defaults to False.
            local_storage_path (str, optional): Place to store data locally. 
                Defaults to "./tmp".
            cloud_storage_path (str, optional): S3 path used for cloud caching. If not None, cloud caching will be used.
                Defaults to None.
            buffer_size (int, optional): Number of data batches to prefetch and store 
                in memory. Defaults to 4.
            output_format (str, optional): Format of the output data of the loader. Only
                "PyG" is supported. Defaults to "PyG".
            reindex (bool, optional): Whether to reindex the vertices. Defaults to False.
            cache_id (str, optional): An identifier associated to data from this loader. If none, a random string will be used automatically. Defaults to None.
            aws_access_key_id (str, optional): AWS access key for cloud storage. Defaults to None.
            aws_secret_access_key (str, optional): AWS access key secret for cloud storage. Defaults to None.
        """
        super().__init__(graph, local_storage_path, cloud_storage_path,
                         buffer_size, output_format, num_batches, cache_id,
                         aws_access_key_id, aws_secret_access_key)
        self.reindex = reindex
        # Resolve attributes
        v_attributes = [j.split(':')[0] for i in filter(
            None, (v_in_feats, v_out_labels, v_extra_feats)) for j in i.split(',')]
        self.v_in_feats = v_in_feats
        self.v_out_labels = v_out_labels
        self.v_extra_feats = v_extra_feats
        self.add_self_loop = add_self_loop
        # Initialize the exporter
        self._base_endpoint += "/export/graph"
        self._payload["v_attributes"] = ','.join(v_attributes)
        resp = self._graph._mixed_session.get(
            self._base_endpoint+"/init", params=self._payload)
        resp.raise_for_status()

    def start_requester(self, out_q: Queue) -> None:
        args = (self._exit_event,
                self._request_task_q,
                out_q,
                self._base_endpoint+"/run",
                self._payload,
                self._graph,
                {"cloud-keys": self._cloud_keys},
                True)
        self._requester = Thread(target=self._request, args=args)
        self._requester.start()

    def start_reader(self) -> None:
        self._reader = Thread(target=self._read_file,
                              args=(self._exit_event,
                                    self._read_task_q,
                                    self._data_q,
                                    self.output_format,
                                    self.v_in_feats,
                                    self.v_out_labels,
                                    self.v_extra_feats,
                                    self.add_self_loop,
                                    self.reindex))
        self._reader.start()


class NeighborLoader(BaseLoader):
    def __init__(self,
                 graph: TigerGraph,
                 tmp_id: str = "tmp_id",
                 v_in_feats: str = "",
                 v_out_labels: str = "",
                 v_extra_feats: str = "",
                 add_self_loop: bool = False,
                 local_storage_path: str = "./tmp",
                 cloud_storage_path: str = None,
                 buffer_size: int = 4,
                 output_format: str = "PyG",
                 batch_size: int = None,
                 num_batches: int = 1,
                 num_neighbors: int = 10,
                 num_hops: int = 2,
                 cache_id: str = None,
                 shuffle: bool = False,
                 filter_by: str = None,
                 aws_access_key_id: str = None,
                 aws_secret_access_key: str = None) -> None:
        """A data loader that performs neighbor sampling as introduced in the 
        [Inductive Representation Learning on Large Graphs](https://arxiv.org/abs/1706.02216) paper. 

        Specifically, it first chooses `batch_size` number of vertices as seeds, 
        then picks `num_neighbors` number of neighbors of each seed at random, 
        then `num_neighbors` neighbors of each neighbor, and repeat for `num_hops`. 
        This generates one subgraph. As you loop through this data loader, all 
        vertices will be chosen as seeds and you will get all subgraphs expanded from those seeds.

        If you want to limit seeds to certain vertices, the boolean attribute provided to `filter_by` will be used to indicate which vertices can be included as seeds.

        **Note**: For the first time you initialize the loader on a graph in TigerGraph, 
        the initialization might take half a minute as it installs the corresponding 
        query to the database and optimizes it. However, the query installation only 
        needs to be done once, so it will take no time when you initialize the loader 
        on the same TG graph again. For the data loader to work, the *Graph Data Processing Service* 
        has to be running on the TigerGraph server.

        There are two ways to use the data loader. See [here](https://github.com/tg-bill/mlworkbench-docs/blob/main/tutorials/basics/2_dataloaders.ipynb) for examples.

        * First, it can be used as an iterator, which means you can loop through 
          it to get every batch of data. If you load all edges at once (`num_batches=1`), 
          there will be only one batch (of all the edges) in the iterator.
        * Second, you can access the `data` property of the class directly. If there is 
          only one batch of data to load, it will give you the batch directly instead 
          of an iterator, which might make more sense in that case. If there are 
          multiple batches of data to load, it will return the loader again.

        It can either stream data directly from the server or cache data on the cloud. 
        Set `cloud_storage_path` to turn on cloud cache. This way data will be moved to 
        a cloud storage first and then downloaded 
        to local, so it will be slower compared to streaming directly from the server. 
        However, when there are multiple consumers of the same data such as when trying 
        out different models in parallel or tuning hyperparameters, the cloud caching 
        would reduce workload of the server, and consequently it might be faster overall. 
        If using cloud caching, cloud storage access keys need to be provided. For AWS s3, 
        `aws_access_key_id` and `aws_secret_access_key` are required. However, the class 
        can read from environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`, 
        and hence it is recommended to store those credentials in the `.env` file instead of hardcoding them. 

        Args:
            graph (TigerGraph): Connection to the TigerGraph database.
            tmp_id (str, optional): Attribute name that holds the temporary ID of 
                vertices. Defaults to "tmp_id".
            v_in_feats (str, optional): Attributes to be used as input features and their types. Attributes should be seperated by ',' and an attribute and its type should be separated by ':'. The type of an attrbiute can be omitted together with the separator ':', and the attribute will be default to type "float32". and Defaults to "".
            v_out_labels (str, optional): Attributes to be used as labels for prediction. It follows the same format as 'v_in_feats'. Defaults to "".
            v_extra_feats (str, optional): Other attributes to get such as indicators of train/test data. It follows the same format as 'v_in_feats'. Defaults to "".
            add_self_loop (bool, optional): Whether to add self-loops to the graph. 
                Defaults to False.
            local_storage_path (str, optional): Place to store data locally. 
                Defaults to "./tmp".
            cloud_storage_path (str, optional): S3 path used for cloud caching. If not None, cloud caching will be used.
                Defaults to None.
            buffer_size (int, optional): Number of data batches to prefetch and store 
                in memory. Defaults to 4.
            output_format (str, optional): Format of the output data of the loader. Only
                "PyG" is supported. Defaults to "PyG".
            batch_size (int, optional): Number of vertices as seeds in each batch. 
                Defaults to None.
            num_batches (int, optional): Number of batches to split the vertices. 
                Defaults to 1.
            num_neighbors (int, optional): Number of neighbors to sample for each vertex. 
                Defaults to 10.
            num_hops (int, optional): Number of hops to traverse when sampling neighbors. 
                Defaults to 2.
            shuffle (bool, optional): Whether to shuffle the vertices after every epoch. 
                Defaults to False.
            filter_by (str, optional): A boolean attribute used to indicate which vertices 
                can be included as seeds. Defaults to None.
            cache_id (str, optional): An identifier associated to data from this loader. If none, a random string will be used automatically. Defaults to None.
            aws_access_key_id (str, optional): AWS access key for cloud storage. Defaults to None.
            aws_secret_access_key (str, optional): AWS access key secret for cloud storage. Defaults to None.
        """
        super().__init__(graph, local_storage_path, cloud_storage_path,
                         buffer_size, output_format, num_batches, cache_id,
                         aws_access_key_id, aws_secret_access_key)
        # Resolve attributes
        v_attributes = [j.split(':')[0] for i in filter(
            None, (v_in_feats, v_out_labels, v_extra_feats)) for j in i.split(',')]
        self.v_in_feats = v_in_feats
        self.v_out_labels = v_out_labels
        self.v_extra_feats = v_extra_feats
        self.add_self_loop = add_self_loop
        # If batch_size is given, calculate the number of batches
        if batch_size:
            self.batch_size = batch_size
            self.num_batches = math.ceil(
                self._graph.number_of_vertices(filter_by=filter_by)/batch_size)
        else:
            self.num_batches = num_batches
            self.batch_size = math.ceil(
                self._graph.number_of_vertices(filter_by=filter_by)/num_batches)
        # Initialize temp ID for every vertex
        self._payload["tmp_id"] = tmp_id
        resp = self._graph._mixed_session.get(
            self._base_endpoint + "/shuffle/vertices/init", params=self._payload)
        resp.raise_for_status()
        self.shuffle = shuffle
        # Initialize the sampler
        self._base_endpoint += "/sample/neighbor"
        self._payload["v_attributes"] = ','.join(v_attributes)
        self._payload["num_neighbors"] = num_neighbors
        self._payload["num_hops"] = num_hops
        self._payload["filter_by"] = filter_by
        resp = self._graph._mixed_session.get(
            self._base_endpoint+"/init", params=self._payload)
        resp.raise_for_status()

    def start_requester(self, out_q: Queue) -> None:
        args = (self._exit_event,
                self._request_task_q,
                out_q,
                self._base_endpoint+"/run",
                self._payload,
                self._graph,
                {"cloud-keys": self._cloud_keys},
                True)
        self._requester = Thread(target=self._request, args=args)
        self._requester.start()

    def start_reader(self) -> None:
        self._reader = Thread(target=self._read_file,
                              args=(self._exit_event,
                                    self._read_task_q,
                                    self._data_q,
                                    self.output_format,
                                    self.v_in_feats,
                                    self.v_out_labels,
                                    self.v_extra_feats,
                                    self.add_self_loop,
                                    True))
        self._reader.start()

    def __iter__(self):
        if self.num_batches == 1:
            return iter([self.data])
        if self._iterations == 0 or self.shuffle:
            resp = self._graph._rest_session.get(
                "{}:8000/shuffle/vertices/run".format(self._graph.host), params=self._payload)
            resp.raise_for_status()
        self.reset()
        self.start()
        self._iterations += 1
        self._payload["iterations"] = self._iterations
        return self

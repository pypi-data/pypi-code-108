import ast
import hashlib
import json
import logging
import re
import urllib.parse
from io import BytesIO

import pandas as pd

from brevettiai.data.sample_integrity import load_sample_identification, save_sample_identification, SampleSplit
from brevettiai.data.sample_tools import BrevettiDatasetSamples, get_samples, save_samples
from brevettiai.interfaces import vue_schema_utils as vue
from brevettiai.io import io_tools
from brevettiai.data.image import ImageKeys
import numpy as np

log = logging.getLogger(__name__)

DATASET_ROOT = "__root__"

__all__ = ["tif2dzi", "BrevettiDatasetSamples", "load_sample_identification", "save_sample_identification",
           "SampleSplit", "get_samples", "save_samples"]

DATASET_LOCATIONS = dict(
    annotations=".annotations",
    meta=".meta",
    samples=".samples",
    data="",
)


class DatasetSchema(vue.SchemaBuilderFunc):
    label = "Data"
    ns = "data"
    sharding = [["dataset", "category"], ["category"]]

    def schema(self, b, ns, **kwargs):
        # Class definitions and mapping
        b.add_field(vue.field_classes(model=ns + "classes"))
        b.add_field(vue.field_class_mapping(model=ns + "class_mapping"))

        # Purpose assignment
        ns_purpose = ns + "purpose."
        b.add_field(vue.number_input("Training split ratio", model=ns_purpose + "split",
                                     default=0.8, min=0, max=1, step=0.05))
        b.add_field(vue.select("Sample purpose stratification", model=ns_purpose + "stratification",
                               default=self.sharding[0], values=self.sharding, json=True))
        b.add_field(vue.text_input("Custom sample purpose stratification", model=ns_purpose + "stratification",
                                   default=self.sharding[0], required=False, json=True))
        b.add_field(vue.text_input("Sample purpose uniqueness", model=ns_purpose + "uniqueness", json=True))


def get_category(mapping, keys, default=None):
    try:
        key, keys = keys[0], keys[1:]
        default = default or key
        if keys:
            return mapping.get(key, get_category(mapping, keys, default=default))
        else:
            return mapping.get(key, default)
    except IndexError:
        return mapping.get(default[0], default)


class Dataset:
    def __init__(self, bucket, id="", name="", reference=None, locked=False, tags=None, notes=None,
                 host_name="https://platform.brevetti.ai", resolve_access_rights=True, io=io_tools, **kwargs):
        self.io = io
        self.host_name = host_name
        self.id = id
        self.bucket = bucket
        self.name = name
        self.reference = reference or "N/A"
        self.locked = locked
        self.tags = tags or []
        self.notes = notes
        self.meta = kwargs

        self._uri_offset = self._get_uri_offset(self.bucket)

        if resolve_access_rights:
            self.resolve_access_rights()

    def resolve_access_rights(self):
        self.io.resolve_access_rights(path=self.bucket, resource_id=self.id, resource_type="dataset", mode='w')

    @staticmethod
    def from_s3(id, name=None, old=False, bucket="data.criterion.ai", *args, **kwargs):
        """Utility function for creating Criterion Datasets in without full json object"""
        name = name or id
        if old:
            bucket = f"s3://{bucket}/{id}.datasets.criterion.ai"
        else:
            bucket = f"s3://{bucket}/{id}"
        return Dataset(id=id, bucket=bucket, name=name, *args, **kwargs)

    def get_image_samples(self, sample_filter=r".+(\.tif|\.bmp|\.jpeg|\.jpg|\.png|\.JPG)$",
                          annotations=False, location="data", **kwargs):
        """
        :param sample_filter: Filter samples by regex
        :param annotations: boolean, or dict Load annotation paths
        :param location: location in dataset ("data", "annotations", "samples", or path in dataset to search under)
        :param kwargs:
        :return: Dataframe of samples

        Mapping from path to category:
        Start from the leaf folder, and work towards the dataset root folder. If folder in class_mapping then apply
        its key as the category. If no match is found, apply leaf folder name
        Example:
        class_mapping={
        "A": ["Tilted"],
        "B": ["Tilted"],
        "1": ["Crimp"]
        }
        If classes is True or a list/set of categories. The filter is applied after the mapping.
        """
        log.info(f"Getting image samples from dataset '{self.name}' [{self.get_uri()}]")
        samples = self.find_files(self.get_location(location), sample_filter=sample_filter, exclude_hidden=True,
                                  **kwargs)
        if annotations is not False:
            for ann in annotations if isinstance(annotations, (tuple, list)) else [annotations]:
                samples = self.merge_annotations(samples, **(ann if isinstance(ann, dict) else {}))

        samples["bucket"] = self.bucket
        samples["dataset"] = self.name
        samples["dataset_id"] = self.id
        samples["reference"] = self.reference
        samples["url"] = samples.path.apply(self.get_sample_uri)
        log.info(f"Contents: {samples.category.value_counts().to_dict()}")
        return samples

    def get_annotations(self, filter=None):
        log.info(f"Getting annotations from dataset '{self.name}' [{self.get_uri()}] with filter: {filter}")
        samples = self.find_files(self.get_location("annotations"),
                                  sample_filter=filter,
                                  default_category_folder_index=-2, full_path=True)
        return samples

    def merge_annotations(self, samples, filter=None, duplicates="last", how="inner", prefix="segmentation_"):
        """
        :param samples: Samples to merge with annotations
        :param filter: Annotation filter
        :param duplicates: What to do about duplicate annotations
        True: include all, False: remove all, 'first': keep first, 'last' keep last
        :param how: Join mode between samples and annotations
        :param prefix: naming prefix for annotation file paths
        :return:
        """
        samples.index = samples.path.apply(self.get_ds_path)
        ann = self.get_annotations(filter=filter).set_index("folder")
        del ann["category"]
        if duplicates is not True:
            ann = ann[~ann.index.duplicated(keep=duplicates)]
        samples = samples.join(ann.add_prefix(prefix), how=how)
        mask = samples.select_dtypes(include=["number", "bool", "object"]).columns
        samples[mask] = samples[mask].fillna("")
        return samples.reset_index(drop=True)

    def get_samples(self, target):
        """
        Get samples from sample definition file located in .samples
        :param target: file path from bucket/.samples/
        :return: pandas dataframe of samples
        """
        target = (target,) if isinstance(target, str) else target
        sample_file = self.get_location("samples", *target)
        sep = self.io.path.get_sep(self.bucket)
        if self.io.isfile(sample_file):
            df = pd.read_csv(BytesIO(self.io.read_file(sample_file)), sep=";")
            if df.shape[1] == 1:
                df = pd.read_csv(BytesIO(self.io.read_file(sample_file)))
        else:
            df = pd.DataFrame(dict(path=["NaN"], category=[("NaN",)]))[:0]
        if ImageKeys.SIZE in df:
            df[ImageKeys.SIZE] = df[ImageKeys.SIZE].apply(lambda sz: np.array(json.loads(sz)))
        df["folder"] = df.path.str.rsplit(sep, 2).str[-2].fillna(DATASET_ROOT)  # path is still relative path
        df.path = df.path.apply(lambda pp: self.io.path.join(self.bucket, pp))
        if "segmentation_path" in df:
            df.segmentation_path = df.segmentation_path.fillna("")
            df.segmentation_path = df.segmentation_path.apply(lambda sp: self.io.path.join(self.bucket, sp))
        df["bucket"] = self.bucket
        df["dataset"] = self.name
        df["dataset_id"] = self.id
        df["url"] = df.path.apply(self.get_sample_uri)
        df["category"] = df.category.apply(ast.literal_eval)
        return df

    def save_samples(self, target, df):
        """
        Save samples in dataset to samples file
        :param target:
        :param df:
        :return:
        """
        target = (target,) if isinstance(target, str) else target
        sample_file = self.get_location("samples", *target)

        # Only save samples from this dataset
        df = df[df.path.str.startswith(self.bucket)]
        # Only save non known columns
        df = df.iloc[:, ~df.columns.isin({"folder", "bucket", "dataset", "dataset_id", "url"})]
        df.path = df.path.apply(self.get_ds_path)
        if "segmentation_path" in df:
            df.segmentation_path = df.segmentation_path.apply(self.get_ds_path)
        self.upload(sample_file, df.to_csv(index=False, sep=";"))

    def get_meta(self, filter=None):
        return self.find_files(self.get_location("meta"),
                               sample_filter=filter,
                               default_category_folder_index=-2, full_path=True)

    def find_files(self, path=None, *args, **kwargs):
        path = path or self.bucket
        return pd.DataFrame(self.sample_walk(path, *args, **kwargs),
                            columns=("category", "folder", "path", "etag"))

    def sample_walk(self, bucket, sample_filter=None, class_mapping: dict = None, classes: list = None,
                    default_category=(DATASET_ROOT,),
                    exclude_hidden=False, default_category_folder_index=-1, full_path=False, calculate_md5=True,
                    **kwargs):
        class_mapping = class_mapping or {}
        classes = classes or []

        if isinstance(sample_filter, (list, tuple, set)):
            sample_filter = "|".join(map(str, sample_filter))
        if isinstance(sample_filter, str):
            sample_filter = re.compile(sample_filter).search
        class_mapping = {k: ((v,) if isinstance(v, str) else tuple(v)) for k, v in class_mapping.items()}

        bucket_offset = len(bucket)
        sep = self.io.path.get_sep(bucket)
        for r, dirs, files in self.io.walk(bucket, exclude_hidden=exclude_hidden, include_object=True):
            rel_path = r[bucket_offset:].strip(sep)
            folders = [] if rel_path == '' else [DATASET_ROOT] + rel_path.split(sep)
            def_cat = (folders[default_category_folder_index],) if folders else default_category
            category = get_category(class_mapping, folders[::-1], def_cat)

            if classes:
                if isinstance(category, str):  # If category is string make sure it is in allowed classes
                    if category not in classes:
                        continue
                elif len(category) > 0:  # IF category is not empty filter allowed classes
                    category = tuple(c for c in category if c in classes)
                    if len(category) == 0:
                        continue

            if len(files) > 0:
                for file in files:
                    if isinstance(file, tuple):
                        file, fobj = file
                    else:
                        fobj = None

                    if sample_filter is None or sample_filter(file.lower()):
                        folder = rel_path if full_path else (DATASET_ROOT, *folders)[-1]
                        path = self.io.path.join(r, file)
                        if calculate_md5 and (fobj is None or len(fobj.etag) != 32 or "-" in fobj.etag):
                            etag = self.io.get_md5(path)
                        elif fobj is None:
                            etag = hashlib.sha1(path.encode("utf8")).hexdigest()
                        else:
                            etag = fobj.etag
                        yield category, folder, path, etag

    @staticmethod
    def _get_uri_offset(bucket):
        start = bucket.find("://") + 3
        return bucket.find("/", start) + 1

    def get_uri(self):
        return f"{self.host_name}/data/{self.id}"

    def get_sample_uri(self, path):
        return f"{self.host_name}/download?path={urllib.parse.quote(path[self._uri_offset:], safe='')}"

    def upload(self, path, data):
        pth = self.get_location(path)
        return self.io.write_file(pth, data)

    def get_ds_path(self, path):
        return path[len(self.bucket) + 1:]

    def get_location(self, mode, *path):
        """Get path to object, prefixing 'annotations', 'data', 'samples' with . if they are in the first argument """
        location = DATASET_LOCATIONS.get(mode, mode)

        path = (location, *path) if location else path
        return self.io.path.join(self.bucket, *path)

    def __str__(self):
        return json.dumps({k: v for k, v in self.__dict__.items() if not k.startswith("_")})


def tif2dzi(path, bucket):
    if ".tif" in path:
        rel_path = path.replace(bucket, "").strip("/")
        return io_tools.path.join(bucket.strip("/"), ".tiles", rel_path, "dzi.json")
    else:
        return path

from rio_cogeo.cogeo import cog_validate, cog_info
import boto3
from dataclasses import dataclass
from rasterio.io import MemoryFile
from rio_cogeo.cogeo import cog_translate
from rio_cogeo.profiles import cog_profiles
from typing import List
from pyproj import Transformer
import os


@dataclass
class S3Cog:
    filepath: str
    filename: str
    bucket_name: str
    s3_object_name: str
    s3_path: str


@dataclass
class LayerInfo:
    bbox_wgs84: List[float]
    resolution: float
    minzoom: int
    maxzoom: int


def create_s3_cog_info(bucket_name: str, layer_id: str, filepath: str) -> S3Cog:
    filename = os.path.basename(filepath)
    object_name = f"layer/{layer_id}/{filename}"
    s3_path = f"s3://{bucket_name}/{object_name}"
    return S3Cog(s3_object_name=object_name, s3_path=s3_path, bucket_name=bucket_name, filename=filename,
                 filepath=filepath)


def upload_cog_file(s3_cog: S3Cog) -> bool:
    s3_client = boto3.client('s3')

    try:
        s3_client.upload_file(s3_cog.filepath, s3_cog.bucket_name, s3_cog.s3_object_name)
    except Exception:
        return False
    return True


def transform_upload_cog(s3_cog: S3Cog, cog_profile: str) -> bool:
    client = boto3.client("s3")
    dst_profile = cog_profiles.get(cog_profile)

    try:
        with MemoryFile() as mem_dst:
            cog_translate(s3_cog.filepath, mem_dst.name, dst_profile, in_memory=True, web_optimized=True)
            client.upload_fileobj(mem_dst, s3_cog.bucket_name, s3_cog.s3_object_name)
    except Exception:
        return False
    return True


def layer_is_valid_cog(filepath: str) -> bool:
    result = cog_validate(filepath)
    return result == (True, [], [])


def pairwise(iterable):
    a = iter(iterable)
    return zip(a, a)


def transform_bbox(bbox, in_proj: str, out_proj: str = "EPSG:4326") -> List[float]:
    transformer = Transformer.from_crs(in_proj, out_proj)
    bbox_wgs84 = [transformer.transform(x, y) for x, y in pairwise(bbox)]

    return list(sum(bbox_wgs84, ()))


def get_layer_info(filename: str) -> LayerInfo:
    result = cog_info(filename)
    geo_info = result["GEO"]
    bbox_wgs84 = transform_bbox(geo_info["BoundingBox"], geo_info["CRS"])
    bbox_wgs84 = [round(x, 6) for x in bbox_wgs84]

    return LayerInfo(bbox_wgs84=bbox_wgs84, resolution=float(geo_info["Resolution"][0]),
                     maxzoom=geo_info["MaxZoom"], minzoom=geo_info["MinZoom"])

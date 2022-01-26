import os
import logging
import uuid
import numpy as np
import urllib

log = logging.getLogger(__name__)


class PlatformBackend:
    """
    Environment class for holding a platform environment context
    """
    def __init__(self,
                 host=os.getenv("BREVETTIAI_HOST_NAME", "https://platform.brevetti.ai"),
                 data_bucket=None,
                 output_segmentation_dir="output_segmentations"):
        self.host = host
        self.data_bucket = data_bucket
        self.bucket_region = os.getenv("AWS_REGION", "eu-west-1")
        self.output_segmentation_dir = output_segmentation_dir

    @property
    def s3_endpoint(self):
        return f"s3.{self.bucket_region}.amazonaws.com"

    @property
    def data_bucket(self):
        if self._data_bucket is None:
            self._data_bucket = os.getenv("BREVETTIAI_DATA_BUCKET", "s3://data.criterion.ai")
        return self._data_bucket

    @data_bucket.setter
    def data_bucket(self, value):
        self._data_bucket = value

    def job_dir(self, job_guid):
        """
        Get job directory path on platform
        :param job_guid:
        :return:
        """
        try:
            uuid.UUID('urn:' + str(job_guid), version=1)
        except ValueError as ex:
            raise ValueError(f"Bad job_guid: {job_guid}") from ex
        return f"{self.data_bucket}/{job_guid}"

    def get_download_link(self, path):
        if path.startswith("s3://"):
            target = path[5:].split("/", 1)[1]
            return f"{self.host}/download?path={urllib.parse.quote(target, safe='')}"
        else:
            raise ValueError("Can only provide download links on s3")

    def get_artifact_path(self, model, *path_args):
        from brevettiai.io import io_tools
        try:
            uuid.UUID('urn:' + model, version=1)
        except ValueError:
            return io_tools.path.join(model, "artifacts", *path_args)
        return f"{self.host}/{model}/artifacts/{'/'.join(path_args)}"

    def get_annotation_url(self, s3_image_path, annotation_name=None,
                           bbox=None, zoom=None, screen_size=1024, test_report_id=None, model_id=None,
                           min_zoom=2, max_zoom=300):
        """
        Get url to annotation file
        :param s3_image_path: Name of image file
        :param annotation_name: Name of annotation file, if any
        :param bbox: Selects zoom and center for the bbox
        :param zoom: Zoom level [2-300] related to screen pixel size (if None zoom will be calculated from bbox)
        :param screen_size: default screen size in pixels
        """

        uri_length = 36
        rm_keys = [self.data_bucket, ".tiles/", "/dzi.json"]
        image_key = s3_image_path
        for rm_key in rm_keys:
            image_key = image_key.replace(rm_key, "")
        image_key = image_key.lstrip("/")
        dataset_id = image_key[:uri_length]
        image_rel_path = "/".join(image_key.split("/")[1:])

        url_info = dict(file=image_rel_path)

        if annotation_name:
            url_info["annotationFile"] = annotation_name

        if test_report_id:
            url_info["testReportId"] = test_report_id

        if model_id:
            url_info["modelId"] = model_id

        if bbox is not None:
            url_info["x"], url_info["y"] = np.array(bbox).reshape(2, 2).mean(0).astype(np.int)
            # NB: This will be overwritten if zoom is provided
            url_info["zoom"] = int((100 * screen_size / np.array(bbox).reshape(2, 2).T.dot([-1, 1])).\
                                   clip(min=min_zoom, max=max_zoom).min())

        if zoom:
            url_info["zoom"] = zoom

        return "https://platform.brevetti.ai/data/{}?".format(dataset_id) + urllib.parse.urlencode(url_info)


backend = PlatformBackend()

import logging
import os
import pathlib
import posixpath
import urllib.parse

from mlflow.entities import FileInfo
from mlflow.store.artifact.artifact_repo import ArtifactRepository

logger = logging.getLogger(__name__)


class OSSArtifactRepository(ArtifactRepository):

    def __init__(self, *args, **kwargs):
        super(OSSArtifactRepository, self).__init__(*args, **kwargs)
        logger.debug("init with artifact_uri: %s", self.artifact_uri)
        try:
            uri = urllib.parse.urlparse(self.artifact_uri)
            self.obj_key_prefix = uri.path.lstrip("/")
            self.bucket = self._create_oss_client(bucket_name=uri.hostname)
        except Exception as ex:
            logger.error("failed to initialize OSS client", ex)

    def log_artifact(self, local_file, artifact_path=None):
        logger.debug("log artifact: %s => %s", local_file, artifact_path)
        artifact_path = self._normalize_artifact_path(artifact_path)
        obj_key = posixpath.abspath(posixpath.join(artifact_path, os.path.basename(local_file))).lstrip("/")
        self.bucket.put_object_from_file(posixpath.join(self.obj_key_prefix, obj_key), local_file)

    def log_artifacts(self, local_dir, artifact_path=None):
        logger.debug("log artifacts: %s => %s", local_dir, artifact_path)
        artifact_path = self._normalize_artifact_path(artifact_path)
        for (root, _, filenames) in os.walk(local_dir):
            dest_path = posixpath.join(artifact_path, pathlib.Path(root).relative_to(local_dir).as_posix())
            for fn in filenames:
                local_file = os.path.join(root, fn)
                self.log_artifact(local_file, dest_path)

    def list_artifacts(self, path):
        logger.debug("list artifacts: %s, obj_key_prefix: %s", path, self.obj_key_prefix)
        prefix = posixpath.join(self.obj_key_prefix, self._normalize_artifact_path(path).strip("/")).rstrip("/") + "/"
        logger.debug("listing objects with prefix: %s", prefix)
        objects = self.bucket.list_objects_v2(prefix, delimiter="/")
        results = []
        for obj in objects.object_list:
            logger.debug("object found: %s", obj.key)
            results.append(FileInfo(obj.key.removeprefix(self.obj_key_prefix).lstrip("/"), False, obj.size))
        for path in objects.prefix_list:
            logger.debug("prefix found: %s", path)
            results.append(FileInfo(path.removeprefix(self.obj_key_prefix).strip("/"), True, 0))
        return sorted(results, key=lambda x: x.path)

    def _download_file(self, remote_file_path, local_path):
        artifact_path = self._normalize_artifact_path(remote_file_path)
        obj_key = artifact_path.lstrip("/")
        self.bucket.get_object_to_file(posixpath.join(self.obj_key_prefix, obj_key), local_path)

    def _normalize_artifact_path(self, artifact_path):
        if artifact_path is None:
            return "/"
        return "/" + artifact_path.lstrip("/")

    @staticmethod
    def _create_oss_client(bucket_name):
        import oss2
        endpoint = os.environ.get("MLFLOW_OSS_ENDPOINT_URL", "https://oss-cn-shanghai.aliyuncs.com")
        access_key_id = os.environ["MLFLOW_OSS_KEY_ID"]
        access_key_secret = os.environ["MLFLOW_OSS_KEY_SECRET"]
        auth = oss2.Auth(access_key_id, access_key_secret)
        return oss2.Bucket(auth, endpoint, bucket_name)

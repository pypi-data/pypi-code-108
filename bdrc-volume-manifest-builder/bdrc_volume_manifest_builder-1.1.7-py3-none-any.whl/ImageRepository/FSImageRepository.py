import json
import os
from pathlib import Path
from typing import Tuple

import v_m_b.manifestCommons as Common
from v_m_b.ImageRepository.ImageGroupResolver import ImageGroupResolver
from v_m_b.ImageRepository.ImageRepositoryBase import ImageRepositoryBase
from v_m_b.VolumeInfo.VolInfo import VolInfo
# You only use onf generateManifest_a or _s
from v_m_b.image.generateManifest import generateManifest_s


class FSImageRepository(ImageRepositoryBase):

    def manifest_exists(self, work_Rid: str, image_group_id: str) -> bool:
        """
        tests for a well known item in the repository
        :param work_Rid:
        :param image_group_id:
        :return:
        """
        return Path(self.resolveImageGroup(work_Rid, image_group_id), 'dimensions.json').exists()

    def generateManifest(self, work_Rid: str, vol_info: VolInfo) -> []:
        if self.manifest_exists(work_Rid, vol_info.imageGroupID):
            self.repo_log.info(f"manifest exists for work {work_Rid} image group {vol_info.imageGroupID}")
        manifest: [] = []
        full_path: Path = self.resolveImageGroup(work_Rid, vol_info.imageGroupID)
        if full_path.exists():
            # manifest = asyncio.run(generateManifest_a(full_path, vol_info.image_list))
            manifest = generateManifest_s(full_path, vol_info.image_list)
        return manifest

    def __init__(self, bom_key: str, source_root: str, images_name: str):
        """
        Creation.
        :param source_root: parent of all works in the repository. Existing directory name
        :param images_name: subfolder of the work which contains the image group folders
        """
        super(FSImageRepository, self).__init__(bom_key)
        self._container = source_root
        self._image_folder_name = images_name
        self._IGResolver = ImageGroupResolver(source_root, images_name)

    def getImageNames(self, work_rid: str, image_group: str, bom_name: str) -> []:
        """
        File system implementation
        :param work_rid: locator
        :param image_group: locator
        :param bom_name: file name of BOM
        :return: list of images in an image group, either from the BOM or by listing all the non json files in a folder
        """

        bom_home = self.resolveImageGroup(work_rid, image_group)
        bom_path = Path(bom_home, bom_name)

        image_list: [] = []

        # try reading the bom first
        if bom_path.exists():
            with open(bom_path, "rb") as f:
                json_body = json.loads(f.read())
                image_list = [x[Common.VMT_BUDABOM_JSON_KEY] for x in json_body]
        else:
            if bom_home.exists():
                image_list = [f for f in os.listdir(str(bom_home)) if os.path.isfile(Path(bom_home, f))
                              and not str(f).lower().endswith('json')]
        return image_list

    def uploadManifest(self, work_rid: str, image_group: str, bom_name: str, manifest_zip: bytes):
        """
        FS implemenation
        :param work_rid:
        :param image_group:
        :param bom_name: output object name
        :param manifest_zip:
        :return:
        """
        bom_path = Path(self.resolveImageGroup(work_rid, image_group), bom_name)
        with open(bom_path, "wb") as upl:
            upl.write(manifest_zip)

    def getPathfromLocators(self, work_Rid: str, image_group_id: str) -> str:
        """
        :param work_Rid: Work resource id
        :param image_group_id: image group - gets transformed
        :returns:  the s3 prefix (~folder) in which the volume will be present.
        gives the s3 prefix (~folder) in which the volume will be present.
        inpire from https://github.com/buda-base/buda-iiif-presentation/blob/master/src/main/java/
        io/bdrc/iiif/presentation/ImageInfoListService.java#L73
        Example:
           - work_Rid=W22084, imageGroupID=I0886
           - result = "Works/60/W22084/images/W22084-0886/
        where:
           - 60 is the first two characters of the md5 of the string W22084
           - 0886 is:
              * the image group ID without the initial "I" if the image group ID is in the form I\\d\\d\\d\\d
              * or else the full image group ID (incuding the "I")
        """
        suffix = self.getImageGroup(image_group_id)
        parent, rid = self.resolveWork(work_Rid)
        return f"{parent}/{self._image_folder_name}/{rid}-{suffix}"

    def resolveWork(self, work_rid_path: str) -> Tuple[str, str]:
        """
        Resolve work, possibly from path
        :param work_rid_path:
        :return: the path and the work_rid
        """
        w_path = self.fullPath(str(Path(self._container, work_rid_path)))
        return os.path.dirname(w_path), os.path.basename(w_path)

    def resolveImageGroup(self, work_Rid: str, image_group_folder_name: str) -> Path:
        """
        Fully qualifies a RID and a Path
        :param work_Rid:
        :param image_group_folder_name: Image group folder name
        :return: fully qualified path to image group. The I{d}{4} issue is resolved in VolInfo
        """
        _work: str
        _dir, _work = self.resolveWork(work_Rid)
        # shouldn't need this any more, moved into Volinfos
        # image_group_folder_name: str = self.getImageGroup(image_group_name)
        pre_path = Path(_dir, _work, self._image_folder_name)
        v1path = Path(pre_path, f"{_work}-{image_group_folder_name}")

        # all image groups must exist
        # volume-manifest-builder-#37 - allow nonexistent igs 2020.XI-03
        # if not os.path.exists(v1path):
        #     raise FileNotFoundError(f"image group {v1path} not found.")
        return v1path

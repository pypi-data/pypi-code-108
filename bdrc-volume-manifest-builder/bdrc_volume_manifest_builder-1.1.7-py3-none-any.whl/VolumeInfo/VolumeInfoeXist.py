# import os
# import ssl
from typing import List, Any
from urllib import request

from v_m_b.ImageRepository import ImageRepositoryBase
from v_m_b.VolumeInfo.VolumeInfoBase import VolumeInfoBase
from v_m_b.VolumeInfo.VolInfo import VolInfo
from v_m_b.manifestCommons import VMT_BUDABOM


class VolumeInfoeXist(VolumeInfoBase):
    """
    this uses the exist db queries get the volume list of a work, including, for each volume:
    - image list
    - image group ID

    The information should be fetched (in csv or json) from lds-pdi, query for W22084 for instance is:
    http://www.tbrc.org/public?module=work&query=work-igs&arg=WorkRid
    """

    def __init__(self, repo: ImageRepositoryBase):
        super(VolumeInfoeXist, self).__init__(repo)

    def fetch(self, work_rid: str) -> []:
        """
        :param work_rid: Resource id
        :type work_rid: object
        """

        # Interesting first pass failure: @ urllib.error.URLError: <urlopen error
        # [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:777)>
        # # Tried fix
        # debugging lines needed on timb's machine also
        import os
        import ssl
        if not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
            ssl._create_default_https_context = ssl._create_unverified_context

        _dir: str
        _work: str
        _dir, _work = self._repo.resolveWork(work_rid)
        req = f'https://legacy.tbrc.org/public?module=work&query=work-igs&args={_work}'

        vol_info: List[Any] = []
        from lxml import etree

        try:

            with request.urlopen(req) as response:
                info = response.read()
                info = info.decode('utf8').strip()

                # work-igs returns one node with space delimited list of image groups
                rTree = etree.fromstring(info)
                igText = rTree.text
                if igText:
                    igs = igText.split(" ")
                    vol_info = self.expand_groups(work_rid, igs)
        except etree.ParseError:
            pass
        return vol_info

    def expand_groups(self, work_rid: str, image_groups: []) -> list:
        """
        expands an image group into a list of its files
        :type image_groups: []
        :param work_rid: work resource Id
        :param image_groups: Image Groups to expand
        :return: VolInfo[] of all the images in all imagegroups in the input
        """
        vi = []
        for ig in image_groups:
            ig_folder_name: str = self.getImageGroup(ig)
            vol_infos = self.getImageNames(work_rid, ig_folder_name, VMT_BUDABOM)
            vi.append(VolInfo(vol_infos, ig_folder_name))

        return vi

import csv
from urllib import request

from v_m_b.ImageRepository import ImageRepositoryBase
from v_m_b.VolumeInfo.VolumeInfoBase import VolumeInfoBase
from v_m_b.VolumeInfo.VolInfo import VolInfo
from v_m_b.manifestCommons import VMT_BUDABOM


class VolumeInfoBUDA(VolumeInfoBase):
    """
    Gets the Volume list from BUDA. BUDA decided it did not want to support
    the get image list, so we have to turn to the repository provider to get the list from the VMT_BUDABOM
    """
    def __init__(self, repo: ImageRepositoryBase):
        super(VolumeInfoBUDA, self).__init__(repo)

    def fetch(self, work_rid: str) -> object:
        """
        BUDA LDS-PDI implementation
        :param: work_rid
        :return: VolInfo[]
        """

        from lxml import etree
        vol_info = []

        _dir, _work = self._repo.resolveWork(work_rid)

        req = f'http://purl.bdrc.io/query/table/volumesForInstance?R_RES=bdr:{_work}&format=xml'
        try:
            with request.urlopen(req) as response:
                rTree = etree.parse(response)
                rtRoot = rTree.getroot()

                # There's a lot of churn about namespaces and xml, including discussion of lxml vs xml,
                # but this works, using lxml
                # Thanks to: https://izziswift.com/parsing-xml-with-namespace-in-python-via-elementtree/
                for uri in rTree.findall('results/result/binding[@name="volid"]/uri',rtRoot.nsmap):
                    # the XML format returns the URI, not the bdr:Image group name, so that needs to be
                    # split out
                    uri_path:[] = uri.text.split(':')

                    # take the last thing
                    uri_path_nodes: str = uri_path[-1]

                    # find the last node on the path
                    image_group_name = uri_path_nodes.split('/')[-1]


                    # HACK
                    image_group_folder = self.getImageGroup(image_group_name)
                    image_list = self.getImageNames(work_rid, image_group_folder, VMT_BUDABOM)

                    # Dont add empty vol infos
                    if len(image_list) > 0:
                        vi = VolInfo(image_list, image_group_folder)
                        vol_info.append(vi)
                    else:
                        self.logger.warn(f"No images found in group named {image_group_name} folder {image_group_folder}")
        # Swallow all exceptions.
        except Exception as eek:
            pass
        finally:
            pass

        return vol_info

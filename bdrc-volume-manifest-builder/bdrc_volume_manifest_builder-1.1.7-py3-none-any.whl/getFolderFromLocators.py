"""
Get folder prefixes for a variety of situations
"""
import hashlib

# TODO

def get_s3_folder_prefix(workRID, imageGroupID):
    """
    gives the s3 prefix (~folder) in which the volume will be present.
    inpire from https://github.com/buda-base/buda-iiif-presentation/blob/master/src/main/java/
    io/bdrc/iiif/presentation/ImageInfoListService.java#L73
    Example:
       - workRID=W22084, imageGroupID=I0886
       - result = "Works/60/W22084/images/W22084-0886/
    where:
       - 60 is the first two characters of the md5 of the string W22084
       - 0886 is:
          * the image group ID without the initial "I" if the image group ID is in the form I\\d\\d\\d\\d
          * or else the full image group ID (incuding the "I")
    """
    md5 = hashlib.md5(str.encode(workRID))
    two = md5.hexdigest()[:2]

    pre, rest = imageGroupID[0], imageGroupID[1:]
    if pre == 'I' and rest.isdigit() and len(rest) == 4:
        suffix = rest
    else:
        suffix = imageGroupID

    return 'Works/{two}/{RID}/images/{RID}-{suffix}/'.format(two=two, RID=workRID, suffix=suffix)

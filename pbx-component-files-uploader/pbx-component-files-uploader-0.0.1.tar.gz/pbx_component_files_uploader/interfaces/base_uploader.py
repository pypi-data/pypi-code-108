
class BaseUploader:

    def __init__(self, auth: dict, options: dict = {}) -> None:
        raise NotImplementedError

    def upload(self, srcFilePath: str, dstFileName: str) -> str:
        raise NotImplementedError
    """Upload file record for custom storage
    
    if file is uploaded, then return link for record
    if got errors while uploading raise UploadError exception
        
    """

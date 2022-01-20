class BackendBase:
    def __init__(self, cfg) -> None:
        self.cfg = cfg
        
    def put(self, filename, bucket, bucket_name):
        pass
    
    def put_buffer(self, buffer, bucket, bucket_name):
        pass

    async def put_async(self, filename, bucket, bucket_name):
        pass
    
    async def put_buffer_async(self, buffer, bucket, bucket_name):
        pass
    
    def get(self, filename, bucket, bucket_name):
        pass
    
    def geturl(self, entrypoint):
        return entrypoint

    async def get_async(self, filename, bucket, bucket_name):
        pass
    
class Dz:
    dzchunkbyteoffset = None
    dzchunkindex = None
    dztotalchunkcount = None
    dztotalfilesize = None
    dzuuid = None

    def __init__(self, POST):
        for k, v in POST.dict().items():
            try:
                setattr(self, k, int(v))
            except:
                setattr(self, k, v)

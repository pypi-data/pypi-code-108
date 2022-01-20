from zerohash.zerohash_object import ZerohashObject


class APIResource(ZerohashObject):
    @classmethod
    def retrieve(cls, id, **kwargs):
        instance = cls(id, **kwargs)
        instance.refresh()
        return instance

    @classmethod
    def class_url(cls):
        if cls == APIResource:
            raise NotImplementedError(
                "APIResource is an abstract class. Perform actions on one of its subclasses"
            )

        base = cls.OBJECT_NAME.replace(".", "/")
        return "/%s" % (base,)

    def instance_url(self):
        id = self.get("id")

        base = self.class_url()
        extn = id
        return "%s/%s" % (base, extn)

    def refresh(self):
        self.refresh_from(self.request("get", self.instance_url()))
        return self

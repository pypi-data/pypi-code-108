from zerohash.resources.abstract.api_resource import APIResource


class Participants(APIResource):
    OBJECT_NAME = "participants"

    @classmethod
    def retrieve(cls, email, **kwargs):
        instance = cls(email, **kwargs)
        instance.refresh()
        return instance

    # def instance_url(self):
    #     email = self.get("email")
    #
    #     base = self.class_url()
    #     extn = email
    #     return "%s/%s" % (base, extn)

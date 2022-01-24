
class JSONReprMixin:

    def json_repr(self):
        return dict(pk=self.pk, resource_name=str(self))

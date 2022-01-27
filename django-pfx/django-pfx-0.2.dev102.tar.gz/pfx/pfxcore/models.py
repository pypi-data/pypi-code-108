
class JSONReprMixin:

    def json_repr(self):
        res = dict(
            pk=self.pk,
            resource_name=str(self))
        if hasattr(self, 'slug'):
            res['resource_slug'] = self.slug
        if hasattr(self, 'reference'):
            res['resource_reference'] = self.reference
        return res

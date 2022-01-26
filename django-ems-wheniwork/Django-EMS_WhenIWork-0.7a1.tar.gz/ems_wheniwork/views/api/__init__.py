import csv
import json

from django.http import HttpResponse
from django.views.decorators.cache import never_cache


class RESTDispatch(object):
    """ Handles passing on the request to the correct view method
        based on the request type.
    """

    @never_cache
    def run(self, *args, **named_args):
        request = args[0]

        if "GET" == request.method:
            if hasattr(self, "GET"):
                return self.GET(*args, **named_args)
            else:
                return self.invalid_method(*args, **named_args)
        elif "POST" == request.method:
            if hasattr(self, "POST"):
                return self.POST(*args, **named_args)
            else:
                return self.invalid_method(*args, **named_args)
        elif "PUT" == request.method:
            if hasattr(self, "PUT"):
                return self.PUT(*args, **named_args)
            else:
                return self.invalid_method(*args, **named_args)
        elif "DELETE" == request.method:
            if hasattr(self, "DELETE"):
                return self.DELETE(*args, **named_args)
            else:
                return self.invalid_method(*args, **named_args)
        elif "PATCH" == request.method:
            if hasattr(self, "PATCH"):
                return self.PATCH(*args, **named_args)
            else:
                return self.invalid_method(*args, **named_args)
        else:
            return self.invalid_method(*args, **named_args)

    def invalid_method(self, *args, **named_args):
        return HttpResponse("Method not allowed", status=405)

    def data_exception_response(self, exception):
        message = "Error: %s" % exception.msg.capitalize()
        return HttpResponse(json.dumps({"error": message}),
                            status=exception.status,
                            content_type="application/json")

    def error_response(self, status, message="", content={}):
        content["error"] = message
        return HttpResponse(json.dumps(content),
                            status=status,
                            content_type="application/json")

    def _json_dump_default(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()

        raise TypeError(
            "Unserializable object {} of type {}".format(obj, type(obj))
        )

    def json_response(self, content="", status=200):
        return HttpResponse(
            json.dumps(content, default=self._json_dump_default, indent=4),
            status=status,
            content_type="application/json"
        )

    def tsv_response(self, content="", fields=[], status=200):
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/tab-separated-values')

        if not len(fields):
            fields = content[0].keys()

        writer = csv.DictWriter(
            response,
            fieldnames=fields, extrasaction='ignore', dialect='excel-tab'
        )

        writer.writerows(content)

        return response

    def xml_response(self, content="", status=200):
        return HttpResponse(content,
                            status=status,
                            content_type="application/xml")

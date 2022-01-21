from pymasmovil.errors.exceptions import UnknownMMError


class MMError(Exception):
    def __init__(self):
        self.status_code = ""
        self.message = ""
        self.fields = ""

    def build(self, response):
        """
        MM API should return always an HTTPError with this structure:
        {
            "success": false,
            "errors": [
                {
                    "fields": "",
                    "statusCode": "",
                    "message": ""
                }
            ]
        }
        But in at least one endpoint the API returns this dictionary inside a list.
        When the session is invalid the MM API returns also another different list.

        This method builds a MMError from these different structures.
        """

        bad_response = response.json()

        try:
            if isinstance(bad_response, list):
                if "errorCode" in bad_response[0]:
                    self.status_code = response.status_code
                    self.message = "{}: {}".format(
                        bad_response[0]["errorCode"], bad_response[0]["message"]
                    )
                else:
                    self._set_attributes_with_error_dct(bad_response[0]["errors"][0])
            else:
                self._set_attributes_with_error_dct(bad_response["errors"][0])
        except (TypeError, KeyError):
            raise UnknownMMError(bad_response)

    def _set_attributes_with_error_dct(self, error_dct):
        self.status_code = error_dct["statusCode"]
        self.message = error_dct["message"]
        self.fields = error_dct["fields"]

class SimpleErrorRenderer:
    """
    This class models the flattening of simple errors.
    I converts an error that follows the SimpleError protocol to a shallow object
    made up of basic, plain, shallow types/objects.
    """
    def render(self, error):
        result_dict = {
                "code": error.code(),
                "text": error.text()
            }
        return result_dict

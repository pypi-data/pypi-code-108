class ForceFail(Exception):
    pass


class MissingPrimaryKey(Exception):
    pass


class SliceError(IndexError):
    pass


def rollback_on_exception(method):
    def inner_method(self, *args, **kwargs):
        try:
            method(self, *args, **kwargs)
        except Exception as e:
            self.rollback()
            raise e
    return inner_method
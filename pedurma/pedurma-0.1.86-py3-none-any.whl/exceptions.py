class PageNumMissing(BaseException):
    def __init__(self):
        self.message = "page number not found in note pages. Please correct the page num of preview page in note pages.."


class TextMappingNotFound(BaseException):
    def __init__(self):
        self.message = "Text mapping to its opf is not found. Please text pecha mapping.json in editable text repo"

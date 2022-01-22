from xmldt import XmlDt


class HtmlDt (XmlDt):
    def __init__(self, **kwargs):
        super().__init__(**{**kwargs, "html": True})  # couldn't rewrite better

    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **{**kwargs, "html": True})




import Famcy
import json

class style(Famcy.FamcyElement):
    def __init__(self):
        super(style, self).__init__()

    def render_element(self):
        html = ""

        if self.innerHTML and self.innerHTML != "":
            html += self.innerHTML
        self.html = html
        return "<style" + self.setAttrTag() + ">" + html + "</style>"
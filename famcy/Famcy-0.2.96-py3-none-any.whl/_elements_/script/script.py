import Famcy
import json

class script(Famcy.FamcyElement):
    def __init__(self):
        super(script, self).__init__()

    def render_element(self):
        html = ""

        if self.innerHTML and self.innerHTML != "":
            html += self.innerHTML
        self.html = html
        return "<script" + self.setAttrTag() + ">" + html + "</script>"
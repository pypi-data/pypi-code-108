import markdown
import Famcy
import json

class displayTag(Famcy.FamcyBlock):
    """
    Represents the block to display
    paragraph. 
    """
    def __init__(self):
        self.value = displayTag.generate_template_content()
        super(displayTag, self).__init__()
        self.init_block()

    @classmethod
    def generate_template_content(cls):
        return {
            "title": "displayTag",
            "content": "displayTag content",
        }

    def init_block(self):
        self.body = Famcy.div()
        self.body["id"] = self.id
        self.body["className"] = "displayTag"

        h3_temp = Famcy.h3()
        h4_temp = Famcy.h4()

        self.body.addElement(h3_temp)
        self.body.addElement(h4_temp)

    def render_inner(self):
        self.body.children[0].innerHTML = self.value["title"]
        self.body.children[1].innerHTML = self.value["content"]

        return self.body
import markdown
import Famcy
import json

class displayPicWord(Famcy.FamcyBlock):
    """
    Represents the block to display
    paragraph. 
    """
    def __init__(self):
        self.value = displayPicWord.generate_template_content()
        super(displayPicWord, self).__init__()
        self.init_block()

    @classmethod
    def generate_template_content(cls):
        return {
                "title": "displayPicWord",
                "content": "",
                "img_src": "static/image/transparent.png"
        }

    def init_block(self):
        self.body = Famcy.div()
        self.body["id"] = self.id
        self.body["className"] = "displayPicWord"

        img_holder = Famcy.div()
        img_temp = Famcy.img()
        h3_temp = Famcy.h3()
        h4_temp = Famcy.h4()

        img_holder.addElement(img_temp)

        self.body.addElement(img_holder)
        self.body.addElement(h3_temp)
        self.body.addElement(h4_temp)

    def render_inner(self):
        self.body.children[0].children[0]["src"] = self.value["img_src"]
        self.body.children[1].innerHTML = self.value["title"]
        self.body.children[2].innerHTML = markdown.markdown(self.value["content"])

        return self.body
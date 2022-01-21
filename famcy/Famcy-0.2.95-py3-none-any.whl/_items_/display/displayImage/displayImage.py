import markdown
import Famcy
import json

class displayImage(Famcy.FamcyBlock):
    """
    Represents the block to display
    paragraph. 
    """
    def __init__(self):
        self.value = displayImage.generate_template_content()
        super(displayImage, self).__init__()
        self.init_block()

    @classmethod
    def generate_template_content(cls):
        return {
                "title": "displayImage",
                "img_name": ["/static/image/test.jpg"],
                "img_size": ["100%"],
                "border_radius": None
            }

    def init_block(self):
        self.body = Famcy.div()
        self.body["id"] = self.id
        self.body["className"] = "displayImage"

        h3_temp = Famcy.h3()
        div_temp = Famcy.div()

        self.body.addElement(h3_temp)
        self.body.addElement(div_temp)

    def render_inner(self):
        self.body.children[0].innerHTML = self.value["title"]

        i = 0
        self.body.children[1].children = []
        for img_name, img_size in zip(self.value["img_name"], self.value["img_size"]):
            i_temp = Famcy.img()
            i_temp.style["width"] = img_size
            i_temp["src"] = img_name
            if self.value["border_radius"]:
                i_temp.style["border-radius"] = self.value["border_radius"][i]
            else:
                if "border-radius" in i_temp.style.keys():
                    del i_temp.style["border-radius"]
            self.body.children[1].addElement(i_temp)
            i+=1

        return self.body

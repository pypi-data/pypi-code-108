import markdown
import Famcy
import json

class inputBlockSec(Famcy.FamcyInputBlock):
    """
    Represents the block to display
    paragraph. 
    """
    def __init__(self):
        self.value = inputBlockSec.generate_template_content()
        super(inputBlockSec, self).__init__()
        self.init_block()

    @classmethod
    def generate_template_content(cls):
        return {
                "title": "inputBlockSec",
                "content": "",
                "img_src": "",
                "btn_name": ""
        }

    def init_block(self):
        self.body = Famcy.div()
        self.body["id"] = self.id
        self.body["className"] = "inputBlockSec"

        div_temp = Famcy.div()
        h3_temp = Famcy.h3()
        h4_temp = Famcy.h4()
        btn_temp = Famcy.button()

        div_temp.addElement(h3_temp)
        div_temp.addElement(h4_temp)
        div_temp.addElement(btn_temp)
        
        self.body.addElement(div_temp)

    def render_inner(self):

        if self.value["btn_name"] != "":
            self.body.children[0].children[2].innerHTML = self.value["btn_name"]
        else:
            del self.body.children[0].children[2]

        if self.value["content"] != "":
            self.body.children[0].children[1].innerHTML = markdown.markdown(self.value["content"])
        else:
            del self.body.children[0].children[1]

        if self.value["title"] != "":
            self.body.children[0].children[0].innerHTML = self.value["title"]
        else:
            del self.body.children[0].children[0]

        self.body.style["background-image"] =  "url('" + self.value["img_src"] + "')"

        return self.body

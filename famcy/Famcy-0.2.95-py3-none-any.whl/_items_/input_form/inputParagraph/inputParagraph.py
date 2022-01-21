import markdown
import Famcy
import json

class inputParagraph(Famcy.FamcyInputBlock):
    """
    Represents the block to display
    paragraph. 
    """
    def __init__(self):
        self.value = inputParagraph.generate_template_content()
        super(inputParagraph, self).__init__()
        self.init_block()

    @classmethod
    def generate_template_content(cls):
        return {
            "title": "inputParagraph",
            "desc": "",
            "height": "20vh",                               # eg: ("200px")
            "placeholder": "",
            "mandatory": False,
            "action_after_post": "clean",                   # (clean / save)
        }

    def init_block(self):
        self.body = Famcy.div()
        self.body["id"] = self.id
        self.body["className"] = "inputParagraph"

        l_temp = Famcy.label()
        l_temp["for"] = self.id + "_input"

        p_temp = Famcy.p()

        input_temp = Famcy.textarea()
        input_temp["id"] = self.id + "_input"
        input_temp["name"] = self.name

        script = Famcy.script()

        self.body.addElement(l_temp)
        self.body.addElement(p_temp)
        self.body.addElement(input_temp)
        self.body.addElement(script)

    def render_inner(self):
        self.body.children[0].innerHTML = self.value["title"]
        self.body.children[1].innerHTML = self.value["desc"]

        if 'height: ' + self.value["height"] not in self.body.children[2].style:
            self.body.children[2].style['height'] = self.value["height"]
        self.body.children[2]["placeholder"] = self.value["placeholder"]

        if self.value["mandatory"]:
            self.body.children[2]["required"] = "required"
        else:
            del self.body.children[2]["required"]

        if "save" in self.value["action_after_post"]:
            self.body.children[2]["onkeyup"] = 'saveValue(\'' + self.id + '\', this.value);'
            self.body.children[3].innerHTML = 'document.getElementById("' + self.id + '_input").value = getSavedValue("' + self.id + '");'
        else:
            del self.body.children[2]["onkeyup"]
            self.body.children[3].innerHTML = ''

        return self.body

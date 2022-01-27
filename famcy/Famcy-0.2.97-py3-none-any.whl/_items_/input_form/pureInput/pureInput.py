import markdown
import Famcy
import json

class pureInput(Famcy.FamcyInputBlock):
    """
    Represents the block to display
    paragraph. 
    """
    def __init__(self):
        self.value = pureInput.generate_template_content()
        super(pureInput, self).__init__()
        self.init_block()

    @classmethod
    def generate_template_content(cls):
        return {
            "title": "pureInput",
            "desc": "",
            "defaultValue": None,
            "input_type": "text",                               # text / number / password
            "num_range": None,                                  # if type == number
            "placeholder": "",
            "mandatory": False,
            "action_after_post": "clean",                       # (clean / save)
        }

    def init_block(self):
        self.body = Famcy.div()
        self.body["id"] = self.id
        self.body["className"] = "pureInput"

        l_temp = Famcy.label()
        l_temp["for"] = self.id + "_input"

        p_temp = Famcy.p()

        input_temp = Famcy.input()
        input_temp["id"] = self.id + "_input"
        input_temp["name"] = self.name

        script = Famcy.script()

        self.body.addElement(l_temp)
        self.body.addElement(p_temp)
        self.body.addElement(input_temp)
        self.body.addStaticScript(script)

    def render_inner(self):
        if self.value["input_type"] == "number" and self.value["num_range"]:
            self.body.children[2]["min"] = str(self.value["num_range"][0])
            self.body.children[2]["max"] = str(self.value["num_range"][1])

        self.body.children[0].innerHTML = self.value["title"]
        self.body.children[1].innerHTML = self.value["desc"]

        self.body.children[2]["type"] = self.value["input_type"]
        self.body.children[2]["placeholder"] = self.value["placeholder"]

        if self.value["defaultValue"]:
            self.body.children[2]["value"] = self.value["defaultValue"]
        else:
            del self.body.children[2]["value"]

        if self.value["mandatory"]:
            self.body.children[2]["required"] = "required"
        else:
            del self.body.children[2]["required"]

        if "save" in self.value["action_after_post"]:
            self.body.children[2]["onkeyup"] = 'saveValue(\'' + self.id + '\', this.value);'
            self.body.script[0].innerHTML = 'document.getElementById("' + self.id + '_input").value = getSavedValue("' + self.id + '");'
        else:
            del self.body.children[2]["onkeyup"]
            self.body.script[0].innerHTML = ''


        return self.body

import markdown
import Famcy
import json

class inputBtn(Famcy.FamcyInputBlock):
    """
    Represents the block to display
    paragraph. 
    """
    def __init__(self):
        self.value = inputBtn.generate_template_content()
        super(inputBtn, self).__init__()
        self.init_block()

    @classmethod
    def generate_template_content(cls):
        return {
            "title": "inputBtn",
            "desc": "",
            "input_type": "text",                           # ("number" / "text" / "password")
            "num_range": None,                              # if type == number ([0, 10] / None)
            "placeholder": "",
            "mandatory": False,
            "button_name": "送出",                          # btn name in same section must not be same
            "action_after_post": "clean",                   # (clean / save)
        }

    def init_block(self):
        self.body = Famcy.div()
        self.body["id"] = self.id
        self.body["className"] = "inputBtn"

        l_temp = Famcy.label()
        l_temp["for"] = self.id + "_input"

        p_temp = Famcy.p()

        input_temp = Famcy.input()
        input_temp["id"] = self.id + "_input"
        input_temp["name"] = self.name

        submit_temp = Famcy.input()
        submit_temp["name"] = "send"
        submit_temp["type"] = "submit"

        script = Famcy.script()

        self.body.addElement(l_temp)
        self.body.addElement(p_temp)
        self.body.addElement(input_temp)
        self.body.addElement(submit_temp)
        self.body.addElement(script)


    def render_inner(self):
        if self.value["input_type"] == "number" and self.value["num_range"]:
            self.body.children[2]["min"] = str(self.value["num_range"][0])
            self.body.children[2]["max"] = str(self.value["num_range"][1])

        self.body.children[0].innerHTML = self.value["title"]
        self.body.children[1].innerHTML = self.value["desc"]

        self.body.children[2]["type"] = self.value["input_type"]
        self.body.children[2]["placeholder"] = self.value["placeholder"]

        self.body.children[3]["value"] = self.value["button_name"]

        if self.value["mandatory"]:
            self.body.children[2]["required"] = "required"
        else:
            del self.body.children[2]["required"]

        if "save" in self.value["action_after_post"]:
            self.body.children[2]["onkeyup"] = 'saveValue(\'' + self.id + '\', this.value);'
            self.body.children[4].innerHTML = 'document.getElementById("' + self.id + '_input").value = getSavedValue("' + self.id + '");'
        else:
            del self.body.children[2]["onkeyup"]
            self.body.children[4].innerHTML = ''

        return self.body
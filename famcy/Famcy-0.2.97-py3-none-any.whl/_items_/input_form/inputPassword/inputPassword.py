import markdown
import Famcy
import json

class inputPassword(Famcy.FamcyInputBlock):
    """
    Represents the block to display
    paragraph. 
    """
    def __init__(self):
        self.value = inputPassword.generate_template_content()
        super(inputPassword, self).__init__()
        self.init_block()

    @classmethod
    def generate_template_content(cls):
        return {
                "title": "inputPassword",
                "desc": "",
                "mandatory": False,
                "action_after_post": "clean",                    # (clean / save)
            }

    def init_block(self):
        self.body = Famcy.div()
        self.body["id"] = self.id
        self.body["className"] = "inputPassword"

        label_temp = Famcy.label()
        label_temp["for"] = self.id + "_input"
        p_temp = Famcy.p()
        div_temp = Famcy.div()
        div_temp["id"] = self.id + "_input"

        script = Famcy.script()
        script.innerHTML = '$(document).ready(function($) { $("#' + self.id + "_input" + '").strength_meter({strengthMeterClass: "t_strength_meter", name: "' + self.name + '"})});'

        self.body.addElement(label_temp)
        self.body.addElement(p_temp)
        self.body.addElement(div_temp)
        self.body.addElement(script)

    def render_inner(self):
        self.body.children[0].innerHTML = self.value["title"]
        self.body.children[1].innerHTML = self.value["desc"]

        if self.value["mandatory"]:
            self.body.children[2]["className"] = "required_password"
        else:
            if "required_password" in self.body.children[2].classList:
                self.body.children[2].classList.remove("required_password")

        return self.body
import Famcy
import json

class inputList(Famcy.FamcyInputBlock):
    """
    Represents the block to display
    paragraph. 
    """
    def __init__(self):
        self.value = inputList.generate_template_content()
        super(inputList, self).__init__()
        self.init_block()

    @classmethod
    def generate_template_content(cls):
        return {
            "title": "inputList",
            "desc": "",
            "mandatory": False,
            "value": [],
            "action_after_post": "clean",                    # (clean / save)
        }

    def init_block(self):
        self.body = Famcy.div()
        self.body["id"] = self.id
        self.body["className"] = "inputList"

        h3_temp = Famcy.h3()
        p_temp = Famcy.p()
        div_temp = Famcy.div()
        div_temp["id"] = self.id + '_inputList'
        div_temp["className"] = "inputList_holder"
        sel_temp = Famcy.select()

        div_temp.addElement(sel_temp)

        script = Famcy.script()
        script.innerHTML = 'generate_list("' + self.id + '")'

        self.body.addElement(h3_temp)
        self.body.addElement(p_temp)
        self.body.addElement(div_temp)
        self.body.addElement(script)

    def render_inner(self):
        self.body.children[2].children[0].children = []
        if "---" not in self.value["value"]:
            self.value["value"].insert(0, "---")
        for list_value in self.value["value"]:
            opt_temp = Famcy.option()
            opt_temp["name"] = self.name
            opt_temp["value"] = list_value
            opt_temp.innerHTML = list_value
            self.body.children[2].children[0].addElement(opt_temp)

        if self.value["mandatory"]:
            self.body["className"] = "required_list"
        else:
            if "required_list" in self.body.classList:
                self.body.classList.remove("required_list")

        self.body.children[0].innerHTML = self.value["title"]
        self.body.children[1].innerHTML = self.value["desc"]
        self.body.children[2].children[0]["after_action"] = self.value["action_after_post"]

        return self.body

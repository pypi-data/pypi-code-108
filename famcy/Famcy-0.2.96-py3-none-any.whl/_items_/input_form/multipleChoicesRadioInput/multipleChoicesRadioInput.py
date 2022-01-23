import markdown
import Famcy
import json

class multipleChoicesRadioInput(Famcy.FamcyInputBlock):
    """
    Represents the block to display
    paragraph. 
    """
    def __init__(self):
        self.value = multipleChoicesRadioInput.generate_template_content()
        super(multipleChoicesRadioInput, self).__init__()
        self.init_block()

    @classmethod
    def generate_template_content(cls):
        return {
                "title": "multipleChoicesRadioInput",
                "desc": "",
                "mandatory": False,
                "value": [],
                "action_after_post": "clean",                    # (clean / save)
            }

    def init_block(self):
        self.body = Famcy.div()
        self.body["id"] = self.id
        self.body["className"] = "multipleChoicesRadioInput"

        h3_temp = Famcy.h3()
        p_temp = Famcy.p()
        div_temp = Famcy.div()
        script = Famcy.script()

        self.body.addElement(h3_temp)
        self.body.addElement(p_temp)
        self.body.addElement(div_temp)
        self.body.addElement(script)


    def render_inner(self):
        self.body.children[2].children = []
        for list_value in self.value["value"]:
            label_temp = Famcy.label()
            label_temp["className"] = "rad-label"

            input_temp = Famcy.input()
            input_temp["id"] = self.id + list_value
            input_temp["type"] = "checkbox"
            input_temp["className"] = "rad-input"
            input_temp["name"] = self.name
            input_temp["value"] = list_value
            div1_temp = Famcy.div()
            div1_temp["className"] = "rad-design"
            div2_temp = Famcy.div()
            div2_temp["className"] = "rad-text"
            div2_temp.innerHTML = list_value

            if "save" in self.value["action_after_post"]:
                input_temp["onclick"] = 'saveMultValue(\'' + self.id + '\', \'' + self.id + '\' + this.value);'
                self.body.children[3].innerHTML = 'for(var i = 0; i < getMultSavedValue("' + self.id + '").length; i++){document.getElementById(getMultSavedValue("' + self.id + '")[i]).checked = true;}'
            else:
                del input_temp["onclick"]
                self.body.children[3].innerHTML = ''

            label_temp.addElement(input_temp)
            label_temp.addElement(div1_temp)
            label_temp.addElement(div2_temp)

            self.body.children[2].addElement(label_temp)

        self.body.children[0].innerHTML = self.value["title"]
        self.body.children[1].innerHTML = self.value["desc"]

        if self.value["mandatory"]:
            self.body["className"] = "required_list"
        else:
            if "required_list" in self.body.classList:
                self.body.classList.remove("required_list")

        return self.body

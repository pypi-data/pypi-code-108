import markdown
import Famcy
import json

class displayStepLoader(Famcy.FamcyBlock):
    """
    Represents the block to display
    paragraph. 
    """
    def __init__(self):
        self.value = displayStepLoader.generate_template_content()
        super(displayStepLoader, self).__init__()
        self.init_block()

    @classmethod
    def generate_template_content(cls):
        return {
                "title": "displayStepLoader",
                "steps": ["step1", "step2", "step3"],
                "steps_status": ["complete", "active", ""]                 # ("" / "complete" / "active")
            }

    def init_block(self):
        self.body = Famcy.div()
        self.body["id"] = self.id
        self.body["className"] = "displayStepLoader"

        h3_temp = Famcy.h3()
        ol_temp = Famcy.ol()
        ol_temp["className"] = "_progress-bar"

        self.body.addElement(h3_temp)
        self.body.addElement(ol_temp)

    def render_inner(self):
        self.body.children[0].innerHTML = self.value["title"]

        self.body.children[1].children = []
        for step_title, step_status in zip(self.value["steps"], self.value["steps_status"]):
            li_temp = Famcy.li()
            li_temp["className"] = "is-" + step_status

            span_temp = Famcy.span()
            span_temp.innerHTML = step_title

            li_temp.addElement(span_temp)
            self.body.children[1].addElement(li_temp)

        return self.body

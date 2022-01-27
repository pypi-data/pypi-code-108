import markdown
import Famcy
import json

class displayLight(Famcy.FamcyBlock):
    """
    Represents the block to display
    paragraph. 
    """
    def __init__(self):
        self.value = displayLight.generate_template_content()
        super(displayLight, self).__init__()
        self.init_block()

    def init_block(self):
        self.body = Famcy.div()
        self.body["id"] = self.id
        self.body["className"] = "displayLight"

        holder_temp = Famcy.div()
        holder_temp["className"] = "bulb_holder"

        bulb_red_temp = Famcy.div()
        bulb_red_temp["className"] = 'bulb'

        bulb_yellow_temp = Famcy.div()
        bulb_yellow_temp["className"] = 'bulb'

        bulb_green_temp = Famcy.div()
        bulb_green_temp["className"] = 'bulb'

        holder_temp.addElement(bulb_red_temp)
        holder_temp.addElement(bulb_yellow_temp)
        holder_temp.addElement(bulb_green_temp)

        self.body.addElement(holder_temp)

    @classmethod
    def generate_template_content(cls):
        return {
            "title": "displayLight",
            "status": {"red": "bulb_red", "yellow": "", "green": ""}, 
            "light_size": "100%",
        }

    def render_inner(self):
        self.body.children[0].style['width'] = self.value["light_size"]

        for item in self.body.children[0].children:
            item.classList = ["bulb"]

        self.body.children[0].children[0]["className"] = self.value["status"]["red"]
        self.body.children[0].children[1]["className"] = self.value["status"]["yellow"]
        self.body.children[0].children[2]["className"] = self.value["status"]["green"]

        return self.body

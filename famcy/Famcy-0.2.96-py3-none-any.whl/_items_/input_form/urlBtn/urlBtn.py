import markdown
import Famcy
import json

class urlBtn(Famcy.FamcyInputBlock):
    """
    Represents the block to display
    paragraph. 
    """
    def __init__(self):
        self.value = urlBtn.generate_template_content()
        super(urlBtn, self).__init__()
        self.init_block()

    @classmethod
    def generate_template_content(cls):
        return {
            "title": "urlBtn",
            "style": "btn_style",                               # (link_style, btn_style)
            "url": "",
            "desc": "",
            "mandatory": False,                                 # this is useless
            "button_name": "送出",                              # btn name in same section must not be same
            "action_after_post": "clean",                       # (clean / save)
        }

    def init_block(self):
        self.body = Famcy.div()
        self.body["id"] = self.id
        self.body["className"] = "urlBtn"

        p_temp = Famcy.p()
        p_temp["className"] = self.value["style"] + '_p'

        btn_temp = Famcy.button()
        btn_temp["type"] = "button"

        self.body.addElement(p_temp)
        self.body.addElement(btn_temp)

    def render_inner(self):
        self.body.children[0].innerHTML = self.value["desc"]

        self.body.children[1]["className"] = self.value["style"]
        self.body.children[1]["onclick"] = 'window.location.href=\'' + self.value["url"] + '\''
        self.body.children[1].innerHTML = self.value["button_name"]

        return self.body



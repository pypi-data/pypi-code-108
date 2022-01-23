import markdown
import Famcy
import json

class uploadFile(Famcy.FamcyUploadBlock):
    """
    Represents the block to display
    paragraph. 
    """
    def __init__(self):
        self.value = uploadFile.generate_template_content()
        super(uploadFile, self).__init__()
        self.init_block()

    @classmethod
    def generate_template_content(cls, fblock_type=None):
        return {
            "title": "uploadFile",
            "file_num": "multiple",                     # ("single", "multiple")
            "accept_type": ["png", "jpg"],
            "file_path": './',
            "mandatory": True,
            "action_after_post": "clean",                    # (clean)
        }

    def init_block(self):
        self.body = Famcy.div()
        self.body["id"] = self.id
        self.body["className"] = "uploadFile"

        input_temp = Famcy.input()
        input_temp["id"] = self.id + "_input"
        input_temp["name"] = "file"
        input_temp["type"] = "file"

        self.body.addElement(input_temp)

    def render_inner(self):
        if self.value["file_num"] == "multiple":
            self.body.children[0]["multiple"] = "multiple"
        else:
            del self.body.children[0]["multiple"]

        return self.body

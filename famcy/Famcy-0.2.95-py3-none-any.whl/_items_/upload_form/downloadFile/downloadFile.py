import markdown
import Famcy
import json

class downloadFile(Famcy.FamcyUploadBlock):
    """
    Represents the block to display
    paragraph. 
    """
    def __init__(self):
        self.value = downloadFile.generate_template_content()
        super(downloadFile, self).__init__()
        self.init_block()

    @classmethod
    def generate_template_content(cls, fblock_type=None):
        return {
            "title": "downloadFile",
            "file_path": 'C:/Users/user/Downloads',
            "file_name": 'download.txt',
            "mandatory": True,
            "action_after_post": "clean",                    # (clean)
        }

    def init_block(self):
        self.body = Famcy.div()
        self.body["id"] = self.id
        self.body["className"] = "downloadFile"

        input_temp = Famcy.a()
        input_temp["id"] = self.id + "_input"
        input_temp["download"] = ""
        input_temp["href"] = ""
        input_temp["target"] ="_blank"

        self.body.addElement(input_temp)

    def render_inner(self):
        if self.value["file_path"]:
            self.body.children[0]["href"] = self.value["file_path"]
        if self.value["file_name"]:
            self.body.children[0]["download"] = self.value["file_name"]
        self.body.children[0].innerHTML = self.value["title"]

        return self.body

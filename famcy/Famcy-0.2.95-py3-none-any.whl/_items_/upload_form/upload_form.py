import Famcy
from flask import flash
from flask import current_app
import json

class upload_form(Famcy.FamcyCard):
    """
    Represents the block to upload 
    all kinds of files. 
    """
    def __init__(self, layout_mode=Famcy.FamcyLayoutMode.recommend):
        super(upload_form, self).__init__(layout_mode=layout_mode)
        self.configs["method"] = "post"
        self.init_block()

    def init_block(self):
        self.body = Famcy.form()
        self.body["id"] = self.id
        self.body["method"] = self.configs["method"]
        self.body["action"] = self.action
        self.body["enctype"] = "multipart/form-data"
        self.body["target"] = "sjxUpload_iframe_"+self.id

        self.iframe_tag = Famcy.iframe()
        self.submit_input_tag = Famcy.input()
        self.rq_input_tag = Famcy.input()
        self.args_input_tag = Famcy.input()
        self.csrf_input_tag = Famcy.input()
        self.crsf_script = Famcy.script()

    def render_inner(self):

        header_script, self.body = self.layout.render()
        if header_script not in self.header_script:
            self.header_script += header_script

        for widget, _, _, _, _ in self.layout.content:
            if widget.clickable:

                if self.iframe_tag not in self.body.children:

                    self.iframe_tag["id"] = "sjxUpload_iframe_"+self.id
                    self.iframe_tag["name"] = "sjxUpload_iframe_"+self.id
                    self.iframe_tag["style"] = "display: none;"

                    self.submit_input_tag["type"] = "hidden"
                    self.submit_input_tag["name"] = "fsubmission_obj"
                    self.submit_input_tag["value"] = str(widget.submission_obj_key)

                    self.rq_input_tag["type"] = "hidden"
                    self.rq_input_tag["name"] = "sijax_rq"
                    self.rq_input_tag["value"] = self.id+"_upload"

                    self.args_input_tag["id"] = "args_upload_"+self.id
                    self.args_input_tag["type"] = "hidden"
                    self.args_input_tag["name"] = "sijax_args"

                    self.csrf_input_tag["id"] = "crsf_upload_"+self.id
                    self.csrf_input_tag["type"] = "hidden"
                    self.csrf_input_tag["name"] = "csrf_token"

                    self.crsf_script.innerHTML = "document.getElementById('args_upload_"+self.id+"').value = JSON.stringify("+json.dumps([self.id])+");document.getElementById('crsf_upload_"+self.id+"').value = document.head.querySelector('[name~=csrf-token][content]').content;"
                    
                    self.body.addElement(self.iframe_tag)
                    self.body.addElement(self.submit_input_tag)
                    self.body.addElement(self.rq_input_tag)
                    self.body.addElement(self.args_input_tag)
                    self.body.addElement(self.csrf_input_tag)
                    self.body.addElement(self.crsf_script)

        return self.body
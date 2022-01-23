import json
import Famcy
from flask import current_app
import urllib
import time

class video_stream(Famcy.FamcyBlock):
    """
    Represents the block to display
    video_stream. 
    """
    def __init__(self, **kwargs):
        self.value = video_stream.generate_template_content()
        super(video_stream, self).__init__(**kwargs)
        self.init_block()

    @classmethod
    def generate_template_content(cls, fblock_type=None):
        """
        This is the function that
        returns the template content 
        for the given fblock. 
        - Return a content dictionary
        """
        return {
            "refreash_stream": "刷新",
            "stop_stream": "停止",
            "title": "videoStream",
            "desc": "",
            "rtsp_address": [],
            "video_timeout": [],
            "holder_width": [],
            "holder_height": [],
            "img_path": []
        }

    def init_block(self):
        self.body = Famcy.div()
        self.body["id"] = self.id
        self.body["className"] = "videoStream"

        h3_temp = Famcy.h3()
        p_temp = Famcy.p()
        div_temp = Famcy.div()

        self.body.addElement(h3_temp)
        self.body.addElement(p_temp)
        self.body.addElement(div_temp)

    def render_inner(self):

        index = 0
        self.body.children[2].children = []
        for w, h, address, timeout, path in zip(self.value["holder_width"], self.value["holder_height"], self.value["rtsp_address"], self.value["video_timeout"], self.value["img_path"]):
            
            script_temp = Famcy.script()
            script_temp.innerHTML = """
                $('#mbr' + '%s_' + '%s').bind('click', (e) => {
                    e.target.parentElement.children[0].classList.remove("video_placeholder");
                    e.target.parentElement.children[0].setAttribute("src", "")
                    e.target.parentElement.children[0].setAttribute("src", "%s&datetime=" + new Date().getTime())
                });
                $('#mbd' + '%s_' + '%s').bind('click', (e) => {
                    e.target.parentElement.children[0].classList.add("video_placeholder");
                    e.target.parentElement.children[0].setAttribute("src", "/static/image/transparent.png")
                });
            """ % (index, self.id, path + '?' + urllib.parse.urlencode({"address": address, "timeout": timeout}), index, self.id)

            div_temp = Famcy.div()
            div_temp["className"] = "video_holder"
            div_temp.style['width'] = w

            img_temp = Famcy.img()
            img_temp["src"] = path + '?' + urllib.parse.urlencode({"address": address, "timeout": timeout, "datetime": time.time()})
            img_temp.style['height'] = h

            btn1_temp = Famcy.button()
            btn1_temp["id"] = 'mbr' + str(index) + "_" + self.id
            btn1_temp["className"] = "video_submit_btn"
            btn1_temp.innerHTML = self.value["refreash_stream"]

            btn2_temp = Famcy.button()
            btn2_temp["id"] = 'mbd' + str(index) + "_" + self.id
            btn2_temp["className"] = "video_submit_btn"
            btn2_temp.innerHTML = self.value["stop_stream"]

            div_temp.addElement(img_temp)
            div_temp.addElement(btn1_temp)
            div_temp.addElement(btn2_temp)
            div_temp.addElement(script_temp)

            index += 1

        self.body.children[0].innerHTML = self.value["title"]
        self.body.children[1].innerHTML = self.value["desc"]
        self.body.children[2].addElement(div_temp)

        return self.body
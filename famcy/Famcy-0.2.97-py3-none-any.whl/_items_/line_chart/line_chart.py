import json
import Famcy
from flask import current_app

class line_chart(Famcy.FamcyBlock):
    """
    Represents the block to display
    line_chart. 
    """
    def __init__(self):
        self.value = line_chart.generate_template_content()
        super(line_chart, self).__init__()
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
                "title": "line_chart",
                "labels": ["line1", "line2", "line3"],
                "values": [{
                    "x": [1, 2, 3, 4],
                    "y": [12, 9, 15, 12],
                    "mode": "lines+markers",
                    "color": "rgb(128, 0, 128)",
                    "marker_size": 8,
                    "line_width": 1
                },
                {
                    "x": [1, 2, 3, 4],
                    "y": [2, 9, 1, 3],
                    "mode": "lines",
                    "color": "rgb(2, 0, 128)",
                    "marker_size": 8,
                    "line_width": 3
                },
                {
                    "x": [1, 2, 3, 4],
                    "y": [4, 3, 7, 13],
                    "mode": "markers",
                    "color": "rgb(128, 0, 2)",
                    "marker_size": 12,
                    "line_width": 1
                }]
            }

    def init_block(self):

        self.body = Famcy.div()
        self.body["id"] = self.id

        div_temp = Famcy.div()
        script = Famcy.script()

        self.body.addElement(div_temp)
        self.body.addElement(script)

        static_script = Famcy.script()
        static_script["src"] = "/static/js/line_chart.js"
        self.body.addStaticScript(static_script)

    def render_inner(self):
        data = []
        for dict, label in zip(self.value["values"], self.value["labels"]):
            
            temp = {}
            temp["x"] = dict["x"]
            temp["y"] = dict["y"]
            temp["mode"] = dict["mode"]
            temp["name"] = label

            if dict["mode"] == "lines+markers":
                temp["line"] = {
                    "color": dict["color"],
                    "width": dict["line_width"]
                }
                temp["marker"] = {
                    "color": dict["color"],
                    "size": dict["marker_size"]
                }

            elif dict["mode"] == "lines":
                temp["line"] = {
                    "color": dict["color"],
                    "width": dict["line_width"]
                }

            elif dict["mode"] == "markers":
                temp["marker"] = {
                    "color": dict["color"],
                    "size": dict["marker_size"]
                }

            data.append(temp)

        json_line_dict_values = json.dumps(data)
        json_line_dict_title = json.dumps(self.value["title"])

        self.body.children[1].innerHTML = 'generateLineChart("%s", %s, %s)' % (self.id, json_line_dict_values, json_line_dict_title)
        
        return self.body

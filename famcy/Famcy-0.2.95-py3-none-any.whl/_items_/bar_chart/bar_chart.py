import json
import Famcy
from flask import current_app

import pandas as pd
import plotly.graph_objects as go

class bar_chart(Famcy.FamcyBlock):
    """
    Represents the block to display
    bar_chart. 
    """
    def __init__(self, **kwargs):
        self.value = bar_chart.generate_template_content()
        super(bar_chart, self).__init__(**kwargs)
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
            "values": [{
                "x": [1995, 1996, 1997, 1998, 1999, 2000],
                "y": [219, 146, 112, 127, 124, 180],
                "color": "rgb(55, 83, 109)"
            },
            {
                "x": [1995, 1996, 1997, 1998, 1999, 2000],
                "y": [200, 246, 132, 120, 198, 110],
                "color": "rgb(55, 83, 109)"
            }],
            "labels": ["bar1", "bar2"],
            "title": "bar_chart",
            "xy_axis_title": ["x_title", "y_title"],
            "size": [500, 500]
        }

    def init_block(self):
        self.body = Famcy.div()
        self.body["id"] = self.id

        div_temp = Famcy.div()
        script = Famcy.script()

        self.body.addElement(div_temp)
        self.body.addElement(script)

        static_script = Famcy.script()
        static_script["src"] = "/static/js/bar_chart.js"
        self.body.addStaticScript(static_script)

    def generate_png_file(self, img_name="bar_img"):
        x_name = self.value["xy_axis_title"][0]
        y_name = self.value["xy_axis_title"][1]

        data = {}
        data[x_name] = []
        data[y_name] = []
        data["name"] = []
        for dict, label in zip(self.value["values"], self.value["labels"]):
            data[x_name].extend(dict["x"])
            data[y_name].extend(dict["y"])
            data["name"].extend([label for i in range(len(dict["x"]))])
                    
        df = pd.DataFrame(data)

        fig = go.Figure()
        for contestant, group in df.groupby("name"):
            fig.add_trace(go.Bar(x=group[x_name], y=group[y_name], name=contestant))

        fig.write_image(img_name+".png")

    def render_inner(self):
        """
        context = {
            "values": [{
                "x": [1995, 1996, 1997, 1998, 1999, 2000],
                "y": [219, 146, 112, 127, 124, 180],
                "color": "rgb(55, 83, 109)"
            },
            {
                "x": [1995, 1996, 1997, 1998, 1999, 2000],
                "y": [200, 246, 132, 120, 198, 110],
                "color": "rgb(55, 83, 109)"
            }],
            "labels": ["bar1", "bar2", "bar3"],
            "title": "bar_chart",
            "xy_axis_title": ["x_title", "y_title"]
        }
        """

        data = []
        for dict, label in zip(self.value["values"], self.value["labels"]):
            temp = {}
            temp["x"] = dict["x"]
            temp["y"] = dict["y"]
            temp["type"] = "bar"
            temp["marker"] = {"color": dict["color"]}
            temp["name"] = label

            data.append(temp)

        json_line_dict_values = json.dumps(data)
        json_line_dict_title = json.dumps(self.value["title"])
        json_line_dict_xy_title = json.dumps(self.value["xy_axis_title"])
        json_size = json.dumps(self.value["size"])

        self.body.children[1].innerHTML = 'generateBarChart("%s", %s, %s, %s, %s)' % (self.id, json_line_dict_values, json_line_dict_title, json_line_dict_xy_title, json_size)
        
        return self.body

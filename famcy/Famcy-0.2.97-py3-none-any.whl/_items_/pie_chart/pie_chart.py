import json
import Famcy
from flask import current_app

import plotly.graph_objects as go

class pie_chart(Famcy.FamcyBlock):
    """
    Represents the block to display
    pie_chart. 
    """
    def __init__(self, **kwargs):
        self.value = pie_chart.generate_template_content()
        super(pie_chart, self).__init__(**kwargs)
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
            "values": [
                {
                    "number":1
                }, 
                {  
                    "number":1
                }, 
                {
                    "number":2
                }, 
                {   
                    "number":3
                }
            ],
            "labels": ["pie1", "pie2", "pie3", "pie4"],
            "size": [800, 800], # width, height
        }

    def init_block(self):
        self.body = Famcy.div()
        self.body["id"] = self.id

        div_temp = Famcy.div()
        script = Famcy.script()

        self.body.addElement(div_temp)
        self.body.addElement(script)

        static_script = Famcy.script()
        static_script["src"] = "/static/js/pie_chart.js"
        self.body.addStaticScript(static_script)

    def generate_png_file(self, img_name="bar_img"):
        labels = []
        values = []
        for dict, label in zip(self.value["values"], self.value["labels"]):
            labels.append(label)
            values.append(dict["number"])

        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        fig.write_image(img_name+".png")

    def render_inner(self):
        pie_values = []
        for num in self.value["values"]:
            pie_values.append(num["number"])
            
        json_pie_dict_values = json.dumps(pie_values)
        json_pie_dict_labels = json.dumps(self.value["labels"])
        json_pie_dict_size = json.dumps(self.value["size"])

        self.body.children[1].innerHTML = 'generatePieChart("%s", %s, %s, %s)' % (self.id, json_pie_dict_values, json_pie_dict_labels, json_pie_dict_size)
        
        return self.body
        
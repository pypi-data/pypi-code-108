from abc import ABCMeta, abstractmethod
from typing import List, TypeVar

import pandas as pd

from pipedash.DataRegistryApiService import DataRegistryApiService
from pipedash.DrawableComponentData import DrawableComponentData, DrawableDataInfo
from pipedash.DrawableProperties import DrawableProperty, DrawablePropertyRepeatable, DrawablePropertyBasic


class DrawableComponent(metaclass=ABCMeta):
    _plot_data: []
    _title: str
    _custom_css: str
    _sub_title: str
    def __init__(self):
        self._plot_data = []
        self._title = None
        self._custom_css = None
        self._sub_title = None
        return None

    def get_plotly_template(self):
        return "plotly_white"

    def plot(self, figure):

        if self._plot_data is None:
            self._plot_data = []

        figure.update_layout(template=self.get_plotly_template())

        self._plot_data.append(figure.to_json())
        return True

    def get_custom_css(self):
        return self._custom_css

    def get_title(self):
        return self._title

    def get_sub_title(self):
        return self._sub_title

    def get_output_options(self):
        return {
            "custom_css": self.get_custom_css(),
            "title": self.get_title(),
            "subtitle": self.get_sub_title()
        }

    def subtitle(self, title: str):
        self._sub_title = title

    def title(self, title: str):
        self._title = title

    def custom_css(self, css: str):
        self._custom_css = css

    def get_data(self):
        return {
            "options": self.get_output_options(),
            "plot_data": self.get_plot_data()
        }

    def get_plot_data(self):
        if self._plot_data is None:
            self._plot_data = []
        return self._plot_data

    def load_data(self, kv: DrawableDataInfo):

        api = DataRegistryApiService(kv["registry"])
        data = api.queryData(kv["group"], kv["query"], kv)

        # iterate over data
        """
        rdata = []
        for row in data:
            nrow = {}
            for col_k in row:
                col_v = row[col_k]
                if type(col_v) == dict:
                    col_v =
                nrow[col_k] = col_v
            rdata.append(nrow)
        """

        df = pd.json_normalize(data, sep='.')




        return df

    def fetch_all_option_datastreams(self, properties, options):
        for r in properties:
            if "group" in r:
                if r["key"] in options:
                    for o in range(len(options[r["key"]])):
                        options[r["key"]][o] = self.fetch_all_option_datastreams(r["group"], options[r["key"]][o])
            if r["type"] == "datastream":
                kv = options[r["key"]]
                if kv is not None:
                    nv = self.load_data(kv)
                    options[r["key"]] = nv
        return options

    def _get_child_options(self, name, options):
        for k in options:
            if name == k:
                return options[k]

        return None

    def get_option(self, name):
        if "." in name:

            sub_options = self.options
            path = name.split(".")
            for element in path:
                sub_options = self._get_child_options(element, sub_options)

            return sub_options
        else:
            return self._get_child_options(name, self.options)


    def run_draw_data(self, data: DrawableComponentData):
        self.options = data["component"]["options"]
        self.options = self.fetch_all_option_datastreams(data["component"]["component"]["properties"], self.options)

        self.draw_data(data)
        ### now we send this back

    @abstractmethod
    def draw_data(self, data: DrawableComponentData):
        raise Exception("Method not implemented")

    @abstractmethod
    def get_properties(self) -> List[DrawablePropertyBasic]:
        raise Exception("Method not implemented")

    def get_icon(self):
        return None

TDrawableComponent = TypeVar("TDrawableComponent", bound=DrawableComponent)
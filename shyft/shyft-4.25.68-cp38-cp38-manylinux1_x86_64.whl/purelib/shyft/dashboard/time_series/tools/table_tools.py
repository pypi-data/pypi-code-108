import abc
from typing import Any, Optional, List, Dict

import bokeh
from bokeh.layouts import column
from bokeh.models import Button, PreText, ColumnDataSource, CustomJS

from shyft.dashboard.base import constants
from shyft.dashboard.base.app import Widget, LayoutComponents
from shyft.dashboard.time_series.tools.base import BaseTool


class TableToolError(RuntimeError):
    pass


class TableTool(BaseTool):
    """
    This object represents the base class of all figure tools
    """
    def __init__(self, logger=None):
        """
        Parameters
        ----------
        logger:
            optional logger
        """
        super().__init__(logger=logger)

    @abc.abstractmethod
    def on_bind(self, *, parent: Any):
        pass


class ExportTableDataButton(TableTool, Widget):
    """
    Tool to download all data shown in all figures where this tool is attached to!

    Two obstacles:
    - each obj/renderer in a figure has its own data source with own amount of time, value tuples
    - js callbacks and python callbacks in bokeh are not sync

    Therefore:
    - for each renderer one separate csv file is downloaded
    - we create a bokeh PreText obj in addition to the download button, to which we attach a js callback for the download
    after the download the callback is removed again
    """

    def __init__(self,
                 label: str = 'Download Table Data',
                 height: int = 50,
                 width: int = 150,
                 padding: Optional[int] = None,
                 sizing_mode: Optional[str] = None,
                 logger=None):
        """
        Parameters
        ----------
        logger:
            optional logger
        """
        TableTool.__init__(self, logger=logger)
        Widget.__init__(self, logger=logger)

        padding = padding or constants.widget_padding
        sizing_mode = sizing_mode or constants.sizing_mode

        self.download_button = Button(label=label, width=width, height=height)
        self.download_button.on_click(self.on_click)
        self.download_text = PreText(text="")

        self._layout = column(self.download_text, self.download_button, width=width + padding, height=height,
                              sizing_mode=sizing_mode)

    def on_bind(self, *, parent: Any) -> None:
        pass

    def on_click(self) -> None:
        sources = []
        names = []
        column_name_maps = []
        dummy_dict_for_sorting = []
        for parent in self.parents:
            sources.append(parent.bokeh_data_source)
            names.append(parent.title)
            column_name_maps.append({tc.field: tc.title for tc in parent.table_columns.values()})
            dummy_dict_for_sorting.append({str(i): tc.field for i, tc in enumerate(parent.table_columns.values())})
            # add js callback
        self.download_text.js_on_change("text", self.js_callback(sources=sources,
                                                                 names=names,
                                                                 column_name_maps=column_name_maps,
                                                                 map_of_name_map=dummy_dict_for_sorting))
        # trigger js callback
        self.download_text.text = 'downloading'
        # remove js callback
        for k, v in self.download_text.js_property_callbacks.items():
            if 'text' in k:
                self.download_text.js_property_callbacks[k] = []
        # reset download text
        self.download_text.text = ''

    @staticmethod
    def js_callback(*,
                    sources: List[ColumnDataSource],
                    names: List[str],
                    column_name_maps: List[Dict[str, str]],
                    map_of_name_map: List[Dict[str, str]]) -> str:
        """Creates js to download all data from multiple data sources to multiple csv files"""
        java_script = """
        function table_to_csv(source, column_name_map, map_of_name_map) {  
            /*
            Depending on the browser used, the keys of an Object may or may not be sorted alphabetically/numerically. 
            To ensure that the columns in the downloaded csv file are ordered as the user sees the table in the app,
            we use keys 0,1,2,3, ... (in map_of_name_map) to extract the real keys needed to get match the proper titles
            of the columns with the data of the columns. 
            */
            const sort_keys = Object.keys(map_of_name_map)
            const nrows = source.get_length()
            let row = []
            for (let j = 0; j < sort_keys.length; j++) {
                const column = map_of_name_map[sort_keys[j]]
                console.log(column)
                row.push(column_name_map[column].toString())
            }
            const lines = [row.join(';')]
            for (let i = 0; i < nrows; i++) {
                let multi = false;
                let nrows_multi = 0;
                for (let j = 0; j < sort_keys.length; j++) {
                    const column = map_of_name_map[sort_keys[j]]
                    
                    if (Array.isArray(source.data[column][i])) {
                        multi = true
                        nrows_multi = source.data[column][i].length
                        break
                    }
                }
                if (multi) {
                    for (let k = 0; k < nrows_multi; k++) {
                        let row = []
                        for (let j = 0; j < sort_keys.length; j++) {
                            const column = map_of_name_map[sort_keys[j]]
                            let data = source.data[column][i]
                            if (Array.isArray(data) || typeof(data) === 'object'){
                                row.push(data[k].toString())
                            }
                            else {
                                row.push(data.toString())
                            }                            
                        }
                        lines.push(row.join(';'))    
                    }
                } else {
                    let row = [];
                    for (let j = 0; j < sort_keys.length; j++) {
                        const column = map_of_name_map[sort_keys[j]]
                        row.push(source.data[column][i].toString())
                    }
                    lines.push(row.join(';'))
                }
            }
            return lines.join('\\n').concat('\\n')
        }


        for (var i = 0; i < sources.length; i++){

            var source = sources[i]
            var name = names[i]
            var column_name_map = column_name_maps[i]
            var map_of_name_map = map_of_name_map[i]  

            try {
                const filename = "data-"+name+".csv";
                var filetext = table_to_csv(source, column_name_map, map_of_name_map)
                const blob = new Blob([filetext], { type: 'text/csv;charset=utf-8;' })

                const link = document.createElement('a')
                link.href = URL.createObjectURL(blob)
                link.download = filename
                link.target = '_blank'
                link.style.visibility = 'hidden'
                link.dispatchEvent(new MouseEvent('click'))
              } catch (error) {
                console.error(error)
              }
        }
"""
        return CustomJS(args=dict(sources=sources, names=names, column_name_maps=column_name_maps, map_of_name_map=map_of_name_map), code=java_script)

    @property
    def layout_components(self) -> LayoutComponents:
        return {'widgets': [self.download_text, self.download_button], 'figures': []}

    @property
    def layout(self) -> bokeh.models.LayoutDOM:
        return self._layout

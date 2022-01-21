import pandas as _pd
import numpy as _np
from dash import html
from dash import dash_table


class ParamHandler:

    def __init__(self, mongo=None, apps=None, metaColumns=None, name=None, port=None, appName=None, df=None):
        """ create the typical parameter meta handling for a dashpool app

        mongo => mongo db
        apps => array of apps handeled with this meta handler
        metaColumns => columns we want to handle
        name => name of the main app

        """
        if (df is not None) and isinstance(df, _pd.DataFrame):
            self.__static = True
            self.paramHeader = [{"id": m, "name": m} for m in df.columns]
            self.paramTableData = df.to_dict('records')
        else:
            self.__static = False
        self._mongo = mongo
        self._apps = apps
        self._metaColumns = metaColumns
        self._name = name
        self._appName = appName
        self._port = port

    def trafoData(self, df):
        print("ParamHandler.trafoData: {}".format(self._name))

        self._params = self._mongo.db.params.find_one({"name": self._name})

        if self._params == None:
            # create an emply default config

            self._params = {"name": self._name,
                            "port": self._port,
                            "appName": self._appName,
                            "config": [{"input": el,
                                        "output": el,
                                        "joinid": 0,
                                        **{m: "" for m in self._metaColumns},
                                        **{"app_"+a: False for a in self._apps}
                                        } for el in df.columns]}
            print("save new configuration in Mongo ({})".format(self._name))
            self._mongo.db.params.insert_one(self._params)

        # check if new input colums apeared
        oldCols = [p["input"] for p in self._params["config"]]
        addedNewCol = False
        for el in df.columns:
            if el not in oldCols:
                # add the new colum to the config part
                self._params["config"].append({"input": el,
                                               "output": el,
                                               "joinid": 0,
                                               **{m: "" for m in self._metaColumns},
                                               **{"app_"+a: False for a in self._apps}
                                               })
                addedNewCol = True
        if addedNewCol:
            # update mongo db if new collum appeared
            print("update configuration in Mongo ({})".format(self._name))
            self._mongo.db.params.update_one(
                {"name": self._name},
                {"$set": {"config":  self._params["config"]}}
            )

        # apply the column transformations
        outdf = df
        columnDF = _pd.DataFrame(self._params["config"])
        renameCols = {}
        for group, vals in columnDF.groupby("output"):
            # columns need a rename
            if(len(vals) == 1 and vals["input"].values[0] != vals["output"].values[0]):
                print("apply rename ({} => {})".format(
                    vals["input"].values[0], vals["output"].values[0]))
                renameCols[vals["input"].values[0]] = vals["output"].values[0]

            # columns need to be joined
            if(len(vals) > 1):
                input_cols = vals.sort_values(by="joinid")["input"].values

                # remove not known columns
                input_cols = [el for el in input_cols if el in outdf.columns]

                def mapfirst(x):
                    if x.first_valid_index() is None:
                        return None
                    else:
                        return x[x.first_valid_index()]

                print("apply merge ({} => {})".format(input_cols, group))
                outdf[group] = outdf[input_cols].apply(mapfirst, axis=1)

        print("final rename of {} cols".format(len(renameCols)))
        outdf.rename(index=str, columns=renameCols, inplace=True)

        # calculate the data needed to initialize a dash datatable header
        self.paramHeader = [
            {"id": "output", "name": "Name"},
            *[{"id": m, "name": m} for m in self._metaColumns]
        ]

        # calculate the data needed to initialize a specific datatable of an subapp
        self.paramTableData = {}  # data needed to show the meta table description
        self.publicCols = {}  # data to hide private columns from plotters and filters
        for a in self._apps:
            publicRows = []
            publicEntries = []

            for el in self._params["config"]:
                if ("app_"+a in el and el["app_"+a] and "joinid" in el and el["joinid"] == 0):
                    publicRows.append(
                        {
                            "output": el["output"],
                            **{m: el[m] for m in self._metaColumns if m in el},
                        }
                    )
                    publicEntries.append(el["output"])
            self.paramTableData[a] = publicRows
            self.publicCols[a] = publicEntries

        # return the transformed dataframe
        return outdf

    def getParamMenuLayout(self):
        """
        create the typical layout of a dashpool Param Menu
        """

        if self.__static:
            return html.Div([
                html.H4("Parameters"),
                dash_table.DataTable(
                    id='param-table',
                    editable=False,
                    css=[{"selector": ".show-hide", "rule": "display: none"}],
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    page_action="native",
                    columns=self.paramHeader,
                    data=self.paramTableData,
                    style_cell={'textAlign': 'left'},
                )
            ], style={'width': '800'})
        else:
            return html.Div([
                html.H4("Parameters"),
                dash_table.DataTable(
                    id='param-table',
                    editable=False,
                    css=[{"selector": ".show-hide", "rule": "display: none"}],
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    page_action="native",
                    columns=self.paramHeader,
                    style_cell={'textAlign': 'left'},
                )
            ], style={'width': '800'})

import pandas as pd
import numpy as np
import datetime as dt

import warnings

warnings.filterwarnings("ignore")

from datetime import date, datetime, timedelta
import time

import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


today = datetime.today()
todayStr = today.strftime("%Y%m%d%H%M")

start_time = time.time()


class Plotly:
    def barchart_1d(self, df, metrics_list, dimensions_list, secondary_metrics=None):
        if df is None:
            print("Error Plotly")
            return

        print(" ==== ", secondary_metrics)

        df = df.set_index(dimensions_list)

        # plotly setup
        fig1 = go.Figure()

        if secondary_metrics:
            fig1 = make_subplots(specs=[[{"secondary_y": True}]])
            df[[secondary_metrics]] = (
                df[[secondary_metrics]]
                .replace({"\$": "", ",": "", "%": ""}, regex=True)
                .astype(float)
            )
            fig1.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[secondary_metrics],
                    name=secondary_metrics,
                    yaxis="y2",
                    mode="lines+markers",
                )
            )

        y_axis = 1
        # add trace for eat
        for col in metrics_list:
            df[[col]] = (
                df[[col]]
                .replace({"\$": "", ",": "", "%": ""}, regex=True)
                .astype(float)
            )
            fig1.add_trace(
                go.Bar(x=df.index, y=df[col], name=col, yaxis="y", offsetgroup=y_axis)
            ),
            y_axis += 1

        fig1.update_xaxes(tickangle=90)

        fig1.update_layout(
            autosize=False,
            width=1100,
            height=800,
            font=dict(family="Courier", size=12, color="#222323"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            title=str(
                "Analysis - "
                + str([i.upper() for i in metrics_list])
                + " by "
                + str([i.upper() for i in df.index])
            ),
            xaxis_title="Mesures",
            yaxis_title="Dimensions",
            legend_title="Type",
            legend=dict(
                x=0,
                y=-0.5,
                traceorder="reversed",
                title_font_family="Times New Roman",
                font=dict(family="Courier", size=12, color="#222323"),
                bgcolor="white",
                bordercolor="Black",
                borderwidth=2,
            ),
        )

        return fig1

    def html_report(self, data_df1, fig1, data_df2, fig2):
        html_start = (
            """
                    <!doctype html>
                    <html lang="en">
                    <head>

                        <!-- Required meta tags -->
                        <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

                        <!-- Bootstrap CSS -->
                        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">

                        <!-- Font Awesome -->
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">

                        <style type="text/css">
                        body {
                            background-color: #f0f6f0;
                        }
                        
                        h1,h2,h3 {
                            padding-top: 50px;
                            color: black;
                        }

                        .center {
                            text-align: center;
                        }

                        /* Add a black background color to the top navigation */
                        .topnav {
                            background-color: #333;
                            margin-top: 50px;
                            overflow: hidden;
                            position: sticky;
                            top: 0;
                            z-index: 2;
                        }

                        /* Style the links inside the navigation bar */
                        .topnav a {
                            float: left;
                            color: #f2f2f2;
                            text-align: center;
                            padding: 14px 16px;
                            text-decoration: none;
                            font-size: 17px;
                        }

                        /* Change the color of links on hover */
                        .topnav > a:hover {
                            background-color: #ddd;
                            color: black;
                        }

                        /* Add a color to the active/current link */
                        .topnav > a.active {
                            background-color: #04AA6D;
                            color: white;
                        }

                        </style>

                        <title>Google Analytics - Monthly Activity Report - Rocketry 113</title>

                    </head>

                    <div class = "container">

                    <body>
                        <div class="topnav">
                            <a class="active" href="#top">Top</a>
                            <a href="#device">Device</a>
                            <a href="#bounce">Bounce Rate</a>
                        </div>

                        <!-- Script -->
                        <script src='http://ajax.aspnetcdn.com/ajax/jQuery/jquery-3.2.1.js'></script>
                        <script type="text/javascript">
                            $('.topnav a').click(function(){
                                $(this).addClass('active').siblings().removeClass('active');
                            });
                        </script>
                        <h1 id="top">Google Analytics - Monthly Activity Report</h1>
                        <h4 style="color:grey"> """
            + dt.datetime.strftime(dt.datetime.now(), "%b %-d, %Y")
            + """</h4>
                    """
        )

        html_end = """

                        </div>
                        </div>

                        </body>
                        </html>

                    """

        with open("html_report.html", "w") as f:
            f.write(html_start)

            f.write('<h2 id="device">Device Data</h2>')
            f.write(fig1.to_html(full_html=False, include_plotlyjs="cdn"))
            if fig2 == "pass":
                print("null")
            else:
                f.write('<h2 id="bounce">Bounce Rate & Users Data</h2>')
                f.write(fig2.to_html(full_html=False, include_plotlyjs="cdn"))
            # for i in lst:
            #    f.write(chart_func(i).to_html(full_html=False, include_plotlyjs='cdn'))

            f.write(html_end)

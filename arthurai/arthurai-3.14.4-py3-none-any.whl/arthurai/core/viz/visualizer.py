import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Any, List

from arthurai.common.exceptions import arthur_excepted
from arthurai.core.viz import style, utils
import warnings
warnings.filterwarnings('ignore')


class DataVisualizer(object):
    def __init__(self, arthur_models):
        self.models = arthur_models

    @arthur_excepted("failed to generate timeline")
    def timeline(self, attribute_name):
        """Generates a visualization of the distribution of an attribute over time. 
        For categorical attributes, a stacked area chart over time.
        For continuous attributes, a joyplot showing probability densities over time.
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        for model in self.models:
            if model.get_attribute(attribute_name).categorical:
                self._timeline_categorical(model, attribute_name)
            else:
                self._timeline_continuous(model, attribute_name)

    @arthur_excepted("failed to generate metric series")
    def metric_series(self, metric_names, time_resolution="day"):
        """Generates a line series visualization for selected metrics.
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        fig = plt.figure(figsize=(20,4))
        ax = fig.add_subplot(1, 1, 1)
        predicted_property, ground_truth_property = utils.get_pred_and_gt_attrs(self.models[0])
        pal = style.categorical_palette

        # Define list of palettes to be used
        num_metrics = len(metric_names)
        max_metrics = len(style.multi_categorical_palette_names)
        if num_metrics > max_metrics:
            raise UserValueError(f"Too many metrics to display. The maximum is {max_metrics}, you wanted to see {num_metrics}")
        color_palette_names = style.multi_categorical_palette_names[0:num_metrics]

        for metric_index, metric_name in enumerate(metric_names):
            color_palette = sns.color_palette(palette=color_palette_names[metric_index], n_colors=len(self.models))
            for model_index, model in enumerate(self.models):
                if model.is_batch:
                    time_resolution = "batch_id"
                    query = _metric_series_batch_query(metric_name, ground_truth_property,
                        predicted_property, model.classifier_threshold)
                else:
                    query = _metric_series_streaming_query(metric_name, time_resolution,
                        ground_truth_property, predicted_property, model.classifier_threshold)

                response = model.query(query)
                df = pd.DataFrame(response)[::-1]

                label = _label(model, metric_name)
                color = _alpha_color(color_palette[model_index])
                plt.plot(df[time_resolution], df[metric_name], lw=12, color=color, label=label)
                plt.plot(df[time_resolution], df[metric_name], lw=2, color=color)
                plt.xticks([])
                ax.spines['right'].set_visible(False)
                ax.spines['top'].set_visible(False)
                plt.legend(loc="upper left", facecolor="white")

    @arthur_excepted("failed to generate drift series")
    def drift_series(self, attribute_names, drift_metric="PSI", time_resolution="day"):
        """Generates a line series visualization of data drift metrics for selected attributes.
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        fig = plt.figure(figsize=(20,4))
        ax = fig.add_subplot(1, 1, 1)
        labels = []

        # Define list of palettes to be used
        color_palettes = _drift_color_palettes(len(attribute_names), len(self.models))

        for model_index, model in enumerate(self.models):
            if model.is_batch:
                time_resolution = "batch_id"
            timestamp_query = _batch_timestamp_query()
            drift_query = {
                "properties": attribute_names,
                "num_bins": 20,
                "rollup": time_resolution,
                "base": {
                "source": "reference"
                },
                "target": {
                "source": "inference"
                },
                "metric": drift_metric
            }
            if model.is_batch:
                drift_df = pd.DataFrame(model.query(drift_query, query_type="drift"))
                timestamp_df = pd.DataFrame(model.query(timestamp_query))
                df = drift_df.rename(columns={"rollup":time_resolution}
                    ).join(timestamp_df.set_index(time_resolution), on=time_resolution
                    ).sort_values(by="timestamp"
                    ).set_index(time_resolution)
            else:
                df = pd.DataFrame(model.query(drift_query, query_type="drift")
                        ).sort_values(by="rollup").set_index("rollup")

            for attribute_name in attribute_names:
                labels.append(_label(model, attribute_name))

            # base_color_palette = style.categorical_palette
            color_palette = color_palettes[model_index]
            # This darkens the color for each successive model version. There are probably better way of doing this
            # but this is just a hack to get it to work for now.
            # for color_tuple in base_color_palette:
            #     color_palette.append((color_tuple[0] / (2 ** model_index), color_tuple[1] / (2 ** model_index), color_tuple[2] / (2 ** model_index), color_tuple[3]))
            df[attribute_names].plot(ax=ax, color=color_palette, lw=8)
            plt.ylabel(drift_metric)
            plt.xticks([])
            plt.xlabel("")
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
        plt.legend(labels, loc="upper left", facecolor="white")

    def _timeline_categorical(self, model, attribute_name, time_resolution="day"):
        """
        """
        print(_label(model, attribute_name))
        if model.is_batch:
            time_resolution="timestamp"
            query = _timeline_categorical_batch_query(attribute_name, time_resolution)
        else:
            query = _timeline_categorical_streaming_query(attribute_name, time_resolution)
        response = model.query(query)
        df = pd.DataFrame(response
            ).sort_values(by=time_resolution
            ).pivot(index=time_resolution,columns=attribute_name, values="count"
            ).fillna(0.0)

        sns.set(style="white")
        fig = plt.figure(figsize=(20,4))
        ax = fig.add_subplot(1, 1, 1)
        plt.stackplot(df.index.values, df.values.T.tolist(),
            labels=df.columns.values, colors=style.categorical_palette)
        plt.xticks([])
        plt.ylabel("Count")
        plt.legend(loc='upper right')
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        plt.show()



    def _timeline_continuous(self, model, attribute_name, time_resolution="day"):
        """
        """
        print(_label(model, attribute_name))
        if model.is_batch:
            time_resolution="timestamp"
            query = _timeline_continuous_batch_query(attribute_name, time_resolution)
        else:
            query = _timeline_continuous_streaming_query(attribute_name, time_resolution)
        response = model.query(query)

        dfs= []
        for group in response:
            temp_df= pd.DataFrame(group["distribution"])
            temp_df[time_resolution] = group[time_resolution]
            temp_df["count"] = utils.savgol_filter(temp_df["count"])
            dfs.append( temp_df)
        df = pd.concat(dfs).sort_values([time_resolution, "lower"])

        global_y_min = df["lower"].min()
        global_y_max = df["lower"].max()
        global_x_min = df["count"].min()
        global_x_max = df["count"].max()

        sns.set(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})
        # Initialize the FacetGrid object
        pal = style.continuous_palette
        g = sns.FacetGrid(df, col=time_resolution, hue=time_resolution, aspect=.2, height=8, palette=pal, subplot_kws={"xlim":(global_x_max, global_x_min), "ylim":(global_y_min, global_y_max)})

        # Draw the densities in a few steps
        g.map(plt.plot, "count", "lower",clip_on=False,  color="white", lw=4.5,  alpha=0.6)
        g.map(plt.fill_between, "count","lower", clip_on=False, lw=2)

        # Set the subplots to overlap
        g.fig.subplots_adjust(wspace=-.55, left = 0.125)
        g.set_titles("")
        g.set(yticks=[])
        g.set(xticks=[])
        g.set(ylabel="")
        g.set(xlabel="")
        g.despine(bottom=True, left=True)


def _metric_series_streaming_query(metric_name, time_resolution, ground_truth_property, predicted_property, classifier_threshold):
    """Generates query for fetching metrics for streaming model.
    """
    query = {
                "select": [
                    {
                        "function": metric_name,
                        "alias": metric_name,
                        "parameters": {
                            "ground_truth_property": ground_truth_property,
                            "predicted_property": predicted_property,
                            "threshold": classifier_threshold
                        }

                    },

                    {
                        "function": "roundTimestamp",
                        "alias": time_resolution,
                        "parameters": {
                            "property": "inference_timestamp",
                            "time_interval": time_resolution
                        }
                    }
                ],
                "group_by": [
                    {
                        "alias": time_resolution
                    }
                ],
                "order_by": [
                    {
                        "alias": time_resolution,
                        "direction": "desc"
                    }
                ]
            }
    return query


def _metric_series_batch_query(metric_name, ground_truth_property, predicted_property, classifier_threshold):
    """Generates query for fetching metrics for batch model.
    """
    query = {
                "select": [
                    {"function": metric_name,
                        "alias": metric_name,
                        "parameters": {
                            "ground_truth_property": ground_truth_property,
                            "predicted_property": predicted_property,
                            "threshold": classifier_threshold
                        }

                    },
                    {
                        "function":"max",
                        "parameters": {"property":"inference_timestamp"},
                        "alias":"timestamp"
                    },
                    {"property":"batch_id"}
                ],
                "group_by": [
                    {
                        "property":"batch_id"
                    }
                ],
                "order_by": [
                    {
                        "alias":"timestamp",
                        "direction": "desc"
                    }
                ]
            }
    return query


def _timeline_continuous_streaming_query(attribute_name, time_resolution):
    """Generates a query for continuous attribute in a streaming model.
    """
    return {
        "select":[
            {
                "function":"distribution",
                "alias":"distribution",
                "parameters":{"property": attribute_name, "num_bins":50}
            },
            {
                "function": "roundTimestamp",
                "alias": time_resolution,
                "parameters": {
                    "property": "inference_timestamp",
                    "time_interval": time_resolution
                    }
            }
        ],
        "group_by": [{"alias":time_resolution} ],
        "order_by": [{"alias":time_resolution, "direction": "desc"} ]
    }


def _timeline_continuous_batch_query(attribute_name, time_resolution):
    """Generates a query for continuous attribute in a batch model.
    """
    return {
        "select":[
            {
                "function":"distribution",
                "alias":"distribution",
                "parameters":{"property": attribute_name, "num_bins":50}
            },
            {
                "function":"max",
                "alias":"timestamp",
                "parameters": {"property":"inference_timestamp"}
            },
            {"property": "batch_id"}
        ],
        "group_by": [
            {
                "property":"batch_id"
            }
        ],
        "order_by": [
            {
                "alias":"timestamp",
                "direction": "desc"
            }
        ]
    }


def _timeline_categorical_streaming_query(attribute_name, time_resolution):
    """Generates a query for categorical attribute in a streaming model.
    """
    return {
        "select": [
            {
                "property": attribute_name
            },
            {
                "function": "count"
            },
            {
                "function": "roundTimestamp",
                "alias": time_resolution,
                "parameters": {
                    "property": "inference_timestamp",
                    "time_interval": time_resolution
                }
            }
        ],
        "group_by": [
            {
                "property": attribute_name
            },
            {
                "alias": time_resolution
            }
        ],
        "order_by": [
            {
                "property": attribute_name
            },
            {
                "alias": time_resolution,
                "direction": "desc"
            }
        ]
    }


def _timeline_categorical_batch_query(attribute_name, time_resolution):
    """Generates a query for categorical attribute in a batch model.
    """
    return {
        "select": [
            {
                "property": attribute_name
            },
            {
                "function": "count"
            },
            {
                "property":"batch_id"
            },
            {"function":"max", "parameters": {"property":"inference_timestamp"}, "alias":"timestamp"}
        ],
        "group_by": [
            {
                "property": attribute_name
            },
            {
                "property":"batch_id"
            }
        ],
        "order_by": [
            {
                "property": attribute_name
            },
            {
                "alias":"timestamp",
                "direction": "desc"
            }
        ]
    }


def _batch_timestamp_query():
    return {
        "select":[
            {
                "function":"max",
                "alias":"timestamp",
                "parameters": {"property":"inference_timestamp"}
            },
            {"property": "batch_id"}
        ],
        "group_by": [
            {
                "property":"batch_id"
            }
        ],
        "order_by": [
            {
                "alias":"timestamp",
                "direction": "desc"
            }
        ]
    }


def _label(model, label):
    return model.partner_model_id + "__" + label  # TODO [TMJ]: When model groups are added, make this (model_group_name)__(version_sequence_num)__(attribute)


def _alpha_color(color):
    return (color[0], color[1], color[2], style.alpha)


def _drift_color_palettes(num_attributes, num_models):
    max_attributes = len(style.multi_categorical_palette_names)
    if num_attributes > max_attributes:
        raise UserValueError(
            f"Too many attributes to display. The maximum is {max_attributes}, you wanted to see {num_attributes}")

    color_palettes = []
    color_palette_names = style.multi_categorical_palette_names[0:num_attributes]
    for i in range(num_models):
        color_palettes.append([])
    for color_palette_name in color_palette_names:
        base_palette = sns.color_palette(palette=color_palette_name, n_colors=num_models)
        for i, base_palette_color in enumerate(base_palette):
            color_palettes[i].append(_alpha_color(base_palette_color))

    return color_palettes

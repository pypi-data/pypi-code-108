import logging
import math

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_freq_bar(df, protocol, column, title, plot_type="bar", log_scale=False):
    """
    Plots the frequency of different values of a column across the dataset

    Parameters
    ----------
    df : pd.DataFrame
      The DataFrame containing the desired data.
    protocol : str
      The Protocol of the DataFrame (e.g. Mosquito Habitat Mapper or Land Cover)
    column : str
      The name of the column that the graph will plot.
    title : str
      The title of the graph
    plot_type : str, default="bar"
      The type of graph that will be used to visually compare the data.
    log_scale : bool, default=False
      If a log scale will be used for the data. If true, all the values will be in Log 10.
    """
    col_vals = pd.DataFrame()
    col_vals["Count"] = df.groupby(column).size()
    col_vals.reset_index(inplace=True)
    col_vals.columns = ["index", "Count"]
    if len(col_vals) <= 1:  # pragma: no cover
        logging.warning(
            f"There is only one value for this column: {col_vals['index'][0]}: {col_vals['Count'][0]}"
        )
    plt.figure(figsize=(10, 6))
    ylabel = "Frequency"
    title = f"{protocol} - {title}"
    if log_scale:
        col_vals["Count"] = pd.Series([math.log10(val) for val in col_vals["Count"]])
        ylabel += " (Log Scale)"
        title += " (Log Scale)"
    if plot_type == "line":  # pragma: no cover
        plt.plot(col_vals["index"], col_vals["Count"], color="lightblue")
    else:
        plt.bar(col_vals["index"], col_vals["Count"], color="lightblue")

    plt.title(title)
    plt.xlim(left=-0.5)
    plt.xlabel(f"{column} Values")
    plt.ylabel(ylabel)


def multiple_bar_graph(df, protocol, cols, title, log_scale=False):
    """
    Plots the frequency of different values of a column across the dataset alongside eachother.

    Parameters
    ----------
    df : pd.DataFrame
      The DataFrame containing the desired data.
    protocol : str
      The Protocol of the DataFrame (e.g. Mosquito Habitat Mapper or Land Cover)
    cols : list str
      The names of the columns that the graph will plot.
    title : str
      The title of the graph
    log_scale : bool, default=False
      If a log scale will be used for the data. If true, all the values will be in Log 10.
    """

    def create_summary_df(cols):
        """
        data = df
        x = [0,6]
        hue = photoType: photocount, rejectedcount, etc
        """
        photo_summary = pd.DataFrame()
        for name in cols:
            photo_summary[name] = df[name].value_counts()
            # print(type(photo_summary[name]))
        photo_summary.sort_index(inplace=True)
        photo_summary = photo_summary.reset_index()
        # print(photo_summary)

        category_counts = []

        for name in cols:
            for j in range(len(photo_summary)):
                count = photo_summary[name][j]
                if log_scale:
                    count = math.log10(count)
                new_row = {
                    "index": photo_summary["index"][j],
                    "category": name,
                    "count": count,
                }
                category_counts.append(new_row)
        category_counts = pd.DataFrame(category_counts)
        return category_counts

    category_counts = create_summary_df(cols)
    plt.figure(figsize=(10, 6))

    title = f"{protocol} -- {title}"
    ylabel = "Frequency"
    if log_scale:
        ylabel += " (Log Scale)"
        title += " (Log Scale)"

    ax = sns.barplot(
        data=category_counts,
        x="index",
        y="count",
        hue="category",
        palette=[
            "#377eb8",
            "#ff7f00",
            "#4daf4a",
            "#f781bf",
            "#a65628",
            "#984ea3",
            "#999999",
            "#e41a1c",
            "#dede00",
        ],
    )
    ax.set_xlabel("Photo Count")
    ax.set_ylabel(ylabel)

    ax.set_title(title)
    plt.legend(loc="upper right")


def plot_int_distribution(df, col_name, title_name):
    """
    Plots the frequency of different integer values of a column across a cleaned dataset

    Parameters
    ----------
    df : pd.DataFrame
      The DataFrame containing the desired data.
    col_name : str
      The name of the column that the graph will plot.
    title_name : str
      The name of the column as you would like to have as the title (e.g. mhm_Genus could be just Genus in the title)
    """
    df = df.copy()
    df[col_name] = df[col_name].replace(-9999, -5)

    counts = df.groupby(col_name).size()
    title = f"{title_name} Distribution (with Null)"
    plt.figure(figsize=(10, 5))
    plt.title(title)
    plt.ylabel(f"{title_name} Entries  (Log Scale)")
    plt.yscale("log")
    plt.bar(counts.index, counts, color="#b30000")


def completeness_histogram(df, protocol, completeness_col, completeness_type):
    """
    Plots a histogram of the completeness score distribution.

    Parameters
    ----------
    df : pd.DataFrame
      The DataFrame containing the desired data.
    protocol : str
      The name of the protocol that the graph will plot.
    completeness_col : str
      The column containing the desired completeness metric
    completness_type : str
      The type of completeness score (Sub or Cumulative)
    """
    plt.figure(figsize=(10, 4))
    title = f"{protocol} -- {completeness_type} Completeness Scores Frequency Histogram"
    plt.title(title)
    plt.hist(df[completeness_col], color="pink", label=completeness_type)
    plt.xlabel("Scores")
    plt.ylabel("Count")


def save_stored_plots():
    """
    Saves any generated graphs currently stored by the pyplot object.
    """
    for num in plt.get_fignums():
        plt.figure(num)
        title = plt.gca().get_title()
        plt.savefig(f"{title}.png")

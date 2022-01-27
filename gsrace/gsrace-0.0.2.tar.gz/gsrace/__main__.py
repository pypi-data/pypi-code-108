import click
import pandas as pd
from joblib import Parallel, delayed
from tqdm import tqdm

from gsrace import __version__

from ._bar_chart_race import bar_chart_race
from ._scholarly import _Scholarly
from .utils import tqdm_joblib


@click.version_option(version=__version__)
@click.command()
@click.argument("google_scholar_id", required=True, type=str)
@click.option(
    "--output_directory",
    "-o",
    default=".",
    type=click.Path(file_okay=False, dir_okay=True, readable=True, resolve_path=True),
    show_default=True,
    help="Directory to write the output GIF file.",
)
@click.option(
    "--n_threads",
    "-p",
    default=4,
    type=int,
    show_default=True,
    help="Number of threads to use for extracting papers information.",
)
@click.option(
    "--dpi",
    "-d",
    default=142,
    type=int,
    show_default=True,
    help="Resolution of output GIF file.",
)
@click.option(
    "--height",
    "-h",
    default=5,
    type=int,
    show_default=True,
    help="Height of output GIF file.",
)
@click.option(
    "--width",
    "-w",
    default=10,
    type=int,
    show_default=True,
    help="Width of output GIF file.",
)
def main(google_scholar_id, output_directory, n_threads, height, width, dpi):
    """Google Scholar Journal Race."""
    data, name, _ = extract_papers(google_scholar_id, n_threads)
    _, df2 = build_dataframe(data)
    generate_plot(df2, output_directory, name, width, height, dpi)


def extract_papers(google_scholar_id, n_threads):
    scholarly = _Scholarly()
    author = scholarly.search_author_id(google_scholar_id)
    name = author["name"]
    print(f"Looking for {name}'s papers trend.")
    pubs = scholarly.fill(author, sections=["publications"])["publications"]
    with tqdm_joblib(
        tqdm(
            ascii=True,
            ncols=120,
            desc="Extracting papers",
            total=len(pubs),
            position=0,
            disable=False,
            unit="paper",
        )
    ):
        papers = Parallel(n_jobs=n_threads)(delayed(scholarly.fill)(p) for p in pubs)

    data = []
    for p in papers:
        if "pub_year" in p["bib"] and "pub_month" in p["bib"] and "pub_day" in p["bib"]:
            if "journal" in p["bib"]:
                journal = p["bib"]["journal"].lower()
                year = p["bib"]["pub_year"]
                month = p["bib"]["pub_month"]
                day = p["bib"]["pub_day"]
                data.append(
                    {
                        "journal": journal,
                        "year": year,
                        "month": month,
                        "day": day,
                    }
                )
            elif "conference" in p["bib"]:
                conference = p["bib"]["conference"].lower()
                year = p["bib"]["pub_year"]
                month = p["bib"]["pub_month"]
                day = p["bib"]["pub_day"]
                data.append(
                    {
                        "journal": conference,
                        "year": year,
                        "month": month,
                        "day": day,
                    }
                )
        else:
            pass
    return data, name, papers


def build_dataframe(data):
    df = pd.DataFrame(data)
    df["journal"] = df["journal"].apply(
        lambda x: x.split(" ")[0] if "arxiv" in x else x
    )
    df["datetime"] = pd.to_datetime(df[["year", "month", "day"]])
    df["value"] = 1
    df2 = df.pivot_table(
        index="datetime",
        columns="journal",
        values="value",
        aggfunc="count",
        fill_value=0,
    )
    df2 = df2.cumsum(axis=0)
    return df, df2


def generate_plot(df2, output_directory, name, width, height, dpi):
    print("Generating plot...")
    bar_chart_race(
        df=df2,
        filename=f"{output_directory}/{name}.gif",
        orientation="h",
        sort="desc",
        n_bars=min(24, df2.shape[0]),
        fixed_order=False,
        fixed_max=True,
        steps_per_period=20,
        period_length=500,
        end_period_pause=0,
        interpolate_period=False,
        period_label={"x": 0.98, "y": 0.3, "ha": "right", "va": "center"},
        period_template="%B, %Y",
        period_summary_func=lambda v, r: {
            "x": 0.98,
            "y": 0.2,
            "s": f"Total papers: {v.sum():,.0f}",
            "ha": "right",
            "size": 11,
        },
        colors="dark24",
        title=f"{name}'s publications race",
        bar_size=0.95,
        bar_textposition="inside",
        bar_texttemplate="{x:,.0f}",
        bar_label_font=7,
        tick_label_font=7,
        tick_template="{x:,.0f}",
        shared_fontdict=None,
        scale="linear",
        fig=None,
        writer=None,
        # bar_kwargs={'alpha': .7},
        fig_kwargs={"figsize": (width, height), "dpi": dpi},
        filter_column_colors=True,
    )
    print(f"Ouptut was saved at {output_directory}/{name}.gif")


if __name__ == "__main__":
    main()

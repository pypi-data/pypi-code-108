import click
from progress.spinner import Spinner
import requests
import time
import sys

url = "https://wowless.dev/api/v1/run"


@click.group()
@click.version_option(package_name="wowless-cli")
def wowless():
    pass


@wowless.group()
def alpha():
    pass


@alpha.command()
@click.option(
    "--product",
    "-p",
    required=True,
    type=click.Choice(
        [
            "wow",
            "wowt",
            "wow_classic",
            "wow_classic_ptr",
            "wow_classic_era",
            "wow_classic_era_ptr",
        ]
    ),
)
@click.option("--loglevel", "-l", default=0)
@click.argument("zip", type=click.File("rb"))
def run(product, loglevel, zip):
    # Step 1: Get a runid and an upload URL.
    r = requests.put(url, json={"product": product})
    r.raise_for_status()
    runid, uploadurl = r.json()["runid"], r.json()["url"]

    # Step 2: Upload the addon zip.
    requests.put(
        uploadurl, headers={"Content-Type": "application/zip"}, data=zip
    ).raise_for_status()

    # Step 3: Queue the wowless run.
    r = requests.post(
        url,
        json={
            "loglevel": loglevel,
            "products": [product],
            "runid": runid,
        },
    )
    r.raise_for_status()
    runid = r.json()[product]

    # Step 4: Poll for wowless run completion.
    wait = 1.0
    for _ in Spinner(f"waiting for runid {runid} to complete... ").iter(
        range(400)
    ):
        wait = wait * 1.1
        time.sleep(wait)
        r = requests.get(url, params={"runid": runid})
        r.raise_for_status()
        j = r.json()
        if "status" in j and j["status"] == "done":
            for k, v in j["rawlogurls"].items():
                r = requests.get(v, stream=True)
                r.raise_for_status()
                print(k)
                for line in r.iter_lines(decode_unicode=True):
                    print(line)
            return
    print("task never finished", file=sys.stderr)


if __name__ == "__main__":
    wowless()

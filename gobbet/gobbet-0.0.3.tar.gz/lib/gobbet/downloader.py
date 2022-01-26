import htmllistparse
import tqdm
import os
import requests

url = "https://dumps.wikimedia.org/other/cirrussearch/current/"


def news_dir():
    newsdir = os.path.expanduser("~/.gobbet")
    if not os.path.isdir(newsdir):
        os.mkdir(newsdir)
    return newsdir


def get_available(which="wikinews"):
    cwd, listing = htmllistparse.fetch_listing(url, timeout=30)
    return {
        l.name[0:2]: l.name for l in listing if which in l.name and "content" in l.name
    }


def download_articles(lang="en", which="wikinews"):
    news_path = os.path.join(news_dir(), f"{lang}.json.gz")
    available = get_available(which)
    if lang not in available:
        raise ValueError("No news for language '%s'" % lang)

    with open(news_path, "wb") as f:
        response = requests.get(url + available[lang], stream=True)
        total_length = response.headers.get("content-length")

        if total_length is None:  # no content length header
            f.write(response.content)
        else:
            dl = 0
            with tqdm.tqdm(
                total=int(total_length), unit_scale=True, desc="downloading"
            ) as bar:
                for data in response.iter_content(chunk_size=4096):
                    bar.update(len(data))
                    f.write(data)


def get_articles_json(lang="en", which="wikinews", force=False):
    source_path = os.path.join(news_dir(), f"{lang}.json.gz")
    if not os.path.isfile(source_path) or force:
        download_articles(lang=lang, which=which)
    return source_path

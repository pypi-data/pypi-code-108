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


def get_available():
    cwd, listing = htmllistparse.fetch_listing(url, timeout=30)
    return {
        l.name[0:2]: l.name
        for l in listing
        if "wikinews" in l.name and "content" in l.name
    }


def download_news(lang="en"):
    news_path = os.path.join(news_dir(), f"{lang}.json.gz")
    available = get_available()
    if lang not in available:
        raise ValueError("No news for language '%s'" % lang)

    with open(news_path, "wb") as f:
        response = requests.get(url + available[lang], stream=True)
        total_length = response.headers.get("content-length")

        if total_length is None:  # no content length header
            f.write(response.content)
        else:
            dl = 0
            with tqdm.tqdm(total=int(total_length), desc="downloading") as bar:
                for data in response.iter_content(chunk_size=4096):
                    bar.update(len(data))
                    f.write(data)


def get_news_json(lang="en", force=False):
    news_path = os.path.join(news_dir(), f"{lang}.json.gz")
    if not os.path.isfile(news_path) or force:
        download_news(lang)
    return news_path

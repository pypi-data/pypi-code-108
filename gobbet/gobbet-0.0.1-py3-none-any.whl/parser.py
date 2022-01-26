import orjson
import mwparserfromhell as mwp
import tqdm
from nltk.tokenize import wordpunct_tokenize
import gzip
from gobbet import Wordlist
import struct


def parse_dump(filename):
    def getuncompressedsize(filename):
        with open(filename, "rb") as f:
            f.seek(-4, 2)
            return struct.unpack("I", f.read(4))[0]

    f = gzip.open(filename)
    articles = []
    headlines = []
    paragraphs = []
    threshold = 2

    words = Wordlist()
    # This ain't real json.
    with tqdm.tqdm(
        total=getuncompressedsize(filename), unit_scale=True, desc="parsing"
    ) as bar:
        for line in f:
            bar.update(len(line))
            article = orjson.loads(line)
            if "index" in article:
                continue
            # Just store text here
            text = article["text"]
            this_words = filter(lambda x: len(x) > 2, wordpunct_tokenize(text))
            words.update(this_words)

            if article["namespace"] != 0:
                continue
            headlines.append(article["title"])
            plain_text = mwp.parse(article["source_text"]).strip_code()
            for para in plain_text.split("\n\n"):
                if not para.startswith("Category:"):
                    paragraphs.append(para)

    return {
        "paragraphs": paragraphs,
        "headlines": headlines,
        "words": words,
    }

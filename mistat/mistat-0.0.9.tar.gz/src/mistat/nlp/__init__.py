import gzip
from pathlib import Path

DEMO_FILE_DIR = Path(__file__).parent


def _readFile(filename):
    with gzip.open(filename) as f:
        return f.read()


def globalWarmingBlogs():
    articles = {
        'blog-1': _readFile(DEMO_FILE_DIR / 'global-warming-blog-1.txt.gz'),
        'blog-2': _readFile(DEMO_FILE_DIR / 'global-warming-blog-2.txt.gz'),
    }


def covid19Blogs():
    return {
        'article-1': _readFile(DEMO_FILE_DIR / 'covid-19-article-1.txt.gz'),
        'article-2': _readFile(DEMO_FILE_DIR / 'covid-19-article-2.txt.gz'),
        'blog-1': _readFile(DEMO_FILE_DIR / 'covid-19-blog-1.txt.gz'),
        'blog-2': _readFile(DEMO_FILE_DIR / 'covid-19-blog-2.txt.gz'),
        'blog-3': _readFile(DEMO_FILE_DIR / 'covid-19-blog-3.txt.gz'),
    }

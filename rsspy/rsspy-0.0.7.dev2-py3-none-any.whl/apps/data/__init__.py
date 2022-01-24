from rss.apps.meituan import MeiTuan
from rss.apps.openai import OpenAI
from rss.apps.tensorflow import TensorFlowBlog

BLOG_SOURCES = {
    'tensorflow': {
        'host':
        'https://blog.tensorflow.org/search?updated-max=2022-06-02T12:00:00-07:00&max-results=200&start=20&by-date=false',
        'url': 'https://blog.tensorflow.org',
        'parser': TensorFlowBlog
    },
    'openai': {
        'host': 'https://openai.com/blog/',
        'url': 'https://openai.com/blog/',
        'parser': OpenAI
    },
    'meituan': {
        'host': 'https://tech.meituan.com/',
        'url': 'https://tech.meituan.com/',
        'parser': MeiTuan
    }
}

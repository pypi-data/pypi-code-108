from pathlib import Path

DEMO_FILE_DIR = Path(__file__).parent

def globalWarmingBlogs():
    return {
        'blog-1': (DEMO_FILE_DIR / 'global warming blog 1.txt').read_text(),
        'blog-2': (DEMO_FILE_DIR / 'global warming blog 2.txt').read_text(),
    }

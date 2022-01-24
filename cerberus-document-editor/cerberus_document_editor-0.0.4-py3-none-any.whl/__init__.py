import sys
try:
    from .editor import MainWindow
    from .user_page import EditorPage
except Exception as e:
    print(e, file=sys.stderr)
    ...
__version__ = '0.0.4'
import os
import webbrowser

def launchDocs():
    ROOT_DIR = (os.path.dirname(os.path.abspath(__file__)))
    url = os.path.join(ROOT_DIR, 'docs/index.html')
    url = 'file://' + url
    new = 2  # open in a new tab, if possible
    webbrowser.open(url, new=new)

######################################################
if __name__ == '__main__':
    launchDocs()
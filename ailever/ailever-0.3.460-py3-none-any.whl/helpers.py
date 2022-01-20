from .logging_system import logger

def helper(what):
    if what == "ailever":
        logger['ailever'].info(ailever)
    elif what == "server":
        logger['ailever'].info(server)
    elif what == "graph":
        logger['ailever'].info(graph)
    elif what == "frame":
        logger['ailever'].info(frame)

server = """
jupyter lab &
python -m visdom.server &
rstudio-server start
service postgresql start"""

graph = """
# Matplotlib Cache
import matplotlib as mpl
mpl.get_cachedir()

# Korean Font D/U
- Download1 : sudo apt-get install -y fonts-nanum fonts-nanum-coding fonts-nanum-extra
- Downlaod2 : https://hangeul.naver.com/font
- Upload : site-packages/matplotlib/mpl-data/fonts/ttf
- Check : head ~/.cache/matplotlib/fontList.json

# Korean Font Setup
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = 'NanumBarunGothic'"""

frame = """
# Frame Display Option
import pandas as pd
pd.set_option('display.max_row', 500)
pd.set_option('display.max_columns', 100)"""

ailever = """
- https://github.com/ailever/ailever
- https://github.com/ailever/dataset
- https://github.com/ailever/analysis
- https://github.com/ailever/forecast
- https://github.com/ailever/investment"""

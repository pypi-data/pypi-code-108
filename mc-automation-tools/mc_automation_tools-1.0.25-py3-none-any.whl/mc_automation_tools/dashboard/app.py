"""
This is mc-automation-board
"""
import json
from typing import List, Tuple
import streamlit as st
from mc_automation_tools import common
import os
CONF_FILE='/home/ronenk1/dev/automation-kit/configuration.json'

# read base configuration file
# CONF_FILE = common.get_environment_variable('CONF_FILE', None)
if not CONF_FILE:
    raise EnvironmentError('Should provide path for CONF_FILE')

with open(CONF_FILE, 'r') as fp:
    conf = json.load(fp)

from PIL import Image
image = Image.open('mapcolonies_logo.png')
st.image(image, width=None)

# path = os.path.dirname(__file__)
# my_file = path+'/mapcolonies_logo.png'
def main():
    """
    init main web page
    """
    load_homepage()


def load_homepage() -> None:
    """ The homepage is loaded using a combination of .write and .markdown.
    Due to some issues with emojis incorrectly loading in markdown st.write was
    used in some cases.

    When this issue is resolved, markdown will be used instead.

    """
    path = os.path.dirname(__file__)
    my_file = path + '.mapcolonies_logo.png'
    st.image(my_file,
             use_column_width=True)
    st.markdown("> A Dashboard for the Board Game Geeks among us")
    st.write("As many Board Game Geeks like myself track the scores of board game matches "
             "I decided to create an application allowing for the exploration of this data. "
             "Moreover, it felt like a nice opportunity to see how much information can be "
             "extracted from relatively simple data.")
    st.write("As a Data Scientist and self-proclaimed Board Game Nerd I obviously made sure to "
             "write down the results of every board game I played. The data in the application "
             "is currently my own, but will be extended to include those of others.")
    st.markdown("<div align='center'><br>"
                "<img src='https://img.shields.io/badge/MADE%20WITH-PYTHON%20-red?style=for-the-badge'"
                "alt='API stability' height='25'/>"
                "<img src='https://img.shields.io/badge/SERVED%20WITH-Heroku-blue?style=for-the-badge'"
                "alt='API stability' height='25'/>"
                "<img src='https://img.shields.io/badge/DASHBOARDING%20WITH-Streamlit-green?style=for-the-badge'"
                "alt='API stability' height='25'/></div>", unsafe_allow_html=True)
    for i in range(3):
        st.write(" ")
    st.header("🎲 The Application")
    st.write("This application is a Streamlit dashboard hosted on Heroku that can be used to explore "
             "the results from board game matches that I tracked over the last year.")
    st.write("There are currently four pages available in the application:")
    st.subheader("♟ General Statistics ♟")
    st.markdown("* This gives a general overview of the data including frequency of games over time, "
                "most games played in a day, and longest break between games.")
    st.subheader("♟ Player Statistics ♟")
    st.markdown("* As you play with other people it would be interesting to see how they performed. "
                "This page allows you to see, per player, an overview of their performance across games.")
    st.markdown("* This also includes a one-sample Wilcoxon signed-rank test to test if a player performs "
                "significantly better/worse than the average for one board game.")
    st.subheader("♟ Head to Head ♟")
    st.markdown("* I typically play two-player games with my wife and thought it would be nice to include a "
                "head to head page. This page describes who is the better of two players between and within games.")
    st.subheader("♟ Explore Games ♟")
    st.markdown("* This page serves to show statistics per game, like its distribution of scores, frequency of "
                "matches and best/worst players.")


if __name__ == "__main__":
    main()

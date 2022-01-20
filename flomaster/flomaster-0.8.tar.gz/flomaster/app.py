import os
import pandas as pd
import streamlit as st
import plotly.express as px

# from traitlets.traitlets import default

from col_type_detector import *
from plots import *
from helpers import *
# from colorthief import ColorThief

from PIL import Image

st.set_option('deprecation.showPyplotGlobalUse', False)

DEFAULT_FILE = 'Iris.csv'

ONE_NUMERIC = ['Histogram', 'Distplot']
ONE_CATEOGIRCAL = ['Donut', 'Pie', 'Histogram']
TWO_NUMERIC = ["Scatter", "Scatter plot with margins", "2D density plot", \
               "Distplot", "Histogram", "Basic Stats"]
TWO_NUMERIC_SORTED = ['Connected Scatter', "Area plot", "Line plot"]

ONE_CATEOGIRCAL_ONE_NUMERICAL = ['Box', "Violin", "Basic Stats"]

TWO_CATEGORICAL = ['Cross tab', "Stacked bar"]
ONE_DATETIME_ONE_NUMERIC = ['Connected Scatter']


# url_logo = st.sidebar.text_input('select your logo or provide a url', "")
# if url_logo:
#     color_pallete = get_color(url_logo, 2)
try:
    image = Image.open('logo.jpg')

    st.image(image)
except Exception as e:
    print (f"could load image {e}")

url = st.sidebar.text_input('Input url to the .csv file', "None")
uploaded_file = st.sidebar.file_uploader("Choose a file")

if url != "None" and len(url) > 3:
    data_path = url 
elif uploaded_file:
    data_path = uploaded_file
else:
    data_path = os.path.join('data_samples',DEFAULT_FILE)
    
df = pd.read_csv(data_path)

data_types = get_column_types(df, num_unique_categories=2)


st.markdown("## Data Preview")
st.write(df.head(100))

x = st.sidebar.selectbox('Select x axis', ["None"] + list(df.columns))
y = st.sidebar.multiselect("Select columns to use as y axis", ['None'] + list(df.columns))
group_by = st.sidebar.selectbox("Select column representing group", ['None'] + list(df.columns))

if group_by == "None":
    group_by = None

if y == []:
    y = ["None"]

x_dtype = get_data_type_for_given_feature(data_types, x)
st.write(f"{x} dtype is {x_dtype}")
y_dtype = get_data_type_for_given_feature(data_types, y[0])
st.write(f"{y[0]} dtype is {y_dtype}")

# adding labels and axis names
x_axis = st.sidebar.text_input("Please input x axis name", x)
y_axis = st.sidebar.text_input("Please input y axis name", y[0])

if y_axis == "None":
    y_axis = ""

title = st.sidebar.text_input("Please input title name", f"{x_axis} vs {y_axis}")


# one feature
if x != "None" and y[0] == 'None':
    if x_dtype == 'numeric':
        plot_type = st.selectbox('Select type of the plot', ONE_NUMERIC)
        fig = one_numeric(df, x, group_by, plot_type)
        add_labels_to_fig(fig, x_axis, y_axis, title)
        st.plotly_chart(fig)

    if x_dtype == 'categorical':
        plot_type = st.selectbox('Select type of the plot', ONE_CATEOGIRCAL)
        fig = one_categoric(df, x, group_by, plot_type)
        add_labels_to_fig(fig, x_axis, y_axis, title)        
        st.plotly_chart(fig)

    if x_dtype == 'texts':
        fig = one_textual(df, x)
        st.pyplot(fig)

# two features
if x != "None" and y[0] != 'None':
    # two numeric
    if x_dtype == "numeric" and y_dtype == 'numeric':
        if df[x].to_list() == sorted(df[x].to_list()):
            TWO_NUMERIC += TWO_NUMERIC_SORTED
        
        plot_type = st.selectbox('Select type of the plot', TWO_NUMERIC)
        if len(df)>2000 and plot_type in ["Histogram", "Scatter"]:
            st.markdown('**Data has two many rows, we suggest plotting \
                with one on the folowing: "Scatter plot with margins", "2D density plot", "Distplot"**')
        
        if len(df)<2000 and plot_type not in ["Histogram", "Scatter"]:
            st.markdown('**Data has two little rows, we suggest plotting \
                with one on the folowing: "Histogram", "Scatter"**')

                

        fig = two_numeric(df, x, y[0], group_by, plot_type)
        add_labels_to_fig(fig, x_axis, y_axis, title)        
        st.plotly_chart(fig)
    # /////////////////////////////////////////////////////////

    #one numeric one categoric
    if x_dtype == "categorical" and y_dtype == 'numeric':
        plot_type = st.selectbox('Select type of the plot', ONE_CATEOGIRCAL_ONE_NUMERICAL)

        fig = one_numeric_one_categorical(df, x, y, group_by, plot_type)
        add_labels_to_fig(fig, x_axis, y_axis, title)        

        st.plotly_chart(fig)

    # two categoricals
    if x_dtype == "categorical" and y_dtype == 'categorical':
        plot_type = st.selectbox('Select type of the plot', TWO_CATEGORICAL)
        if plot_type == 'Cross tab':
            df_cross = two_categorical(df, x, y[0], plot_type)
            st.write(df_cross)
        if plot_type == "Stacked bar":
            fig = two_categorical(df, x, y[0], plot_type)
            add_labels_to_fig(fig, x_axis, y_axis, title)            
            st.plotly_chart(fig)

    # one datetime one numeric
    if x_dtype == "datetime" and y_dtype == 'numeric':

        if check_list_in_list(list(df.columns), ['Date', "Open", "High", "Low", "Close"]):
            ONE_DATETIME_ONE_NUMERIC += ["Stock price"]
        plot_type = st.selectbox('Select type of the plot', ONE_DATETIME_ONE_NUMERIC)
        fig = one_datetime_one_numeric(df, x, y, group_by,plot_type)
        add_labels_to_fig(fig, x_axis, y_axis, title)        
        st.plotly_chart(fig)

    
from typing import Any
import pandas as pd
import numpy as np
import webcolors
import matplotlib as mpl
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show

def filtering(frame:pd.DataFrame, low_abundace:bool=False):
    #Remove singletons
    frame = frame.loc[(frame!=0).sum(axis=1)>=2,:]
    
    #Remove low abudance < 5
    if low_abundace == True:
        frame = frame.loc[frame.sum(axis=1)>5,:]
    else: 
        pass

    indx = list(frame.index)

    return indx,frame

def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

def get_colour_name(requested_colour):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
    return closest_name

def filter_otus(frame:pd.DataFrame, taxa=False, low_abundance=False):
    if taxa:
        X=frame.iloc[:,2:].copy()
        X=X.astype('float').copy()
        indx, X = filtering(X, low_abundance)
        
        Text = frame.iloc[indx,:2].copy()
        
        Taxa =  frame.iloc[indx,1].str.split(';').str.get(0)+'-'+\
                frame.iloc[indx,1].str.split(';').str.get(1)+'-'+\
                frame.iloc[indx,1].str.split(';').str.get(5)
    else:
        X = frame.iloc[:,1:].copy()
        indx, X = filtering(X,low_abundance)
        Text = frame.iloc[indx,:1].copy()
        X=X.astype('float').copy()
        
    return X, Taxa, Text

def plot_umap(embedding_, l, Text, Taxa=None):
    #Dimensions 
    x = embedding_[:, 0]
    y = embedding_[:, 1]
    z = np.sqrt(1 + np.sum(embedding_**2, axis=1))


    #Projections
    disk_x = x / (1 + z)
    disk_y = y / (1 + z)

    #Colors
    colors = ["#%02x%02x%02x" % (int(r), int(g), int(b)) \
    for r, g, b, _ in 255*mpl.cm.viridis(mpl.colors.Normalize()(l))]
            
    colors2  = [(int(r), int(g), int(b)) \
    for r, g, b, _ in 255*mpl.cm.viridis(mpl.colors.Normalize()(l))]

    tempd = dict(zip(l, colors2))

    TOOLS="hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,save,box_select,poly_select,lasso_select,"
            
    if Taxa==None:
        dataE=dict(x=disk_x.tolist(),y=disk_y.tolist(),Color=colors,Name=Text.iloc[:,0].tolist())
        TOOLTIPS=[("Name", "@Name")]
    else:
        dataE=dict(x=disk_x.tolist(),y=disk_y.tolist(),Color=colors,Name=Text.iloc[:,0].tolist(),Taxa=Taxa.tolist())
        TOOLTIPS=[("Name", "@Name"),("Taxa","@Taxa")]
        
    S=ColumnDataSource(dataE)

    p = figure(title="Embedding", x_axis_label='x',y_axis_label='y', output_backend = "svg",
                x_range=[-1,1],y_range=[-1,1],width=800, height=800,tools=TOOLS,tooltips=TOOLTIPS)

    p.circle(x=0.0,y=0.0,fill_alpha=0.1,line_color='black',size=20,radius=1,fill_color=None,line_width=2,muted=False)
    p.scatter(x='x',y='y',fill_color='Color', fill_alpha=0.3,line_color='black',radius=0.03,source=S)
    p.hover.point_policy="none"
    show(p)


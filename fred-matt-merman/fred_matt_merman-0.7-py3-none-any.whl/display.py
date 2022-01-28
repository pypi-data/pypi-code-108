from matplotlib import pyplot as plt
from . import database

#costante usata per selezionare il numero di valori da graficare.
#è importante che sia negativa! In quanto sono graficati gli ultimi dati
#è usato anche nel calcolo della varinza tra serie, nel case study
NUMBER_VALUE = -50
DB = "./database.db"

grid_color = "grey"
label_color = "white"
plot_color="green"
title_fontsize = 30
axes_fontsize = 20
text_pad = 20
context = {'axes.edgecolor':'grey',
           'axes.facecolor':'black',
           'font.family':'sans-serif', 
           'figure.facecolor':'black', 
           'figure.edgecolor':'black',
           'xtick.color':'white', 
           'ytick.color':'white', 
           'savefig.transparent':'True'}

def convert_string_float(array_string):
    
    array_float = []
    
    for values in array_string:
    
        if values == ".": values = 0
    
        array_float.append(float(values))
    
    return array_float

def display(x, y, title, id, x_label):

    with plt.rc_context(context):
  
        plt.figure(figsize=(21,9))
        
        plt.title(title, color=label_color, pad=text_pad, fontsize=title_fontsize)
        plt.grid(color=grid_color)
        
        if y is not None: plt.plot(x[NUMBER_VALUE:], y[NUMBER_VALUE:], color="green", label="ID: " + id)
        else: plt.plot(x[NUMBER_VALUE:], color="green", label="ID: " + id)
            
        plt.ylabel("value", color=label_color, fontsize=axes_fontsize, labelpad=text_pad)
        plt.xlabel(x_label, color=label_color, fontsize=axes_fontsize, labelpad=text_pad)
        plt.xticks(rotation=45)
        
        #mp.savefig('chart_observation.png')
        
        legend = plt.legend(fontsize=text_pad)
        plt.setp(legend.get_texts(), color=label_color)

        return plt
    
def display_observation(id):
    
    pd = database.get_db(DB, "observations", id)
    x = pd['date'].tolist()
    y = pd['value'].tolist()
    y = convert_string_float(y)    
    
    return display(x, y, "Observation", id, "date")
        
def moving_average(input_array, day):
    
    list = convert_string_float(input_array)
    
    ret = []
    window = 0
    
    for i in range(day):
        window += list[i]
        
    for i in range(day, len(list)):
        ret.append(window / day)
        window = window + list[i] - list[i-day]
    
    return ret
    
def display_moving_average(id, day):
    
    pd = database.get_db(DB, "observations", id)
    x = pd['value'].tolist()    
    ma = moving_average(x, day)
    
    return display(ma, None, "Moving Average", id, "day")
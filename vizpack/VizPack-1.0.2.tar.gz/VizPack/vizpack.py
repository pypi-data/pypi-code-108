import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np




class Viz_Func:

  def __init__(self):
      '''
       Contains Methods for plotting visualizations from Pandas DataFrame
       - label_plot : Labelling a plot
       - plot_bar : Plotting a Bar Chart
       - plot_donut : Making a Donut Plot
       - annot_bar : Annotating a Barplot
      '''
      liner = '\n\n'
      spacer = "=========="
      sns.set_theme()

      print(liner, spacer, 'Welcome to the Visualization Tool kit', spacer, liner)
  
  
  def label_plot(self, title = 'Distribution Plot', x = 'X-axis', y = 'Y-axis'):
      '''
      Parameters:
        title : str
                Default - 'Distribution Plot'
        
        x : X-axis label (str)
                Default - 'X-axis'
                
        y : Y-axis label (str)
                Default - 'Y-axis'  
      '''
      
      plt.title(title, weight = 'bold', fontsize = 17)
      plt.ylabel(y, weight = 'bold', fontsize = 15)
      plt.xlabel(x, weight = 'bold', fontsize = 15)
      
  
      
  
  
  
  def plot_bar(self, dataset, limit = None, column = None, horizontal = False, figsize = (20,10), color = 'darkcyan'):
      '''
      Parameters:
        dataset : Pandas DataFrame, Pandas Series

        limit : Limit of Variables to Plot
                Useful in large datasets (None, int)
                Default - None
        
        column  : Dataset Column (None, str)
                  Default - None
        
        horizontal  : Should it be an Horizontal Plot (boolean)
                  Default - False
        
        figsize  : Figure Dimension (Tuple)
                  Default - (20,10)
        
        color  : Color of the bar (str)
                  Default - 'Darkcyan'
      '''
      
      if column == None: 
          DataHist = dataset.value_counts()
          if horizontal: 
              plt.gca().invert_yaxis()
              
              if limit == None: return DataHist.plot.barh(figsize = figsize, color = color)
              else: return DataHist[:limit].plot.barh(figsize = figsize, color = color)

              
          else:
              if limit == None:  return DataHist.plot.bar(figsize = figsize, color = color)
              else: return DataHist[:limit].plot.bar(figsize = figsize, color = color)
      else:
          DataHist = dataset[column].value_counts()
          if horizontal: 
              plt.gca().invert_yaxis()
              
              if limit == None: return DataHist.plot.barh(figsize = figsize, color = color)
              else: return DataHist[:limit].plot.barh(figsize = figsize, color = color)
              
              
          else: 
              if limit == None:  return DataHist.plot.bar(figsize = figsize, color = color)
              else: return DataHist[:limit].plot.bar(figsize = figsize, color = color)
              
  
          
  
          
  
  
  
  
  def plot_donut(self, dataset, limit = None, column = None, title = 'Donut Plot', figsize = (20,10), shadow = False, colors = False, explode = False, background = 'white'):
      
      '''
      Parameters:
        dataset : Pandas DataFrame, Pandas Series
        
        limit : Limit of Variables to Plot
                Useful in large datasets (None, int)
                Default - None

        column  : Dataset Column (None, str)
                  Default - None
        
        title : str
                Default - 'Donut Plot'
        
        figsize  : Figure Dimension (Tuple)
                  Default - (20,10)
        
        shadow  : Presence of Shadow (Boolean)
                  Default - False
        
        colors  : Colors of the bar (boolean, list)
                  Default - False
        
        explode  : Presence of Explosion (Boolean)
                  Default - False
        
        background  : Color of the background (str)
                  Default - 'white'
      '''
      
      
      plt.figure(figsize = figsize)
      
      if column == None: 
        data = dataset.value_counts()
        if limit: data = data[:limit]
            
      else: 
        data = dataset[column].value_counts()
        if limit: data = data[:limit]
      labs = data.values
      
      
      plt.title(title, weight = 'bold', fontsize = 30)
      
      
      
      if not colors: colors = ['darkcyan', 'green', 'darkorange', 'black', 'darkred', 'darkmagenta', 'gold']
      if not explode: 
          try: explode = [0.04] + (list(np.linspace(0.05,0.1, len(labs) - 2))[::-1]) + [0]
          except: explode = [0] * len(labs)
                  
              
      data.plot.pie(
          label = '',
          colors = colors,
          shadow = shadow,
          explode = explode,
          autopct = lambda x: f'{round(x, 2)}%')
      
      circle = plt.Circle( (0,0), 0.8, color = background)
      plt.gcf().gca().add_artist(circle)
      
  
      
  
      
  
  
  
  
  
  
  
  
  def annot_bar(self, plots, horizontal = False):
      '''
      Parameters:
        plots : Barplot plots
                i.e. plots = sns.barplot(x, y)
      '''
      
      if plots == None: return None
      if horizontal == True:
          for rect in plots.patches:
              width = rect.get_width()
              plt.text(
                  (1.025 * rect.get_width()), (rect.get_y() + (0.49 * rect.get_height())),
                  '%d' % int(width),
                  ha='center', va='center')
          plt.gca().invert_yaxis()
      else: 
          for bar in plots.patches:
              plots.annotate(format(bar.get_height(), '.0f'),
                   (bar.get_x() + bar.get_width() / 2,
                    bar.get_height()), ha='center', va='center',
                    size=15, xytext=(0, 8),
                    textcoords='offset points')
      
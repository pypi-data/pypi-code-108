import math
import numpy as np
import pandas as pd 
import seaborn as sns
import matplotlib.pyplot as plt 

class Check():
    """ Check class for quick insights from the data
    Attributes:
          df (pandas dataframe) representing the variable holding the table in question      
    """
    def __init__(self,df):

        self.data = df
   
        
    def show_preview(self):
        
        print("Number of columns: ", self.data.shape[1])
        print("Number of rows: ", self.data.shape[0])
        print('\n')
        print('Nulls proportions: ')
        for i,z in zip(self.data.columns,list(self.data.isnull().sum())):
            if (z/self.data.shape[0]) != 0: 
                print(" "*4,i,": ",round(z/self.data.shape[0],4))
        print('\n')
        print('Numerical columns: ')
        print(" ",list(self.data.select_dtypes(include= ['int','float','int64','float64']).columns))
        print('\n')
        print('Categorical columns: ')
        print(" ",list(self.data.select_dtypes(include= ['object']).columns))
        print('\n')
        print('Correlation Heatmap: ')
        sns.heatmap(self.data.corr(),xticklabels=False,square=True, cbar = False, annot_kws = {'fontsize':12, 'fontweight': 'bold'},cmap = 'viridis_r', annot = True, fmt = '.2f');
        plt.show()
        return self.data.head(5)

    
        
            
        

          

'''
Class to process UMAP and HDBSCAN together
@dlegor

'''
from pandas.core.base import DataError
import pandas as pd 
import numpy as np 
import umap
import hdbscan
import matplotlib as mpl
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show

class Embedding_Output:
    '''
    Class to estimate the embedding 
    and detect the outliers from the embedding
    '''

    def __init__(self,n_neighbors:int=15,min_dist:float=0.1,
    n_components:int=2,metric_umap:str='euclidean',metric_hdb:str='euclidean',
    min_cluster_size:int=15,min_sample:int=5,get_embedding:bool=True,get_outliers:bool=True,quantile_limit:float=0.9,
    output:bool=False):
        
        self.n_neighbors=n_neighbors
        self.min_dist=min_dist
        self.n_components=n_components
        self.metric_umap = metric_umap
        self.metric_hdb=metric_hdb
        self.min_cluster_size=min_cluster_size
        self.min_sample=min_sample
        self.get_embedding=get_embedding
        self.get_outliers=get_outliers
        self.quantile_limit=quantile_limit
        self.output=output
        # self.file_output=file_output

        

    def _validation_data(self,X):

        if all(X.select_dtypes('float').dtypes==float):
            pass
        else:
            raise DataError

    def fit(self,X):

        self._validation_data(X)
        
        #UMAP
        hyperbolic_mapper = umap.UMAP(output_metric='hyperboloid',
        metric=self.metric_umap,n_neighbors=self.n_neighbors,
        min_dist=self.min_dist,n_components=self.n_components,
        random_state=42).fit(X)

        self._shape_embedding=hyperbolic_mapper.embedding_.shape
  
        #HDBSCAN
        clusterer = hdbscan.HDBSCAN(min_samples=self.min_sample,
        min_cluster_size=self.min_cluster_size,
        metric=self.metric_hdb).fit(hyperbolic_mapper.embedding_)
        
        #Outliers
        threshold = pd.Series(clusterer.outlier_scores_).quantile(self.quantile_limit)
        outliers = np.where(clusterer.outlier_scores_ > threshold)[0]
        
        if self.output:
            return hyperbolic_mapper.embedding_,X.index.isin(outliers).astype(int),clusterer.labels_


    def __repr__(self) -> str:
        print('Embedding_Outliers')

def plot_umap(embedding_, l, Text, Taxa=[0]):
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
            
    if len(Taxa)<1:
        dataE=dict(x=disk_x.tolist(),y=disk_y.tolist(),Color=colors,Name=Text.iloc[:,0].tolist())
        TOOLTIPS=[("Name", "@Name")]
    else:
        dataE=dict(x=disk_x.tolist(),y=disk_y.tolist(),Color=colors,Name=Text.iloc[:,0].tolist(),Taxa=Taxa.tolist())
        TOOLTIPS=[("Name", "@Name"),("Taxa","@Taxa")]
        
    S=ColumnDataSource(dataE)

    p = figure(title="Embedding", x_axis_label='x',y_axis_label='y', output_backend = "svg", x_range=[-1,1],y_range=[-1,1],width=800, height=800,tools=TOOLS,tooltips=TOOLTIPS)

    p.circle(x=0.0,y=0.0,fill_alpha=0.1,line_color='black',size=20,radius=1,fill_color=None,line_width=2,muted=False)
    p.scatter(x='x',y='y',fill_color='Color', fill_alpha=0.3,line_color='black',radius=0.03,source=S)
    p.hover.point_policy="none"
    show(p)
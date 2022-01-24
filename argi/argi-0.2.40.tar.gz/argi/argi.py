
import pandas as pd
from adtk.data import validate_series
from adtk.detector import PersistAD
import numpy as np
from datetime import datetime, timedelta
from tslearn.clustering import KShape, TimeSeriesKMeans, KernelKMeans
from tslearn.datasets import CachedDatasets
from tslearn.preprocessing import TimeSeriesScalerMeanVariance
import numpy
import matplotlib.pyplot as plt
import networkx as nx
persist_ad = PersistAD(c=3.0, side='positive')
from sklearn import preprocessing



class argi:

  G = nx.MultiGraph()
  debug = False
  my_array = []
  y_pred = []
  ks = ''
  agregados = pd.DataFrame()
  columnas = {'src': 'IPsrc',
              'dst': 'IPdst',
              'value': '# bytes',
              'label': 'label',
              'timestamp': 'fecha'}
  num_cluster = 5

  def set_debug(self,value=True):
    self.debug= value

  def set_num_cluster(self, num_cluster):
    self.num_cluster= num_cluster

  def set_columns(self, values):
    self.columnas = values

  def df_transform(self, datos, freq='S'):
    
    datos[self.columnas['timestamp']] =  pd.to_datetime(datos[self.columnas['timestamp']])
    datos = datos.set_index(self.columnas['timestamp'])
    le = preprocessing.LabelEncoder()
    le.fit(datos[self.columnas['label']])
    datos[self.columnas['label']]= le.transform(datos[self.columnas['label']])
    entrada = datos.groupby([pd.Grouper(freq='S'), self.columnas['src'], self.columnas['dst']])[[self.columnas['value'],self.columnas['label']]].sum().reset_index()
    entrada[self.columnas['timestamp']] =  pd.to_datetime(entrada[self.columnas['timestamp']], unit='s')
    entrada = entrada.set_index(self.columnas['timestamp'])
    self.agregados = datos.groupby([pd.Grouper(freq=freq), self.columnas['src'],self.columnas['dst']]).agg({self.columnas['value']: 'sum', self.columnas['label']: 'max'}).reset_index()
    return(self.agregados)

  def graph_clear(self):
    self.G.clear

  def graph_get(self):
    return(self.G)
  
  def graph_set(self,G_temp):
    self.G = G_temp


  def graph_create(self,datos):

    self.G = nx.MultiGraph()
    datos2 = datos.groupby([self.columnas['src'],self.columnas['dst']])[[self.columnas['value'],self.columnas['label']]]
    nodes1 = datos[self.columnas['src']].unique().tolist()
    nodes2 = datos[self.columnas['dst']].unique().tolist()
    nodes = set(nodes1 + nodes2)
    self.G.add_nodes_from(nodes)

    for (src,dst), df_group in datos2:
      self.G.add_edge(src, dst, ts_len=len(df_group), ts= df_group, label=max(df_group[self.columnas['label']]) )


  def count_anomalies(self,start, stop, freq, sensibility= 3.0) :
    ts_clustering =[]
    idx = pd.date_range(start, stop, freq=freq)
    idx = idx.tz_localize(None)

    persist_ad = PersistAD(c=sensibility, side='positive')

    for node1, node2, data in self.G.edges(data=True):
      # timeseries = data['ts']
      salida = data['ts']
      if len(salida) > 1:
        salida[self.columnas['timestamp']] =  pd.to_datetime(salida[self.columnas['timestamp']])
        # salida= salida.set_index(self.columnas['timestamp'],drop=False)
        salida= salida.set_index(self.columnas['timestamp'])
        
        salida = salida.resample(freq).sum()
        salida = salida.tz_localize(None)

        salida=salida.reindex(idx, fill_value='0')

        s = validate_series(salida[self.columnas['value']])
        ts_clustering.append(salida[self.columnas['value']].array)
        anomalies = persist_ad.fit_detect(s)
        total_anomalies = anomalies.tolist().count(1)

        #print( src + ' '+ dst, end='')
        self.G[node1][node2][0]['anomalies'] =  total_anomalies # , anomalies = total_anomalies)
    if self.debug: 
      print(salida)

  def create_clustering(self,start,stop, freq, method = 'KShape'):
    ts_clustering = []


    #for node1, node2, data in G2.edges(data=True):
    attr = nx.get_edge_attributes(self.G, "ts")

    try:
      idx = pd.date_range(start, stop, freq=freq).round(freq)
      idx = idx.tz_localize(None)
    except:
      idx = pd.date_range(start, stop, freq=freq)
      idx = idx.tz_localize(None)

    for ((src,dst,index), values) in attr.items():
        # values[[self.columnas['timestamp'],self.columnas['value']]]
        values[self.columnas['timestamp']] =  pd.to_datetime(values[self.columnas['timestamp']])
        values = values.set_index(self.columnas['timestamp']).resample(freq).sum()
        values = values.tz_localize(None)
        values = values.reindex(idx, fill_value=0)
        ts_clustering.append(values[self.columnas['value']].tolist())

    if self.debug:
      print(ts_clustering)
    my_array = np.array(ts_clustering)

    

    my_array=my_array.reshape((my_array.shape[0],my_array.shape[1],1))
    my_array.shape
    self.my_array = my_array
    seed = 0
    numpy.random.seed(seed)

    # kShape clustering
    if (method == 'KShape'):
      ks = KShape(n_clusters=self.num_cluster, verbose=True, random_state=seed)
    elif (method == 'KernelKMeans'):
      ks = KernelKMeans(n_clusters=self.num_cluster, kernel="gak", kernel_params={"sigma": "auto"}, n_init=20, verbose=True, random_state=seed)
    else:
      ks = TimeSeriesKMeans(n_clusters=self.num_cluster, verbose=True, random_state=seed)
    y_pred = ks.fit_predict(my_array)
    contador = 0
    for (key, values) in attr.items():
      ts_clustering.append(values[self.columnas['value']])

      attrs = {}
      attrs[key] = {}
      attrs[key]['cluster'] = y_pred[contador]
      nx.set_edge_attributes(self.G, attrs)
      contador = contador +1
    my_array = []
    self.y_pred = y_pred
    self.ks = ks
    ts_clustering = []


  def create_visibility(self,start,stop, freq):
    from ts2vg import NaturalVG, HorizontalVG

    ts_clustering = []


    #for node1, node2, data in G2.edges(data=True):
    attr = nx.get_edge_attributes(self.G, "ts")
    
    try:
      idx = pd.date_range(start, stop, freq=freq).round(freq)
      idx = idx.tz_localize(None)
    except:
      idx = pd.date_range(start, stop, freq=freq)
      idx = idx.tz_localize(None)

    for ((src,dst,index), values) in attr.items():
        # values[[self.columnas['timestamp'],self.columnas['value']]]
        values[self.columnas['timestamp']] =  pd.to_datetime(values[self.columnas['timestamp']])
        values = values.set_index(self.columnas['timestamp']).resample(freq).sum()
        values = values.tz_localize(None)
        values = values.reindex(idx, fill_value=0)
        ts = values[self.columnas['value']].tolist()
        g = HorizontalVG()
        g.build(ts)
        nx_g = g.as_networkx()

        attrs = {}
        attrs[(src,dst,index)] = {}
        attrs[(src,dst,index)]['density_h'] = nx.density(nx_g)
        max_grade = max(nx_g.degree, key=lambda x: x[1])[1]
        attrs[(src,dst,index)]['max_degree_h'] = max_grade

        ################# Natural VG
        gn = NaturalVG()
        gn.build(ts)
        nx_gn = gn.as_networkx()
        attrs[(src,dst,index)]['density_n'] = nx.density(nx_gn)
        max_grade_n = max(nx_gn.degree, key=lambda x: x[1])[1]
        attrs[(src,dst,index)]['max_degree_n'] = max_grade_n
        nx.set_edge_attributes(self.G, attrs)
    matrix = []
    for u,v,e in self.G.edges(data=True):
      matrix.append([str(u)+'-'+str(v), e['density_h'], e['max_degree_h'], e['density_n'], e['max_degree_n']])
    df = pd.DataFrame(matrix, columns=['edges','density_h','max_degree_h','density_n','max_degree_n'])
    from sklearn.cluster import KMeans
    X = np.array(df[['density_h','max_degree_h','density_n','max_degree_n']])

    kmeans = KMeans(init="k-means++", n_clusters=self.num_cluster, n_init=4)
    kmeans.fit(X)
    labels = kmeans.predict(X)

    contador = 0
    for (key, values) in attr.items():
      attrs = {}
      attrs[key] = {}
      attrs[key]['cluster'] = labels[contador]
      nx.set_edge_attributes(self.G, attrs)
      contador = contador + 1

  def visualization_ts(self):
    import matplotlib.pyplot as plt

    sz = self.my_array.shape[1]
    plt.figure(figsize=(14, 12))
    for yi in range(self.num_cluster):
      plt.subplot(self.num_cluster, 1, 1 + yi)
      min = 0
      max = 0
      for xx in self.my_array[self.y_pred == yi]:
        if min > xx.min():
          min = xx.min()
        if max < xx.max():
          max = xx.max()
        plt.plot(xx.ravel(), "k-", alpha=.2)
        plt.plot(self.ks.cluster_centers_[yi].ravel(), "r-")
        plt.xlim(0, sz)
        plt.ylim(min, max)
        # plt.title("Cluster %d min: %d max %d" % (yi + 1) % min % max)
        plt.title("Cluster " + str((yi + 1)) + " min: "
                      + str("{:.2e}".format(min)) + " max:" + str("{:.2e}".format(max)))

    plt.tight_layout()
    plt.show()

  def clustering_description(self,top = 5):
    for num_cluster in range(self.num_cluster):
      H = nx.Graph(((u, v, e) for u,v,e in self.G.edges(data=True) if e['cluster'] == num_cluster))
      print("Cluster: "+str(num_cluster) + " num_edges: " +str(H.number_of_edges())+ " num_nodes: "+str(H.number_of_nodes()))
      num_neighbors = []
      for node in H.nodes():
        salida= len(list(nx.all_neighbors(H, node)))
        num_neighbors.append([node,salida]) 
      df = pd.DataFrame.from_records(num_neighbors)
      print(df.sort_values(by=[1],ascending=False).head(top))

  def cluster_ts_visualization(self, lower, upper, start, stop, freq, cluster_id):
    import altair as alt

    salida_df = pd.DataFrame()
    contador = 1
    ts = []
    for u,v,e in self.G.edges(data=True):
      if e['cluster'] == cluster_id:
        ts.append(e['ts'])
    for serie in ts[lower:upper]:
      salida = serie
      salida[self.columnas['timestamp']] =  pd.to_datetime(salida[self.columnas['timestamp']])
      #salida= salida.set_index(self.columnas['timestamp'],drop=False)
      salida= salida.set_index(self.columnas['timestamp'])
      idx = pd.date_range(start,stop, freq=freq)
      idx = idx.tz_localize(None)
      salida = salida.resample(freq).sum()
      salida = salida.tz_localize(None)
      salida=salida.reindex(idx, fill_value='0')
      salida_df[str(contador)]= salida[self.columnas['value']]
      contador= contador +1
    salida_df['index'] = salida_df.index
    lista = salida_df.columns.tolist()
    lista.remove('index')

    import plotly.express as px


    fig = px.line(salida_df, x='index', y=lista[0])

    for columna in lista:
      fig.add_scatter(x=salida_df['index'], y=salida_df[columna], mode='lines', name=columna)

    fig.update_xaxes(rangeslider_visible=True)

    fig.show()

  def anomaly_ts_visualization(self, lower, upper, start, stop, freq, anomaly=True):
    import altair as alt

    salida_df = pd.DataFrame()
    contador = 1
    ts = []
    for u,v,e in self.G.edges(data=True):
      if e['anomaly'] > 0:
        ts.append(e['ts'])
    for serie in ts[lower:upper]:
      salida = serie
      salida[self.columnas['timestamp']] =  pd.to_datetime(salida[self.columnas['timestamp']])
      #salida= salida.set_index(self.columnas['timestamp'],drop=False)
      salida= salida.set_index(self.columnas['timestamp'])
      idx = pd.date_range(start,stop, freq=freq)
      idx = idx.tz_localize(None)
      salida = salida.resample(freq).sum()
      salida = salida.tz_localize(None)
      salida=salida.reindex(idx, fill_value='0')
      salida_df[str(contador)]= salida[self.columnas['value']]
      contador= contador +1
    salida_df['index'] = salida_df.index
    lista = salida_df.columns.tolist()
    lista.remove('index')

    import plotly.express as px


    fig = px.line(salida_df, x='index', y=lista[0])

    for columna in lista:
      fig.add_scatter(x=salida_df['index'], y=salida_df[columna], mode='lines', name=columna)

    fig.update_xaxes(rangeslider_visible=True)

    fig.show()



  def graph_plot(self):
    import plotly.graph_objects as go
    pos = nx.random_layout(self.G)
    nx.set_node_attributes(self.G, pos, 'pos')

    #G = nx.random_geometric_graph(200, 0.125)
    #pos=nx.spring_layout(G)
    #nx.set_node_attributes(G,pos) 

    edge_x = []
    edge_y = []
    for edge in self.G.edges():
        x0, y0 = self.G.nodes[edge[0]]['pos']
        x1, y1 = self.G.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in self.G.nodes():
        x, y = self.G.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='Blues',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(self.G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append('# of connections: '+str(len(adjacencies[1])))

    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text

    fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                width=1000,
                height=1000,
                title='<br>Network graph',
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[ dict(
                    text="Python code: <a href='https://plot.ly/ipython-notebooks/network-graphs/'> https://plot.ly/ipython-notebooks/network-graphs/</a>",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002 ) ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )
    fig.show()

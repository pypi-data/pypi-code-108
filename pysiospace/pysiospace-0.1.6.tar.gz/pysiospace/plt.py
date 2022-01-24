from seaborn import clustermap

def viz(physioscore, **kwargs):
  clustermap(physioscore, **kwargs)
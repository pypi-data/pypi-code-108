#from __future__ import annotations

import uproot
import numpy as np
import pandas as pd


def data_from_trees ( trees ,
                      branches ,
                      cut = None ,
                      max_ntrees = None ,
                      chunk_size = None ) -> pd.DataFrame:
  """Stratified data shuffling from list of `uproot.TTree`.

  The number of entries picked from each `uproot.TTree` is proportional to 
  the fraction of the total entries that that tree includes. For example, 
  if `tree_1` has 900 entries and `tree_2` has 100, requiring a `chunk_size` 
  of 100 will return 90 entries picked randomly form `tree_1` and 10 picked 
  randomly from `tree_2`. 
  
  Parameters
  ----------
  trees : `list` of `uproot.TTree`
    List of `uproot.TTree` from which to pick data.

  branches : `str` or `list` of `str`
    Column names of the trees from which to pick data.

  cut : `str`, optional
    Boolean expression to filter the trees (`None`, by default).

  max_ntrees : `int`, optional
    Maximum number of trees from which to pick data. Can be decreased
    if trees are similar to each other and accessing too often to all 
    of them affects performance (`None`, by default).

  chunk_size : `int`, optional
    Total number of data rows picked from trees (`None`, by default).
    Note: it may not correspond with the actual length of the output 
    dataframe, since the filtering is applied as final step.

  Returns
  -------
  data : `pd.DataFrame`
    Dataframe containing stratified entries picked from `trees`. The 
    column labels correspond with `branches`, and the total number of 
    rows is less than or equal to the `chunk_size` value.

  See Also
  --------
  uproot.models.TTree.arrays

  Examples
  --------
  >>> import uproot
  >>> events = uproot.open ("https://scikit-hep.org/uproot3/examples/Zmumu.root:events")
  >>> print ( events.keys() [3:11] )
  ['E1', 'px1', 'py1', 'pz1', 'pt1', 'eta1', 'phi1', 'Q1']
  >>> from lb_pidsim_train.utils import data_from_trees
  >>> trees = [events]
  >>> branches = ['px1', 'py1', 'pz1']
  >>> df = data_from_trees (tree, branches, chunk_size = 10)
  >>> print (df)
           px1        py1        pz1
  0  -8.079890  32.745788  27.202641
  1  -8.079890  32.745788  27.202641
  2  -8.082860  32.757827  27.213639
  3  10.979156 -45.455666  40.564073
  4  -8.175690  42.604240  10.029813
  5  -8.175690  42.604240  10.029813
  6  -8.177104  42.611606  10.020414
  7  24.778697   7.897128  38.278596
  8 -33.957113 -23.001362  22.853348
  9 -33.957113 -23.001362  22.853348
  """
  ## Total entries
  tot_entries = 0
  for t in trees:
    tot_entries += t.num_entries

  ## Data-type control
  if max_ntrees is not None:
    try:
      max_ntrees = int ( max_ntrees )
    except:
      raise TypeError ("The maximum number of trees should be an integer.")
  else:
    max_ntrees = int ( len(trees) )

  if chunk_size is not None:
    try:
      chunk_size = int ( chunk_size )
    except:
      raise TypeError ("The chunk-size should be an integer.")
  else:
    chunk_size = int ( tot_entries )

  data = list()
  indices = np.random.permutation (len(trees)) [:max_ntrees]
  for i in indices:
    tree = trees[i]

    ## Entry start-stop computation
    num_entries = tree.num_entries
    frac = num_entries / tot_entries
    tree_chunk = int (frac * chunk_size)
    entry_start = np.random.randint ( 0, max (1, num_entries - tree_chunk) )
    entry_stop  = entry_start + tree_chunk

    ## Data load
    data . append ( tree.arrays ( expressions = branches ,
                                  cut = cut ,
                                  entry_start = entry_start ,
                                  entry_stop  = entry_stop  ,
                                  library = "pd" ) )

  data = pd.concat (data, ignore_index = True)

  return data



if __name__ == "__main__":
  ## Open ROOT tree
  events = uproot.open ("../data/Zmumu.root:events")
  print ( events.keys() [3:11] )

  ## Tree -> dataframe
  trees = [events]
  branches = ['px1', 'py1', 'pz1']
  df = data_from_trees (trees, branches, chunk_size = 10)
  print (df)

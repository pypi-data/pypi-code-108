# Authors: Patrick Stumpf
#          Natalija Stojanovic
#          Rodrigo Salazar
#
import sys
import numpy as np
import pandas as pd
import scanpy as scp
from scipy.stats import mannwhitneyu as mwu

def run(AdataSrc, AdataTgt, groupby = None, groups = None, rankFeatures = False, method = 't-test', nFeatures=200, returnTestStatistic = False):
  ''' Main function to annotate target data using source data.
  
  Calculate cluster-specific expression patterns and match these patterns against samples in target data. Data typically originates from scRNAseq experiments but other modalities or large-scale bulk-cell experiments are also conceivable. Data is strictly required to be stored as an annotated data object (https://anndata.readthedocs.io/), e.g. obtained from scanpy (https://scanpy.readthedocs.io).
  
  Parameters
  ----------
  AdataSrc : anndata object
    Reference data from which expression patterns are to be extracted.
  AdataTgt : anndata object
    New data to which expression patterns from reference data are matched.
  groupby : string
    Name of the column in AdataSrc.obs containing the cluster labels (e.g.celltype/subtype/louvain/leiden cluster).
  groups : tuple of strings, optional
    Names of the clusters to include in PhysioSpace. Subset of labels in AdataSrc.obs[groupby]. If None (default), all cluster labels are used.
  method : string
    Name of the statistical hypothesis test used by _scanpy.tl.ranked_genes_groups()_ (default: 't-test').
  rankFeatures : bool, optional
    Should features be ranked using scanpty.rank_genes_groups()
  nFeatures : int, optional
    Number of features to consider when calculating the physioscore.
  returnTestStatistic: bool, optional
    The test statistic of the Wilcoxon Rank-Sum test is returned if true , or else the corresponding signed log10 p-value (default).

  Returns
  -------
  PhysioScore : pandas.DataFrame
    DataFrame of shape [n x m], where n is the number of samples in target and m is the number of clusters in source. Values are the test statistic from Mann-Whitney-U test (or signed log10 p-value if _ReturnStatistic=False_).

  See Also
  --------
  Lenz et al. (2013) https://doi.org/10.1371/journal.pone.0077627

  Examples
  --------
  >>> ...
  
  '''

  print('\n(1/3) Aligning feature space ... ')
  AdataSrc, AdataTgt = _alignFeatureSpace(AdataSrc, AdataTgt)
  
  print('\n(2/3) Calculating source physiospace ... ')
  physiospace = _calculatePhysioSpace(AdataSrc, groupby = groupby, groups = groups, method = method, rankFeatures = rankFeatures)
  
  print('\n(3/3) Annotating target cells ... ')
  physioscore = _calculatePhysioScore(physiospace, AdataTgt, nFeatures = nFeatures, returnTestStatistic = returnTestStatistic)
  
  return physioscore





def _alignFeatureSpace(AdataSrc, AdataTgt):
  '''Subset AnnData objects to common features. 
  
  Returns AnnData objects containing intersect between features obtained from simple matching of **var_names**.
  
  Parameters
  ----------
  AdataSrc : anndata object
    Reference data from which expression patterns are to be extracted.
  AdataTgt : anndata object
    New data to which expression patterns from reference data are matched.
    
  Returns
  -------
  AdataSrc, AdataTgt : AnnData objects
    Subsets of input data are returned, containing only the intersect of features in source and target data in the same order.
  '''

  # match feature names between AnnData objects
  common_genes = AdataSrc.var_names.intersection(AdataTgt.var_names)
  
  if common_genes.empty:
    raise ValueError("Alignment of features failed. Please ensure that feature labels can be matched between AnnData objects.")
  elif common_genes.shape[0] < 0.1 * min(AdataSrc.shape[0], AdataTgt.shape[0]):
    raise ValueError("Less than 10% features could be matched between AnnData objects.")
  elif common_genes.shape[0] < 100:
    raise ValueError("Less than 100 features could be matched between AnnData objects.")
  else:
    print('{} common features could be matched.'.format(common_genes.shape[0]))
    return AdataSrc[:, common_genes], AdataTgt[:, common_genes]






def _calculatePhysioSpace(AdataSrc, groupby, groups = None, method = 't-test', rankFeatures = False):  
  '''Obtain PhysioSpace from source data.
  
  Extracts the PhysioSpace from AdataSrc by calling _cluster_PhysioSpace()_ in a parallelized manner.

  Parameters
  ----------
  AdataSrc : anndata object
    Reference data.
  groupby : string
    Name of the column in AdataSrc.obs containing the cluster labels (e.g. celltype/subtype/louvain/leiden cluster).
  groups : tuple of strings, optional
    Names of the clusters to include in physiospace. Subset of labels in AdataSrc.obs[groupby]. If None (default), all cluster labels are used.
  method : string, optional
    Name of the statistical hypothesis test used by _scanpy.tl.ranked_genes_groups()_
  rankFeatures: bool
    Default false, i.e. use existing gene ranking.
  
  Returns
  -------
  physiospace : numpy.array
    A numpy array containing the physiospace obtained from AdataSrc, where rows are the features in AdataSrc and columns are the group labels in parameter groups.
  '''

  # init empty pandas DataFrame 
  physiospace = pd.DataFrame() 
  
  if groups is None:
    groups = set(AdataSrc.obs[groupby].to_list())
  
  if rankFeatures:
    print('Running "rank_genes_groups()" ... ')
    scp.tl.rank_genes_groups(adata = AdataSrc, groupby = groupby, groups = groups, method=method)
    print('complete.')
  elif 'rank_genes_groups' not in AdataSrc.uns:
    raise ValueError('Please run "scanpy.tl.rank_genes_groups(adata=AnnDataSource)" before running physiopy.')
    
  for group in groups:
    print('Processing {}'.format(group))
    physiospace.loc[:,group] = scp.get.rank_genes_groups_df(adata=AdataSrc, group=group).sort_values(by='names').set_index(['names'])['scores']
  
  return physiospace





def _calculatePhysioScore(physiospace, AdataTgt, nFeatures, returnTestStatistic):
  ''' Calculates a score for each source physiospace axes and target samples.
  
  Iterate through the target samples (columns) and through the physiospace axes (columns).
  For each sample in target, extract the 100 top-ranking features and the 100 bottom-ranking features based on the expression relative to the median across all target samples.
  
  Parameters
  ----------
  physiospace : numpy array
  AdataTgt : anndata object
    New data to which expression patterns from reference data are matched.
  nFeatures : int, optional
    Number of features to consider when calculating the physioscore.
  returnTestStatistic: bool, optional
    The test statistic of the Wilcoxon Rank-Sum test is returned if true , or else the corresponding signed log10 p-value (default).

  Returns
  -------
  physioscore : pandas.DataFrame
    Score indicating the alignment of each sample in AdataTgt to the provided physiospace axes.
  '''
  # calculate mean across all samples
  meanstddf = _meanstd(AdataTgt)
 
  # init empty pandas.DataFrame to store scores
  physioscore = pd.DataFrame(data = np.zeros((AdataTgt.shape[0], physiospace.shape[1])), columns=physiospace.columns)
  
  # iterate through rows in target AnnData object (samples aka. cells)
  for i in _progressbar(range(AdataTgt.shape[0]), "Computing: ", 40):     # TO DO: parallelize

    # calculate relative expression of sample by subtracting the mean; sort values and extract top & bottom 100 indices
    x = ((AdataTgt.X[i,:] - meanstddf['center']) / meanstddf['center']).sort_values()
    ixDown = x.head(int(nFeatures/2)).index.to_list()
    ixUp = x.tail(int(nFeatures/2)).index.to_list()
    
    # iterate through columns in source physiospace
    for j in range(physiospace.shape[1]):
      physioscore.iloc[i,j] = _onescore(physiospaceAxis = physiospace.iloc[:,j], ixUp = ixUp, ixDown = ixDown, returnTestStatistic = returnTestStatistic)
  
  return physioscore
  




def _meanstd(AdataTgt):
  ''' Mean expression and standard deviation for features in target data.
  '''
  if 'mean_counts' in AdataTgt.var:
    return pd.DataFrame({'center': AdataTgt.var['mean_counts'], 'scale': np.std(AdataTgt.X)}, index=AdataTgt.var_names)
  else:
    return pd.DataFrame({'center': np.mean(AdataTgt.X), 'scale': np.std(AdataTgt.X)}, index=AdataTgt.var_names)
  
  


  
def _onescore(physiospaceAxis, ixUp, ixDown, returnTestStatistic=True):
  ''' Test PhysioSpace from source for differential expression of indices from target, using Mann-Whitney-U test.
  
  Parameters
  ----------
  physiospaceAxis :
    A single PhysioSpace axis, corresponding to e.g. a cell identity.
  ixUp : list
   Indices of top features in target sample (largest z-score, indicating higher than average expression).
  ixDown : list
   Indices of bottom features in target sample (smallest z-score, indicating lower than average expression).
  ReturnTestStatistic : bool, optional
    Return test-statistic if returnTestStatistic = True [default]; else: return signed log2 p-value)
  
  Returns
  -------
  testresult : dtype:float
    Wilcoxon rank sum test result.
  '''
  
  w, p = mwu(physiospaceAxis[ixUp], physiospaceAxis[ixDown])
  
  wm = (w / ( len(ixUp) * len(ixDown) ) - 0.5 ) * 2

  if returnTestStatistic:
    return wm
  else:
    return np.sign(wm) * (-np.log10(p))

  
  
  
  
def _progressbar(it, prefix="", size=60, file=sys.stdout):
  '''
  https://stackoverflow.com/a/34482761
  '''
  count = len(it)
  def show(j):
    x = int(size*j/count)
    file.write("%s[%s%s] %i/%i\r" % (prefix, "#"*x, "."*(size-x), j, count))
    file.flush()        
  show(0)
  for i, item in enumerate(it):
    yield item
    show(i+1)
  file.write("\n")
  file.flush()
import numpy as np
from sklearn.decomposition import PCA
import random

def SampleFromCluster(train_id_list, dis_list, dis_list_prob, sample_method, num_sample):
    # train_id_list: position in one original dataset
    # dis_list: repository for distance of current sample to center
    # dis_list_pro: probility of the sample belong to one class
    # sample method: how to select samples
    # num_sample: number of samples we are going to select
    num_class = len(train_id_list)
    toLabel = []

       # print(num_sample, len(dis_list[i]))

          #num_sample = 1

    if sample_method == 'random':
      all_id = []
      for i in train_id_list:
        all_id += i
      np.random.shuffle(all_id)

      toLabel = all[:num_sample].tolist()

    if sample_method == 'ktop':
      print('ktop selection')
      for i in range(len(train_id_list)):
        index = train_id_list[i]
        distance = np.argsort(dis_list[i])
        if len(distance) > 0:
        #toLabel = toLabel + index[:num_sample].tolist()
          toLabel = toLabel + [index[distance[0]]]

    if sample_method == 'krandom':
      print('krandom selection')
      for i in range(len(train_id_list)):
        index = train_id_list[i]
        np.random.shuffle(index)
        # toLabel = toLabel + index[:num_sample].tolist()
        if len(index) > 0:
          toLabel = toLabel + [index[0]]

    if sample_method == 'kmi':
      print('kmi selection')
      for i in range(len(train_id_list)):
        index = train_id_list[i]
        # computed marginal difference
        mi = dis_list_prob[i]
        sort_mi = np.argsort(mi)
        if len(index) > 0:
          toLabel = toLabel + [index[sort_mi[0]]]

    return toLabel
# if sample_method == 'topbottom':
          #   index = train_id_list[i]
          #   distance = np.argsort(dis_list[i])
          #   num_ave = int(num_sample / 2)
          #   if num_ave < 1:
          #     num_ave = 1
          #   #toLabel = toLabel + index[distance[:num_ave]].tolist()+ index[distance[-num_ave:]].tolist()
          #   toLabel = toLabel + index[:num_ave].tolist() + index[-num_ave:].tolist()
          #
          # if sample_method == 'topmed':
          #   index = train_id_list[i]
          #   distance = np.argsort(dis_list[i])
          #   num_ave = int(num_sample / 2)
          #   if num_sample < 1.5:
          #     num_ave = 1
          #     p = random.uniform(0,1)
          #     if p > 0.5:
          #       toLabel = toLabel + [index[distance[0]]]
          #     else:
          #       toLabel = toLabel + [index[distance[1]]]
          #   else:
          #     interval = int(len(index)/num_sample)
          #     for i in range(num_sample):
          #       toLabel = toLabel + [index[distance[i*interval]]]

          #
          # if sample_method == 'bottom':
          #
          #   index = train_id_list[i]
          #   distance = np.argsort(dis_list[i]) # from smallest distance to large distance
          #
          #
          #   #toLabel = toLabel + index[:num_sample].tolist()
          #   toLabel = toLabel + index[distance[-num_sample:]].tolist()
          #
          # if sample_method == 'prob':
          #   index = train_id_list[i]
          #   prob = np.argsort(dis_list_prob[i]) # extract smallest probility
          #   toLabel = toLabel + index[prob[:num_sample]].tolist()




def SampleFromCluster_numSample(train_id_list, dis_list, dis_list_prob, sample_method, num_sample=1):
  # train_id_list position in one original dataset
  # dis_list: repository for distance of current sample to center
  # dis_list_pro: probility of the sample belong to one class
  # sample method: how to select samples
  # percentage: number of samples we are going to select
  num_class = len(train_id_list)
  toLabel = []
  for i in range(num_class):
    # print(num_sample, len(dis_list[i]))
    if num_sample >= 1:
      # num_sample = 1

      if sample_method == 'random':
        index = train_id_list[i]
        np.random.shuffle(index)

        toLabel = toLabel + index[:num_sample].tolist()

      if sample_method == 'topbottom':
        index = train_id_list[i]
        distance = np.argsort(dis_list[i])
        num_ave = int(num_sample / 2)
        if num_ave < 1:
          num_ave = 1
        # toLabel = toLabel + index[distance[:num_ave]].tolist()+ index[distance[-num_ave:]].tolist()
        toLabel = toLabel + index[:num_ave].tolist() + index[-num_ave:].tolist()

      if sample_method == 'topmed':
        index = train_id_list[i]
        distance = np.argsort(dis_list[i])
        num_ave = int(num_sample / 2)
        if num_sample < 1.5:
          num_ave = 1
          p = random.uniform(0, 1)
          if p > 0.5:
            toLabel = toLabel + [index[distance[0]]]
          else:
            toLabel = toLabel + [index[distance[1]]]
        else:
          interval = int(len(index) / num_sample)
          for i in range(num_sample):
            toLabel = toLabel + [index[distance[i * interval]]]

      if sample_method == 'top':
        index = train_id_list[i]
        distance = np.argsort(dis_list[i])
        # toLabel = toLabel + index[:num_sample].tolist()
        toLabel = toLabel + index[distance[:num_sample]].tolist()

      if sample_method == 'bottom':
        index = train_id_list[i]
        distance = np.argsort(dis_list[i])  # from smallest distance to large distance

        # toLabel = toLabel + index[:num_sample].tolist()
        toLabel = toLabel + index[distance[-num_sample:]].tolist()

      if sample_method == 'prob':
        index = train_id_list[i]
        prob = np.argsort(dis_list_prob[i])  # extract smallest probility
        toLabel = toLabel + index[prob[:num_sample]].tolist()

  return toLabel

def SampleClaProb(train_id_list, classification_prob, sample_method, percentage):
    # train_id_list position in one original dataset
    # dis_list: repository for distance of current sample to center
    # dis_list_pro: probility of the sample belong to one class
    # sample method: how to select samples
    # percentage: number of samples we are going to select
    num_class = len(train_id_list)
    toLabel = []
    for i in range(num_class):
        num_sample = np.round(percentage * len(train_id_list[i]))
        num_sample = int(num_sample)
        #print(num_sample, len(dis_list[i]))
        if num_sample  >=  1:
          #num_sample = 1    

          if sample_method == 'prob':
            index = train_id_list[i]
            prob = np.argsort(classification_prob[i]) 
            # if prob corresponding to entropy (without minus) then maximum entropy 
            # equals to smallest value in the prob
            # extract smallest probility (most uncertain or difference 
            #between the first one and the second one is the smallest)
            toLabel = toLabel + index[prob[:num_sample]].tolist()

    return toLabel

def SampleOneCluster(train_id_list, dis_list, dis_list_prob, sample_method, percentage, ith_cluster):
    # train_id_list position in one original dataset
    # dis_list: repository for distance of current sample to center
    # dis_list_pro: probility of the sample belong to one class
    # sample method: how to select samples
    # percentage: number of samples we are going to select
  
    num_sample = int(np.round(percentage * len(dis_list[ith_cluster])))
    #print(num_sample, len(dis_list[i]))
    if num_sample  == 0:
      num_sample = 1

    if sample_method == 'random':
      index = train_id_list[ith_cluster]
      np.random.shuffle(index)
      
      toLabel = index[:num_sample].tolist()

    if sample_method == 'topbottom':
      index = train_id_list[ith_cluster]
      distance = np.argsort(dis_list[ith_cluster])
      num_ave = int(num_sample / 2)
      if num_ave < 1:
        num_ave = 1 
      #toLabel = toLabel + index[distance[:num_ave]].tolist()+ index[distance[-num_ave:]].tolist()
      toLabel = toLabel + index[:num_ave].tolist() + index[-num_ave:].tolist()

    if sample_method == 'top':
      index = train_id_list[ith_cluster]
      distance = np.argsort(dis_list[ith_cluster]) 
      #toLabel = toLabel + index[:num_sample].tolist()
      toLabel =  index[distance[:num_sample]].tolist()

    if sample_method == 'bottom':

      index = train_id_list[ith_cluster]
      distance = np.argsort(dis_list[ith_cluster]) # from smallest distance to large distance

      
      #toLabel = toLabel + index[:num_sample].tolist()
      toLabel =  index[distance[-num_sample:]].tolist()      

    if sample_method == 'prob':
      index = train_id_list[ith_cluster]
      prob = np.argsort(dis_list_prob[ith_cluster]) # extract smallest probility
      toLabel = index[prob[:num_sample]].tolist()

    return toLabel

# def pca_dimension_reduction(data_matrix, num_components):
#   #data_matrix = np.asarray(data_matrix)
#   pca = PCA(n_components=num_components).fit(data_matrix)
#
#   reduced_data = PCA(n_components=num_components).fit_transform(data_matrix)
#
#   return reduced_data

def remove_labeled(hi_train, label_semi, index):
 	non_labeled = label_semi == 0
 	if np.sum(non_labeled) == hi_train.shape[0]:
 		re_train = hi_train
 		re_index = index
 	else:
	 	re_train = hi_train[non_labeled,:]
	 	re_index = label_semi[non_labeled]
 	return re_train, re_index

def UniformSampling(hi_train, label_semi, index_train,  percentage):

  #reduced_data = pca_dimension_reduction(hi_train, num_components=3)
  re_train, re_index = remove_labeled(hi_train, label_semi, index_train)
  reduced_dimension = pca_dimension_reduction(re_train, 3)

  # find range
  x_max = np.max(reduced_dimension[:,0])+0.5
  x_min = np.min(reduced_dimension[:,0])-0.5
  y_max = np.max(reduced_dimension[:,1])+0.5
  y_min = np.min(reduced_dimension[:,1])-0.5
  z_max = np.max(reduced_dimension[:,2])+0.5
  z_min = np.min(reduced_dimension[:,2])-0.5

  nbins = np.int(np.ceil((reduced_dimension.shape[0]*percentage)**(1/3)))
  x_edge = np.linspace(x_min, x_max, nbins)
  y_edge = np.linspace(y_min, y_max, nbins)
  z_edge = np.linspace(z_min, z_max, nbins)

  # find corresponding position in edges
  x_pos = np.searchsorted(x_edge, reduced_dimension[:, 0], side='left')
  y_pos = np.searchsorted(y_edge, reduced_dimension[:,1], side='left')
  z_pos = np.searchsorted(z_edge, reduced_dimension[:, 2], side='left')

  label = []
  test = np.arange(len(x_pos))
  for xi in range(1, len(x_edge)):
    for yi in range(1, len(y_edge)):
      for zi in range(1, len(z_edge)):
        
        t = (x_pos == xi) & (y_pos == yi) & (z_pos == zi)
        selected = test[t]

        if np.random.uniform(0,1,1) >=0.5:
          n = np.int(np.ceil(len(selected) * percentage))
        else:
          n = np.int(np.round(len(selected) * percentage))
  

        if n >= 1:
          idx = list(range(n))
          random.shuffle(idx)
          
          tmp = selected[idx[:n]]# for i in idx[:n]
          label_tmp = index_train[tmp].tolist()
          label = label + label_tmp

  return label

def sample_class(label, index, num_class, sample_num=1):
  label = np.asarray(label)
  tolabel = []
  for cla_i in range(1, num_class + 1):
    class_list = list(index[label == cla_i])
    #    print(len(class_list))
    random.shuffle(class_list)

    if sample_num == 1:
      tolabel = tolabel + [class_list[0]]
    else:
      tolabel = tolabel + class_list[:sample_num]

  return tolabel

  # kde = KernelDensity(kernel='gaussian', bandwidth=0.2).fit(reduced_dimension)
  # den = np.exp(kde.score_samples(reduced_dimension))


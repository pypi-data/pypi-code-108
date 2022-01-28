
from openlabcluster.training_utils.ssl.acc_func import *
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def remove_labeled_cluster(train_set,train_id, labeled, mi=[]):
    if len(labeled) != 0:
        del_id = []
        for i in range(len(train_id)):
            if train_id[i] in labeled:
                del_id = del_id + [i]
        train_set = np.delete(train_set, del_id, axis=0)
        train_id = np.delete(train_id, del_id, axis=0)
        if len(mi)>0:
            mi = np.delete(mi, del_id, axis=0)
    if len(mi)>0 or len(train_id)==0: # for the case all sample is labeled
        return train_set,  train_id, mi
    else:
        return train_set, train_id


# def iter_kmeans_cluster(train_set, test_set, train_label,
#                         test_label, train_id, pred_id, ncluster=7,
#                         beta=1):
#     if type(train_label) != np.array:
#         train_label = np.asarray(train_label)

#     test_label = np.asarray(test_label)

#     kmeans = KMeans(ncluster, init='k-means++', max_iter=500, random_state=0).fit(train_set)
#     pre_train = kmeans.predict(train_set)

#     pre_test = kmeans.predict(test_set)

#     distance = kmeans.transform(train_set)
#     distance_prob = np.exp(-beta * distance)  # label start from 0
#     distance_prob = np.divide(distance_prob, np.sum(distance_prob, 1, keepdims=True))

#     DisToCenter = []
#     DisToCenter_prob = []
#     for i in range(len(pre_train)):
#         DisToCenter.append(distance[i, pre_train[i]])  # distance of sample i to kmeans cluster
#         DisToCenter_prob.append(distance_prob[i, pre_train[i]])
#     DisToCenter = np.asarray(DisToCenter)
#     DisToCenter_prob = np.asarray(DisToCenter_prob)

#     train_id_list = []
#     dis_list = []
#     dis_list_prob = []
#     for i in range(ncluster):
#         clas_poss = pre_train == i  # select samples with predicted cluter i
#         train_id_list.append(train_id[clas_poss])
#         dis_list.append(DisToCenter[clas_poss])
#         dis_list_prob.append(DisToCenter_prob[clas_poss])

#     # compute the adjusted label for measure of accuracy
#     adjusted_rand_train = precision_score(train_label, pre_train, average='micro')
#     adjusted_rand_test = precision_score(test_label, pre_test, average='micro')

#     acc_train = recall_score(train_label, pre_train, average='micro')
#     acc_test = recall_score(test_label, pre_test, average='micro')

#     list_pre_train = []
#     list_pre_test = []
#     for i in range(1, ncluster + 1):
#         ith_label = train_label == i
#         corresponding_pre = pre_train[ith_label]
#         # list_pre_train.append(Counter(corresponding_pre))

#         ith_test = test_label == i
#         corresponding_test_pre = pre_test[ith_test]
#         # list_pre_test.append(Counter(corresponding_test_pre))

#     return adjusted_rand_train, adjusted_rand_test, acc_train, acc_test, train_id_list, dis_list, DisToCenter_prob

def few_knn_data_semi(data_train, data_eval, label_train, label_eval, train_semi, eval_semi):
    # only use few labels
    train_index = []
    label_train = np.asarray(label_train)
    label_eval = np.asarray(label_eval)
    for i in range(len(train_semi)):
        if train_semi[i] != 0:
            train_index.append(i)
    train_index = np.r_[train_index]
    data_train = data_train[train_index, :]
    label_train = label_train[train_index]
#    assert (train_semi[train_semi != 0] == label_train).all()
    return data_train, data_eval, label_train, label_eval

def iter_kmeans_cluster(train_set,
                         train_id, ncluster=10,
                          mi=[]):
    train_set = preprocessing.normalize(train_set)

    kmeans = KMeans(ncluster, init='k-means++', max_iter=500, random_state=0).fit(train_set)
    pre_train = kmeans.predict(train_set)

    distance = kmeans.transform(train_set)
    distance_prob = np.exp( distance)
    distance_prob = np.divide(distance_prob, np.sum(distance_prob, 1, keepdims=True))

    DisToCenter = []

    for i in range(len(pre_train)):
        DisToCenter.append(distance[i, pre_train[i]])
        #DisToCenter_prob.append(distance_prob[i, pre_train[i]])
    DisToCenter = np.asarray(DisToCenter)

    train_id_list = []
    dis_list = []
    dis_list_prob = []
    cluster_label = np.zeros(len(train_id))
    for i in range(ncluster):
        clas_poss = pre_train == i
        cluster_label[clas_poss] = i
        train_id_list.append(train_id[clas_poss])
        dis_list.append(DisToCenter[clas_poss])
        if len(mi) >0:
            dis_list_prob.append(mi[clas_poss])

    return train_id_list,dis_list,dis_list_prob, cluster_label


def iter_cluster_withlabel(train_set, test_set, train_label,
                           test_label, train_id, pred_id, ncluster=10,
                           beta=1):
    train_label = np.asarray(train_label)
    test_label = np.asarray(test_label)
    train_set = preprocessing.normalize(train_set)
    test_set = preprocessing.normalize(test_set)

    dis_list = []
    train_id_list = []
    train_label_list = []
    DisToCenter_prob = []
    dis = np.zeros(train_set.shape[0])
    for i in range(1, max(train_label) + 1):
        icla = train_label == i
        icenter = np.mean(train_set[icla, :], axis=0)
        dis_tmp = np.power((train_set[icla, :] - icenter), 2).sum(1)
        dis_tmp = np.sqrt(dis_tmp)
        dis_list.append(dis_tmp)
        train_id_list.append(train_id[icla])
        train_label_list.append(train_label[icla])

    return train_id_list, dis_list, DisToCenter_prob, train_label_list


def iter_kmeans_nei(train_set, test_set, train_label,
                        test_label, train_id, toLabel, ncluster=10,
                         beta=1):
    # compute two meansure for selection,
    # 1. distance to cluster center
    # 2. distance to slsected neighbour
    train_label = np.asarray(train_label)
    test_label = np.asarray(test_label)
    train_set = preprocessing.normalize(train_set)
    test_set = preprocessing.normalize(test_set)
    kmeans = KMeans(ncluster, init='k-means++', max_iter=500, random_state=0).fit(train_set)
    pre_train = kmeans.predict(train_set)

    pre_test = kmeans.predict(test_set)

    distance = kmeans.transform(train_set)
    distance_prob = np.exp(-beta * distance)
    distance_prob = np.divide(distance_prob, np.sum(distance_prob, 1, keepdims=True))

    DisToCenter = []
    DisToCenter_prob = []
    for i in range(len(pre_train)):
        DisToCenter.append(distance[i, pre_train[i]])
        DisToCenter_prob.append(distance_prob[i, pre_train[i]])
    DisToCenter = np.asarray(DisToCenter)
    DisToCenter_prob = np.asarray(DisToCenter_prob)

    train_id_list = []
    dis_list = []
    dis_list_prob = []
    for i in range(ncluster):
        clas_poss = pre_train == i
        hi_tmp = train_set[clas_poss,:]
        id_tmp = train_id[clas_poss]
        dis_tmp  = DisToCenter[clas_poss]
        dis_tmp_prob = DisToCenter_prob[clas_poss]
        ave_nei_dis, unlab_pos = average_toLabeled(hi_tmp, id_tmp, toLabel)#average_toLabeled(hi_tmp, id_tmp, toLabel)
        train_id_list.append(id_tmp[unlab_pos])
        dis_list.append(dis_tmp[unlab_pos] - ave_nei_dis)
        dis_list_prob.append(dis_tmp_prob[unlab_pos])
    return train_id_list, dis_list, DisToCenter_prob

def average_toLabeled(hi_train, idx, toLabel):
    if len(toLabel) > 0:
        label_pos = []
        for i in range(len(idx)):
            if idx[i] in toLabel:
                label_pos = label_pos + [i]
        if len(label_pos) > 0:
            unalb_pos = np.setdiff1d(list(range(len(idx))), label_pos)
            label_pos = np.asarray(label_pos)
            unlab_pos = np.asarray(unalb_pos)
            lab_data = hi_train[label_pos,:]
            unlab_data = hi_train[unlab_pos, :]
            lab_data = np.repeat(np.expand_dims(lab_data, 0), unlab_data.shape[0], axis=1)
            unlab_data = np.repeat(np.expand_dims(unlab_data, 1), lab_data.shape[0], axis=1)
            dis = np.sqrt(np.sum(np.power(unlab_data-lab_data, 2), 2))
            ave_dis = np.mean(dis, 1)
            return ave_dis, unlab_pos
        else:
            return np.zeros(len(idx)), np.arange(0, len(idx))

    else:
        return np.zeros(len(idx)), np.arange(0, len(idx))

def dis_tomeanLabeled(hi_train, idx, toLabel):
    if len(toLabel) > 0:
        label_pos = []
        for i in range(len(idx)):
            if idx[i] in toLabel:
                label_pos = label_pos + [i]
        if len(label_pos) > 0:
            unalb_pos = np.setdiff1d(list(range(len(idx))), label_pos)
            label_pos = np.asarray(label_pos)
            unlab_pos = np.asarray(unalb_pos)
            lab_data = np.mean(hi_train[label_pos,:], 0)
            unlab_data = hi_train[unlab_pos, :]
            dis = np.sqrt(np.sum(np.power(unlab_data-lab_data, 2), 1))
            return dis, unlab_pos
        else:
            return np.zeros(len(idx)), np.arange(0, len(idx))

    else:
        return np.zeros(len(idx)), np.arange(0, len(idx))

def use_kmeans_cluster(train_set, test_set, train_label, test_label, ncluster):
    # print(train_set)
    train_label = np.asarray(train_label)
    test_label = np.asarray(test_label)
    Xtr_Norm = preprocessing.normalize(train_set)
    Xte_Norm = preprocessing.normalize(test_set)

    kmeans = KMeans(ncluster, init='k-means++', max_iter=500, random_state=0).fit(Xtr_Norm)
    pre_train = kmeans.predict(Xtr_Norm)
    pre_test = kmeans.predict(Xte_Norm)

    # compute the adjusted label for measure of accuracy
    adjusted_rand_train = precision_score(train_label, pre_train,
                                          average='micro')  # adjusted_rand_score(train_label, pre_train)
    adjusted_rand_test = precision_score(test_label, pre_test, average='micro')

    acc_train = recall_score(train_label, pre_train, average='micro')
    acc_test = recall_score(test_label, pre_test, average='micro')

    list_pre_train = []
    list_pre_test = []
    for i in range(1, ncluster + 1):
        ith_label = train_label == i
        corresponding_pre = pre_train[ith_label]
        # list_pre_train.append(Counter(corresponding_pre))

        ith_test = test_label == i
        corresponding_test_pre = pre_test[ith_test]
        # list_pre_test.append(Counter(corresponding_test_pre))

    return adjusted_rand_train, adjusted_rand_test, acc_train, acc_test
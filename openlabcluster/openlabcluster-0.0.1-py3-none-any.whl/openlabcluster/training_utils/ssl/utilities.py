import matplotlib.pyplot as plt
import time
import math
# plt.switch_backend('agg')
import matplotlib.ticker as ticker
import numpy as np
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def asMinutes(s):
    m = math.floor(s / 60)
    s -= m * 60
    return '%dm %ds' % (m, s)


def timeSince(since, percent):
    now = time.time()
    s = now - since
    es = s / (percent)
    rs = es - s
    return '%s (- %s)' % (asMinutes(s), asMinutes(rs))


from collections import Counter


def print_class(label_train, index_train, tolabel):
    lab = []
    for i in range(len(index_train)):
        if index_train[i] in tolabel:
            lab = lab + [label_train[i]]
    print('class', Counter(lab))


def showPlot(loss, eval_loss, ari, eval_ari, figure_name):
    plt.figure()
    fig, ax = plt.subplots()
    # this locator puts ticks at regular intervals
    loc = ticker.MultipleLocator(base=0.2)
    ax.yaxis.set_major_locator(loc)
    plt.plot(loss, '-', c='red')
    plt.plot(eval_loss, '-', c='blue')
    plt.plot(ari, '.-', c='red')
    plt.plot(ari, '.-', c='blue')
    plt.show()
    plt.savefig(figure_name)


def load_model(model_path, model, optimizer, device):
    model_dict = torch.load(model_path, map_location=device)
    model.load_state_dict(model_dict['model_state_dict'])
    if optimizer:
        optimizer.load_state_dict(model_dict['optimizer_state_dict'])
        model.train()

    else:
        model.eval()

    return model, optimizer


def save_checkpoint(model, epoch, optimizer, loss, PATH):
    torch.save({
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss,
    }, PATH)


from sklearn.decomposition import PCA
# import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
# plt.switch_backend('agg')
from mpl_toolkits.mplot3d import Axes3D


def pca_dimension_reduction(data_matrix, num_components):
    # data_matrix = np.asarray(data_matrix)
    pca = PCA(n_components=num_components).fit(data_matrix)

    reduced_data = PCA(n_components=num_components).fit_transform(data_matrix)

    return reduced_data


from mpl_toolkits.mplot3d import Axes3D

font = {'family': 'normal',
        'weight': 'bold',
        'size': 22}

mpl.rc('font', **font)


def show_low_dimension(reduced_dimension, label, semi_label, file_path, dimensions):
    N = 10  # Number of labels

    # setup the plot
    fig = plt.figure(figsize=[10, 10], dpi=600)
    if dimensions == 3:
        ax = fig.add_subplot(111, projection='3d')
    else:
        ax = fig.add_subplot(111)
    # define the data
    # x = np.random.rand(1000)
    # y = np.random.rand(1000)
    # tag = np.random.randint(0,N,1000) # Tag each point with a corresponding label

    # define the colormap
    cmap = plt.cm.jet
    # extract all colors from the .jet map
    cmaplist = [cmap(i) for i in range(cmap.N)]
    # create the new map
    cmap = cmap.from_list('Custom cmap', cmaplist, cmap.N)

    # define the bins and normalize
    bounds = np.linspace(0.5, N + 0.5, N + 1)
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

    size = 3 * np.ones(len(label))
    for ith in range(len(semi_label)):
        if semi_label[ith] != 0:
            size[ith] = 10

    # make the scatter
    if dimensions == 3:
        scat = ax.scatter(reduced_dimension[:, 0], reduced_dimension[:, 1], reduced_dimension[:, 2],
                          c=label, s=size, cmap=cmap, norm=norm)
    else:
        scat = ax.scatter(reduced_dimension[:, 0], reduced_dimension[:, 1],
                          c=label, s=1, cmap=cmap, norm=norm)

    # create the colorbar
    cb = plt.colorbar(scat, spacing='proportional', ticks=bounds)
    cb.set_label('Custom cbar')
    ax.set_title('Reduced Action Dimension')
    ax.set_xlabel('PC 1')
    ax.set_ylabel('PC 2')
    if dimensions == 3:
        ax.set_zlabel('PC 3')
    plt.savefig(file_path)
    plt.show()


def label_transformation_plot(reduced_dimension, cla_label, cluster_label, id, old_lab_id, new_lab_id, dimensions,
                              root_path, network, iteration):
    # plot cluster and label in the class
    N = 10
    fig1 = plt.figure(figsize=(10, 10), dpi=600)
    if dimensions == 3:
        ax = fig1.add_subplot(111, projection='3d')
    else:
        ax = fig1.add_subplot(111)

    cmap = plt.cm.jet
    # extract all colors from the .jet map
    cmaplist = [cmap(i) for i in range(cmap.N)]
    # create the new map
    cmap = cmap.from_list('Custom cmap', cmaplist, cmap.N)

    # define the bins and normalize
    bounds = np.linspace(0.5, N + 0.5, N + 1)
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    symbol = ['.', 'o', '*', '^', '+', 'x', 'd', 'v', 'h', 'p']
    size = 10
    for icla in range(N):
        # if cla_label[i] < 10:
        #     if id[i] in old_lab_id:
        #         size = 20
        #     elif id[i] in new_lab_id:
        #         size = 50
        #     else:
        #         size = 3
        cla_label = np.asarray(cla_label)
        i = cla_label == icla

        if dimensions == 3:
            scat = ax.scatter(reduced_dimension[i, 0], reduced_dimension[i, 1], reduced_dimension[i, 2],
                              c=icla * np.ones(sum(i)), s=size, marker=symbol[0], cmap=cmap, norm=norm)
        if dimensions == 2:
            scat = ax.scatter(reduced_dimension[i, 0], reduced_dimension[i, 1],
                              c=icla * np.ones(sum(i)), s=size, marker=symbol[0], cmap=cmap, norm=norm)

    cb = plt.colorbar(scat, spacing='proportional', ticks=bounds)
    cb.set_label('Custom cbar')
    ax.set_title('Reduced Action Dimension')
    ax.set_xlabel('PC 1')
    ax.set_ylabel('PC 2')
    if dimensions == 3:
        ax.set_zlabel('PC 3')
    plt.savefig(root_path + network + 'Claplot_%d.jpg' % iteration)


#  plt.show()
def topk_accuracy(output, target, topk=(1,)):
    """Computes the precision@k for the specified values of k"""
    maxk = max(topk)
    if not torch.is_tensor(target):
        target = torch.tensor(target)
    elif target.device != 'cpu':
        target = target.detach().cpu()
    batch_size = target.size(0)

    _, pred = output.topk(maxk, 1, True, True)
    pred = pred.t().cpu()
    correct = pred.eq(target.view(1, -1).expand_as(pred))

    res = []
    for k in topk:
        correct_k = correct[:k].flatten().float().sum(0, keepdim=True)
        res.append(correct_k.mul_(100.0 / batch_size))
    return res

def plot_selection(data_matrix, num_components, cla_label, cluster_label, id, old_lab_id, new_lab_id, root_path,
                   network, iteration):
    reduced_dimension = pca_dimension_reduction(data_matrix, num_components)
    label_transformation_plot(reduced_dimension, cla_label, cluster_label, id, old_lab_id, new_lab_id, num_components,
                              root_path, network, iteration)
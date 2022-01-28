# load file

from re import T
from sklearn.manifold import TSNE
from openlabcluster.training_utils.ssl.extract_hidden import extract_hidden_ordered
import matplotlib.pyplot as plt
import umap
from sklearn.decomposition import PCA
from torch.nn.utils import clip_grad_norm_
from openlabcluster.training_utils.ssl.utilities import save_checkpoint
from openlabcluster.training_utils.ssl.data_loader import *
from openlabcluster.utils.plotting import format_axes

DIMENSION_REDUCTION_DICT = {'PCA': PCA, 'tSNE': TSNE, 'UMAP':umap.UMAP}
def train_iter(input_tensor, seq_len, label, model, optimizer, criterion_seq, criterion_cla, alpha, device):
    optimizer.zero_grad()
    if alpha == 0:
        en_hi, de_out = model(input_tensor, seq_len)
        cla_loss = 0
        cla_pre = None
    else:
        en_hi, de_out, cla_pre = model(input_tensor, seq_len)
        if sum(label != 0) != 0:
            cla_loss = criterion_cla(cla_pre[label != 0], label[label != 0] - 1)
        else:
            cla_loss = 0

    mask = torch.zeros([len(seq_len), max(seq_len)]).to(device)
    for ith_batch in range(len(seq_len)):
        mask[ith_batch, 0:seq_len[ith_batch]] = 1
    mask = torch.sum(mask, 1)

    seq_loss = torch.sum(criterion_seq(de_out, input_tensor), 2)
    seq_loss = torch.mean(torch.sum(seq_loss, 1) / mask)

    total_loss = alpha * cla_loss + (1 - alpha) * seq_loss
    if cla_loss!=0:
        cla_loss = cla_loss.item()

    total_loss.backward()
    clip_grad_norm_(model.parameters(), 25, norm_type=2)

    optimizer.step()
    del mask
    return seq_loss.item(), cla_loss, en_hi, cla_pre

def clustering_knn_acc(model, train_loader, hidden_size,
                       num_class, alpha, few_knn, figure, epoch,
                       device, reducer_name, dimension
                       ):
    if alpha == 0:
        hi_train, label_train,  train_semi = extract_hidden_ordered(model, train_loader, hidden_size, alpha, device)
    else:
        hi_train, label_train, train_semi,_,_ = extract_hidden_ordered(model, train_loader, hidden_size, alpha, device)
    # print(hi_train.shape)
    # MOISHE: commented line below
    # np.save('/home/ws2/Documents/jingyuan/IC_GUI/deeplabcut_removetest/gui/3D-2021-05-02/models/hidden_epoch%d.npy' % epoch, hi_train)
    #transformed = TSNE(n_components=2).fit_transform(hi_train)
    #reducer = umap.UMAP(random_state=42, n_components=dimension)
    dim_reducer = DIMENSION_REDUCTION_DICT[reducer_name]
    if dimension == '2d':
        reducer = dim_reducer(n_components=2)
    else:
        reducer = dim_reducer(n_components=3)
    transformed = reducer.fit_transform(hi_train)
    if figure:
        figure.axes.cla()
        if dimension =='2d':
            figure.axes.scatter(transformed[:,0], transformed[:,1],s=10, picker=True, color='k')
        else:
            figure.axes.scatter(transformed[:, 0], transformed[:, 1],  transformed[:, 1], s=10, picker=True, color='k')

        figure.axes.set_title('Cluster Map Epoch %d' % epoch)
        
        format_axes(axes=figure.axes)

        figure.canvas.draw_idle()


def training(ith_epoch, epoch, train_loader, print_every,canvas,
             model, optimizer, criterion_seq, criterion_cla, alpha, k, file_output, past_loss,
             model_path, pre, hidden_size,  model_prefix, num_class=10,
             few_knn=False, device='cuda',reducer_name='PCA', dimension='2d'):
    cla = 0
    seq=0

    if ith_epoch % print_every == 0:
        clustering_knn_acc(
            model,
            train_loader,
             hidden_size,
            num_class,
            alpha,
            few_knn, canvas,  ith_epoch, device, reducer_name, dimension)
    corr_num = 0
    labeled_num = 0
    for it, (data, seq_len, label, semi_label,_) in enumerate(train_loader):
        # MOISHE: does it have to load data into a GPU??
        # try changing the flag in the config
        input_tensor = data.to(device)
        semi_label = torch.tensor(semi_label, dtype=torch.long).to(device)
        seq_loss, cla_loss, en_hid, cla_pre = train_iter(input_tensor, seq_len, semi_label, model, optimizer, criterion_seq,
                                                 criterion_cla, alpha, device)
        if alpha >0:
            corr_num += sum((torch.argmax(cla_pre, axis=1)[semi_label!=0]+1) == semi_label[semi_label!=0])
        labeled_num += sum(semi_label!=0)
        cla += cla_loss
        seq += seq_loss
        loss = (1-alpha)*seq + alpha*cla
    print(f"Clas loss: {cla/(it+1):.3f} seq_loss:{seq/(it+1):.3f} acc {corr_num/labeled_num}")

    if  loss <  past_loss:
        past_loss = loss
        if os.path.exists(model_path):
            for item in os.listdir(model_path):
                if item.startswith(pre):
                    if os.path.exists('./models'):
                        open('./models/' + item,
                             'w').close()  # overwrite and make the file blank instead - ref: https://stackoverflow.com/a/4914288/3553367
                        os.remove('./models/' + item)
        else:
            os.mkdir(model_path)
        path_model = model_prefix + '_epoch%d' % (ith_epoch)

        save_checkpoint(model, epoch, optimizer, loss, path_model)
    else:
        path_model = None
    acc=corr_num/labeled_num
    if alpha >0:
        return past_loss, path_model, acc.cpu().numpy().item()
    else:
        return past_loss, path_model





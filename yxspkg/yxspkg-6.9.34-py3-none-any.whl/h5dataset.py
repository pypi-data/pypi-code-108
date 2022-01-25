#自定义的dataset，用来存储数据，通过append(list)的形式存储数据
from torch.utils.data import Dataset
import h5py
import numpy as np
import random
class dataset(Dataset):
    def __init__(self,h5name,opt,auto_save=True):
        self.h5 = h5py.File(h5name,opt)
        self.auto_save = auto_save
        self.opt = opt
        if opt in ('r','r+'):
            self.nkeys = len([i for i in self.h5.keys() if i.startswith('0_')])
            if self.nkeys:
                self.length = len(self.h5) // self.nkeys
            else:
                self.length = 0
        elif opt == 'w':
            self.length = 0
            self.nkeys = 0
        else:
            raise Exception('The opt must be one of r,r+,w')
    def append(self,data:tuple):
        if not data:
            return
        if self.nkeys == 0:
            self.nkeys = len(data)
        assert len(data) == self.nkeys, '数组大小不一'
        for i,v in enumerate(data):
            self.h5.create_dataset('{}_{}'.format(self.length,i),data=v)
        self.length += 1
        if self.auto_save: 
            self.h5.flush()
    def __iter__(self):
        self.n_iter=0
        return self
    def __next__(self):
        self.n_iter+=1
        return self[self.n_iter-1]
    def __len__(self):
        return self.length
    def __getitem__(self,n):
        return [self.h5['{}_{}'.format(n,i)].value for i in range(self.nkeys)]
    def iter_batch(self,batch_size=1,shuffle=True,cat=True):
        iter_list = list(range(self.length))
        if shuffle:
            random.shuffle(iter_list)
        groups = self.length // batch_size 
        remainder = self.length % batch_size
        for g in range(groups):
            t = [self[i] for i in iter_list[g*batch_size:g*batch_size+batch_size]]
            if cat:
                yield [np.concatenate(i,0) for i in zip(*t)]
            else:
                yield t
        if remainder:
            t = [self[i] for i in iter_list[-remainder:]]
            if cat:
                yield [np.concatenate(i,0) for i in zip(*t)]
            else:
                yield t

    def __del__(self):
        try:
            self.h5.close()
        except:
            pass

if __name__=='__main__':
    t = dataset(r'F:\pythonAPP\torch\kaggle_dog_vs_cat\model\data.h5','r+')
    for i in t.iter_batch(32):
        x,y = i
        print(x.shape,y.shape)

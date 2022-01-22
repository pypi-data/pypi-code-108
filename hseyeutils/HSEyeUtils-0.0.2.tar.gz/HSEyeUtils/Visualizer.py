import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import cv2
import torch
from torch.autograd import Variable


def showImage(array, dim = 128, tensor = True):
    if tensor:
        array = (purify(array, dim) + 1) / 2 # [-1,1] --> [0,1]
    plt.imshow(array, interpolation='nearest')
    return plt.show()



def showMap(depthMap, dim = 128, tensor = True):
        
    if tensor:
        depthMap = np.nan_to_num(purify(depthMap, dim))
    else:
        depthMap = depthMap.reshape(dim,dim)

    fig = plt.figure(figsize = (5,5))
    ax1 = fig.add_subplot(projection='3d')
    ax1.set_zlim(1000,3500)

    x = np.arange(0, dim)
    y = np.arange(0, dim)
    X, Y = np.meshgrid(x, y)
    surf = ax1.plot_surface(X, Y, depthMap, cmap = cm.coolwarm)

    ax1.set_zlabel("Thickness" + " (" + "nm" + ")")
    ax1.set_title('Patient Tear Film Thickness Profile')
    return plt.show()


def sm(depthMap, dim = 128):
    depthMap = cv2.resize(np.nan_to_num(depthMap), dsize=(128,128), interpolation=cv2.INTER_CUBIC)

    fig = plt.figure(figsize = (5,5))
    ax1 = fig.add_subplot(projection='3d')

    x = np.arange(0, dim)
    y = np.arange(0, dim)
    X, Y = np.meshgrid(x, y)
    surf = ax1.plot_surface(X, Y, depthMap, cmap = cm.coolwarm)

    ax1.set_zlabel("Thickness" + " (" + "nm" + ")")
    ax1.set_title('Patient Tear Film Thickness Profile')
    return plt.show()

def purify(tensor, dim = 128):
    cloned_tensor = tensor.clone()
    if tensor.requires_grad:
        cloned_tensor = tensor.detach()
    if tensor.device.type == 'cuda':
        cloned_tensor = cloned_tensor.cpu()
    
    if tensor.shape[0] != dim:
        if len(tensor.shape) == 4:
            if tensor.shape[1] != dim:
                cloned_tensor = cloned_tensor[0].permute(1, 2, 0)
            else:
                cloned_tensor = cloned_tensor[0]
        else:
            cloned_tensor = cloned_tensor.permute(1, 2, 0)
            
    cloned_tensor = cloned_tensor.numpy()
    channels = cloned_tensor.shape[2]
    
    if channels == 1:
        return cloned_tensor.reshape(dim,dim)
    else:
        return cloned_tensor
    
def normalize(image, maxVal):
    image = (image / (maxVal/2)) - 1
    return image


def showSample(dataloader, prediction = False):
    batch = next(iter(dataloader))
    image = batch["A"]
    dMap = batch["B"]
    color_image = batch["CA"]



    showImage(color_image)
    showImage(image)
    showMap(dMap)
    showImage(depth_to_color.apply(tensorNormalize(dMap).cpu()))

    if prediction:
        predMap = generator(Variable(image).type(Tensor))
        showMap(predMap) 
        showImage(depth_to_color.apply(tensorNormalize(predMap).cpu()))

    
    
def restore(x, maxVal):
    scalar = maxVal/2
    return (x * scalar)/scalar

    
    
def imRegulate(data):
    m = np.max(data)
    mi = np.min(data)
    norm = ((data - mi) / (m - mi))*255
    return norm.astype(np.uint8)

def tensorNormalize(tensor):
        m = torch.max(tensor)
        mi = torch.min(tensor)
        norm = (tensor - mi) / (m - mi)
        return norm
    
def npNormalize(tensor):
        m = np.max(tensor)
        mi = np.min(tensor)
        norm = (tensor - mi) / (m - mi)
        return norm
    
    
def fetchRange(tensor):
    print(torch.min(tensor), torch.max(tensor))
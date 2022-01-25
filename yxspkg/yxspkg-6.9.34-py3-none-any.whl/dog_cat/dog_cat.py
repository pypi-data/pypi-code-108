import torch as tc
from .net import feature_net, classifier
from PIL import Image
from torchvision import models, transforms
from pathlib import Path
from urllib import request
import os
import sys
def get_feature(jpgs,model_label='vgg',batch_size=4):
    
    featurenet = feature_net(model_label)
    img_transform = transforms.Compose([
    transforms.Resize(320),
    transforms.CenterCrop(299),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
    features = []
    groups = len(jpgs) // batch_size
    def get_img(img_name):
        img = Image.open(img_name)
        if img.mode=='RGBA':
            img.mode = 'RGB'
        return img_transform(img).unsqueeze(0)
    if len(jpgs) % batch_size!=0:
        groups += 1
    for i in range(groups):
        t = [get_img(name) for name in jpgs[i*batch_size:(i+1)*batch_size]]
        f = tc.cat(t,0)
        features.append(featurenet(f))
    
    return tc.cat(features,0)
def get_dog_or_cat(feature):
    mynet = classifier(512, 2)
    if sys.platform.startswith('win'):
        p = Path(os.environ['HOMEPATH']) / '.yxspkg' / 'dog_cat'
        p = os.environ['HOMEDRIVE'] / p
    else:
        p = Path(os.environ['HOME']) / '.yxspkg' / 'dog_cat'
    if not p.exists():
        os.makedirs(p)
    pth = p / 'feature_model.pth'
    if not pth.is_file():
        print('下载模型文件','https://github.com/blacksong/fragment/raw/master/dog_cat/feature_model.pth')
        request.urlretrieve('https://github.com/blacksong/fragment/raw/master/dog_cat/feature_model.pth',pth)
        print('模型文件下载完毕')
    mynet.load_state_dict(tc.load(pth))
    out = mynet(feature)
    _, pred = tc.max(out,1)
    return pred
def run(jpgs):
    m = get_feature(jpgs)
    t = get_dog_or_cat(m)
    return t
def main(jpgs=None):
    if jpgs is None:
        jpgs = sys.argv[1:]
    t = run(jpgs)
    d = ['cat','dog']
    for jpg,i in zip(jpgs,t):
        print(jpg,d[i.item()])
if __name__=='__main__':
    main()
    

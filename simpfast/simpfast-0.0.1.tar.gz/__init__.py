from fastai.vision.all import*
from fastai import*
def train_model_without_split_folder(pat, pct, bs):
  dls = ImageDataLoaders.from_folder(path=pat,                             
                                   valid_pct=pct,
                                   item_tfms=Resize(224),
                                   #fastai version 2
#                                   batch_tfms=batch,
#                                   batch_tfms=Normalize.from_stats(*imagenet_stats), #fastai version 1
                                   bs=bs,
#                                   size= 224,  #fastai version 1                            
                                   shuffle=True)
  dls.show_batch(max_n=9, ncols=3, nrows=3)
  learn = cnn_learner(dls, 
              resnet50, loss_func=CrossEntropyLossFlat(), ps=[0.2, 0.3],
                  metrics=[accuracy, Precision(average='weighted'), error_rate])
  #print ("worked")
  return learn
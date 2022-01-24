#!/usr/bin/env python
'''
ugly
Created by Seria at 14/12/2018 8:06 PM
Email: zzqsummerai@yeah.net

                    _ooOoo_
                  o888888888o
                 o88`_ . _`88o
                 (|  0   0  |)
                 O \   。   / O
              _____/`-----‘\_____
            .’   \||  _ _  ||/   `.
            |  _ |||   |   ||| _  |
            |  |  \\       //  |  |
            |  |    \-----/    |  |
             \ .\ ___/- -\___ /. /
         ,--- /   ___\<|>/___   \ ---,
         | |:    \    \ /    /    :| |
         `\--\_    -. ___ .-    _/--/‘
   ===========  \__  NOBUG  __/  ===========

'''
# -*- coding:utf-8 -*-
import nebulae
import tensorflow as tf
import os
import csv
import h5py
import numpy as np
import pandas as pd
import scipy.misc as misc
import matplotlib.pyplot as plt
import resv2


fd = nebulae.fuel.FuelDepot()
fname = 'kpi'
fd.loadFuel(name=fname + '-ct',
            batch_size=32,
            height=224,
            width=224,
            channel=3,
            data_path='/home/ai/seria/data/kpi18_mxt.hdf5',
            data_key='image',
            spatial_aug='flip,crop',
            p_sa=(0.5, 0.5),
            theta_sa=(0, ((0.25, 1), (3/4, 4/3))),
            if_shuffle=False)
fd.loadFuel(name=fname + '-cv',
            batch_size=32,
            height=224,
            width=224,
            channel=3,
            data_path='/home/ai/seria/data/kpi18_clv.hdf5',
            data_key='image',
            if_shuffle=False)
fd.loadFuel(name=fname + '-test',
            batch_size=32,
            height=224,
            width=224,
            channel=3,
            data_path='/home/ai/seria/data/kpi18_test.hdf5',
            data_key='image',
            if_shuffle=False)
# fd.loadFuel(name=fname + '-n',
#             batch_size=50,
#             height=224,
#             width=224,
#             channel=3,
#             data_path='/home/ai/seria/data/kpi18_trn.hdf5',
#             data_key='image',
#             if_shuffle=False)

# launcher = tf.placeholder(tf.float32, (None, 224, 224, 3), 'FL/input')
# terminator = tf.placeholder(tf.int64, (None), 'FL/label')

COMP = nebulae.spacedock.Component()
ls = nebulae.aerolog.LayoutSheet('/home/ai/seria/kpi_ug')
scope = 'sc'
mdtype = 'resnet_v2_152' ######################################################################
sc = nebulae.spacedock.SpaceCraft(scope, layout_sheet=ls)
sc.fuelLine('input', (None, 224, 224, 3), 'float32')
sc.fuelLine('label', (None), 'int64')
sc.fuelLine('is_train', (), 'bool', default=False)
with tf.contrib.slim.arg_scope(resv2.resnet_arg_scope()):
    logits, endpts = resv2.resnet_v2_152(sc.layout['input'], is_training=sc.layout['is_train'],
                                    num_classes=128) ###########################################################
feature = tf.squeeze(endpts['global_pool'])
# cost = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(
#             logits=logits, labels=sc.layout['label']))
#
# prob = sc.assemble(COMP.SOFTMAX(name='sftm1', input=logits))
# mmnt = COMP.ADAM(name='adam', input=cost, mile_meter=sc.miles,
#                      lr=1e-6, update_scope=mdtype, lr_decay='exp_stair',
#                      lr_miles=1000, decay_param=0.95, grad_limit=4.)
# optz = sc.assemble(mmnt)
#
# correct = tf.equal(tf.argmax(sc.layout[prob], 1), sc.layout['label'])
# accuracy = tf.reduce_mean(tf.cast(correct, tf.float32))

ind = tf.argmax(tf.nn.softmax(logits), 1)
# error = tf.where(tf.logical_not(correct))
# error = tf.where(correct)


config_proto = tf.ConfigProto(allow_soft_placement=True)
config_proto.gpu_options.per_process_gpu_memory_fraction = 0.99
config_proto.gpu_options.visible_device_list = '0' ###################################################
config_proto.gpu_options.allow_growth = True
sess = tf.Session(config=config_proto)
sess.run(tf.global_variables_initializer())

mdir = '/home/ai/seria/model/res-e' ############################################################
if not os.path.exists(mdir):
    os.mkdir(mdir)


ckpt = tf.train.latest_checkpoint(mdir)
vars = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES)
# vars = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope=mdtype)
# vars = [v for v in vars if 'logits' not in v.name]
restorer = tf.train.Saver(vars)
restorer.restore(sess, ckpt)
# restorer.restore(sess, '/home/ai/seria/model/res-slim/%s.ckpt'%mdtype)


# saver = tf.train.Saver(tf.global_variables(), max_to_keep=1)
#
# epoch = 7
# mile = fd.milesPerEpoch(fname + '-ct')
# miles = epoch*mile+1
# monitor = np.zeros((100,))
# record_t = miles*[0]
# record_v = epoch*[0]
# for s in range(1):
#     batch = fd.nextBatch(fname + '-ct')
#     _, acc, loss = sess.run([sc.layout[optz], accuracy, cost],
#                             feed_dict={sc.layout['input']: batch['image'],
#                                        sc.layout['label']: batch['label'],
#                                        sc.layout['is_train']: True})
#     monitor[s % 100] = acc
#     avg = monitor.mean()
#     record_t[s] = avg*100
#     # import pdb
#     # pdb.set_trace()
#     if s % 50 == 0:
#         print('epoch #%d - %d miles acc: %.2f%%, loss: %.4f' %
#               (fd.currentEpoch(fname + '-ct'), s, acc * 100, loss))
#         if s % 200 == 0:
#             saver.save(sess, os.path.join(mdir,'res_n'), global_step=s, write_meta_graph=True) ##########################
#     if s>0 and s%fd.milesPerEpoch(fname + '-ct') == 0:
#         print(50 * '=')
#         acc_tot = 0
#         loss_tot = 0
#         steps = fd.milesPerEpoch(fname + '-cv')
#         for m in range(steps):
#             batch = fd.nextBatch(fname + '-cv')
#             acc, loss = sess.run([accuracy, cost], feed_dict={sc.layout['input']: 255*batch['image']-np.array([123.68, 116.779, 103.939]),
#                                                               sc.layout['label']: batch['label'],
#                                                               })
#             # import pdb
#             # pdb.set_trace()
#             # misc.imsave('/home/ai/seria/err.jpg', batch['image'][0])
#             acc_tot += acc
#             loss_tot += loss
#         print('epoch #%d: acc: %.2f%%, loss: %.4f' % (
#         fd.currentEpoch(fname + '-cv'), acc_tot / steps * 100, loss_tot / steps))
#         print(50 * '=')
#         record_v[fd.currentEpoch(fname + '-cv')-1] = acc_tot / steps * 100
# plt.switch_backend('agg')
# plt.plot(np.arange(miles), record_t, c='blue')
# plt.plot(np.arange(mile,miles,mile), record_v, c='red')
# plt.savefig(os.path.join(mdir,'curve.jpg'))
#
#
# fd.unloadFuel(fname + '-ct')
# fd.unloadFuel(fname + '-cv')


steps = fd.milesPerEpoch(fname + '-ct')
vec = np.zeros((40853,2048))
for m in range(steps):
    if m==steps-1:
        fd.editProperty(fname + '-ct', batch_size=21)
    batch = fd.nextBatch(fname + '-ct')
    feat = sess.run(feature, feed_dict={sc.layout['input']: batch['image'],
                                        sc.layout['is_train']: True})
    if m == steps - 1:
        vec[-21:] = feat
    else:
        vec[m * 32:(m + 1) * 32] = feat
hdf5 = h5py.File('/home/ai/seria/mxt.hdf5', 'w')
hdf5['train'] = vec
hdf5.close()

steps = fd.milesPerEpoch(fname + '-cv')
vec = np.zeros((4096,2048))
for m in range(steps):
    batch = fd.nextBatch(fname + '-cv')
    feat = sess.run(feature, feed_dict={sc.layout['input']: batch['image'],
                                        sc.layout['is_train']: True})
    vec[m * 32:(m + 1) * 32] = feat
hdf5 = h5py.File('/home/ai/seria/clv.hdf5', 'w')
hdf5['val'] = vec
hdf5.close()


steps = fd.milesPerEpoch(fname + '-test')
vec = np.zeros((19200,2048))
indices = np.zeros((19200,))
for m in range(steps):
    batch = fd.nextBatch(fname + '-test')
    idx,feat = sess.run([ind,feature], feed_dict={sc.layout['input']: batch['image'],
                                                  sc.layout['is_train']: True})
    indices[m * 32:(m + 1) * 32] = idx
    vec[m * 32:(m + 1) * 32] = feat
flist = os.listdir('/home/ai/challenge/test')
flist.remove('kpi18_test.csv')
with open('/home/ai/seria/liyuyulv.csv', 'w') as csvf:
    csvw = csv.writer(csvf)
    for i, f in enumerate(flist):
        csvw.writerow([f, str(indices[i] + 1)])
hdf5 = h5py.File('/home/ai/seria/test.hdf5', 'w')
hdf5['test'] = vec
hdf5.close()

fd.unloadFuel(fname + '-ct')
fd.unloadFuel(fname + '-cv')
fd.unloadFuel(fname + '-test')


# steps = fd.milesPerEpoch(fname + '-test')
# indices = np.zeros((19200,))
# for m in range(steps):
#     batch = fd.nextBatch(fname + '-test')
#     idx = sess.run(ind, feed_dict={sc.layout['input']: batch['image'],
#                                                       })
#     indices[m*32:(m+1)*32] = idx
# flist = os.listdir('/home/ai/challenge/test')
# flist.remove('kpi18_test.csv')
# with open('/home/ai/seria/liyuyulv.csv', 'w') as csvf:
#     csvw = csv.writer(csvf)
#     for i,f in enumerate(flist):
#         csvw.writerow([f,str(indices[i]+1)])
#
# fd.unloadFuel(fname + '-test')



# steps = fd.milesPerEpoch(fname + '-n')
# indices = []
# for m in range(steps):
#     batch = fd.nextBatch(fname + '-n')
#     err = sess.run(error, feed_dict={sc.layout['input']: batch['image'],
#                                    sc.layout['label']: batch['label'],
#                                      sc.layout['is_train']: True})
#     for e in err.flatten():
#         indices.append(e+m*50)
# flist = pd.read_csv('/home/ai/seria/kpi18_trn.csv', header=0)
# with open('/home/ai/seria/model/reliable.csv', 'w') as csvf:
#     csvw = csv.writer(csvf)
#     for i in indices:
#         csvw.writerow([flist.iloc[i,0], flist.iloc[i,1]])
#
# fd.unloadFuel(fname + '-n')
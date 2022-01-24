#!/usr/bin/env python
'''
setup
Created by Seria at 04/11/2018 10:50 AM
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

import setuptools

with open("Nebulae_Brochure.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nebulae",
    version="0.5.14",
    author="Seria",
    author_email="zzqsummerai@yeah.net",
    description="A novel and simple framework based on prevalent DL frameworks and other image processing libs."
                + " v0.5.14: add multi_piston argument for Engine;"
                + " now users need to receive returned object from gear().",
                # + " v0.5,13: add nworkers as an input argment for fuel tank;"
                # + " remove an unnecessary conversion in HWC2CHW.",
                # + " v0.5.12: add dissect() method in Craft for estimating model size and exporting architecture.",
                # + " v0.5.11: update SN implementation so that PyTorch Module works well to be wrapped;"
                # + " users can input 'optz' argument in TimeMachine to save optimizer states;"
                # + " tell DashBoard.log() where the history metric data are, it'll append to current datalog;"
                # + " in autoPad function, empty tuple and None are legal value for in_size if users make sure"
                # + " in_size can be divided by stride along all dimensions.",
                # + " v0.5.10: add keep_pos argument in OHEM.",
                # + " v0.5.9: add OHEM loss; users could turn up or down the flush argument in dashboard"
                # + " to control the refreshed lines on screen.",
                # + " v0.5.8: add SurPix module.",
                # + " v0.5.7: move multiverse from law to astrobase; add GPUtil for monitoring GPU status.",
                # + " v0.5.6: add back apex-based multi-gpu training for low version of PyTorch.",
                # + " v0.5.5: add SubPix module.",
                # + " v0.5.4: add PSNR and SSIM metrics; the default behavior of Upscale is corner aligned now.",
                # + " v0.5.3: add Recurrent networks module.",
                # + " v0.5.2: add 3 types of Graph Convolution block; add sparse-tensor-related methods.",
                # + " v0.5.1: correct implementation on applying weight decay and EMA module;"
                # + " add Retroact module for visualizing decisive map.",
                # + " v0.5.0: the latest version takes the Big Two mainstream frameworks as backends,"
                # + " and they share the same interfaces and arguments"
                # + " i.e. Pytorch and Tensorflow. It is convenient for everyone to create nerworks and train,"
                # + " no matter using single or multiple GPUs. Code blocks written in naive Pytorch or Tensorflow"
                # + " are allowed to mix with Nebulae to work together.",
                # + " v0.4.20: fix a crucial typo which results in installation failure.",
                # + " v0.4.19: mute redundant INFO in multi-process.",
                # + " v0.4.18: add prep_fn argument in Tank.",
                # + " v0.4.17: remove mxnet core; add tf2 core which is under test.",
                # + " v0.4.16: engine is now a required argument for initializing Craft, so does as_const for Engine.coat;"
                # + " add depot.Random to control if the comburant event is gonna happen.",
                # + " v0.4.15: set 'grad_accum' argument in optimizer to control gradient accumulations.",
                # + " v0.4.14: add BigGAN and EMA wrapper;"
                # + " reform weight initializers and lr decayors as Class instead of flags.",
                # + " v0.4.13: reimplement Multiverse using built-in pytorch function; add SoftPlus layer.",
                # + " v0.4.12: optimize the interface of Res-GAN.",
                # + " v0.4.11: add Identity, MatMul, Permute, Embed layers and supports SN-Embed;"
                # + " orthogonal initialization is added.",
                # + " v0.4.10: add epoch, mile and MPE as new input arguments of INVIZ item in dashboard.",
                # + " v0.4.9: fix an error if input of GAN is a gray image.",
                # + " v0.4.8: add SN (Spectral Norm) and SN-GAN.",
                # + " v0.4.7: fix a bug of getting available GPUs.",
                # + " v0.4.6: add Instance Norm layer; slight changes on resnetGAN.",
                # + " v0.4.5: reorganize hangar.",
                # + " v0.4.4: add ResnetV2 and varieties of GANs in hangar;"
                # + " change input arguments in pooling layers for better use of global pooling.",
                # + " v0.4.3: add VGG16 in hangar.",
                # + " v0.4.2: optimize distributed training using Multiverse.",
                # + " v0.4.1: mute in all subprocesses.",
                # + " v0.4.0: a brand new version is released. it is more compatible with the backend framework"
                # + " so as to ease pain for transplanting code.",
                # + " v0.3.2: update implementations of data augmentation;"
                # + " users can build spacecraft as many as need and manage them in a spacedock.",
                # + " v0.3.1: fix an unexpected error when miles in DashBoard starts from a number greater than 1;"
                # + " fix a bug that strings cannot be stored using fuel generator;"
                # + " users are able to wrap their model written in core framework as a component by inheriting from OffTheShelf;"
                # + " garage is replaced by hangar and GAN is added to it;"
                # + " update spatial data augmentation methods;",
                # + " v0.3.0: fix a catastrophic bug that brings wrong shaped components in network;"
                # + " add new attribute, info, in Pod to serve another new tool named Imperative Symbol;"
                # + " now users can indicate to Dense layer which axis is to be projected;"
                # + " core modules of PyTorch is integrated now.",
                # + "v0.2.6: fix a bug that returns available gpu ids more than need;"
                # + "move the weight decay term to correct device;",
                # + "v0.2.5: unify convolution functions in different dimensions.",
                # + "v0.2.4: add 'rescale' option in FuelDepot.loadFuel().",
                # + "v0.2.3: fix a bug would cause error when decode hdf5 file.",
                # + "v0.2.2: remove the functionality of param:ckpt_scope with mxnet core.",
                # + "v0.2.1: mute re-initialization warning with mxnet core; add new way to save&load models.",
                # + "v0.2.0: now tensorflow and mxnet cores are completely supported."
                # + "we patch so much of it, and it is easier to take almost every module as a stand-alone plug-in.",
                # + " v0.1.21: set complete_last_batch as True when loading fuel to keep the last batch in same size as others.",
                # + " v0.1.20: optimize the execution of shuffling data.",
                # + " v0.1.19: if users want to print their results in a flexible way, they can pass a tailor function to Dash Board.",
                # + " v0.1.18: if_shuffle is modifiable for fuel tank now.",
                # + " v0.1.17: set MPE, volume and epoch as properties in fuel depot;"
                # + " if nothing is assigned to name while calling unloadFuel and modify of fuel depot, every tank will be manipulated",
                # + " v0.1.16: shorten some function names e.g. 'milesPerEpoch' to 'getMPE', 'editProperty' to 'modify'.",
                # + " v0.1.15: move merge, fill and deduct functions from toolkit to fuel.",
                # + " v0.1.14: fix a bug in toolkit.toDenseLabel.",
                # + " v0.1.13: new argument num_gpus indicates how many gpus you need.",
                # + " v0.1.12: change the quoting character of label file to |;"
                # + " add fillFuel and deductFuel in toolkit;"
                # + " users can store data with variable length;"
                # + " reorganize the logic for assembling components.",
                # + " v0.1.11: rename LayoutSheet as BluePrint;"
                # + " change the initial parts of Space Craft and Navigator;"
                # + " merge log function in Aerolog as an interface exposed by Navigator.",
                # + " v0.1.10: make it simpler to use Dash Board module alone.",
                # + " v0.1.9: be able to remove EXIF without modifying raw images.",
                # + " v0.1.7: users can generate hdf5 as several files since generating large dataset at once is risky;"
                # + " In addition, mergeFuel function is provided for merging multiple hdf5 files;"
                # + " users can remove EXIF in images while generating data file by setting keep_exif as False.",
                # + " v0.1.6: add SE Resnets to Garage;"
                # + " read image in RGB mode of which number of channel is 3.",
                # + " v0.1.5: fix a bug would return wrong device id when looking for available gpu.",
                # + " v0.1.1: change the way to register stage;"
                # + " fix a bug in DashBoard may draw points in wrong places.",
                # + " v0.1.0: A roughly complete version. New parts, Engine, Time Machine, Dashboard and Navigator are added.",
                # + " v0.0.18: fix a bug would repeatedly append variable scope.",
                # + " v0.0.17: network layout will be saved as image instead of pdf;"
                # + " add components: RESHAPE, SLICE, CLIP;"
                # + " implement Time Machine.",
                # + " v0.0.15: fix a bug would lead to wrong implementation of ** symbol."
                # + " v0.0.14: unable to assemble DUPLICATE component without name but passing existent name is allowed."
                # + " v0.0.13: allow users to assemble DUPLICATE component without passing name;"
                # + " add RESIZE component;"
                # + " shorten automatically generated component names."
                # + " v0.0.12: fix wrong implementation on data augmentation;"
                # + " FuelGenerator will keep original image size if width or height is not given.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/",
    packages=setuptools.find_packages(),
    install_requires=
    ['graphviz',
     'h5py',
     'pillow',
     'pandas',
     'piexif',
     'scipy',
     'matplotlib',
     'onnx',
     'tf2onnx',
     'tensorflow-probability',
     'tensorflow-addons',
     'protobuf>=3.13',
     'numpy<1.19',
     'torch>=1.0'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
import unittest
import reliefcpp
import numpy as np
from mnist import MNIST
import matplotlib.pyplot as plt

if __name__ == "__main__":
    mndata = MNIST('../data')
    images, labels = mndata.load_training()
    images, labels = np.array(images), np.array(labels).astype(int)

    # images = images[(labels == 6) | (labels == 5)]
    images = images / 255
    # labels = labels[(labels == 6) | (labels == 5)]
    rr = reliefcpp.ReliefF(1000)
    print(images.shape, labels.shape)

    rr.fit(images, labels)

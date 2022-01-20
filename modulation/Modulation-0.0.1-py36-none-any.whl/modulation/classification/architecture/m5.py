#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 18-11-2020
           """

__all__ = ["M5"]

import torch


class M5(torch.nn.Module):
    """
    M5 network architecture
    described in `this paper <https://arxiv.org/pdf/1610.00087.pdf>`__. An
    important aspect of models processing raw audio data is the receptive
    field of their first layer’s filters. The model’s first filter is length
    80 so when processing audio sampled at 8kHz the receptive field is
    around 10ms (and at 4kHz, around 20 ms). This size is similar to speech
    processing applications that often use receptive fields ranging from
    20ms to 40ms.
    """

    def __init__(self, n_input=1, n_output=35, stride=16, n_channel=32):
        super().__init__()

        self.conv1 = torch.nn.Conv1d(n_input, n_channel, kernel_size=80, stride=stride)
        self.bn1 = torch.nn.BatchNorm1d(n_channel)
        self.pool1 = torch.nn.MaxPool1d(4)

        self.conv2 = torch.nn.Conv1d(n_channel, n_channel, kernel_size=3)
        self.bn2 = torch.nn.BatchNorm1d(n_channel)
        self.pool2 = torch.nn.MaxPool1d(4)

        self.conv3 = torch.nn.Conv1d(n_channel, 2 * n_channel, kernel_size=3)
        self.bn3 = torch.nn.BatchNorm1d(2 * n_channel)
        self.pool3 = torch.nn.MaxPool1d(4)

        self.conv4 = torch.nn.Conv1d(2 * n_channel, 2 * n_channel, kernel_size=3)
        self.bn4 = torch.nn.BatchNorm1d(2 * n_channel)
        self.pool4 = torch.nn.MaxPool1d(4)

        self.fc1 = torch.nn.Linear(2 * n_channel, n_output)

    def forward(self, x):
        x = torch.relu(self.bn1(self.conv1(x)))
        x = torch.relu(self.bn2(self.conv2(self.pool1(x))))
        x = torch.relu(self.bn3(self.conv3(self.pool2(x))))
        x = torch.relu(self.bn4(self.conv4(self.pool3(x))))
        x = self.pool4(x)

        x = torch.avg_pool1d(x, x.shape[-1])

        return torch.log_softmax(self.fc1(x.permute(0, 2, 1)), dim=2)

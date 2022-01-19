#!/usr/bin/env python3
# coding: UTF-8

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def main():
    data = pd.read_csv('peopleconvicted.csv') #csvデータ読み込み
    # print(data)

    India = data.loc[12]
    India2 = India[1:12]


    India2.plot(kind='bar', color=['blue','blue','blue','red','blue','blue','blue','blue','red','blue','blue'])
    plt.title('Iidia', fontsize='xx-large')
    plt.show()

if __name__ == '__main__':
    main()
# 著作者：叶凯文
# Author: YE KAIWEN
# 版权归著作者叶凯文所有
# Copyright (c) 2022 YE KAIWEN. All Rights Reserved.

from valuequant.VQconnect import VQC
import valuequant.Models as Models
import valuequant.ModelSets as ModelSets
import valuequant.StockModels as StockModels
import valuequant.StockModelSets as StockModelSets
import valuequant.StockFrameSets as StockFrameSets

def login(name,pswd):
    VQC.login(name,pswd)

def logout():
    VQC.logout()



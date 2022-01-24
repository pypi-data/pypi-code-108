# 快捷键判断
# 创建人：曾逸夫
# 创建时间：2022-01-04

import sys


# 判断快捷键是否冲突
def hotkey_judge(keyList):
    for i in range(len(keyList)):
        tmp_key = keyList[i]  # 临时快捷键
        for j in range(len(keyList[i+1:])):
            if (tmp_key == keyList[i+1:][j]):
                print(f'快捷键冲突! 程序结束！')
                sys.exit()  # 结束程序

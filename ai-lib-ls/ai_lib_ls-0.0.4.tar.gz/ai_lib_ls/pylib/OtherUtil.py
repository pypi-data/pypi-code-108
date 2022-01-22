

#将表格里面数据转化为数组或者string
def for_arr_str():
    key_str = 'pixel'
    arrStr = [f'{key_str}{i}' for i in range(784)] # 通过for循环生成所有数据
    sss = ','.join(arrStr)  #将生成的数据转换为String
    return







if __name__ == "__main__":
    key_str = 'pixel'
    arrStr = [f'{key_str}{i}' for i in range(784)]
    sss = ','.join(arrStr)
    print(sss)

    pass
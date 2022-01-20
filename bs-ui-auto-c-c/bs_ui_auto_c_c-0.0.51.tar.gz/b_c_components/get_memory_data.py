
import ctypes


def get_memory_data(memory_id):
    """
    return: 根据在内存中获取数据并返回
    """
    return ctypes.cast(int(memory_id), ctypes.py_object).value

# 140215463389648
# _*_coding     : UTF_8_*_
# Author        :Jie Shen
# CreatTime     :2022/1/25 10:23
from collections import deque
from typing import List


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build_by_order():
    """
    按顺序添加左右孩子
    :return:
    """
    pass


def sortedArrayToBST(nums: List[int]):
    """
    从一个升序数组创建平衡二叉搜索树
    108. 将有序数组转换为二叉搜索树: https://leetcode-cn.com/problems/convert-sorted-array-to-binary-search-tree/
    :param nums: 
    :return: 
    """
    pass


def print_TreeNode(root: TreeNode):
    order = levelOrder(root)
    print(order)


def levelOrder(root: TreeNode) -> List[List[int]]:
    res = []
    q = deque()
    if root is not None:
        q.append(root)
    while q:
        Size = len(q)
        tmp = []
        # 记录这层的所有node
        while Size > 0:
            Size -= 1
            node = q.popleft()
            if node is None:
                tmp.append(None)
                continue
            tmp.append(node.val)
            q.append(node.left)
            q.append(node.right)
            # if node.left is not None:
            #     q.append(node.left)
            # if node.right is not None:
            #     q.append(node.right)
        res.append(tmp)
    return res

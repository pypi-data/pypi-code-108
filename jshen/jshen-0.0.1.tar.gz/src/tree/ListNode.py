# _*_coding     : UTF_8_*_
# Author        :Jie Shen
# CreatTime     :2022/1/17 20:53

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class BuildTree:

    def __init__(self):
        pass

    def build_by_array(self, arr) -> ListNode:
        if arr is None or len(arr) == 0:
            return None
        head = ListNode(arr[0])
        node = head
        for _ in range(1, len(arr)):
            node.next = ListNode(arr[_])
            node = node.next
        return head


def print_node(head: ListNode):
    print("node:", end="")
    if head is None:
        print(None)
        return
    while head is not None:
        print(head.val, end=",")
        head = head.next
    print()


if __name__ == '__main__':
    arr = [1, 2, 3]
    b = BuildTree().build_by_array(arr)
    print_node(b)

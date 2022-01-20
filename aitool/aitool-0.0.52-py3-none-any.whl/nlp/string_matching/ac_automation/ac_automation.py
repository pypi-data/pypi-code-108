# -*- coding: UTF-8 -*-
# Copyright©2020 xiangyuejia@qq.com All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""

"""
from typing import Dict, Tuple, Union, List, Iterator, Any, NoReturn

__all__ = ['Ahocorasick', ]


class Node(object):

    def __init__(self):
        self.next = {}
        self.fail = None
        self.isWord = False


class Ahocorasick(object):

    def __init__(self):
        self.__root = Node()

    def addWord(self, word):
        '''
            @param word: add word to Tire tree
                            添加关键词到Tire树中
        '''
        tmp = self.__root
        for i in range(0, len(word)):
            if word[i] not in tmp.next:
                tmp.next[word[i]] = Node()
            tmp = tmp.next[word[i]]
        tmp.isWord = True

    def make(self):
        '''
            build the fail function
            构建自动机，失效函数
        '''
        tmpQueue = []
        tmpQueue.append(self.__root)
        while (len(tmpQueue) > 0):
            temp = tmpQueue.pop()
            p = None
            for k, v in temp.next.items():
                if temp == self.__root:
                    temp.next[k].fail = self.__root
                else:
                    p = temp.fail
                    while p is not None:
                        if k in p.next:
                            temp.next[k].fail = p.next[k]
                            break
                        p = p.fail
                    if p is None:
                        temp.next[k].fail = self.__root
                tmpQueue.append(temp.next[k])

    def search(self, content):
        '''
            @return: a list of tuple,the tuple contain the match start and end index
        '''
        p = self.__root
        result = []
        startWordIndex = 0
        endWordIndex = -1
        currentPosition = 0

        while currentPosition < len(content):
            word = content[currentPosition]
            # 检索状态机，直到匹配
            while word not in p.next and p != self.__root:
                p = p.fail

            if word in p.next:
                if p == self.__root:
                    # 若当前节点是根且存在转移状态，则说明是匹配词的开头，记录词的起始位置
                    startWordIndex = currentPosition
                # 转移状态机的状态
                p = p.next[word]
            else:
                p = self.__root

            if p.isWord:
                # 若状态为词的结尾，则把词放进结果集
                result.append((startWordIndex, currentPosition))

            currentPosition += 1
        return result

    def replace(self, content):
        replacepos = self.search(content)
        result = content
        for i in replacepos:
            result = result[0:i[0]] + (i[1] - i[0] + 1) * u'*' + content[i[1] + 1:]
        return result


def show(text, patterns):
    ah = Ahocorasick()
    words = patterns.split(" ")
    for w in words:
        ah.addWord(w)
    ah.make()
    results = ah.search(text)
    print(results)
    if len(results) == 0:
        print("No find.")
    else:
        print(len(results), " matching results are listed below.")
        print("-------" + "-" * len(text) + "-------")
        print(text)
        count = 0
        for site in results:
            w = text[site[0]:site[1] + 1]
            count += 1
            print(" " * site[0] + w + " " * (len(text) - site[1]) + "  " + str(site[0]) + "  " + str(count))
        print("-------" + "-" * len(text) + "-------")


if __name__ == '__main__':
    show(
        text='a his hoge hershe xx.',
        patterns='he hers his she'
    )

    # TODO 这个测试用例有问题，没识别出he
    show(
        text='ushers',
        patterns='he hers his she'
    )

#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description:       :
@Date               :2021/02/07 11:46:35
@Author             :mayq
@version            :1.0
'''
import re
class Sent_tool:
    def __init__(self):
        pass
    # https://www.cnblogs.com/aloiswei/p/11679625.html
    @staticmethod
    def __merge_symmetry(sentences, symmetry=('“', '”')):
        '''合并对称符号，如双引号'''
        effective_ = []
        merged = True
        for index in range(len(sentences)):
            if symmetry[0] in sentences[index] and symmetry[1] not in sentences[index]:
                merged = False
                effective_.append(sentences[index])
            elif symmetry[1] in sentences[index] and not merged:
                merged = True
                effective_[-1] += sentences[index]
            elif symmetry[0] not in sentences[index] and symmetry[1] not in sentences[index] and not merged:
                effective_[-1] += sentences[index]
            else:
                effective_.append(sentences[index])

        return [i.strip() for i in effective_ if len(i.strip()) > 0]

    @staticmethod
    def to_sentences(paragraph):
        """由段落切分成句子"""
        sentences = re.split(r"(？|。|！|\…\…)", paragraph)
        sentences.append("")
        sentences = ["".join(i) for i in zip(sentences[0::2], sentences[1::2])]
        sentences = [i.strip() for i in sentences if len(i.strip()) > 0]

        for j in range(1, len(sentences)):
            if sentences[j][0] == '”':
                sentences[j - 1] = sentences[j - 1] + '”'
                sentences[j] = sentences[j][1:]

        return Sent_tool.__merge_symmetry(sentences)

def test():
    para ='''
我心里暗笑他的迂；他们只认得钱，托他们只是白托!而且我这样大年纪的人，难道还不能料理自己么？唉，我现在想想，那时真是太聪明了!
我说道：“爸爸，你走吧。”他往车外看了看说：“我买几个橘子去。你就在此地，不要走动。”我看那边月台的栅栏外有几个卖东西的等着顾客。走到那边月台，须穿过铁道，须跳下去又爬上去。
          '''
    
    res = Sent_tool.to_sentences(paragraph = para)
    [print(r) for r in res]

if __name__ == "__main__":
    test()
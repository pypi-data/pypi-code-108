# -*- coding:utf-8 -*-
import numpy as np
from bert_text_pretty import cls,ner,relation,tokenization

'''
    简化文本特征化，解码，当前ner为crf 解码
    https://github.com/ssbuild/bert_text_pretty.git
'''


text_list = ["你是谁123456","你是谁123456222222222222"]


tokenizer = tokenization.FullTokenizer(vocab_file=r'F:\pretrain\chinese_L-12_H-768_A-12\vocab.txt',do_lower_case=True)

feat = cls.cls_text_feature(tokenizer,text_list,max_seq_len=128,with_padding=False)
print(feat)

feat = ner.ner_text_feature(tokenizer,text_list,max_seq_len=128,with_padding=False)
print(feat)

feat = relation.re_text_feature(tokenizer,text_list,max_seq_len=128,with_padding=False)
print(feat)


labels = ['标签1','标签2']
print(cls.load_labels(labels))

print(ner.load_label_bio(labels))


# logits 为bert 预测结果
# ner.ner_decoding(text_list,labels,logits,trans=None)

# ner 是否启用trans预测
#text_list 文本list , labels id2label list,logits 2D or 3D , trans 2D
#ner.ner_decoding(text_list,labels,logits,trans)


# logits 为bert 预测结果
# cls.cls_decoding(text_list,labels,logits)

# cls.cls_decoding(text_list,labels,logits)

# relation.re_decoding(example_all, id2spo, logits_all)



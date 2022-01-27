#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : sim_app
# @Time         : 2021/9/1 下午2:45
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *

from bertzoo.simbert2vec import Simbert2vec
from gensim.models import KeyedVectors

model = KeyedVectors.load_word2vec_format("vecs.txt", no_header=True)

s2v = Simbert2vec('chinese_roformer-sim-char-ft_L-6_H-384_A-6')


@lru_cache()
def text2vec(text='年收入'):
    return s2v.encoder([text], output_dim=None)[0]


def func(**kwargs):
    text = kwargs.get('text', '年收入').strip()
    topn = int(kwargs.get('topn', 10))
    _ = model.similar_by_vector(text2vec(text))
    return dict(_)


if __name__ == '__main__':
    from appzoo import App

    app = App()
    app.add_route('/sim', func, method="GET", version="demo")
    app.run(port=9955, debug=False, reload=False)

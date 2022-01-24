# -*- coding:utf-8 -*-
# CREATED BY: bohuai jiang 
# CREATED ON: 2020/8/13 3:55 PM
# LAST MODIFIED ON:
# AIM:
from sentence_spliter_old.automata import condition, operation
from sentence_spliter_old.automata.state_machine import StateMachine
import attrdict
import matplotlib.pyplot as plt
import time
from sentence_spliter_old.automata.sequence import StrSequence



options = {
        'language': 'zh',  # 'zh'中文 'en' 英文
        'long_short_sent_handle': 'y',  # 'y'自然切分，不处理长短句；'n'处理长短句
        'max_length': 5,  # 最长句子，默认值150
        'min_length': 2,  # 最短句子，默认值15
        'hard_max_length': 5,  # 强制截断，默认值300
        'remove_blank': True
    }


Edges = attrdict.AttrDict({
    'is_end_symbol': condition.IsEndSymbolCN(),
    'is_bracket_close': condition.IsBracketClose(),
    'is_book_close': condition.IsBookClose(),
    'is_quote_close': condition.IsQuoteClose(),
    'is_end_state': condition.IsEndState(),
    'is_long_sentence': condition.IsLongSentence(max_len=options['max_length']),
    'is_short_sentence': condition.IsShortSentence(min_len=options['min_length'])
})

Nodes = attrdict.AttrDict({
    'do_cut': operation.Normal(),
    'long_handler': operation.LongHandler(hard_max=options['hard_max_length']),
    #'short_handler': operation.ShortHandler(),
    'init': operation.Indolent(),
    'end': operation.EndState()
})

logic_simple = {
    Nodes.init: [
        {'edge': Edges.is_end_state,
         'node': Nodes.end},

        {'edge': [
                  Edges.is_end_symbol,
                  Edges.is_book_close,
                  Edges.is_bracket_close,
                  Edges.is_quote_close
            ],
         'args': all,
         'node': Nodes.do_cut},

        {'edge': None,
         'node': Nodes.do_cut},
    ],
    Nodes.do_cut: [
        {'edge': Edges.is_end_state,
         'node': Nodes.end},

        {'edge': None,  # else 状态
         'node': Nodes.init},
    ],
}

logic_graph = {
    Nodes.init: [
        {'edge': Edges.is_end_state,
         'node': Nodes.end},

        {'edge': Edges.is_short_sentence,
         'node': Nodes.init},

        {'edge': Edges.is_long_sentence,
         'node': Nodes.long_handler},


        {'edge': [Edges.is_end_symbol,
                  Edges.is_bracket_close,
                  Edges.is_book_close,
                  Edges.is_quote_close],
         'args': all,
         'node': Nodes.do_cut},



    ],
    Nodes.do_cut: [
        {'edge': Edges.is_end_state,
         'node': Nodes.end},

        {'edge': None,  # else 状态
         'node': Nodes.init},
    ],
    Nodes.long_handler: [
        {'edge': Edges.is_end_state,
         'node': Nodes.end},

        {'edge': None,  # else 状态
         'node': Nodes.do_cut},
    ]
}


def check(options, sentence_list) -> bool:
    for sentence in sentence_list:
        if not ( len(sentence) <= options['max_length']):
            print(sentence)
            return False
    else:
        return True


def run_single(sample_size=1):
    sentence = '(太阳当空照.).(花儿对我笑)，"小鸟说早早《哈哈哈！》!"，"你为什么背上书包了,".我去上学校,天天不迟到，爱学习爱劳.' * sample_size
    #machine = StateMachineZH(logic_simple)
    machine = StateMachine(logic_graph)
    start_t = time.time()
    state = StrSequence(sentence, False)
    machine.run(state,verbose=False)
    end_t = time.time() - start_t
    return end_t, state.sentence_list


def test(options):
    time = []
    size = []
    for i in range(1000, 1000000, 1000):
        t, out = run_single(i)
        # if not check(options, sentence_list=out):
        #     raise Exception('分句错误')
        time.append(t)
        size.append(i)
        if i % 100 == 0:
            print(i)
            plt.figure()
            plt.plot(time)
            plt.savefig('perform')
            plt.close()
    #print('\n'.join(out))


if __name__ == '__main__':

     test(options)
    # run_single()

# -*- coding:utf-8 -*-
# CREATED BY: jiangbohuai
# CREATED ON: 2021/4/26 6:28 PM
# LAST MODIFIED ON:
# AIM:
import unittest
from sentence_spliter_old.spliter import long_machine_en, cut_to_sentences_en
from sentence_spliter_old.logic_graph_en import long_cuter_en
from sentence_spliter_old.automata.sequence import EnSequence
from sentence_spliter_old.automata.state_machine import StateMachine


# from sentence_spliter.logic_graph_en import


class test_file(unittest.TestCase):
    # @unittest.skip('pass')
    def test_white_list(self):
        with open('file.txt', 'r') as f:
            sentence = f.read()
        m_input = EnSequence(sentence)
        StateMachine(long_cuter_en()).run(m_input)
        expected = m_input.sentence_list()

        print('\n'.join(expected))
        print('\n\n\n')
        for i in range(3):
            m_input = EnSequence(sentence)
            StateMachine(long_cuter_en()).run(m_input)
            out = m_input.sentence_list()
            print('\n'.join(out))
            self.assertEqual(expected, out)

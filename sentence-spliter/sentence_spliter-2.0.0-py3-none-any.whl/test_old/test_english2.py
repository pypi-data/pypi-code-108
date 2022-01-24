# -*- coding:utf-8 -*-
# CREATED BY: jiangbohuai
# CREATED ON: 2021/4/15 4:52 PM
# LAST MODIFIED ON:
# AIM:

import unittest
from sentence_spliter_old.logic_graph_en import long_cuter_en
from sentence_spliter_old.automata.sequence import EnSequence
from sentence_spliter_old.automata.state_machine import StateMachine


class test_spliter(unittest.TestCase):
    # @unittest.skip('pass')
    def test_bug_2021_4_15(self):
        paragraph = "five sisters and a cousin. And when the party entered the assembly room it consisted of only five altogether-Mr. Bigley, his two sisters, the husband of the eldest, and another you man."

        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ['five sisters and a cousin. And when the party entered the assembly room it '
                  'consisted of only five altogether-Mr. Bigley,',
                  ' his two sisters, the husband of the eldest, and another you man.']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_15_1(self):
        paragraph = "While there are many ways of improving time management — such as writing a schedule, prioritizing, adjusting your sleeping patterns, and downloading productivity apps — if you don't fully understand why time management is improtant, you may not have the motivation to change."
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ['While there are many ways of improving time management —',
                  ' such as writing a schedule, prioritizing, adjusting your sleeping patterns, '
                  'and downloading productivity apps —',
                  " if you don't fully understand why time management is improtant, you may not "
                  'have the motivation to change.']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_15_2(self):
        paragraph = "On one occasion, an employee was passed over for a management position because this individual left " \
                    "work every day at exactly 5:00 p.m. - not 5:01 p.m. or 5:02 p.m. Regardless of what was going on or " \
                    "what deadline was looming, the employee refused to stay one minute past 5:00 p.m. However, the other managers " \
                    "at the organization rarely left work on time, and if they did, they would often continue working when they arrived at home."
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ['On one occasion, an employee was passed over for a management position '
                  'because this individual left work every day at exactly 5:00 p.m. - not 5:01 '
                  'p.m. or 5:02 p.m. Regardless of what was going on or what deadline was '
                  'looming,',
                  ' the employee refused to stay one minute past 5:00 p.m. However, the other '
                  'managers at the organization rarely left work on time,',
                  ' and if they did, they would often continue working when they arrived at '
                  'home.']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_15_3(self):
        paragraph = "embattled we are-- but a call to bear the burden of a long twilight struggle, year in and year out,\"rejoicing in hope, " \
                    "patient in tribulation\"--a struggle against the common enemies of man: tyranny, poverty, disease and war itslef."
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ['embattled we are-- but a call to bear the burden of a long twilight '
                  'struggle, year in and year out,',
                  '"rejoicing in hope, patient in tribulation"--a struggle against the common '
                  'enemies of man: tyranny, poverty, disease and war itslef.']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_15_4(self):
        paragraph = "'\"I thought it too, when I went off watch\"--we was standing six hours on and six off--\"but the boys told me," \
                    " \" I says, \" thata the raft didn't seem to hardly move, for the last hour,\" says I, \"thought she's a slipping along all right, now,\""
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ['\'"I thought it too, when I went off watch"--',
                  'we was standing six hours on and six off--',
                  '"but the boys told me, " I says,',
                  ' " thata the raft didn\'t seem to hardly move, for the last hour," says I, '
                  '"thought she\'s a slipping along all right, now,"']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_15_5(self):
        paragraph = "Adiminstration in Wshington, D.C. To me the office of the Vice Presidency of the United States is a great office, " \
                    "and I feel that the people have got to have confidence in the integrity if the men who run."
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ['Adiminstration in Wshington, D.C. To me the office of the Vice Presidency of '
                  'the United States is a great office,',
                  ' and I feel that the people have got to have confidence in the integrity if '
                  'the men who run.']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_16(self):
        paragraph = "Job seekers are misusing the Internet by relying too much on its networks and forgetting there is " \
                    "less room for rejection when meeting with someone in person (no unanswered e-mails, for example). " \
                    "\"Go to at least two or three meetups a month, and bring business cards and introduce yourself to " \
                    "random people,\" said Strom. \"Don't be shy, even if you aren't the most outgoing person, " \
                    "talk to one or two strangers at these meetups, and see if you can find common ground.\""
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ['Job seekers are misusing the Internet by relying too much on its networks '
                  'and forgetting there is less room for rejection when meeting with someone in '
                  'person (no unanswered e-mails,',
                  ' for example). "Go to at least two or three meetups a month, and bring '
                  'business cards and introduce yourself to random people," said Strom.',
                  ' "Don\'t be shy, even if you aren\'t the most outgoing person, talk to one '
                  'or two strangers at these meetups, and see if you can find common ground."']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_16_1(self):
        paragraph = "'“O God, 1231231 233123 make me good, but not yet”?' go go go go go go go"
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=10))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ["'“O God, 1231231 233123 make me good, but not yet”?' ",
                  'go go go go go go go']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_16_2(self):
        paragraph = "‘“O God, 1231231 233123 make me good, but not yet”?’ go go go go go go go"
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=10))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ["‘“O God, 1231231 233123 make me good, but not yet”?’ ",
                  'go go go go go go go']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_26(self):
        paragraph = " 'Do you mean to say, child, that any human being has gone into a Christian church, and got herself named Peggotty?' 'It's her surname,' said my mother, faintly."
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = [
            " 'Do you mean to say, child, that any human being has gone into a Christian church, and got herself named Peggotty?' ",
            "'It's her surname,' said my mother, faintly."]
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_29(self):
        paragraph = "(Do you mean to say, child, that any human being has gone into a Christian church, and got herself named Peggotty?) It's her surname, said my mother, faintly."
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=21))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ['(Do you mean to say, child, that any human being has gone into a Christian '
                  'church, and got herself named Peggotty?)',
                  " It's her surname, said my mother, faintly."]
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_29_1(self):
        paragraph = " ' Do you mean to say, child, that any human being has gone' into a Christian church, and got herself named Peggotty?"
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=15))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = [" ' Do you mean to say, child, that any human being has gone' ",
                  'into a Christian church, and got herself named Peggotty?']
        self.assertEqual(expect, acutal)

        paragraph = " ' Do you mean to say, child, that any human being has gones' into a Christian church, and got herself named Peggotty?"
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=15))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = [" ' Do you mean to say, child, that any human being has gones' into a "
                  'Christian church,',
                  ' and got herself named Peggotty?']
        self.assertEqual(expect, acutal)

# -*- coding:utf-8 -*-
# CREATED BY: jiangbohuai
# CREATED ON: 2021/1/21 4:20 PM
# LAST MODIFIED ON:
# AIM:

import unittest
from sentence_spliter_old.spliter import cut_to_sentences_en
from sentence_spliter_old.logic_graph_en import long_cuter_en
from sentence_spliter_old.automata.sequence import EnSequence
from sentence_spliter_old.automata.state_machine import StateMachine


class test_spliter(unittest.TestCase):
    # @unittest.skip('pass')
    def test_white_list(self):
        sentence = "He was a private in the U. S. Army."
        out = cut_to_sentences_en(sentence)
        expected = ["He was a private in the U. S. Army."]
        self.assertEqual(expected, out)

        # sentence = "He was a private in the U.S. Army. AHAH!"
        # out = cut_to_sentences_en(sentence)
        # expected = ['He was a private in the U.S. Army.', ' AHAH!']
        # self.assertEqual(expected, out)
        #
        # sentence = "Notice that U.S.A. can also be written USA, but U.S. is better with the periods. Also, we can use U.S. as a modifier (the U.S. policy on immigration) but not as a noun (He left the U.S. U.S.A.)."
        # out = cut_to_sentences_en(sentence)
        # expected = ['Notice that U.S.A. can also be written USA, but U.S. is better with the '
        #             'periods.',
        #             ' Also, we can use U.S. as a modifier (the U.S. policy on immigration)',
        #             ' but not as a noun (He left the U.S. U.S.A.).']
        # self.assertEqual(expected, out)
        #
        # sentence = "U.S.A is the ency of the world"
        # out = cut_to_sentences_en(sentence)
        # expected = ['U.S.A is the ency of the world']
        # self.assertEqual(expected, out)
        # sentence = "Notice that U.S.A. can also be written USA."
        # out = cut_to_sentences_en(sentence)
        # expected = ["Notice that U.S.A. can also be written USA."]
        # self.assertEqual(expected, out)
        #
        # sentence = "Notice that U.S.A. can also be written USA, but U.S. is better with the periods. Also, we can use U.S. as a modifier (the U.S. policy on immigration) but not as a noun (He left the U.S. U.S.A.)."
        # out = cut_to_sentences_en(sentence)
        # expected = ['Notice that U.S.A. can also be written USA, but U.S. is better with the '
        #             'periods.',
        #             ' Also, we can use U.S. as a modifier (the U.S. policy on immigration)',
        #             ' but not as a noun (He left the U.S. U.S.A.).']
        # self.assertEqual(expected, out)
        #
        # sentence = "Mrs. Gibson, meanwhile, counting her stitches aloud with great distinctness and vigour."
        # out = cut_to_sentences_en(sentence)
        # expected = ["Mrs. Gibson, meanwhile, counting her stitches aloud with great distinctness and vigour."]
        # self.assertEqual(expected, out)
        #
        # sentence = "Dr. Who and Who Dr. aren't same person."
        # out = cut_to_sentences_en(sentence)
        # expected = ["Dr. Who and Who Dr. aren't same person."]
        # self.assertEqual(expected, out)

        # sentence = ""

    # @unittest.skip('pass')
    def test_bracket_quota(self):
        sentence = ' "keep forawrd !!", said he. (but he already tired..)'
        out = cut_to_sentences_en(sentence)
        expected = [' "keep forawrd !!", said he. (but he already tired..)']
        self.assertEqual(expected, out)

        sentence = '“Which, if true, will have been recorded in the muster returns. Does it require a general to inspect the books? A clerk could do that.”'
        out = cut_to_sentences_en(sentence)
        expected = [
            '“Which, if true, will have been recorded in the muster returns. Does it require a general to inspect the books? A clerk could do that.”']
        self.assertEqual(expected, out)

    # @unittest.skip('pass')
    def test_dialogue(self):
        sentence = '"you are all lying !" "I am won!!!","Joe, you know I won!!!"'
        out = cut_to_sentences_en(sentence)
        expected = ['"you are all lying !" "I am won!!!","Joe, you know I won!!!"']
        self.assertEqual(expected, out)

        sentence = '"you are all lying !""I am won!!!","Joe, you know I won!!!"'
        out = cut_to_sentences_en(sentence)
        expected = ['"you are all lying !""I am won!!!","Joe, you know I won!!!"']
        self.assertEqual(expected, out)

        sentence = '"you are all lying lying lying and lying!"     "I am won!!!","Joe, you know I won!!!"'
        out = cut_to_sentences_en(sentence)
        expected = ['"you are all lying lying lying and lying!"     ', '"I am won!!!","Joe, you know I won!!!"']
        self.assertEqual(expected, out)

        sentence = '"you are all lying lying lying and lying!""I am won!!!","Joe, you know I won!!!"'
        out = cut_to_sentences_en(sentence)
        expected = ['"you are all lying lying lying and lying!"', '"I am won!!!","Joe, you know I won!!!"']
        self.assertEqual(expected, out)

        sentence = '“This presupposes that you have disposed of the enemy’s shore battery?” “It does, sir.” “A joint attack, eh?”'
        out = cut_to_sentences_en(sentence)
        expected = ['“This presupposes that you have disposed of the enemy’s shore battery?” ',
                    '“It does, sir.” “A joint attack, eh?”']
        self.assertEqual(expected, out)

    # @unittest.skip('pass')
    def test_short_stence(self):
        sentence = '1. 2 3 4. 1 2 3 4 5 6. 1 2 3 4 5 6 7 8.'
        out = cut_to_sentences_en(sentence)
        expected = ['1. 2 3 4. 1 2 3 4 5 6.', ' 1 2 3 4 5 6 7 8.']
        self.assertEqual(expected, out)

    # @unittest.skip('pass')
    def test_long_cutter(self):
        # __long_machine_en = StateMachine(long_cuter_en(max_len=9))
        #
        # sentence = '"1 2 3 4 5 6 7?" cried Henry'
        # m_input = EnSequence(sentence)
        # __long_machine_en.run(m_input)
        # out = m_input.sentence_list()
        # m_input.sentence_list()
        # expected = ['"1 2 3 4 5 6 7?"', ' cried Henry']
        # self.assertEqual(expected, out)
        #
        # sentence = '1 3 5 6 7 8 9 10, where 1 2 3 4.'
        # m_input = EnSequence(sentence)
        # __long_machine_en.run(m_input)
        # out = m_input.sentence_list()
        # m_input.sentence_list()
        # expected = ['1 3 5 6 7 8 9 10, ', 'where 1 2 3 4.']
        # self.assertEqual(expected, out)

        sentence = "\"What would a stranger do here, Mrs. Price?\" he inquired angrily, remembering, with a pang, that certain new, unaccountable, engrossing emotions had quite banished Fiddy from his thoughts and notice, when he might have detected the signs of approaching illness, met them and vanquished them before their climax."
        __long_machine_en = StateMachine(long_cuter_en(max_len=9, min_len=3))
        m_input = EnSequence(sentence)
        __long_machine_en.run(m_input)
        for v in m_input.sentence_list():
            print(v)

    # @unittest.skip('pass')
    def test_sample2(self):
        # sentence = '. . . . We now commend you to the Supream being Sincerely praying him to preserve you and the Forces under your Command in health and safety, & Return you Crowned with Victory and Laurels.'
        #
        # out = cut_to_sentences_en(sentence)
        # for v in out:
        #     print(v + "\n")

        sentence = '978-0-06-196963-8 EPub Edition © 2010 ISBN: 9780062013842 10 11 12 13 14 OFF/RRD 10 9 8 7 6 5 4 3 2 1 About the Publisher Australia HarperCollins Publishers (Australia) Pty. Ltd. 25 Ryde Road (PO Box 321) Pymble, NSW 2073, Australia http://www.harpercollinsebooks.com.au Canada HarperCollins Canada 2 Bloor Street East - 20th Floor Toronto, ON, M4W, 1A8, Canada http://www.harpercollinsebooks.ca New Zealand HarperCollinsPublishers (New Zealand) Limited P.O. Box 1 Auckland, New Zealand'

        __long_machine_en = StateMachine(long_cuter_en(max_len=9))
        m_input = EnSequence(sentence)
        out = __long_machine_en.run(m_input)
        for v in out:
            print(v + "\n")

    # @unittest.skip('pass')
    def test_demo(self):
        # paragraph = "A long time ago. there is a mountain, and there is a temple in the mountain!!! And here is an old monk in the temple!?...."
        # __long_machine_en = StateMachine(long_cuter_en(min_len=4))
        # m_input = EnSequence(paragraph)
        # __long_machine_en.run(m_input)
        # print(m_input.sentence_list())

        paragraph = "A long time ago. There is a mountain, and there is a temple in the mountain!!! And here is an old monk in the temple!?...."
        __long_machine_en = StateMachine(long_cuter_en(max_len=11, min_len=3))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        print(m_input.sentence_list())

    # @unittest.skip('pass')
    def test_bug_2021_3_19(self):
        paragraph = "\"Er ... \" Da ji covered his head and didn' t know what to do. "
        out = cut_to_sentences_en(paragraph)
        print(out)

    # @unittest.skip('pass')
    def test_bug_2021_3_31(self):
        paragraph = "In the new economy, computer science isn’t an optional skill – it’s a basic skill, right along with the three “Rs.”  Nine out of ten parents want it taught at their children’s schools."
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        expect = ['In the new economy, computer science isn’t an optional skill – it’s a basic '
                  'skill, right along with the three “Rs.”',
                  '  Nine out of ten parents want it taught at their children’s schools.']
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_3_31_break(self):
        paragraph = '"I like big meat meat meat meat meat meat meat meat!"'
        __long_machine_en = StateMachine(long_cuter_en(max_len=2))
        expect = ['"I like big meat meat meat meat meat meat meat meat!"']
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_1_1(self):
        paragraph = '"you know worlds is differenct now." "your need to change your mind."'
        __long_machine_en = StateMachine(long_cuter_en(max_len=2))
        expect = ['"you know worlds is differenct now." ', '"your need to change your mind."']
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        # print(acutal)
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_1_2(self):
        paragraph = '"you know worlds is differenct now.""your need to change your mind."'
        __long_machine_en = StateMachine(long_cuter_en(max_len=5))
        expect = ['"you know worlds is differenct now."', '"your need to change your mind."']
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_1_3(self):
        paragraph = 'In a world of uncertainty, we must cherish the importance of “you you you you you me,” “you,” and “us.”'
        __long_machine_en = StateMachine(long_cuter_en(min_len=2, max_len=30))
        expect = ['In a world of uncertainty, we must cherish the importance of “you you you you you me,” ',
                  '“you,” and “us.”']
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        # print(acutal)
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_1(self):
        paragraph = "I found again the people I love. The other members. my family, my friends. I found the music I love, and I found myself. Thinking about the future and trying hard are all important. But cherishing yourself, encouraging yourself and keeping yourself happy is the most important. In a world of uncertainty, we must cherish the importance of “me,” “you,” and “us.”"
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        expect = ['I found again the people I love.',
                  ' The other members. my family, my friends.',
                  ' I found the music I love, and I found myself.',
                  ' Thinking about the future and trying hard are all important.',
                  ' But cherishing yourself, encouraging yourself and keeping yourself happy is the most important.',
                  ' In a world of uncertainty, we must cherish the importance of “me,” “you,” and “us.”']
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print('\n'.join(acutal))
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_2(self):
        paragraph = 'In his own farewell address, George Washington wrote that self-government is the underpinning of our safety, prosperity, and liberty, but “from different causes and from different quarters much pains will be taken… to weaken in your minds the conviction of this truth;” that we should preserve it with “jealous anxiety;” that we should reject “the first dawning of every attempt to alienate any portion of our country from the rest or to enfeeble the sacred ties” that make us one.'
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=25))
        expect = ['In his own farewell address, George Washington wrote that self-government is '
                  'the underpinning of our safety, prosperity,',
                  ' and liberty, but “from different causes and from different quarters much '
                  'pains will be taken… to weaken in your minds the conviction of this truth;” ',
                  'that we should preserve it with “jealous anxiety;” that we should reject '
                  '“the first dawning of every attempt to alienate any portion of our country '
                  'from the rest or to enfeeble the sacred ties” ',
                  'that make us one.']
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        # print(acutal)
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_long_handler_in_quota(self):
        paragraph = '"1" "2 3" 4 5 6 7 8 9 10. 11 12 13 14 15 16 17. "18 19 20 21 22 23 24 25. 26 27 1 1 28 29 30 31 32 33." 34 35 36 37. 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57.'
        __long_machine_en = StateMachine(long_cuter_en(min_len=10, max_len=30))
        expect = ['"1" "2 3" 4 5 6 7 8 9 10.',
                  ' 11 12 13 14 15 16 17. "18 19 20 21 22 23 24 25. 26 27 1 1 28 29 30 31 32 '
                  '33." 34 35 36 37.',
                  ' 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57.']
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_3_1(self):
        paragraph = "The show's writers gave these tropes a 2021 refresh by leaning into the \"woke\" culture of millennials and Gen Z, calling out intolerance, accepting and normalising LGBTQ+ issues, and highlighting struggles faced by minorities living in the US – African-Americans in particular."
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        expect = ["The show's writers gave these tropes a 2021 refresh by leaning into the "
                  '"woke" culture of millennials and Gen Z,',
                  ' calling out intolerance, accepting and normalising LGBTQ+ issues, and '
                  'highlighting struggles faced by minorities living in the US – '
                  'African-Americans in particular.']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_6(self):
        paragraph = """ "A lot of studies show that (masks)don't help the situation with COVID-19 at all," Altherr said. "And not only political, but spiritual beliefs ... the mask represents compliance and silence, being silenced and not being able to speak your opinions. It represents being controlled by the government. There's a lot of stuff to it that I just don't agree with." """
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        expect = [' "A lot of studies show that (masks)don\'t help the situation with COVID-19 '
                  'at all," Altherr said.',
                  ' "And not only political, but spiritual beliefs ...',
                  ' the mask represents compliance and silence, being silenced and not being '
                  'able to speak your opinions.',
                  " It represents being controlled by the government. There's a lot of stuff to "
                  'it that I just don\'t agree with." ']
        # print(acutal)

        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_6_1(self):
        paragraph = "A very touching 2012 documentary that reunites the original G.L.O.W. wrestlers is available to stream on Netflix. "
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        expect = [
            'A very touching 2012 documentary that reunites the original G.L.O.W. wrestlers is available to stream on Netflix. ']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_6_2(self):
        paragraph = "That's fine: Miracle is one of those rare rah-rah movies that deeply, genuinely earns its U!S!A! U!S!A! spirit, " \
                    "presenting us with a collection of blue-collar kids working together to raise the nation's morale."
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        expect = ["That's fine: Miracle is one of those rare rah-rah movies that deeply,",
                  ' genuinely earns its U!S!A! U!S!A! spirit, presenting us with a collection '
                  "of blue-collar kids working together to raise the nation's morale."]
        print('\n'.join(acutal))

        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_6_3(self):
        paragraph = "Trump ignited a furor after signing the order to ban U.S. entities from dealing with WeChat -- along with TikTok, ByteDance Ltd.’s viral video platform -- from September. Confusion reigned as investors grappled with the sweeping language of Trump’s order -- which bars “transactions” with the Chinese company -- that leaves the door open for the administration to extend it well beyond the service in America. "
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        expect = ['Trump ignited a furor after signing the order to ban U.S. entities from '
                  'dealing with WeChat -- along with TikTok, ByteDance Ltd.’s viral video '
                  'platform -- from September.',
                  ' Confusion reigned as investors grappled with the sweeping language of '
                  'Trump’s order --',
                  ' which bars “transactions” with the Chinese company -- that leaves the door '
                  'open for the administration to extend it well beyond the service in '
                  'America. ']

        print(acutal)

        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_6_4(self):
        paragraph = "Some of the best conversations that I have had about history and about the history of slavery have been with 5 - year - olds, 7 - year - olds, 9 - year - olds. It is so important that we know our history, that we teach all aspects of history, even the tough parts, the subjects that make us uncomfortable, the subjects that make us feel ashamed about our nation. That's when we are in a place where we can move forward and grow and live in a realistic space. "
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        expect = [
            'Some of the best conversations that I have had about history and about the history of slavery have been with 5 - year - olds, 7 - year - olds, 9 - year - olds.',
            ' It is so important that we know our history, that we teach all aspects of history,',
            ' even the tough parts, the subjects that make us uncomfortable, the subjects that make us feel ashamed about our nation.',
            " That's when we are in a place where we can move forward and grow and live "
            'in a realistic space. ']

        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_6_5(self):
        paragraph = """ *On the Internet, @ (pronounced "at" or "at sign" or "address sign") is the symbol in an e-mail address that separates the name of the user from the user's Internet address, as in this hypothetical e-mail address example: msmuffet@tuffet.org.  """
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        expect = [' *On the Internet, @ (pronounced "at" or "at sign" or "address sign")',
                  ' is the symbol in an e-mail address that separates the name of the user from '
                  "the user's Internet address, as in this hypothetical e-mail address example:",
                  ' msmuffet@tuffet.org.  ']
        print('\n'.join(acutal))
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_6_6(self):
        paragraph = """Lee Bo-jin is the second daughter of the chairman of Samsung, the "genuine" heir of Korea's largest chaebol. Ms. Lee is currently running the family's Shilla hotel chain. With everything from money to power, Lee Bo-jin has always been dubbed the "No. 1 Korean woman" and ranked 87th in the top 100 most powerful women in the world voted by Forbes magazine. However, inside that flashy life is a tragic life of the "Samsung princess". *
    *Princess means the richest woman in the country."""
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        expect = ['Lee Bo-jin is the second daughter of the chairman of Samsung, the "genuine" '
                  "heir of Korea's largest chaebol.",
                  " Ms. Lee is currently running the family's Shilla hotel chain.",
                  ' With everything from money to power, Lee Bo-jin has always been dubbed the '
                  '"No. 1 Korean woman" ',
                  'and ranked 87th in the top 100 most powerful women in the world voted by '
                  'Forbes magazine.',
                  ' However, inside that flashy life is a tragic life of the "Samsung '
                  'princess".',
                  ' *\n    *Princess means the richest woman in the country.']

        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_6_8(self):
        paragraph = """These uses often vary depending upon the language of the text it is used in. The word “tilde” originally came from the Latin word titulus meaning “title” or “superscription,” and made its way to English from Spanish. Like ~ in the sea. """
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        expect = ['These uses often vary depending upon the language of the text it is used in.',
                  ' The word “tilde” originally came from the Latin word titulus meaning '
                  '“title” or “superscription,” and made its way to English from Spanish.',
                  ' Like ~ in the sea. ']

        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_6_9(self):
        paragraph = "The night was rapidly approaching; and already, at the cry of “Moccoletti!” repeated by the shrill voices of a thousand vendors, two or three stars began to burn among the crowd. It was a signal. At the end of ten minutes fifty thousand lights glittered, descending from the Palazzo di Venezia to the Piazza del Popolo, and mounting from the Piazza del Popolo to the Palazzo di Venezia. It seemed like the fête of Jack-o’-lanterns."
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        expect = ['The night was rapidly approaching; and already, at the cry of “Moccoletti!” '
                  'repeated by the shrill voices of a thousand vendors,',
                  ' two or three stars began to burn among the crowd.',
                  ' It was a signal. At the end of ten minutes fifty thousand lights glittered,',
                  ' descending from the Palazzo di Venezia to the Piazza del Popolo, and '
                  'mounting from the Piazza del Popolo to the Palazzo di Venezia.',
                  ' It seemed like the fête of Jack-o’-lanterns.']

        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_10(self):
        paragraph = "Some of the fellows pretended to think I was mad when I rushed at Chandos and hugged him, and shouted, \"It's all your doing, old fellow. I'm going to sea! I'm going to sea!\""
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ['Some of the fellows pretended to think I was mad when I rushed at Chandos '
                  'and hugged him, and shouted,',
                  ' "It\'s all your doing, old fellow. I\'m going to sea! I\'m going to sea!"']

        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_10_1(self):
        paragraph = "And today, I signed into law the American Rescue Plan, an historic piece of legislation that delivers immediate relief to millions of people. It includes $1,400 in direct rescue checks — payments. "
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ['And today, I signed into law the American Rescue Plan, an historic piece of '
                  'legislation that delivers immediate relief to millions of people.',
                  ' It includes $1,400 in direct rescue checks — payments. ']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_10_2(self):
        paragraph = "But Nicholson added a little something to cut the tension — the production went through dozens of doors before director Stanley Kubrick was satisfied — and his improvised \"Here's Johnny!\" made the cut."
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ['But Nicholson added a little something to cut the tension —',
                  ' the production went through dozens of doors before director Stanley Kubrick '
                  'was satisfied — and his improvised "Here\'s Johnny!" made the cut.']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_10_3(self):
        paragraph = "Stock up on gifts and shoes from lesser-known designers at pastel-painted boutique TenOverSix and spot celebrities at DASH boutique, a 2,000-square-foot space at 8420 Melrose Avenue owned by the Kardashian sisters. "

        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ['Stock up on gifts and shoes from lesser-known designers at pastel-painted '
                  'boutique TenOverSix and spot celebrities at DASH boutique,',
                  ' a 2,000-square-foot space at 8420 Melrose Avenue owned by the Kardashian '
                  'sisters. ']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_10_4(self):
        paragraph = "'\"Who was it used to pray, O God, make me good, but not yet\"?' and 1 2 3 4 5 6 7"
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ['\'"Who was it used to pray, O God, make me good, but not yet"?\' and 1 2 3 4 5 6 7']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_10_5(self):
        paragraph = "'Charles Irving.'"
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ["'Charles Irving.'"]
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_12(self):
        paragraph = 'I\'m coming to it! All right. I\'m coming to it! I was going to say that when I listened that morning, I listened with admiration amounting to haw. I thought to myself, "Here\'s a man with a wooden leg—a literary man with—"'

        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ["I'm coming to it! All right.",
                  " I'm coming to it! I was going to say that when I listened that morning, I "
                  'listened with admiration amounting to haw.',
                  ' I thought to myself, "Here\'s a man with a wooden leg—a literary man with—"']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_12_1(self):
        paragraph = "'I'm coming to it! All right. I'm coming to it! I was going to say that when I listened that morning, I listened with admiration amounting to haw. I thought to myself, \"Here's a man with a wooden leg—a literary man with—\"'"

        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ["'I'm coming to it! All right.",
                  " I'm coming to it! I was going to say that when I listened that morning, I "
                  'listened with admiration amounting to haw.',
                  ' I thought to myself, "Here\'s a man with a wooden leg—a literary man '
                  'with—"\'']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_4_15(self):
        paragraph = "'Calls me Sir!' said Mr Wegg, to himself; 'HE won't answer. A bow gone!'"
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ["'Calls me Sir!' said Mr Wegg, to himself; 'HE won't answer. A bow gone!'"]
        self.assertEqual(expect, acutal)

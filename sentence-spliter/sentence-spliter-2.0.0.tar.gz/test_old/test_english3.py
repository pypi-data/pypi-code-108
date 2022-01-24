# -*- coding:utf-8 -*-
# CREATED BY: jiangbohuai
# CREATED ON: 2021/5/21 2:23 PM
# LAST MODIFIED ON:
# AIM:

import unittest
from sentence_spliter_old.logic_graph_en import long_cuter_en
from sentence_spliter_old.automata.sequence import EnSequence
from sentence_spliter_old.automata.state_machine import StateMachine


class test_spliter(unittest.TestCase):

    # @unittest.skip('pass')
    def test_bug_2021_5_21(self):
        paragraph = "\"There's -- got -- to -- be -- a -- shotcut,\" Ron pathed as they climbed their seventh long " \
                    "staircase and emerged on an unfamiliar landing, where there was nothing but a large painting of a bare" \
                    "stretch of grass hanging on the stone wall."
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        expect = ['"There\'s -- got -- to -- be -- a -- shotcut,"',
                  ' Ron pathed as they climbed their seventh long staircase and emerged on an '
                  'unfamiliar landing,',
                  ' where there was nothing but a large painting of a barestretch of grass '
                  'hanging on the stone wall.']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_5_21_2(self):
        paragraph = "\"And Professor Lupin stepped over you, and waled toward the dementor, and pulled out his wand,\" " \
                    "said Hermione, \" and he said, 'None of us is hiding Sirius Black under our cloaks. Go.' But the " \
                    "dementor didn't move, so Lupin muttered something, and a silvery thing shot out of his wand at it, " \
                    "and itturned around and sort of glided away ....\""
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ['"And Professor Lupin stepped over you, and waled toward the dementor, and '
                  'pulled out his wand," said Hermione,',
                  ' " and he said, \'None of us is hiding Sirius Black under our cloaks. Go.\' ',
                  "But the dementor didn't move, so Lupin muttered something, and a silvery "
                  'thing shot out of his wand at it, and itturned around and sort of glided '
                  'away ...."']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_5_21_3(self):
        paragraph = "noticed that they could slied through gaps that Uncle Vernon's new company car certainly " \
                    "couldn't have managed. They reached King's Cross with twenty minutes to spare; the Ministry" \
                    "drivers found them trolleys, unloaded their trunks, touched their hats in salute ti Mr. Weasley," \
                    "and drove away, somehow managing to jump to the head of an unmoving line at the traffic lights."

        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = [
            "noticed that they could slied through gaps that Uncle Vernon's new company car certainly couldn't have managed.",
            " They reached King's Cross with twenty minutes to spare;",
            ' the Ministrydrivers found them trolleys, unloaded their trunks, touched their hats in salute ti Mr. Weasley,and drove away,',
            ' somehow managing to jump to the head of an unmoving line at the traffic lights.']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_5_21_4(self):
        paragraph = "\"The sooner we get on the train, the better,\" he said. \"At least I can get away from" \
                    "Percy at Hogwarts. Now he's accusing me of dripping tea on his photo of Penelop Clearwarter." \
                    "You Know,\" Ron grimaced, \"his girlfriend. She's hidden her face under the frame because her nose " \
                    "gone all blotchy....\""
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ['"The sooner we get on the train, the better," he said.',
                  ' "At least I can get away fromPercy at Hogwarts. Now he\'s accusing me of dripping tea on his photo of Penelop Clearwarter.You Know," Ron grimaced,',
                  ' "his girlfriend. She\'s hidden her face under the frame because her nose gone all blotchy...."']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_5_24_1(self):
        paragraph = "Harry had not chance to speak to Ron or Hermione in the chaos of leaving; they were too busey heaving all thier trunks down the Leaky Cauldron's " \
                    "narrow staircase and piling them up near the door, with Hedwig and Hermes, Percy's screech owl, perched on top in thier cages."
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ['Harry had not chance to speak to Ron or Hermione in the chaos of leaving;',
                  " they were too busey heaving all thier trunks down the Leaky Cauldron's narrow staircase and piling them up near the door,",
                  " with Hedwig and Hermes, Percy's screech owl, perched on top in thier cages."]
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_5_24_2(self):
        paragraph = "I wept like a child. \"Dear mountains! my own beautiful lake! How do you welcome your wanderer? Your summits are clear; the sky and lake are blue and placid. Is this to prognosticate peace, or to mock at my unhappiness?\""
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ['I wept like a child.',
                  ' "Dear mountains! my own beautiful lake! How do you welcome your wanderer?',
                  ' Your summits are clear; the sky and lake are blue and placid. Is this to '
                  'prognosticate peace, or to mock at my unhappiness?"']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_5_24_3(self):
        paragraph = "\"Not at all. The 'G' with the small 't' stands for 'Gesellschaft,' which is the German for 'Company" \
                    ".' It is a customary contraction like our 'Co.' 'P,' of course, stands for 'Papier.' Now for the " \
                    "'Eg.' Let us glance at our Continental Gazetteer.\" He took down a heavy brown volume from his " \
                    "shelves. \"Eglow, Eglonitz--here we are, Egria. It is in a German-speaking country--in Bohemia, " \
                    "not far from Carlsbad. 'Remarkable as being the scene of the death of Wallenstein, and for its " \
                    "numerous glass-factories and paper-mills.' Ha, ha, my boy, what do you make of that?\" His " \
                    "eyes sparkled, and he sent up a great blue triumphant cloud from his cigarette."

        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = [
            '"Not at all. The \'G\' with the small \'t\' stands for \'Gesellschaft,\' which is the German for \'Company.\'',
            ' It is a customary contraction like our \'Co.\' \'P,\' of course, stands for \'Papier.\' Now for the \'Eg.\' Let us glance at our Continental Gazetteer."',
            ' He took down a heavy brown volume from his shelves.',
            ' "Eglow, Eglonitz--here we are, Egria. It is in a German-speaking country--in Bohemia, not far from Carlsbad.',
            " 'Remarkable as being the scene of the death of Wallenstein, and for its numerous glass-factories and paper-mills.' Ha, ha, my boy, what do you make of that?\"",
            ' His eyes sparkled, and he sent up a great blue triumphant cloud from his cigarette.']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_5_24_4(self):
        paragraph = '''
I wept like a child. "Dear mountains! my own beautiful lake! how do you welcome your wanderer? Your summits are clear; the sky and lake are blue and placid. Is this to prognosticate peace, or to mock at my unhappiness?"
        '''

        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ['\nI wept like a child.',
                  ' "Dear mountains! my own beautiful lake! how do you welcome your wanderer?',
                  ' Your summits are clear; the sky and lake are blue and placid. Is this to '
                  'prognosticate peace, or to mock at my unhappiness?"\n'
                  '        ']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_5_25_1(self):
        paragraph = '''"I was still balancing the matter in my mind when a hansom cab drove up to Briony Lodge, and a gentleman sprang out. He was a remarkably handsome man, dark, aquiline, and moustached, evidently the man of whom I had heard. He appeared to be in a great hurry, shouted to the cabman to wait, and brushed past the maid who opened the door with the air of a man who was thoroughly at home.'''
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = [
            '"I was still balancing the matter in my mind when a hansom cab drove up to Briony Lodge, and a gentleman sprang out.',
            ' He was a remarkably handsome man, dark, aquiline, and moustached, evidently the man of whom I had heard.',
            ' He appeared to be in a great hurry, shouted to the cabman to wait,',
            ' and brushed past the maid who opened the door with the air of a man who was thoroughly at home.']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_5_25_2(self):
        paragraph = '''"He was in the house about half an hour, and I could catch glimpses of him in the windows of the sitting-room, pacing up and down, talking excitedly, and waving his arms. Of her I could see nothing. Presently he emerged, looking even more flurried than before. As he stepped up to the cab, he pulled a gold watch from his pocket and looked at it earnestly, 'Drive like the devil,' he shouted, 'first to Gross & Hankey's in Regent Street, and then to the Church of St. Monica in the Edgeware Road. Half a guinea if you do it in twenty minutes!' '''
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ['"He was in the house about half an hour,',
                  ' and I could catch glimpses of him in the windows of the sitting-room, pacing up and down, talking excitedly, and waving his arms.',
                  ' Of her I could see nothing. Presently he emerged, looking even more flurried than before.',
                  ' As he stepped up to the cab,',
                  ' he pulled a gold watch from his pocket and looked at it earnestly,',
                  " 'Drive like the devil,' he shouted, 'first to Gross & Hankey's in Regent Street,",
                  " and then to the Church of St. Monica in the Edgeware Road. Half a guinea if you do it in twenty minutes!' "]
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_5_25_3(self):
        paragraph = ''' "It may be so, or it may not. Mr. Holmes," said he, "but if you are so very sharp you ought to be sharp enough to know that it is you who are breaking the law now, and not me. I have done nothing actionable from the first, but as long as you keep that door locked you lay yourself open to an action for assault and illegal constraint." '''
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = [' "It may be so, or it may not. Mr. Holmes," said he,',
                  ' "but if you are so very sharp you ought to be sharp enough to know that it is you who are breaking the law now, and not me.',
                  ' I have done nothing actionable from the first, but as long as you keep that door locked you lay yourself open to an action for assault and illegal constraint." ']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_5_25_4(self):
        paragraph = ''' Commenting on the stereotypes that Asian Americans face in the US, John C. Yang President and Executive Director of the Asian Americans Advancing Justice (AAJC) told CNN, “Unfortunately, Asian Americans and Pacific Islanders often are invisible to the public. Or, where we are visible, it falls into a couple of different stereotypes. One stereotype is the so called ‘model minority’ — the suggestion that there are no issues that really affect the Asian American community.” '''
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = [' Commenting on the stereotypes that Asian Americans face in the US, John C. '
                  'Yang President and Executive Director of the Asian Americans Advancing '
                  'Justice (AAJC) told CNN,',
                  ' “Unfortunately, Asian Americans and Pacific Islanders often are invisible '
                  'to the public.',
                  ' Or, where we are visible, it falls into a couple of different stereotypes.',
                  ' One stereotype is the so called ‘model minority’ — the suggestion that '
                  'there are no issues that really affect the Asian American community.” ']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_5_25_5(self):
        paragraph = ''' In a statement on March 19, US President Joe Biden urged Congress to “swiftly pass the COVID-19 Hate Crimes Act, which would expedite the federal government’s response to the rise of hate crimes exacerbated during the pandemic, support state and local governments to improve hate crimes reporting, and ensure that hate crimes information is more accessible to Asian American communities.”'''
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = [' In a statement on March 19, US President Joe Biden urged Congress to '
                  '“swiftly pass the COVID-19 Hate Crimes Act,',
                  ' which would expedite the federal government’s response to the rise of hate '
                  'crimes exacerbated during the pandemic,',
                  ' support state and local governments to improve hate crimes reporting, and '
                  'ensure that hate crimes information is more accessible to Asian American '
                  'communities.”']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_5_25_6(self):
        paragraph = '''Now, the former child star is being hailed for her big screen directorial debut in "One Night in Miami," adapted from Kemp Powers' stage play about a meeting between Cassius Clay, Jim Brown, Sam Cooke and Malcolm X.'''
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = [
            'Now, the former child star is being hailed for her big screen directorial debut in "One Night in Miami,"',
            " adapted from Kemp Powers' stage play about a meeting between Cassius Clay, Jim Brown, Sam Cooke and Malcolm X."]
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_5_25_7(self):
        paragraph = '''The numbers don't lie: For the second consecutive year, the percentages of women directing top-grossing films increased, reaching "recent historic highs," while the overall percentages of women working in key behind-the-scenes roles remained relatively stable, according to a study by San Diego State University released in January.'''
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ["The numbers don't lie: For the second consecutive year, the percentages of "
                  'women directing top-grossing films increased, reaching "recent historic '
                  'highs,"',
                  ' while the overall percentages of women working in key behind-the-scenes '
                  'roles remained relatively stable, according to a study by San Diego State '
                  'University released in January.']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_5_25_8(self):
        paragraph = '''Lydia declared herself satisfied. “Oh! yes. It would be much better to wait till Jane was well, and by that time most likely Captain Carter would be at Meryton again. And when you have given your ball,” she added, “I shall insist on their giving one also. I shall tell Colonel Forster it will be quite a shame if he does not.”'''
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ['Lydia declared herself satisfied.',
                  ' “Oh! yes. It would be much better to wait till Jane was well,',
                  ' and by that time most likely Captain Carter would be at Meryton again.',
                  ' And when you have given your ball,” she added,',
                  ' “I shall insist on their giving one also. I shall tell Colonel Forster it '
                  'will be quite a shame if he does not.”']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_5_25_9(self):
        paragraph = '''Two common classifications of chips are logic and memory. Logic chips perform operations; these include microprocessors – the brains your mobile phone, laptop, etc. Memory chips store data, either temporarily or in longer term storage (such as solid state drives).'''
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ['Two common classifications of chips are logic and memory.',
                  ' Logic chips perform operations; these include microprocessors – the brains '
                  'your mobile phone, laptop, etc.',
                  ' Memory chips store data, either temporarily or in longer term storage (such '
                  'as solid state drives).']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_5_25_10(self):
        paragraph = '''You don't predict the future; you imagine the future. So as a science fiction writer whose stories often take place years or even centuries from now, I've found that people are really hungry for visions of the future that are both colorful and lived in, but I found that research on its own is not enough to get me there.'''
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ["You don't predict the future; you imagine the future.",
                  ' So as a science fiction writer whose stories often take place years or even '
                  'centuries from now,',
                  " I've found that people are really hungry for visions of the future that are "
                  'both colorful and lived in,',
                  ' but I found that research on its own is not enough to get me there.']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_5_25_11(self):
        paragraph = '''We also have a social and relational crisis; we're in the valley. We're fragmented from each other, we've got cascades of lies coming out of Washington...'''
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ["We also have a social and relational crisis; we're in the valley.",
                  " We're fragmented from each other, we've got cascades of lies coming out of "
                  'Washington...']
        self.assertEqual(expect, acutal)

    # @unittest.skip('pass')
    def test_bug_2021_5_25_12(self):
        paragraph = '''Quidditch team: three Chasers, whose job it was to score goals by putting the Quaffle(a red, soccer-sized ball) through one of the fifity-foot-high hoops at each end of the field;two Beaters, who were equipped with heavy bats to repel the Budgers(two heavy black balls that zoomed around trying to attack the players); a Keeper who defended the goalposts, and the Seeker, who had the'''
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ['Quidditch team: three Chasers, whose job it was to score goals by putting '
                  'the Quaffle(a red, soccer-sized ball)',
                  ' through one of the fifity-foot-high hoops at each end of the field;',
                  'two Beaters, who were equipped with heavy bats to repel the Budgers(two '
                  'heavy black balls that zoomed around trying to attack the players);',
                  ' a Keeper who defended the goalposts, and the Seeker, who had the']
        self.assertEqual(expect, acutal)

    def test_bug_2021_5_25_13(self):
        paragraph = '''the dog in the shadows of Magnolia Crescent. . . Lavernder Browb claooed her hands on'''
        __long_machine_en = StateMachine(long_cuter_en(min_len=2, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ['the dog in the shadows of Magnolia Crescent. . .',
                  ' Lavernder Browb claooed her hands on']
        self.assertEqual(expect, acutal)

    def test_bug_2021_5_25_13_1(self):
        paragraph = '''the dog in the shadows of Magnolia Crescent. ? ! Lavernder Browb claooed her hands on'''
        __long_machine_en = StateMachine(long_cuter_en(min_len=2, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ['the dog in the shadows of Magnolia Crescent. ? !',
                  ' Lavernder Browb claooed her hands on']
        self.assertEqual(expect, acutal)

    # 这个是一个分复杂的例子
    def test_bug_2021_5_25_14(self):
        paragraph = '''"Yeh always wait fer the hippogriff ter make the firs' move," Hagrid cointinued. "It's polite, see? Yeh walk toward him, and yeh bow, an' yeh wait. If he bows back, yeh're allowed ter toych him. If he desn' bow, then get away from him sharpish,' cause those talons hurt.'''

        #paragraph = "\"Yeh always wait fer the hippogriff ter make the firs' move,\" Hagrid cointinued. \"It's polite, see? Yeh walk toward him, and yeh bow, an' yeh wait. If he bows back, yeh're allowed ter toych him. If he desn' bow, then get away from him sharpish,' cause those talons hurt."

        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ['"Yeh always wait fer the hippogriff ter make the firs\' move," Hagrid cointinued.',
                  ' "It\'s polite, see? Yeh walk toward him, and yeh bow, an\' yeh wait.',
                  " If he bows back, yeh're allowed ter toych him. If he desn' bow, then get away from him sharpish,' cause those talons hurt."]
        self.assertEqual(expect, acutal)

    def test_bug_2021_5_26(self):
        paragraph = "In the new economy, computer science isn't an optional skill – it's a basic skill, right along with the three \"Dr.\" Steven Nine out of ten parents want it taught at their children's schools"
        __long_machine_en = StateMachine(long_cuter_en(min_len=6, max_len=30))
        m_input = EnSequence(paragraph)
        __long_machine_en.run(m_input)
        acutal = m_input.sentence_list()
        print(acutal)
        expect = ["In the new economy, computer science isn't an optional skill – it's a basic skill,",
                  ' right along with the three "Dr." Steven Nine out of ten parents want it taught at their children\'s schools']
        self.assertEqual(expect, acutal)

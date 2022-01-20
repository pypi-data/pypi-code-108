import html
import re

import langid


class MyTokenizer:
    def __init__(self,do_lower_case=False):
        # 把连号‘-’分开,空格也作为一个词
        self.sentences_tokenizer_en = self.get_sentences_tokenizer_en()
        self.words_tokenizer_en = self.get_word_tokenizer_en(do_lower_case=do_lower_case)

    @staticmethod
    def cut_paragraph_to_sentences_zh(para: str, drop_empty_line=True, strip=True, deduplicate=False):
        """
            中文切句
        Args:
           para: 输入段落文本
           drop_empty_line: 是否丢弃空行
           strip:  是否对每一句话做一次strip
           deduplicate: 是否对连续标点去重，帮助对连续标点结尾的句子分句

        Returns:
           sentences: list[str]
        """
        if deduplicate:
            para = re.sub(r"([。！？\!\?])\1+", r"\1", para)

        para = re.sub('([。！？\?!])([^”’])', r"\1\n\2", para)  # 单字符断句符
        para = re.sub('(\.{6})([^”’])', r"\1\n\2", para)  # 英文省略号
        para = re.sub('(\…{2})([^”’])', r"\1\n\2", para)  # 中文省略号
        para = re.sub('([。！？\?!][”’])([^，。！？\?])', r'\1\n\2', para)
        # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
        para = para.rstrip()  # 段尾如果有多余的\n就去掉它
        # 很多规则中会考虑分号;，但是这里我把它忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
        sentences = para.split("\n")
        if strip:
            sentences = [sent.strip() for sent in sentences]
        if drop_empty_line:
            sentences = [sent for sent in sentences if len(sent.strip()) > 0]
        return sentences

    @staticmethod
    def get_sentences_tokenizer_en():
        """
            the tokenizer for cutting paragraph to sentences
        Returns:
            tokenizer
        """
        from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
        punkt_param = PunktParameters()
        abbreviation = ['et al.', 'i.e.', 'e.g.', 'etc.', 'i.e', 'e.g', 'etc', ' et al']
        punkt_param.abbrev_types = set(abbreviation)
        tokenizer = PunktSentenceTokenizer(punkt_param)
        return tokenizer

    @staticmethod
    def cut_sentence_to_words_zh(sentence: str):
        """
            cut_sentence_to_words_zh
        Args:
            sentence: a sentence ,str

        Returns:
            sentences: list[str]
        """
        english = 'abcdefghijklmnopqrstuvwxyz0123456789αγβδεζηθικλμνξοπρστυφχψω'
        output = []
        buffer = ''
        for s in sentence:
            if s in english or s in english.upper():  # 英文或数字
                buffer += s
            else:  # 中文
                if buffer:
                    output.append(buffer)
                buffer = ''
                output.append(s)
        if buffer:
            output.append(buffer)
        return output

    @staticmethod
    def get_word_tokenizer_en(do_lower_case=False):
        """
            the tokenizer for cutting sentence to words
        Returns:
            tokenizer
        """
        from transformers import BasicTokenizer
        return BasicTokenizer(do_lower_case=do_lower_case)
        # from nltk import WordPunctTokenizer
        # return WordPunctTokenizer()  # ').' 分不开，垃圾

    def cut_sentence_to_words(self, sentence: str,return_starts = False):
        if langid.classify(sentence)[0] == 'zh':
            words = self.cut_sentence_to_words_zh(sentence)
        else:
            words =  self.words_tokenizer_en.tokenize(sentence)
        if return_starts:
            starts = []  # 每个word在句子中的位置
            i = 0
            for j in words:
                while i < len(sentence):
                    if sentence[i:i + len(j)] == j:
                        starts.append(i)
                        i += len(j)
                        break
                    else:
                        i += 1
            return words,starts
        return words

    def cut_paragraph_to_sentences(self, paragraph: str):
        if langid.classify(paragraph)[0] == 'zh':
            return self.cut_paragraph_to_sentences_zh(paragraph)
        else:
            return self.sentences_tokenizer_en.tokenize(paragraph)


class TextProcessor:
    def __init__(self):
        pass

    @staticmethod
    def clean_text(text: str):
        """
        清洗数据
        Args:
            text: 文本

        Returns:
            text
        """
        import re
        text = re.sub('<[^<]+?>', '', text).replace('\n', '').strip()  # 去html中的<>标签
        text = ' '.join(text.split()).strip()
        return text

    @staticmethod
    def ner_find(text: str, entities: dict, ignore_nested=True):
        """
        find the loaction of entities in a text
        Args:
            text: a text, like '我爱吃苹果、大苹果，小苹果，苹果【II】，梨子，中等梨子，雪梨，梨树。'
            entities: {'entity_type1':{entity_str1,entity_str2...},
                       'entity_type2':{entity_str1,entity_str2...},
                       ...}
                       like : {'apple': ['苹果', '苹果【II】'], 'pear': ['梨', '梨子'],}
            ignore_nested: if nested
        #>>>IndexedRuleNER().ner(text, entities, False)
        Returns:
            indexed_entities:{'entity_type1':[[start_index,end_index,entity_str],
                                              [start_index,end_index,entity_str]...]
                              'entity_type2':[[start_index,end_index,entity_str],
                                              [start_index,end_index,entity_str]...]
                                              ...}
        #>>>{'apple': [[3, 5, '苹果'], [7, 9, '苹果'], [11, 13, '苹果'], [14, 16, '苹果'], [14, 20, '苹果【II】']],
        'pear': [[21, 22, '梨'], [26, 27, '梨'], [30, 31, '梨'], [32, 33, '梨'], [21, 23, '梨子'], [26, 28, '梨子']]}
        """

        indexed_entities = dict()
        for every_type, every_value in entities.items():
            every_type_value = []
            for every_entity in list(every_value):
                special_character = set(re.findall('\W', str(every_entity)))
                for i in special_character:
                    every_entity = every_entity.replace(i, '\\' + i)
                re_result = re.finditer(every_entity, text)
                for i in re_result:
                    res = [i.span()[0], i.span()[1], i.group()]
                    if res != []:
                        every_type_value.append([i.span()[0], i.span()[1], i.group()])
            indexed_entities[every_type] = every_type_value
        if ignore_nested:
            for key, value in indexed_entities.items():
                all_indexs = [set(range(i[0], i[1])) for i in value]
                for i in range(len(all_indexs)):
                    for j in range(i, len(all_indexs)):
                        if i != j and all_indexs[j].issubset(all_indexs[i]):
                            value.remove(value[j])
                            indexed_entities[key] = value
                        elif i != j and all_indexs[i].issubset(all_indexs[j]):
                            value.remove(value[i])
                            indexed_entities[key] = value
        return indexed_entities

    @staticmethod
    def remove_illegal_chars(text: str):
        """
        移除非法字符
        Args:
            text:

        Returns:

        """
        ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')
        return ILLEGAL_CHARACTERS_RE.sub(r'', text)  # 非法字符

    @staticmethod
    def remove_invisible_chars(text, including_char=('\t', '\n', '\r')):
        """移除所有不可见字符，除'\t', '\n', '\r'外"""
        str = ''
        for t in text:
            if (t not in including_char) and (not t.isprintable()):
                str += ' '
            else:
                str += t
        return str

    @staticmethod
    def remove_html_tags(text):
        # soup = BeautifulSoup(raw_str, features="html.parser")
        # return ''.join([s.text.replace('\n', '') for s in soup.contents if hasattr(s, 'text') and s.text])

        # text = re.sub('<[^<]+?>', '', text).replace('\n', '').strip()  # 去html中的<>标签
        # text = ' '.join(text.split()).strip()
        return html.unescape(text)  # html转义字符

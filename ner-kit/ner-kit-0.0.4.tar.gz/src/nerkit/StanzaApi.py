import stanza
from stanza.server import CoreNLPClient, StartServer
from stanza.models.common.doc import Document
from stanza.pipeline.core import Pipeline
from stanza.pipeline.multilingual import MultilingualPipeline
import os
class StanfordCoreNLPClient:
    def __init__(self,corenlp_root_path,language='en',memory='6G', timeout=300000):
        self.corenlp_root_path=corenlp_root_path
        if corenlp_root_path != "":
            stanza.install_corenlp(
                dir=self.corenlp_root_path)
        self.client = CoreNLPClient(
            start_server=StartServer.TRY_START,
            annotators=['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'parse', 'depparse', 'coref','natlog','openie'],
            timeout=timeout,
            memory=memory,
            properties=language,
            # StartServer=StartServer.TRY_START
        )

    def install_corenlp(self):
        stanza.install_corenlp(
            dir=self.corenlp_root_path)

    def get_entity_list(self,text):
        list_token = []
        ann = self.client.annotate(text)
        for sentence in ann.sentence:
            for token in sentence.token:
                # print(token.value, token.pos, token.ner)
                token_model = {
                    "value": token.value,
                    "pos": token.pos,
                    "ner": token.ner
                }
                list_token.append(token_model)
        return list_token

    def open_ie(self,text,raw_result=False,min_confidence=-1):
        # with CoreNLPClient(annotators=["tokenize","ssplit","pos","lemma","depparse","natlog","openie"], be_quiet=False) as client:
        # self.client= CoreNLPClient(annotators=["openie"], be_quiet=False,StartServer=StartServer.TRY_START)

        list_result = []
        '''
        properties = {"annotators": "tokenize,ssplit,pos,lemma,depparse,natlog,openie",
                     # "outputFormat": "json",
                      "openie.triple.strict": "true",
                      "openie.max_entailments_per_clause": "1"}
        '''
        ann = self.client.annotate(text)
        # print(ann)
        for sentence in ann.sentence:
            for triple in sentence.openieTriple:
                # print(triple)
                if min_confidence!=-1:
                    if triple.confidence<min_confidence:
                        continue
                model={
                    "subject":triple.subject,
                    "relation":triple.relation,
                    "object":triple.object,
                    "confidence":triple.confidence
                }
                if raw_result:
                    list_result.append(triple)
                else:
                    list_result.append(model)
        return list_result

    def force_close_server(self,port=9000):
        # windows
        out = os.popen(f'netstat -ano | findstr :{port}').read()
        pid = -1
        for line in out.split("\n"):
            line = line.strip()
            if 'LISTENING' in line:
                pid = line.split(' ')[-1]
                # print("pid = ", pid)
                break
        if pid != -1:
            out = os.popen(f'taskkill /F /PID {pid}').read()
            return out
        else:
            return ""
        # linux: sudo kill -9 `sudo lsof -t -i:9001`

class StanzaWrapper:
    def __init__(self,auto_download_en=False,auto_download_zh=False,should_print_msg=False,use_gpu=True):
        if auto_download_en:
            self.download(lang="en")
        if auto_download_zh:
            self.download_chinese_model()
        self.should_print_result=should_print_msg
        self.use_gpu=use_gpu

    def download(self,lang="en",processors="tokenize,pos",verbose=False):
        stanza.download(lang,processors=processors,verbose=verbose)

    def download_chinese_model(self,lang='zh',verbos=False):
        stanza.download(lang=lang,verbose=verbos)

    def set_gpu(self,use_gpu):
        self.use_gpu=use_gpu

    def get_gpu(self):
        return self.use_gpu

    def tokenize_chinese(self, text):
        return self.tokenize(text,lang='zh')

    def tokenize(self,text,lang="en",processors="tokenize",tokenize_no_ssplit=False,tokenize_pretokenized=False,verbose=False):
        nlp = stanza.Pipeline(lang=lang, processors=processors,tokenize_no_ssplit=tokenize_no_ssplit,tokenize_pretokenized=tokenize_pretokenized,verbose=verbose,use_gpu=self.use_gpu)
        doc = nlp(text)
        list_sentence=[]

        for i, sentence in enumerate(doc.sentences):
            if self.should_print_result:
                print(f'====== Sentence {i + 1} tokens =======')
                print(*[f'id: {token.id}\ttext: {token.text}' for token in sentence.tokens], sep='\n')
            tokens=[]
            for token in sentence.tokens:
                model={
                    "id":token.id,
                    "text":token.text
                }
                tokens.append(model)
            list_sentence.append(tokens)
        return list_sentence

    def tokenize_sentence(self,text,lang="en",processors="tokenize",tokenize_no_ssplit=False,tokenize_pretokenized=False,verbose=False):
        nlp = stanza.Pipeline(lang=lang, processors=processors,tokenize_no_ssplit=tokenize_no_ssplit,tokenize_pretokenized=tokenize_pretokenized,verbose=verbose,use_gpu=self.use_gpu)
        doc = nlp(text)
        list_sentence=[]
        for i, sentence in enumerate(doc.sentences):
            if self.should_print_result:
                print(f'====== Sentence {i + 1} tokens =======')
                print(sentence.text, sep='\n')
            list_sentence.append(sentence.text)
        return list_sentence

    def tokenize_list(self,list_tokens,lang="en",processors="tokenize",tokenize_no_ssplit=False,tokenize_pretokenized=False,verbose=False):
        nlp = stanza.Pipeline(lang=lang, processors=processors,tokenize_no_ssplit=tokenize_no_ssplit,tokenize_pretokenized=tokenize_pretokenized,verbose=verbose,use_gpu=self.use_gpu)
        doc = nlp(list_tokens)
        list_sentence=[]
        for i, sentence in enumerate(doc.sentences):
            if self.should_print_result:
                print(f'====== Sentence {i + 1} tokens =======')
                print(*[f'id: {token.id}\ttext: {token.text}' for token in sentence.tokens], sep='\n')
            tokens=[]
            for token in sentence.tokens:
                model = {
                    "id": token.id,
                    "text": token.text
                }
                tokens.append(model)
            list_sentence.append(tokens)
        return list_sentence

    def tokenize_by_spacy(self,text,verbose=False):
        processors={"tokenize":'spacy'}
        nlp = stanza.Pipeline(lang='en', processors=processors,verbose=verbose,use_gpu=self.use_gpu)
        doc = nlp(text)
        list_sentence=[]
        for i, sentence in enumerate(doc.sentences):
            if self.should_print_result:
                print(f'====== Sentence {i + 1} tokens =======')
                print(*[f'id: {token.id}\ttext: {token.text}' for token in sentence.tokens], sep='\n')
            tokens=[]
            for token in sentence.tokens:
                model = {
                    "id": token.id,
                    "text": token.text
                }
                tokens.append(model)
            list_sentence.append(tokens)
        return list_sentence

    def mwt_expand(self,text,lang='en',processors='tokenize,mwt',verbose=False):

        nlp = stanza.Pipeline(lang=lang, processors=processors,verbose=verbose,use_gpu=self.use_gpu)
        doc = nlp(text)
        list_result=[]
        for sentence in doc.sentences:
            list_token=[]
            for token in sentence.tokens:
                if self.should_print_result:
                    print(f'token: {token.text}\twords: {", ".join([word.text for word in token.words])}')
                model={
                    "token":token.text,
                    "text":", ".join([word.text for word in token.words])
                }
                list_token.append(model)
            list_result.append(list_token)
        return list_result

    def tag_chinese(self,text,lang='zh',processors='tokenize,lemma,pos,depparse',verbose=False,tokenize_pretokenized=False):
        return self.tag(text,lang,processors,verbose=verbose,tokenize_pretokenized=tokenize_pretokenized)

    def tag(self,text,lang='en',processors='tokenize,mwt,pos',verbose=False,tokenize_pretokenized=False):
        nlp = stanza.Pipeline(lang=lang, processors=processors,verbose=verbose,tokenize_pretokenized=tokenize_pretokenized,use_gpu=self.use_gpu)
        doc = nlp(text)
        if self.should_print_result:
            print(
                *[f'word: {word.text}\tupos: {word.upos}\txpos: {word.xpos}\tfeats: {word.feats if word.feats else "_"}' for
                  sent in doc.sentences for word in sent.words], sep='\n')
        list_result=[]
        for sent in doc.sentences:
            for word in sent.words:
                model={
                    "word":word.text,
                    "upos":word.upos,
                    "xpos":word.xpos,
                    "feats":word.feats if word.feats else "_"
                }
                list_result.append(model)
        return list_result

    def parse_dependency_chinese(self,text,lang='zh',processors='tokenize,lemma,pos,depparse',verbose=False):
        return self.parse_dependency(text,lang,processors,verbose=verbose)

    def parse_dependency(self,text,lang='en',processors='tokenize,mwt,pos,lemma,depparse',verbose=False):
        nlp = stanza.Pipeline(lang=lang, processors=processors,verbose=verbose,use_gpu=self.use_gpu)
        doc = nlp(text)
        if self.should_print_result:
            print(*[
            f'id: {word.id}\tword: {word.text}\thead id: {word.head}\thead: {sent.words[word.head - 1].text if word.head > 0 else "root"}\tdeprel: {word.deprel}'
            for sent in doc.sentences for word in sent.words], sep='\n')
        list_result = []
        for sent in doc.sentences:
            for word in sent.words:
                model = {
                    "id": word.id,
                    "text": word.text,
                    "head id": word.head,
                    "head": sent.words[word.head - 1].text if word.head > 0 else "root",
                    "deprel":word.deprel
                }
                list_result.append(model)
        return list_result

    def ner(self,text,lang='en',processors='tokenize,ner',verbose=False,tokenize_pretokenized=False):
        nlp = stanza.Pipeline(lang=lang, processors=processors,verbose=verbose,tokenize_pretokenized=tokenize_pretokenized,use_gpu=self.use_gpu)
        doc = nlp(text)
        if self.should_print_result:
            print(*[f'entity: {ent.text}\ttype: {ent.type}' for ent in doc.ents], sep='\n')
        list_result=[]
        for ent in doc.ents:
            model={
                "entity":ent.text,
                "type":ent.type
            }
            list_result.append(model)
        return list_result

    def ner_chinese(self,text,lang='zh',processors='tokenize,ner',verbose=False,tokenize_pretokenized=False):
        return self.ner(text,lang,processors,verbose=verbose,tokenize_pretokenized=tokenize_pretokenized)

    def ner_token_chinese(self,text,lang='zh',processors='tokenize,ner',verbose=False):
        return self.ner_token(text,lang,processors,verbose=verbose)

    def ner_token(self,text,lang='en',processors='tokenize,ner',verbose=False):
        nlp = stanza.Pipeline(lang=lang, processors=processors,verbose=verbose,use_gpu=self.use_gpu)
        doc = nlp(text)
        if self.should_print_result:
            print(*[f'token: {token.text}\tner: {token.ner}' for sent in doc.sentences for token in sent.tokens], sep='\n')
        list_result=[]
        for sent in doc.sentences:
            for token in sent.tokens:
                model = {
                    "token": token.text,
                    "ner": token.ner,
                    "pos":token.pos
                }
                list_result.append(model)
        return list_result

    def sentiment_chinese(self,text,lang='zh',processors='tokenize,sentiment',verbose=False):
        return self.sentiment(text,lang=lang,processors=processors,verbose=verbose)

    def sentiment(self,text,lang='en',processors='tokenize,sentiment',verbose=False):
        nlp = stanza.Pipeline(lang=lang, processors=processors,verbose=verbose,use_gpu=self.use_gpu)
        doc = nlp(text)
        list_result=[]
        for i, sentence in enumerate(doc.sentences):
            # print(i, sentence.sentiment)
            model={
                "sentence":sentence.text,
                "sentiment":sentence.sentiment
            }
            list_result.append(model)
        return list_result

    def lang(self,list_text,lang="multilingual",langid_clean_text=False,verbose=False):
        stanza.download(lang="multilingual")
        nlp = Pipeline(lang=lang, processors="langid",langid_clean_text=langid_clean_text,verbose=verbose,use_gpu=self.use_gpu)
        docs =list_text
        docs = [Document([], text=text) for text in docs]
        nlp(docs)
        if self.should_print_result:
            print("\n".join(f"{doc.text}\t{doc.lang}" for doc in docs))
        list_result=[]
        for doc in docs:
            model={
                "text":doc.text,
                "lang":doc.lang
            }
            list_result.append(model)
        return list_result

    def lang_multi(self,list_text,func_process=None,download_lang=""):
        if download_lang!="":
            for l in download_lang.split(","):
                stanza.download(lang=l)
        nlp = MultilingualPipeline()
        docs=list_text
        docs = nlp(docs)
        list_result=[]
        for doc in docs:
            if  self.should_print_result:
                print("---")
                print(f"text: {doc.text}")
                print(f"lang: {doc.lang}")
                print(f"{doc.sentences[0].dependencies_string()}")
            model={
                "text":doc.text,
                "lang":doc.lang,
                "doc":doc
            }
            if func_process!=None:
                func_process(model)
            list_result.append(model)
        return list_result

    def print_result(self,result):
        if result==None or len(result)==0:
            print("No Result!")
            return
        for idx,item in enumerate(result):
            print(idx)
            if type(item)==dict:
                fields = list(result[0].keys())
                print('\t\t'+ '\t'.join(fields))
                list_v=[]
                for k in item.keys():
                    list_v.append(str(item[k]))
                line = '\t'.join(list_v)
                print(f"\t\t{line}")
            elif type(item)==list:
                fields = list(item[0].keys())
                print('\t\t' + '\t'.join(fields))
                for idx1,li in enumerate(item):
                    # print('\t-',idx1)
                    if type(li)==dict:
                        list_v=[]
                        for k in li.keys():
                            list_v.append(str(li[k]))
                            # print(f"\t\t{k}\t{li[k]}")
                        line='\t'.join(list_v)
                        print(f"\t\t{line}")
                    else:
                        print('\t\t',li)

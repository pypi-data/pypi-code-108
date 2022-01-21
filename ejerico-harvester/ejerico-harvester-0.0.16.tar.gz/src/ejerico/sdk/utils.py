"""TODO doc"""

import itertools
import inspect
import hashlib
import re
import sys
import os
import traceback
import textwrap
import uuid
import logging
import math
import sqlite3

import xmltodict
import langdetect
import requests

import numpy as np
import nltk
import pycountry
import langdetect
import nameparser
import orcid

from datetime import datetime, timedelta
from functools import partial, reduce
from pathlib import Path

from crossref.restful import Works

from geopy.geocoders import Nominatim 
from SPARQLWrapper import SPARQLWrapper,JSON
#from validate_email import validate_email 

from ejerico.sdk.annotations import singleton
from ejerico.sdk.config import ConfigManager

__all__=["format_exception", "xml_to_object"]

def format_exception(e):
    exception_list = traceback.format_stack()
    exception_list = exception_list[:-2]
    exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
    exception_list.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))

    exception_str = "Traceback (most recent call last):\n"
    exception_str += "".join(exception_list)
    
    # Removing the last \n
    exception_str = exception_str[:-1]

    return exception_str

def format_email(email):
    email = email.replace(" at ", "@")
    email = email.replace(" ", "")
    return email

def isPrimitive(obj):
    return not hasattr(obj, '__dict__')

def parseDatetime(date_string, date_format='%Y-%m-%d %H:%M:%S', ignore_time=False):
    for pattern in (date_format, '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S%Z', '%Y-%m-%dT%H:%M:%SZ'):
        try:
            dt = datetime.strptime(date_string, pattern)
            dt = dt.replace(hour=0, minute=0, second=0, microsecond=0) if ignore_time else dt
        except Exception as e: pass
    m = re.match(parseDatetime.re_pattern, date_string)
    if m is not None:
        year = int(m.group("year"))
        month = int(m.group("month"))
        day = int(m.group("day"))

        hour = int(m.group("hour")) if m.group("hour") is not None and not ignore_time else 0 
        minute = int(m.group("minute")) if m.group("minute") is not None and not ignore_time else 0 
        second = int(m.group("second")) if m.group("second") is not None and not ignore_time else 0
        
        timezone = m.group("tz")
        
        return datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)

    logging.warning("[parseDatetime] Error parsing datetime ({}) with format '{}'".format(date_string, date_format))
    return None
parseDatetime.re_pattern = re.compile('(?P<year>[\d]{2,4})(-|/){1}(?P<month>[\d]{2})(-|/){1}(?P<day>[\d]{2})(\w)?(?P<hour>[\d]{2})?(:)?(?P<minute>[\d]{2})?(:)?(?P<second>[\d]{2})?(?P<tz>[a-zA-Z]+)?')

def roundTime(date_time, roundToSeconds=24*60*60):
    if date_time == None : date_time = datetime.now()
    seconds = (date_time.replace(tzinfo=None) - date_time.min).seconds
    rounding = (seconds+roundToSeconds/2) // roundToSeconds * roundToSeconds
    return date_time + timedelta(0,rounding-seconds,-date_time.microsecond)

def camelCaseToSnakeCase(value, sep='_'):
    return ''.join([sep+c.lower() if c.isupper() else c for c in value]).lstrip(sep)

def snakeCaseToCamelCase(value, sep='_'):
    return ''.join(word.title() for word in value.split(sep))

def is_sha1(str_value, return_sha1_string=False):
    match = re.match(is_sha1.re_sha1, str_value)
    return hashlib.sha1(str_value.encode("utf-8")).hexdigest() if return_sha1_string else (match is not None)
is_sha1.re_sha1 = re.compile(r'\b[0-9a-f]{40}\b')

def to_dict_lowercase(value):
    if not isinstance(value, dict): return value
    my_dict = {}
    for k,v in value.items():
        if isinstance(v, dict):
            my_dict[k.lower()] = to_dict_lowercase(v)
        elif isinstance(v, list):
            my_dict[k.lower()] = []
            for l in v:
                if isinstance(l, dict):
                    my_dict[k.lower()].append(to_dict_lowercase(l))
                else:
                    my_dict[k.lower()].append(l)
        else:
            my_dict[k.lower()] = v
    return my_dict


def tokenize_name(name, remove_punctuation=True, min_terms=-1, left_coincidences=1, hash_token=True):
        rst = None
        if name is None or not isinstance(name,str): return None

        if 0 < min_terms:
            tokens = [n for n in name.split(' ')]
            if remove_punctuation: tokens = [re.sub(r"[\W]+","", t) for t in tokens]
            tokens = [t.strip().lower() for t in tokens if "" != t.strip()]

            if min_terms < len(tokens):
                rst = []
                for r in range(min(min_terms,len(tokens)),len(tokens)+1):
                    for t in itertools.combinations(tokens, r):
                        is_valid = True
                        for i in range(left_coincidences):
                            is_valid = is_valid and (t[i] == tokens[i])
                        
                        if is_valid:
                            candidate = ''.join(t)
                            if hash_token:
                                rst.append(hashlib.sha1(candidate.encode("utf-8")).hexdigest())
                            else:
                                rst.append(candidate.encode("utf-8")) 
            else:
                return tokenize_name(name, remove_punctuation=remove_punctuation)
        else:
            if remove_punctuation:
                _name = re.sub(r"[\W]+","", name)
            _name  = _name.strip().lower()
            if re.match(r"[\w]*,[\w]*", _name):
                _name = ' '.join(reversed(_name.split(',')))

            if hash_token:
                rst = [hashlib.sha1(_name.encode("utf-8")).hexdigest()]
            else:
                rst = [_name.encode("utf-8")]
 
        return rst[0] if -1 == min_terms and len(rst) > 0 else rst

def countWordOcurrences(string, word):
    if string is None or word is None: return 0
    rst = len(re.findall(word, string))
    return rst

def url_exists(url):
    response = requests.get(url)
    return response.status_code == 200

def detect_lang(string):
    if not isinstance(string, str): return None
    return langdetect.detect(string)

def geolocate(country=None, locality=None):
    try:
        if country is not None: 
            query = country
            query = "{},{}".format(locality, country) if locality is not None else query
            if query in geolocate.cache:
                rst = geolocate.cache[query]
            else:
                rst = geolocate.locator.geocode(query)
                geolocate.cache[query] = rst
            return (rst.latitude, rst.longitude)
    except Exception as e: pass
    return None
geolocate.cache = {}
geolocate.locator = Nominatim(user_agent="jerico-s3.wp7.5")

def srs_to_uri(srs):
    match = re.match(srs_to_uri.re_pattern_srs, srs if srs is not None else "")
    if match:
        if "EPSG" == match.group("SRS"):
            return "<http://www.opengis.net/def/crs/EPSG/0/{}>".format(match.group("NN"))
        elif "CRS" == match.group("SRS"):
            return "<http://www.opengis.net/def/crs/OGC/1.3/CSR{}>".format(match.group("NN"))
        else:
            logging.warning("[srs_to_uri] missing process logic for SRS: {}".format(srs))
    elif "WSG84" == srs:
        return "EPSG:4326"
    else: 
        return ""
srs_to_uri.re_pattern_srs = re.compile(r"(?P<SRS>\w+):(?P<NN>\d+)")

def is_valid_email(email):
    if email not in is_valid_email.cache:
        #TODO solve depedency problema with pyDNS
        """
        kwargs = {
            "check_regex":True, 
            "check_mx":True, 
            "smtp_timeout":10, 
            "dns_timeout":10, 
            "use_blacklist":True, 
            "debug":False
        }
        is_valid_email.cache[email] = validate_email(email_address=email, **kwargs)
        """
        is_valid_email.cache[email] = bool(re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", email))
    return is_valid_email.cache[email]
is_valid_email.cache = {}

def calculate_sha1_of_file(path):
    f = open(path)
    d = f.read()
    h = hashlib.sha1(str(d).encode("utf-8"))
    h = h.hexdigest()
    return h

def parseHTTPRequestParameters(url, parameter=None):
    query = requests.utils.urlparse(url).query
    params = dict(x.split('=') for x in query.split('&'))
    return params[parameter] if parameter is not None else params

def injectPatchIntoMethod(p_clazz, p_method, p_patch):
    try:
        if not inspect.isclass(p_clazz): return False
        if not inspect.isfunction(p_patch): return False
        if not isinstance(p_method, str): return False

        my_method = getattr(p_clazz, p_method)
        if not hasattr(p_clazz, p_method): return False
        if not inspect.isfunction(my_method): return False

        name = "z__{}__{}".format(my_method.__name__, p_patch.__name__)
        if hasattr(p_clazz, name): return True

        name_patch = "z_impl_{}".format(p_patch.__name__)
        setattr(p_clazz, name_patch, p_patch)

        src = inspect.getsource(my_method)
        src = textwrap.dedent(src)
        src = src.replace("def {}".format(p_method), "def {}".format(name))
        src = "{source}{indent}self.{patch}()".format(source=src,indent=4*' ', patch=name_patch)

        code = compile(src, "", "exec")
        exec(code)

        code = compile("injectPatchIntoMethod._functions['{name}'] = {name}".format(name=name), "", "exec")
        exec(code)
        setattr(p_clazz,p_method, injectPatchIntoMethod._functions[name])
        
        return True
    except Exception as e: 
        logging.error("[injectPatchIntoMethod] exception injecting ({}, {})".format(p_class.__name__, p_method)) 
        return False
injectPatchIntoMethod._functions = {}

def extractDOIMetadata(doi):
    logging.debug("[extractDOIMetadata] entering emthod with param: {}".format(doi))
    rst = extractDOIMetadata._works.doi(doi.replace("https://doi.org/", "")) if doi is not None else None
    return rst
extractDOIMetadata._works = Works()

# def injectPatchIntoFunction(p_function, p_patch):
#     try:
#         if not inspect.isfunction(p_function): return False
#         if not inspect.isfunction(p_patch): return False

#         p_module = inspect.getmodule(p_function)
#         if p_module is None: return False

#         name = "z__{}__{}".format(p_function.__name__, p_patch.__name__)
#         if hasattr(p_module, name): return True

#         name_patch = "z_impl_{}".format(p_patch.__name__)
#         setattr(p_module, name_patch, p_patch)

#         src = inspect.getsource(p_function)
#         src = textwrap.dedent(src)
#         src = src.replace("def {}".format(p_function.__name__), "def {}".format(name))
#         src = "{source}{indent}{patch}()".format(source=src,indent=4*' ', patch=name_patch)

#         code = compile(src, "", "exec")
#         exec(code)

#         code = compile("injectPatchIntoFunction._functions['{name}'] = {name}".format(name=name), "", "exec")
#         exec(code)
#         setattr(p_module, p_function.__name__, injectPatchIntoFunction._functions[name])
        
#         return True
#     except Exception as e: logging.error(e)
# injectPatchIntoFunction._functions = {}

class XmlToObject(object):

    def get_attribute_keys(self):
        if not hasattr(self,"_attribute_keys"):
            self._attribute_keys = self.__get_attribute_keys_impl(self,"")
            self._attribute_keys = [a[1:] if a[0] == '/' else a for a in self._attribute_keys]
        return self._attribute_keys

    def get_attributes(self, re_path, sep='/'):
        if re_path is None: return []
        if not isinstance(re_path,str): return []
        if "" == re_path.strip(): return []

        format_re_path = lambda x: "[a-zA-Z0-9_/]{}".format(x) if x in ('*','+','?') else x
        splitted_re_path = re_path.split(sep)
        splitted_re_path = [format_re_path(a.strip()) for a in splitted_re_path]

        re_path = '/'.join(splitted_re_path)
        re_pattern = re.compile(re_path)
        re_attrs = list(filter(re_pattern.match, self.get_attribute_keys()))

        rst_tmp,rst = [],[]

        if 0 != len(re_attrs):
            valid_term = lambda x: "[a-zA-Z0-9_/]*" != x and "[a-zA-Z0-9_/]?" != x and "[a-zA-Z0-9_/]+" != x
            splitted_re_path = [a for a in splitted_re_path if valid_term(a)]

            re_valid_term = splitted_re_path[-1] if 0!= len(splitted_re_path) else "[a-zA-Z0-9_/]*"
            re_valid_term  = re.compile(re_valid_term)

            for re_attr in re_attrs:
                re_obj = self
                rst_obj = None

                lst_re_attr = re_attr.split(sep)
                while 0 != len(lst_re_attr):
                    my_re_attr = lst_re_attr.pop(0)
                    if re_valid_term.match(my_re_attr): 
                        rst_obj = re_obj.__dict__[my_re_attr]
                    re_obj = re_obj.__dict__[my_re_attr]
                if rst_obj is not  None: rst_tmp.append(rst_obj)

        rst = [r for r in rst_tmp if r not in rst] 
        return rst

    def get_attribute(self, re_path, sep='/'):
        rst = self.get_attributes(re_path)
        return rst[0] if 0 != len(rst) else None

    def __get_attribute_keys_impl(self,obj,path):
        rst = []
        for attr in obj.__dict__.keys():
            if isPrimitive(obj.__dict__[attr]):
                rst.append("{}/{}".format(path,attr))
            else:
                rst.extend([a for a in self.__get_attribute_keys_impl(obj.__dict__[attr],"{}/{}".format(path,attr))])
        return rst

    @staticmethod
    def parseXML(xml, default_class=None, class_mapping={}, prefix_attr="attr_", ignore_namespaces=False, lower_case=False, snake_case=False):
        def map_class(key): 
            return class_mapping[key] if class_mapping is not None and key in class_mapping else default_class

        def rename_key(key):
            key = key.replace('@',prefix_attr) if '@' in key else key
            key = key[key.index(':')+1:] if ignore_namespaces and ':' in key else key
            key = key.replace(':','_')
            key = ''.join(['_'+c.lower() if c.isupper() else c for c in key]).lstrip('_') if snake_case else key
            key = key.lower() if lower_case else key
            return key

        def parseXMLImplementation(my_object, my_data):
            if isinstance(my_data, dict):
                for key,value in my_data.items():
                    my_data_class = map_class(key)
                    my_data_object = my_data_class()
                    key = rename_key(key)

                    if not isPrimitive(value):
                        value = parseXMLImplementation(my_data_object, value)
                        setattr(my_object, key, value)
                    elif isinstance(value, list):
                        lst = []
                        for item in value:
                            my_data_item = my_data_class()
                            lst.append(parseXMLImplementation(my_data_item, item))
                        else:
                            setattr(my_object, key, lst)
                    else:
                        setattr(my_object, key, value)
                return my_object
            elif isinstance(my_data, list):
                lst = []
                for item in my_data:
                    lst.append(parseXMLImplementation(default_class(), item))
                return lst
            else:
                return my_data

        if xml is None: return None
        if not isinstance(xml,str) and not isinstance(xml,bytes): return None

        default_class = XmlToObject if default_class is None else default_class
        my_data = xmltodict.parse(xml)
        my_data = my_data[next(iter(my_data))]

        my_object = default_class()
        my_object = parseXMLImplementation(my_object, my_data)
        return my_object

def xml_to_object(xml, default_class=None, class_mapping={}, prefix_attr="attr_", ignore_namespaces=False, lower_case=False, snake_case=False):
    return XmlToObject().parseXML(xml, default_class=default_class, class_mapping=class_mapping, prefix_attr=prefix_attr, ignore_namespaces=ignore_namespaces, lower_case=lower_case, snake_case=snake_case)

@singleton
class NaturalLanguageManager(object):
    def __init__(self): 
        nltk.download('stopwords')

    def is_humanName(self, name):
        tokens = nltk.tokenize.word_tokenize(name)
        pos = nltk.pos_tag(tokens)
        sentt = nltk.ne_chunk(pos, binary = False)
        
        names = []
        for subtree in sentt.subtrees(filter=lambda t: t.label() == 'PERSON'):
            names.extends([leaf for leaf in subtree.leaves()])
        return True if len(names) > 1 else False

    def extract_keywords(self, text):
        text=text.lower()
        text=re.sub(r"(\d|\W)+"," ",text)

        tokens = nltk.tokenize.word_tokenize(text)
        tokens = [t for t in tokens if len(t)>2]
        
        pos = nltk.pos_tag(tokens)
        tokens = [t[0] for t in pos if t[1].startswith('N')]
        
        tokens = nltk.FreqDist(tokens)
        return [t[0] for t in tokens.most_common(50)]

    def summarize_text(self, text):

        #0. clean not relevant tokens
        text=text.lower()
        text=re.sub(r"(\d|\W)+"," ",text)

        tokens = nltk.tokenize.word_tokenize(text)
        tokens = [t for t in tokens if len(t)>2]
        
        
        #1. tokenize sentences
        sentences = nltk.sent_tokenize(text) 
        total_sentences = len(sentences)

        #2. create F(requency) matrix of the words in each sentence
        matrix_F = self._create_frequency_matrix(sentences)

        #3. create T(erm) F(requenct) matrix
        matrix_TF = self._create_tf_matrix(matrix_F)

        #4. create T(able) for S(entence) per W(ord)
        table_SpW = self._create_sentences_per_words_table(matrix_F) 

        #5. create I(nverse) D(ocument) F(frequency) matrix
        matrix_IDF = self._create_idf_matrix(matrix_F, table_SpW, total_sentences)

        #6. create TF-IDF matrix
        matrix_TF_IDF = self._create_tf_idf_matrix(matrix_TF, matrix_IDF)

        #7. score sentence 
        score_sentences = self._score_sentences(matrix_TF_IDF)

        #8. calcultate threshold
        threshold = self._find_average_score(score_sentences)

        #9. generate summary
        summary = self._generate_summary(sentences, score_sentences, threshold)

        return summary

    def prepare_text(self, text, lang):
        if 2 == len(lang):
            my_lang = [language.name.lower() for language in pycountry.languages if hasattr(language, "alpha_2") and language.alpha_2 == lang]
            lang = my_lang[0] if len(my_lang) else lang
        elif 3 == len(lang):
            my_lang = [language.name.lower() for language in pycountry.languages if hasattr(language, "alpha_2") and language.alpha_2 == lang]
            lang = my_lang[0] if len(my_lang) else lang
    
        stopwords = nltk.corpus.stopwords.words(lang)
        tokens = re.sub(r"[\d|\W]", ' ', text)
        tokens = nltk.tokenize.word_tokenize(tokens.lower())
        tokens = [q for q in tokens if q not in stopwords]
        tokens = [q for q in tokens if len(q)>2]
        return ' '.join(tokens)
        
    def _create_frequency_matrix(self, sentences):
        matrix_F = {}
        stopWords = set(nltk.corpus.stopwords.words("english")) #todo detect lang
        stemmer = nltk.PorterStemmer()
        
        for sentence in sentences:
            table_F = {}
            
            words = nltk.word_tokenize(sentence)
            for word in words:
                word = word.lower()
                word = stemmer.stem(word)
                if word in stopWords: continue
                table_F[word] = table_F[word]+1 if word in table_F else 1
            matrix_F[sentence[:15]] = table_F
        return matrix_F

    def _create_tf_matrix(self, matrix_F):
        matrix_TF = {}
        for sentence, table_F in matrix_F.items():
            table_TF = {}
            count_words_in_sentence = len(table_F)
            for word, count in table_F.items():
                table_TF[word] = count / count_words_in_sentence
            matrix_TF[sentence] = table_TF
        return matrix_TF

    def _create_sentences_per_words_table(self, matrix_F):
        table_SpW = {}
        for sentence, table_F in matrix_F.items():
            for word, count in table_F.items():
                table_SpW[word] = table_SpW[word]+1 if word in table_SpW  else 1
        return table_SpW

    def _create_idf_matrix(self, matrix_F, table_SpW, total_sentences):
        matrix_IDF = {}
        for sentence, table_F in matrix_F.items():
            table_IDF = {}
            for word in table_F.keys():
                table_IDF[word] = math.log10(total_sentences / float(table_SpW[word]))
            matrix_IDF[sentence] = table_IDF
        return matrix_IDF

    def _create_tf_idf_matrix(self, matrix_TF, matrix_IDF):
        matrix_TF_IDF = {}
        for (sentence_1, table_F_1),(sentence_2, table_F_2) in zip(matrix_TF.items(), matrix_IDF.items()):
            table_TF_IDF = {}
            for (word_1, value_1),(word_2, value_2) in zip(table_F_1.items(),table_F_2.items()): 
                table_TF_IDF[word_1] = float(value_1 * value_2)
            matrix_TF_IDF[sentence_1] = table_TF_IDF
        return matrix_TF_IDF

    def _score_sentences(self, matrix_TF_IDF):
        table_SS = {}
        for sentence, table_TF_IDF in matrix_TF_IDF.items():
            score_per_sentence = 0
            words_in_sentence = len(table_TF_IDF)
            for word, score in table_TF_IDF.items():
                score_per_sentence += score
        table_SS[sentence] = score_per_sentence / words_in_sentence
        return table_SS

    def _find_average_score(self, score_sentences):
        sum_score = 0
        for sentence in score_sentences:
            sum_score += score_sentences[sentence]
        return (sum_score / len(score_sentences))
    
    def _generate_summary(self, sentences, score_sentences, threshold):
        count_sentences = 0
        summary = ""
        for sentence in sentences:
            if sentence[:15] in score_sentences and score_sentences[sentence[:15]] >= (threshold):
                summary += " " + sentence
                count_sentences += 1
        return summary

@singleton
class ORCIDResolver(object):

    TAG_GIVENAME = "given-names"
    TAG_FAMILY_NAME = "family-name"
    TAG_EMAIL = "email"

    def __init__ (self):
        self.config = ConfigManager.instance() 
        self.orcid_KEY = self.config.get("orcid_key")
        self.orcid_SECRET = self.config.get("orcid_secret")
        if self.orcid_KEY is not None and self.orcid_SECRET is not None:
            self.orcid_API = orcid.PublicAPI(self.orcid_KEY, self.orcid_SECRET)
        else:
            self.orcid_API = None
    
    def resolve (self, terms):
        logging.debug("[ORCIDResolver:resolve] entering method")
        if self.orcid_API is None: return None
        
        query_terms = []
        for t in terms if isinstance(terms, list) else [terms]:
            
            if isinstance(t, dict):
                for key in t:
                    if "given-names" == key: query_terms.append('given-names: "{}"'.format(t[key]))
                    if "family-name" == key: query_terms.append('family-name: "{}"'.format(t[key]))
                    if "email" == key: query_terms.append('email: "{}"'.format(t[key]))
            elif isinstance(t, str) and re.match(self.resolve._re_pattern_email, t):
                query_terms.append('email: "{}"'.format(terms))
            elif isinstance(t, str): 
                query_terms.append('"{}"'.format(terms))
        else:
            if 0 == len(query_terms): return None
        
        try:
            query = " AND ".join(query_terms)
            if query in self.resolve._cache: return self.resolve._cache[query]
            rst = self.orcid_API.search(query)
            if 1 == len(rst["result"]): 
                self.resolve._cache[query] = rst["result"][0]["url"]
                logging.debug("[ORCIDResolver:resolve] Found ORCID profile({}): {}".format(query, rst["result"][0]["url"]))
                return rst["result"][0]["url"]
        except Exception as e:
            logging.debug("[ORCIDResolver:resolve] something wrong with query({})".format(query))

    resolve._re_pattern_email = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
    resolve._cache = {}

    def buildResolveTerm (self, given_name=None, family_name=None, email=None):
        rst = {}
        if given_name is not None: rst["given-names"] = given_name
        if family_name is not None: rst["family-name"] = family_name
        if email is not None: rst["email"] = email
        return rst

@singleton
class SEADATANETNameResolver(object):

    def __init__(self):
        nltk.download('stopwords')

        self._seadatanet_edmerp_uri = "https://edmerp.seadatanet.org/report/{}"
        self._seadatanet_edmerp_sparql = SPARQLWrapper("https://edmerp.seadatanet.org/sparql/sparql")
        self._seadatanet_edmerp_cache = {}

        self._seadatanet_edmo_uri = "https://edmo.seadatanet.org/report/{}"
        self._seadatanet_edmo_sparql = SPARQLWrapper("https://edmo.seadatanet.org/sparql/sparql")
        self._seadatanet_edmo_cache = {}

    def get_edmerpIDByName(self, name, threshold=0.85):  
        logging.debug("[SEADATANETNameResolver:get_edmerpIDByName] entering method with param '{}'".format(name))

        if re.match(self.get_edmerpIDByName._re_pattern, name): return name

        nameID = hashlib.sha1(name.encode("utf-8")).hexdigest()
        if nameID in self._seadatanet_edmerp_cache:
            if self._seadatanet_edmerp_cache[nameID] is not None: 
                logging.debug("[SEADATANETNameResolver:get_edmerpIDByName] '{}' found in cache: {}".format(name, self._seadatanet_edmerp_cache[nameID]))
            return self._seadatanet_edmerp_cache[nameID]

        edmerpID = None; edmerpNAME=None; best_ratio = 0.0

        ignored_words = self.get_edmerpIDByName._ignored_words

        query_term = self._remove_not_working_speech_tags(name, lang=self._lang_detect(name), ignored_words=ignored_words)
        query_term = [n for n in query_term.split(' ') if '' != n]
        query_term = ".*".join(query_term[:2])
        query_term = ".*{}.*".format(query_term)

        query = self.get_edmerpIDByName._seadatanet_edmerp_query.format(name=query_term)
        query = query.replace('\n', '')
        
        self._seadatanet_edmerp_sparql.setReturnFormat(JSON)
        self._seadatanet_edmerp_sparql.setQuery(query) 
        self._seadatanet_edmerp_sparql.method = 'GET'
        
        results = self._seadatanet_edmerp_sparql.query().convert()
        if "results" in results and  "bindings" in results["results"]:
            for result in results["results"]["bindings"]:
                s = result["s"]["value"]; o = result["o"]["value"]

                a = self._remove_not_working_speech_tags(name, lang=self._lang_detect(name), ignored_words=ignored_words, as_list=True); 
                b = self._remove_not_working_speech_tags(o, lang=langdetect.detect(o), ignored_words=ignored_words, as_list=True)
                current_ratio = self._cosine_similarity(a, b)
                if best_ratio < current_ratio:
                    edmerpID  = s
                    edmerpNAME = o 
                    best_ratio = current_ratio

        if edmerpID is not None:
            self._seadatanet_edmerp_cache[nameID] = None 
            if threshold < best_ratio:
                logging.debug("[get_edmerpIDByName] found match '{}' (ratio: {})".format(edmerpNAME, best_ratio))
                self._seadatanet_edmerp_cache[nameID] = edmerpID
            elif 0.7 < best_ratio: 
                logging.warning("[get_edmerpIDByName] found candidate '{}' (ratio: {})".format(edmerpNAME, best_ratio))
            
        
        edmerpID = None if best_ratio < threshold else edmerpID
        edmerpID = UnknowRegisterHandler.instance().resolveUnknown("project", name) if edmerpID is None else edmerpID 
        return edmerpID
    get_edmerpIDByName._seadatanet_edmerp_query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dbpedia: <http://dbpedia.org/ontology/>
        PREFIX geo: <http://schema.geolink.org/1.0/base/main#>

        SELECT DISTINCT ?s ?o
        WHERE
        {{ 
            {{ 
                ?s rdf:type dbpedia:ResearchProject.
                ?s rdfs:label ?o.
                FILTER regex(?o, '{name}', 'i'). 
            }}
        UNION
            {{
                ?s rdf:type dbpedia:ResearchProject.
                ?s geo:hasAcronym ?o.
                FILTER regex(?o, '{name}', 'i').
            }}
        }}
        ORDER BY strlen(str(?o))
    """
    get_edmerpIDByName._ignored_words = ["marine", "monitoring", "water", "management", "system", "research", "ecosystem", "study", "data", "pollution", "dynamics", "climate", "impact", "development", "waters", "area", "fisheries", "project", "zone", "assessment"]
    get_edmerpIDByName._re_pattern = re.compile(r"https://edmerp.seadatanet.org/report/([\d])")

    def get_edmoIDByName(self, name, threshold=0.85):
        logging.debug("[SEADATANETNameResolver:get_edmoIDByName] entering method with param '{}'".format(name))

        if re.match(self.get_edmoIDByName._re_pattern, name): return name

        nameID = hashlib.sha1(name.encode("utf-8")).hexdigest()
        if nameID in self._seadatanet_edmo_cache: 
            if self._seadatanet_edmo_cache[nameID] is not None: 
                logging.debug("[SEADATANETNameResolver:get_edmoIDByName] '{}' found in cache: {}".format(name, self._seadatanet_edmo_cache[nameID]))
            return self._seadatanet_edmo_cache[nameID]

        if re.match(self.get_edmoIDByName._re_pattern_0001, name):
            m = re.match(self.get_edmoIDByName._re_pattern_0001, name)
            edmoID = self.get_edmoIDByName._uri_pattern.format(m.group("EDMO"))
            self._seadatanet_edmo_cache[nameID] = edmoID
            return edmoID

        ignored_words = self.get_edmoIDByName._ignored_words

        edmoID = None; edmoNAME=None; best_ratio = 0.0

        query_term = self._remove_not_working_speech_tags(name, lang=self._lang_detect(name), ignored_words=ignored_words)
        query_term = [n for n in query_term.split(' ') if '' != n]
        query_term = ".*".join(query_term[:2])
        query_term = ".*{}.*".format(query_term)

        query = self.get_edmoIDByName._seadatanet_edmo_query.format(name=query_term)
        query = query.replace('\n', '')
        
        self._seadatanet_edmo_sparql.setReturnFormat(JSON)
        self._seadatanet_edmo_sparql.setQuery(query) 
        self._seadatanet_edmo_sparql.method = 'GET'
        
        results = self._seadatanet_edmo_sparql.query().convert()
        if "results" in results and  "bindings" in results["results"]:
            for result in results["results"]["bindings"]:
                s = result["s"]["value"]; o = result["o"]["value"]

                a = self._remove_not_working_speech_tags(name, lang=self._lang_detect(name), ignored_words=ignored_words, as_list=True); 
                b = self._remove_not_working_speech_tags(o, lang=langdetect.detect(o), ignored_words=ignored_words, as_list=True)
                current_ratio = self._cosine_similarity(a, b)
                if best_ratio < current_ratio:
                    edmoID  = s
                    edmoNAME = o 
                    best_ratio = current_ratio

        if edmoID is not None:
            self._seadatanet_edmo_cache[nameID] = None 
            if threshold < best_ratio:
                logging.debug("[get_edmoIDByName] found match '{}' (ratio: {})".format(edmoNAME, best_ratio))
                self._seadatanet_edmo_cache[nameID] = edmoID
            elif 0.7 < best_ratio: 
                logging.warning("[get_edmoIDByName] found candidate '{}' (ratio: {})".format(edmoNAME, best_ratio))
            
        
        edmoID = None if best_ratio < threshold else edmoID
        edmoID = UnknowRegisterHandler.instance().resolveUnknown("organization", name) if edmoID is None else edmoID 
        return edmoID
    get_edmoIDByName._seadatanet_edmo_query = "SELECT DISTINCT ?s ?o WHERE {{ ?s <http://www.w3.org/2004/02/skos/core#prefLabel> ?o. FILTER regex(?o, '{name}', 'i'). }} order by strlen(str(?o))"
    get_edmoIDByName._ignored_words = ["university", "department", "research", "institute", "marine", "sciences", "centre", "environment", "school", "science", "fisheries", "laboratory", "earth", "water", "state", "technology", "faculty", "laboratoire", "engineering", "biology"]
    get_edmoIDByName._re_pattern = re.compile(r"https://edmo.seadatanet.org/report/([\d])")
    get_edmoIDByName._re_pattern_0001 = re.compile(r"([\w\W]*)(edmo:([ ]*)(?P<EDMO>[\d]+))([\w\W]*)")
    get_edmoIDByName._uri_pattern = re.compile("https://edmo.seadatanet.org/report/{}")
    
    def _remove_not_working_speech_tags(self, name, ignored_words=[], lang=None, as_list=False):
        lang = "english" #languageFromISOCode(lang) if 2 == len(lang) else lang    
        stopwords = nltk.corpus.stopwords.words(lang)
        
        tokens = re.sub(r"[\W]", ' ', name)
        tokens = nltk.tokenize.word_tokenize(tokens.lower())
        tokens = [q for q in tokens if q not in ignored_words]
        tokens = [q for q in tokens if q not in stopwords]
        tokens = [self._countryFromISOCode(q.upper()) if 2==len(q) else q for q in tokens]
        tokens = [q[0] for q in nltk.pos_tag(tokens) if q[1] not in self._remove_not_working_speech_tags._nltk_speech_tags]
        
        return tokens if as_list else  ' '.join(tokens)
    _remove_not_working_speech_tags._nltk_speech_tags = [
        "CC", 
        "DT", 
        "IN", 
        "PRP", 
        "PRP$", 
        "UH", 
        "WDT",
    ]

    def _languageFromISOCode(self, code):
        lang = "english"
        try:
            lang = pycountry.languages.get(alpha_2=code).name.lower()
        except: 
            lang = code
        return lang

    def _countryFromISOCode(self, code):
        country = code
        try:
            country = pycountry.countries.get(alpha_2=code).name.lower()
        except: pass
        return country
            
    def _cosine_similarity(self, a,b):
        a_set = {w for w in a} 
        b_set = {w for w in b}

        a_vector = []; b_vector = []
        
        # form a set containing keywords of both strings 
        keywords = a_set.union(b_set) 
        for keyword in keywords:
            a_vector.append(1 if keyword in a_set else 0)
            b_vector.append(1 if keyword in b_set else 0)

        a_vector = np.array(a_vector)
        b_vector = np.array(b_vector)

        rst = np.inner(a_vector, b_vector) / (np.linalg.norm(a_vector) * np.linalg.norm(b_vector))
        rst = (rst - (-1)) / (1 - (-1))
        
        return rst

    def _lang_detect(self,name):
        try:
            return langdetect.detect(name)
        except Exception: pass
        return "en"

@singleton
class UnknowRegisterHandler(object):
    def __init__(self):
        self.db = None
        self.cache = {}
        self.tables = []
        
        path = self._getPathInternalDB()
        try:
            self.db = sqlite3.connect(path, check_same_thread=False)
        except sqlite3.Error as e:
            logging.info("[UnknowRegisterHandler:__init__] error opening 'unknown register' db ({}): {}".format(path, e))
            
    def _getPathInternalDB(self):
        config = ConfigManager.instance() 
        path = None
        if sys.platform == "linux" or sys.platform == "linux2":
            path = "{}{}.ejerico".format(str(Path.home()), os.sep)
            os.makedirs(path, exist_ok=True)
            path = "{}{}harvester_unknown_register.db".format(path, os.sep)
        elif sys.platform == "darwin":
            path = "{}{}.ejerico".format(str(Path.home()), os.sep)
            os.makedirs(path, exist_ok=True)
            path = "{}{}harvester_unknown_register.db".format(path, os.sep)
        elif sys.platform == "win32":
            path = "{}{}.ejerico".format(str(Path.home()), os.sep, mode)
            os.makedirs(path, exist_ok=True)
            path = "{}{}harvester_unknown_register.db".format(path, os.sep)

        try:
            url = "{}/harvester_unknown_register.db".format(self.config.get("unknown_register_url", default="http://example.com"))
            response = requests.get(url, stream=True)
            with open(path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8*1024): f.write(chunk)
        except Exception as e: pass

        return path

    def resolveUnknown(self, scope, concept):
        if "{}:{}".format(scope.upper(), concept) in self.cache: 
            return self.cache["{}:{}".format(scope.upper(), concept)]

        scope = scope.upper()
        concept = concept.strip().lower()

        rst = None
        try:
            conn = self.db
            cur = conn.cursor()
            
            if concept.upper() not in self.tables:
                stm = self.resolveUnknown._STM_QUERY_TABLE.format(scope)
                cur.execute(stm)
                rows = cur.fetchone()
                if rows is None or 0 == rows[0]:
                    stm = self.resolveUnknown._STM_CREATE_TABLE.format(scope) 
                    cur.execute(stm)
                    self.tables.append(scope.upper())

            stm = self.resolveUnknown._STM_QUERY_CONCEPT.format(scope, concept)
            cur.execute(stm)
            for row in cur.fetchall():
                if row[0] is None: continue
                self.cache["{}:{}".format(scope, concept)] = rst = row[0] 
            conn.commit()

            if rst is None: self.registerUnknown(scope, concept)
        except sqlite3.Error as e:
            logging.info("[UnknowRegisterHandler:resolveUnknown] error resolving '{}:{}' ({})".format(scope, concept, e))
        return rst
    resolveUnknown._STM_QUERY_TABLE = '''
        SELECT count(name) FROM sqlite_master WHERE type='table' AND name='UNKNOWN_{}'
    '''
    resolveUnknown._STM_QUERY_CONCEPT = '''
        SELECT value FROM "UNKNOWN_{}" WHERE name = '{}'
    '''
    resolveUnknown._STM_CREATE_TABLE = '''
        CREATE TABLE IF NOT EXISTS "UNKNOWN_{}" (
	        "name"	TEXT,
	        "value"	TEXT,
	        PRIMARY KEY("name")
        )
    '''

    def registerUnknown(self, scope, concept):
        scope = scope.upper()
        concept = concept.strip().lower()

        try:
            conn = self.db
            cur = conn.cursor()
            stm = self.registerUnknown._STM_INSERT_CONCEPT.format(scope, concept)
            cur.execute(stm)
            conn.commit()
            self.cache["{}:{}".format(scope, concept)] = None
        except sqlite3.Error as e:
            logging.info("[UnknowRegisterHandler:registerUnknown] error registering '{}:{}' ({})".format(scope, concept, e))
    registerUnknown._STM_INSERT_CONCEPT = '''REPLACE INTO "UNKNOWN_{}" ("name", "value") VALUES('{}', NULL)'''
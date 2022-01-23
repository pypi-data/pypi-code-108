from typing import Union

from nlu.pipe.extractors.extractor_configs_HC import *
from enum import Enum

# TODO pre-defined schema time for extracotrs
# TODO universe module with all overview files, components and namespaces in this sexy format
from nlu.universe.annotator_class_universe import AnnoClassRef
from nlu.universe.atoms import JslUniverse, JslAnnoId
from nlu.universe.component_universes import ComponentMap
from nlu.universe.feature_node_ids import NLP_NODE_IDS, NLP_HC_NODE_IDS, OCR_NODE_IDS
from nlu.universe.feature_node_universes import NlpFeatureNode, NlpHcFeatureNode, OcrFeatureNode, \
    NLP_FEATURE_NODES, OCR_FEATURE_NODES, NLP_HC_FEATURE_NODES
from nlu.universe.feature_resolutions import OcrFeatureResolutions, NlpHcFeatureResolutions, NlpFeatureResolutions
from nlu.universe.feature_universes import NLP_FEATURES, OCR_FEATURES, NLP_HC_FEATURES
from nlu.universe.logic_universes import NLP_LEVELS, AnnoTypes
from nlu.universe.universes import ComponentBackends


# ___________________________ GENERAL NOTES FOR CORE LIB______________________-
"""
# TODO COOL FEATURE :
Simple ExternalNode to extend for public facing usiers
Enables creation of custom Spark NLP Pipelines, t
he ExternalNodes become embelished in a way that they fit into Spark NLP/Vanilla Spark Pipes and support Distribution in clusters!!!
    -Boom!

 
"""


"""TODO FIXED EXPLOSION LOGIC: 
If there are multiple Annotators of Sub/Super levels,
we can still get clean output by Exploding Row-wise on the col whose corrosponding value is LONGES

Since we always explode on array cols, the question is which to explode,
In the easy case, we can zip(token, stem, lema)
but
zip(token, stem, clean_tokens)
can fail in PANDAS (but not spark) because not equal lengths !!!
So we must check for each row, which which col is longest and explode on that..

Or just view it as seperate output level and leave it as that

But aaalso multiple NERS have the SAME!!! Issue!!
How to handle 

s = "Billy has history of cancer, leukima, low blood pressure"
nlu.load('med_ner ner.names').predict(s)
med_entities = ['cancer', 'leukima', 'low blood pressure']
name_entities = ['Billy']
So Now there are 2 explode and display options
1 Row per name_entity or 1 row per med entity?
OOOR We do god Damn Padding Like spark Would do???

-->
|med_ner_chunk    |name_ner_chunk| Full sentence |
|-----------------|--------------|---------------|
| cancer          | Billy        | Billy has.... |
| leukima         | None         | Billy has.... |
| low blod..      | None         | Billy has.... |







"""
"""FEATURE IDEA 
NLP PROPHET: 
We can re-create every model in modelshub, IF we have the link to dataset.
This now is a train/test dataset for a Meta-ML engine
X = Pipe-Config
Y = Pipe-Accuracy
"""
"""HF DATASET MODEL SNAP:
Loop over all Datasets in HF Datasets and Generate a model and auto-upload to
modelshub!
"""



# Auto-retrain all common problems with NLU and NEW embeds! --> Free models with each new Embeds and retran entire m
# dfs = nlu.load('extract_tables ').predict('mypdf') # --> Pandas DF returns 1 Row Per Table detected. But each row easily Unpackable to extra Pandas DF that represents the table
# for df in dfs.tables: nlu.load('sent').predict(df)
# for df in dfs : nlu.fit(df).upload(metadata) # Tuesday session! Upload all models BAR Plot distribution of Tasks!
"""

Generate Dataset Topic and TASK distribution
If many finacne datasets -> Fin NLP Lib!
View What HF can do what we cannot do


nlu.load_dataset()
"""

# nlu.load('pdf2text med_ner').predict(ocr_level ='page', nlp_level ='document') # EACH PAGE is a seperate doc/row
# nlu.load('pdf2text med_ner').predict(ocr_level ='file', nlp_level ='document') # EACH FILE is a seperate doc/row
# nlu.load('pdf2text med_ner').predict(ocr_level ='object', nlp_level ='document') # EACH OBJ is a seperate doc/row



""":cvar

nlu.detect_lang=True # Global
nlu.default_lang='en' , 'xx', 'auto_detect' # Global
nlu.optimization_strategy = 'speed'
nlu.load('pdf2text lemmatimze sentiment').predict(pdf, detect_lang=True) # Dynamically load ENG/DE models by detectling

text -> document -> Tok -> .... Sentiment

nlu.load('jpg2text   med_ner').predict('
nlu.load(ocr =True, 'med_ner').predict('/path/to/img.jpg') # 

jpg->  jpg2pdf 
jpg->  jpg2text
jpg->  jpgResacle 

nlu.loadl('image_rotate image_autoscale image2text med_ner).predict(pdf)

pdf->  (image_rotate image_autoscale image2text)      -> med_ner 

pdf->  (image_rotate image_autoscale image2text)->Spell      -> med_ner 
pdf->  (image_rotate image_autoscale image2text)Lema->Stem->->Spell      -> med_ner 


nlu.load('image_rotate med_ner').predict(INPUT_NODE)

input_node->  image_rotate->( img2text->)med_ner 




analze inpt data which effect pipeline search/generation + Lang detect from data
optimize for accuracy/speed/balance
Accuracy for papaer 
speed for edge fast case 
balance for most users 


"""


# _____ Helper extension enum ______ (UNUSED BELOW)
class EnumExtended(Enum):
    """Extended Enum with iterable helper methods"""

    @classmethod
    def get_iterable_values(cls):
        # get_iterable_values = lambda x :  [v.value for v in x]
        """Returns iterable list of values from dataclass"""
        return [v.value for v in list(cls)]

# @dataclass
# class ComponentConstructorArgs:
#     """
#     Arguments for creating a NLU component
#
#     """
#     # TODO encode output_level
#     ## TODO pretty __repr__ or __to__string() method! Leverage  SparkNLPExtractor fields
#     # These 4 Params are required for construction, rest is optional.. deducted dynamically from nlu_ref to build any type of NluComponent
#     nlp_ref: str
#     nlu_ref: str
#     anno_class: JslAnnoId  # Input/Output TYPE # What annotator class is the model for ? IMMUTABLE
#     lang: str = 'en'
#     bucket: Optional[str] = None  # None for OpenSource and ??? fopr healthcare
#     reason: str = ''  # Why was this component added to the component_list. TODO integrate/optional
#     is_licensed: bool = False
#     get_default_model: bool = False  # Input/Output TYPE  # Should load default model for this Component class? If true, will ignore nlu/nlp ref
#     get_trainable_model: bool = False  # Input/Output TYPE  # Should load default model for this Component class? If true, will ignore nlu/nlp ref
#     model: AnnotatorTransformer = None  # Optionally a Spark NLP Annotator can be provided and wrapped as component. If provided, no annotator wi be created.
#     infer_anno_class: bool = False  # Wether to use input param anno_class or to deduct it from nlu ref and nlp ref, i.e. Type Deduction TODO this is currently called do_ref_checks
#     loaded_from_pretrained_pipe: bool = False  # If loaded from pretrained Spark NLP pipeline. In this case model param should not be None
#     trainable_config: NluTrainConfig = False  # TODO
#     # trained_on_dataset: NluTrainConfig = False  # TODO

# __________ Embelishment of logical building blocks in our universe for various domain specifc concepts_________
class DatasetReferences:
    """Embelishment for Datasets"""

    def get_url_reference(self): pass

    def get_paper_reference(self): pass

    def get_language(self): pass

    def get_task(self): pass


class NluSpell:
    """Embelishment for NLU spells"""

    def get_lang(self): pass

    def get_ano_class(self): pass

    def get_nlp_ref(self): pass

    def get_dataset(self): pass

    def get_model_size(self): pass






# class NluComponentFactory():
#     @staticmethod
#     def create_component(c_args): # v ComponentConstructorArgs
#         """
#         Constrcut 1 Single NLU Component. If used for pretrained component_list, this neeeds a extra clean up call on the final component_list object
#         May construct trainable components
#         """
#
#         anno2compInfo: Dict[
#             JslAnnoId, NluComponent] = ComponentMap.os_components  # TODO test this but this should be fine  {NLP_NODE_IDS.CLASSIFIER_DL :ComponentMap.os_components[NLP_NODE_IDS.CLASSIFIER_DL] } # Todo map anno2 component Constructors
#
#         # Gets
#         # 1. Verify Anno class Ref is correct or deduct it
#         if c_args.infer_anno_class:
#             c_args.anno_class = 'todo infer..'
#             NotImplementedError("TODO")
#
#         # Grab the Base Empty Component for this. TODO make sure this makes fresh objects and NOT POINTERS!!
#         component = anno2compInfo[c_args.anno_class]
#         component.constructor_args = c_args
#         # 2. Load Annotator Class into JVM and to component if its not loaded from Pretrained Spark NLP Pipe
#         if c_args.model and c_args.loaded_from_pretrained_pipe:
#             component.model = c_args.model
#             component.loaded_from_pretrained_pipe = True
#         else:
#             if c_args.get_default_model:
#                 component.model = component.get_default_model()
#             elif c_args.get_trainable_model:
#                 component.model = component.get_trainable_model()
#             else:
#                 component.model = component.get_trainable_model(c_args.lang, c_args.nlp_ref, c_args.bucket)
#                 # TODO handle HDD load here??
#
#         # 3. Set Input/Output Col Names from Disk file(Only afterward init model possible) and only for loaded_from_pretrained_pipe because these are the only cols we may not overwrite
#         if c_args.loaded_from_pretrained_pipe:
#             NotImplementedError("TODO")
#
#         if c_args.is_licensed:  # If Nlu ref was licensed, update license relevant fields
#             component.license
#             # TODO different in OCR???
#             component.provider = ComponentBackends.hc,
#             component.license = Licenses.hc,
#         # THESE ATTRIBUTES ARE SET BY FACTORY! TODO
#
#         component.language = c_args.lang,
#         component.nlu_ref = c_args.nlu_ref,
#         component.nlp_ref = c_args.nlp_ref,
#         component.in_types = component.node.value.ins,
#         component.out_types = component.node.value.outs,
#         component.in_types_default = component.node.value.ins,
#         component.out_types_default = component.node.value.outs,
#
#         # 4. Do the extra shit in  __set_missing_model_attributes__() from SparkNLUComponent ?
#         component = NluComponentFactory.__set_missing_model_attributes__(component)
#         if component.has_storage_ref: component.storage_ref = component.model.getStorageRef()
#
#         # TODO, resolve right away? Maybe as optional parameter, because we still want to support users  giving custom emebeds
#         component.storage_ref_nlu_ref_resolution = None,
#
#         # TODO only for pipelien!! AFTER construction of the entire thing!!!
#         # return ComponentUtils.set_storage_ref_attribute_of_embedding_converters(PipeUtils.set_column_values_on_components_from_pretrained_pipe(constructed_components, nlp_ref, language,path))
#
#     def __set_missing_pipe_attributes__(components: List[NluComponent], c_args, path=None): # c_args: ComponentConstructorArgs
#         """
#         Set missing attributes on pipeline loaded from pretrained SparkNLP Stack or Disk Stored Pipe
#         :param c_args:
#         :param path:
#         :return:
#         """
#         from nlu.pipe.utils.component_utils import ComponentUtils
#         from nlu.pipe.utils.pipe_utils import PipeUtils
#         return ComponentUtils.set_storage_ref_attribute_of_embedding_converters(
#             PipeUtils.set_column_values_on_components_from_pretrained_pipe(
#                 components, c_args.nlp_ref, c_args.lang, path))
#
#     def __set_missing_model_attributes__(component: NluComponent) -> NluComponent:
#         '''
#         For a given Spark NLP model this model will extract the poarameter map and search for input/output/label columns and set them on the model.
#         This is a workaround to undefined behaviour when getting input/output/label columns
#         :param : The model for which the attributes should be set
#         :return: model with attributes properly set
#         '''
#         # TODO for Pipeline Models we should be also RE-SET spark_input/output cols!! I.e. read from disc..
#         # For nlu generated models it does not matter because it can change col names at wil
#         model = component.model
#         for k in model.extractParamMap():
#             if "inputCol" in str(k):
#                 if isinstance(model.extractParamMap()[k], str):
#                     if model.extractParamMap()[k] == 'embeddings':  # swap name so we have uniform col names
#                         model.setInputCols('word_embeddings')
#                     component.spark_input_column_names = [model.extractParamMap()[k]]
#                 else:
#                     if 'embeddings' in model.model.extractParamMap()[k]:  # swap name so we have uniform col names
#                         new_cols = model.model.extractParamMap()[k]
#                         new_cols.remove("embeddings")
#                         new_cols.append("word_embeddings")
#                         model.setInputCols(new_cols)
#                     component.spark_input_column_names = model.extractParamMap()[k]
#
#             if "outputCol" in str(k):
#                 if isinstance(model.model.extractParamMap()[k], str):
#                     if model.model.extractParamMap()[k] == 'embeddings':  # swap name so we have uniform col names
#                         model.model.setOutputCol('word_embeddings')
#                     component.spark_output_column_names = [model.extractParamMap()[k]]
#                 else:
#                     if 'embeddings' in model.extractParamMap()[k]:  # swap name so we have uniform col names
#                         new_cols = model.extractParamMap()[k]
#                         new_cols.remove("embeddings")
#                         new_cols.append("word_embeddings")
#                         model.model.setOutputCol(new_cols)
#                     component.spark_output_column_names = model.extractParamMap()[k]
#
#             # if "labelCol" in str(k):
#             #     if isinstance(self.model.extractParamMap()[k], str) :
#             #         self.component_info['spark_label_column_names'] =  [self.model.extractParamMap()[k]]
#             #     else :
#             #         self.component_info['spark_label_column_names'] =  self.model.extractParamMap()[k]
#             return component


# _____ Pipe Generation _____



"""
OC API
Allow Only file Paths or also Pd Dataframes with binary img data or img matrices?

Potential references
2 Options : 
NOT AUTO INSTALL 
# Should NLU automatically check if iput is a Path, IF ocr component are loaded? or should it be extra path param?
# Load all images in folder ocr_fun. If pdf2text is loaded, grabs only .pdf files.  By default searches folder recursively. Optinally can also pass regex ?



nlu.load('pdf2text').predict('~/images/ocr_fun/`)




nlu.load('pdf2text').predict('~/images/ocr_fun/`, recurisve=False) # No nested search
nlu.load('pdf2text').predict('~/images/ocr_fun/myfile.pdf`, recurisve=False) # No nested search
nlu.load('pdf2text').predict(['~/images/ocr_fun/myfile.pdf`,'~/images/ocr_fun/myfile2.pdf`], recurisve=False) # No nested search

df = pd.DataFrame({'img_path': ['~/images/ocr_fun/myfile.pdf`,'~/images/ocr_fun/myfile2.pdf`.]})

nlu.load('doc2text').predict(df)
nlu.load('img2text')


"""
######## AUTO NLP NOTES AND CODE BELOW


"""SMall problems with NLP Expert AUto ML:
1. We do not store Learning Rate, Batch Size, etc.. Learning parameters..
    1.1 We can run some benchmarks to find them or manually aggregate them
2. 
     
"""

# @dataclass
# class NLP_TRAINABLE_PROBLEM:
#     NLP_ANNO.TRAINABLE_VIVEKN_SENTIMENT = ViveknSentimentApproach
#     = SentimentDLApproach
#     = ClassifierDLApproach
#     = MultiClassifierDLApproach
#     = NerDLApproach
#     = PerceptronApproach

# NLP EXPERT NOTES BELOW!!
## TODO DATASET MODEL PARAMETERS
# Model References should point to NLU alias references/defaults. This way, if underyling models get updated and there are new reccomended models, we just update the NLU reference and it effect all configs in the expert
#
# nlu.set_optimize_goal('fast')
# nlu.set_optimize_goal('accurate')
# # for each alias .fast and .accurate options. i.e. ner.fast or ner.accurate or ner.balanced
# # --> just use benchmarks
# # Transfer Learning on Medical NER and resolver possible
# # Train/test/val , if lang not coverd, use multi-lang
# # Lang classifier no embeds, low mem!
# # WordCoverage for Embeddings to pick best embeddings. Look at OOV metadata to know if coverd
# # model identifier maps to configs
# # Only save the classifier Model OOOR save the entire Pipe
# # Create Extra Metadata to create entire component_list from scratch. Load data from cache pretrained
# # Add flag for ONLINE/OFFLINE (and add docs about cache pretrained)`
# # Add Configure memory and cores
# nlu.load('train.sentiment', optimze_for='balanced', memory={}).predict(df)  # DEFAULT <----
# nlu.load('train.sentiment', optimze_for='speed').predict(df)
# nlu.load('train.sentiment', optimze_for='accuracy').predict(df)
# component_list = nlu.load('train.sentiment')  # auto lang and domain classify
# component_list.predict(df)
#
# component_list.save('my/model')
# component_list = nlu.load('my/model')
# df = nlu.load('my/model').predict
#
# nlu.load("remove_background remove_noise pdf2text lemma xx.robterta train.classifier")
# # LANG - > DOMAIN -> Problem ->
# # ---> Start making list of all NLP domains we cover
# # LR/Batchhsizes not on fited model stored
# nlp_expert = {
#     'en':
#         {
#             'healthcare': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'fast': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing_pipe': {
#                             NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                                 # TODO for each annotator a param object/class?
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             NLP_ANNO.LEMMATIZER: {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             NLP_ANNO.ELMO_EMBEDDINGS: {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#                             'preprocess_order': [NLP_ANNO.CONTEXT_SPELL_CHECKER, NLP_ANNO.LEMMATIZER,
#                                                  NLP_ANNO.ELMO_EMBEDDINGS],
#                             # ideally we define the input/outputs here, so there are no ambigous cases, but can be optional because tedious
#                             'preprocess_input_mapping': [NLP_ANNO.CONTEXT_SPELL_CHECKER, NLP_ANNO.LEMMATIZER,
#                                                          NLP_ANNO.ELMO_EMBEDDINGS]
#                         },
#                     },
#                     'accurate': {{}},  # ...
#                     'balanced': {{}},  # ...
#
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'fast': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'accurate': {{}},  # ...
#                     'balanced': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'oncology': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'radiology': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'twitter': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'reddit': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                             'input_level': 'document',  # Or sentence
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'sentence_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                             'input_level': 'token',
#                         },
#                         'preprocessing': {
#
#                             'tokenize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings'],
#                             'input_mappings':
#                                 {
#                                     'tokens': 'spellcheck',
#                                     'spellcheck': 'lemmatize',
#                                     'lemmatize': 'word_embeddings',
#                                     'word_embeddings': 'ner_dl',
#
#                                 }
#
#                                 ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'marketing': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#         },
#     'fr':
#         {
#             'healthcare': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                                 # TODO for each annotator a param object/class?
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             NLP_ANNO.LEMMATIZER: {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             NLP_ANNO.ELMO_EMBEDDINGS: {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#                             'preprocess_order': [NLP_ANNO.CONTEXT_SPELL_CHECKER, NLP_ANNO.LEMMATIZER,
#                                                  NLP_ANNO.ELMO_EMBEDDINGS]
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'oncology': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'radiology': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'twitter': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'reddit': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'marketing': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#         },
#     'de':
#         {
#             'healthcare': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                                 # TODO for each annotator a param object/class?
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             NLP_ANNO.LEMMATIZER: {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             NLP_ANNO.ELMO_EMBEDDINGS: {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#                             'preprocess_order': [NLP_ANNO.CONTEXT_SPELL_CHECKER, NLP_ANNO.LEMMATIZER,
#                                                  NLP_ANNO.ELMO_EMBEDDINGS]
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'oncology': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'radiology': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'twitter': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'reddit': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'marketing': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#         },
#
# }









##########___________________ OLD GRAPH NLP NOTES  and COPDE BELOW NOT USED


# def get_iterable_NLP_nodes() -> List[NLP_FEATURE_NODES]:
#     """Get an iterable list of every NLP Feature Node"""
#     pass
#
#
# def get_iterable_NLP_HC_nodes() -> List[NLP_FEATURE_NODES]:
#     """Get an iterable list of every NLP Feature Node"""
#     pass
#
#
# def get_iterable_feature_nodes(universe: List[Union[JslUniverse, List[JslUniverse]]]) -> List[
#     Union[NlpFeatureNode, NlpHcFeatureNode, OcrFeatureNode]]:
#     """Get an iterable list of every NLP Feature Node in a universe.
#     If List of Universes is provided, it will merge all the universes into one large,
#     i.e. merging them all into a large list
#
#     """
#     if isinstance(universe, List):
#         pass
#     elif isinstance():
#         pass
#
#     # TODO filter nodes by applicable license
#     nodes = NLP_FEATURE_NODES.get_iterable_values().get_iterable_values() \
#             + NLP_HC_FEATURE_NODES.get_iterable_values() \
#             + OCR_FEATURE_NODES.get_iterable_values()
#     return nodes

# def pre_graph_completion_connector(pipe_to_fix: List[NluComponent]):
#     """
#     If multiple nlu_references are loaded in one call, nlu will try to connect the components in an orderd fashion.
#     ONLY for components originating from non-component_list stacks?
#     from left to right while respecting the `Logical Pipeline Operators` below:
#
#     NLU pipeline composition Operators
#     Whitespace-Operator, i.e. " " --> N-Hop Join
#         nlu.load('glove classifier_dl')
#
#     Arrow-Operator, i.e. "->" --> HARD-Join
#     nlu.load('lemma->spell->T5  lemma->stem-> ')
#
#     Pipeline Concatination, i.e. pipe1 + pipe1
#     p1 = nlu.load('sentiment')
#     p2 = nlu.load('emotion')
#     p3 = p1+p2
#
#
#     We could look N hops back, depending on annotator
#     :return:
#     """
#     if len(pipe_to_fix) <= 1: return pipe_to_fix
#     new_pipe = []
#     while pipe_to_fix:
#         c1 = pipe_to_fix.pop(0)
#         c2 = pipe_to_fix.pop(0)
#
#         find_connection_candidates(c1, c2, 2)
#
#     pass
#
#
# def find_connection_candidates(start: NluComponent, target: NluComponent, hops: int) -> List[List[NluComponent]]:
#     """Try to connect 2 JSl-Nodes Nodes by adding N-Hops many bridge JSL-Nodes between them
#     Since there could be multiple options to arrive at the destionation, multiple paths are returned
#     """
#
#     pass
#
#
# # def find_connection_candidates(start:Union[NluComponent,ExternalFeature], between:NluComponent, target:NluComponent, hops:int)->List[List[NluComponent]]:
# #     """
# #
# #     target_node = 'sentiment'
# #     p = nlu.load(target_node)
# #
# #     start_node = 'Hello abstract world!'
# #     p.predict(start_node)
# #
# #     On a high level,
# #     NLU finds a path between the external input_node defined by predict
# #     and the internal target_node defined by the the nlu_reference.
# #
# #     Nodes between start and target are represented by Annotators.
# #     nlu.load('node1 node2 finalNode').predict('start') can be called with multiple refs, which will
# #     constrain the path from target to finalNode, to go over node1 and afterwards to node2, with as
# #     little as possible BRIDGES between them!
# #
# #     If nlu.load(nlu_spell) is called with multiple spells,
# #
# #
# #
# #     # Node connectivity
# #
# #     ## Bridges
# #     If a Node generates at least ONE feature consumed by another node,
# #     they may be viewed as a bridge that makes travel from one node to the other possible.
# #
# #     ## N-Hop Connectivity
# #     2 Nodes may not be connected directly via output and input features.
# #     For this scenario, N-Hops are defined, which enables multiple bridges to form a larger bridge
# #
# #
# #     """
# #     nodes = get_iterable_feature_nodes() # <--- TODo filter nodes by applicable license
# #     # TODO external node is TARGEt and internal is SOURCE/START!!Makes more sense because thats how we build the graph
# #     partial_paths = []
# #     consumers = [[start]] # TODO external Feature should be a Node? Just has a outs field. This would be text/pdf/etc..
# #      # TODO define missing_input_types() for component_list generation
# #     while consumers:
# #         # TODO remove all nodes from current path that are satisfied and only resolve  rest?
# #         current_path = consumers.pop()
# #
# #         current_node = current_path[-1]
# #         if target in current_path[-1] : partial_paths.append(current_path)
# #
# #         """
# #         TODO Double backtrack, this is like finding the shortest path on a graph, but sometimes we have to take
# #         MULTPLE edges at the same time, where choice in feature producers gives different result
# #
# #         i.e. classifierDL has ins Sentence, Document, Token
# #         Sentence can resolve to SentenceDetectorDL, SentenceDetector
# #         Document can to document
# #         Token can to Tokenizer, RegexTokenizer, MatchTokenzer
# #
# #         CITY SCHNITZELJAG/ SCAVENGER HUNT
# #
# #         We are starting in city S and want to visit city T.
# #         We are a working tavler and only may travelling via working.
# #
# #
# #         Before we can leave a City C, we must peform a list of tasks K[C] in the city.
# #         There are O[K_i] options to perform a particular task K_i for a city.
# #         We must fulfill each todo by choosing one of the options for performing it.
# #
# #         Each of these tasks brings us to a new City, with new tasks todo.
# #         This is how we live our schnitzel live, peforming todos in one city to the next, until we arrive at Target city.
# #
# #         Once we are at target city, we still have to make sure to finish all open TODOs in visited cities.
# #
# #         We are also a Smart Schnitzel fanatic, so we want to plan ahead and want to map out
# #         every unique path in live, that cold bring us to the target city.
# #
# #
# #         Thats NLU, chasing the magical spells, starting from text and ending at magic ;)
# #
# #
# #
# #
# #         Problem Can be viewed like planning a RoadTrip where we start in one City and  want to end in a particular target city.
# #         Additionally, there are  N cities to visits inbetween, and in each City, there are C[N] Things todo.
# #         For each thing C[N] todo, there are K[C[N]] Options .
# #
# #         We need to visit every city and for every item on the TODO list, we must do the thing,
# #         by peforming one to the corrosponding TODO's valid options.
# #         I.e. each todo can be fulfilled various ways.
# #
# #         Also, in each city B, thats not in C[N] but which we are visiting we must fulfill a specific todo list
# #
# #
# #         This is a complete abstraction of the graph problem.
# #         We are looking to generate every possible combination of Paths that
# #
# #
# #         """
# #         for input_feature in current_node.in_types:
# #             # For each feature loop over each node and see if they can connect to form a birdge
# #             SAT_feature_producers = [] # partial solution matches for Path, but complete solution for bridge
# #             # Explore all nodes for producer candaiftes that satisfy input feature
# #             # TODO leverage storage refs?? Some Pipe Configs require Multi-Embeds.
# #             #  We only get Storage Ref, after we instantiate the graph... This means we gotta come back after init the graph to fix this.. Or HARDCODE every storageref somewhere...
# #             #### ---> OOor we just need to onl instantiate embed-consumers Instalty and read out storage-ref. All else get lazy instantiated. This way we resolve in resprect to storage ref
# #             # TODO actually doing BFS yields TOO many possiblities.. we must hardcode some places.. i.e. 3 choies for tokenizer 2 choices for sentence, 10 choices for embeds, etc..
# #             # --> need to hardcode bridges/pre-defines feature resolutions
# #
# #             feature_producer_candidates = get_feature_resolution_candidates(input_feature)
# #
# #             consumers.append(current_path + [node2explore])
# #
#
#
# def get_feature_resolution_candidates(target_feature: JslFeature) -> List[FeatureNode]:
#     """Get all JSL-Anno candidates that generate target_feature  """
#     nodes = get_iterable_feature_nodes()  # <--- TODo filter nodes by applicable license
#     candidates = []
#     for n in nodes:
#         if target_feature in n.outs: candidates.append(n)
#     if len(n) == 0: raise Exception(f"Could not resolve feature={target_feature}")
#     return candidates
#
#
# #
# # def complete_graph(start:NluComponent):
# #     print("Completing graph", start)
# #
# #
# #     required_features = [start.in_types]
# #     while required_features:
# #         # 1. Check what is missing in component_list
# #         get_missing_features() # i.e. missing paths/links
# #
# #         # 2. Resolve missing Features
# #
# #         # 3. Update Stuff
# #
# #         # 4. Extra Pipe Logic, I.e add missing stuff
# #
# #         # TODO 1 hop connection logic
# #         # load('glove classifier_dl')
# #         # Need to connect 2 nodes with intermediate nodes
# #         # --> If
#
#
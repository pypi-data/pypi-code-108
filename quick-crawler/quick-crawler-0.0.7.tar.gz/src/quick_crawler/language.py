import os
from semantickit.lang.wordnet import *
import urllib.request
from deep_translator import GoogleTranslator

lang_data='''
alpha3-b,alpha2,English
aar,aa,Afar
abk,ab,Abkhazian
afr,af,Afrikaans
aka,ak,Akan
alb,sq,Albanian
amh,am,Amharic
ara,ar,Arabic
arg,an,Aragonese
arm,hy,Armenian
asm,as,Assamese
ava,av,Avaric
ave,ae,Avestan
aym,ay,Aymara
aze,az,Azerbaijani
bak,ba,Bashkir
bam,bm,Bambara
baq,eu,Basque
bel,be,Belarusian
ben,bn,Bengali
bih,bh,Bihari languages
bis,bi,Bislama
bos,bs,Bosnian
bre,br,Breton
bul,bg,Bulgarian
bur,my,Burmese
cat,ca,Catalan; Valencian
cha,ch,Chamorro
che,ce,Chechen
chi,zh,Chinese
chu,cu,Church Slavic; Old Slavonic; Church Slavonic; Old Bulgarian; Old Church Slavonic
chv,cv,Chuvash
cor,kw,Cornish
cos,co,Corsican
cre,cr,Cree
cze,cs,Czech
dan,da,Danish
div,dv,Divehi; Dhivehi; Maldivian
dut,nl,Dutch; Flemish
dzo,dz,Dzongkha
eng,en,English
epo,eo,Esperanto
est,et,Estonian
ewe,ee,Ewe
fao,fo,Faroese
fij,fj,Fijian
fin,fi,Finnish
fre,fr,French
fry,fy,Western Frisian
ful,ff,Fulah
geo,ka,Georgian
ger,de,German
gla,gd,Gaelic; Scottish Gaelic
gle,ga,Irish
glg,gl,Galician
glv,gv,Manx
gre,el,"Greek, Modern (1453-)"
grn,gn,Guarani
guj,gu,Gujarati
hat,ht,Haitian; Haitian Creole
hau,ha,Hausa
heb,he,Hebrew
her,hz,Herero
hin,hi,Hindi
hmo,ho,Hiri Motu
hrv,hr,Croatian
hun,hu,Hungarian
ibo,ig,Igbo
ice,is,Icelandic
ido,io,Ido
iii,ii,Sichuan Yi; Nuosu
iku,iu,Inuktitut
ile,ie,Interlingue; Occidental
ina,ia,Interlingua (International Auxiliary Language Association)
ind,id,Indonesian
ipk,ik,Inupiaq
ita,it,Italian
jav,jv,Javanese
jpn,ja,Japanese
kal,kl,Kalaallisut; Greenlandic
kan,kn,Kannada
kas,ks,Kashmiri
kau,kr,Kanuri
kaz,kk,Kazakh
khm,km,Central Khmer
kik,ki,Kikuyu; Gikuyu
kin,rw,Kinyarwanda
kir,ky,Kirghiz; Kyrgyz
kom,kv,Komi
kon,kg,Kongo
kor,ko,Korean
kua,kj,Kuanyama; Kwanyama
kur,ku,Kurdish
lao,lo,Lao
lat,la,Latin
lav,lv,Latvian
lim,li,Limburgan; Limburger; Limburgish
lin,ln,Lingala
lit,lt,Lithuanian
ltz,lb,Luxembourgish; Letzeburgesch
lub,lu,Luba-Katanga
lug,lg,Ganda
mac,mk,Macedonian
mah,mh,Marshallese
mal,ml,Malayalam
mao,mi,Maori
mar,mr,Marathi
may,ms,Malay
mlg,mg,Malagasy
mlt,mt,Maltese
mon,mn,Mongolian
nau,na,Nauru
nav,nv,Navajo; Navaho
nbl,nr,"Ndebele, South; South Ndebele"
nde,nd,"Ndebele, North; North Ndebele"
ndo,ng,Ndonga
nep,ne,Nepali
nno,nn,"Norwegian Nynorsk; Nynorsk, Norwegian"
nob,nb,"Bokmål, Norwegian; Norwegian Bokmål"
nor,no,Norwegian
nya,ny,Chichewa; Chewa; Nyanja
oci,oc,Occitan (post 1500)
oji,oj,Ojibwa
ori,or,Oriya
orm,om,Oromo
oss,os,Ossetian; Ossetic
pan,pa,Panjabi; Punjabi
per,fa,Persian
pli,pi,Pali
pol,pl,Polish
por,pt,Portuguese
pus,ps,Pushto; Pashto
que,qu,Quechua
roh,rm,Romansh
rum,ro,Romanian; Moldavian; Moldovan
run,rn,Rundi
rus,ru,Russian
sag,sg,Sango
san,sa,Sanskrit
sin,si,Sinhala; Sinhalese
slo,sk,Slovak
slv,sl,Slovenian
sme,se,Northern Sami
smo,sm,Samoan
sna,sn,Shona
snd,sd,Sindhi
som,so,Somali
sot,st,"Sotho, Southern"
spa,es,Spanish; Castilian
srd,sc,Sardinian
srp,sr,Serbian
ssw,ss,Swati
sun,su,Sundanese
swa,sw,Swahili
swe,sv,Swedish
tah,ty,Tahitian
tam,ta,Tamil
tat,tt,Tatar
tel,te,Telugu
tgk,tg,Tajik
tgl,tl,Tagalog
tha,th,Thai
tib,bo,Tibetan
tir,ti,Tigrinya
ton,to,Tonga (Tonga Islands)
tsn,tn,Tswana
tso,ts,Tsonga
tuk,tk,Turkmen
tur,tr,Turkish
twi,tw,Twi
uig,ug,Uighur; Uyghur
ukr,uk,Ukrainian
urd,ur,Urdu
uzb,uz,Uzbek
ven,ve,Venda
vie,vi,Vietnamese
vol,vo,Volapük
wel,cy,Welsh
wln,wa,Walloon
wol,wo,Wolof
xho,xh,Xhosa
yid,yi,Yiddish
yor,yo,Yoruba
zha,za,Zhuang; Chuang
zul,zu,Zulu
'''

def get_language_code3(code2):
    # current_path = os.path.dirname(os.path.realpath(__file__))
    # lines=open(current_path+"/data/language-codes-3b2.csv",'r',encoding='utf-8').readlines()
    lines=lang_data.split("\n")
    dict_lang={}
    for line in lines:
        ls=line.strip().split(",")
        if len(ls)<2:
            continue
        dict_lang[ls[1]]=ls[0]
    if code2 in dict_lang:
        return dict_lang[code2]
    else:
        return None

def get_language_code_list():
    # current_path = os.path.dirname(os.path.realpath(__file__))
    # lines=open(current_path+"/data/language-codes-3b2.csv",'r',encoding='utf-8').readlines()
    lines=lang_data.split("\n")
    list_lang=[]
    for line in lines:
        ls=line.strip().split(",")
        if len(ls)<2:
            continue
        list_lang.append(ls[1])
    return list_lang

def get_language_code2(code3):
    # current_path = os.path.dirname(os.path.realpath(__file__))
    # lines=open(current_path+"/data/language-codes-3b2.csv",'r',encoding='utf-8').readlines()
    lines=lang_data.split("\n")
    dict_lang={}
    for line in lines:
        ls=line.strip().split(",")
        if len(ls)<2:
            continue
        dict_lang[ls[0]]=ls[1]
    if code3 in dict_lang:
        return dict_lang[code3]
    else:
        return None

def get_lang3(lang):
    if '-' in lang:
        lang=lang.split("-")[0]
    if '_' in lang:
        lang=lang.split("_")[0]
    return get_language_code3(lang)

def get_lang2(lang):
    if '-' in lang:
        lang=lang.split("-")[0]
    return get_language_code2(lang)



def get_all_related_words(text):
    nltk.download("wordnet")
    nltk.download('omw')
    dict_lang_all = get_all_related_word_from_text(text)
    print()
    for lang in dict_lang_all:
        print(lang, ','.join(dict_lang_all[lang]))
    return dict_lang_all

def get_all_related_words_by_lang(dict_lang_all,lang):
    if lang in dict_lang_all:
        return dict_lang_all[lang]
    else:
        return None



def get_translation(text, target):
    try:
        translated = GoogleTranslator(source='auto', target=target).translate(text)
        # print(translated)
        return translated
    except:
        return None

def get_lang_dict_by_translation(src_lang, to_translate,target_langs=None):
    list_lang = get_language_code_list()
    dict_lang = {}
    dict_lang[src_lang] = to_translate
    for lang in list_lang:
        if target_langs!=None:
            if lang not in target_langs:
                continue
        if lang != src_lang:
            translated = get_translation(to_translate, lang)
            if translated != None:
                dict_lang[lang] = translated
            print(lang, " -> ", translated)
    return dict_lang

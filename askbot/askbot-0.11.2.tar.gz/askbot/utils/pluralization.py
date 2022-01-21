"""pluralization formulae for the supported languages"""
import logging

def arabic(count):
    """six forms for arabic:
    n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 && n%100<=99 ? 4 : 5;\n"""
    if count == 0:
        return 0
    elif count == 1:
        return 1
    elif count == 2:
        return 2
    else:
        rem = count % 100
        if rem >= 3 and rem <= 10:
            return 3
        if rem >= 11 and rem <= 99:
            return 4
    return 5

def germannic(count):
    """two forms for germannic languages"""
    return int(count != 1)

def francoid(count):
    """french, portuguese"""
    return int(count > 1)

def singular(count):
    return 0

def slavic(count):
    """'ru', 'sr', 'hr'"""
    rem10 = count % 10
    rem100 = count % 100
    if rem10 == 1 and rem100 != 11:
        return 0
    elif rem10 >=2 and rem10 <= 4 and (rem100 < 10 or rem100 >= 20):
        return 1
    return 2

def romanian(count):
    if count == 1:
        return 0
    else:
        rem100 = count % 100
        if rem100 > 19 or (count and rem100 == 0):
            return 2
    return 1

def polish(count):
    if count == 1:
        return 0
    else:
        rem10 = count % 10
        rem100 = count % 100
        if rem10 >=2 and rem10 <= 4 and (rem100 < 10 and rem100 >= 20):
            return 1
    return 2

def slovenian(count):
    rem100 = count % 100
    if rem100 == 1:
        return 0
    elif rem100 == 2:
        return 1
    elif rem100 in (3, 4):
        return 2
    return 3

def chech(count):
    if count == 1:
        return 0
    elif count >=2 and count <=4:
        return 1
    return 2

"Plural-Forms: nplurals=3; plural=(n==1) ? 0 : (n>=2 && n<=4) ? 1 : 2;\n"

FORMULAE = {
    'arabic': arabic,
    'germannic': germannic,
    'slavic': slavic,
    'singular': singular,
    'romanian': romanian,
    'slovenian': slovenian,
    'chech': chech,
    'francoid': francoid
}

GERMANNIC_FAMILY = (
    'en', 'bg', 'bg_BG', 'el', 'nb_NO', 'pt', 'ast', 'ca', 'de',
    'it', 'hu', 'hi', 'sv_SE', 'fi', 'he_IL', 'gl', 'es', 'bn_IN'
)

FRANCOID_FAMILY = ('fr', 'pt', 'pt_BR', 'pt-br')

SLAVIC_FAMILY = (
    'ru', 'sr', 'hr'
)

ROMANIAN_FAMILY = ('ro',)
POLISH_FAMILY = ('pl',)
SLOVENIAN_FAMILY = ('sl',)
CHECH_FAMILY = ('cs', 'cs_CZ')

SINGULAR_FAMILY = (
    'zh_HK', 'fa_IR', 'zh_CN', 'id_ID', 'zh_TW', 'ko', 'ms_MY', 'tr', 'tr_TR', 'vi', 'ja', 'uz', 'uz_UZ'
)

def get_formula(lang):
    """returns pluralization formula, default to germannic"""
    if lang == 'ar':
        return arabic
    elif lang in GERMANNIC_FAMILY:
        return germannic
    elif lang in SINGULAR_FAMILY:
        return singular
    elif lang in SLAVIC_FAMILY:
        return slavic
    elif lang in FRANCOID_FAMILY:
        return francoid
    elif lang in ROMANIAN_FAMILY:
        return romanian
    elif lang in POLISH_FAMILY:
        return polish
    elif lang in SLOVENIAN_FAMILY:
        return slovenian
    elif lang in SINGULAR_FAMILY:
        return singular
    logging.critical('language %s not supported by askbot.utils.pluralization' % lang)
    return germannic

def py_pluralize(plural_forms, count):
    from django.utils.translation import get_language
    lang = get_language()
    formula = get_formula(lang)
    num_forms = len(plural_forms)
    form_number = formula(count)
    if form_number >= num_forms:
        template = 'not enough plural forms for %s in language %s'
        logging.critical(template % (str(plural_forms), lang))
        form_number = num_forms - 1
    return plural_forms[form_number]

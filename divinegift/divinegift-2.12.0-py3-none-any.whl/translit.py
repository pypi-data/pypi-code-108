try:
    from transliterate import translit, get_available_language_codes
    from transliterate.discover import autodiscover
    from transliterate.base import TranslitLanguagePack, registry
except ImportError:
    raise ImportError("transliterate isn't installed. Run: pip install -U transliterate")


class ExtendedRussianLangPack(TranslitLanguagePack):
    language_code = 'ru_ext'
    language_name = 'Russian extended'
    mapping = (
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'абцдефгхийклмнопкрстуввкызАБЦДЕФГХИЙКЛМНОПКРСТУВВКЫЗ',
    )
    reversed_specific_mapping = (
        'вВёЁйЙкКэЭыЫьЬъЪ',
        "vVeEiIkKeEyY''''"
    )
    pre_processor_mapping = {
        'shch': 'щ',
        'ya': 'я',
        'ia': 'я',
        'yu': 'ю',
        'iu': 'ю',
        'ch': 'ч',
        'sh': 'ш',
        'x': 'кс',
        'zh': 'ж',
        'ts': 'ц',
        'kh': 'х',
        'SHCH': 'Щ',
        'YA': 'Я',
        'IA': 'Я',
        'YU': 'Ю',
        'IU': 'Ю',
        'CH': 'Ч',
        'SH': 'Ш',
        'X': 'КС',
        'ZH': 'Ж',
        'TS': 'Ц',
        'KH': 'Х',
    }
    reversed_specific_pre_processor_mapping = {
        'ж': 'zh',
        'х': 'kh',
        'ц': 'ts',
        'ч': 'ch',
        'ш': 'sh',
        'щ': 'shch',
        'ю': 'iu',
        'я': 'ia',
        'Ж': 'ZH',
        'Х': 'KH',
        'Ц': 'TS',
        'Ч': 'CH',
        'Ш': 'SH',
        'Щ': 'SHCH',
        'Ю': 'IU',
        'Я': 'IA',
    }


class RussianAftnLangPack(TranslitLanguagePack):
    language_code = 'ru_aftn'
    language_name = 'Russian aftn'
    mapping = (
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'абцдефгхийклмнопщрстужвкызАБЦДЕФГХИЙКЛМНОПЩРСТУЖВКЫЗ',
    )
    reversed_specific_mapping = (
        'вВёЁжЖйЙхХщЩъЪыЫьЬэЭЧкК',
        'wWeEvViIhHqQxXyYxXeE4kK'
    )
    pre_processor_mapping = {
        'ya': 'я',
        'ia': 'я',
        'yu': 'ю',
        'iu': 'ю',
        'ch': 'ч',
        'sh': 'ш',
        'x': 'кс',
        'YA': 'Я',
        'IA': 'Я',
        'YU': 'Ю',
        'IU': 'Ю',
        'CH': 'Ч',
        'SH': 'Ш',
        'X': 'КС',
    }
    reversed_specific_pre_processor_mapping = {
        'ч': 'ch',
        'ш': 'sh',
        'ю': 'iu',
        'я': 'ia',
        'Ш': 'SH',
        'Ю': 'IU',
        'Я': 'IA',
    }


registry.register(ExtendedRussianLangPack, force=True)
registry.register(RussianAftnLangPack, force=True)

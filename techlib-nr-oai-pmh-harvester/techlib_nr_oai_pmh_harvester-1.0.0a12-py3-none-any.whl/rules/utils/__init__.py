import re


def filter_language(el, res: dict = None):
    if not res:
        res = {}
    if isinstance(el, dict):
        for k, v in el.items():
            match = re.fullmatch(r'\w\w_\w\w', k)
            if match:
                res[k] = filter_language(v, res=res)
            else:
                return filter_language(v, res=res)
    if isinstance(el, (list, tuple)):
        list_ = []
        l = len(el)
        for item in el:
            result = filter_language(item, res=res)
            if not result:
                continue
            if isinstance(result, (str, int, float)) and l > 1:
                list_.append(result)
            else:
                return result
        if list_:
            return list_
    if isinstance(el, (str, int, float)):
        return el
    if el is None:
        return el
    return res


def remove_country_from_lang_codes(word_dict):
    return {k[:2]: v for k, v in word_dict.items()}
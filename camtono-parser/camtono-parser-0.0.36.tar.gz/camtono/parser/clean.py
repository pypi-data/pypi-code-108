import re

ENCODING_CHARACTER = "'"


def clean_query(query, sql_dialect) -> str:
    """

    :param query:
    :param sql_dialect:
    :return:
    """
    cleaned_query = strip_comments(query=query)
    cleaned_query = pad_comparisons(query=cleaned_query)
    cleaned_query = clean_spaces(query=cleaned_query)
    return cleaned_query.lower()


def pad_comparisons(query):
    import re
    cleaned_query = re.sub(
        '([\s\(][\d\w\.\_\{\}]*)(<=|>=|<>|==|!=|<|>|=|\|\||::|\+|-|/|\*|~)([\d\w\.\_\{\}]*[\)\s]*)', r' \1 \2 \3',
        query)
    return cleaned_query


def clean_spaces(query) -> str:
    """

    :param query:
    :return:
    """
    cleaned_query = re.sub('\s+', ' ', query)
    cleaned_query = re.sub('\(\s', '(', cleaned_query)
    cleaned_query = re.sub('\s\)', ')', cleaned_query)
    return cleaned_query.strip()


def strip_comments(query) -> str:
    """

    :param query:
    :return:
    """
    return re.sub('((\n)+(\s)*(--)(.+\n))|((\n)+(\s)*(\#)(.+\n))', ' ', query)


def wrap_variables(query, encoding_character='', wrap_character="'", encoded=False):
    """

    :param query:
    :param encoding_character:
    :param wrap_character:
    :param encoded:
    :param skip_characters:
    :param feature_name:
    :return:
    """
    if encoded and encoding_character:
        encoding_character = '\\' + encoding_character
    regex = '(' + encoding_character + '[\w\d\_]*\{\S+\}[\w\d\_]*' + encoding_character + ')'
    variables = set()
    query = re.sub(regex, r"{0}\1{0}".format(wrap_character), query)
    for match in re.findall('(' + wrap_character + '[\w\d\_]*\{\S+\}[\w\d\_]*' + wrap_character + ')', query):
        new_name = match
        variables.add(new_name)

    return query, variables


def unwrap_variables(query, encoding_character='', encoded=False, skip_characters=0):
    if encoded and encoding_character:
        encoding_character = '\\' + encoding_character
    regex = '(' + encoding_character + '[\w\d\_]*\{\S+\}[\w\d\_]*' + encoding_character + ')'
    for match in re.findall(regex, query):
        new_name = match
        new_string = new_name[skip_characters:len(new_name) - skip_characters]
        query = query.replace(
            match,
            new_string
        )
    return query


def prune_ast(json, parent=None):
    """ Recursive function to remove partial or nulled values from the AST

    :param json: json query AST
    :param parent: the parent key of the ast
    :return: cleaned query AST
    """
    pruned = type(json)()
    if isinstance(json, dict):
        for k, v in json.items():
            child = prune_ast(json=v, parent=k)
            if child is not None:
                pruned[k] = child
        pruned = validate_tree(k=parent, json=pruned)
        if pruned == {} and pruned != json:
            pruned = None
    elif isinstance(json, list):
        child_parent = None
        if parent:
            if parent == 'from':
                child_parent = 'from'
            elif parent == 'cross join':
                child_parent = 'cross join'
            elif 'join' in parent:
                child_parent = 'join'
            elif 'where' == 'parent':
                child_parent = 'where'
        for v in json:
            child = prune_ast(json=v, parent=child_parent)
            if child is not None:
                pruned.append(child)
        pruned = validate_tree(k=parent, json=pruned)
    elif json is not None:
        pruned = json

    return pruned


def validate_tree(k, json):
    """ Validates whether the query ast has the required number of values

    :param k: the query key
    :param json: the query AST
    :return: None if invalid and the query_ast if valid.
    """
    from camtono.parser.keywords import min_keys
    if k is None:
        return json
    elif isinstance(json, dict) and any(set(json.keys()) >= set(i) for i in min_keys.get(k, [list(json.keys())])):
        return json
    elif isinstance(json, list) and len(json) >= len(min_keys.get(k, [['value']])[0]):
        return json
    elif any(isinstance(json, i) for i in [str, int, float, bool]):
        return json
    else:
        return None

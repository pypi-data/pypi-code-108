


def tokenizer(target, delim):
    if not target:
        return None

    tokens = []
    for t in target.split(delim):
        t = t.strip()
        if t:
            tokens.append(t)

    return tokens

def trimEmpty(src):
    if src:
        return src.strip()
    else:
        return ''
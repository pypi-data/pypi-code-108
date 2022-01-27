from yamhl.yamhl import YAMHL

toc = YAMHL["toc"]

def toc_fn():
    op = []
    for k, v in toc["links"].items():
        op.append(f'<li><a href="{v or k}"><strong>{k}</strong></a></li>')
    ul = "\n".join(op)
    return f'<ul>\n{ul}\n</ul>'
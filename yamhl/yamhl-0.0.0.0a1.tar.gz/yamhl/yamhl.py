from os import path
from pathlib import Path
from typing import Any, Dict, List
from os import path
from shutil import rmtree, move

import httpx

from .settings import stg
from .utils import ddir, srv_tpl, run

class Constants:
    pass

YAMHL = stg(None, "yamhl.yml")
MD_VARS_YML = ddir(YAMHL, "md_vars")
RMVC = ddir(MD_VARS_YML, "commons")

RULES = ddir(YAMHL, "rules")
PDOC = ddir(YAMHL, "pdoc")

def dd(od: Dict[str, List[str]], *dicts: List[Dict[str, List[str]]]) -> Dict[str, List[str]]:
    for d in dicts:
        for a, v in d.items():
            od[a] = [*(od.get(a, []) or []), *v]
    return od

def rules_fn(rules: Dict[Any, Any], key: str) -> Dict[str, List[str]]:
    _rules = ddir(rules, key)
    return dd({"": ddir(_rules, "del", [])}, ddir(_rules, "repl"))

def op_fn(ip, s: str):
    op = None
    if (_op:= ip.stem) not in ddir(YAMHL, f"{s}_op_exc", []):
        op = path.join(YAMHL[f'{s}_op'], *ip.parts[1:-1], f"{ddir(YAMHL, f'files_conv/{_op}/{s}_op', _op)}.{s}")
    return op

def repl(s: str, repl_dict: Dict[str, List[str]]) -> str:
    op = s
    for k, v in repl_dict.items():
        for i in v:
            op = op.replace(i, k)
    return op

for i in ["md", "html"]:
    setattr(Constants, f"{i}_rules", rules_fn(RULES, i))

def main(rmv: Dict[Any, Any]={}):
    if ddir(PDOC, "enabled", False):
        pn = PDOC["project"]
        docs_pdir = PDOC["op"]
        docs_dir = path.join(docs_pdir, "docs")
        rmtree(docs_dir)
        run(PDOC["command"].format(**{i: PDOC[i] for i in ["project", "templates", "op"]}))
        move(path.join(docs_pdir, pn), docs_dir)

    rmv_r = ddir(rmv, "rules")
    rmv_mv = ddir(rmv, "md_vars")
    for i in ["md", "html"]:
        setattr(Constants, f"{i}_repl", dd(rules_fn(RULES, i), rules_fn(rmv_r, i)))
    MVC = dict(RMVC, **ddir(rmv_mv, "commons"))
    for rip in list(Path(f'./{YAMHL["input"]}').rglob("*.md")):
        md_out, html_out = [op_fn(rip, i) for i in ["md", "html"]]

        with open(rip, "r") as ip:
            md = repl(ip.read(), Constants.md_repl)
            for k, v in dict(MVC, **ddir(MD_VARS_YML, f"files/{rip.stem}"), **ddir(rmv_mv, f"files/{rip.stem}")).items():
                md = md.replace(f"${{{k}}}", v)

            if md_out:
                with open(md_out, "w") as md_out:
                    md_out.write(md)

            if html_out:
                with open(html_out, "w") as html_out:
                    headers = {"accept": "application/vnd.github.v3+json"}
                    data = {"text": md}
                    md = str(
                        httpx.post("https://api.github.com/markdown", headers=headers, json=data).content,
                        encoding="utf-8"
                    )

                    html_out.write(srv_tpl("yamhl_html.mako", content=repl(md, Constants.html_repl)))

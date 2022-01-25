from genomoncology.parse.doctypes import DocType
from genomoncology.pipeline.converters import cint
from genomoncology.pipeline.transformers.registry import register


def wgl_transform(x):
    def tr(v, f=None):
        f = f or int
        v = v.replace("NA", "")

        if v:
            return [f(s.strip()) for s in v.split(",")]
        else:
            return []

    return dict(
        hgvs_c=x.get("hgvs_c"),
        dna_number__mint=tr(x.get("dna_number")),
        parents__mint=tr(x.get("parents")),
        category__mstring=tr(x.get("category"), f=str),
        proband__int=cint(x.get("proband")),
    )


register(output_type=DocType.BAYLOR_WGL, transformer=wgl_transform)

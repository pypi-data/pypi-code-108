from genomoncology.parse.doctypes import DocType, __TYPE__, __CHILD__
from .registry import register, get_transformer


class VariantMapper(object):
    """
    Variant is a Call with additional meta information such as file_path,
    build, pipeline, run_id.

    Also, all of the 'info' fields are inserted to to the top-level of the
    document with wild-card typing format (e.g. DP__mint, etc.)
    """

    def __init__(self, **meta):
        self.meta = {k: v for (k, v) in meta.items() if v is not None}
        self.types = {}

    def resolve_info_key(self, k):
        return f"{k}__{self.types.get(k, 'string')}"

    def __call__(self, doc):
        if DocType.HEADER.is_a(doc):
            self.types = doc.get("types", {})
            self.meta["file_path"] = doc.get("file_path", None)

            # todo: replace copy with cytoolz
            header = doc.copy()
            header[__CHILD__] = doc.get(__CHILD__, "").replace(
                "CALL", "VARIANT"
            )
            return header

        elif DocType.VARIANT.is_a(doc):
            return doc

        elif DocType.TSV.is_a(doc) or DocType.ANNOTATED_TSV.is_a(doc):
            variant = doc.copy()
            variant.pop("annotations", None)
            variant[__TYPE__] = "VARIANT"
            variant.update(self.meta)
            return variant

        elif DocType.CALL.is_a(doc) or DocType.ANNOTATED_CALL.is_a(doc):
            # todo: replace copy with cytoolz
            # todo: replace with registered function, remove this elif
            variant = doc.copy()
            variant.pop("annotations", None)
            variant[__TYPE__] = doc.get(__TYPE__).replace("CALL", "VARIANT")
            variant.update(self.meta)
            info = variant.pop("info", {})
            info = {self.resolve_info_key(k): v for (k, v) in info.items()}
            variant.update(info)
            return variant

        else:
            tx = get_transformer(DocType.VARIANT, doc.get(__TYPE__))
            return tx(doc)


register(transformer=VariantMapper, output_type=DocType.VARIANT)


class FeatureMapper(object):
    r"""
    Feature Fields:
        * chr
        * start
        * end

    File Fields:
        * build
        * run_id
        * file_path
        * pipeline

    Info Fields:
        * \d+           => __int
        * \d+\.\d+      => __float
        * anything else => __string
        * w/ comma      => __m(int,float,string)
    """

    CORE = {"chr", "start", "end", "build", "run_id", "file_path", "pipeline"}

    def __init__(self, **meta):
        self.meta = {k: v for (k, v) in meta.items() if v is not None}
        self.meta[__TYPE__] = "FEATURE"
        self.types = {}
        self.is_multi = set()

    @staticmethod
    def get_val_type(value):
        is_multi = False
        if "," in value and len(value) > 1:
            is_multi = True
            value = value.split(",")[0]

        try:
            int(value)
            val_type = "int"
        except ValueError:
            try:
                float(value)
                val_type = "float"
            except ValueError:
                val_type = "string"

        val_type = "m" + val_type if is_multi else val_type
        return is_multi, val_type

    def transform_key_value(self, key, value):
        if key not in self.types:
            is_multi, val_type = self.get_val_type(value)
            if is_multi:
                self.is_multi.add(key)
            self.types[key] = val_type

        if value and (key in self.is_multi):
            value = value.split(",")

        return f"{key}__{self.types[key]}", value

    def __call__(self, doc: dict):  # pragma: no mccabe
        if DocType.HEADER.is_a(doc):
            self.meta["file_path"] = doc.get("file_path", None)
            header = doc.copy()
            header[__CHILD__] = "FEATURE"
            return header

        elif DocType.FEATURE.is_a(doc):
            return doc

        elif DocType.TSV.is_a(doc):
            feature = self.meta.copy()
            for (key, value) in doc.items():
                if key in self.CORE:
                    feature[key] = value
                elif key == "stop":
                    feature["end"] = value
                elif key != "__type__":
                    new_key, new_value = self.transform_key_value(key, value)
                    feature[new_key] = new_value

            return feature

        else:
            tx = get_transformer(DocType.VARIANT, doc.get(__TYPE__))
            return tx(doc)


register(transformer=FeatureMapper, output_type=DocType.FEATURE)

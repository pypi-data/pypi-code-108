# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import tablib
from babel.messages.pofile import read_po
from modeltranslation.translator import translator
from modeltranslation.utils import build_localized_fieldname

from .settings import DEFAULT_TO_LANG, DEFAULT_FROM_LANG
from .utils.xml.parse import XMLParser


def normalize_text(text):
    text = text or ""
    return text.strip()


def build_model_map():
    models_map = {}
    models = translator.get_registered_models(abstract=False)
    for model in models:
        model_name = "%s.%s" % (model._meta.app_label, model._meta.model_name)

        models_map[model_name] = model
    return models_map


def group_dataset(dataset):
    group = {}
    key = None
    for row in sorted(dataset, key=lambda r: (r["model_key"], r["object_id"])):
        row = dict(row)
        cur_key = (row["model_key"], row["object_id"])
        if key != cur_key:
            if group:
                #
                yield group
            key = cur_key
            group = row
            group["fields"] = []

        field = {}
        for k in ["field", "from_lang", "to_lang", row["from_lang"], row["to_lang"]]:
            field[k] = row.pop(k)
        group["fields"].append(field)
    # return last group
    yield group


def catalog_to_dataset(catalog, from_lang=DEFAULT_FROM_LANG, to_lang=DEFAULT_TO_LANG):
    model_map = build_model_map()
    for m in catalog:
        if not m.id:
            pass
        text_row = {
            "from_lang": from_lang,
            "to_lang": to_lang,  # may be set
            from_lang: m.id,
            to_lang: normalize_text(m.string),
        }
        for path, _ in m.locations:
            app_name, model_name, field, object_id = path.split(".")
            model_key = ".".join([app_name, model_name])
            row = dict(
                zip(
                    ["model_key", "field", "object_id", "app_name", "model_name"],
                    [model_key, field, object_id, app_name, model_name],
                )
            )
            row["model"] = model_map[model_key]
            row.update(text_row)
            yield row


def xlsx_to_dataset(td_set):
    model_map = build_model_map()
    comment_name, locations_name, from_lang_name, to_lang_name = td_set.headers[:4]
    for d in td_set.dict:
        locations = d[locations_name].splitlines()
        text_row = {
            "from_lang": from_lang_name,
            "to_lang": to_lang_name,  # may be set
            from_lang_name: d[from_lang_name],
            to_lang_name: d[to_lang_name],
        }
        for path in locations:
            app_name, model_name, field, object_id = path.split(".")
            model_key = ".".join([app_name, model_name])
            row = dict(
                zip(
                    ["model_key", "field", "object_id", "app_name", "model_name"],
                    [model_key, field, object_id, app_name, model_name],
                )
            )
            row["model"] = model_map[model_key]
            row.update(text_row)
            yield row


def load_translation(grouped_dataset, to_lang=DEFAULT_TO_LANG):
    stat = dict.fromkeys(["update", "skip", "fail", "total"], 0)
    fail_rows = []
    for row in grouped_dataset:
        stat["total"] += 1
        try:
            if import_row(row, to_lang):
                stat["update"] += 1
            else:
                stat["skip"] += 1
        except Exception as e:
            print(e)
            fail_rows.append(row)
            stat["fail"] += 1
    return {"stat": stat, "fail_rows": fail_rows}


def load_same_rows(rows, to_lang=DEFAULT_TO_LANG, from_lang=DEFAULT_FROM_LANG):
    """

    :param rows:
    :param to_lang:
    :param from_lang:
    :return:
    """
    stat = dict.fromkeys(["update", "skip", "fail", "total"], 0)
    for r in rows:
        from_name = build_localized_fieldname(r["field"], from_lang)
        to_name = build_localized_fieldname(r["field"], to_lang)

        model = r["model"]
        msg_id = r[from_lang].strip()
        msg_str = normalize_text(r[to_lang]).strip()

        objects = model.objects.filter(**{from_name: msg_id})

        for obj in objects:
            stat["total"] += 1
            update_fields = []
            if (
                msg_str
                and normalize_text(getattr(obj, from_name)) == msg_id
                and normalize_text(getattr(obj, to_name)) != msg_str
            ):
                update_fields.append(to_name)
                setattr(obj, to_name, msg_str)
            if not update_fields:
                stat["skip"] += 1
                continue
            print("SAVE", obj, from_name, msg_id, msg_str)
            stat["update"] += 1
            try:
                obj.save(update_fields=update_fields)
            except Exception as e:
                print(r["Model"], r["object_id"])
                print(e)
                stat["fail"] += 1
    return stat


def import_row(row, to_lang, check_msg_id=False):
    model = row["model"]
    obj = model.objects.get(id=row["object_id"])

    update_fields = []
    for field in row["fields"]:
        to_field_name = build_localized_fieldname(field["field"], to_lang)
        msg_id = normalize_text(field[field["from_lang"]])
        if check_msg_id:
            from_field_name = build_localized_fieldname(
                field["field"], field["from_lang"]
            )
            obj_msg_id = normalize_text(getattr(obj, from_field_name))
            if obj_msg_id != msg_id:
                raise ValueError("msg_id changed!")
        if not msg_id:
            raise ValueError("msg_id is empty!")

        msg_str = normalize_text(field[to_lang]).strip()
        if msg_str and normalize_text(getattr(obj, to_field_name)) != msg_str:
            update_fields.append(to_field_name)
            setattr(obj, to_field_name, msg_str)

    if update_fields:
        obj.save(update_fields=update_fields)
        return True
    return False


def parse_po(stream, from_lang=DEFAULT_FROM_LANG, to_lang=DEFAULT_TO_LANG):
    catalog = read_po(stream)
    return catalog_to_dataset(catalog, from_lang=from_lang, to_lang=to_lang)


def parse_xlsx(stream, from_lang=DEFAULT_FROM_LANG, to_lang=DEFAULT_TO_LANG):
    td = tablib.import_set(stream.read(), format="xlsx")
    return xlsx_to_dataset(td)


def parse_xml(stream, from_lang=DEFAULT_FROM_LANG, to_lang=DEFAULT_TO_LANG):
    model_map = build_model_map()

    x = XMLParser()
    parsed_iter = x.parse(stream, tags=["Object"])

    for d in parsed_iter:
        d = d["Object"]
        locations = d["@id"].split(";")
        text_row = {"from_lang": from_lang, "to_lang": to_lang}
        is_merged = "Lang" in d

        for path in locations:
            fields = []
            if is_merged:
                app_name, model_name, field, object_id = path.split(".")
                lang_map = {i["@code"]: i for i in d["Lang"]}
                fields.append(
                    {
                        "field": field,
                        from_lang: lang_map[from_lang]["#text"],
                        to_lang: lang_map[to_lang].get("#text"),
                    }
                )

            else:
                app_name, model_name, object_id = path.split(".")
                for k, v in d.items():
                    if not k.startswith("@") and "@field" in v:
                        lang_map = {i["@code"]: i for i in v["Lang"]}
                        fields.append(
                            {
                                "field": v["@field"],
                                from_lang: lang_map[from_lang]["#text"],
                                to_lang: lang_map[to_lang].get("#text"),
                            }
                        )

            model_key = ".".join([app_name, model_name])
            for f in fields:
                row = dict(
                    zip(
                        ["model_key", "object_id", "app_name", "model_name"],
                        [model_key, object_id, app_name, model_name],
                    )
                )
                row["model"] = model_map[model_key]
                row.update(f)
                row.update(text_row)
                yield row

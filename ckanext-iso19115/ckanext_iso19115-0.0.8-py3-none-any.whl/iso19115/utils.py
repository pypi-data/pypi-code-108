from __future__ import annotations

import functools
import pickle
from io import BytesIO
from pathlib import Path
from typing import Any, Container, Iterable, Optional, cast
from xml.etree import ElementTree as xtree

import ckan.plugins.toolkit as tk
import xmlschema
from lxml import etree as ltree
from lxml import isoschematron

from . import builder
from .types.base import CodeListValue

DEFAULT_XSD = "mdb2"
_root = Path(__file__).parent

_codelists = _root / "namespaces/19115/resources/Codelists/cat/codelists.xml"

ns = {
    "srv": "http://standards.iso.org/iso/19115/-3/srv/2.0",
    "cat": "http://standards.iso.org/iso/19115/-3/cat/1.0",
    "cit": "http://standards.iso.org/iso/19115/-3/cit/2.0",
    "gco": "http://standards.iso.org/iso/19115/-3/gco/1.0",
    "gcx": "http://standards.iso.org/iso/19115/-3/gcx/1.0",
    "gex": "http://standards.iso.org/iso/19115/-3/gex/1.0",
    "lan": "http://standards.iso.org/iso/19115/-3/lan/1.0",
    "mac": "http://standards.iso.org/iso/19115/-3/mac/2.0",
    "mas": "http://standards.iso.org/iso/19115/-3/mas/1.0",
    "mcc": "http://standards.iso.org/iso/19115/-3/mcc/1.0",
    "mco": "http://standards.iso.org/iso/19115/-3/mco/1.0",
    "mdb": "http://standards.iso.org/iso/19115/-3/mdb/2.0",
    "mdq": "http://standards.iso.org/iso/19157/-2/mdq/1.0",
    "mmi": "http://standards.iso.org/iso/19115/-3/mmi/1.0",
    "mpc": "http://standards.iso.org/iso/19115/-3/mpc/1.0",
    "mrc": "http://standards.iso.org/iso/19115/-3/mrc/2.0",
    "mrd": "http://standards.iso.org/iso/19115/-3/mrd/1.0",
    "mri": "http://standards.iso.org/iso/19115/-3/mri/1.0",
    "mrl": "http://standards.iso.org/iso/19115/-3/mrl/2.0",
    "mrs": "http://standards.iso.org/iso/19115/-3/mrs/1.0",
    "msr": "http://standards.iso.org/iso/19115/-3/msr/2.0",
    "gml": "http://www.opengis.net/gml/3.2",
    "xlink": "http://www.w3.org/1999/xlink",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}
_schema_mapping = {
    "mds2": _root / "namespaces/19115/-3/mds/2.0/mds.xsd",
    "mdb2": _root / "namespaces/19115/-3/mdb/2.0/mdb.xsd",
}

_schematron_mapping = {
    "metadata": _root / "schematron/mdb.xml",
    "identification": _root / "schematron/mri.xml",
    "constraints": _root / "schematron/mco.xml",
    "maintenance": _root / "schematron/mmi.xml",
    "extent": _root / "schematron/gex.xml",
    "medium": _root / "schematron/mrd.xml",
    "quality": _root / "schematron/dqm.xml",
    "service": _root / "schematron/srv.xml",
    "citation": _root / "schematron/cit.xml",
    "extended": _root / "schematron/mex.xml",
    "catalogue": _root / "schematron/mrc.xml",
    "measure": _root / "schematron/mdq.xml",
}

for f in _schema_mapping.values():
    assert (
        f.is_file()
    ), f"Schema {f} does not exists. Have you extracted namespaces.zip?"


for f in _schematron_mapping.values():
    assert (
        f.is_file()
    ), f"Schema {f} does not exists. Have you extracted namespaces.zip?"


def lookup(root: str, schema: xmlschema.XMLSchema):
    qualified_root = root

    try:
        _ns, tag = root.split(":")
        qualified_root = "{%s}%s" % (ns[_ns], tag)
    except (ValueError, KeyError):
        pass

    el = None

    if root in schema.maps.elements:
        el = schema.maps.elements[root]
    else:
        for component in schema.maps.iter_components():
            if not hasattr(component, "qualified_name"):
                continue
            if component.qualified_name == qualified_root:
                el = component
                break

    # el = schema.find(f".//{root}", namespaces=utils.ns)
    return el


def _get_schema(name: str, rebuild: bool = False) -> xmlschema.XMLSchema:
    cache = _root / f"{name}.pickle"
    if not cache.is_file() or rebuild:
        schema = xmlschema.XMLSchema(
            str(_schema_mapping[name]), validation="lax"
        )
        with cache.open("wb") as dest:
            pickle.dump(schema, dest)
    with cache.open("rb") as src:
        return pickle.load(src)


def get_builder(root, name: str = DEFAULT_XSD) -> builder.Builder:
    schema = _get_schema(name)
    return builder.Builder(schema, root)


def validate_schema(
    content: bytes, name: str = DEFAULT_XSD, validate_codelists: bool = False
):
    schema = _get_schema(name)
    try:
        # from icecream import ic

        # ic(
        #     schema.decode(
        #         BytesIO(content), converter=xmlschema.JsonMLConverter
        #     )
        # )

        schema.validate(
            BytesIO(content),
            extra_validator=get_extra_validator(validate_codelists),
        )
    except xmlschema.XMLSchemaValidationError as e:
        raise tk.ValidationError({"schema": [str(e)]})
    except (ValueError, xtree.ParseError) as e:
        raise tk.ValidationError({"content": [str(e)]})


def validate_schematron(content: bytes, schemas: Iterable[str] = frozenset()):
    errors = []
    if not schemas:
        schemas = _schematron_mapping.keys()
    for name in schemas:
        path = str(_schematron_mapping[name])
        with open(path, "rb") as src:
            sch = isoschematron.Schematron(
                ltree.XML(src.read()), store_report=True
            )
        if sch.validate(ltree.XML(content)):
            continue

        failed = sch.validation_report.xpath(
            "//*[local-name() = 'failed-assert']/*[text()]"
        )
        errors.extend(
            " ".join(l.strip() for l in f.itertext()) for f in failed
        )
    if errors:
        raise tk.ValidationError({"schematron": list(set(errors))})


def validate_codelist(el: xtree.Element, xsd: xmlschema.XMLSchemaBase):
    if xsd.type.local_name != "CodeListValue_Type":
        return
    if xsd.local_name not in codelist_names():
        return

    validOptions = {c.name for c in codelist_options(xsd.local_name)}
    value = el.attrib["codeListValue"]
    if value not in validOptions:
        reason = (
            f"{value} is not a valid code. Valid options are: {validOptions}"
        )
        raise xmlschema.XMLSchemaValidationError(xsd, el, reason)


def get_extra_validator(codelists: bool):
    def validator(el: xtree.Element, xsd: xmlschema.XMLSchemaBase):
        if codelists:
            validate_codelist(el, xsd)

    return validator


@functools.lru_cache(1)
def codelist_names() -> Container[str]:
    xml = ltree.XML(_codelists.open("rb").read())
    xpath = f"//cat:codelistItem/cat:CT_Codelist/@id"
    namespaces = {"cat": xml.nsmap["cat"]}
    return xml.xpath(xpath, namespaces=namespaces)


@functools.lru_cache()
def codelist_options(name: str) -> list[CodeListValue]:
    xml = ltree.XML(_codelists.open("rb").read())
    xpath = f"//cat:codelistItem/cat:CT_Codelist[@id='{name}']/cat:codeEntry/cat:CT_CodelistValue"
    namespaces = {"cat": xml.nsmap["cat"], "gco": xml.nsmap["gco"]}
    codes = xml.xpath(xpath, namespaces=namespaces)

    return [
        CodeListValue(
            code.find(
                "cat:identifier/gco:ScopedName", namespaces=namespaces
            ).text,
            code.find(
                "cat:definition/gco:CharacterString", namespaces=namespaces
            ).text,
        )
        for code in codes
    ]


@functools.lru_cache(1)
def enum_elements(name: str = DEFAULT_XSD) -> dict[str, xmlschema.XsdElement]:
    schema = _get_schema(name)
    return {
        e.local_name: e
        for e in schema.maps.elements.values()
        if isinstance(e, xmlschema.XsdElement)
        and e.type.is_simple()
        and getattr(e.type, "enumeration", None)
    }


@functools.lru_cache()
def enum_values(name: str, schema: str = DEFAULT_XSD) -> Optional[list[Any]]:
    el = enum_elements(schema)[name]
    if el.local_name == name:
        type_ = cast(
            xmlschema.validators.simple_types.XsdAtomicRestriction, el.type
        )
        return type_.enumeration

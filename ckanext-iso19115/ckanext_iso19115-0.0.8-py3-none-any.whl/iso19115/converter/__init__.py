from __future__ import annotations

import dataclasses
import contextlib
from typing import Any
from typing_extensions import TypeAlias
import ckan.plugins.toolkit as tk

from ..types.base import JmlRecord
from . import helpers as h

from ..types import *

DataClass: TypeAlias = Any


class Converter:
    data: mdb.MD_Metadata
    pkg: dict[str, Any]

    def __init__(self, data_dict: dict[str, Any]):
        pass

    def initialize(self, pkg_dict):
        self.data = mdb.MD_Metadata()
        self.pkg = pkg_dict

    def process(self):
        self._add_identifier()
        self._add_default_locale()
        self._add_parent()
        self._add_scope()

        self._add_contacts()
        self._add_dates()

        self._add_standard()
        self._add_profile()
        self._add_alternative_reference()
        self._add_other_locale()
        self._add_linkage()
        self._add_spatial_representation()
        self._add_reference_system()
        self._add_metadata_extension()

        self._add_identification()

        self._add_content()
        self._add_distribution()
        self._add_dq()
        self._add_lineage()
        self._add_catalogue()
        self._add_constraints()
        self._add_schema()
        self._add_maintenance()
        self._add_acquisition()

    def finalize(self):
        ...

    def build(self):
        result = jml(self.data)
        return result

    def _add_identifier(self):
        identifier: mcc.MD_Identifier = h.id(
            self.pkg["id"], codeSpace="urn:uuid"
        )
        self.data.metadataIdentifier = identifier

    def _add_default_locale(self):
        locale = h.locale(
            self.pkg.get("language") or tk.config.get("ckan.locale_default")
        )
        self.data.set_locale(locale)

    def _add_parent(self):
        parent: cit.CI_Citation
        pass

    def _add_scope(self):
        scope: mdb.MD_MetadataScope = mdb.MD_MetadataScope(
            mcc.MD_ScopeCode("dataset"), h.cs("Dataset")
        )

        self.data.metadataScope.append(scope)

    def _add_contacts(self):
        org = self.pkg["organization"]
        if org:
            contact = h.responsibility(
                "pointOfContact",
                h.org(
                    self.pkg["organization"]["title"],
                    logo=h.image(org["image_url"]),
                ),
            )
            self.data.add_contact(contact)

        author_contact = self._make_user_contact(
            "author", self.pkg["creator_user_id"]
        )
        if author_contact:
            self.data.add_contact(author_contact)

    def _add_dates(self):
        has_creation = True

        for date in self.pkg.get("date_info", []):
            self.data.add_dateInfo(
                cit.CI_Date(
                    h.date(date["date"]), cit.CI_DateTypeCode(date["type"])
                )
            )
            if date["type"] == "creation":
                has_creation = True
        if not has_creation:
            creation = self.pkg["metadata_created"]
            self.data.add_dateInfo(
                cit.CI_Date(h.date(creation), cit.CI_DateTypeCode(creation))
            )

    def _add_standard(self):
        standard: cit.CI_Citation = h.citation("ISO 19115", edition="2016")
        self.data.metadataStandard.append(standard)

    def _add_profile(self):
        profile: cit.CI_Citation
        pass

    def _add_alternative_reference(self):
        ref: cit.CI_Citation
        pass

    def _add_other_locale(self):
        locale: lan.PT_Locale
        pass

    def _add_linkage(self):
        link: cit.CI_OnlineResource
        pass

    def _add_spatial_representation(self):
        spatial: mcc.Abstract_SpatialRepresentation
        pass

    def _add_reference_system(self):
        ref: mrs.MD_ReferenceSystem
        pass

    def _add_metadata_extension(self):
        ext: mex.MD_MetadataExtensionInformation
        pass

    def _add_identification(self):
        cit: cit.CI_Citation = h.citation(
            self.pkg["title"], identifier=h.id(self.pkg["id"])
        )
        poc = self._make_user_contact("author", self.pkg["creator_user_id"])
        kw = [h.keyword(t) for t in self.pkg["tags"]]

        resources = []
        for res in self.pkg["resources"]:
            r_name = (
                h.citation(res["name"], presentationForm="documentDigital")
                if res["name"]
                else None
            )
            resources.append(
                mri.MD_AssociatedResource(
                    r_name,
                    mri.DS_AssociationTypeCode("isComposedOf"),
                )
            )

        ident: mri.MD_DataIdentification = mri.MD_DataIdentification(
            cit,
            self.pkg["notes"],
            pointOfContact=[poc] if poc else [],
            descriptiveKeywords=kw,
            associatedResource=resources,
        )

        self.data.add_identificationInfo(ident)

    def _add_content(self):
        content: mcc.Abstract_ContentInformation
        content: mrc.MD_FeatureCatalogueDescription
        content: mrc.MD_CoverageDescription
        content: mrc.MD_FeatureCatalogue

        pass

    def _add_distribution(self):
        dist: mrd.MD_Distribution
        pass

    def _add_dq(self):
        for dq in self.pkg.get("data_quality", []):
            result = mdq.DQ_DescriptiveResult(
                statement=h.cs(dq["details"] or "xx")
            )
            if "date" in dq:
                result.dateTime = h.date(dq["date"], True)

            report: mdq.AbstractDQ_Element = h.make(
                dq["type"], result=[result]
            )

            self.data.dataQualityInfo.append(
                mdq.DQ_DataQuality(
                    scope=mcc.MD_Scope(mcc.MD_ScopeCode("dataset")),
                    report=[report],
                )
            )

    def _add_lineage(self):
        ln: mrl.LI_Lineage
        pass

    def _add_catalogue(self):
        catalogue: mpc.MD_PortrayalCatalogueReference
        pass

    def _add_constraints(self):
        ctr: mco.MD_Constraints
        pass

    def _add_schema(self):
        schema: mas.MD_ApplicationSchemaInformation
        pass

    def _add_maintenance(self):
        maintenance: mmi.MD_MaintenanceInformation
        pass

    def _add_acquisition(self):
        acq: mac.MI_AcquisitionInformation
        pass

    def _make_user_contact(self, role: str, user_id: str):
        with contextlib.suppress(tk.NotAuthorized):
            author = tk.get_action("user_show")({}, {"id": user_id})
            return h.responsibility(
                role, h.individual(author["fullname"] or author["name"])
            )


def _default_as_jml(el: DataClass, ns: str):
    data = JmlRecord(f"{ns}:{el.__class__.__name__}")

    for field in dataclasses.fields(el):
        k = field.name
        v = getattr(el, k)

        optional = is_optional(field)
        # not sure if it's safe to simplify it ignoring any falsy value
        if optional and (v is None or v == []):
            continue

        if not isinstance(v, list) or v == []:
            v = [v]

        for element in v:
            child = JmlRecord(f"{ns}:{k}")
            data.append(child)

            if not dataclasses.is_dataclass(element):
                if is_cs(field):
                    element = h.cs(element)
                elif is_codelist(field):
                    element = h.codelist(field, element)

            content = (
                jml(element) if dataclasses.is_dataclass(element) else element
            )
            if content != []:
                child.append(content)
            child.refine_attributes()

    data.refine_attributes()
    return data


def jml(el: DataClass):
    ns = el.__module__.split(".")[-1]

    if hasattr(el, "as_jml"):
        data = el.as_jml()
    else:
        data = _default_as_jml(el, ns)
    data.refine_attributes

    return data


def is_codelist(field: dataclasses.Field) -> bool:
    return "Codelist[" in field.type


def is_cs(field: dataclasses.Field) -> bool:
    return "gco.CharacterString" in field.type


def is_optional(field: dataclasses.Field) -> bool:
    return "Optional[" in field.type

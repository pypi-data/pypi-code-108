from __future__ import annotations

import dataclasses
import contextlib
from typing import Any, Iterable
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
        mcc.MD_Identifier
        identifier: mcc.MD_Identifier = h.id(
            self.pkg["id"], codeSpace="urn:uuid"
        )
        self.data.metadataIdentifier = identifier

    def _add_default_locale(self):
        lan.PT_Locale
        locale = h.locale(
            self.pkg.get("language") or tk.config.get("ckan.locale_default")
        )
        self.data.defaultLocale = locale

    def _add_parent(self):
        cit.CI_Citation
        pass

    def _add_scope(self):
        mdb.MD_MetadataScope
        scope: mdb.MD_MetadataScope = mdb.MD_MetadataScope(
            mcc.MD_ScopeCode("dataset"), h.cs("Dataset")
        )

        self.data.metadataScope.append(scope)

    def _add_contacts(self):
        cit.CI_Responsibility
        for contact in self.pkg.get("contact", []):

            ind = cit.CI_Individual(
                name=h.cs(contact.get("inidvidual")),
                positionName=h.cs(contact.get("position")),
            )
            org = h.org(
                contact.get("name"),
                contactInfo=[
                    cit.CI_Contact(
                        phone=[h.phone(contact.get("phone"))],
                        address=[h.address(email=h.cs(contact.get("email")))],
                    )
                ],
                individual=[ind],
            )
            resp = cit.CI_Responsibility(contact["role"], [org])
            self.data.add_contact(resp)

        for contact in self._extra_contacts():
            self.data.add_contact(contact)

    def _extra_contacts(self) -> Iterable[cit.CI_Responsibility]:
        return []

    def _add_dates(self):
        cit.CI_Date
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
        cit.CI_Citation
        standard: cit.CI_Citation = h.citation("ISO 19115", edition="2016")
        self.data.metadataStandard.append(standard)

    def _add_profile(self):
        cit.CI_Citation
        pass

    def _add_alternative_reference(self):
        cit.CI_Citation
        pass

    def _add_other_locale(self):
        lan.PT_Locale
        pass

    def _add_linkage(self):
        cit.CI_OnlineResource
        pass

    def _add_spatial_representation(self):
        # mcc.Abstract_SpatialRepresentation
        msr.MD_GridSpatialRepresentation
        msr.MD_VectorSpatialRepresentation
        for rep in self.pkg.get("vector_spatial_representation", []):
            self.data.spatialRepresentationInfo.append(
                msr.MD_VectorSpatialRepresentation(
                    geometricObjects=msr.MD_GeometricObjects(
                        msr.MD_GeometricObjectTypeCode(rep["type"]),
                        gco.Integer(rep["count"] or 0),
                    )
                )
            )

    def _add_reference_system(self):
        mrs.MD_ReferenceSystem
        pass

    def _add_metadata_extension(self):
        mex.MD_MetadataExtensionInformation
        pass

    def _add_identification(self):
        mcc.Abstract_ResourceDescription
        mri.MD_DataIdentification
        srv.SV_ServiceIdentification

        citation: cit.CI_Citation = h.citation(
            self.pkg["title"], identifier=h.id(self.pkg["id"])
        )
        kw = [h.keyword(t) for t in self.pkg["tags"]]

        ident: mri.MD_DataIdentification = mri.MD_DataIdentification(
            citation,
            self.pkg["notes"],
            descriptiveKeywords=kw,
        )
        self.data.add_identificationInfo(ident)

        for res in self.pkg["resources"]:
            self.data.add_identificationInfo(
                mri.MD_DataIdentification(
                    h.citation(
                        res["name"], presentationForm="documentDigital"
                    ),
                    h.cs(res["description"]),
                    resourceFormat=[
                        mrd.MD_Format(
                            cit.CI_Citation(res["format"]),
                            res.get("version"),
                        )
                    ],
                )
            ),

    def _add_content(self):
        # mcc.Abstract_ContentInformation
        mrc.MD_FeatureCatalogueDescription
        mrc.MD_CoverageDescription
        mrc.MD_FeatureCatalogue
        pass

    def _add_distribution(self):
        mrd.MD_Distribution
        pass

    def _add_dq(self):
        mdq.DQ_DataQuality
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
        mrl.LI_Lineage
        pass

    def _add_catalogue(self):
        mpc.MD_PortrayalCatalogueReference
        pass

    def _add_constraints(self):
        mco.MD_Constraints
        pass

    def _add_schema(self):
        mas.MD_ApplicationSchemaInformation
        pass

    def _add_maintenance(self):
        mmi.MD_MaintenanceInformation
        pass

    def _add_acquisition(self):
        mac.MI_AcquisitionInformation
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

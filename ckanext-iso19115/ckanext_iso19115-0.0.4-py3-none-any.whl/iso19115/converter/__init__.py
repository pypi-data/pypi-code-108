from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

import ckan.plugins.toolkit as tk

from . import helpers as h

if TYPE_CHECKING:
    import ckanext.iso19115.types as t


class Converter:
    data: t.mdb.MD_Metadata
    pkg: dict[str, Any]

    def __init__(self, data_dict: dict[str, Any]):
        pass

    def initialize(self, pkg_dict):
        self.data = h.make("mdb:MD_Metadata")
        self.pkg = pkg_dict

    def process(self):
        self._add_default_locale()
        self._add_dates()
        self._add_contacts()
        self._add_identification()

    def finalize(self):
        ...

    def build(self):
        result = h.jml(self.data)
        return result

    def _add_default_locale(self):
        locale = h.locale(tk.config.get("ckan.locale_default"))
        self.data.set_locale(locale)

    def _add_dates(self):
        creation = self.pkg["metadata_created"]
        self.data.add_dateInfo(h.date(creation, "creation"))

        revision = self.pkg["metadata_modified"]
        if revision != creation:
            self.data.add_dateInfo(h.date(revision, "revision"))

    def _add_contacts(self):
        org = self.pkg["organization"]
        if org:
            contact = h.responsibility(
                "owner",
                self.pkg["organization"]["title"],
                logo=h.image(org["image_url"]),
            )
            self.data.add_contact(contact)

        author_contact = self._make_user_contact(
            "author", self.pkg["creator_user_id"]
        )
        if author_contact:
            self.data.add_contact(author_contact)

    def _add_identification(self):
        cit = h.citation(self.pkg["title"])
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
                h.make(
                    "mri:MD_AssociatedResource",
                    r_name,
                    "isComposedOf",
                )
            )

        ident: t.mri.MD_DataIdentification = h.make(
            "mri:MD_DataIdentification",
            cit,
            self.pkg["notes"],
            pointOfContact=poc,
            descriptiveKeywords=kw,
            associatedResource=resources,
        )

        self.data.add_identificationInfo(ident)

    def _make_user_contact(self, role: str, user_id: str):
        with contextlib.suppress(tk.NotAuthorized):
            author = tk.get_action("user_show")({}, {"id": user_id})
            return h.responsibility(role, author["fullname"] or author["name"])

from __future__ import annotations

from xmlschema import etree_tostring

import ckanext.iso19115.converter as c
import ckanext.iso19115.converter.helpers as h
import ckanext.iso19115.types as t
import ckanext.iso19115.utils as u


def print_xml(el):
    print(etree_tostring(el, namespaces=u.ns))


class TestConverter:
    def test_minimal_xml(self, faker):
        el: t.mdb.MD_Metadata = h.make("mdb:MD_Metadata")
        dt1 = faker.date_time()
        el.add_dateInfo(
            t.cit.CI_Date(h.date(dt1), t.cit.CI_DateTypeCode("creation"))
        )
        data = c.jml(el)
        builder = u.get_builder("mdb:MD_Metadata")
        assert builder.build(data)

    def test_with_party(self, faker):
        el: t.mdb.MD_Metadata = h.make("mdb:MD_Metadata")
        el.add_dateInfo(
            t.cit.CI_Date(
                h.date(faker.date_time().date()),
                t.cit.CI_DateTypeCode("creation"),
            )
        )
        el.add_contact(
            h.responsibility("author", t.cit.CI_Individual(h.cs("author")))
        )

        builder = u.get_builder("mdb:MD_Metadata")
        data = c.jml(el)
        builder.build(data)

    def test_with_identification(self, faker):
        el: t.mdb.MD_Metadata = h.make("mdb:MD_Metadata")
        el.add_dateInfo(
            t.cit.CI_Date(
                h.date(faker.date_time().date()),
                t.cit.CI_DateTypeCode("creation"),
            )
        )
        el.add_identificationInfo(
            h.make(
                "mri:MD_DataIdentification",
                h.citation(faker.sentence()),
                faker.sentence(),
            )
        )

        builder = u.get_builder("mdb:MD_Metadata")
        data = c.jml(el)
        builder.build(data)

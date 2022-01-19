""" Upgrade to version 4.0
"""
# pylint: disable=line-too-long
import logging
from Products.CMFCore.utils import getToolByName
from eea.dexterity.indicators.interfaces import IIndicator

logger = logging.getLogger("eea.dexterity.indicators")

DPSIR = {
    "Driving forces": "driving-forces",
    "Impact": "impact",
    "Pressure": "pressure",
    "Response": "response",
    "State": "state"
}

TYPOLOGY = {
    "Descriptive indicator (Type A - What is happening to the environment and to humans?)": "type-a",
    "Performance indicator (Type B - Does it matter?)": "type-b",
    "Efficiency indicator (Type C - Are we improving?)": "type-c",
    "Policy-effectiveness indicator (Type D)": "type-d",
    "Total welfare indicator (Type E - Are we on whole better off?)": "type-e"
}


def migrate_schema(context):
    """ Fix Indicator schema """
    ctool = getToolByName(context, "portal_catalog")
    portal_type = "ims_indicator"
    brains = ctool.unrestrictedSearchResults(portal_type=portal_type)

    logger.warn("Migrate IMS indicator schema...")
    for brain in brains:
        doc = brain.getObject()
        url = brain.getURL()

        # Fix DPSIR
        dpsir = getattr(doc, "DPSIR", None)
        if dpsir is not None:
            doc.taxonomy_dpsir = DPSIR.get(dpsir, dpsir)
            logger.warn("Fixed %s dpsir: %s -> %s", url, dpsir, doc.taxonomy_dpsir)
            delattr(doc, "DPSIR")

        # Fix Typology
        typology = getattr(doc, "Typology", None)
        if typology is not None:
            doc.taxonomy_typology = TYPOLOGY.get(typology, typology)
            logger.warn("Fixed %s typology: %s -> %s", url, typology, doc.taxonomy_typology)
            delattr(doc, "Typology")

        # Fix contact
        contact = getattr(doc, "contact", None)
        if contact is None:
            doc.contact = IIndicator["contact"].default
            logger.warn("Fixed %s contact: %s -> %s", url, contact, doc.contact)

        # Fix frequency_of_dissemination
        frequency_of_dissemination = getattr(doc, "frequency_of_dissemination", None)
        if frequency_of_dissemination is None:
            doc.frequency_of_dissemination = IIndicator[
                "frequency_of_dissemination"
            ].default
            logger.warn(
                "Fixed %s frequency_of_dissemination: %s -> %s",
                url,
                frequency_of_dissemination,
                doc.frequency_of_dissemination,
            )

        # Consultation_emails
        consultation_emails = getattr(doc, 'Consultation_emails', None)
        if consultation_emails is not None:
            doc.consultation_emails = consultation_emails
            delattr(doc, 'Consultation_emails')
            logger.warn("Fixed %s consultation_emails: %s -> %s", url, consultation_emails, doc.consultation_emails)

        # Consultation_members emails
        consultation_members_emails = getattr(doc, 'Consultation_members emails', None)
        if consultation_members_emails is not None:
            doc.consultation_members_emails = consultation_members_emails
            delattr(doc, 'Consultation_members emails')
            logger.warn("Fixed %s consultation_emails: %s -> %s", url, consultation_members_emails, doc.consultation_members_emails)

        # Head_of group email
        head_of_group_email = getattr(doc, 'Head_of group email', None)
        if head_of_group_email is not None:
            doc.head_of_group_email = head_of_group_email
            delattr(doc, 'Head_of group email')
            logger.warn("Fixed %s head_of_group_email: %s -> %s", url, head_of_group_email, doc.head_of_group_email)

    logger.warn("Migrate IMS indicator schema... done")

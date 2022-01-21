#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from re import A, search
from socket import create_connection
from fhirclient.models import extension
from fhirclient.models import reference
from fhirclient.models import resource
import requests
import json
import copy
from jinja2 import Template
from datetime import date, datetime
from distutils.util import strtobool
from fhirclient.models.patient import Patient, PatientContact
from fhirclient.models.humanname import HumanName
from fhirclient.models.identifier import Identifier
from fhirclient.models.extension import Extension
from fhirclient.models.codeableconcept import CodeableConcept
from fhirclient.models.coding import Coding
from fhirclient.models.fhirdate import FHIRDate
from fhirclient.models.address import Address
from fhirclient.models.contactpoint import ContactPoint
from fhirclient.models.condition import Condition
from fhirclient.models.reference import Reference
from fhirclient.models.operationoutcome import OperationOutcome, OperationOutcomeIssue
from fhirclient.models.parameters import Parameters, ParametersParameter
from fhirclient.models.bundle import Bundle, BundleEntry, BundleEntryRequest, BundleEntryResponse
from fhirclient.models.immunization import Immunization, ImmunizationExplanation
from fhirclient.models.resource import Resource
from fhirclient.models.meta import Meta
from fhirclient.models.organization import Organization
from fhirclient.models.location import Location
from fhirclient.models.fhirreference import FHIRReference
from fhirclient.models.practitioner import Practitioner
from fhirclient.models.quantity import Quantity

from requests.api import patch

class BaseFHIR():
    base_headers = {
        "Content-type": "application/json+fhir"
    }

    def __init__(self, base_url=None, base_uri=None, token_header=None) -> None:
        self.base_url = base_url if base_url is not None else "http://localhost:14001"
        self.base_uri = base_uri if base_uri is not None else ""
        self.set_headers(token_header=token_header)

    def set_headers(self, headers={}, token_header=None):
        new_headers = {**headers, **self.base_headers}
        if token_header is not None:
            if 'Content-Type' in token_header:
                del token_header['Content-Type']
            headers_with_auth = {**new_headers, **token_header}
            self.headers = headers_with_auth
        else:
            self.headers = new_headers
        return self.headers

    def get_fhir_url(self):
        return "{0}{1}".format(self.base_url, self.base_uri)

    def get_model_from_json(self, jsondict=None):
        if jsondict is None:
            return None
        if jsondict['resourceType'] == 'Patient':
            return Patient(jsondict=jsondict) 
        elif jsondict['resourceType'] == 'PatientContact':
            return PatientContact(jsondict=jsondict) 
        elif jsondict['resourceType'] == 'HumanName':
            return HumanName(jsondict=jsondict) 
        elif jsondict['resourceType'] == 'Identifier':
            return Identifier(jsondict=jsondict) 
        elif jsondict['resourceType'] == 'Extension':
            return Extension(jsondict=jsondict) 
        elif jsondict['resourceType'] == 'CodeableConcept':
            return CodeableConcept(jsondict=jsondict) 
        elif jsondict['resourceType'] == 'Coding':
            return Coding(jsondict=jsondict) 
        elif jsondict['resourceType'] == 'FHIRDate':
            return FHIRDate(jsondict=jsondict) 
        elif jsondict['resourceType'] == 'Address':
            return Address(jsondict=jsondict) 
        elif jsondict['resourceType'] == 'ContactPoint':
            return ContactPoint(jsondict=jsondict) 
        elif jsondict['resourceType'] == 'Condition':
            return Condition(jsondict=jsondict) 
        elif jsondict['resourceType'] == 'Reference':
            return Reference(jsondict=jsondict) 
        elif jsondict['resourceType'] == 'OperationOutcome':
            return OperationOutcome(jsondict=jsondict) 
        elif jsondict['resourceType'] == 'OperationOutcomeIssue':
            return OperationOutcomeIssue(jsondict=jsondict) 
        elif jsondict['resourceType'] == 'Parameters':
            return Parameters(jsondict=jsondict) 
        elif jsondict['resourceType'] == 'ParametersParameter':
            return ParametersParameter(jsondict=jsondict) 
        elif jsondict['resourceType'] == 'Bundle':
            return Bundle(jsondict=jsondict) 
        elif jsondict['resourceType'] == 'BundleEntry':
            return BundleEntry(jsondict=jsondict) 
        elif jsondict['resourceType'] == 'BundleEntryRequest':
            return BundleEntryRequest(jsondict=jsondict) 
        elif jsondict['resourceType'] == 'BundleEntryResponse':
            return BundleEntryResponse(jsondict=jsondict) 
        elif jsondict['resourceType'] == 'Immunization':
            return Immunization(jsondict=jsondict) 
        elif jsondict['resourceType'] == 'Organization':
            return Organization(jsondict=jsondict) 
        elif jsondict['resourceType'] == 'Location':
            return Location(jsondict=jsondict) 
        elif jsondict['resourceType'] == 'Practitioner':
            return Practitioner(jsondict=jsondict) 
        else:
            return Resource(jsondict=jsondict)

    def add_or_update_extension_to_extensions(self, extension, extensions):
        if extensions is None:
            extensions = [extension]
        else:
            ext_found = False
            for ext in extensions:
                if type(ext) is Extension:
                    if ext.url == extension.url:
                        ext = extension
                        ext_found = True
                        break
                elif type(ext) is list:
                    for sub_ext in ext:
                        ext = self.add_or_update_extension_to_extensions(extension=sub_ext, extensions=ext)
            if not ext_found:
                extensions.append(extension)
        return extensions



    def get_visitor_from_json(self, jsondict=None):
        if jsondict is None:
            return None
        if type(jsondict) is dict and jsondict['resourceType'] == 'Patient':
            return PatientFHIR(patient_resource_dict=jsondict)
        if type(jsondict) is dict and jsondict['resourceType'] == 'Parameter':
            return ParameterFHIR(resource=jsondict)
        elif type(jsondict) is dict and jsondict['resourceType'] == 'Bundle':
            return BundleFHIR(resource=jsondict)
        elif type(jsondict) is dict and jsondict['resourceType'] == 'Immunization':
            return ImmunizationFHIR(imm_dict=jsondict)
        elif type(jsondict) is dict and jsondict['resourceType'] == 'OperationOutcome':
            return OperationOutcomeFHIR(resource=jsondict)
        elif type(jsondict) is dict and jsondict['resourceType'] == 'Condition':
            return ConditionFHIR(resource=jsondict)
        elif type(jsondict) is dict and jsondict['resourceType'] == 'Organization':
            return OrganizationFHIR(resource=jsondict)
        elif type(jsondict) is dict and jsondict['resourceType'] == 'Location':
            return LocationFHIR(resource=jsondict)
        else:
            return self.get_model_from_json(jsondict=jsondict)
    
    def is_visitor(self, resource):
        if resource is None:
            return False
        
        if (type(resource) is ParameterFHIR or 
            type(resource) is PatientFHIR or 
            type(resource) is BundleFHIR or
            type(resource) is ImmunizationFHIR or
            type(resource) is OperationOutcomeFHIR or
            type(resource) is ConditionFHIR or
            type(resource) is OrganizationFHIR or
            type(resource) is LocationFHIR):
            return True
        return False

    def get_model_from_visitor(self, resource):
        if self.is_visitor(resource=resource):
            return resource.fhir_resource
        return None

class ConditionFHIR(BaseFHIR):
    resource_type = "Condition"
    default_coding_system = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary'
    default_coding_version = '1.0.0'
    agent_url = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#condition/agent"
    antigen_url = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#condition/antigen"
    fhir_resource = None

    def __init__(self, resource=None) -> None:
        self.patient = None
        self.code = None
        self.category = None
        self.extension = []
        self.fhir_resource = None
        if resource is not None:
            self.fhir_resource = Condition(jsondict=resource)
            self.from_dict()
        else:
            self.fhir_resource = Condition()

    
    def from_dict(self, condition=None):
        if condition is None:
            condition = self.fhir_resource
        
        if condition.extension is not None:
            for extension in condition.extension:
                self.extension.append(extension.as_json())
        if condition.patient is not None:
            self.patient = condition.patient.as_json()
        self.code = condition.code.as_json()
        self.category = condition.category.as_json()

    def to_fhir_condition(self, condition=None):
        if condition is None:
            condition = self.fhir_resource
        if self.patient is not None and type(self.patient) is PatientFHIR:
            condition.patient = self.patient.patient
        elif self.patient is not None and type(self.patient) is dict and 'reference' in self.patient:
            reference = Reference(jsondict=self.patient['reference'])
            condition.patient = reference
        condition.code = CodeableConcept(jsondict=self.code)
        condition.category = CodeableConcept(jsondict=self.category)
        if self.extension is not None:
            condition.extension = []
            for ext in self.extension:
                extension = Extension(jsondict=ext)
                condition.extension.append(extension)
        return condition

    def get_code(self, system=None, version=None, condition=None):
        if condition is None:
            condition = self.fhir_resource
        self.to_fhir_condition(condition=condition)

        if system is None:
            system = self.default_coding_system
        if version is None:
            version = self.default_coding_version
        for coding in self.fhir_resource.code.coding:
            if coding.system == system and coding.version == version:
                return coding.as_json()
        return self.fhir_resource.code.coding[0].as_json()

    def get_code_code(self, system=None, version=None, condition=None):
        code = Coding(jsondict=self.get_code(system=system, version=version, condition=condition))
        return code.code

    def get_category(self, system=None, version=None, condition=None):
        if condition is None:
            condition = self.fhir_resource
        self.to_fhir_condition(condition=condition)

        if system is None:
            system = self.default_coding_system
        if version is None:
            version = self.default_coding_version
        for coding in self.fhir_resource.category.coding:
            if coding.system == system and coding.version == version:
                return coding.as_json()
        return self.fhir_resource.category.coding[0].as_json()

    def get_category_code(self, system=None, version=None, condition=None):
        code = Coding(jsondict=self.get_category(system=system, version=version, condition=condition))
        return code.code

    def get_extension(self, url, system=None, version=None, condition=None):
        if condition is None:
            condition = self.fhir_resource
        self.to_fhir_condition(condition=condition)
        if system is None:
            system = self.default_coding_system
        if version is None:
            version = self.default_coding_version

        if self.fhir_resource.extension is not None:
            for extension in self.fhir_resource.extension:
                if extension.url == url and extension.valueCodeableConcept is not None:
                    for coding in extension.valueCodeableConcept.coding:
                        if coding.system == system and coding.version == version:
                            return coding
                    return extension.valueCodeableConcept.coding[0]
        return None

    def get_agent(self, system=None, version=None, condition=None):
        return self.get_extension(system=system, version=version, url=self.agent_url, condition=condition).as_json()

    def get_agent_display(self, system=None, version=None, condition=None):
        code = self.get_extension(system=system, version=version, url=self.agent_url, condition=condition)
        return code.display

    def get_antigen(self, system=None, version=None, condition=None):
        return self.get_extension(system=system, version=version, url=self.antigen_url, condition=condition).as_json()

    def get_antigen_display(self, system=None, version=None, condition=None):
        code = self.get_extension(system=system, version=version, url=self.antigen_url, condition=condition)
        return code.display

class OperationOutcomeFHIR(BaseFHIR):
    resource_type = "OperationOutcome"
    issues = []
    default_coding_system = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary'
    default_coding_version = '1.0.0'
    fhir_resource = None

    def __init__(self, resource=None) -> None:
        self.issues = []
        if resource is not None:
            self.fhir_resource = OperationOutcome(jsondict=resource)
            self.from_dict()
        else:
            self.fhir_resource = OperationOutcome()


    def from_dict(self, operation_outcome=None):
        if operation_outcome is None:
            operation_outcome = self.fhir_resource

        if operation_outcome.issue is not None:
            self.issues = []
            for issue in operation_outcome.issue:
                self.issues.append(issue.as_json())

    def to_fhir_operation_outcome(self, operation_outcome=None):
        if operation_outcome is None:
            operation_outcome = self.fhir_resource

        operation_outcome.issue = []
        for issue in self.issues:
            oper_outcome = OperationOutcomeIssue(jsondict=issue)
            operation_outcome.issue.append(oper_outcome)

    def getFhirResource(self):
        self.to_fhir_operation_outcome()
        return self.fhir_resource.as_json()

    def get_issue_count(self):
        return len(self.issues)

    def get_issue_code(self, index=0):
        self.to_fhir_operation_outcome()
        return self.fhir_resource.issue[index].code

    def get_issue_severity(self, index=0):
        self.to_fhir_operation_outcome()
        return self.fhir_resource.issue[index].code

    def get_issue_details(self, index=0, system=None, version=None):
        if system is None:
            system = self.default_coding_system
        if version is None:
            version = self.default_coding_version
        self.to_fhir_operation_outcome()

        for coding in self.fhir_resource.issue[index].details.coding:
            if coding.system == system and coding.version == version:
                return coding
        return self.fhir_resource.issue[index].details.coding[0]

    def get_issue_details_code(self, index=0, system=None, version=None):
        return self.get_issue_details(index=index, system=system, version=version).code
        
class ParameterFHIR(BaseFHIR):
    resource_type = "Parameters"
    fhir_resource = None
    def __init__(self, resource=None):
        self.fhir_resource = Parameters(jsondict=resource) if resource is not None else Parameters()

    def add_parameter(self, resource, name='resource'):
        parameter = ParametersParameter()
        parameter.name=name
        if type(resource) is dict:
            parameter.resrouce = self.get_model_from_json(jsondict=resource)
        elif self.is_visitor(resource=resource):
            parameter.resource = self.get_model_from_visitor(resource=resource)
        else:
            parameter.resource = resource
        if self.fhir_resource.parameter is None:
            self.fhir_resource.parameter = []
        self.fhir_resource.parameter.append(parameter)

    def getFhirResource(self):
        return self.fhir_resource.as_json()

    def fromFhirResource(self, resource):
        self.fhir_resource = Parameters(jsondict=resource)

class BundleFHIR(BaseFHIR):
    resource_type = "Bundle"
    type = None
    entries = []
    fhir_resource = None
    def __init__(self, resource=None):
        self.entries = []
        self.fhir_resource = Bundle(jsondict=resource) if resource is not None else Bundle()

        if self.fhir_resource.entry is not None:
            for entry in self.fhir_resource.entry:
                new_entry = {}
                new_entry['resource'] = super().get_visitor_from_json(jsondict=entry.resource.as_json()) if entry.resource is not None else None
                new_entry['response'] = entry.response.as_json() if entry.response is not None else None
                self.entries.append(new_entry)
        self.type = self.fhir_resource.type

    def add_entry(self, resource, response=None):
        bundle_entry = BundleEntry()
        bundle_entry.resource = super().get_visitor_from_json(jsondict=resource).fhir_resource if type(resource) is dict else resource.fhir_resource
        bundle_entry.response = BundleEntryResponse(jsondict=response) if response is not None else None
        if self.fhir_resource.entry is None:
            self.fhir_resource.entry = []
        self.fhir_resource.entry.append(bundle_entry)
        self.fhir_resource.type = self.type

    def getFhirResource(self):
        self.fhir_resource.type = self.type
        return self.fhir_resource.as_json()

    def fromFhirResource(self, resource):
        resource = json.loads(resource) if type(resource) is str else resource
        self.fhir_resource = Bundle(jsondict=resource)
        self.type = self.fhir_resource.type
        
    def count_entries(self, recurse=False, resource_type=None):
        if self.fhir_resource.entry is None:
            return 0
        if recurse:
            total = 0
            for entry in self.fhir_resource.entry:
                if type(entry.resource) is Bundle:
                    bundle_fhir = BundleFHIR(resource=entry.resource.as_json())
                    nb_entries = bundle_fhir.count_entries(recurse=True, resource_type=resource_type)
                    total += nb_entries
                
                if resource_type is None or entry.resource.resource_name == resource_type:
                    total += 1
            return total
        else:
            return len(self.fhir_resource.entry)

    def get_fhir_entries(self, recurse=False, resource_type=None):
        if self.fhir_resource.entry is None:
            return []
        entries = []
        if recurse:
            for entry in self.fhir_resource.entry:
                if resource_type is None or entry.resource.resource_name == resource_type:
                    entries.append(super().get_visitor_from_json(jsondict=entry.resource.as_json()))
                if type(entry.resource) is Bundle:
                    bundle_fhir = BundleFHIR(resource=entry.resource.as_json())
                    sub_entries = bundle_fhir.get_fhir_entries(recurse=recurse, resource_type=resource_type)
                    for e in sub_entries:
                        entries.append(e)
        else:
            for e in self.fhir_resource.entry:
                entries.append(super().get_visitor_from_json(jsondict=e.as_json()))

        return entries

    def get_entries(self, recurse=False, resource_type=None):
        entries = []
        for e in self.get_fhir_entries(recurse=recurse, resource_type=resource_type):
            entries.append(e)
        return entries

class ImmunizationFHIR(BaseFHIR):
    resource_type = 'Immunization'
    id = None
    updated_by = None
    creation_date = None
    created_by = None
    version_id = 1
    last_updated = None
    profile = ['http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/profiles/InspqImmunization.structuredefinition.xml']
    organization = None
    override_status_id = None
    override_status_code = None
    override_status_display = None
    lot_id = None
    lot_number = None
    expiration_date = None
    antigen_status = {
        'url': 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#immunization/antigenstatus',
        'extension': []
    }
    antigen_extension_dose_number = {
        'url': 'doseNumber'
    }
    antigen_id = None
    antigen_code = None
    antigen_display = None
    antigen_dose_number = 0
    antigen_status_id = None
    antigen_status_code = None
    antigen_status_display = None
    trade_name = None
    status = None
    date = None
    vaccine_code_id = None
    vaccine_code_code = None
    vaccine_code_display = None
    patient = None
    patient_reference = None
    reported = False
    performer = None
    performer_reference = None
    performer_display = None
    location = None
    location_reference = None
    location_display = None
    
    site_id = None
    site_code = None
    site_display = None
    route_id = None
    route_code = None
    route_display = None
    coding_system = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary'
    coding_version = '1.0.0'

    dose_quantity_value = 0.0
    dose_quantity_unit = None
    dose_quantity_code = None
    reason = None
    response_status = None
    response_etag = None
    response_last_modified = None
    override_status_url = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#immunization/overridestatus"
    lot_id_url = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#immunization/lotid"
    trade_name_url = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#immunization/tradename'
    antigen_status_url = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#immunization/antigenstatus"
    profile_url = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/profiles/InspqImmunization.structuredefinition.xml'
    updated_by_url = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#common/updatedby"
    created_by_url = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#common/createdby'
    creation_date_url = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#common/creationdate'

    fhir_resource = None

    def __init__(self, imm_dict=None, base_url=None, base_uri=None) -> None:
        super().__init__(base_url=base_url, base_uri=base_uri)

        if imm_dict is None:
            self.creation_date = date.today()
            self.last_updated = datetime.now()
            self.date = datetime.now()
            self.fhir_resource = self.to_fhir_resource()
        else: 
            self.from_dict(imm_dict=imm_dict)


    def set_id(self, immunization=None, id=None):
        if immunization is None:
            immunization = self.fhir_resource
        if id is not None:
            self.id = id
        immunization.id = self.id

    def get_id(self, immunization=None):
        if immunization is None:
            immunization = self.fhir_resource

        return immunization.id
        
    def get_meta_updated_by(self, immunization=None):
        if immunization is None:
            immunization = self.fhir_resource
        if immunization is None or immunization.meta is None or immunization.meta.extension is None:
            return None
        for extension in immunization.meta.extension:
            if extension.url == self.updated_by_url:
                return extension.valueString
        return None

    def get_meta_created_by(self, immunization=None):
        if immunization is None:
            immunization = self.fhir_resource
        if immunization is None or immunization.meta is None or immunization.meta.extension is None:
            return None
        for extension in immunization.meta.extension:
            if extension.url == self.created_by_url:
                return extension.valueString
        return None

    def get_meta_creation_date(self, immunization=None):
        if immunization is None:
            immunization = self.fhir_resource
        if immunization is None or immunization.meta is None or immunization.meta.extension is None:
            return None
        for extension in immunization.meta.extension:
            if extension.url == self.creation_date_url:
                return extension.valueDate
        return None

    def get_meta_version_id(self, immunization=None):
        if immunization is None:
            immunization = self.fhir_resource
        if immunization is None or immunization.meta is None:
            return None
        return immunization.meta.versionId

    def get_meta_last_updated(self, immunization=None):
        if immunization is None:
            immunization = self.fhir_resource
        if immunization is None or immunization.meta is None:
            return None
        return immunization.meta.lastUpdated.isostring

    def get_meta_profile(self, immunization=None):
        if immunization is None:
            immunization = self.fhir_resource
        if immunization is None or immunization.meta is None:
            return None
        return immunization.meta.profile

    def set_meta(self, immunization=None, version_id=None, last_updated=None, profile=None, updated_by=None, creation_date=None, created_by=None):
        if immunization is None:
            immunization = self.fhir_resource
        if version_id is not None:
            self.version_id = version_id
        if last_updated is not None:
            self.last_updated = last_updated
        if profile is not None:
            self.profile = profile
        if updated_by is not None:
            self.updated_by = updated_by
        if creation_date is not None:
            self.creation_date = creation_date
        if created_by is not None:
            self.created_by = created_by
        if immunization.meta is None:
            immunization.meta = Meta()
        immunization.meta.versionId = self.version_id
        immunization.meta.lastUpdated = self.last_updated
        immunization.meta.profile = self.profile
        if self.updated_by is not None:
            updated_by_ext = Extension()
            updated_by_ext.url = self.updated_by_url
            updated_by_ext.valueString = self.updated_by
            immunization.meta.extension = super().add_or_update_extension_to_extensions(extension=updated_by_ext, extensions=immunization.meta.extension)
        if self.creation_date is not None and (
            type(self.creation_date) is date or
            type(self.creation_date) is FHIRDate or 
            type(self.creation_date) is str):

            creation_date_ext = Extension()
            creation_date_ext.url = self.creation_date_url
            if type(self.creation_date) is str:
                creation_date_ext.valueDate = datetime.strftime(self.creation_date, "%Y-%m-%dT%H:%M:%S%z")
            else:
                creation_date_ext.valueDate = self.creation_date
            immunization.meta.extension = super().add_or_update_extension_to_extensions(extension=creation_date_ext, extensions=immunization.meta.extension)
        if self.created_by is not None:
            created_by_ext = Extension()
            created_by_ext.url = self.created_by_url
            created_by_ext.valueString = self.created_by
            immunization.meta.extension = super().add_or_update_extension_to_extensions(extension=created_by_ext, extensions=immunization.meta.extension)

    def get_override_status(self, immunization=None):
        if immunization is None:
            immunization = self.fhir_resource
        override_status_extension = None
        if immunization.extension is not None:
            for ext in immunization.extension:
                if ext.url == self.override_status_url:
                    override_status_extension = ext
        return override_status_extension

    def set_override_status(self, immunization=None, status_code=None, status_display=None, status_id=None, coding_system=None, coding_version=None):
        if immunization is None:
            immunization = self.fhir_resource
        if status_code is not None and status_display is not None and status_id is not None:
            self.override_status_code = status_code
            self.override_status_display = status_display
            self.override_status_id = status_id
        status_codeable_concept = self.to_codeable_concept(
            code=self.override_status_code,
            display=self.override_status_display,
            id=self.override_status_id,
            coding_system=coding_system,
            coding_version=coding_version)
        new_ext = Extension()
        new_ext.url = self.override_status_url
        new_ext.valueCodeableConcept = status_codeable_concept
        immunization.extension = super().add_or_update_extension_to_extensions(extension=new_ext, extensions=immunization.extension)

    def set_antigen_status(
        self,
        immunization=None,
        antigen_code=None,
        antigen_id=None,
        antigen_display=None,
        dose_number=None,
        status_code=None,
        status_id=None,
        status_display=None,
        coding_system=None,
        coding_version=None):
        if immunization is None:
            immunization = self.fhir_resource

        antigen_status_ext = Extension()
        antigen_status_ext.url = self.antigen_status_url

        if antigen_code is not None and antigen_id is not None and antigen_display is not None:
            self.antigen_display = antigen_display
            self.antigen_code = antigen_code
            self.antigen_id = antigen_id
        antigen_codeable_concept = self.to_codeable_concept(
            code=self.antigen_code,
            display=self.antigen_display,
            id=self.antigen_id,
            coding_system=coding_system,
            coding_version=coding_version)
        antigen_ext = Extension()
        antigen_ext.url = 'antigen'
        antigen_ext.valueCodeableConcept = antigen_codeable_concept
        antigen_status_ext.extension = super().add_or_update_extension_to_extensions(extension=antigen_ext, extensions=antigen_status_ext.extension)

        if dose_number is not None:
            self.antigen_dose_number = dose_number
        dose_number_ext = Extension()
        dose_number_ext.url = 'doseNumber'
        dose_number_ext.valueInteger = self.antigen_dose_number
        antigen_status_ext.extension = super().add_or_update_extension_to_extensions(extension=dose_number_ext, extensions=antigen_status_ext.extension)

        if status_code is not None and status_id is not None and status_display is not None:
            self.antigen_status_code = status_code
            self.antigen_status_display = status_display
            self.antigen_status_id = status_id
        status_codeable_concept = self.to_codeable_concept(
            code = self.antigen_status_code,
            id = self.antigen_status_id,
            display=self.antigen_status_display,
            coding_system=coding_system,
            coding_version=coding_version
        )
        status_ext = Extension()
        status_ext.url = 'status'
        status_ext.valueCodeableConcept = status_codeable_concept
        antigen_status_ext.extension = super().add_or_update_extension_to_extensions(extension=status_ext, extensions=antigen_status_ext.extension)

        immunization.extension = super().add_or_update_extension_to_extensions(extension=antigen_status_ext, extensions=immunization.extension)

    def get_antigen_status(self, immunization=None):
        if immunization is None:
            immunization = self.fhir_resource
        antigen_status_extension = None
        if immunization.extension is not None:
            for ext in immunization.extension:
                if ext.url == self.antigen_status_url:
                    antigen_status_extension = ext
        return antigen_status_extension

    def get_antigen_status_antigen(self, immunization=None):
        antigen_status_extension = self.get_antigen_status(immunization=immunization)
        antigen_extension = None
        if antigen_status_extension is not None:
            for antigen_extension in antigen_status_extension.extension:
                if antigen_extension.url == 'antigen':
                    break
        return antigen_extension

    def get_antigen_status_dose_number(self, immunization=None):
        antigen_status_extension = self.get_antigen_status(immunization=immunization)
        antigen_extension = None
        if antigen_status_extension is not None:
            for antigen_extension in antigen_status_extension.extension:
                if antigen_extension.url == 'doseNumber':
                    break
        return antigen_extension

    def get_antigen_status_status(self, immunization=None):
        antigen_status_extension = self.get_antigen_status(immunization=immunization)
        antigen_extension = None
        if antigen_status_extension is not None:
            for antigen_extension in antigen_status_extension.extension:
                if antigen_extension.url == 'status':
                    break
        return antigen_extension

    def get_codeable_concept_coding(self, codeable_concept=None, coding_system=None, coding_version=None):
        coding_system = coding_system if coding_system is not None else self.coding_system
        coding_version = coding_version if coding_version is not None else self.coding_version
        
        coding = None
        if codeable_concept is not None and codeable_concept.coding is not None:
            for coding in codeable_concept.coding:
                if coding.system == coding_system and coding.version == coding_version:
                    break
        return coding
    
    def to_codeable_concept(self, code=None, display=None, id=None, coding_system=None, coding_version=None):
        coding_system = coding_system if coding_system is not None else self.coding_system
        coding_version = coding_version if coding_version is not None else self.coding_version
        coding = Coding()
        coding.code = code
        coding.display = display
        coding.id = id
        coding.version = coding_system
        coding.system = coding_system
        codeable_concept = CodeableConcept()
        codeable_concept.coding = [coding]
        return codeable_concept

    def get_lot_id(self, immunization=None):
        if immunization is None:
            immunization = self.fhir_resource
        if immunization is None or immunization.extension is None:
            return None
        lot_id = None
        for extension in immunization.extension:
            if extension.url == self.lot_id_url:
                lot_id = extension.valueString
        return lot_id
    
    def set_lot_id(self, immunization=None, lot_id=None):
        if immunization is None:
            immunization = self.fhir_resource
        if lot_id is not None:
            self.lot_id = lot_id
        lot_id_ext = Extension()
        lot_id_ext.url = self.lot_id_url
        lot_id_ext.valueString = self.lot_id
        immunization.extension = super().add_or_update_extension_to_extensions(extension=lot_id_ext, extensions=immunization.extension)

    def get_trade_name(self, immunization=None):
        if immunization is None:
            immunization = self.fhir_resource
        if immunization is None or immunization.extension is None:
            return None
        trade_name = None
        for extension in immunization.extension:
            if extension.url == self.trade_name_url:
                trade_name = extension.valueString
        return trade_name

    def set_trade_name(self, immunization=None, trade_name=None):
        if immunization is None:
            immunization = self.fhir_resource
        if trade_name is not None:
            self.trade_name = trade_name
        trade_name_ext = Extension()
        trade_name_ext.url = self.trade_name_url
        trade_name_ext.valueString = self.trade_name
        immunization.extension = super().add_or_update_extension_to_extensions(extension=trade_name_ext, extensions=immunization.extension)

    def get_contained_organization(self, immunization=None):
        if immunization is None:
            immunization = self.fhir_resource
        if immunization.contained is not None:
            for contained in immunization.contained:
                if type(contained) is Organization:
                    return contained
        return None

    def set_contained_organization(self, immunization=None, organization=None):
        if immunization is None:
            immunization = self.fhir_resource
        if organization is not None:
            self.organization = organization
        contained_organization = None
        if type(self.organization) is dict:
            contained_organization = Organization(jsondict=self.organization)
        elif type(self.organization) is Organization:
            contained_organization = self.organization
        if contained_organization is not None:
            if immunization.contained is None:
                immunization.contained = [contained_organization]
            else:
                org_found = False
                for contained in immunization.contained:
                    if type(contained) is Organization:
                        contained = self.organization
                        org_found = True
                if not org_found:
                    immunization.contained.append(self.organization)
    
    def get_vaccine_code(self, immunization=None, coding_system=None, coding_version=None):
        if immunization is None:
            immunization = self.fhir_resource
        vaccine_code = self.get_codeable_concept_coding(
            codeable_concept=immunization.vaccineCode,
            coding_system=coding_system,
            coding_version=coding_version)
        return vaccine_code

    def set_vaccine_code(self, immunization=None, vaccine_code=None, vaccine_id=None, vaccine_display=None, coding_system=None, coding_version=None):
        if immunization is None:
            immunization = self.fhir_resource
        if vaccine_id is not None and vaccine_code is not None and vaccine_display is not None:
            self.vaccine_code_code = vaccine_code
            self.vaccine_code_display = vaccine_display
            self.vaccine_code_id = vaccine_id

        vaccine_codeable_concept = self.to_codeable_concept(
            code=self.vaccine_code_code,
            display=self.vaccine_code_display,
            id=self.vaccine_code_id,
            coding_system=coding_system,
            coding_version=coding_version)
        immunization.vaccineCode = vaccine_codeable_concept

    def get_patient(self, immunization=None):
        if immunization is None:
            immunization = self.fhir_resource
        
        if type(immunization.patient) is Patient:
            patient = PatientFHIR(patient_resource_dict=immunization.patient.as_json())
            return patient
        return None

    def get_patient_reference(self, immunization=None):
        if immunization is None:
            immunization = self.fhir_resource
        
        if type(immunization.patient) is FHIRReference:
            return immunization.patient.reference
        return None
    
    def set_patient(self, immunization=None, patient_reference=None, patient=None):
        if immunization is None:
            immunization = self.fhir_resource

        if patient_reference is not None:
            self.patient_reference = patient_reference

        if patient is not None:
            self.patient = patient

        if self.patient is not None and self.patient_reference is None:
            patient_model = Patient(jsondict=self.patient.getFhirResource())
            immunization.patient = patient_model
        elif self.patient_reference is not None:
            reference = FHIRReference()
            reference.reference = self.patient_reference
            immunization.patient = reference

    def get_performer(self, immunization=None):
        if immunization is None:
            immunization = self.fhir_resource

        if immunization.performer is not None and type(immunization.performer) is Practitioner:
            return immunization.performer
        return None

    def get_performer_reference(self, immunization=None):
        if immunization is None:
            immunization = self.fhir_resource

        if immunization.performer is not None and type(immunization.performer) is FHIRReference:
            return immunization.performer
        return None

    def set_performer(self, immunization=None, performer=None, performer_reference=None, performer_display=None):
        if immunization is None:
            immunization = self.fhir_resource
        if performer is not None:
            self.performer = performer
        if performer_reference is not None:
            self.performer_reference = performer_reference
        if performer_display is not None:
            self.performer_display = performer_display

        if self.performer is not None and self.performer_reference is None:
            immunization.performer = self.performer
        elif self.performer_reference is not None:
            ref = FHIRReference()
            ref.reference = self.performer_reference
            ref.display = self.performer_display
            immunization.performer = ref

    def get_location(self, immunization=None):
        if immunization is None:
            immunization = self.fhir_resource
        if immunization.location is not None and type(immunization.location) is Location:
            return immunization.location
        return None

    def get_location_reference(self, immunization=None):
        if immunization is None:
            immunization = self.fhir_resource
        if immunization.location is not None and type(immunization.location) is FHIRReference:
            return immunization.location
        return None

    def set_location(self, immunization=None, location=None, location_reference=None, location_display=None):
        if immunization is None:
            immunization = self.fhir_resource
        if location is not None:
            self.location=location
        if location_reference is not None:
            self.location_reference = location_reference
        if location_display is not None:
            self.location_display = location_display

        if self.location is not None and self.location_reference is None:
            immunization.location = self.location
        elif self.location_reference is not None:
            ref = FHIRReference()
            ref.reference = self.location_reference
            ref.display = self.location_display
            immunization.location = ref

    def get_lot_number(self, immunization=None):
        if immunization is None:
            immunization = self.fhir_resource
        return immunization.lotNumber

    def set_lot_number(self, immunization=None, lot_number=None):
        if immunization is None:
            immunization = self.fhir_resource
        if lot_number is not None:
            self.lot_number = lot_number
        immunization.lotNumber = self.lot_number

    def get_expiration_date(self, immunization=None):
        if immunization is None:
            immunization = self.fhir_resource
        if immunization.expirationDate is not None:
            return immunization.expirationDate.isostring

    def set_expiration_date(self, immunization=None, expiration_date=None):
        if immunization is None:
            immunization = self.fhir_resource
        if expiration_date is not None:
            self.expiration_date = expiration_date
        if self.expiration_date is not None:
            if type(self.expiration_date) is str:
                immunization.expirationDate = datetime.strptime(self.expiration_date, "%Y-%m-%d")
            else:
                immunization.expirationDate = self.expiration_date

    def get_site(self, immunization=None, coding_system=None, coding_version=None):
        if immunization is None:
            immunization = self.fhir_resource
        if immunization.site is not None and type(immunization.site) is CodeableConcept:
            coding = self.get_codeable_concept_coding(
                codeable_concept=immunization.site,
                coding_system=coding_system,
                coding_version=coding_version)
            return coding
        return None

    def set_site(self, immunization=None, site_code=None, site_id=None, site_display=None, coding_system=None, coding_version=None):
        if immunization is None:
            immunization = self.fhir_resource
        if site_code is not None and site_id is not None and site_display is not None:
            self.site_code = site_code
            self.site_display = site_display
            self.site_id = site_id
        site = self.to_codeable_concept(
            code=self.site_code,
            display=self.site_display,
            id=self.site_id,
            coding_system=coding_system,
            coding_version=coding_version
        )
        immunization.site = site

    def get_dose_quantity(self, immunization=None):
        if immunization is None:
            immunization = self.fhir_resource
        return immunization.doseQuantity
            
    
    def set_dose_quantity(self, immunization=None, quantity_code=None, quantity_unit=None, quantity_value=None, quantity_system=None):
        if immunization is None:
            immunization = self.fhir_resource
        if quantity_system is None:
            quantity_system = self.coding_system
        if quantity_unit is not None and quantity_value is not None and quantity_code is not None:
            self.dose_quantity_code = quantity_code
            self.dose_quantity_unit = quantity_unit
            self.dose_quantity_value = quantity_value
        dose_quantity = Quantity()
        dose_quantity.code = self.dose_quantity_code
        dose_quantity.system = quantity_system
        dose_quantity.unit = self.dose_quantity_unit
        dose_quantity.value = self.dose_quantity_value
        immunization.doseQuantity = dose_quantity

    def get_reasons(self, immunization=None, coding_system=None, coding_version=None):
        if immunization is None:
            immunization  = self.fhir_resource
        if immunization.explanation is not None and immunization.explanation.reason is not None:
            reasons = []
            for reason in immunization.explanation.reason:
                if type(reason) is CodeableConcept:
                    reason_coding = self.get_codeable_concept_coding(
                        codeable_concept=reason,
                        coding_system=coding_system,
                        coding_version=coding_version)
                    reasons.append(reason_coding.as_json())
                elif type(reason) is Coding:
                    reasons.append(reason.as_json())
            return reasons

    def set_reason(self, immunization=None, reasons=None, coding_system=None, coding_version=None):
        if immunization is None:
            immunization = self.fhir_resource
        coding_system = coding_system if coding_system is not None else self.coding_system
        coding_version = coding_version if coding_version is not None else self.coding_version
        if reasons is not None and len(reasons) > 0:
            self.reason = reasons

        if self.reason is not None and len(self.reason) > 0:
            imm_explanation = ImmunizationExplanation()
            imm_explanation.reason = []
            for reason in self.reason:
                reason_coding = Coding(jsondict=reason)
                reason_coding.version = coding_version
                reason_coding.system = coding_system 
                imm_explanation.reason.append(reason_coding)
            immunization.explanation = imm_explanation

    def get_date(self, immunization=None):
        if immunization is None:
            immunization = self.fhir_resource
        return immunization.date

    def set_date(self, immunization=None, date_to_set=None):
        if immunization is None:
            immunization = self.fhir_resource
        if date_to_set is not None:
            if type(date_to_set) is str:
                self.date = date_to_set
            elif type(date_to_set) is date or type(date_to_set) is datetime:
                self.date = datetime.strftime(date_to_set, "%Y-%m-%dT%H:%M:%S")
        if type(self.date) is date or type(self.date) is datetime:
            self.date = datetime.strftime(self.date,"%Y-%m-%dT%H:%M:%S")
        immunization.date = FHIRDate(jsonval=self.date) if self.date is not None else None
        

    def get_status(self, immunization=None):
        if immunization is None:
            immunization = self.fhir_resource
        return immunization.status

    def set_status(self, immunization=None, status=None):
        if immunization is None:
            immunization = self.fhir_resource
        if status is not None:
            self.status = status
        immunization.status = self.status

    def to_fhir_resource(self, immunization=None):
        if immunization is None:
            immunization = Immunization()
        self.set_id(immunization=immunization)
        self.set_meta(immunization=immunization)
        self.set_contained_organization(immunization=immunization)
        self.set_override_status(immunization=immunization)
        self.set_lot_id(immunization=immunization)
        self.set_antigen_status(immunization=immunization)
        self.set_trade_name(immunization=immunization)
        self.set_vaccine_code(immunization=immunization)
        self.set_patient(immunization=immunization)
        self.set_performer(immunization=immunization)
        self.set_location(immunization=immunization)
        self.set_lot_number(immunization=immunization)
        self.set_expiration_date(immunization=immunization)
        self.set_site(immunization=immunization)
        self.set_dose_quantity(immunization=immunization)
        self.set_reason(immunization=immunization)
        self.set_date(immunization=immunization)
        self.set_status(immunization=immunization)
        return immunization

    def getFhirResource(self):
        self.fhir_resource = self.to_fhir_resource()
        resource = self.fhir_resource.as_json()
        return resource
        
    def from_dict(self, imm_dict=None):
        if imm_dict is None:
            return None
        imm_resource = Immunization(jsondict=imm_dict)
        self.from_fhir_resource(immunization=imm_resource)

    def from_fhir_resource(self, immunization=None, coding_system=None, coding_version=None):
        if immunization is None:
            immunization = self.fhir_resource

        self.fhir_resource = immunization
        self.id = self.get_id()
        antigen = self.get_antigen_status_antigen()
        antigen_coding = self.get_codeable_concept_coding(
            codeable_concept=antigen.valueCodeableConcept,
            coding_system=coding_system,
            coding_version=coding_version)
        self.antigen_code = antigen_coding.code
        self.antigen_display = antigen_coding.display
        self.antigen_id = antigen_coding.id
        dose_number = self.get_antigen_status_dose_number()
        self.antigen_dose_number = dose_number.valueInteger
        antigen_status = self.get_antigen_status_status()
        antigen_status_code = self.get_codeable_concept_coding(
            codeable_concept=antigen_status.valueCodeableConcept,
            coding_system=coding_system,
            coding_version=coding_version)
        self.antigen_status_code = antigen_status_code.code
        self.antigen_status_display = antigen_status_code.display
        self.antigen_status_id = antigen_status_code.id
        self.updated_by = self.get_meta_updated_by()
        self.created_by = self.get_meta_created_by()
        self.creation_date = self.get_meta_creation_date().isostring
        self.version_id = self.get_meta_version_id()
        self.last_updated = self.get_meta_last_updated()
        self.profile = self.get_meta_profile()
        self.organization = self.get_contained_organization()
        override_status_extension = self.get_override_status()
        override_status_coding = self.get_codeable_concept_coding(
            codeable_concept=override_status_extension.valueCodeableConcept,
            coding_system=coding_system,
            coding_version=coding_version)
        self.override_status_code = override_status_coding.code
        self.override_status_display = override_status_coding.display
        self.override_status_id = override_status_coding.id
        self.lot_id = self.get_lot_id()
        self.trade_name = self.get_trade_name()
        self.status = self.get_status()
        self.date = self.get_date().isostring
        vaccine_code = self.get_vaccine_code(
            coding_system=coding_system,
            coding_version=coding_version)
        self.vaccine_code_code = vaccine_code.code
        self.vaccine_code_display = vaccine_code.display
        self.vaccine_code_id = vaccine_code.id
        self.patient = self.get_patient(immunization=immunization)
        self.patient_reference = self.get_patient_reference(immunization=immunization)
        performer_reference = self.get_performer_reference(immunization=immunization)
        if performer_reference is not None:
            self.performer_reference = performer_reference.reference
            self.performer_display = performer_reference.display
        else:
            self.performer = self.get_performer(immunization=immunization)

        self.location = self.get_location(immunization=immunization)
        location_ref = self.get_location_reference(immunization=immunization)
        if location_ref is not None:
            self.location_reference = location_ref.reference
            self.location_display = location_ref.display
        self.lot_number = self.get_lot_number(immunization=immunization)
        self.expiration_date = self.get_expiration_date(immunization=immunization)
        site = self.get_site(
            immunization=immunization,
            coding_system=coding_system,
            coding_version=coding_version)
        if site is not None:
            self.site_code = site.code
            self.site_display = site.display
            self.site_id = site.id
        route_coding = self.get_codeable_concept_coding(
            immunization.route,
            coding_system=coding_system,
            coding_version=coding_version)
        self.route_code = route_coding.code
        self.route_display = route_coding.display
        self.route_id = route_coding.id
        dose_quantity = self.get_dose_quantity(immunization=immunization)
        if dose_quantity is not None:
            self.dose_quantity_code = dose_quantity.code
            self.dose_quantity_unit = dose_quantity.unit
            self.dose_quantity_value = dose_quantity.value
        self.reason = self.get_reasons(immunization=immunization,coding_system=coding_system, coding_version=coding_version)

class PatientFHIR(BaseFHIR):
    resource_type = 'Patient'
    default_coding_system = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary'
    default_coding_version = "1.0.0"
    nam_identifier_extension_url = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#patient/healthcardorigin"
    nam_identifier_system = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary/identifierType?code=NAM"
    niu_identifier_system = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary/identifierType?code=NIUU"
    aucun_identifier_system = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary/identifierType?code=AUCUN"
    matchramq_extension_url = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#patient/matchramq"
    id = None
    user_name = None
    creation_date = None
    update_timestamp = None
    matchramq = None
    active = True
    nam = None
    niu = None
    family_name = None
    given_name = None
    phone_number = None
    gender = None
    birth_date = None
    deceased_boolean = False
    address_line = None
    address_city = None
    address_state = None
    address_postal_code = None
    address_country = None
    mother_given_name = None
    mother_family_name = None
    father_given_name = None
    father_family_name = None
    base_url = ""
    patient_endpoint = "{0}/Patient"
    patient_id_endpoint = "{0}/Patient/{1}"
    patient_match_endpoint = "{0}/Patient/$match"
    patient_definir_niu_endpoint = patient_id_endpoint + "/$definir-niu"

    headers = {}
    fhir_resource = None
    def __init__(self, base_url=None, base_uri=None, patient_dict=None, token=None, patient_resource_dict=None):
        super().__init__(base_url=base_url, base_uri=base_uri)

        if patient_resource_dict is None and patient_dict is not None:
            self.from_dict(patient_dict)
            self.fhir_resource = self.patient_dict_to_fhir_patient(patient_dict=patient_dict, patient=Patient())
        elif patient_resource_dict is not None:
            self.fhir_resource = Patient(jsondict=patient_resource_dict)
            self.from_fhir_patient()
        else:
            self.fhir_resource = Patient()

        if base_url is not None:
            self.base_url = base_url
            
        self.setHeaders(token=token)

    def from_dict(self, patient_dict):
        self.id = patient_dict['id'] if 'id' in patient_dict else None
        self.given_name = patient_dict['given_name'] if 'given_name' in patient_dict else None
        self.family_name = patient_dict['family_name'] if 'family_name' in patient_dict else None
        self.active = patient_dict['active'] if 'active' in patient_dict else True
        self.gender = patient_dict['gender'] if 'gender' in patient_dict else None
        self.birth_date = patient_dict['birth_date'] if 'birth_date' in patient_dict else None
        self.niu = patient_dict['niu'] if 'niu' in patient_dict else None
        self.nam = patient_dict['nam'] if 'nam' in patient_dict else None
        self.address_line = patient_dict['address_line'] if 'address_line' in patient_dict else None
        self.address_city = patient_dict['address_city'] if 'address_city' in patient_dict else None
        self.address_state = patient_dict['address_state'] if 'address_state' in patient_dict else None
        self.address_postal_code = patient_dict['address_postal_code'] if 'address_postal_code' in patient_dict else None
        self.address_country = patient_dict['address_country'] if 'address_country' in patient_dict else None
        self.mother_given_name = patient_dict['mother_given_name'] if 'mother_given_name' in patient_dict else None
        self.mother_family_name = patient_dict['mother_family_name'] if 'mother_family_name' in patient_dict else None
        self.father_given_name = patient_dict['father_given_name'] if 'father_given_name' in patient_dict else None
        self.father_family_name = patient_dict['father_family_name'] if 'father_family_name' in patient_dict else None
        self.phone_number = patient_dict['phone_number'] if 'phone_number' in patient_dict else None

    def from_json(self, resource):
        if type(resource) is str:
            str_resource = resource
            resource = json.loads(str_resource)
        self.fhir_resource = Patient(jsondict=resource)
        self.from_fhir_patient()

    def getFhirResource(self):
        self.to_fhir_patient()
        return self.fhir_resource.as_json()

    def getFhirResourceParameter(self):
        self.to_fhir_patient()
        param = ParameterFHIR()
        param.add_parameter(self.fhir_resource)
        return param.getFhirResource()

    def setHeaders(self, headers={}, token=None):
        newHeaders = {**headers, **self.base_headers}
        if token is not None:
            if 'Content-type' in token:
                del token['Content-type']
            headersWithAuth = {**newHeaders, **token}
            self.headers = headersWithAuth
        else:
            self.headers = newHeaders
        return self.headers

    def Create(self):
        res = self.getFhirResource()
        response = requests.post(url=self.patient_endpoint.format(
            self.get_fhir_url()), data=json.dumps(res), headers=self.headers)
        self.from_json(resource=response.content.decode())
        if self.niu is not None:
            res = self.getFhirResourceParameter()
            requests.post(url=self.patient_definir_niu_endpoint.format(
                self.get_fhir_url(), self.id), data=json.dumps(res), headers=self.headers)
        return response

    def GetById(self, patient_id=None):
        response = requests.get(url=self.patient_id_endpoint.format(
            self.get_fhir_url(), patient_id), headers=self.headers)
        self.from_json(resource=response.content.decode())
        return response

    def Match(self):
        res = self.getFhirResourceParameter()
        response = requests.post(url=self.patient_match_endpoint.format(
            self.get_fhir_url()), data=json.dumps(res), headers=self.headers)
        if response.status_code == 200:
            params = ParameterFHIR(resource=json.loads(response.content.decode()))
            if params.fhir_resource is not None and params.fhir_resource.parameter is not None:
                for param in params.fhir_resource.parameter:
                    if type(param.resource) is Patient:
                        self.fhir_resource = param.resource
                        self.from_fhir_patient()
        return response

    def Search(self, identifier=None, given=None, family=None, gender=None, birthdate=None):
        params = {}
        if identifier is not None:
            params['identifier'] = identifier
        elif self.nam is not None:
            params['identifier'] = "code=NAM|{}".format(self.nam)
        if given is not None:
            params['given'] = given
        elif self.given_name is not None:
            params['given'] = self.given_name
        if family is not None:
            params['family'] = family
        elif self.family_name is not None:
            params['family'] = self.family_name
        if gender is not None:
            params['gender'] = gender
        elif self.gender is not None:
            params['gender'] = self.gender
        if birthdate is not None:
            params['birthdate'] = birthdate
        elif self.birth_date is not None:
            params['birthdate'] = self.birth_date
        response = requests.get(url=self.patient_endpoint.format(
            self.get_fhir_url()), params=params, headers=self.headers)

        return response

    def nam_to_identifier(self, nam, coding_system=None, coding_version=None):
        nam_coding_system = coding_system if coding_system is not None else self.default_coding_system
        nam_coding_version = coding_system if coding_version is not None else self.default_coding_version
        nam_identifier = Identifier()
        nam_identifier_extension = Extension()
        nam_identifier_extension.url = self.nam_identifier_extension_url
        nam_ext_codable_concept = CodeableConcept()
        nam_ext_codable_concept.coding = [Coding(jsondict={"system": nam_coding_system,"version": nam_coding_version,"code": "QC"})]
        nam_identifier_extension.valueCodeableConcept = nam_ext_codable_concept
        nam_identifier.extension = [nam_identifier_extension]
        nam_type_codable_concept = CodeableConcept()
        nam_type_codable_concept.coding = [Coding(jsondict={"system": nam_coding_system,"version": nam_coding_version,"code": "NAM"})]
        nam_identifier.type = nam_type_codable_concept
        nam_identifier.system = self.nam_identifier_system
        nam_identifier.value = nam
        return nam_identifier

    def niu_to_identifier(self, niu, coding_system=None, coding_version=None):
        niu_coding_system = coding_system if coding_system is not None else self.default_coding_system
        niu_coding_version = coding_system if coding_version is not None else self.default_coding_version
        niu_identifier = Identifier()
        niu_type_codable_concept = CodeableConcept()
        niu_type_codable_concept.coding = [Coding(jsondict={"system": niu_coding_system,"version": niu_coding_version,"code": "NIUU","display":"NIU"})]
        niu_identifier.type = niu_type_codable_concept
        niu_identifier.value = niu
        niu_identifier.system = self.niu_identifier_system
        return niu_identifier

    def aucun_identifiant_to_identifier(self, coding_system=None, coding_version=None):
        coding_system = coding_system if coding_system is not None else self.default_coding_system
        coding_version = coding_system if coding_version is not None else self.default_coding_version
        aucun_identifier = Identifier()
        aucun_type_codable_concept = CodeableConcept()
        aucun_type_codable_concept.coding = [Coding(jsondict={"system": coding_system,"version": coding_version,"code": "AUCUN","display":"Aucun identifiant"})]
        aucun_identifier.type = aucun_type_codable_concept
        aucun_identifier.system = self.aucun_identifier_system
        return aucun_identifier

    def given_family_to_human_name(self, given_name=None, family_name=None):
        hn = HumanName()
        hn.given = [given_name]
        hn.family = [family_name]
        return hn

    def str_date_to_fhir_date(self, str_date):
        fhir_date  = FHIRDate()
        fhir_date.date = datetime.strptime(str_date, '%Y-%m-%d').date()
        return fhir_date

    def fhir_date_to_str_date(self, fhir_date):
        str_date = None
        if fhir_date is not None and fhir_date.date is not None:
            str_date = fhir_date.isostring
        return str_date

    def set_id(self, id, patient=None):
        if patient is None:
            patient = self.fhir_resource
            self.id = id
        patient.id = id

    def get_id(self, patient=None):
        if patient is None:
            patient = self.fhir_resource
        return patient.id

    def set_matchramq(self, matchramq=False, patient=None):
        if type(matchramq) is bool:
            bool_matchramq = matchramq
        elif type(matchramq) is str:
            bool_matchramq = bool(strtobool(matchramq))
        else:
            bool_matchramq = False
        if patient is None:
            patient = self.fhir_resource
        matchramq_extension = Extension()
        matchramq_extension.url = self.matchramq_extension_url
        matchramq_extension.valueBoolean = bool_matchramq

        if patient.extension is None:    
            patient.extension = [matchramq_extension]
        else:
            extension_found = False
            for ext in patient.extension:
                if ext.url == self.matchramq_extension_url:
                    extension_found = True
                    ext.valueBoolean = bool_matchramq
                    break
            if not extension_found:
                patient.extension.append(matchramq_extension)

    def get_matchramq(self, patient=None):
        matchramq = False
        if patient.extension is not None:    
            for ext in patient.extension:
                if ext.url == self.matchramq_extension_url:
                    return ext.valueBoolean
        return matchramq        

    def set_active(self, active, patient=None):
        if patient is None:
            patient = self.fhir_resource
            self.active = active
        patient.active = active

    def get_active(self, patient=None):
        if patient is None:
            patient = self.fhir_resource
        return patient.active

    def set_name(self, given_name=None, family_name=None, patient=None):
        if patient is None:
            patient = self.fhir_resource
            self.given_name = given_name
            self.family_name = family_name
        hn = self.given_family_to_human_name(given_name=given_name, family_name=family_name)
        if patient.name is None:
            patient.name = [hn]

    def get_name(self, index=0, patient=None):
        if patient is None:
            patient = self.fhir_resource

        return patient.name[index]

    def get_given_name(self, index=0, patient=None):
        if patient is None:
            patient = self.fhir_resource

        given_name = None
        if patient.name is not None and len(patient.name) > 0 and len(patient.name[index].given) > 0:
            given_name = patient.name[index].given[index]
        return given_name

    def get_family_name(self, index=0, patient=None):
        if patient is None:
            patient = self.fhir_resource
        family_name = None
        if patient.name is not None and len(patient.name) > 0 and len(patient.name[index].family) > 0:
            family_name = patient.name[index].family[index]
        return family_name

    def set_gender(self, gender, patient=None):
        if patient is None:
            patient = self.fhir_resource
            self.gender = gender

        patient.gender = gender

    def get_gender(self, patient=None):
        if patient is None:
            patient = self.fhir_resource

        return patient.gender

    def set_nam(self, nam, patient=None, coding_system=None, coding_version=None):
        if patient is None:
            patient = self.fhir_resource
            self.nam = nam
        nam_identifier = self.nam_to_identifier(nam=nam, coding_system=coding_system, coding_version=coding_version)
        if patient.identifier is None:
            patient.identifier = [nam_identifier]
        else:
            nam_identifier_found = False
            for identifier in patient.identifier:
                if identifier.system == self.nam_identifier_system:
                    identifier.value = nam
                    nam_identifier_found = True
            if not nam_identifier_found and nam_identifier is not None:
                patient.identifier.append(nam_identifier)

    def get_nam(self, patient=None):
        nam = None
        if patient is None:
            patient = self.fhir_resource
        if patient.identifier is not None:
            for identifier in patient.identifier:
                if identifier.system == self.nam_identifier_system:
                    nam = identifier.value
        return nam

    def set_niu(self, niu, patient=None, coding_system=None, coding_version=None):
        if patient is None:
            patient = self.fhir_resource
            self.niu = niu

        niu_identifier = self.niu_to_identifier(niu=niu, coding_system=coding_system, coding_version=coding_version)
        if patient.identifier is None:
            patient.identifier = [niu_identifier]
        else:
            niu_identifier_found = False
            for identifier in patient.identifier:
                if identifier.system == self.niu_identifier_system:
                    identifier.value = niu
                    niu_identifier_found = True
            if not niu_identifier_found and niu_identifier is not None:
                patient.identifier.append(niu_identifier)

    def get_niu(self, patient=None):
        niu = None
        if patient is None:
            patient = self.fhir_resource
        if patient.identifier is not None:
            for identifier in patient.identifier:
                if identifier.system == self.niu_identifier_system:
                    niu = identifier.value
        return niu

    def set_aucun_identifiant(self, patient=None, coding_system=None, coding_version=None):
        if patient is None:
            patient = self.fhir_resource

        aucun_identifier = self.aucun_identifiant_to_identifier(coding_system=coding_system, coding_version=coding_version)
        patient.identifier = [aucun_identifier]

    def set_birth_date(self, str_date, patient=None):
        if patient is None:
            patient = self.fhir_resource
            self.birth_date = str_date
        patient.birthDate = self.str_date_to_fhir_date(str_date)

    def get_birth_date(self, patient=None):
        if patient is None:
            patient = self.fhir_resource
        return self.fhir_date_to_str_date(fhir_date=patient.birthDate)

    def set_address(self, address_line=None, address_city=None, address_state=None, address_postal_code=None, address_country=None, patient=None):
        if patient is None:
            patient = self.fhir_resource
            self.address_city = address_city
            self.address_country = address_country
            self.address_line = address_line
            self.address_postal_code = address_postal_code
            self.address_state = address_state
        address = Address()
        address.city = address_city
        address.country = address_country
        address.state = address_state
        address.postalCode = address_postal_code
        address.line = [address_line]
        patient.address = [address]

    def get_address(self, patient=None, index=0):
        if patient is None:
            patient = self.fhir_resource
        if patient.address is not None and len(patient.address) > index:
            return patient.address[index]
        return None

    def set_mother_name(self, mother_given_name=None, mother_family_name=None, patient=None, coding_system=None, coding_version=None):
        if patient is None:
            patient = self.fhir_resource
            self.mother_family_name = mother_family_name
            self.mother_given_name = mother_given_name
        mother_coding_system = coding_system if coding_system is not None else self.default_coding_system
        mother_coding_version = coding_system if coding_version is not None else self.default_coding_version
        contact = PatientContact()
        hn = self.given_family_to_human_name(given_name=mother_given_name, family_name=mother_family_name)
        contact.name = hn
        mother_codable_concept = CodeableConcept()
        mother_codable_concept.coding = [Coding(jsondict={"system": mother_coding_system,"version": mother_coding_version,"code": "MERE"})]
        contact.relationship = [mother_codable_concept]
        if patient.contact is None:
            patient.contact = [contact]
        else:
            contact_found = False
            for patient_contact in patient.contact:
                for relationship in patient_contact.relationship:
                    for coding in relationship.coding:
                        for mother_codable_concept_coding in mother_codable_concept.coding:
                            if coding.code == mother_codable_concept_coding.code and coding.system == mother_codable_concept_coding and coding.version and mother_codable_concept_coding.version:
                                patient_contact = contact
                                contact_found = True
                                break
                        if contact_found:
                            break
                    if contact_found:
                        break
                if contact_found:
                    break
            if not contact_found and contact is not None:
                patient.contact.append(contact)

    def get_mother_name(self, patient=None, coding_system=None, coding_version=None):
        mother_coding_system = coding_system if coding_system is not None else self.default_coding_system
        mother_coding_version = coding_system if coding_version is not None else self.default_coding_version
        if patient is None:
            patient = self.fhir_resource
        mother_name = None
        if patient.contact is not None:
            for patient_contact in patient.contact:
                for relationship in patient_contact.relationship:
                    for coding in relationship.coding:
                        if coding.code == 'MERE' and coding.system == mother_coding_system and coding.version == mother_coding_version:
                            mother_name = patient_contact.name
                            break
                    if mother_name is not None:
                        break
                if mother_name is not None:
                    break
                    
        return mother_name
        
    def set_father_name(self, father_given_name=None, father_family_name=None, patient=None, coding_system=None, coding_version=None):
        if patient is None:
            patient = self.fhir_resource
            self.father_family_name = father_family_name
            self.father_given_name = father_given_name
        father_coding_system = coding_system if coding_system is not None else self.default_coding_system
        father_coding_version = coding_system if coding_version is not None else self.default_coding_version
        contact = PatientContact()
        hn = self.given_family_to_human_name(given_name=father_given_name, family_name=father_family_name)
        contact.name = hn
        father_codable_concept = CodeableConcept()
        father_codable_concept.coding = [Coding(jsondict={"system": father_coding_system,"version": father_coding_version,"code": "PERE"})]
        contact.relationship = [father_codable_concept]
        if patient.contact is None:
            patient.contact = [contact]
        else:
            contact_found = False
            for patient_contact in patient.contact:
                for relationship in patient_contact.relationship:
                    for coding in relationship.coding:
                        for father_codable_concept_coding in father_codable_concept.coding:
                            if coding.code == father_codable_concept_coding.code and coding.system == father_codable_concept_coding and coding.version and father_codable_concept_coding.version:
                                patient_contact = contact
                                contact_found = True
                                break
                        if contact_found:
                            break
                    if contact_found:
                        break
                if contact_found:
                    break
            if not contact_found and contact is not None:
                patient.contact.append(contact)
        
    def get_father_name(self, patient=None, coding_system=None, coding_version=None):
        if patient is None:
            patient = self.fhir_resource
        father_coding_system = coding_system if coding_system is not None else self.default_coding_system
        father_coding_version = coding_system if coding_version is not None else self.default_coding_version
        father_name = None
        if patient.contact is not None:
            for patient_contact in patient.contact:
                for relationship in patient_contact.relationship:
                    for coding in relationship.coding:
                        if coding.code == 'PERE' and coding.system == father_coding_system and coding.version == father_coding_version:
                            father_name = patient_contact.name
                            break
                    if father_name is not None:
                        break
                if father_name is not None:
                    break
        return father_name

    def set_phone_number(self, phone_number, patient=None):
        if not phone_number.startswith('+1'):
            phone_number = '+1{0}'.format(phone_number)
        if patient is None:
            patient = self.fhir_resource
            self.phone_number = phone_number
        contact_point = ContactPoint()
        contact_point.system = 'phone'
        contact_point.value = phone_number

        if patient.telecom is None:
            patient.telecom = [contact_point]
        else:
            for point in patient.telecom:
                phone_found = False
                if point.system == 'phone':
                    point = contact_point
                    phone_found = True
                    break
            if not phone_found and contact_point is not None:
                patient.telecom.append(contact_point)
         
    def get_phone_number(self, patient=None):
        if patient is None:
            patient = self.fhir_resource
        phone_number = None
        if patient.telecom is not None:
            for point in patient.telecom:
                if point.system == 'phone':
                    phone_number = point.value
                    break
        return phone_number

    def patient_dict_to_fhir_patient(self, patient_dict=None, coding_system=None, coding_version=None, patient=None):
        patient_coding_system = coding_system if coding_system is not None else self.default_coding_system
        patient_coding_version = coding_system if coding_version is not None else self.default_coding_version

        if patient_dict is not None:
            if 'matchramq' in patient_dict and patient_dict['matchramq'] is not None:
                self.set_matchramq(matchramq=patient_dict['matchramq'], patient=patient)
            if 'given_name' in patient_dict or 'family_name' in patient_dict:
                given = patient_dict['given_name'] if 'given_name' in patient_dict else None
                family = patient_dict['family_name'] if 'family_name' in patient_dict else None
                self.set_name(given_name=given, family_name=family, patient=patient)
            if 'nam' not in patient_dict and 'niu' not in patient_dict:
                self.set_aucun_identifiant(patient=patient)
            else:
                if 'nam' in patient_dict:
                    self.set_nam(nam=patient_dict['nam'], coding_system=patient_coding_system, coding_version=patient_coding_version, patient=patient)
                if 'niu' in patient_dict:
                    self.set_niu(niu=patient_dict['niu'], coding_system=patient_coding_system, coding_version=patient_coding_version, patient=patient)
            if 'gender' in patient_dict:
                self.set_gender(gender=patient_dict['gender'], patient=patient)
            if 'birth_date' in patient_dict:
                self.set_birth_date(str_date=patient_dict['birth_date'], patient=patient)
            if 'id' in patient_dict:
                self.set_id(id=patient_dict['id'], patient=patient)
            active = patient_dict['active'] if 'active' in patient_dict else True
            self.set_active(active=active, patient=patient)
            if 'address_line' in patient_dict or 'address_city' in patient_dict or 'address_postal_code' in patient_dict or 'address_state' in patient_dict or 'address_country' in patient_dict:
                address_line = patient_dict['address_line'] if 'address_line' in patient_dict else None
                address_city = patient_dict['address_city'] if 'address_city' in patient_dict else None
                address_state = patient_dict['address_state'] if 'address_state' in patient_dict else None
                address_postal_code = patient_dict['address_postal_code'] if 'address_postal_code' in patient_dict else None
                address_country = patient_dict['address_country'] if 'address_country' in patient_dict else None
                self.set_address(
                    address_city=address_city,
                    address_country=address_country,
                    address_line=address_line,
                    address_state=address_state,
                    address_postal_code=address_postal_code,
                    patient=patient)
            if 'mother_given_name' in patient_dict or 'mother_family_name' in patient_dict:
                mother_given_name = patient_dict['mother_given_name'] if 'mother_given_name' in patient_dict else None
                mother_family_name = patient_dict['mother_family_name'] if 'mother_family_name' in patient_dict else None
                self.set_mother_name(mother_family_name=mother_family_name, mother_given_name=mother_given_name, patient=patient, coding_system=patient_coding_system, coding_version=patient_coding_version)

            if 'father_given_name' in patient_dict or 'father_family_name' in patient_dict:
                father_given_name = patient_dict['father_given_name'] if 'father_given_name' in patient_dict else None
                father_family_name = patient_dict['father_family_name'] if 'father_family_name' in patient_dict else None
                self.set_father_name(father_family_name=father_family_name, father_given_name=father_given_name, patient=patient, coding_system=patient_coding_system, coding_version=patient_coding_version)
            if 'phone_number' in patient_dict:
                self.set_phone_number(phone_number=patient_dict['phone_number'], patient=patient)

        return patient

    def from_fhir_patient(self, patient=None, coding_system=None, coding_version=None):
        if patient is None:
            patient = self.fhir_resource

        self.id = self.get_id(patient=patient)
        self.matchramq = self.get_matchramq(patient=patient)
        self.nam = self.get_nam(patient=patient)
        self.niu = self.get_niu(patient=patient)
        self.given_name = self.get_given_name(patient=patient)
        self.family_name = self.get_family_name(patient=patient)
        self.active = self.get_active(patient=patient)
        self.gender = self.get_gender(patient=patient)
        self.birth_date = self.get_birth_date(patient=patient)
        address = self.get_address(patient=patient)
        if address is not None:
            self.address_line = address.line
            self.address_city = address.city
            self.address_state = address.state
            self.address_postal_code = address.postalCode
            self.address_country = address.country
        mother_name =  self.get_mother_name(patient=patient, coding_system=coding_system, coding_version=coding_version)
        if mother_name is not None:
            self.mother_given_name = mother_name.given
            self.mother_family_name = mother_name.family
        father_name = self.get_father_name(patient=patient, coding_system=coding_system, coding_version=coding_version)
        if father_name is not None:
            self.father_given_name = father_name.given
            self.father_family_name = father_name.family
        self.phone_number = self.get_phone_number(patient=patient)
        
    def to_fhir_patient(self, patient=None, coding_system=None, coding_version=None):
        if patient is None:
            patient = self.fhir_resource

        if self.id is not None:
            self.set_id(id=self.id, patient=patient)
        if self.niu is None and self.nam is None:
            self.set_aucun_identifiant(patient=patient)
        else:
            if self.nam is not None:
                self.set_nam(nam=self.nam, patient=patient)
            if self.niu is not None:
                self.set_niu(niu=self.niu, patient=patient)
        self.set_active(active=self.active, patient=patient)
        self.set_matchramq(matchramq=self.matchramq, patient=patient)
        if self.address_city is not None or self.address_country is not None or self.address_line is not None or self.address_postal_code is not None or self.address_state is not None:
            self.set_address(
                address_city=self.address_city,
                address_country=self.address_country,
                address_line=self.address_line,
                address_state=self.address_state,
                address_postal_code=self.address_postal_code,
                patient=patient)            
        if self.birth_date is not None:
            self.set_birth_date(str_date=self.birth_date, patient=patient)
        if self.family_name is not None or self.given_name is not None:
            self.set_name(given_name=self.given_name, family_name=self.family_name)
        if self.father_family_name is not None or self.father_given_name is not None:
            self.set_father_name(father_given_name=self.father_given_name, father_family_name=self.father_family_name, coding_system=coding_system, coding_version=coding_version)
        if self.mother_family_name is not None or self.mother_given_name is not None:
            self.set_mother_name(mother_given_name=self.mother_given_name, mother_family_name=self.mother_family_name, coding_system=coding_system, coding_version=coding_version)
        self.set_gender(gender=self.gender, patient=patient)
        if self.phone_number is not None:
            self.set_phone_number(phone_number=self.phone_number, patient=patient)

class OrganizationFHIR(BaseFHIR):
    organization_endpoint = "{base_url}/Organization"
    search_endpoint = organization_endpoint + "/_search"
    get_by_id_endpoint = organization_endpoint + "/{id}"
    rrss_system = 'https://pro.consultation.rrss.rtss.qc.ca'
    rrss_mot_cle_extension_url = 'http://www.santepublique.rtss.qc.ca/sipmi/rrss/1.0.0/extensions/#motscles'

    def __init__(self, base_url=None, base_uri=None, resource=None, token_header=None) -> None:
        super().__init__(base_url=base_url, base_uri=base_uri, token_header=token_header)
        if resource is not None:
            self.fhir_resource = Organization(jsondict=resource)
        else:
            self.fhir_resource = Organization()

    def getFhirResource(self):
        return self.fhir_resource.as_json()

    def get_id(self, organization=None):
        if organization is None:
            organization = self.fhir_resource
        return organization.id

    def get_id_rrss(self, organization=None):
        if organization is None:
            organization = self.fhir_resource
        if organization.identifier is not None:
            for identifier in organization.identifier:
                if identifier.system == self.rrss_system:
                    return identifier.value
        return None

    def set_name(self, organization=None, name=None):
        if organization is None:
            organization = self.fhir_resource

        organization.name = name

    def get_name(self, organization=None):
        if organization is None:
            organization = self.fhir_resource
        return organization.name

    def have_mot_cle(self, organization=None, mot_cle=None):
        if organization is None:
            organization = self.fhir_resource
        if mot_cle is not None and organization.extension is not None:
            for extension in organization.extension:
                if extension.url == self.rrss_mot_cle_extension_url and extension.valueString == mot_cle:
                    return True
        return False

    def search(self, name=None, identifier=None):
        params = {}
        if name is not None:
            params['name'] = name
        if identifier is not None:
            params['identifier'] = identifier
        response = requests.get(url=self.organization_endpoint.format(base_url=self.get_fhir_url()), params=params, headers=self.headers)
        content = json.loads(response.content.decode())
       
        return self.get_visitor_from_json(jsondict=content)

class LocationFHIR(BaseFHIR):
    location_endpoint = "{base_url}/Location"
    get_by_id_endpoint = location_endpoint + "/{id}"
    rrss_system = 'https://pro.consultation.rrss.rtss.qc.ca'
    rrss_mot_cle_extension_url = 'http://www.santepublique.rtss.qc.ca/sipmi/rrss/1.0.0/extensions/#motscles'

    def __init__(self, base_url=None, base_uri=None, resource=None, token_header=None) -> None:
        super().__init__(base_url=base_url, base_uri=base_uri, token_header=token_header)
        if resource is not None:
            self.fhir_resource = Location(jsondict=resource)
        else:
            self.fhir_resource = Location()

    def getFhirResource(self):
        return self.fhir_resource.as_json()

    def have_mot_cle(self, location=None, mot_cle=None):
        if location is None:
            location = self.fhir_resource
        if mot_cle is not None and location.extension is not None:
            for extension in location.extension:
                if extension.url == self.rrss_mot_cle_extension_url and extension.valueString == mot_cle:
                    return True
        return False

    def set_name(self, location=None, name=None):
        if location is None:
            location = self.fhir_resource

        location.name = name

    def get_name(self, location=None):
        if location is None:
            location = self.fhir_resource
        return location.name

    def get_id(self, location=None):
        if location is None:
            location = self.fhir_resource
        return location.id

    def get_id_rrss(self, location=None):
        if location is None:
            location = self.fhir_resource
        if location.identifier is not None:
            for identifier in location.identifier:
                if identifier.system == self.rrss_system:
                    return identifier.value
        return None

    def search(self, name=None, address_city=None, identifier=None):
        params = {}
        if name is not None:
            params['name'] = name
        if identifier is not None:
            params['identifier'] = identifier
        if address_city is not None:
            params['address-city'] = address_city
        response = requests.get(url=self.location_endpoint.format(base_url=self.get_fhir_url()), params=params, headers=self.headers)
        content = json.loads(response.content.decode())
    
        return self.get_visitor_from_json(jsondict=content)
    
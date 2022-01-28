# -*- coding: utf-8 -*-
# Copyright © 2021 Wacom. All rights reserved.
import json
import urllib.parse
from http import HTTPStatus
from typing import Dict, List, Any, Optional, Tuple

import requests
from requests import Response

from knowledge.base.entity import OntologyContext, LocalizedContent, Label, Comment
from knowledge.base.ontology import OntologyClassReference, OntologyPropertyReference, OntologyProperty, OntologyClass,\
    PropertyType, THING_CLASS, DataPropertyType
from knowledge.services import USER_AGENT_STR
from knowledge.services.base import WacomServiceAPIClient, WacomServiceException
from knowledge.services.graph import AUTHORIZATION_HEADER_FLAG

# ------------------------------------------------- Constants ----------------------------------------------------------
BASE_URI_TAG: str = "baseUri"
COMMENTS_TAG: str = "comments"
USER_AGENT_TAG: str = "User-Agent"
DOMAIN_TAG: str = "domain"
ICON_TAG: str = "icon"
INVERSE_OF_TAG: str = "inverseOf"
KIND_TAG: str = "kind"
LABELS_TAG: str = "labels"
LANGUAGE_CODE: str = 'languageCode'
NAME_TAG: str = "name"
RANGE_TAG: str = "range"
SUB_CLASS_OF_TAG: str = "subClassOf"
SUB_PROPERTY_OF_TAG: str = "subPropertyOf"
TEXT_TAG: str = 'value'


class OntologyService(WacomServiceAPIClient):
    """
    Ontology API Client
    -------------------
    Client to access the ontology service. Offers the following functionality:
    - Listing class names and property names
    - Create new ontology types
    - Update ontology types

    Parameters
    ----------
    service_url: str
        URL of the service
    service_endpoint: str
        Base endpoint
    """
    CONTEXT_ENDPOINT: str = 'context'
    CONCEPTS_ENDPOINT: str = 'context/{}/concepts'
    CONCEPT_ENDPOINT: str = 'context/{}/concepts/{}'
    PROPERTIES_ENDPOINT: str = "context/{}/properties"
    COMMIT_ENDPOINT: str = "context/{}/commit"
    RDF_ENDPOINT: str = "context/{}/versions/rdf"
    PROPERTY_ENDPOINT: str = "context/{}/properties/{}"

    def __init__(self, service_url: str, service_endpoint: str = 'ontology'):
        super().__init__(application_name="Ontology Service", service_url=service_url,
                         service_endpoint=service_endpoint)

    def contexts(self, auth_key: str) -> List[OntologyContext]:
        """List all concepts.

        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.

        Parameters
        ----------
        auth_key: str
            Auth key from user.

        Returns
        -------
        contexts: List[OntologyContext]
            List of ontology contexts
        """
        headers: Dict[str, str] = {
            USER_AGENT_TAG: USER_AGENT_STR,
            AUTHORIZATION_HEADER_FLAG: f'Bearer {auth_key}'
        }
        response: Response = requests.get(f'{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}',
                                          headers=headers, verify=self.verify_calls)
        if response.ok:
            response_list: List[OntologyContext] = []
            for c in response.json():
                response_list.append(OntologyContext.from_dict(c))
            return response_list
        raise WacomServiceException(f'Listing of context failed. '
                                    f'Response code:={response.status_code}, exception:= {response.text}')

    def concepts(self, auth_key: str, context: str) -> List[Tuple[OntologyClassReference, OntologyClassReference]]:
        """Retrieve all concept classes.

        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.

        Parameters
        ----------
        auth_key: str
            Auth key from user.
        context: str
            Context of the ontology

        Returns
        -------
        concepts: List[Tuple[OntologyClassReference, OntologyClassReference]]
            List of ontology classes. Tuple<Classname, Superclass>
        """
        headers: Dict[str, str] = {
            USER_AGENT_TAG: USER_AGENT_STR,
            AUTHORIZATION_HEADER_FLAG: f'Bearer {auth_key}'
        }
        response: Response = requests.get(f'{self.service_base_url}{OntologyService.CONCEPTS_ENDPOINT.format(context)}',
                                          headers=headers, verify=self.verify_calls)
        if response.ok:
            response_list: List[Tuple[OntologyClassReference, OntologyClassReference]] = []
            result = response.json()
            for struct in result:
                response_list.append((OntologyClassReference.parse(struct[NAME_TAG]),
                                      None if struct[SUB_CLASS_OF_TAG] is None else
                                      OntologyClassReference.parse(struct[SUB_CLASS_OF_TAG])))
            return response_list
        raise WacomServiceException(f'Response code:={response.status_code}, exception:= {response.text}')

    def properties(self, auth_key: str, context_name: str) -> List[Tuple[OntologyPropertyReference,
                                                                         OntologyPropertyReference]]:
        """List all properties.

        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.

        Parameters
        ----------
        auth_key: str
            Auth key from user.
        context_name: str
            Name of the context

        Returns
        -------
        contexts: List[Tuple[OntologyPropertyReference, OntologyPropertyReference]]
            List of ontology contexts
        """
        headers: Dict[str, str] = {
            USER_AGENT_TAG: USER_AGENT_STR,
            AUTHORIZATION_HEADER_FLAG: f'Bearer {auth_key}'
        }
        context_url: str = urllib.parse.quote_plus(context_name)

        response: Response = requests.get(f'{self.service_base_url}'
                                          f'{OntologyService.PROPERTIES_ENDPOINT.format(context_url)}',
                                          headers=headers, verify=self.verify_calls)
        # Return empty list if the NOT_FOUND is reported
        if response.status_code == HTTPStatus.NOT_FOUND:
            return []
        if response.ok:
            response_list: List[Tuple[OntologyPropertyReference, OntologyPropertyReference]] = []
            for c in response.json():
                response_list.append((OntologyPropertyReference.parse(c[NAME_TAG]),
                                      None if c[SUB_PROPERTY_OF_TAG] is None else
                                      OntologyPropertyReference.parse(c[SUB_PROPERTY_OF_TAG])))
            return response_list
        raise WacomServiceException(f'Response code:={response.status_code}, exception:= {response.text}')

    def concept(self, auth_key: str, context_name: str, concept_name: str) -> OntologyClass:
        """Retrieve a concept instance.

        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.

        Parameters
        ----------
        auth_key: str
            Auth key from user.
        context_name: str
            Name of the context
        concept_name: str
            IRI of the concept

        Returns
        -------
        instance: OntologyClass
            Instance of the concept
        """
        headers: Dict[str, str] = {
            USER_AGENT_TAG: USER_AGENT_STR,
            AUTHORIZATION_HEADER_FLAG: f'Bearer {auth_key}'
        }
        context_url: str = urllib.parse.quote_plus(context_name)
        concept_url: str = urllib.parse.quote_plus(concept_name)
        response: Response = requests.get(f'{self.service_base_url}'
                                          f'{OntologyService.CONCEPT_ENDPOINT.format(context_url, concept_url)}',
                                          headers=headers, verify=self.verify_calls)
        if response.ok:
            result: Dict[str, Any] = response.json()
            return OntologyClass.from_dict(result)
        raise WacomServiceException(f'Response code:={response.status_code}, exception:= {response.text}')

    def property(self, auth_key: str, context_name: str, property_name: str) -> OntologyProperty:
        """Retrieve a property instance.

        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.

        Parameters
        ----------
        auth_key: str
            Auth key from user.
        context_name: str
            Name of the context
        property_name: str
            IRI of the property

        Returns
        -------
        instance: OntologyProperty
            Instance of the property
        """
        headers: Dict[str, str] = {
            USER_AGENT_TAG: USER_AGENT_STR,
            AUTHORIZATION_HEADER_FLAG: f'Bearer {auth_key}'
        }
        context_url: str = urllib.parse.quote_plus(context_name)
        concept_url: str = urllib.parse.quote_plus(property_name)
        param: str = OntologyService.PROPERTY_ENDPOINT.format(context_url, concept_url)
        response: Response = requests.get(f'{self.service_base_url}{param}', headers=headers, verify=self.verify_calls)
        if response.ok:
            return OntologyProperty.from_dict(response.json())
        raise WacomServiceException(f'Response code:={response.status_code}, exception:= {response.text}')

    def create_concept(self, auth_key: str, context: str, reference: OntologyClassReference,
                       subclass_of: OntologyClassReference = THING_CLASS,
                       icon: Optional[str] = None, labels: Optional[List[Label]] = None,
                       comments: Optional[List[Comment]] = None) -> Dict[str, str]:
        """Create concept class.

        **Remark:**
        Only works for users with role 'TenantAdmin'.

        Parameters
        ----------
        auth_key: str
            Auth key from user.
        context: str
            Context of ontology
        reference: OntologyClassReference
            Name of the concept
        subclass_of: OntologyClassReference (default:=wacom:core#Thing)
            Super class of the concept
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[List[Label]] (default:= None)
            Labels for the class
        comments: Optional[List[Comment]] (default:= None)
            Comments for the class
        Returns
        -------
        result: Dict[str, str]
            Result from the service

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.
        """
        headers: Dict[str, str] = {
            USER_AGENT_TAG: USER_AGENT_STR,
            AUTHORIZATION_HEADER_FLAG: f'Bearer {auth_key}'
        }
        payload: Dict[str, Any] = {
            SUB_CLASS_OF_TAG: subclass_of.iri,
            NAME_TAG: reference.iri,
            LABELS_TAG: [],
            COMMENTS_TAG: [],
            ICON_TAG: icon
        }
        context_url: str = urllib.parse.quote_plus(context)
        for label in labels if labels is not None else []:
            payload[LABELS_TAG].append({TEXT_TAG: label.content, LANGUAGE_CODE: label.language_code})
        for comment in comments if comments is not None else []:
            payload[COMMENTS_TAG].append({TEXT_TAG: comment.content, LANGUAGE_CODE: comment.language_code})
        url: str = f'{self.service_base_url}{OntologyService.CONCEPTS_ENDPOINT.format(context_url)}'
        response: Response = requests.post(url, headers=headers, json=payload, verify=self.verify_calls)
        if response.ok:
            result_dict: Dict[str, str] = response.json()
            return result_dict
        raise WacomServiceException(f'Creation of concept failed. '
                                    f'Response code:={response.status_code}, exception:= {response.text}')

    def update_concept(self, auth_key: str, context: str, name: str, subclass_of: Optional[str],
                       icon: Optional[str] = None, labels: Optional[List[Label]] = None,
                       comments: Optional[List[Comment]] = None) -> Dict[str, str]:
        """Update concept class.

        **Remark:**
        Only works for users with role 'TenantAdmin'.

        Parameters
        ----------
        auth_key: str
            Auth key from user.
        context: str
            Context of ontology
        name: str
            Name of the concept
        subclass_of: Optional[str]
            Super class of the concept
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[List[Label]] (default:= None)
            Labels for the class
        comments: Optional[List[Comment]] (default:= None)
            Comments for the class

        Returns
        -------
        response: Dict[str, str]
            Response from service

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.
        """
        headers: Dict[str, str] = {
            USER_AGENT_TAG: USER_AGENT_STR,
            AUTHORIZATION_HEADER_FLAG: f'Bearer {auth_key}'
        }
        payload: Dict[str, Any] = {
            SUB_CLASS_OF_TAG: subclass_of,
            NAME_TAG: name,
            LABELS_TAG: [],
            COMMENTS_TAG: [],
            ICON_TAG: icon
        }
        context_url: str = urllib.parse.quote_plus(context)
        for label in labels if labels is not None else []:
            payload[LABELS_TAG].append({TEXT_TAG: label.content, LANGUAGE_CODE: label.language_code})
        for comment in comments if comments is not None else []:
            payload[COMMENTS_TAG].append({TEXT_TAG: comment.content, LANGUAGE_CODE: comment.language_code})
        url: str = f'{self.service_url}{self.service_endpoint}' \
                   f'{OntologyService.CONCEPTS_ENDPOINT.format(context_url)}'
        response: Response = requests.put(url, headers=headers, json=payload, verify=self.verify_calls)
        if response.ok:
            return response.json()
        raise WacomServiceException(f'Update of concept failed. '
                                    f'Response code:={response.status_code}, exception:= {response.text}')

    def create_object_property(self, auth_key: str, context: str,
                               reference: OntologyPropertyReference,
                               domain_cls: OntologyClassReference, range_cls: OntologyClassReference,
                               inverse_of: Optional[OntologyPropertyReference] = None,
                               subproperty_of: Optional[OntologyPropertyReference] = None,
                               icon: Optional[str] = None,
                               labels: Optional[List[LocalizedContent]] = None,
                               comments: Optional[List[LocalizedContent]] = None) -> Dict[str, str]:
        """Create property.

        **Remark:**
        Only works for users with role 'TenantAdmin'.

        Parameters
        ----------
        auth_key: str
            Auth key from user.
        context: str
            Context of ontology
        reference: OntologyPropertyReference
            Name of the concept
        domain_cls: OntologyClassReference
            IRI of the domain
        range_cls: OntologyClassReference
            IRI of the range
        inverse_of: Optional[OntologyPropertyReference] (default:= None)
            Inverse property
        subproperty_of: Optional[OntologyPropertyReference] = None,
            Super property of the concept
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[List[Label]] (default:= None)
            Labels for the class
        comments: Optional[List[Comment]] (default:= None)
            Comments for the class

        Returns
        -------
        result: Dict[str, str]
            Result from the service

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.
        """
        headers: Dict[str, str] = {
            USER_AGENT_TAG: USER_AGENT_STR,
            AUTHORIZATION_HEADER_FLAG: f'Bearer {auth_key}'
        }
        payload: Dict[str, Any] = {
            KIND_TAG: PropertyType.OBJECT_PROPERTY.value,
            DOMAIN_TAG: domain_cls.iri,
            RANGE_TAG: range_cls.iri,
            SUB_PROPERTY_OF_TAG: subproperty_of.iri if subproperty_of is not None else None,
            INVERSE_OF_TAG: inverse_of.iri if inverse_of is not None else None,
            NAME_TAG: reference.iri,
            LABELS_TAG: [],
            COMMENTS_TAG: [],
            ICON_TAG: icon
        }
        context_url: str = urllib.parse.quote_plus(context)
        for label in labels if labels is not None else []:
            payload[LABELS_TAG].append({TEXT_TAG: label.content, LANGUAGE_CODE: label.language_code})
        for comment in comments if comments is not None else []:
            payload[COMMENTS_TAG].append({TEXT_TAG: comment.content, LANGUAGE_CODE: comment.language_code})
        url: str = f'{self.service_base_url}{OntologyService.PROPERTIES_ENDPOINT.format(context_url)}'
        response: Response = requests.post(url, headers=headers, json=payload, verify=self.verify_calls)
        if response.ok:
            return response.json()
        raise WacomServiceException(f'Creation of object property failed. '
                                    f'Response code:={response.status_code}, exception:= {response.text}')

    def create_data_property(self, auth_key: str, context: str,
                             reference: OntologyPropertyReference,
                             domain_cls: OntologyClassReference, range_cls: DataPropertyType,
                             subproperty_of: Optional[OntologyPropertyReference] = None,
                             icon: Optional[str] = None,
                             labels: Optional[List[LocalizedContent]] = None,
                             comments: Optional[List[LocalizedContent]] = None) -> Dict[str, str]:
        """Create data property.

        **Remark:**
        Only works for users with role 'TenantAdmin'.

        Parameters
        ----------
        auth_key: str
            Auth key from user.
        context: str
            Context of ontology
        reference: OntologyPropertyReference
            Name of the concept
        domain_cls: OntologyClassReference
            IRI of the domain
        range_cls: DataPropertyType
            Data property type
        subproperty_of: Optional[OntologyPropertyReference] = None,
            Super property of the concept
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[List[Label]] (default:= None)
            Labels for the class
        comments: Optional[List[Comment]] (default:= None)
            Comments for the class

        Returns
        -------
        result: Dict[str, str]
            Result from the service

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.
        """
        headers: Dict[str, str] = {
            USER_AGENT_TAG: USER_AGENT_STR,
            AUTHORIZATION_HEADER_FLAG: f'Bearer {auth_key}'
        }
        payload: Dict[str, Any] = {
            KIND_TAG: PropertyType.DATA_PROPERTY.value,
            DOMAIN_TAG: domain_cls.iri,
            RANGE_TAG: range_cls.value,
            SUB_PROPERTY_OF_TAG: subproperty_of.iri if subproperty_of is not None else None,
            NAME_TAG: reference.iri,
            LABELS_TAG: [],
            COMMENTS_TAG: [],
            ICON_TAG: icon
        }
        context_url: str = urllib.parse.quote_plus(context)
        for label in labels if labels is not None else []:
            payload[LABELS_TAG].append({TEXT_TAG: label.content, LANGUAGE_CODE: label.language_code})
        for comment in comments if comments is not None else []:
            payload[COMMENTS_TAG].append({TEXT_TAG: comment.content, LANGUAGE_CODE: comment.language_code})
        url: str = f'{self.service_base_url}{OntologyService.PROPERTIES_ENDPOINT.format(context_url)}'
        response: Response = requests.post(url, headers=headers, json=payload, verify=self.verify_calls)
        if response.ok:
            return response.json()
        raise WacomServiceException(f'Creation of data property failed. '
                                    f'Response code:={response.status_code}, exception:= {response.text}')

    def create_context(self, auth_key: str, name: str, base_uri: Optional[str] = None, icon: Optional[str] = None,
                       labels: List[Label] = None, comments: List[Comment] = None) -> Dict[str, str]:
        """Create context.

        **Remark:**
        Only works for users with role 'TenantAdmin'.

        Parameters
        ----------
        auth_key: str
            Auth key from user.
        base_uri: str
            Base URI
        name: str
            Name of the context
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[List[Label]] (default:= None)
            Labels for the context
        comments: Optional[List[Comment]] (default:= None)
            Comments for the context

        Returns
        -------
        result: Dict[str, str]
            Result from the service

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.
        """
        headers: Dict[str, str] = {
            USER_AGENT_TAG: USER_AGENT_STR,
            AUTHORIZATION_HEADER_FLAG: f'Bearer {auth_key}'
        }
        payload: Dict[str, Any] = {
            BASE_URI_TAG: base_uri if base_uri is not None else f'wacom:{name}',
            NAME_TAG: name,
            LABELS_TAG: [],
            COMMENTS_TAG: [],
            ICON_TAG: icon
        }
        for label in labels if labels is not None else []:
            payload[LABELS_TAG].append({TEXT_TAG: label.content, LANGUAGE_CODE: label.language_code})
        for comment in comments if comments is not None else []:
            payload[COMMENTS_TAG].append({TEXT_TAG: comment.content, LANGUAGE_CODE: comment.language_code})
        url: str = f'{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}'
        response: Response = requests.post(url, headers=headers, json=payload, verify=self.verify_calls)
        if response.ok:
            return response.json()
        raise WacomServiceException(f'Creation of concept failed. '
                                    f'Response code:={response.status_code}, exception:= {response.text}')

    def commit(self, auth_key: str, context_name: str):
        """
        Commit the ontology.

        Parameters
        ----------
        auth_key: str
            User token (must have TenantAdmin) role
        context_name: str
            Name of the context.
        """
        headers: Dict[str, str] = {
            USER_AGENT_TAG: USER_AGENT_STR,
            AUTHORIZATION_HEADER_FLAG: f'Bearer {auth_key}'
        }
        context_url: str = urllib.parse.quote_plus(context_name)
        url: str = f'{self.service_base_url}{OntologyService.COMMIT_ENDPOINT.format(context_url)}'
        response: Response = requests.put(url, headers=headers, verify=self.verify_calls)
        if not response.ok:
            raise WacomServiceException(f'Commit of ontology failed. '
                                        f'Response code:={response.status_code}, exception:= {response.text}')

    def rdf_export(self, auth_key: str, context_name: str) -> str:
        """
        Export RDF.

        Parameters
        ----------
        auth_key: str
            User token (must have TenantAdmin) role
        context_name: str
            Name of the context.

        Returns
        -------
        rdf: str
            Ontology as RDFS / OWL  ontology
        """
        headers: Dict[str, str] = {
            USER_AGENT_TAG: USER_AGENT_STR,
            AUTHORIZATION_HEADER_FLAG: f'Bearer {auth_key}'
        }
        context_url: str = urllib.parse.quote_plus(context_name)
        url: str = f'{self.service_base_url}{OntologyService.RDF_ENDPOINT.format(context_url)}'
        response: Response = requests.get(url, headers=headers, verify=self.verify_calls)
        if response.ok:
            return response.text
        raise WacomServiceException(f'RDF export failed. '
                                    f'Response code:={response.status_code}, exception:= {response.text}')

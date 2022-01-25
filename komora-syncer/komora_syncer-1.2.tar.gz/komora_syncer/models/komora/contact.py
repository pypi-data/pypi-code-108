from typing import List
from datetime import datetime


class ContactType:
    contact_id: int
    contract_id: int
    contact_type_id: int
    contact_type_name: str
    id: int

    def __init__(self, contact_id: int, contract_id: int, contact_type_id: int, contact_type_name: str, id: int) -> None:
        self.contact_id = contact_id
        self.contract_id = contract_id
        self.contact_type_id = contact_type_id
        self.contact_type_name = contact_type_name
        self.id = id


class Email:
    email_address: str

    def __init__(self, email_address: str) -> None:
        self.email_address = email_address


class Organization:
    organization_name: str
    organization_id: int
    isActive: bool

    def __init__(self, organization_name: str, organization_id: int, isActive: bool) -> None:
        self.organization_name = organization_name
        self.organization_id = organization_id
        self.isActive = isActive


class Tag:
    contact_id: int
    tag_id: int
    tag_name: str
    note: str
    id: int

    def __init__(self, contact_id: int, tag_id: int, tag_name: str, note: str, id: int) -> None:
        self.contact_id = contact_id
        self.tag_id = tag_id
        self.tag_name = tag_name
        self.note = note
        self.id = id


class Contact:
    firstName: str
    surname: str
    title: str
    suffix: str
    contactTypes: List[ContactType]
    phoneNumber: str
    isActive: bool
    address: str
    phoneNumber2: str
    street: str
    city: str
    postCode: str
    validFrom: datetime
    validTo: datetime
    abraContactId: str
    organizations: List[Organization]
    updatedAt: datetime
    updatedBy: str
    fullName: str
    isEditable: bool
    lastContactedNote: str
    lastContactedBy: str
    lastContactedAt: datetime
    emails: List[Email]
    tags: List[Tag]
    id: int

    def __init__(self, firstName: str, surname: str, title: str, suffix: str, contactTypes: List[ContactType], phoneNumber: str, isActive: bool, address: str, phoneNumber2: str, street: str, city: str, postCode: str, validFrom: datetime, validTo: datetime, abraContactId: str, organizations: List[Organization], updatedAt: datetime, updatedBy: str, fullName: str, isEditable: bool, lastContactedNote: str, lastContactedBy: str, lastContactedAt: datetime, emails: List[Email], tags: List[Tag], id: int) -> None:
        self.firstName = firstName
        self.surname = surname
        self.title = title
        self.suffix = suffix
        self.contactTypes = contactTypes
        self.phoneNumber = phoneNumber
        self.isActive = isActive
        self.address = address
        self.phoneNumber2 = phoneNumber2
        self.street = street
        self.city = city
        self.postCode = postCode
        self.validFrom = validFrom
        self.validTo = validTo
        self.abraContactId = abraContactId
        self.organizations = organizations
        self.updatedAt = updatedAt
        self.updatedBy = updatedBy
        self.fullName = fullName
        self.isEditable = isEditable
        self.lastContactedNote = lastContactedNote
        self.lastContactedBy = lastContactedBy
        self.lastContactedAt = lastContactedAt
        self.emails = emails
        self.tags = tags
        self.id = id


"""
 "data": [
    {
      "firstName": "string",
      "surname": "string",
      "title": "string",
      "suffix": "string",
      "contactTypes": [
        {
          "contactId": 0,
          "contractId": 0,
          "contactTypeId": 0,
          "contactTypeName": "string",
          "id": 0
        }
      ],
      "phoneNumber": "string",
      "isActive": true,
      "address": "string",
      "phoneNumber2": "string",
      "street": "string",
      "city": "string",
      "postCode": "string",
      "validFrom": "2021-11-08T08:49:44.972Z",
      "validTo": "2021-11-08T08:49:44.972Z",
      "abraContactId": "string",
      "organizations": [
        {
          "organizationName": "string",
          "organizationId": 0,
          "isActive": true
        }
      ],
      "updatedAt": "2021-11-08T08:49:44.972Z",
      "updatedBy": "string",
      "fullName": "string",
      "isEditable": true,
      "lastContactedNote": "string",
      "lastContactedBy": "string",
      "lastContactedAt": "2021-11-08T08:49:44.972Z",
      "emails": [
        {
          "emailAddress": "string"
        }
      ],
      "tags": [
        {
          "contactId": 0,
          "tagId": 0,
          "tagName": "string",
          "note": "string",
          "id": 0
        }
      ],
      "id": 0
    }
  ]
"""

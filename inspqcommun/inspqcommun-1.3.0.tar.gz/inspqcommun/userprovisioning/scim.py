#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module scim
import uuid 
import json
import requests
from urllib3.exceptions import HTTPError

class SCIMObject(object):
    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def to_json(self):
        if hasattr(self, 'APPARTENANCEORG_SCHEMA') and hasattr(self, 'APPARTENANCEORG_ATTRS'):
            json_dict = json.loads(json.dumps(self, default=lambda o: o.__dict__))
            app_org_ready_json = {}            
            for key in json_dict:
                if key == self.APPARTENANCEORG_ATTRS[0]:
                    app_org_ready_json[self.APPARTENANCEORG_SCHEMA] = {key: json_dict[key].copy()}
                else:
                    app_org_ready_json[key] = json_dict[key]
            return json.dumps(app_org_ready_json)

        return json.dumps(self, default=lambda o: o.__dict__)

    @classmethod
    def from_json(cls, json_str):
        json_dict = json.loads(json_str)
        return cls(**json_dict)

class User(SCIMObject):
    URI = "/Users"

    CORE_USER_SCHEMA = "urn:ietf:params:scim:schemas:core:2.0:User"
    ENTERPRISE_USER_SCHEMA = "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"
    IDCS_USER_SCHEMA = "urn:ietf:params:scim:schemas:oracle:idcs:extension:user:User"
    PASSWORDSTATE_USER_SCHEMA = "urn:ietf:params:scim:schemas:oracle:idcs:extension:passwordState:User"
    USERSTATE_USER_SCHEMA = "urn:ietf:params:scim:schemas:oracle:idcs:extension:userState:User"
    APPARTENANCEORG_SCHEMA = "urn:sadupanorama:scim:api:messages:2.0:AppartenancesOrganisationnelles"
    
    SCIM_ATTRS = ['schemas', 'id', 'externalId', 'meta', 'idaasCreatedBy',
    'idaasLastModifiedBy']
    CORE_ATTRS = ['userName', 'name', 'displayName', 'nickName', 'profileUrl',
    'title', 'userType', 'locale', 'preferredLanguage', 'timezone', 'active',
    'password', 'emails', 'phoneNumbers', 'ims', 'photos', 'addresses',
    'groups', 'entitlements', 'roles', 'x509certificates']
    ENTERPRISE_ATTRS = ['employeeNumber', 'costCenter', 'organization',
    'division', 'department', 'manager']
    IDCS_ATTRS = ['isFederatedUser', 'status', 'internalName', 'provider',
    'creationMechanism', 'appRoles', 'doNotShowGettingStarted']
    PASSWORDSTATE_ATTRS = ['lastSuccessfulSetDate', 'cantChange', 'cantExpire',
            'mustChange', 'expired', 'passwordHistory']
    USERSTATE_ATTRS = ['lastSuccessfulLoginDate', 'lastFailedLoginDate',
    'loginAttempts', 'locked']
    
    APPARTENANCEORG_ATTRS = ["appartenancesOrganisationnelles"]

    def __init__(self, *initial_data, **kwargs):
        self.schemas = [User.CORE_USER_SCHEMA]

        super(SCIMObject, self).__init__()

        for dictionary in initial_data:
            for key in dictionary:
                if key == User.APPARTENANCEORG_SCHEMA:
                    for app_org_key in dictionary[key]:
                        if app_org_key in User.APPARTENANCEORG_ATTRS:
                            setattr(self, app_org_key, dictionary[key][app_org_key])
                else:
                    setattr(self, key, dictionary[key])
        for key in kwargs:
            if key == User.APPARTENANCEORG_SCHEMA:
                for app_org_key in kwargs[key]:
                    if app_org_key in User.APPARTENANCEORG_ATTRS:
                        setattr(self, app_org_key, kwargs[key][app_org_key])
            else:
                setattr(self, key, kwargs[key])

    def __setattr__(self, name, value):
        if name in User.ENTERPRISE_ATTRS and User.ENTERPRISE_ATTRS not in self.schemas:
            self.schemas += [User.ENTERPRISE_USER_SCHEMA]
        elif name in User.IDCS_ATTRS and User.IDCS_ATTRS not in self.schemas:
            self.schemas += [User.IDCS_USER_SCHEMA]
        elif name in User.PASSWORDSTATE_ATTRS and User.PASSWORDSTATE_ATTRS not in self.schemas:
            self.schemas += [User.PASSWORDSTATE_USER_SCHEMA]
        elif name in User.USERSTATE_ATTRS and User.USERSTATE_ATTRS not in self.schemas:
            self.schemas += [User.USERSTATE_USER_SCHEMA]
        elif name in User.APPARTENANCEORG_ATTRS and User.APPARTENANCEORG_SCHEMA not in self.schemas:
            self.schemas += [User.APPARTENANCEORG_SCHEMA]
            
        self.__dict__[name] = value
    
    def update(self, user):
        updates = json.loads(user.to_json())
        actual = json.loads(self.to_json())
        updated = dict()
        updated.update(actual)
        updated.update(updates)
        return self.from_json(json.dumps(updated))

class Group(SCIMObject):
    URI = "/Groups"

    CORE_GROUP_SCHEMA = "urn:ietf:params:scim:schemas:core:2.0:Group"
    IDCS_GROUP_SCHEMA = "urn:ietf:params:scim:schemas:oracle:idcs:extension:group:Group"

    SCIM_ATTRS = ['schemas', 'id', 'externalId', 'meta', 'idaasCreatedBy',
    'idaasLastModifiedBy']
    CORE_ATTRS = ['displayName', 'members']
    IDCS_ATTRS = ['internalName', 'description', 'creationMechanism', 'appRoles']

    def __init__(self, *initial_data, **kwargs):
        self.schemas = [Group.CORE_GROUP_SCHEMA]

        super(SCIMObject, self).__init__()

        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __setattr__(self, name, value):
        if name in Group.IDCS_ATTRS:
            self.schemas += [Group.IDCS_GROUP_SCHEMA]

        self.__dict__[name] = value        

class SCIMClient(object):
    base_url = ""
    access_token = ""
    headers = ""
    validate_certs = True
    
    def __init__(self, base_url="", access_token="", additionnal_headers={}):
        self.base_url = base_url
        self.access_token = access_token
        self.headers = {
            'Content-Type': 'application/scim+json'
        }
        if access_token is not None and len(access_token) > 0:
            self.headers["Authorization"] = "bearer " + access_token
        if additionnal_headers is not None and len(additionnal_headers.keys()) > 0:
            for header in additionnal_headers.keys():
                if header.upper() != 'CONTENT-TYPE':
                    self.headers[header] = additionnal_headers[header]
        
    def searchUserByUserName(self, userName):
        user_search_url = self.base_url + User.URI + '/.search'
        data = '{"filter":"userName eq \\\"' + userName + '\\\""}"'
        try:
            response = requests.post(url=user_search_url, headers=self.headers, data=data)
            users = response.json()
            if response.status_code != 200:
                raise SCIMException(
                'Could not search for user %s at %s: %s' % (userName, user_search_url, str(response.status_code)))
            if "Resources" in users and len(users["Resources"]) > 0:
                return User.from_json(json.dumps(users["Resources"][0]))
            return None
        except Exception as e:
            raise SCIMException(
                'Could not search for user %s at %s: %s' % (userName, user_search_url, str(e)))
        
    def getMe(self):
        me_url = self.base_url + '/Me'
        try:
            response = requests.get(url=me_url, headers=self.headers)
            if response.status_code == 200: 
                return User.from_json(response.content)
            raise SCIMException('Could not get Me at %s: %s' % (me_url, response.json()))
        except Exception as e:
            raise SCIMException('Could not get Me at %s: %s' % (me_url, str(e)))

    def getUserById(self, id):
        user_url = self.base_url + User.URI + '/' + id
        try:
            response = requests.get(url=user_url, headers=self.headers)
            if response.status_code == 200: 
                return User.from_json(response.content)
            raise SCIMException('Could not get user id %s at %s: %s' % (id, user_url, response.json()))
        except Exception as e:
            raise SCIMException('Could not get user id %s at %s: %s' % (id, user_url, str(e)))

    def createUser(self, user):
        user_url = self.base_url + User.URI
        try:
            if "externalId" not in json.loads(user.to_json()):
                user.externalId = str(uuid.uuid1())
            data = user.to_json()
            response = requests.post(url=user_url, headers=self.headers, data=data)
            if response.status_code == 201 or response.status_code == 200: 
                return User.from_json(response.content)
            raise SCIMException('Could not create user %s at %s: %s' % (user.userName, user_url, response.json()))        
        except Exception as e:
            raise SCIMException('Could not create user %s at %s: %s' % (user.userName, user_url, str(e)))
    
    
    def deleteUser(self, user):
        user_url = self.base_url + User.URI + '/' + user.id
        try:
            response = requests.delete(url=user_url, headers=self.headers)
            return response
        except Exception as e:
            raise SCIMException('Could not delete user %s at %s: %s' % (user.userName, user_url, str(e)))
        
    def updateUser(self, user):
        user_url = self.base_url + User.URI + '/' + user.id
        try:
            data = user.to_json()
            response = requests.put(url=user_url, headers=self.headers, data=data)
            if response.status_code == 200: 
                return User.from_json(response.content)
            raise SCIMException('Could not create user %s at %s: %s' % (user.userName, user_url, response.json()))
        except Exception as e:
            raise SCIMException('Could not update user %s at %s: %s' % (user.userName, user_url, str(e)))
            
class SCIMException(Exception):
    """ Exception SCIM """

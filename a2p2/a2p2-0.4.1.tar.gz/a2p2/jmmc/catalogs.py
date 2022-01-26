#!/usr/bin/env python

__all__ = []

import logging

from .utils import JmmcAPI
from . import PRODLABEL

logger = logging.getLogger(__name__)

class Catalog():
    """ Get remote access to read and update catalogs exposed through JMMC's API.
    Credential can be explicitly given but .netrc file will be automagically used on 401.
    """

    def __init__(self, catalogName, username=None, password=None, prod=False, apiUrl=None):
        self.catalogName = catalogName
        self.prod = prod

        # Manage prod & preprod or user provided access points
        if apiUrl:
            self.apiUrl = apiUrl  # trust given url as catalogAPI if value is provided
        elif self.prod:
            self.apiUrl = ""  # no api in production yet
            raise Warning("sorry, no api for production yet")
        else:
            self.apiUrl = "https://oidb-beta.jmmc.fr/restxq/catalogs"

        self.api = JmmcAPI(self.apiUrl, username, password)

        logger.info("Create catalog wrapper to access '%s' (%s API at %s)" %
                    (catalogName, PRODLABEL[self.prod], self.api.rootURL))

    def list(self):
        """ Get list of exposed catalogs on API associated to this catalog. """
        return self.api._get("")

    def metadata(self):
        """ Get catalog metadata """
        return self.api._get("/meta/%s" % self.catalogName)

    def pis(self):
        """ Get PIs from catalog and check for associated JMMC login """
        return self.api._get("/accounts/%s" % self.catalogName)

    def getRow(self, id):
        """ Get a single catalog record for the given id.
             usage: cat.getRow(42)
        """
        return self.api._get("/%s/%s" % (self.catalogName, id))

    def updateRow(self, id, values):
        """ Update record identified by given id and associated values.
            usage: cat.updateRows(42, {"col_a":"a", "col_b":"b" })
        """
        return self.api._put("/%s/%s" % (self.catalogName, id), values)

    def updateRows(self, values):
        """ Update multiple rows.
        Values must contain a list of dictionnary and each entry must contains id key among other columns.
            usage: updateRows([ { "id":42, "col_a":"a" }, { "id":24, "col_b":"b" } ])
        """

        # We may check befere sending payload that we always provide an id for every record
        return self.api._put("/%s" % (self.catalogName), values)

    def addRows(self, values):
        """ add multiple rows.
            Values is an array of row to add. id column values will be ignored.
            usage: addCatalogRows([ { "id":42, "col_a":"a" }, { "id":24, "col_b":"b" } ])
        """
        return self.api._post("/%s" % (self.catalogName), json=values)

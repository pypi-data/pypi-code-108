"""TODO doc"""

import sys 
import logging
import re

import utm

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.namespace import NamespaceManager
from rdflib.store import Store, VALID_STORE

from ejerico.sdk.utils import srs_to_uri

class SpatialImpl(object):

    def __init__(self):
        object.__init__(self)
        self.name = None
        self.address = None
        self.geometry = None
        self.location = None
        self.latitude = None
        self.longitude = None
        self.max_latitude = None
        self.max_longitude = None
        self.min_latitude = None
        self.min_longitude = None
        self.reference_system = None
        self.unit_latitude = None
        self.unit_longitude = None

    def prepare(self):
        logging.debug("[Spatial:prepare] entering method")

        spatialID = None

        UTM_TO_WSG84 = {
            "northernmost_northing": "min_latitude",
            "southernmost_northing": "max_latitude",
            "easternmost_easting": "min_longitude",
            "westernmost_easting": "max_longitude",
        }
        #for key,value: utm.to_latlon(340000, 5710000, 1, 'Z')

        for geo_stuff in ["min_latitude", "max_latitude", "min_longitude", "max_longitude", "latitude", "longitude"]:
            if hasattr(self, geo_stuff) and getattr(self, geo_stuff) is not None: setattr(self, geo_stuff, float(getattr(self, geo_stuff)))

        self.reference_system = "CRS:84" if self.reference_system is None else self.reference_system
        self.reference_system =  "EPSG:4326" if "WSG:84" == self.reference_system is None else self.reference_system
        
        if self.geometry is None:
            by_geopoints = hasattr(self, "min_latitude") and self.min_latitude 
            by_geopoints = by_geopoints and hasattr(self, "max_latitude") and self.max_latitude 
            by_geopoints = by_geopoints and hasattr(self, "min_longitude") and self.min_longitude 
            by_geopoints = by_geopoints and hasattr(self, "max_longitude") and self.max_longitude
            if by_geopoints:
                if self.min_latitude == self.max_latitude and  self.min_longitude == self.max_longitude:
                    self.latitude = self.min_latitude; self.longitude = self.min_longitude
                    self.min_latitude = self.min_longitude = self.max_latitude = self.max_longitude = None
                    self.geometry = "{crs}POINT(({lat:.4f} {lng:.4f}))".format(crs=srs_to_uri(self.reference_system), lat=self.latitude, lng=self.longitude)
                    spatialID = "{lat:.4f}_{lng:.4f}".format(lat=self.latitude, lng=self.longitude)
                else:
                    self.geometry = "{crs}POLYGON(({min_lat:.4f} {min_lng:.4f}, {min_lat:.4f} {max_lng:.4f}, {max_lat:.4f} {max_lng:.4f}, {max_lat:.4f} {min_lng:.4f}, {min_lat:.4f} {min_lng:.4f}))"
                    self.geometry = self.geometry.format(
                        crs=srs_to_uri(self.reference_system),
                        min_lat=self.min_latitude, max_lat=self.max_latitude, 
                        min_lng=self.min_longitude, max_lng=self.max_longitude,
                    )
                    spatialID = "{min_lat:.4f}_{min_lng:.4f}_{max_lat:.4f}_{max_lng:.4f}".format(min_lat=self.min_latitude, min_lng=self.min_longitude, max_lat=self.max_latitude, max_lng=self.max_longitude)
            else: 
                by_geopoints = hasattr(self, "latitude") and self.latitude 
                by_geopoints = by_geopoints and hasattr(self, "longitude") and self.longitude
                if by_geopoints:
                    self.geometry = "{crs}POINT(({lat:.4f} {lng:.4f}))".format(lat=self.latitude, lng=self.longitude)
                    spatialID = "{lat:.4f}_{lng:.4f}".format(lat=self.latitude, lng=self.longitude)
        else:
            match = re.match(self.__class__.prepare.re_pattern_csr, self.geometry)  
            self.reference_system = match.group("CSR") if match else self.reference_system
            match = re.match(self.__class__.prepare.re_pattern_urn_csr, self.geometry)
            self.reference_system = "{}:{}".format(match.group("CSR_REF"),match.group("CSR_NO")) if match else self.reference_system
            
            match = re.match(self.__class__.prepare.re_pattern_geometry_point, self.geometry)
            if match:
                self.latitude = float(match.group("lat"))
                self.longitude = float(match.group("lng"))
                logging.warning("[Spatial:prepare] Was a lat/lng swap here, WHY?")
                #FINDME: Why there is a explicit swap of lat/lon?
                #self.latitude,self.longitude = self.longitude,self.latitude
                spatialID = "{lat:.4f}_{lng:.4f}".format(lat=self.latitude, lng=self.longitude)
            else:
                match = re.match(self.__class__.prepare.re_pattern_list_point, self.geometry)
                if match:
                    logging.warning("[Spatial:prepare] TODO create spatialID from list of points")
        
        if self.longitude is None and self.latitude is None:
            has_boundingbox = self.min_latitude and self.max_latitude and self.min_longitude and self.max_longitude
            if has_boundingbox:
                self.longitude = self.min_longitude + (self.max_longitude-self.min_longitude)/2
                self.latitude = self.min_latitude + (self.max_latitude-self.min_latitude)/2

        if spatialID is not None:
            self.alias = [a for a in self.alias if not str(a).startswith(self.entity_domain)]
            self.id = self.__class__.buildURI("{}:{}".format(self.source if self.source is not None else "ejerico", spatialID))
            self.alias.append(self.__class__.buildSourceURI(self.source if self.source is not None else "ejerico", spatialID))
            self.first_born = True
    prepare.re_pattern_geometry_point = re.compile(r"[\w\W]*POINT\((?P<lat>[-\d.]+)\W+(?P<lng>[-\d.]+)\)")
    prepare.re_pattern_list_point = re.compile(r"((?P<lat>[\d.]+)[\W]+(?P<lng>[\d.]+))+")
    prepare.re_pattern_csr = re.compile(r"<[\w\W]+/(?P<CSR>[\w]+)>[\w\W]*")
    prepare.re_pattern_urn_csr = re.compile(r"(?P<CSR_REF>[\w]+):(?P<CSR_NO>[\d]+)$")


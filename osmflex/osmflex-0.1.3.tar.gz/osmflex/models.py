import logging
from typing import Generator

from django.contrib.gis.db import models
from django.db import connection

from osmflex.utils import truncate_sql, upsert_sql

logger = logging.getLogger(__name__)
# Create your models here.


class OsmTagged(models.Manager):
    def tagged(self):
        """
        Returns objects with their "tags" column appended
        """
        tags = Tags.objects.filter(osm_id=models.OuterRef("osm_id"))
        return self.get_queryset().annotate(tags=models.Subquery(tags.values("tags")))


class PgosmFlex(models.Model):
    id = models.BigIntegerField(primary_key=True)
    imported = models.DateTimeField()
    osm_date = models.DateField()
    default_date = models.BooleanField()
    region = models.TextField()
    pgosm_flex_version = models.TextField()
    srid = models.TextField()
    project_url = models.TextField()
    osm2pgsql_version = models.TextField()
    language = models.TextField()
    osm2pgsql_mode = models.TextField()

    class Meta:
        managed = False
        db_table = "osmflex_pgosm_flex"


class Osm(models.Model):

    osm_id = models.BigIntegerField(primary_key=True)
    osm_type = models.CharField(max_length=1024, null=True, blank=True)
    name = models.CharField(max_length=1024, null=True, blank=True)

    objects = OsmTagged()

    def __str__(self):
        return f"{self.name or getattr(self, 'osm_subtype', None) or self.osm_type}({self.osm_id})"

    class Meta:
        abstract = True

    @classmethod
    def update_all_from_flex(cls, truncate: bool = False) -> Generator[str, None, None]:
        """
        Generate import SQL for all tables. This executes an "upsert" from the parallel tables in
        the "osm" schema.
        """

        def get_all_subclasses(cls):
            subs = set()
            for sc in cls.__subclasses__():  # type: models.Model
                if not sc._meta.abstract:
                    subs.add(sc)
                subs.update(get_all_subclasses(sc))
            return subs

        for sc in get_all_subclasses(cls):
            print(sc)
            try:
                if truncate:
                    yield truncate_sql(sc)
                yield upsert_sql(sc)
            except Exception as E:
                print(E)


class OsmPoint(Osm):
    geom = models.PointField(srid=3857)

    class Meta:
        abstract = True


class OsmLine(Osm):
    geom = models.LineStringField(srid=3857)

    class Meta:
        abstract = True


class OsmPolygon(Osm):
    geom = models.MultiPolygonField(srid=3857)

    class Meta:
        abstract = True


class Amenity(models.Model):

    housenumber = models.CharField(max_length=512, null=True, blank=True)
    street = models.CharField(max_length=512, null=True, blank=True)
    city = models.CharField(max_length=512, null=True, blank=True)
    state = models.CharField(max_length=512, null=True, blank=True)
    postcode = models.CharField(max_length=512, null=True, blank=True)
    address = models.CharField(max_length=512, null=True, blank=True)

    class Meta:
        abstract = True


class WheelchairAccess(models.Model):
    wheelchair = models.CharField(max_length=512, null=True, blank=True)
    wheelchair_desc = models.CharField(max_length=512, null=True, blank=True)

    class Meta:
        abstract = True


class AmenityPoint(OsmPoint, Amenity, WheelchairAccess):
    pass


class AmenityLine(OsmLine, Amenity, WheelchairAccess):
    pass


class AmenityPolygon(OsmPolygon, Amenity, WheelchairAccess):
    pass


class Building(Amenity):
    """
    Building inherits from Amenity
    as it shares address + wheelchair stats
    """

    levels = models.IntegerField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    operator = models.CharField(max_length=1024, null=True, blank=True)
    osm_subtype = models.CharField(max_length=1024, null=True, blank=True)

    class Meta:
        abstract = True


class BuildingPoint(OsmPoint, Building, WheelchairAccess):
    pass


class BuildingPolygon(OsmPolygon, Building, WheelchairAccess):
    pass


class Indoor(models.Model):
    layer = models.TextField(null=True, blank=True)
    level = models.TextField(null=True, blank=True)
    room = models.TextField(null=True, blank=True)
    entrance = models.TextField(null=True, blank=True)
    door = models.TextField(null=True, blank=True)
    capacity = models.TextField(null=True, blank=True)
    highway = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class IndoorPoint(OsmPoint, Indoor):
    pass


class IndoorPolygon(OsmPolygon, Indoor):
    pass


class IndoorLine(OsmLine, Indoor):
    pass


class Infrastructure(models.Model):

    ele = models.IntegerField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    operator = models.CharField(max_length=1024, null=True, blank=True)
    material = models.CharField(max_length=1024, null=True, blank=True)
    osm_subtype = models.CharField(max_length=1024, null=True, blank=True)

    class Meta:
        abstract = True


class InfrastructurePoint(OsmPoint, Infrastructure):
    pass


class InfrastructureLine(OsmLine, Infrastructure):
    pass


class InfrastructurePolygon(OsmPolygon, Infrastructure):
    pass


class Landuse(models.Model):
    class Meta:
        abstract = True


class LandusePoint(OsmPoint, Landuse):
    pass


class LandusePolygon(OsmPolygon, Landuse):
    pass


class Leisure(models.Model):
    class Meta:
        abstract = True


class LeisurePoint(OsmPoint, Leisure):
    pass


class LeisurePolygon(OsmPolygon, Leisure):
    pass


class Natural(models.Model):

    ele = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True


class NaturalPoint(OsmPoint, Natural):
    pass


class NaturalLine(OsmLine, Natural):
    pass


class NaturalPolygon(OsmPolygon, Natural):
    pass


class Place(models.Model):

    boundary = models.CharField(max_length=1024, null=True, blank=True)
    admin_level = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True


class PlacePoint(OsmPoint, Place):
    pass


class PlaceLine(OsmLine, Place):
    pass


class PlacePolygon(OsmPolygon, Place):
    member_ids = models.JSONField(null=True, blank=True)


class Poi(Amenity):
    operator = models.CharField(max_length=1024, null=True, blank=True)
    osm_subtype = models.CharField(max_length=1024, null=True, blank=True)

    class Meta:
        abstract = True


class PoiPoint(OsmPoint, Poi):
    pass


class PoiLine(OsmLine, Poi):
    pass


class PoiPolygon(OsmPolygon, Poi):
    member_ids = models.JSONField(null=True, blank=True)
    pass


class PublicTransport(WheelchairAccess):

    public_transport = models.TextField(max_length=1024, null=True, blank=True)
    layer = models.IntegerField(null=True, blank=True)
    ref = models.TextField(max_length=1024, null=True, blank=True)
    operator = models.TextField(max_length=1024, null=True, blank=True)
    network = models.TextField(max_length=1024, null=True, blank=True)
    surface = models.TextField(max_length=1024, null=True, blank=True)
    bus = models.TextField(max_length=1024, null=True, blank=True)
    shelter = models.TextField(max_length=1024, null=True, blank=True)
    bench = models.TextField(max_length=1024, null=True, blank=True)
    lit = models.TextField(max_length=1024, null=True, blank=True)
    osm_subtype = models.CharField(max_length=1024, null=True, blank=True)

    class Meta:
        abstract = True


class PublicTransportPoint(OsmPoint, PublicTransport):
    pass


class PublicTransportLine(OsmLine, PublicTransport):
    pass


class PublicTransportPolygon(OsmPolygon, PublicTransport):
    pass


class Road(models.Model):
    ref = models.CharField(max_length=1024, null=True, blank=True)
    maxspeed = models.IntegerField(null=True, blank=True)
    layer = models.CharField(max_length=1024, null=True, blank=True)
    tunnel = models.CharField(max_length=1024, null=True, blank=True)
    bridge = models.CharField(max_length=1024, null=True, blank=True)

    class Meta:
        abstract = True


class RoadPoint(OsmPoint, Road):
    oneway = models.IntegerField(null=True, blank=True)
    access = models.CharField(max_length=1024, null=True, blank=True)


class RoadLine(OsmLine, Road):
    major = models.BooleanField(null=True, default=False)
    route_foot = models.BooleanField(null=True, default=False)
    route_cycle = models.BooleanField(null=True, default=False)
    route_motor = models.BooleanField(null=True, default=False)
    oneway = models.IntegerField(null=True, blank=True)
    access = models.CharField(max_length=1024, null=True, blank=True)


class RoadPolygon(OsmPolygon, Road):
    major = models.BooleanField(null=True, default=False)
    route_foot = models.BooleanField(null=True, default=False)
    route_cycle = models.BooleanField(null=True, default=False)
    route_motor = models.BooleanField(null=True, default=False)
    access = models.CharField(max_length=1024, null=True, blank=True)


class RoadMajor(OsmLine, Road):
    major = models.BooleanField(null=True, default=False)


class Shop(Amenity, WheelchairAccess):

    operator = models.CharField(max_length=1024, null=True, blank=True)
    brand = models.CharField(max_length=1024, null=True, blank=True)
    website = models.CharField(max_length=1024, null=True, blank=True)
    phone = models.CharField(max_length=1024, null=True, blank=True)
    osm_subtype = models.CharField(max_length=1024, null=True, blank=True)

    class Meta:
        abstract = True


class ShopPoint(OsmPoint, Shop):
    pass


class ShopPolygon(OsmPolygon, Shop):
    pass


class Traffic(models.Model):
    osm_subtype = models.CharField(max_length=1024, null=True, blank=True)

    class Meta:
        abstract = True


class TrafficPoint(OsmPoint, Traffic):
    name = None  # type: ignore


class TrafficLine(OsmLine, Traffic):
    name = None  # type: ignore


class TrafficPolygon(OsmPolygon, Traffic):
    name = None  # type: ignore


class Unitable(models.Model):

    """
    Single table that can take any OSM object and any geometry.

    Notes from the LUA file:
    -- Converted from https://github.com/openstreetmap/osm2pgsql/blob/master/flex-config/unitable.lua
    --   to use JSONB instead of HSTORE and osm schema.
    --
    -------------------------
    --  WARNING:   This layer is NOT intended for production use!
    --  Use this to explore data when building proper structures!
    -------------------------
    --
    -- Includes tags in JSONB (does not rely on all_tags.lua)
    -- Does NOT include deep copy for easy use with "require" like other scripts in this project.

    """

    # Note that post import the "id" field will be missing
    # Resstore with  ALTER TABLE osmflex_unitable ADD COLUMN id bigint GENERATED BY DEFAULT AS IDENTITY;
    osm_id = models.BigIntegerField()
    geom_type = models.CharField(max_length=5, null=True, blank=True)  # N(ode), W(way), R(relation)
    tags = models.JSONField()
    geom = models.GeometryField(srid=3857)

    def __str__(self):
        return f"{self.osm_id}" + " " + ",".join([f"{k}={v}" for k, v in self.tags.items()])

    @classmethod
    def update_from_flex(cls):
        """
        Merge updated information (ie a table dump) from
        rustprooflabs' excellent import schema
        """
        statement = upsert_sql(cls, exclude_fields=["id"])

        with connection.cursor() as c:
            c.execute(statement)


class Water(models.Model):

    layer = models.IntegerField()
    tunnel = models.CharField(max_length=1024, null=True, blank=True)
    bridge = models.CharField(max_length=1024, null=True, blank=True)
    boat = models.CharField(max_length=1024, null=True, blank=True)
    osm_subtype = models.CharField(max_length=1024, null=True, blank=True)

    class Meta:
        abstract = True


class WaterPoint(OsmPoint, Water):
    pass


class WaterLine(OsmLine, Water):
    pass


class WaterPolygon(OsmPolygon, Water):
    pass


class Tags(models.Model):
    geom_type = models.CharField(max_length=2, null=True, blank=True)
    osm_id = models.BigIntegerField(primary_key=True)
    tags = models.JSONField()

    def __str__(self):
        return f"{self.osm_id}" + " " + ",".join([f"{k}={v}" for k, v in self.tags.items()])

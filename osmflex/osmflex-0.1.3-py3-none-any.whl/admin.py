from django.contrib.gis import admin
from django.http import HttpRequest

from osmflex import models

# Register your models here.


class OsmFlexAdmin(admin.GISModelAdmin):  # type: ignore
    search_fields = ("name",)
    list_display = ("osm_id", "osm_type", "name")
    list_filter = ("osm_type",)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(self, *args, **kwargs) -> bool:
        return False

    def get_readonly_fields(self, *args, **kwargs):
        fields = [n.name for n in self.model._meta.fields]
        fields.remove("geom")  # Without this the map in the admin does not show
        return fields

    def get_list_display(self, *args, **kwargs):
        list_display = ["osm_id", "osm_type", "name"]
        if "osm_subtype" in [n.name for n in self.model._meta.fields]:
            list_display.append("osm_subtype")
        return list_display

    def get_list_filter(self, *args, **kwargs):
        list_filter = ["osm_type"]
        if "osm_subtype" in [n.name for n in self.model._meta.fields]:
            list_filter.append("osm_subtype")
        return list_filter


@admin.register(models.AmenityLine)
class AmenityLineAdmin(OsmFlexAdmin):
    ...


@admin.register(models.AmenityPoint)
class AmenityPointAdmin(OsmFlexAdmin):
    ...


@admin.register(models.AmenityPolygon)
class AmenityPolygonAdmin(OsmFlexAdmin):
    ...


@admin.register(models.BuildingPoint)
class BuildingPointAdmin(OsmFlexAdmin):
    ...


@admin.register(models.BuildingPolygon)
class BuildingPolygonAdmin(OsmFlexAdmin):
    ...


@admin.register(models.IndoorLine)
class IndoorLineAdmin(OsmFlexAdmin):
    ...


@admin.register(models.IndoorPoint)
class IndoorPointAdmin(OsmFlexAdmin):
    ...


@admin.register(models.IndoorPolygon)
class IndoorPolygonAdmin(OsmFlexAdmin):
    ...


@admin.register(models.InfrastructureLine)
class InfrastructureLineAdmin(OsmFlexAdmin):
    ...


@admin.register(models.InfrastructurePoint)
class InfrastructurePointAdmin(OsmFlexAdmin):
    ...


@admin.register(models.InfrastructurePolygon)
class InfrastructurePolygonAdmin(OsmFlexAdmin):
    ...


@admin.register(models.LandusePoint)
class LandusePointAdmin(OsmFlexAdmin):
    ...


@admin.register(models.LandusePolygon)
class LandusePolygonAdmin(OsmFlexAdmin):
    ...


@admin.register(models.LeisurePoint)
class LeisurePointAdmin(OsmFlexAdmin):
    ...


@admin.register(models.LeisurePolygon)
class LeisurePolygonAdmin(OsmFlexAdmin):
    ...


@admin.register(models.NaturalLine)
class NaturalLineAdmin(OsmFlexAdmin):
    ...


@admin.register(models.NaturalPoint)
class NaturalPointAdmin(OsmFlexAdmin):
    ...


@admin.register(models.NaturalPolygon)
class NaturalPolygonAdmin(OsmFlexAdmin):
    ...


@admin.register(models.PlaceLine)
class PlaceLineAdmin(OsmFlexAdmin):
    ...


@admin.register(models.PlacePoint)
class PlacePointAdmin(OsmFlexAdmin):
    ...


@admin.register(models.PlacePolygon)
class PlacePolygonAdmin(OsmFlexAdmin):
    ...


@admin.register(models.PoiLine)
class PoiLineAdmin(OsmFlexAdmin):
    ...


@admin.register(models.PoiPoint)
class PoiPointAdmin(OsmFlexAdmin):
    ...


@admin.register(models.PoiPolygon)
class PoiPolygonAdmin(OsmFlexAdmin):
    ...


@admin.register(models.PublicTransportLine)
class PublicTransportLineAdmin(OsmFlexAdmin):
    ...


@admin.register(models.PublicTransportPoint)
class PublicTransportPointAdmin(OsmFlexAdmin):
    ...


@admin.register(models.PublicTransportPolygon)
class PublicTransportPolygonAdmin(OsmFlexAdmin):
    ...


@admin.register(models.RoadLine)
class RoadLineAdmin(OsmFlexAdmin):
    ...


@admin.register(models.RoadPoint)
class RoadPointAdmin(OsmFlexAdmin):
    ...


@admin.register(models.RoadPolygon)
class RoadPolygonAdmin(OsmFlexAdmin):
    ...


@admin.register(models.ShopPoint)
class ShopPointAdmin(OsmFlexAdmin):
    ...


@admin.register(models.ShopPolygon)
class ShopPolygonAdmin(OsmFlexAdmin):
    ...


@admin.register(models.TrafficLine)
class TrafficLineAdmin(OsmFlexAdmin):
    ...


@admin.register(models.TrafficPoint)
class TrafficPointAdmin(OsmFlexAdmin):
    ...


@admin.register(models.TrafficPolygon)
class TrafficPolygonAdmin(OsmFlexAdmin):
    ...


@admin.register(models.Unitable)
class UnitableAdmin(admin.GISModelAdmin):  # type: ignore
    ...


@admin.register(models.WaterLine)
class WaterLineAdmin(OsmFlexAdmin):
    ...


@admin.register(models.WaterPoint)
class WaterPointAdmin(OsmFlexAdmin):
    ...


@admin.register(models.WaterPolygon)
class WaterPolygonAdmin(OsmFlexAdmin):
    ...


@admin.register(models.Tags)
class TagsAdmin(admin.ModelAdmin):
    ...

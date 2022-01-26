from weightGIS.Errors import BaseNameNotFound, NoSubUnitWeightIndex

from miscSupports import multi_to_poly, directory_iterator, validate_path, write_json
from shapely.geometry import LineString, Polygon, MultiPolygon
from shapely.ops import split as shp_split
from typing import List, Union, Optional
from shapeObject import ShapeObject
from dataclasses import dataclass
from pathlib import Path
import re


@dataclass
class SubPoly:
    gid: str
    poly: Polygon
    weight: Optional[float]


class PreValidateConstructWeights:
    def __init__(self, working_directory, shapefile_folder, base_name: str, subunits, gid, weight_index):

        # Validate the working directory
        self._working_dir = Path(validate_path(working_directory))

        # Validate the shapefile folder directory
        self._shp_path = validate_path(Path(self._working_dir, shapefile_folder))

        # Set the base shapefile name
        self._base_name = base_name

        # Set if we are investigating sub-units, and note the gid and weight indexes for isolation if we are
        self._sub_units, self.gid, self.weight_index = subunits, gid, self._set_weight_index(weight_index)

    def __call__(self):
        """Validate the starting parameters of ConstructWeights"""

        # Isolate all the shapefiles to investigate changes between
        shape_files = [ShapeObject(f"{self._shp_path}/{file}") for file in self._isolate_shapefiles()]

        # If we are allowing for sub unit population weighting, load that shapefile as well
        if self._sub_units:
            sub_units = self._load_sub_units()
        else:
            sub_units = None

        # Return the base shapefile, the other shapefiles, and the sub-unit shapefile
        return ShapeObject(f"{self._shp_path}/{self._base_name}"), shape_files, sub_units

    @staticmethod
    def _set_weight_index(weight_index):
        """If a weight index has not be declared raise an exception"""
        if not weight_index:
            raise NoSubUnitWeightIndex()
        return weight_index

    def _isolate_shapefiles(self):
        """
        Isolate the shapefile paths, validating that both the base shapefile exists and at least one other file as well
        """
        # Check the base name exists within the shapefile folder, and there is at least one other file
        shapefiles = sorted([file for file in directory_iterator(self._shp_path)
                             if Path(self._shp_path, file).suffix == ".shp"])

        # If it doesn't raise failed to find the base name, raise BaseNameNotFound
        if self._base_name not in shapefiles:
            raise BaseNameNotFound(self._base_name, self._shp_path)

        # If we only found a single shapefile, raise an index error
        if len(shapefiles) <= 1:
            raise IndexError(f"Found {len(shapefiles)} files, but at least two files are required to weight")
        return shapefiles

    def _load_sub_units(self):
        """Load the Sub unit file, if it was requested, and validate a weight_index was set if loaded"""
        # If the subunit name is a path, load it from that path
        if Path(self._sub_units).exists():
            sub_units = ShapeObject(self._sub_units)

        # Otherwise check if it is a file name that exists in the project directory
        elif Path(self._working_dir, self._sub_units).exists():
            sub_units = ShapeObject(f"{self._working_dir}/{self._sub_units}")

        else:
            raise FileNotFoundError(f"Sub unit weighting specified but no file called {self._sub_units} found in "
                                    f"{self._working_dir}")

        # Area interactions don't work with multi-polygons, so split each one based on area of sub poly to multi-polygon
        return [SubPoly(str(rec[self.gid]), p, float(rec[self.weight_index]) * (p.area / poly.area))
                for poly, rec in zip(sub_units.polygons, sub_units.records) for p in multi_to_poly(poly)]


class ConstructWeights:
    def __init__(self, working_directory: Union[str, Path], base_name: str, gid: int, name_indexes: List[int],
                 subunits: Optional[Union[str, Path]] = None, shapefile_folder="Shapefiles", cut_off=100,
                 weight_index: Optional[int] = None):
        """
        This class takes a set of shapefiles and creates a weighted json based on either the overlapping area or
        underlying population.
        """
        self._gid = gid
        self._name_indexes = name_indexes
        self._cut_off = cut_off

        # Validate our parameters, and extract the base shapefile, other shapefiles, and sub unit shapefile if needed
        val = PreValidateConstructWeights(working_directory, shapefile_folder, base_name, subunits, gid, weight_index)
        self.base, self.shapefiles, self.sub_units = val()

    def construct_base_weights(self, write_dir: Union[str, Path], write_name: str = 'BaseWeights') -> None:
        """
        Construct the base weights for a set of shapefiles.

        This iterates through the shapes in the base shapefile to index to, and finds overlapping shapes in another
        shapefile to calculate anm area weight. If sub unit searching is enabled, it is also possible to use under-
        lapping geometery to calculate a sub unit weight. This is done for every shape in the base shapefile and then
        returned
        """
        base_weights = {f"{rec[self._gid]}__{self._construct_name(rec)}": [] for rec in self.base.records}
        for c, (shape, record) in enumerate(zip(self.base.polygons, self.base.records)):
            print(f"{record[self._gid]}: {c + 1} / {len(self.base.polygons)}")

            match_weights = {file: [] for file in [re.sub(r'\D', "", file.file_name) for file in self.shapefiles]}
            for index, match_shape_file in enumerate(self.shapefiles):

                # Set the weight from overlapping area
                weights = self._polygon_area_weights(shape, match_shape_file)

                # If set, set the weight from underling sub unit population
                if self.sub_units:
                    weights = {gid: self._sub_weight(shape, overlap_values) for gid, overlap_values in weights.items()}

                match_weights[re.sub(r'\D', "", match_shape_file.file_name)] = weights

            base_weights[f"{record[self._gid]}__{self._construct_name(record)}"] = match_weights

        write_json(base_weights, write_dir, write_name)

    def _polygon_area_weights(self, current_shape: Union[Polygon, MultiPolygon], match_shape_file: ShapeObject) -> dict:
        """
        Calculates the weights relative to the base years current_shape in terms of area for each shape in the
        match_shape_file which has an overlap
        """
        area_weights = {record[self._gid]: self._calculate_area_weight(current_shape, match_shape, record)
                        for match_shape, record in zip(match_shape_file.polygons, match_shape_file.records)}
        return {gid: weights for gid, weights in area_weights.items() if weights}

    def _calculate_area_weight(self, current_shape: Union[Polygon, MultiPolygon],
                               match_shape: Union[Polygon, MultiPolygon], record: List[str]):
        """
        If the overlap is greater than the cut off, return a dict with Name, Area Weight, Population Stub, and
        Match Shape
        """
        overlap_area = current_shape.intersection(match_shape).area
        if overlap_area > self._cut_off:
            return {'Name': self._construct_name(record), 'Area': (overlap_area / match_shape.area) * 100,
                    'Population': None, 'Match': match_shape}

    def _construct_name(self, record: List[str]) -> str:
        """
        Constructs the place name from the record from a list of indexes
        """
        return "_".join([record[i] for i in self._name_indexes])

    def _sub_weight(self, base_shape: Union[Polygon, MultiPolygon], overlap_values: dict) -> dict:
        """
        Calculates and returns the sub unit weight for each overlapping shape

        If the overlap percentage isn't 100 then the population weight can be calculated from the under-lapping shapes.
        First all the parts of the under-lapping shapes of the overlapping distinct are isolated to calculate the total
        value of the sub weight value. Then, the parts of this shape that overlap the base_shape we are indexing too
        are isolated. The percentage weight is then just the value of (weight_of_match / weight_of_base) * 100.

        """
        if overlap_values['Area'] != 100:
            interior_polys = self._sub_poly_weight(self.sub_units, overlap_values['Match'])
            base_polys = self._sub_poly_weight(interior_polys, base_shape)
            weight = (sum(i.weight for i in base_polys) / sum(i.weight for i in interior_polys) * 100)

            # Some rounding issues may lead to it being possible for it be slightly over 100, in which case we reset it
            # back to be equal to 100
            overlap_values['Population'] = min(weight, 100.0)

        else:
            overlap_values['Population'] = 100.0
        overlap_values.pop('Match', None)
        return overlap_values

    def _sub_poly_weight(self, sub_units: List[SubPoly], main_polygon: Union[Polygon, MultiPolygon]):
        """Calculate the population weight from subunit weights"""
        interior_polys = []
        for poly in multi_to_poly(main_polygon):

            # Isolate the valid sub polys
            valid_subs = [sub for sub in sub_units if poly.intersection(sub.poly).area > self._cut_off]

            # For each valid sub polygon
            for sub_poly in valid_subs:

                # Remove any part of the sub polygon that may be overlapping the polygons holes
                for sub_poly_cut in self._hole_punch_sub_unit(poly, sub_poly):

                    # Split the polygon by the exterior line of the polygon
                    for p in shp_split(sub_poly_cut.poly, LineString(poly.exterior)):

                        # If this split shape is within poly
                        intersection_area = poly.intersection(p).area
                        if intersection_area > self._cut_off:

                            # Calculate its weight, then save this as a SubPoly to interior polygons
                            pop_weight = sub_poly.weight * (intersection_area / sub_poly.poly.area)
                            interior_polys.append(SubPoly(sub_poly.gid, p, pop_weight))

        return interior_polys

    def _hole_punch_sub_unit(self, current_polygon, split_poly):
        """
        A polygon may have holes within it, so we need to punch the holes out so as to not get an inaccurate area.
        """
        changes_from_holes = False
        poly_list = []
        for hole in current_polygon.interiors:
            if Polygon(hole).intersection(split_poly.poly).area > self._cut_off:
                changes_from_holes = True
                split_poly_hole_punched = shp_split(split_poly.poly, LineString(hole))

                # Now we only isolate the parts that are within the overlap from the cut
                for hole_cut_poly in split_poly_hole_punched:
                    if current_polygon.intersection(hole_cut_poly).area > self._cut_off:
                        poly_list.append(SubPoly(split_poly.gid, hole_cut_poly, None))

                if len(poly_list) == 0:
                    changes_from_holes = False

        if changes_from_holes:
            return poly_list
        else:
            return [split_poly]

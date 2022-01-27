from typing import Any, Dict, List

from pandas import DataFrame

from cognite.well_model.models import (
    CasingSchematic,
    DepthMeasurement,
    MnemonicMatchGroup,
    Nds,
    Npt,
    Source,
    SummaryCount,
    TimeMeasurement,
    Trajectory,
    Well,
    Wellbore,
    WellPropertiesSummaryRow,
    WellTops,
    WellWellheadView,
)


class WDLResourceList:
    _RESOURCE = None

    def __init__(self, resources: List[Any]):
        self.data = resources
        for resource in resources:
            if resource is None or not isinstance(resource, self._RESOURCE):  # type: ignore
                raise TypeError(
                    f"All resources for class '{self.__class__.__name__}' must be of type"  # type: ignore
                    f" '{self._RESOURCE.__name__}', "
                    f"not '{type(resource)}'. "
                )

    def dump(self, camel_case: bool = False) -> List[Dict[str, Any]]:
        """Dump the instance into a json serializable Python data type.

        Args:
            camel_case (bool): Use camelCase for attribute names. Defaults to False.

        Returns:
            List[Dict[str, Any]]: A list of dicts representing the instance.
        """
        return [resource.dump(camel_case=camel_case) for resource in self.data]

    def to_pandas(self, camel_case=True) -> DataFrame:
        """Generate a Pandas Dataframe

        Args:
            camel_case (bool, optional): snake_case if false and camelCase if
                true. Defaults to True.

        Returns:
            DataFrame:
        """
        return DataFrame(self.dump(camel_case=camel_case))

    def _repr_html_(self):
        return self.to_pandas(camel_case=True)._repr_html_()

    def __getitem__(self, item):
        return self.data[item]

    def __iter__(self):
        return self.data.__iter__()

    def __repr__(self):
        return_string = [object.__repr__(d) for d in self.data]
        return f"[{', '.join(r for r in return_string)}]"

    def __len__(self):
        return self.data.__len__()


class WellList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.Well` objects"""

    _RESOURCE = Well

    def wellbores(self):
        wellbores: List[Wellbore] = []
        for w in self.data:
            for wb in w.wellbores:
                wellbores.append(wb)
        return WellboreList(wellbores)


class WellboreList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.Wellbore` objects"""

    _RESOURCE = Wellbore


class NptList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.Npt` objects"""

    _RESOURCE = Npt


class TrajectoryList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.Trajectory` objects"""

    _RESOURCE = Trajectory


class NdsList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.Nds` objects"""

    _RESOURCE = Nds


class DepthMeasurementList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.DepthMeasurement` objects"""

    _RESOURCE = DepthMeasurement


class TimeMeasurementList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.TimeMeasurement` objects"""

    _RESOURCE = TimeMeasurement


class CasingsList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.CasingSchematic` objects"""

    _RESOURCE = CasingSchematic


class SourceList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.Source` objects"""

    _RESOURCE = Source


class WellTopsList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.WellTops` objects"""

    _RESOURCE = WellTops

    def to_pandas(self, camel_case=True):
        rows = [
            {
                "wellboreMatchingId": welltop.wellbore_matching_id,
                "wellboreName": welltop.wellbore_name,
                "sequenceExternalId": welltop.source.sequence_external_id,
                "sourceName": welltop.source.source_name,
                "tops_count": len(welltop.tops),
            }
            for welltop in self.data
        ]
        return DataFrame(rows)


class WellPropertiesList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.WellPropertiesSummaryRow` objects"""

    _RESOURCE = WellPropertiesSummaryRow

    def to_pandas(self, camel_case=True) -> DataFrame:
        # Custom pandas implementation to make the column order deterministic
        # and to only show the columns that isn't all None's.
        data: List[WellPropertiesSummaryRow] = self.data
        rows = [
            {
                "region": row.region,
                "country": row.country,
                "block": row.block,
                "field": row.field,
                "quadrant": row.quadrant,
                "operator": row.operator,
                "wellsCount": row.wells_count,
            }
            for row in data
        ]
        df = DataFrame(rows)
        if len(df) > 0:
            df.dropna(axis=1, how="all", inplace=True)
            df.reset_index(drop=True, inplace=True)

        return df


class MnemonicMatchList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.MnemonicMatchGroup` objects"""

    _RESOURCE = MnemonicMatchGroup

    def to_pandas(self, camel_case=True) -> DataFrame:
        """Generate a pandas data frame where each row represents a match.

        Returns:
            DataFrame:
        """
        matches = []
        for group in self.data:
            for match in group.matches:
                tools = [x.code for x in match.tools]
                matches.append(
                    {
                        "mnemonic": group.mnemonic,
                        "companyName": match.company_name,
                        "measurementType": match.measurement_type,
                        "primaryQuantityClass": match.primary_quantity_class,
                        "tools": tools,
                    }
                )
        if len(matches) > 0:
            return DataFrame(matches)

        return DataFrame(
            {
                "mnemonic": [],
                "companyName": [],
                "measurementType": [],
                "primaryQuantityClass": [],
                "tools": [],
            }
        )


class SummaryList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.SummaryCount` objects"""

    _RESOURCE = SummaryCount


class WellWellheadViewList(WDLResourceList):
    """List of :class:`cognite.well_model.models.WellWellheadView` objects"""

    _RESOURCE = WellWellheadView

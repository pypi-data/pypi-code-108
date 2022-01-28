from typing import List

import pandas as pd

from cognite.well_model.models import FieldSources, Well, WellMergeDetails


class WellMergeDetailResource:
    def __init__(self, item: WellMergeDetails):
        self._data = item

    @property
    def well(self) -> Well:
        """Retrieve the well data

        Returns:
            Well: well
        """
        return self._data.well

    @property
    def field_sources(self) -> FieldSources:
        """Get the field sources.

        Returns:
            FieldSources: Field sources
        """
        fs: FieldSources = self._data.field_sources
        return fs

    def to_pandas(self) -> pd.DataFrame:
        """Create a pandas data frame

        Returns:
            pd.DataFrame: Data frame
        """
        w: Well = self.well.dict()
        s = self.field_sources.dict()
        fields = [
            "name",
            "description",
            "country",
            "quadrant",
            "spudDate",
            "block",
            "field",
            "operator",
            "wellType",
            "license",
            "waterDepth",
            "wellhead",
        ]
        data = []
        for field in fields:
            field_source = s[field]
            field_data = {
                "property": field,
                "value": w[field],
            }
            if field_source:
                field_data["sourceName"] = field_source["sourceName"]
                field_data["assetExternalId"] = field_source["assetExternalId"]
            data.append(field_data)
        return pd.DataFrame(data).set_index("property")

    def _repr_html_(self):
        return self.to_pandas()._repr_html_()

    def __getitem__(self, item):
        return self._data[item]

    def __iter__(self):
        return self._data.__iter__()

    def __repr__(self):
        return_string = [object.__repr__(d) for d in self._data]
        return f"[{', '.join(r for r in return_string)}]"

    def __len__(self):
        return self._data.__len__()


class WellMergeDetailList:
    def __init__(self, items: List[WellMergeDetailResource]):
        self._items = items

    def to_pandas(self) -> pd.DataFrame:
        """Create pandas data frame that combines data from multiple wells.

        Returns:
            pd.DataFrame: Data frame
        """
        if not self._items:
            return pd.DataFrame()
        frames = []
        for merge_detail in self._items:
            df = merge_detail.to_pandas()
            df["well_matching_id"] = merge_detail.well.matching_id
            df["well_name"] = merge_detail.well.name
            df["property"] = df.index
            frames.append(df)
        df = pd.concat(frames)
        df.set_index("well_matching_id", inplace=True)
        df = df.reindex(columns=["well_name", "property", "value", "sourceName", "assetExternalId"])
        return df

    def _repr_html_(self):
        return self.to_pandas()._repr_html_()

    def __getitem__(self, item):
        return self._items[item]

    def __iter__(self):
        return self._items.__iter__()

    def __repr__(self):
        return_string = [object.__repr__(d) for d in self._items]
        return f"[{', '.join(r for r in return_string)}]"

    def __len__(self):
        return self._items.__len__()

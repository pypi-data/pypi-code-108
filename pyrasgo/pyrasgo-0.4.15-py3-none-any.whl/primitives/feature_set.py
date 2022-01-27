from pyrasgo.api.connection import Connection
from pyrasgo.schemas import feature_set as api
from pyrasgo.utils import track_usage

class FeatureSet(Connection):
    """
    Stores a Rasgo FeatureSet
    """

    def __init__(self, api_object, **kwargs):
        super().__init__(**kwargs)
        self._fields = api.FeatureSet(**api_object)

    def __getattr__(self, item):
        try:
            return self._fields.__getattribute__(item)
        except KeyError:
            self.refresh()
        try:
            return self._fields.__getattribute__(item)
        except KeyError:
            raise AttributeError(f"No attribute named {item}")

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"FeatureSet(id={self.id}, name={self.name}, sourceTable={self.sourceTable}, granularities={self.granularities})"

# ----------
# Properties
# ----------

# -------
# Methods
# -------
    @track_usage
    def display_source_code(self):
        """
        Convenience function to display the sourceCode property
        """
        return self._fields.sourceCode

    @track_usage
    def rebuild_from_source_code(self):
        """
        Rebuild the FeatureSet using the source code
        """
        raise NotImplementedError()

    @track_usage
    def refresh(self):
        """
        Updates the FeatureSet's attributes from the API
        """
        self._fields = api.FeatureSet(**self._get(f"/feature-sets/{self.id}", api_version=1).json())

    @track_usage
    def rename(self, new_name: str):
        """
        Updates a FeatureSet's display name
        """
        print(f"Renaming FeatureSet {self.id} from {self.name} to {new_name}")
        featureset = api.FeatureSetUpdate(id=self.id, name=new_name)
        self._fields = api.FeatureSet(**self._patch(f"/feature-sets/{self.id}",
                                                    api_version=1, _json=featureset.dict(exclude_unset=True, exclude_none=True)).json())

    def _make_table_metadata(self):
        table_attribute = self._fields.sourceTable
        organization = self._get_profile().get("organization")
        if table_attribute.count(".") == 2:
            database = table_attribute.split(".")[0]
            schema = table_attribute.split(".")[1]
            table = table_attribute.split(".")[-1]
        else:
            database = organization.get("database")
            schema = organization.get("schema")
            table = table_attribute
        metadata = {
            "database": database,
            "schema": schema,
            "table": table,
        }
        return metadata
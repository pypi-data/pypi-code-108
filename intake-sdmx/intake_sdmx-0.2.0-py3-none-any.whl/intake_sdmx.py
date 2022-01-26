"""intake plugin for SDMX data sources"""


from collections.abc import MutableMapping
from datetime import date
from itertools import chain

import intake
import pandasdmx as sdmx
from intake.catalog import Catalog
from intake.catalog.local import LocalCatalogEntry, UserParameter
from intake.catalog.utils import reload_on_change

__version__ = "0.2.0"

__all__ = ["SDMXSources", "SDMXDataflows", "SDMXData"]

# indicate wildcarded dimensions for data reads
NOT_SPECIFIED = "*"


class LazyDict(MutableMapping):
    """
    A dict-like type whose values are computed on first access by calling abcfactory function to be passed to __init__.
    """

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self._dict = dict(*args, **kwargs)
        self._func = func

    def update(self, *args, **kwargs):
        return self._dict.update(*args, **kwargs)

    def __getitem__(self, key):
        if self._dict[key] is None:
            self._dict[key] = self._func(key)
        return self._dict[key]

    def __setitem__(self, key, value):
        return self._dict.__setitem__(key, value)

    def __contains__(self, key):
        return self._dict.__contains__(key)

    def __len__(self):
        return self._dict.__len__()

    def __delitem__(self, key):
        return self._dict.__delitem__(key)

    def __iter__(self):
        return self._dict.__iter__()

    def __str__(self):
        return "".join((self.__class__.__name__, "(", str(self._dict), ")"))


class SDMXSources(Catalog):
    """
     catalog of SDMX data sources, a.k.a. agencies
    supported by pandaSDMX
    """

    version = __version__  # why does version not ocur in the yaml?
    container = "catalog"
    # I thought to set `name`here as well. But it is ignored.
    # so set it as instance attribute below.

    def _load(self):
        self.name = "SDMX data sources"
        self.description = "SDMX data sources (a.k.a. agencies / data providers)\
        supported by pandaSDMX"
        # Add  source entries which do not support dataflows
        for source_id, source in sdmx.source.sources.items():
            # Take only sources which support dataflow.
            # This excludes json-based sources
            # souch as OECD and ABS as these only allow data queries, not metadata
            if source.supports["dataflow"]:
                descr = source.name
                metadata = {"source_id": source_id}
                e = LocalCatalogEntry(
                    source_id + "_SDMX_dataflows",
                    descr,
                    SDMXDataflows,
                    direct_access=True,
                    # set storage_options to {} if not set. This avoids TypeError
                    # when passing it to sdmx.Request() later
                    args={"storage_options": self.storage_options or {}},
                    cache=[],
                    parameters=[],
                    metadata=metadata,
                    catalog_dir="",
                    getenv=False,
                    getshell=False,
                    catalog=self,
                )
                self._entries[source_id] = e
                # add same entry under its name for clarity
                self._entries[descr] = e


class SDMXCodeParam(UserParameter):
    """
    Helper class to distinguish coded dimensions from other parameters
    and to perform additional validation. .
    """

    def validate(self, value):
        value = super().validate(value)
        # additional validations
        if value != self.default:
            # replace names by corresponding codes, eg. "US dollar" by "USD"
            for i in range(len(value)):
                # Does item have an odd index within self.allowed? Then it is a name.
                p = self.allowed.index(value[i])
                if p % 2:
                    # replace it with its predecessor
                    value[i] = self.allowed[p - 1]
            # Check for duplicates
            if len(value) > len(set(value)):
                raise ValueError(f"Duplicate codes are not allowed: {value}")
            # Don't use "*" with regular  codes
            if len(value) > 1 and "*" in value:
                raise ValueError(
                    f"Using '*' alongside regular codes is ambiguous: {value}"
                )
        return value


class SDMXDataflows(Catalog):
    """
    catalog of dataflows for a given SDMX source
    """

    version = __version__
    container = "catalog"
    partition_access = False

    def _make_entries_container(self):
        return LazyDict(self._make_dataflow_entry)

    def _load(self):
        # read metadata on dataflows
        self.name = self.metadata["source_id"] + "_SDMX_dataflows"
        # Request dataflows from remote SDMX service
        self.req = sdmx.Request(self.metadata["source_id"], **self.storage_options)
        # get full list of dataflows
        self._flows_msg = self.req.dataflow()
        # to mapping from names to IDs for later back-translation
        # We use this catalog to store 2 entries per dataflow: ID and# human-readable name
        self.name2id = {}
        for dataflow in self._flows_msg.dataflow.values():
            flow_id, flow_name = dataflow.id, str(dataflow.name)
            # make 2 entries per dataflow using its ID and name
            self._entries[flow_id] = None
            self._entries[flow_name] = None
            self.name2id[flow_name] = flow_id

    def _make_dataflow_entry(self, flow_id):
        """
        Factory for dataflow catalog entries. Passed to :class:`LazyDict`
        """
        # if flow_id is actually its name, get the real id
        if flow_id in self.name2id:
            flow_id = self.name2id[flow_id]
        # Download metadata on specified dataflow
        flow_msg = self.req.dataflow(flow_id)
        flow = flow_msg.dataflow[flow_id]
        # is the full DSD already in the msg?
        if flow.structure.is_external_reference:
            # No. So download it
            dsd_id = flow.structure.id
            dsd_msg = self.req.datastructure(dsd_id)
            dsd = dsd_msg.structure[dsd_id]
        else:
            dsd = flow.structure
        descr = str(flow.name)
        # generate metadata for new catalog entry
        metadata = self.metadata.copy()
        metadata["dataflow_id"] = flow_id
        metadata["structure_id"] = dsd.id
        # Make user params for coded dimensions
        # Check for any content constraints to codelists
        if hasattr(flow_msg, "constraint") and flow_msg.constraint:
            constraint = (
                next(iter(flow_msg.constraint.values())).data_content_region[0].member
            )
        else:
            constraint = None
        params = []
        # params for coded dimensions
        for dim in dsd.dimensions:
            lr = dim.local_representation
            # only dimensions with enumeration, i.e. where values are codes
            if lr.enumerated:
                ci = dim.concept_identity
                # Get code ID and  name as its description
                if constraint and dim.id in constraint:
                    codes_iter = (
                        c
                        for c in lr.enumerated.items.values()
                        if c in constraint[dim.id]
                    )
                else:
                    codes_iter = lr.enumerated.items.values()
                codes = list(chain(*((c.id, str(c.name)) for c in codes_iter)))

                # allow "" to indicate wild-carded dimension
                codes.append(NOT_SPECIFIED)
                p = SDMXCodeParam(
                    name=dim.id,
                    description=str(ci.name),
                    type="mlist",
                    allowed=codes,
                    default=[NOT_SPECIFIED],
                )
                params.append(p)
        # Try to retrieve ID of time and freq dimensions for DataFrame index generation.
        # From these dimensions we generate sensible defaults for pandasdmx.writer config.
        dim_candidates = [d.id for d in dsd.dimensions if "TIME" in d.id]
        try:
            time_dim_id = dim_candidates[0]
        except IndexError:
            time_dim_id = NOT_SPECIFIED
        # Ffrequency for period index generation
        dim_candidates = [p.name for p in params if "FREQ" in p.name]
        try:
            freq_dim_id = dim_candidates[0]
        except IndexError:
            freq_dim_id = NOT_SPECIFIED
        # params for startPeriod and endPeriod
        year = date.today().year
        params.extend(
            [
                UserParameter(
                    name="startPeriod",
                    description="startPeriod",
                    type="str",
                    default=str(year - 2),
                ),
                UserParameter(
                    name="endPeriod",
                    description="endPeriod",
                    type="str",
                    default=str(year - 1),
                ),
                UserParameter(
                    name="dtype",
                    description="""data type for pandas.DataFrame. See pandas docs
                        for      allowed values.
                        Default is '' which translates to 'float64'.""",
                    type="str",
                    default="",
                ),
                UserParameter(
                    name="attributes",
                    description="""Include any attributes alongside observations
                    in the DataFrame. See pandasdmx docx for details.
                    Examples: 'osgd' for all attributes, or
                    'os': only attributes at observation and series level.""",
                    type="str",
                ),
                UserParameter(
                    name="index_type",
                    description="""Type of pandas Series/DataFrame index""",
                    type="str",
                    allowed=["object", "datetime", "period"],
                    default="object",
                ),
                UserParameter(
                    name="freq_dim",
                    description="""To generate PeriodIndex (index_type='period')
                    Default is set based on heuristics.""",
                    type="str",
                    default=freq_dim_id,
                ),
                UserParameter(
                    name="time_dim",
                    description="""To generate datetime or period index.
                        Ignored if index_type='object'.""",
                    type="str",
                    default=time_dim_id,
                ),
            ]
        )
        #  jinja2 template for args specification. See intake user guide
        args = {p.name: f"{{{{{p.name}}}}}" for p in params}
        args["storage_options"] = self.storage_options
        return LocalCatalogEntry(
            name=flow_id,
            description=descr,
            driver=SDMXData,
            direct_access=True,
            cache=[],
            parameters=params,
            args=args,
            metadata=metadata,
            catalog_dir="",
            getenv=False,
            getshell=False,
            catalog=self,
        )

    @reload_on_change
    def search(self, text, operator="|"):
        """
        Make subcatalog of entries whose name contains any word from `text`.

        Parameters:

            text[str] : space-separated words
            operator[str[: either "&" or "|" meaning AND or OR

        Return: :instance:`SDMXDataflows`
        """
        if operator not in ["&", "|"]:
            raise ValueError(f"Operator must be one of '&' or '|'. {operator} given.")
        func = all if operator == "&" else any
        words = text.lower().split()
        cat = SDMXDataflows(
            name=self.name + "_search",
            description=self.description,
            ttl=self.ttl,
            getenv=self.getenv,
            getshell=self.getshell,
            metadata=(self.metadata or {}).copy(),
            storage_options=self.storage_options,
        )
        cat.metadata["search"] = {"text": text, "upstream": self.name}
        cat.cat = self
        cat._entries._dict.clear()
        keys = [
            *chain.from_iterable(
                (self.name2id[k], k)
                for k in self.name2id
                if func(word in k.lower() for word in words)
            )
        ]
        cat._entries.clear()
        cat._entries.update({k: None for k in keys})
        return cat


class SDMXData(intake.source.base.DataSource):
    """
    Driver for SDMX data sets of  a given SDMX dataflow.
    Its parameters largely follows  the :class:pandasdmx.Request API.
    """

    version = __version__
    name = "sdmx_dataset"
    container = "dataframe"
    partition_access = True

    def __init__(self, metadata=None, **kwargs):
        super(SDMXData, self).__init__(metadata=metadata)
        self.name = self.metadata["dataflow_id"]
        self.req = sdmx.Request(self.metadata["source_id"], **self.storage_options)
        self.kwargs = kwargs

    def read(self):
        """
        Request dataset from SDMX data source
        via HTTP,
        and convert it to a pandas Series or DataFrame using pandasdmx. The return typedepends on the kwargs passed on instance creation.
"""
        # construct key for selection of rows and columns. See pandasdmx docs for details.
        key_ids = (
            p.name for p in self.entry._user_parameters if isinstance(p, SDMXCodeParam)
        )
        key = {i: self.kwargs[i] for i in key_ids if self.kwargs[i] != [NOT_SPECIFIED]}
        # params for request. Currently, only start- and endPeriod are supported
        params = {k: str(self.kwargs[k].year) for k in ["startPeriod", "endPeriod"]}
        # remove endPeriod if it is prior to startPeriod ()
        if params["endPeriod"] < params["startPeriod"]:
            del params["endPeriod"]
        # Now request the data via HTTP
        # TODO: handle   optional Request.get kwargs eg. fromfile, timeout.
        data_msg = self.req.data(self.metadata["dataflow_id"], key=key, params=params)
        # get writer config.
        # Capture only non-empty values as these will be filled by the writer
        writer_config = {
            k: self.kwargs[k] for k in ["dtype", "attributes"] if self.kwargs[k]
        }
        # kwargs to customize DataFrame/Series  index generation.
        # construct  args   to conform to writer API
        index_type = self.kwargs["index_type"]
        freq_dim = self.kwargs["freq_dim"]
        time_dim = self.kwargs["time_dim"]
        if index_type == "datetime":
            writer_config["datetime"] = True if freq_dim == NOT_SPECIFIED else freq_dim
        elif index_type == "period":
            datetime = {}
            datetime["freq"] = True if freq_dim == NOT_SPECIFIED else freq_dim
            datetime["dim"] = True if time_dim == NOT_SPECIFIED else time_dim
            writer_config["datetime"] = datetime
        # generate the Series or dataframe
        self._dataframe = data_msg.to_pandas(**writer_config)
        return self._dataframe

    def _close(self):
        self._dataframe = None

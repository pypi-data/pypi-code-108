"""Keep record of all filters used"""
import copy

import dclab

from ..util import hashobj


class Filter(object):
    """Handles filters in a pipeline"""
    _instance_counter = 0
    _instances = {}

    def __init__(self, identifier=None, name=None):
        Filter._instance_counter += 1
        if identifier is None:
            identifier = "Filter_{}".format(Filter._instance_counter)
            while identifier in Filter._instances:
                Filter._instance_counter += 1
                identifier = "Filter_{}".format(Filter._instance_counter)

        if name is None:
            name = identifier
        #: unique identifier of the filter
        self.identifier = identifier
        #: user-defined name of the filter
        self.name = name
        #: general filtering arguments are directly passed to
        #: :class:`dclab.filter.Filter`
        self.general = {"remove invalid events": False,  # removes nan/inf
                        "enable filters": True,  # whether to use the filter
                        }
        #: filter for limiting number of events
        self.limit_events = [False, 5000]
        #: box filters with features as keys; each item is a
        #: dictionary with the keys "start", "end", "active"
        self.boxdict = {}
        #: polygon filter list; each item is an identifier of
        #: :class:`dclab.PolygonFilter`
        self.polylist = []
        if identifier in Filter._instances:
            raise ValueError("Filter with identifier "
                             + "'{}' already exists!".format(identifier))
        Filter._instances[identifier] = self

    def __getstate__(self):
        state = {
            "filter used": self.filter_used,
            "identifier": self.identifier,
            "limit events bool": self.limit_events[0],
            "limit events num": self.limit_events[1],
            "name": self.name,
            "remove invalid events": self.general["remove invalid events"],
            "box filters": self.boxdict,
            "polygon filters": sorted(self.polylist),
        }
        return copy.deepcopy(state)

    def __repr__(self):
        repre = "<Pipeline Filter '{}' at {}>".format(self.identifier,
                                                      hex(id(self)))
        return repre

    def __setstate__(self, state):
        state = copy.deepcopy(state)
        if self.identifier != state["identifier"]:
            raise ValueError("Identifier mismatch: '{}' vs. '{}'".format(
                self.identifier, state["identifier"]))
        self.general["enable filters"] = state["filter used"]
        self.limit_events = [state["limit events bool"],
                             state["limit events num"]]
        self.name = state["name"]
        self.general["remove invalid events"] = state["remove invalid events"]
        self.boxdict = state["box filters"]
        self.polylist = state["polygon filters"]

    @staticmethod
    def get_filter(identifier):
        """Get the filter with the given identifier.

        Notes
        -----
        Creates the filter if it does not exist.
        """
        if identifier in Filter._instances:
            f = Filter._instances[identifier]
        else:
            f = Filter(identifier=identifier)
        return f

    @staticmethod
    def get_instances():
        return Filter._instances

    @property
    def filter_used(self):
        return self.general["enable filters"]

    @filter_used.setter
    def filter_used(self, b):
        self.general["enable filters"] = b

    @property
    def hash(self):
        """Return the hash of the filter"""
        return hashobj(self.__getstate__())

    def add_box_filter(self, feature, start, end, active=True):
        """Add a box filter"""
        if not dclab.dfn.scalar_feature_exists(feature):
            raise ValueError("Unknown scalar feature: {}".format(feature))
        self.boxdict[feature] = {
            "start": start,
            "end": end,
            "active": active}

    def apply_to_dataset(self, dataset):
        """Convenience function to apply this filter to a dataset

        Parameters
        ----------
        dataset: :class:`dclab.RTDCBase`
            Input dataset

        Returns
        -------
        filtered_dataset: RTDCBase
            Either the input dataset, or a hierarchy child.

        Notes
        -----

        """
        self.update_dataset(dataset)
        dataset.apply_filter()

    def update_dataset(self, dataset):
        """Update the filtering configuration of a dataset

        Notes
        -----
        Due to the design of the filtering pipeline, it is not
        possible to use manual filters. If any are set, they
        are removed from the filter.
        """
        # remove all previous filters
        dataset.reset_filter()
        cfgfilt = dataset.config["filtering"]

        # set general options
        cfgfilt.update(self.general)
        cfgfilt["limit events"] = self.limit_events[0] * self.limit_events[1]
        # set box filters
        for feat in self.boxdict:
            if self.boxdict[feat]["active"]:
                cfgfilt["{} min".format(feat)] = self.boxdict[feat]["start"]
                cfgfilt["{} max".format(feat)] = self.boxdict[feat]["end"]

        # set polygon filters
        for pid in self.polylist:
            dataset.polygon_filter_add(pid)

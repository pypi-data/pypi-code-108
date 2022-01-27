import dclab


class FilterRay(object):
    def __init__(self, slot):
        """Manages filter-based dataset hierarchies

        Filter rays are used to cache RTDCBase filter-hierarchy
        children.
        """
        #: identifier of the ray (matches the slot)
        self.identifier = slot.identifier
        #: slot defining the ray
        self.slot = slot
        #: list of RTDCBase (hierarchy children)
        self.steps = []
        #: corresponds to hashes of the applied filters
        self.step_hashes = []
        # holds the filters (protected so that users use set_filters)
        self._filters = []
        # used for testing (incremented when the ray is cut)
        self._generation = 0
        # used for checking validity of the ray
        self._slot_hash = "unset"
        self._root_child = None

    def __repr__(self):
        repre = "<Pipeline Filter Ray '{}' at {}>".format(self.identifier,
                                                          hex(id(self)))
        return repre

    def _add_step(self, ds, filt):
        """Add a filter step"""
        self.step_hashes.append(filt.hash)
        filt.update_dataset(ds)
        self.steps.append(ds)
        return self._new_child(ds, filt)

    def _new_child(self, ds, filt=None, apply_filter=False):
        identifier = self.slot.identifier
        if filt is None:
            identifier += "-root"
        else:
            identifier += "-" + filt.identifier + "-child"
        ds = dclab.rtdc_dataset.RTDC_Hierarchy(
            ds, apply_filter=apply_filter, identifier=identifier)
        return ds

    @property
    def filters(self):
        """filters currently used by the ray"""
        return self._filters

    @property
    def root_child(self):
        """This is the first element in self.steps
        (Will return a dataset even if self.steps is empty)
        """
        if self._slot_hash != self.slot.hash:
            # reset everything (e.g. emodulus recipe might have changed)
            self.steps = []
            self.step_hashes = []
            self._root_child = self._new_child(self.slot.get_dataset(),
                                               apply_filter=True)
            self._slot_hash = self.slot.hash
        return self._root_child

    def get_final_child(self, rtdc_ds=None, apply_filter=True):
        """Return the final ray child of `rtdc_ds`

        If `rtdc_ds` is None, then the dataset of the current
        ray (self.slot) is used. If `rtdc_ds` is given, then
        no ray caching is performed and the present ray is not
        modified.

        This is a convenience function used when the filter ray
        must be applied to a different dataset (not the one in
        `self.slot`). This is used in Shape-Out when a filter ray
        is applied to other data on disk e.g. when computing
        statistics. For regular use of the filter ray in a
        pipeline, use :func:`get_dataset`.
        """
        filters = self.filters

        if rtdc_ds is None:
            # normal case
            external = False
            rtdc_ds = self.slot.get_dataset()
            ds = self.root_child
        else:
            # ray is applied to other data
            external = True
            # do not modify rtdc_ds (create a child to work with)
            ds = self._new_child(rtdc_ds, apply_filter=True)

        # Dear future self,
        #
        # don't even think about filter ray branching.
        #
        # Sincerely,
        # past self

        if filters:
            # apply all filters
            for ii, filt in enumerate(filters):
                # remmeber the previous hierarchy parent
                # (ds is always used for the next iteration)
                prev_ds = ds
                if external:
                    # do not touch self.steps or self.step_hashes
                    filt.update_dataset(ds)
                    ds = self._new_child(ds, filt)
                elif len(self.steps) < ii+1:
                    # just create a new step
                    ds = self._add_step(ds, filt)
                elif filt.hash != self.step_hashes[ii]:
                    # the filter ray is changing here;
                    # cut it and add a new step
                    self.steps = self.steps[:ii]
                    self.step_hashes = self.step_hashes[:ii]
                    ds = self._add_step(ds, filt)
                    self._generation += 1  # for testing
                else:
                    # the filters match so far
                    if len(self.steps) > ii + 1:  # next child exists
                        ds = self.steps[ii + 1]
                    else:  # next child does not exist
                        ds = self._new_child(ds, filt)
            # we now have the entire filter pipeline in self.steps
            final_ds = prev_ds
        else:
            final_ds = rtdc_ds
        if apply_filter:
            final_ds.apply_filter()
        return final_ds

    def get_dataset(self, filters=None, apply_filter=True):
        """Return the dataset that corresponds to applying these filters

        Parameters
        ----------
        filters: list of Filter or None
            Filters used for computing the dataset hierarchy. If set
            to None, the current filters in `self.filters` are used.
        """
        if filters is not None:
            # put the filters in place
            self.set_filters(filters)
        # compute the final hierarchy child
        ds = self.get_final_child(apply_filter=apply_filter)
        return ds

    def set_filters(self, filters):
        """Set the filters of the current ray"""
        # only take into account active filters
        self._filters = [f for f in filters if f.filter_used]

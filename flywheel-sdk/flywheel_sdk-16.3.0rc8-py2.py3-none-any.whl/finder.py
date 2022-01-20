"""Provides finder interface for collections"""


class Finder(object):
    """Finder wrapper for finding objects in a collection"""

    def __init__(self, context, method, *args):
        """Create a new finder object for the given method

        :param object context: The context object (i.e. Flywheel client)
        :param str method: The name of the method to invoke (must support pagination)
        :param args: Additional arguments to pass to the find function (e.g. id)
        """
        self._context = context
        self._method = method
        self._args = args
        self._fn = None

    def __call__(self, *args, **kwargs):
        """Invoke the underlying get function directly

        :param str filter: The filter to apply. (e.g. label=my-label,created>2018-09-22)
        :param str sort: The sort fields and order. (e.g. label:asc,created:desc)
        :param int limit: The maximum number of entries to return.
        :param int skip: The number of entries to skip.
        :param int page: The page number (i.e. skip limit*page entries)
        :param str after_id: Paginate after the given id. (Cannot be used with sort, page or skip)
        """
        return self._func(*(self._args + args), **kwargs)

    def find(self, *args, **kwargs):
        """Find all items in the collection that match the provided filter

        :param args: The list of filters to apply (e.g. 'label=my-label' , 'created>2018-09-22')
        :param str sort: The sort fields and order. (e.g. label:asc,created:desc)
        :param int limit: The maximum number of entries to return.
        :param int skip: The number of entries to skip.
        :param int page: The page number (i.e. skip limit*page entries)
        :param str after_id: Paginate after the given id. (Cannot be used with sort, page or skip)
        """
        return self.__find(args, kwargs)

    def find_one(self, *args, **kwargs):
        """Find exactly one item matching the provided filter. Raises a ValueError if 0 or 2+ items matched.

        :param args: The list of filters to apply (e.g. 'label=my-label' , 'created>2018-09-22')
        :param str sort: The sort fields and order. (e.g. label:asc,created:desc)
        :param int limit: The maximum number of entries to return.
        :param int skip: The number of entries to skip.
        :param int page: The page number (i.e. skip limit*page entries)
        :param str after_id: Paginate after the given id. (Cannot be used with sort, page or skip)
        """
        return self.__find(args, kwargs, find_one=True)

    def find_first(self, *args, **kwargs):
        """Find the first item matching the provided filter. Returns None if no items matched.

        :param args: The list of filters to apply (e.g. 'label=my-label' , 'created>2018-09-22')
        :param str sort: The sort fields and order. (e.g. label:asc,created:desc)
        :param int limit: The maximum number of entries to return.
        :param int skip: The number of entries to skip.
        :param int page: The page number (i.e. skip limit*page entries)
        :param str after_id: Paginate after the given id. (Cannot be used with sort, page or skip)
        """
        return self.__find(args, kwargs, find_first=True)

    def iter(self, limit=250):
        """Iterate over all items in the collection, without limit.

        :param int limit: The number of entries to return per call (default is 250)
        """
        return self.iter_find(limit=limit)

    def iter_find(self, *args, **kwargs):
        """Find all items in the collection that match the provided filter, without limit.

        :param args: The list of filters to apply (e.g. 'label=my-label' , 'created>2018-09-22')
        :param int limit: The number of entries to return per call (default is 250)
        """
        if "limit" not in kwargs:
            kwargs["limit"] = 250

        if args:
            kwargs["filter"] = ",".join(args)

        if "sort" not in kwargs:
            if "limit" not in kwargs:
                kwargs["limit"] = 250

            while True:
                results = self._func(*self._args, **kwargs)

                if not results:
                    break

                for item in results:
                    yield item

                kwargs["after_id"] = results[-1].id
        else:
            if "limit" not in kwargs:
                kwargs["limit"] = 1000

            kwargs["page"] = 1

            while True:
                results = self._func(*self._args, **kwargs)

                if not results:
                    break

                for item in results:
                    yield item

                kwargs["page"] += 1

    @property
    def _func(self):
        if not self._fn:
            self._fn = getattr(self._context, self._method)
        return self._fn

    def __find(self, filters, kwargs, find_first=False, find_one=False):

        if filters:
            kwargs["filter"] = ",".join(filters)

        if find_one:
            kwargs["limit"] = 2  # We only need one some get at most 2 for error case
            results = self._func(*self._args, **kwargs)
            if len(results) != 1:
                raise ValueError("Found more results than 1!")
            return results[0]

        if find_first:
            kwargs["limit"] = 1  # always return first so no need for more
            results = self._func(*self._args, **kwargs)
            if results:
                return results[0]
            return None

        # Force paginated find calls on core-api which now requires a page limit
        # Technically a limit of 0 is supported and returns all results.
        if kwargs.get("limit") is None:
            results = []
            return [r for r in self.iter_find(**kwargs)]

        # Limit applied paginated find
        # Techinically we should iterate find on this too with the limit to
        # prevent a user from setting a limit of 1MM and crushing the server
        # This will pull it to memory though so we should enforce a max limit
        # or deprecate this in favor of iter find
        results = self._func(*self._args, **kwargs)
        return results

import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import warnings


class _click_callbacks(object):
    """
    a collection of callback-functions

    to attach a callback, use:
        >>> cid = m.cb.click.attach.annotate(**kwargs)
        or
        >>> cid = m.cb.pick.attach.annotate(**kwargs)

    to remove an already attached callback, use:
        >>> m.cb.click.remove(cid)
        or
        >>> m.cb.pick.remove(cid)


    you can also define custom callback functions as follows:

        >>> def some_callback(self, **kwargs):
        >>>     print("hello world")
        >>>     print("the position of the clicked pixel", kwargs["pos"])
        >>>     print("the data-index of the clicked pixel", kwargs["ID"])
        >>>     print("data-value of the clicked pixel", kwargs["val"])
    and attach them via:
        >>> cid = m.cb.click.attach(some_callback)
        or
        >>> cid = m.cb.click.attach(some_callback)
    (... and remove them in the same way as pre-defined callbacks)
    """

    # the naming-convention of the functions is as follows:
    #
    # _<NAME>_cleanup : a function that is executed if the callback
    #                   is removed from the plot
    #

    # ID : any
    #     The index-value of the pixel in the data.
    # pos : tuple
    #     A tuple of the position of the pixel in plot-coordinates.
    #     (ONLY relevant if ID is NOT provided!)
    # val : int or float
    #     The parameter-value of the pixel.
    # ind : int
    #     The index of the clicked pixel
    #     (ONLY relevant if ID is NOT provided!)

    # this list determines the order at which callbacks are executed!
    # (custom callbacks are always added to the end)
    _cb_list = [
        "get_values",
        "load",
        "print_to_console",
        "annotate",
        "mark",
        "plot",
        "peek_layer",
        "clear_annotations",
        "clear_markers",
    ]

    def __init__(self, m, temp_artists):
        self.m = m

        # a list shared with the container that is used to store temporary artists
        # (artists will be removed after each draw-event!)
        self._temporary_artists = temp_artists

    @staticmethod
    def _popargs(kwargs):
        # pop the default kwargs passed to each callback function
        # (to avoid showing them as kwargs when called)
        ID = kwargs.pop("ID", None)
        pos = kwargs.pop("pos", None)
        val = kwargs.pop("val", None)
        ind = kwargs.pop("ind", None)
        picker_name = kwargs.pop("picker_name", "default")

        return ID, pos, val, ind, picker_name

    def print_to_console(self, **kwargs):
        """Print details on the clicked pixel to the console"""
        ID, pos, val, ind, picker_name = self._popargs(kwargs)

        xlabel = self.m.data_specs.xcoord
        ylabel = self.m.data_specs.ycoord
        if ID is not None:
            printstr = ""
            x, y = [np.format_float_positional(i, trim="-", precision=4) for i in pos]
            printstr += f"{xlabel} = {x}\n{ylabel} = {y}\n"
            printstr += f"ID = {ID}\n"

            if isinstance(val, (int, float)):
                val = np.format_float_positional(val, trim="-", precision=4)
            printstr += f"{self.m.data_specs.parameter} = {val}"
        else:
            lon, lat = self.m._transf_plot_to_lonlat.transform(*pos)

            printstr = (
                f"x = {pos[0]}\n"
                + f"y = {pos[1]}\n"
                + f"lon = {lon}\n"
                + f"lat = {lat}"
            )

        print(printstr)

    def annotate(
        self,
        pos_precision=4,
        val_precision=4,
        permanent=False,
        text=None,
        layer=10,
        **kwargs,
    ):
        """
        Add a basic text-annotation to the plot at the position where the map
        was clicked.

        If permanent = True, the generated annotations are stored in a list
        which is accessible via `m.cb.[click/pick].get.permanent_annotations`

        Parameters
        ----------
        pos_precision : int
            The floating-point precision of the coordinates.
            The default is 4.
        val_precision : int
            The floating-point precision of the parameter-values (only used if
            "val_fmt=None"). The default is 4.
        permanent : bool
            Indicator if the annotation should be temporary (False) or
            permanent (True). The default is False
        text : callable or str, optional
            if str: the string to print
            if callable: A function that returns the string that should be
            printed in the annotation with the following call-signature:

                >>> def text(m, ID, val, pos, ind):
                >>>     # m   ... the Maps object
                >>>     # ID  ... the ID in the dataframe
                >>>     # pos ... the position
                >>>     # val ... the value
                >>>     # ind ... the index
                >>>
                >>>     return "the string to print"

            The default is None.
        layer : int
            The layer-level on which to draw the artist.
            (First layer 0 is drawn, then layer 1 on top then layer 2 etc...)
            The default is 10.
        **kwargs
            kwargs passed to matplotlib.pyplot.annotate(). The default is:

            >>> dict(xytext=(20, 20),
            >>>      textcoords="offset points",
            >>>      bbox=dict(boxstyle="round", fc="w"),
            >>>      arrowprops=dict(arrowstyle="->"))
            >>>     )

        """

        ID, pos, val, ind, picker_name = self._popargs(kwargs)

        xlabel = self.m.data_specs.xcoord
        ylabel = self.m.data_specs.ycoord

        ax = self.m.figure.ax

        if text is None:
            if ID is not None and self.m.data is not None:
                x, y = [
                    np.format_float_positional(i, trim="-", precision=pos_precision)
                    for i in self.m.data.loc[ID][[xlabel, ylabel]]
                ]
                x0, y0 = [
                    np.format_float_positional(i, trim="-", precision=pos_precision)
                    for i in pos
                ]
                if isinstance(val, (int, float)):
                    val = np.format_float_positional(
                        val, trim="-", precision=val_precision
                    )

                printstr = (
                    f"{xlabel} = {x} ({x0})\n"
                    + f"{ylabel} = {y} ({y0})\n"
                    + (f"ID = {ID}\n" if ID is not None else "")
                    + (
                        f"{self.m.data_specs.parameter} = {val}"
                        if val is not None
                        else ""
                    )
                )
            else:
                lon, lat = self.m._transf_plot_to_lonlat.transform(*pos)
                x, y = [
                    np.format_float_positional(i, trim="-", precision=pos_precision)
                    for i in pos
                ]
                lon, lat = [
                    np.format_float_positional(i, trim="-", precision=pos_precision)
                    for i in (lon, lat)
                ]

                printstr = (
                    f"x = {x}\n" + f"y = {y}\n" + f"lon = {lon}\n" + f"lat = {lat}"
                )
        elif isinstance(text, str):
            printstr = text
        elif callable(text):
            printstr = text(self.m, ID, val, pos, ind)

        if printstr is not None:
            # create a new annotation
            styledict = dict(
                xytext=(20, 20),
                textcoords="offset points",
                bbox=dict(boxstyle="round", fc="w"),
                arrowprops=dict(arrowstyle="->"),
            )

            styledict.update(**kwargs)
            annotation = ax.annotate("", xy=pos, **styledict)

            if not permanent:
                # make the annotation temporary
                self._temporary_artists.append(annotation)
            else:
                if not hasattr(self, "permanent_annotations"):
                    self.permanent_annotations = [annotation]
                else:
                    self.permanent_annotations.append(annotation)

            if layer is not None:
                self.m.BM.add_artist(annotation, layer=layer)

            annotation.set_visible(True)
            annotation.xy = pos
            annotation.set_text(printstr)

    def clear_annotations(self, **kwargs):
        """
        Remove all temporary and permanent annotations from the plot
        """
        if hasattr(self, "permanent_annotations"):
            while len(self.permanent_annotations) > 0:
                ann = self.permanent_annotations.pop(0)
                self.m.BM.remove_artist(ann)
                ann.remove()

    def _annotate_cleanup(self):
        self.clear_annotations()

    def get_values(self, **kwargs):
        """
        Successively collect return-values in a dict accessible via
        `m.cb.[click/pick].get.picked_vals`.

        The structure of the picked_vals dict is as follows:
        (lists are appended as you click on more pixels)

            >>> dict(
            >>>     pos=[... center-position tuples in plot_crs ...],
            >>>     ID=[... the corresponding IDs in the dataframe...],
            >>>     val=[... the corresponding values ...]
            >>> )

        removing the callback will also remove the associated value-dictionary!
        """
        ID, pos, val, ind, picker_name = self._popargs(kwargs)

        if not hasattr(self, "picked_vals"):
            self.picked_vals = defaultdict(list)

        for key, val in zip(["pos", "ID", "val"], [pos, ID, val]):
            self.picked_vals[key].append(val)

    def _get_values_cleanup(self):
        # cleanup method for get_values callback
        if hasattr(self, "picked_vals"):
            del self.picked_vals

    def mark(
        self,
        radius=None,
        radius_crs="in",
        shape=None,
        buffer=1,
        permanent=True,
        n=20,
        layer=10,
        **kwargs,
    ):
        """
        Draw markers at the location where the map was clicked.

        If permanent = True, the generated annotations are stored in a list
        which is accessible via `m.cb.[click/pick].get.permanent_markers`

        Removing the callback will remove ALL markers that have been
        added to the map.

        Parameters
        ----------
        radius : float, string or None, optional
            If float: The radius of the marker in units of the "radius_crs".
            If "pixel" the pixel dimensions of the clicked pixel are used
            If None: The radius of the data used for plotting (if available),
                     otherwise 1/10 of the width and height
            The default is None.
        radius_crs : any
            The crs specification in which the radius is provided.
            The default is "in" (e.g. the crs of the input-data).
            (only relevant if radius is NOT specified as "pixel")

        shape : str, optional
            Indicator which shape to draw. Currently supported shapes are:
                - ellipses
                - rectangles
                - geod_circles

            The default is None which defaults to the used shape for plotting
            if possible and else "ellipses".
        buffer : float, optional
            A factor to scale the size of the shape. The default is 1.
        permanent : bool, optional
            Indicator if the shapes should be permanent (True) or removed
            on each new double-click (False)
        n : int
            The number of points to calculate for the shape.
            The default is 20.
        layer : int
            The layer-level on which to draw the artist.
            (First layer 0 is drawn, then layer 1 on top then layer 2 etc...)
            The default is 10.
        **kwargs :
            kwargs passed to the matplotlib patch.
            (e.g. `facecolor`, `edgecolor`, `linewidth`, `alpha` etc.)
        """
        possible_shapes = ["ellipses", "rectangles", "geod_circles"]

        if shape is None:
            shape = (
                self.m.shape.name
                if (self.m.shape.name in possible_shapes)
                else "ellipses"
            )
        else:
            assert (
                shape in possible_shapes
            ), f"'{shape}' is not a valid marker-shape... use one of {possible_shapes}"

        if radius is None:
            if self.m.figure.coll is not None:
                radius = "pixel"
            else:
                # make a dot with 1/20 of the widht & height of the figure
                t = self.m.figure.ax.bbox.transformed(
                    self.m.figure.ax.transData.inverted()
                )
                radius = (t.width / 10.0, t.height / 10.0)

        ID, pos, val, ind, picker_name = self._popargs(kwargs)

        if ID is not None and picker_name == "default":
            if ind is None:
                # ind = self.m.data.index.get_loc(ID)
                ind = np.flatnonzero(np.isin(self.m._props["ids"], ID))
            pos = (self.m._props["xorig"][ind], self.m._props["yorig"][ind])
            pos_crs = "in"
        else:
            pos_crs = "out"

        if radius == "pixel":
            pixelQ = True
            if not hasattr(self.m.shape, "radius"):
                print(
                    "EOmaps: You cannot attach markers with 'radius=pixel'"
                    + f"if the shape {self.m.shape.name} is used for plotting!"
                )
                return
            radius = self.m.shape.radius
        else:
            pixelQ = False

        # get manually specified radius (e.g. if radius != "estimate")
        if isinstance(radius, (list, tuple)):
            radius = [i * buffer for i in radius]
        elif isinstance(radius, (int, float)):
            radius = radius * buffer

        if self.m.shape.name == "geod_circles":
            if shape != "geod_circles" and pixelQ:
                warnings.warn(
                    "EOmaps: Only `geod_circles` markers are possible"
                    + "if you use radius='pixel' after plotting `geod_circles`"
                    + "Specify an explicit radius to use other shapes!"
                )
                shape = "geod_circles"

        elif self.m.shape.name in ["voroni_diagram", "delaunay_triangulation"]:
            assert radius != "pixel", (
                "EOmaps: Using `radius='pixel' is not possible"
                + "if the plot-shape was '{self.m.shape.name}'."
            )

        if shape == "geod_circles":
            shp = self.m.set_shape._get("geod_circles", radius=radius, n=n)
        elif shape == "ellipses":
            shp = self.m.set_shape._get(
                "ellipses", radius=radius, radius_crs=radius_crs, n=n
            )
        elif shape == "rectangles":
            shp = self.m.set_shape._get(
                "rectangles", radius=radius, radius_crs=radius_crs, mesh=False, n=n
            )
        else:
            raise TypeError(f"EOmaps: '{shape}' is not a valid marker-shape")

        coll = shp.get_coll(
            np.atleast_1d(pos[0]), np.atleast_1d(pos[1]), pos_crs, **kwargs
        )

        if permanent and not hasattr(self, "permanent_markers"):
            self.permanent_markers = []

        marker = self.m.figure.ax.add_collection(coll)

        if permanent:
            self.permanent_markers.append(marker)
        else:
            self._temporary_artists.append(marker)

        if layer is not None:
            self.m.BM.add_artist(marker, layer)

        return marker

    def clear_markers(self, **kwargs):
        """
        Remove all temporary and permanent annotations from the plot.
        """
        if hasattr(self, "permanent_markers"):
            while len(self.permanent_markers) > 0:
                marker = self.permanent_markers.pop(0)
                self.m.BM.remove_artist(marker)
                marker.remove()
            del self.permanent_markers

    def _mark_cleanup(self):
        self.clear_markers()

    def peek_layer(self, layer=1, how="left", **kwargs):
        """
        Swipe between data- or WebMap layers or peek a layers through a rectangle.

        Parameters
        ----------
        layer : int
            The layer-number you want to peek at.
            (You must draw something on the layer first!)

                >>> m.plot_map(layer=1)

        pos : TYPE
            DESCRIPTION.
        how : str , float or tuple, optional
            the peek-method.
                - "left" (→), "right" (←), "top" (↓), "bottom" (↑):
                  swipe the layer at the mouse-position.
                - if float, peek a square at the mouse-position, specified as
                  percentage of the axis-width (0-1)
                - (width, height) peek a rectangle at the mouse-position, specified
                  as percentage of the axis-size (0-1)

            The default is "left".
        **kwargs :
            additional kwargs passed to a rectangle-marker.
            the default is `(fc="none", ec="k", lw=1)`

        """
        ID, pos, val, ind, picker_name = self._popargs(kwargs)

        ax = self.m.figure.ax

        # default boundary args
        args = dict(fc="none", ec="k", lw=1)
        args.update(kwargs)

        if isinstance(how, str):
            # base transformations on transData to ensure correct treatment
            # for shared axes
            if how == "left":
                x, _ = ax.transData.transform((pos[0], pos[1]))
                x0, y0 = ax.transAxes.transform((0, 0))
                blitw = x - x0
                blith = ax.bbox.height
            elif how == "right":
                x0, _ = ax.transData.transform((pos[0], pos[1]))
                xa0, y0 = ax.transAxes.transform((0, 0))
                blitw = ax.bbox.width - x0 + xa0
                blith = ax.bbox.height
            elif how == "top":
                x0, ya0 = ax.transAxes.transform((0, 0))
                _, y0 = ax.transData.transform((pos[0], pos[1]))

                blitw = ax.bbox.width
                blith = ax.bbox.height - y0 + ya0
            elif how == "bottom":
                x0, y0 = ax.transAxes.transform((0, 0))
                _, y = ax.transData.transform((pos[0], pos[1]))

                blitw = ax.bbox.width
                blith = y - y0
            else:
                raise TypeError(f"EOmaps: '{how}' is not a valid input for 'how'")

            x0m, y0m = ax.transData.inverted().transform((x0, y0))
            x1m, y1m = ax.transData.inverted().transform((x0 + blitw, y0 + blith))
            w, h = abs(x1m - x0m), abs(y1m - y0m)

            self.mark(
                pos=((x0m + x1m) / 2, (y0m + y1m) / 2),
                radius_crs="out",
                layer=1,
                shape="rectangles",
                radius=(w / 2, h / 2),
                permanent=False,
                **args,
            )

        elif isinstance(how, (float, list, tuple)):
            if isinstance(how, float):
                w0, h0 = self.m.figure.ax.transAxes.transform((0, 0))
                w1, h1 = self.m.figure.ax.transAxes.transform((how, how))
                blitw, blith = (w1 - w0, w1 - w0)
            else:
                w0, h0 = self.m.figure.ax.transAxes.transform((0, 0))
                w1, h1 = self.m.figure.ax.transAxes.transform(how)
                blitw, blith = (w1 - w0, h1 - h0)

            x0, y0 = ax.transData.transform((pos[0], pos[1]))
            x0, y0 = x0 - blitw / 2.0, y0 - blith / 2

            # make sure that we don't blit outside the axis
            bbox = self.m.figure.ax.bbox
            x1 = x0 + blitw
            y1 = y0 + blith
            if x0 < bbox.x0:
                dx = bbox.x0 - x0
                x0 = bbox.x0
                blitw = blitw - dx * 2
            if x1 > bbox.x1:
                dx = x1 - bbox.x1
                x0 = x0 + dx
                blitw = blitw - dx * 2
            if y0 < bbox.y0:
                dy = bbox.y0 - y0
                y0 = bbox.y0
                blith = blith - dy * 2
            if y1 > bbox.y1:
                dy = y1 - bbox.y1
                y0 = y0 + dy
                blith = blith - dy * 2

            x0m, y0m = ax.transData.inverted().transform(
                (x0 - blitw / 2.0, y0 - blith / 2)
            )
            x1m, y1m = ax.transData.inverted().transform(
                (x0 + blitw / 2.0, y0 + blith / 2)
            )
            w, h = abs(x1m - x0m), abs(y1m - y0m)

            self.mark(
                pos=pos,
                radius_crs="out",
                layer=1,
                shape="rectangles",
                radius=(w / 2, h / 2),
                permanent=False,
                **args,
            )
        else:
            raise TypeError(f"EOmaps: {how} is not a valid peek method!")

        self.m.BM._after_restore_actions.append(
            self.m.BM._get_restore_bg_action(layer, (x0, y0, blitw, blith))
        )

    def load(
        self, database=None, load_method="load_fit", load_multiple=False, **kwargs
    ):
        """
        Load objects from a given database using the ID of the picked pixel.

        The returned object(s) are accessible via `m.cb.pick.get.picked_object`.

        Parameters
        ----------
        database : any
            The database object to use for loading the object
        load_method : str or callable
            If str: The name of the method to use for loading objects from the provided
                    database (the call-signature used is `database.load_method(ID)`)
            If callable: A callable that will be executed on the database with the
                         following call-signature: `load_method(database, ID)`
        load_multiple : bool
            True: A single-object is returned, replacing `m.cb.picked_object` on each pick.
            False: A list of objects is returned that is extended with each pick.
        """
        ID, pos, val, ind, picker_name = self._popargs(kwargs)

        assert database is not None, "you must provide a database object!"

        try:
            if isinstance(load_method, str):
                assert hasattr(
                    database, load_method
                ), "The provided database has no method '{load_method}'"
                pick = getattr(database, load_method)(ID)
            elif callable(load_method):
                pick = load_method(database, ID)
            else:
                raise TypeError("load_method must be a string or a callable!")
        except Exception:
            print(f"could not load object with ID:  '{ID}' from {database}")

        if load_multiple is True:
            self.picked_object = getattr(self, "picked_object", list()) + [pick]
        else:
            self.picked_object = pick

    def _load_cleanup(self):
        if hasattr(self, "picked_object"):
            del self.picked_object

    def plot(
        self,
        x_index="pos",
        precision=4,
        **kwargs,
    ):
        """
        Generate a dynamically updated plot showing the values of the picked pixels.

            - x-axis represents pixel-coordinates (or IDs)
            - y-axis represents pixel-values

        a new figure is started whenever the figure is closed!

        Parameters
        ----------
        x_index : str
            Indicator how the x-axis is labelled

                - pos : The position of the pixel in plot-coordinates
                - ID  : The index of the pixel in the data
        precision : int
            The floating-point precision of the coordinates printed to the
            x-axis if `x_index="pos"` is used.
            The default is 4.
        **kwargs :
            kwargs forwarded to the call to `plt.plot([...], [...], **kwargs)`.

        """
        ID, pos, val, ind, picker_name = self._popargs(kwargs)

        style = dict(marker=".")
        style.update(**kwargs)

        if not hasattr(self, "_pick_f"):
            self._pick_f, self._pick_ax = plt.subplots()
            self._pick_ax.tick_params(axis="x", rotation=90)
            self._pick_ax.set_ylabel(self.m.data_specs.parameter)

            # call the cleanup function if the figure is closed
            def on_close(event):
                self._plot_cleanup()

            self._pick_f.canvas.mpl_connect("close_event", on_close)

        _pick_xlabel = self.m.data_specs.xcoord
        _pick_ylabel = self.m.data_specs.ycoord

        if x_index == "pos":
            x, y = [
                np.format_float_positional(i, trim="-", precision=precision)
                for i in pos
            ]
            xindex = f"{_pick_xlabel}={x}\n{_pick_ylabel}={y}"
        elif x_index == "ID":
            xindex = str(ID)

        if not hasattr(self, "_pick_l"):
            (self._pick_l,) = self._pick_ax.plot([xindex], [val], **style)
        else:
            self._pick_l.set_xdata(list(self._pick_l.get_xdata()) + [xindex])
            self._pick_l.set_ydata(list(self._pick_l.get_ydata()) + [val])

        # self._pick_ax.autoscale()
        self._pick_ax.relim()
        self._pick_ax.autoscale_view(True, True, True)

        self._pick_f.canvas.draw()
        self._pick_f.tight_layout()

    def _plot_cleanup(self):
        # cleanup method for plot callback
        if hasattr(self, "_pick_f"):
            del self._pick_f
        if hasattr(self, "_pick_ax"):
            del self._pick_ax
        if hasattr(self, "_pick_l"):
            del self._pick_l


class pick_callbacks(_click_callbacks):
    """
    A collection of callback functions that are executed when clicking on
    a pixel of the plotted collection.
    """

    _cb_list = [
        "get_values",
        "load",
        "print_to_console",
        "annotate",
        "mark",
        "plot",
        "clear_annotations",
        "clear_markers",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class click_callbacks(_click_callbacks):
    """
    A collection of callback functions that are executed when clicking anywhere
    on the map.
    """

    _cb_list = [
        "get_values",
        "print_to_console",
        "annotate",
        "mark",
        "peek_layer",
        "clear_annotations",
        "clear_markers",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class keypress_callbacks:
    """
    A collection of callback functions that are executed when the assigned
    key is pressed.
    """

    _cb_list = [
        "switch_layer",
    ]

    def __init__(self, m, temp_artists):
        self._temporary_artists = temp_artists
        self._m = m

    def switch_layer(self, layer=1, key="1"):
        """
        Change the default layer of the map.

        Use the keyboard events to set the default layer (e.g. the visible layer)
        displayed in the plot.

        Parameters
        ----------
        layer : int, optional
            The layer to use. The default is 1.
        key : str, optional
            The key to use. Modifiers are indicated with a +, e.g. "alt+x".
            The default is "1".
        """
        self._m.BM.bg_layer = layer
        self._m.BM.fetch_bg()


class dynamic_callbacks:
    """
    Callbacks that are triggered by events in the map (e.g. draw, zoom, etc.).

    Note
    ----

    This is still an experimental feature!


    A collection of callback functions that are executed on triggered events.
    (e.g. draw, zoom etc.)
    """

    def __init__(self, m):
        self.m = m

    def indicate_extent(self, m=None, **kwargs):
        """
        Indicate the plot-extent of another maps object.

        NOTE: This feature is not fully mature... some projections might not work

        Parameters
        ----------
        m : eomaps.Maps, optional
            The maps-object whose extent should be indicated.
            The default is None.
        **kwargs :
            kwargs passed to the projected rectangle patch that is used to
            indicate the plot-extent. The default is {fc="none", ec="r", n=100}
            (see "m.cb.click.attach.mark()" for details on possible kwargs)

        """
        self._extent_marker = None
        self._last_extent = (1, 2, 1, 2)

        def indicate(event):
            if event.inaxes != m.figure.ax:
                return

            try:

                last_extent = m.figure.ax.get_extent()
                if self._last_extent == last_extent:
                    return

                self._last_extent = last_extent

                if self._extent_marker is not None:
                    self.m.BM.remove_artist(self._extent_marker)
                    self._extent_marker.remove()
                    self._extent_marker = None

                x0, x1, y0, y1 = self._last_extent

                w, h = (abs(x0 - x1) / 2, abs(y0 - y1) / 2)

                args = dict(n=100, fc="none", ec="r")
                args.update(kwargs)

                self._extent_marker = self.m.add_marker(
                    xy=((x0 + x1) / 2, (y0 + y1) / 2),
                    xy_crs=m.crs_plot,
                    layer=999,
                    shape="rectangles",
                    radius=(w, h),
                    radius_crs=m.crs_plot,
                    permanent=True,
                    **args,
                )
            except:
                warnings.warn("EOmaps: Extent could not be indicated.")

        cid = f"_indicate_cid_{id(m)}"
        if not hasattr(self, cid):
            setattr(
                self,
                cid,
                m.figure.f.canvas.mpl_connect("button_release_event", indicate),
            )

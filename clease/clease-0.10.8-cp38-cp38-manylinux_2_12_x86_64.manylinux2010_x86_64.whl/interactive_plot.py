# pylint: disable=import-outside-toplevel
from tkinter import TclError
from matplotlib import pyplot as plt
from ase.db import connect
from ase.gui.gui import GUI
from ase.gui.images import Images


class InteractivePlot:
    """Class for creating an interactive plot with annotations

    Parameters:

    fig: Figure instance
        Instance of the figure object visualizing the data

    ax: Axes instance
        Instance of the axes object containing the lines

    lines: Array of Line objects that annotations apply to

    annotations: Nested list with annotations
        Each list contains one annotation for each (x, y) pair on that
        line
    """

    def __init__(self, fig, ax, lines, annotations):
        self.fig = fig
        self.ax = ax
        self.lines = lines
        self.annotations = annotations
        self.active_annot = ax.annotate("",
                                        xy=(0, 0),
                                        xytext=(-20, 20),
                                        textcoords="offset points",
                                        bbox=dict(boxstyle="round", fc="w"),
                                        arrowprops=dict(arrowstyle="->"))
        self.active_annot.set_visible(False)
        self.active_line_index = 0

        for i, line in enumerate(self.lines):
            x, _ = line.get_data()
            if len(x) != len(self.annotations[i]):
                msg = f"Annotations for line {i} "
                msg += f"has length {len(self.annotations[i])} "
                msg += f"but there are {len(x)} data points!"
                raise ValueError(msg)

        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)
        plt.show()

    def _update_annotation(self, ind):
        """Update the annotation shown."""
        try:
            line = self.lines[self.active_line_index]
            x, y = line.get_data()
            self.active_annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
            anot = self.annotations[self.active_line_index]
            text = anot[ind["ind"][0]]
            self.active_annot.set_text(text)
        except IndexError:
            pass

    def hover(self, event):
        """React on a hover event."""
        vis = self.active_annot.get_visible()
        if event.inaxes == self.ax:
            cont = False
            for i, line in enumerate(self.lines):
                cont, ind = line.contains(event)
                if cont:
                    self.active_line_index = i
                    break

            if cont:
                self._update_annotation(ind)
                self.active_annot.set_visible(True)
                self.fig.canvas.draw_idle()
            else:
                if vis:
                    self.active_annot.set_visible(False)
                    self.fig.canvas.draw_idle()


class ShowStructureOnClick(InteractivePlot):

    def __init__(self, fig, ax, lines, names, db_name):
        self.db_name = db_name
        self.active_images = Images()
        # Uninitilized GUI. We don't create this until we click,
        # since we otherwise just open a new empty GUI window.
        self.gui = None
        fig.canvas.mpl_connect("button_press_event", self.on_click)
        super().__init__(fig, ax, lines, names)

    def on_click(self, event):

        if event.inaxes != self.ax:
            return

        if event.button == 1:
            if self.gui is not None:
                # Try to close the existing GUI, if we already opened one
                try:
                    self.gui.exit()
                except TclError:
                    pass
            db = connect(self.db_name)
            atoms = []

            # Find the index of the point
            for i, line in enumerate(self.lines):
                cont, ind = line.contains(event)
                if cont:
                    self.active_line_index = i
                    break

            name = self.annotations[self.active_line_index][ind["ind"][0]]
            for row in db.select(name=name):
                atoms.append(row.toatoms())
            self.active_images.initialize(atoms)
            # Create a new GUI instance and run it
            self.gui = GUI(self.active_images)
            self.gui.run()

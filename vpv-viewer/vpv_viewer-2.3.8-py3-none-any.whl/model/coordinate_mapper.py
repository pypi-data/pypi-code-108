from vpv.common import Orientation
import numpy as np
from vpv.display.slice_view_widget import SliceWidget

flip_to_axial_order = {
    # The order of the source dimensions after mapping to axial space
    # For example [2, 1, 0] reverses the dimension ordering as we are using

    Orientation.axial:    [0, 1, 2],  # keep same
    Orientation.coronal:  [0, 2, 1],
    Orientation.sagittal: [1, 2, 0]
}

flip_from_axial_order = {
    Orientation.axial:    [0, 1, 2],  # Keep same
    Orientation.coronal:  [0, 2, 1],
    Orientation.sagittal: [2, 0, 1]
}


class Coordinate_mapper(object):
    """Map coordinates between views and volumes
    """
    def __init__(self, views: dict, saved_flip_info: dict):
        self.views = views  # Get a reference to the views dict that contains the slice view widgets
        self.flip_info = saved_flip_info

    def view_to_volume(self, x: int, y: int, z: int, src_ori: Orientation, dims: list, from_saved=False) -> tuple:
        """
        Given coordinates from a slice view, convert to actual coordinates in the correct volume space
        This is required as we do some inversion of the order of slices as they come off the volumes to show
        a view that the IMPC annotators like.

        Currently not working if there are no Slice views that are in axial view

        Parameters
        ----------
        x: int
        y: int
        z: int
        src_ori: Orientation
            The orientation of the source view
        dims: list
            dimensions of source volume xyz
        from_saved: bool


        Returns
        -------
        (x, y, z)

        Notes
        -----

        This maps the view coordinates from any view to the normal axial view. Then adds correction for the inverted
        slice ordering

        Problem: If the impc_vie is active the view_to_view() inverts x when mapping between
        axial and the other views so that cross hairs work. this breaks the mouse
        position labels

        """

        if not from_saved:  # If from saved list we don't need to do any flipping on the points
            # Flip the dimensions so thay match the view

            dims_order = flip_from_axial_order[src_ori]
            new_dims = [j for _, j in sorted(zip(dims_order, dims), key=lambda pair: pair[0])]


            if self.flip_info[src_ori.name]['y']:
                y = new_dims[1] - y

            if not self.flip_info[src_ori.name]['x']:  # 280319. x is flipped by default in every view for RAS
                x = new_dims[0] - x

            if self.flip_info[src_ori.name]['z']:
                z = new_dims[2] - z

        order = flip_to_axial_order[src_ori]
        xa, ya, za = [j for _, j in sorted(zip(order, [x, y, z]), key=lambda pair: pair[0])]

        return xa, ya, za

    def view_to_view(self, x, y, z, src_ori, dest_ori, dims, from_saved=False):
        """
        Given a coordinate on one view with a given orientation as well as horizontal flip and slice ordering status,
        map to another view with a given orientation , flip and ordering.
        Parameters
        ----------
        x: int
            the x position in the view
        y: int
            the y position in the view
        z: int
            the slice index
        src_view: [SliceWidget, None]
            The slice view widget that the corrdinate is mapped from. If none assum nornal volume space (z == axial)
        dest_view: SliceWidget
            The slice view widget to map the coordinates to
        rev: bool
            whether to return the inverted point (len(dimension) - point)
        Returns
        -------
        tuple
            (x,y,idx)

        """
        # Get the points in volume space
        axial_space_points = self.view_to_volume(x, y, z, src_ori, dims, from_saved)

        # And map to the destination space

        order = flip_from_axial_order[dest_ori]
        dest_points = [j for _, j in sorted(zip(order, axial_space_points), key=lambda pair: pair[0])]

        dims_order = flip_from_axial_order[dest_ori]
        new_dims = [j for _, j in sorted(zip(dims_order, dims), key=lambda pair: pair[0])]

        if self.flip_info[dest_ori.name]['y']:
            dest_points[1] = new_dims[1] - dest_points[1]

        if not self.flip_info[dest_ori.name]['x']:
            dest_points[0] = new_dims[0] - dest_points[0]

        if self.flip_info[dest_ori.name]['z']:
            dest_points[2] = new_dims[2] - dest_points[2]

        return dest_points

    def roi_to_view(self, xx, yy, zz):

        """
        Given an roi is volume coordinates (z == axial), map the roi to other orthogonal views
        Parameters
        ----------
        xx: tuple
        yy: tuple
        zz: tuple

        Returns
        -------
        tuple
            Mapped coordinates ((x,x), (y,y), (z,z)
        """
        z = [int(i) for i in zz]
        y = [int(i) for i in yy]
        x = [int(i) for i in xx]

        for dest_view in self.views.values():
            # First map the annotation marker between views
            dest_dims = dest_view.main_volume.shape_xyz()

            points_1 = self.view_to_view(x[0], y[0], z[0], Orientation.axial, dest_view.orientation,
                                         dest_dims, from_saved=True)

            points_2 = self.view_to_view(x[1], y[1], z[1], Orientation.axial, dest_view.orientation,
                                         dest_dims, from_saved=True)

            midslice = int(np.mean([points_1[2], points_2[2]]))

            w = abs(points_1[0] - points_2[0])
            h = abs(points_1[1] - points_2[1])
            dest_view.set_slice(midslice)

            # we need to set the start of the roi as the lowest valued x and y. These change if flips occur
            new_x = min((points_1[0], points_2[0]))
            new_y = min((points_1[1], points_2[1]))
            dest_view.set_roi(new_x, new_y, w, h)


# def convert_volume(vol, direction):
#     return vol
#     if direction == (1, 0, 0, 0, 1, 0, 0, 0, 1): # LPS
#         vol = vol[:, ::-1, :]
#     if direction == (-1, 0, 0, 0, -1, 0, 0, 0, 1): # RAS
#         print("ras?")
#         vol = vol
#         # vol = vol[:, :, ::-1]
#
#     return vol

"""
Library of SPAM functions for measuring global descriptors
Copyright (C) 2020 SPAM Contributors

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option)
any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import numpy
import spam.helpers

def volume(segmented, phase=1, aspectRatio=(1.0, 1.0, 1.0), specific=False, ROI=None):
    """
    Computes the (specific) volume of a given phase for a certain *Region Of
    Interest*.

    Parameters
    -----------
        segmented: array of integers
            Array where integers represent the phases.
            The value 0 is stricly reserved for **not** Region Of Interest.

        phase: integer, default=1
            The phase for which the fraction volume is computed.
            The phase should be greater than 0 if ROI is used.

        aspectRatio: tuple of floats, default=(1.0, 1.0, 1.0)
            Length between two nodes in every direction e.g. size of a cell.
            The length of the tuple is the same as the spatial dimension.

        specific: boolean, default=False
            Returns the specific volume if True.

        ROI: array of boolean, default=None
            If not None, boolean array which represents the Region Of Interest.
            Segmented will be 0 where ROI is False.

    Returns
    --------
        float
            The (specific) volume of the phase.
    """

    if phase == 0:
        print("spam.measurements.globalDescriptors.volume: phase={}. Should be > 0.".format(phase))

    if ROI is not None:
        segmented = segmented * ROI

    voxelSize = 1.0
    for a in aspectRatio:
        voxelSize *= a

    if specific:
        return float((segmented == phase).sum()) / float(segmented.size)
    else:
        return voxelSize * float((segmented == phase).sum())


def eulerCharacteristic(segmented, phase=1, ROI=None, verbose=False):
    """
    Compute the Euler Characteristic of a given phase by counting
    n-dimensionnal topological features using the formula:

    .. code-block:: text

        1D: X = #{ Vertices } - #{ Edges }
        2D: X = #{ Vertices } - #{ Edges } + #{ Faces }
        3D: X = #{ Vertices } - #{ Edges } + #{ Faces } - #{ Polyedra }

    This function as been implemented using a optimized algorithm using rolled
    views with unsymetrical structuring elements to count, thus avoiding
    n nested loops.

    Parameters
    -----------
        segmented: array of integers
            Array where integers represent the phases.
            The value 0 is stricly reserved for **not** Region Of Interest.

        phase: integer, default=1
            The phase for which the fraction volume is computed.
            The phase should be greater than 0 if ROI is used.

        ROI: array of boolean, default=None
            If not None, boolean array which represents the Region Of Interest.
            Segmented will be 0 where ROI is False.

        verbose: boolean, default=False,
            Verbose mode.

    Returns
    --------
        int:
            The Euler Characteristic
    """

    if phase == 0:
        print("spam.measurements.globalDescriptors.eulerCharacteristic: phase={}. Should be > 0.".format(phase))

    # get dimension
    dim = len(segmented.shape)

    if ROI is not None:
        segmented = segmented * ROI

    if dim == 1:  # DIMENSION 1

        # Count the vertices
        counter = (segmented == phase).astype('<u1')
        V = counter.sum()

        # Count the edges
        s_x = numpy.roll(counter, 1)
        s_x[0] = 0
        counter_x = numpy.logical_and(counter, s_x)
        E = counter_x.sum()

        # Euler characteristic
        X = int(V - E)

        if verbose:
            print('Compute Euler Characteristic in 1D')
            print('* V = #(vertices) = (+) {}'.format(V))
            print('* E = #(edges)    = (-) {}'.format(E))
            print("* X = V - E       = {}".format(X))

    elif dim == 2:  # DIMENSION 2

        # Count the vertices
        counter = (segmented == phase).astype('<u1')
        V = counter.sum()

        # Count the edges
        s_x = numpy.roll(counter, 1, axis=0)
        s_x[0, :] = 0
        counter_x = numpy.logical_and(counter, s_x)
        s_y = numpy.roll(counter, 1, axis=1)
        s_y[:, 0] = 0
        counter_y = numpy.logical_and(counter, s_y)
        E = counter_x.sum() + counter_y.sum()

        # Count the faces
        s_xy = numpy.roll(s_x, 1, axis=1)
        s_xy[:, 0] = 0
        f_xy = numpy.logical_and(numpy.logical_and(counter_x, s_xy), counter_y)
        F = f_xy.sum()

        # Euler characteristic
        X = int(V - E + F)

        if verbose:
            print('Compute Euler Characteristic in 2D')
            print('* V = #(vertices) = (+) {}'.format(V))
            print('* E = #(edges)    = (-) {}'.format(E))
            print('* F = #(faces)    = (+) {}'.format(F))
            print("* X = V - E + F   = {}".format(X))

    elif dim == 3:  # DIMENSION 3

        # Count the vertices
        counter = (segmented == phase).astype('<u1')
        V = counter.sum()

        # Count the edges
        s_x = spam.helpers.singleShift(counter, 1, 0, sub=0)
        counter_x = numpy.logical_and(counter, s_x)
        s_y = spam.helpers.singleShift(counter, 1, 1, sub=0)
        counter_y = numpy.logical_and(counter, s_y)
        s_z = spam.helpers.singleShift(counter, 1, 2, sub=0)
        counter_z = numpy.logical_and(counter, s_z)
        E = counter_x.sum() + counter_y.sum() + counter_z.sum()

        # Count the faces
        s_xy = spam.helpers.singleShift(s_x, 1, 1, sub=0)
        f_xy = numpy.logical_and(numpy.logical_and(counter_x, s_xy), counter_y)
        s_xz = spam.helpers.singleShift(s_x, 1, 2, sub=0)
        f_xz = numpy.logical_and(numpy.logical_and(counter_x, s_xz), counter_z)
        s_yz = spam.helpers.singleShift(s_y, 1, 2, sub=0)
        f_yz = numpy.logical_and(numpy.logical_and(counter_y, s_yz), counter_z)
        F = f_xy.sum() + f_xz.sum() + f_yz.sum()

        # Count the polyhedra
        s_xyz = spam.helpers.singleShift(s_xy, 1, 2, sub=0)
        f_xyz = numpy.logical_and(numpy.logical_and(f_xy, f_xz), f_yz)
        p_xyz = numpy.logical_and(f_xyz, s_xyz)
        P = p_xyz.sum()

        # Euler characteristic
        X = int(V - E + F - P)

        if verbose:
            print('* V = #(vertices) = (+) {}'.format(V))
            print('* E = #(edges)    = (-) {}'.format(E))
            print('* F = #(faces)    = (+) {}'.format(F))
            print('* P = #(polyedra) = (-) {}'.format(P))
            print("* X = V - E + F - P = {}".format(X))

    return X


def surfaceArea(field, level=0.0, aspectRatio=(1.0, 1.0, 1.0)):
    """
    Computes the surface area of a continuous field over a given level set.

    This function is based on a marching cubes algorithm of skimage.

    Parameters
    -----------
        field: array of floats
            Array where some level sets represent the interface between phases.

        level: float, default=0.0
            The level set.
            See ``skimage.measure.marching_cubes``.
            Contour value to search for isosurfaces in volume.
            If not given or None, the average of the min and max of vol is used.

        aspectRatio: length 3 tuple of floats, default=(1.0, 1.0, 1.0)
            Length between two nodes in every direction e.g. size of a cell.
            It corresponds to ``spacing`` in ``skimage.measure.marching_cubes``.

    Returns
    --------
        float:
            The surface area.
    """
    import skimage.measure

    # add a margin of 3 voxels
    margedField = numpy.zeros([n + 6 for n in field.shape])
    margedField[:, :, :] = field.min()
    margedField[3:-3, 3:-3, 3:-3] = field

    # http://scikit-image.org/docs/dev/api/skimage.measure.html?highlight=mesh_surface_area#skimage.measure.marching_cubes
    verts, faces, _, _ = skimage.measure.marching_cubes(margedField, level=level, spacing=aspectRatio)

    return skimage.measure.mesh_surface_area(verts, faces)

# def totalCurvature(field, level=0.0, aspectRatio=(1.0, 1.0, 1.0)):
#     """
#     Computes the total curvature of a continuous field over a given level set.
#
#     This function is based on a marching cubes algorithm of skimage.
#
#     Parameters
#     -----------
#         field: array of floats
#             Array where some level sets represent the interface between phases.
#         level: float, default=0.0
#             The level set.
#             See ``skimage.measure.marching_cubes``.
#             Contour value to search for isosurfaces in volume.
#             If not given or None, the average of the min and max of vol is used.
#         aspectRatio: length 3 tuple of floats, default=(1.0, 1.0, 1.0)
#             Length between two nodes in every direction e.g. size of a cell.
#             It corresponds to ``spacing`` in ``skimage.measure.marching_cubes``.
#
#     Returns
#     --------
#         float:
#             The total curvature.
#     """
#
#     # specific function
#     def faceNormal(tri3d):
#         f_normal=numpy.zeros((tri3d.shape[0],3))
#         p1=tri3d[:,0,:]-tri3d[:,1,:]
#         p2=tri3d[:,0,:]-tri3d[:,2,:]
#         n=numpy.cross(p1, p2)
#         norm=LA.norm(n,axis=1)
#         f_normal[:,0]=n[:,0]/norm[:]
#         f_normal[:,1]=n[:,1]/norm[:]
#         f_normal[:,2]=n[:,2]/norm[:]
#
#         return f_normal
#
#     # import
#     import skimage.measure
#     from numpy import linalg as LA
#     import math
#
#     # marching cubes
#
#     # add a margin of 3 voxels
#     margedField = numpy.zeros([n+6 for n in field.shape])
#     margedField[:, :, :] = field.min()
#     margedField[3:-3, 3:-3, 3:-3] = field
#
#     # http://scikit-image.org/docs/dev/api/skimage.measure.html?highlight=mesh_surface_area#skimage.measure.marching_cubes
#     verts, faces, _, _ = skimage.measure.marching_cubes(margedField, level=level, spacing=aspectRatio)
#
#     # compute curvature
#
#     tri3d=verts[faces]
#     nb_tri = tri3d.shape[0]
#     nb_p = verts.shape[0]
#
#     #	freeBoundary  ### not yet
#     f_normal = faceNormal(tri3d)
#
#     ###	vectors, areas, angles, edges for every triangle
#     l_edg=numpy.zeros((nb_tri,3))
#     ang_tri=numpy.zeros((nb_tri,3))
#     f_center=numpy.zeros((nb_tri,3))
#     p=numpy.zeros((nb_tri))
#     v0=numpy.zeros((nb_tri,3))
#     v1=numpy.zeros((nb_tri,3))
#     v2=numpy.zeros((nb_tri,3))
#     area_tri=numpy.zeros((nb_tri))
#     for i in range(nb_tri):
# #        print("Boucle 1: {}/{}".format(i, nb_tri))
#         # points
#         p0=faces[i,0]
#         p1=faces[i,1]
#         p2=faces[i,2]
#
#         # edges (vectors)
#         v0[i,:]=tri3d[i,1,:]-tri3d[i,0,:]
#         v1[i,:]=tri3d[i,2,:]-tri3d[i,1,:]
#         v2[i,:]=tri3d[i,0,:]-tri3d[i,2,:]
#
#         # length of edges
#         l_edg[i,0]= LA.norm(v0[i,:])
#         l_edg[i,1]= LA.norm(v1[i,:])
#         l_edg[i,2]= LA.norm(v2[i,:])
#
#         # angle
#         ang_tri[i,0]=math.acos(numpy.dot(v0[i,:]/l_edg[i,0], -v2[i,:]/l_edg[i,2]))
#         ang_tri[i,1]=math.acos(numpy.dot(-v0[i,:]/l_edg[i,0], v1[i,:]/l_edg[i,1]))
#         ang_tri[i,2]=math.pi-ang_tri[i,0]-ang_tri[i,1]
#
#         # incenter
#         p[i]=numpy.sum(l_edg[i,:])
#         f_center[i,0]=(l_edg[i,0]*tri3d[i,2,0]+l_edg[i,1]*tri3d[i,0,0]+l_edg[i,2]*tri3d[i,1,0])/p[i]
#         f_center[i,1]=(l_edg[i,0]*tri3d[i,2,1]+l_edg[i,1]*tri3d[i,0,1]+l_edg[i,2]*tri3d[i,1,1])/p[i]
#         f_center[i,2]=(l_edg[i,0]*tri3d[i,2,2]+l_edg[i,1]*tri3d[i,0,2]+l_edg[i,2]*tri3d[i,1,2])/p[i]
#
#         # surface
#         area_tri[i]=((numpy.cross(v0[i,:],v1[i,:])**2).sum()**0.5).sum() /2.0
#
#     a_mixed=numpy.zeros((nb_p))
#     alf=numpy.zeros((nb_p))
#     MC =numpy.zeros((nb_p))
#     GC =numpy.zeros((nb_p))
#
#     for i in range(nb_p):
# #        print("Boucle 2: {}/{}".format(i, nb_p))
#         mc_vec=[0,0,0]
#         n_vec=[0,0,0]
#
#         # if find(bndry_edge) ### not yet
#
#         # vertex attachment ? find?
#         find=numpy.where(faces==i)
#         neib_tri=find[0]
#
#         for j in range(len(neib_tri)):
#             neib=neib_tri[j]
#             # sum of angles around point i ==> GC
#             for k in range(3):
#                 if faces[neib,k]==i:
#                     alf[i]=alf[i]+ang_tri[neib,k]
#                     break
#             # mean curvature operator
#             if k==0:
#                 mc_vec=mc_vec+(v0[neib,:]/math.tan(ang_tri[neib,2])-v2[neib,:]/math.tan(ang_tri[neib,1]))
#             elif k==1:
#                 mc_vec=mc_vec+(v1[neib,:]/math.tan(ang_tri[neib,0])-v0[neib,:]/math.tan(ang_tri[neib,2]))
#             elif k==2:
#                 mc_vec=mc_vec+(v2[neib,:]/math.tan(ang_tri[neib,1])-v1[neib,:]/math.tan(ang_tri[neib,0]))
#
#             # A_mixed calculation
#             if (ang_tri[neib,k]>=math.pi/2.0):
#                 a_mixed[i]=a_mixed[i]+area_tri[neib]/2.0
#             else:
#                 if  any(ang >=math.pi/2.0 for ang in ang_tri[neib,:]):
#                     a_mixed[i]=a_mixed[i]+area_tri[neib]/4.0
#                 else:
#                     sum=0
#                     for m in range(3):
#                         if m!=k:
#                             ll=m+1
#                             if ll==3:
#                                 ll=0
#                             sum=sum+(l_edg[neib,ll]**2/math.tan(ang_tri[neib,m]))
#                     a_mixed[i]=a_mixed[i]+sum/8.0
#
#
#             # normal vector at each vertex
#             # weighted average of normal vectors of neighbour triangles
#             wi=1.0/LA.norm( [f_center[neib,0]-verts[i,0],f_center[neib,1]-verts[i,1],f_center[neib,2]-verts[i,2]] )
#             n_vec=n_vec+wi*f_normal[neib,:]
#
#         GC[i]=(2.0*math.pi-alf[i])/a_mixed[i]
#
#         mc_vec=0.25*mc_vec/a_mixed[i]
#         n_vec=n_vec/LA.norm(n_vec)
#
#         # sign of MC
#         if numpy.dot(mc_vec, n_vec)<0:
#             MC[i]=-LA.norm(mc_vec)
#         else:
#             MC[i]=LA.norm(mc_vec)
#
#
#     totalCurvature = numpy.multiply(MC, a_mixed).sum()
#
#     return totalCurvature


def totalCurvature(field, level=0.0, aspectRatio=(1.0, 1.0, 1.0), stepSize=None, getMeshValues=False, fileName=None):
    """
    Computes the total curvature of a continuous field over a given level set.

    This function is based on a marching cubes algorithm of skimage.

    Parameters
    -----------
        field: array of floats
            Array where some level sets represent the interface between phases

        level: float
            The level set
            See ``skimage.measure.marching_cubes``.
            Contour value to search for isosurfaces in volume.
            If None is given, the average of the min and max of vol is used
            Default = 0.0

        aspectRatio: length 3 tuple of floats
            Length between two nodes in every direction `e.g.`, size of a cell.
            It corresponds to ``spacing`` in ``skimage.measure.marching_cubes``
            Default = (1.0, 1.0, 1.0)

        step_size: int
            Step size in voxels
            Larger steps yield faster but coarser results. The result will always be topologically correct though.
            Default = 1

        getMeshValues: boolean
            Return the mean and gauss curvatures and the areas of the mesh vertices
            Default = False

        fileName: string
            Name of the output vtk file
            Only if `getMeshValues` = True
            Default = None

    Returns
    --------
        totalCurvature: float
            If ``getMeshValues`` = True,
            total curvature and a (nx3) array of n vertices
            where 1st column is the mean curvature, 2nd column is the gaussian curvature and 3rd column is the area
    """
    # import
    import skimage.measure
    import spam.measurements.measurementsToolkit as mtk

    # marching cubes

    # add a margin of 3 voxels
    margedField = numpy.zeros([n + 6 for n in field.shape])
    margedField[:, :, :] = field.min()
    margedField[3:-3, 3:-3, 3:-3] = field

    # http://scikit-image.org/docs/dev/api/skimage.measure.html?highlight=mesh_surface_area#skimage.measure.marching_cubes
    if stepSize is not None:
        verts, faces, _, _ = skimage.measure.marching_cubes(margedField, level=level, spacing=aspectRatio, step_size=stepSize)
    else:
        verts, faces, _, _ = skimage.measure.marching_cubes(margedField, level=level, spacing=aspectRatio)

    # call CPP function return gaussian curvature, mean curvature and areas
    meanGaussArea = mtk.computeCurvatures(faces.astype('<u8').tolist(), verts.astype('<f8').tolist())
    meanGaussArea = numpy.array(meanGaussArea)

    totalCurvature = numpy.multiply(meanGaussArea[:, 0], meanGaussArea[:, 2]).sum()

    if fileName is not None:
        pointData = {"meanCurvature": meanGaussArea[:, 0],
                     "gaussCurvature": meanGaussArea[:, 1],
                     "area": meanGaussArea[:, 2]
                     }

        import spam.helpers
        spam.helpers.writeUnstructuredVTK(verts, faces, pointData=pointData,
                                          elementType="triangle", fileName=fileName)

    if getMeshValues:
        return totalCurvature, meanGaussArea[:, 0], meanGaussArea[:, 1], meanGaussArea[:, 2]
    else:
        return totalCurvature


def perimeter(segmented, phase=1, aspectRatio=(1.0, 1.0), ROI=None):
    """
    Computes the perimeter of a given phase.

    Parameters
    -----------
        segmented: array of integers
            Array where integers represent the phases.
            The value 0 is stricly reserved for **not** Region Of Interest.

        phase: integer, default=1
            The phase for which the fraction volume is computed.
            The phase should be greater than 0 if ROI is used.

        aspectRatio: length 2 tuple of floats, default=(1.0, 1.0)
            Length between two nodes in every direction e.g. size of a cell.

        ROI: array of boolean, default=None
            If not None, boolean array which represents the Region Of Interest.
            Segmented will be 0 where ROI is False.

    Returns
    --------
        float:
            The perimeter.

    """
    import spam.filters

    if phase == 0:
        print("spam.measurements.globalDescriptors.perimeter: phase={}. Should be > 0.".format(phase))

    if ROI is not None:
        segmented = segmented * ROI

    # add border
    im_l = numpy.zeros((segmented.shape[0] + 2, segmented.shape[1] + 2), dtype=bool)
    im_l[1:segmented.shape[0] + 1, 1:segmented.shape[1] + 1] = (segmented == phase)

    # take perimeters
    peri = spam.filters.binaryMorphologicalGradient(im_l)

    # compute number of each voxel types
    late = peri & spam.helpers.multipleShifts(peri, shifts=[+1, 0])
    late = late + (peri & spam.helpers.multipleShifts(peri, shifts=[0, +1]))
    late = late + (peri & spam.helpers.multipleShifts(peri, shifts=[-1, 0]))
    late = late + (peri & spam.helpers.multipleShifts(peri, shifts=[0, -1]))
    diag = peri & spam.helpers.multipleShifts(peri, shifts=[+1, +1])
    diag = diag + (peri & spam.helpers.multipleShifts(peri, shifts=[+1, -1]))
    diag = diag + (peri & spam.helpers.multipleShifts(peri, shifts=[-1, +1]))
    diag = diag + (peri & spam.helpers.multipleShifts(peri, shifts=[-1, -1]))
    inte = diag & late
    jdiag = (diag & numpy.logical_not(inte))
    jlate = (late & numpy.logical_not(inte))

    voxelSize = aspectRatio[0]

    # compute global coefficient
    alpha = ((1.0 + 0.5**2)**0.5 * numpy.sum(inte)
             + numpy.sum(jlate)
             + 2.0**0.5 * numpy.sum(jdiag))

    return alpha * voxelSize


def generic(segmented, n, phase=1, level=0.0, aspectRatio=(1.0, 1.0, 1.0), specific=False, ROI=None, verbose=False):
    """
    Maps all measures in a homogeneous format

    Parameters
    -----------
        segmented: array of integers
            Array where integers represent the phases.
            The value 0 is stricly reserved for **not** Region Of Interest.

        n: int
            The number of the measure. The meaning depends of the dimension.

            .. code-block:: text

                * In 1D:
                    * n=0: Euler characteristic
                    * n=1: (specific) length
                * In 2D:
                    * n=0: Euler characteristic
                    * n=1: perimeter
                    * n=2: (specific) surface
                * In 3D:
                    * n=0: Euler Characteristic
                    * n=1: ?
                    * n=2: surface
                    * n=3: (specific) volume

        phase: integer, default=1
            The phase for which the fraction volume is computed.
            The phase should be greater than 0 if ROI is used.

        level: float, default=0.0
            The level set.
            See ``skimage.measure.marching_cubes``.
            Contour value to search for isosurfaces in volume.
            If not given or None, the average of the min and max of vol is used.

        specific: boolean, default=False
            Returns the specific volume if True.

        aspectRatio: length 3 tuple of floats, default=(1.0, 1.0, 1.0)
            Length between two nodes in every direction e.g. size of a cell.

        ROI: array of boolean, default=None
            If not None, boolean array which represents the Region Of Interest.
            Segmented will be 0 where ROI is False.

        verbose: boolean, default=False,
            Verbose mode.
    Returns
    --------
        float:
            The measure
    """

    # get dimension
    dim = len(segmented.shape)

    if dim == 1:
        if n == 0:
            return eulerCharacteristic(segmented, phase=phase, ROI=ROI, verbose=verbose)
        elif n == 1:
            return volume(segmented, phase=phase, aspectRatio=aspectRatio, specific=specific, ROI=ROI)
    elif dim == 2:
        if n == 0:
            return eulerCharacteristic(segmented, phase=phase, ROI=ROI, verbose=verbose)
        if n == 1:
            return perimeter(segmented, phase=phase, ROI=ROI)
        if n == 2:
            return volume(segmented, phase=phase, aspectRatio=aspectRatio, specific=specific, ROI=ROI)
    elif dim == 3:
        if n == 0:
            return eulerCharacteristic(segmented, phase=phase, ROI=ROI, verbose=verbose)
        if n == 1:
            return -1
        if n == 2:
            return surfaceArea(segmented, level=level, aspectRatio=aspectRatio)
        if n == 3:
            return volume(segmented, phase=phase, aspectRatio=aspectRatio, specific=specific, ROI=ROI)

    print('spam.measurements.globalDescriptors.generic: dim={} (should be between 1 and 3) and n={} (should be between 0 and dim). Return NaN'.format(dim, n))
    return numpy.nan

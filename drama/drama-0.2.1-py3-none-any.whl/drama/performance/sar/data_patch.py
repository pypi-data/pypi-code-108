import numpy as np
from drama import constants as const
from drama.orbits import orbit_to_vel
from drama.io import cfg as cfg
from drama.utils import misc as misc
import scipy.interpolate as interpol
import matplotlib.pyplot as plt
from collections import namedtuple
from drama.geo import geometry as geo


# This function is version 1 and needs some optimitzation
def find_patch(tar_ecef, Single_orbData, parFile, La, wvlength, inc_angle=30,
               PRF=None, lim_R='method2', orb_type='repeat', int_type='cubic',
               silent_flag=True):
    """ Finds if target is covered by the orbit and returns the coverage
        patch for single targets

        :param tar_ecef: Single target ECEF coordinates
        :param Single_orbData: tuple containing data for a Single Orbit
        :param parFile: All orbit parameters should be in parFile.
        :param La: antenna length
        :param wvlength: signal wave length
        :param inc_ang: incidence angle [deg]
        :param PRF: Pulse Repetition frequency [Hz]
        :param int_type: interpolator type for satellite's location
        :param timelimit: max measurement time (antenna)
        :param lim_R: method2 -> limit determined by swath width
                      method2 -> limit determined by look angles
    """

    inData = cfg.ConfigFile(parFile)

    # Retrieve useful data for the Single Orbit
    Horb = Single_orbData.Horb
    Single_swath = Single_orbData.swathData
    asc_idx = Single_orbData.asc_idx
    desc_idx = Single_orbData.desc_idx
    Torb = Single_orbData.Torb
    near_1 = np.degrees(geo.inc_to_look(np.radians(inData.sar.near_1), Horb))
    far_1 = np.degrees(geo.inc_to_look(np.radians(inData.sar.far_1), Horb))

    nRevs = inData.orbit.orbits_nbr
    # Find the PRF
    T_sidereal = 86164.09053  # [sec]
    if orb_type == 'repeat':
        Tday = T_sidereal
    elif orb_type == 'sunsync':
        Tday = 86400.
    if PRF is None:
        v_sat = orbit_to_vel(Single_orbData.Horb)
        doppler_bw = 2*v_sat/La
        PRF = np.ceil(doppler_bw)

    # Check for all swaths
    sw_lon = Single_swath.lon
    delta_lon = Torb*360./(Tday/3600.)  # shift in longitude between 2 swaths
    # Unwrap the longitudes
    sw_lon = np.where(sw_lon > 0, sw_lon, sw_lon + 360)
    sw_lat = Single_swath.lat

    # Deal with satellite location and velocity
    # array to save history of all pts
    r_ecef_all = np.array(([], [], []), dtype=float).T
    v_ecef_all = np.array(([], [], []), dtype=float).T
    sw_all = np.zeros(sw_lon.shape[1])
    sw_lon_all = sw_all*np.array([])[:, np.newaxis]
    asc_idx_all = np.array(([], []), dtype=float).T
    desc_idx_all = np.array(([], []), dtype=float).T
    timevec_all = np.array([])[:, np.newaxis]
    timestep = Single_orbData.timestep

    # flags for later use
    extended_mode = 0
    shift_special = None

    # Loop around neighbouring swaths
    jj = 0
    while jj < nRevs:
        sw_lon_rot = np.mod(sw_lon - jj*delta_lon, 360)
        sw_lon_all = np.append(sw_lon_all, sw_lon_rot, axis=0)  # save
        # rotate v_ecef and r_ecef by jj*delta_lon
        v_ecef_rot = geo.rot_z(Single_orbData.v_ecef, jj*delta_lon).T
        r_ecef_rot = geo.rot_z(Single_orbData.r_ecef, jj*delta_lon).T
        r_ecef_all = np.append(r_ecef_all, r_ecef_rot, axis=0)  # save
        v_ecef_all = np.append(v_ecef_all, v_ecef_rot, axis=0)  # save
        asc_idx_all = np.append(asc_idx_all,
                                (asc_idx[np.newaxis, :] +
                                 jj*Single_orbData.timevec.shape[0]),
                                axis=0)  # save ascending indices
        desc_idx_all = np.append(desc_idx_all,
                                 (desc_idx[np.newaxis, :] +
                                  jj*Single_orbData.timevec.shape[0]),
                                 axis=0)  # save ascending indices
        timevec = (Single_orbData.timevec +
                   jj*Single_orbData.timevec.shape[0]*timestep)
        timevec_all = np.append(timevec_all, timevec)

        # Range arrays for transmit and receive paths
        D0_tx = tar_ecef - r_ecef_rot
        R0_tx = np.linalg.norm(D0_tx, axis=1)  # distance vector

        # check the section at which the target is visible by the radar
        if lim_R == 'method1':
            # method1
            sw = const.c/(2*PRF*np.sin(np.deg2rad(inc_angle)))  # swath width
            look_ang = geo.inc_to_look(np.radians(inc_angle), Horb)
            R1 = Horb/np.cos(look_ang)
            R2 = np.sqrt(Horb**2 + (sw + np.sqrt(R1**2 - Horb**2))**2)
            R_lim = [R1, R2]  # Range limits
        elif lim_R == 'method2':
            # method2
            look_win = np.radians([near_1, far_1])
            C = geo.look_to_inc(look_win, Horb) - look_win
            alt = Horb + const.r_earth
            R_lim = np.sqrt(alt**2 + const.r_earth**2 -
                            2*alt*const.r_earth*np.cos(C))

        # #### Cut the data to the section where the target is visible #### #
        visible_idx = np.where((R0_tx > R_lim[0]) * (R0_tx < R_lim[1]))[0]
        visible_flag = np.zeros(R0_tx.shape[0], dtype=bool)
        visible_flag[visible_idx] = True

        # Find Valid Segment where target is seen for longer time period
        con = 0
        idx = misc.find_con_idx(visible_idx)  # all possible visible indices
        # ########## in case of discontinuity in visible segment ########## #
        if ((idx.shape[0] > 1) and (idx[0, 0] == 0) and (idx[-1, -1] == (timevec.shape[0]-1))):
            if jj == 0:
                con = 1  # skip to next loop iteration
                if nRevs == 1:
                    return 0  # 'Target Not seen by satellite'
            else:
                # prolongate data set to govern the discontinuity
                print('entered')
                if extended_mode and (shift_special is not None):
                    shift = shift_special
                    idx = np.array(([[0, idx[0, 1] + shift]]))
                else:
                    shift = idx[-1, -1] - idx[-1, 0] + 1
                    idx += shift
                    idx[0, 0] -= shift
                    idx = np.delete(idx, -1, 0)

                extended_mode = 1
                timevec -= shift*timestep
                r_ecef_rot = r_ecef_all[timevec.astype(int), :]
                v_ecef_rot = v_ecef_all[timevec.astype(int), :]
                sw_lat = np.roll(sw_lat, shift)
                # Range arrays for transmit and receive paths
                D0_tx = tar_ecef - r_ecef_rot
                R0_tx = np.linalg.norm(D0_tx, axis=1)  # distance vector

                # Update visible flag
                visible_flag = np.zeros(R0_tx.shape[0], dtype=bool)
                visible_flag[idx] = True
                con = 0
        # ####################### back to normal ########################## #
        while con == 0:
            if idx.shape[0] == 0:
                if jj == (nRevs - 1):
                    if extended_mode and (nRevs == inData.orbit.orbits_nbr):
                        nRevs += 1
                        shift_special = shift
                    else:
                        return 0  # 'Target Not seen by satellite'
                break
            bigidx = np.where((idx[:, 1] - idx[:, 0]) ==
                              np.max(idx[:, 1] - idx[:, 0]))[0][0]
            visible_idx_select = np.arange(idx[bigidx, :][0],
                                           idx[bigidx, :][1] + 1)

            # check if point is on right or left of satellite
            centerPt = (int(len(visible_idx_select)/2) +
                        visible_idx_select[0] + int(timevec[0]/timestep))
            coords = [centerPt, int(sw_lat.shape[1]/2)]
            swathMidpt = [sw_lat[coords[0] - int(timevec[0]/timestep),
                                 coords[1]],
                          sw_lon_all[coords[0], coords[1]], 0]
            swathMidpt_ecef = geo.geodetic_to_ecef(swathMidpt)

            r_vec = swathMidpt_ecef - r_ecef_all[centerPt, :]
            r_vec2 = D0_tx[centerPt - int(timevec[0]/timestep), :]
            ang = np.arccos(np.dot(r_vec, r_vec2) /
                            (np.linalg.norm(r_vec)*np.linalg.norm(r_vec2)))

            Rv = R0_tx[visible_idx_select]
            Rv_min = np.argmin(Rv)
            ang = np.degrees(ang)
            look_deg = np.degrees(look_win)
            if ang > np.abs(look_deg[1] - look_deg[0]):
                idx = np.delete(idx, bigidx, 0)
            # target at swath transition
            elif (Rv_min > Rv.shape[0]-5/timestep) or (Rv_min < 5/timestep):
                idx = np.delete(idx, bigidx, 0)
            else:
                con = 1
                extended_mode = 0
                nswath = jj+1
                if not silent_flag:
                    plt.figure()
                    plt.plot(timevec, visible_flag)
                    plt.title('visible index for Rev ' + str(jj+1))
                jj = nRevs
        jj += 1

    # Force Rmin to middle of patch in azimuth
    if visible_idx_select[-1] == (timevec.shape[0]-1):
        visible_idx_select = np.delete(visible_idx_select, -1)
    R_select = R0_tx[visible_idx_select]
    R_min_loc = np.where(R_select == np.min(R_select))[0][0]
    R_min_idx = R_min_loc + visible_idx_select[0]
    if (((visible_idx_select[-1] - R_min_idx) >
         (R_min_idx-visible_idx_select[0] + 2)) or
        ((visible_idx_select[-1] - R_min_idx) <
         (R_min_idx-visible_idx_select[0] - 2))):

        idx_mod0 = (int(timevec[R_min_idx]/timestep) -
                    int(visible_idx_select.shape[0]/2) - 1)
        idx_mod1 = (int(timevec[R_min_idx]/timestep) +
                    int(visible_idx_select.shape[0]/2))
        if idx_mod1 > timevec_all[-1]/timestep:
            idx_mod1 = timevec_all[-1]/timestep
        if idx_mod0 < 0:
            idx_mod0 = 0
        timevec_new = timevec_all[idx_mod0:idx_mod1]
        r_ecef_mod = r_ecef_all[idx_mod0:idx_mod1 + 2, :]
        v_ecef_mod = v_ecef_all[idx_mod0:idx_mod1 + 2, :]
        R_select = np.linalg.norm(tar_ecef - r_ecef_mod, axis=1)

        # interpolate satellite position and velocity to time
        timevec_extend = timevec_all[idx_mod0:idx_mod1+2]
        t2r = interpol.interp1d(timevec_extend, r_ecef_mod.T, kind=int_type)
        t2v = interpol.interp1d(timevec_extend, v_ecef_mod.T, kind=int_type)

    else:
        timevec_new = timevec[visible_idx_select]
        # interpolate satellite position and velocity to time
        t2r = interpol.interp1d(timevec, r_ecef_rot.T, kind=int_type)
        t2v = interpol.interp1d(timevec, v_ecef_rot.T, kind=int_type)

    Patch = namedtuple('Patch', ['timevec_pat', 'r_interp', 'v_interp',
                                 'dist_vec', 'asc_idx_all', 'desc_idx_all',
                                 'timevec_all', 'r_ecef_all', 'v_ecef_all',
                                 'nswath'])
    patch = Patch(timevec_new, t2r, t2v, R_select, asc_idx_all, desc_idx_all,
                  timevec_all, r_ecef_all, v_ecef_all, nswath)
    return patch


def pt_connect(patches, sep, tar_ecef, int_type='linear'):
    """ Connect patches of different targets according to certain separation
        interval

        :param patches: list of patch tuples
        :param sep: separation between target patches [sec]
        :param tar_ecef: list of targets ECEF coords
        :param int_type: interpolation type

        :returns: a common patch with majority of targets
    """
    # find intersecting segments( neighbouring targets)
    # maybe needs to be extended for whole orbit
    r_ecef_all = patches[0].r_ecef_all
    v_ecef_all = patches[0].v_ecef_all
    timevec_all = patches[0].timevec_all
    asc_idx_all = patches[0].asc_idx_all
    desc_idx_all = patches[0].desc_idx_all

    nPat = len(patches)
    neighbours = np.identity(nPat)  # array to find relative neigbors
    timeminmax = np.zeros((nPat, 2))
    timeminmax[nPat - 1, :] = [patches[nPat - 1].timevec_pat[0],
                               patches[nPat - 1].timevec_pat[-1]]
    nswaths = np.zeros((nPat))  # swath number of patch
    nswaths[nPat - 1] = patches[nPat - 1].nswath

    # iterate around multiple patches
    for npatch in range(nPat - 1):
        timevec0 = patches[npatch].timevec_pat
        timeminmax[npatch, :] = [timevec0[0], timevec0[-1]]
        t0 = np.arange(timevec0[0] - sep, timevec0[-1] + sep + 1)
#        Rminall[npatch] = np.min(patches[npatch].dist_vec)
        nswaths[npatch] = patches[npatch].nswath
        # iterate around patches other than patch 1
        for npatch2 in range(npatch + 1, nPat):
            timevec_n = patches[npatch2].timevec_pat
            # expand time vector to check for neighboring patches
            tn = np.arange(timevec_n[0]-sep, timevec_n[-1]+sep+1)
            # check if patches intersect
            if (t0[0] in tn) or (t0[-1] in tn):
                neighbours[npatch, npatch2] = 1
                neighbours[npatch2, npatch] = 1
    # Find major patch with greatest number of neighboring patches
    # Can be expanded later to select main target manually
    sumne = np.sum(neighbours, axis=1)
    nbmax = np.where(sumne == np.max(sumne))[0][0]
    mainNbr = neighbours[nbmax, :]
    mainNbr[np.where(mainNbr == 0)] = -1
    group = (np.arange(nPat)+1)*mainNbr  # neighbours
    group = (np.delete(group, np.where(group < 0)) - 1).astype(int)
    tar_ecef_new = tar_ecef[group, :]
    nswath_new = nswaths[group]

    # create common time vector
    timewin_common = timeminmax[group, :]
    timevecmin = min(timewin_common[:, 0])
    timevecmax = max(timewin_common[:, 1])

    # This section can be omitted if we create a complete time vector
    # and one single interpolator
    if (timevecmax+2) in timevec_all:
        timevec_new = np.arange(timevecmin, timevecmax+1)
        t2r = interpol.interp1d(np.arange(timevecmin,
                                          timevecmax+3),
                                r_ecef_all[timevecmin:
                                           timevecmax+3, :].T,
                                kind=int_type)
        t2v = interpol.interp1d(np.arange(timevecmin,
                                          timevecmax+3),
                                v_ecef_all[timevecmin:
                                           timevecmax+3, :].T,
                                kind=int_type)
    elif (timevecmax+1) in timevec_all:
        timevec_new = np.arange(timevecmin, timevecmax+1)
        t2r = interpol.interp1d(np.arange(timevecmin,
                                          timevecmax+2),
                                r_ecef_all[timevecmin:
                                           timevecmax+2, :].T,
                                kind=int_type)
        t2v = interpol.interp1d(np.arange(timevecmin,
                                          timevecmax+2),
                                v_ecef_all[timevecmin:
                                           timevecmax+2, :].T,
                                kind=int_type)
    else:
        timevec_new = np.arange(timevecmin, timevecmax)
        t2r = interpol.interp1d(timevec_new,
                                r_ecef_all[timevecmin:
                                           timevecmax+1, :].T,
                                kind=int_type)
        t2v = interpol.interp1d(timevec_new,
                                v_ecef_all[timevecmin:
                                           timevecmax+1, :].T,
                                kind=int_type)

    Patch = namedtuple('Patch', ['timevec_pat', 'r_interp', 'v_interp',
                                 'asc_idx_all', 'desc_idx_all', 'timevec_all',
                                 'r_ecef_all', 'nswath', 'tar_ecef'])
    patch = Patch(timevec_new, t2r, t2v, asc_idx_all, desc_idx_all,
                  timevec_all, r_ecef_all, nswath_new, tar_ecef_new)
    return patch

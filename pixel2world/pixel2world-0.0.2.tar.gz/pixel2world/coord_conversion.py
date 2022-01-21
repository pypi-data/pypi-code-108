
def undistort_points(points_distorted, cal):
    """
    Parameters
    ----------
    points_distorted : dataframe
        A dataframe with the first column as frame number and the remaining as the x and y coordinates of the object
            detection for each camera
    cal : dictionary
        The calibration information for each camera stored in a dictionary

    Returns
    -------
    dataframe
        The original dataframe but with the points undistorted using the calibration parameters for each camera

    """
    import cv2
    import numpy as np
    import pandas as pd

    " initialize data "
    points_undistorted = points_distorted.frame.copy().to_frame()

    " undistort all points from each camera image "
    for i in range(len(cal)):
        # current camera's name
        cam_name = cal[i]['camera_name']
        # find the column names for current camera
        col_names = list(points_distorted.columns[points_distorted.columns.str.contains(cam_name)])
        # store the subset of points for the current camera
        points = points_distorted[col_names]

        print("Undistorting points from " + points.columns[0][6:] + " using " + cam_name + "'s cal parameters")

        # store camera's intrinsics
        intrinsics = [[cal[i]['focal_length_u'], 0, cal[i]['center_point_u']],
                      [0, cal[i]['focal_length_v'], cal[i]['center_point_v']],
                      [0, 0, 1]]
        # store camera's distortion coefficients
        dist_coeffs = [cal[i]['distortion_rad'][0], cal[i]['distortion_rad'][1],
                       cal[i]['distortion_tan'][0], cal[i]['distortion_tan'][1],
                       cal[i]['distortion_rad'][2]]

        " undistort image "
        # create new camera matrix
        newcameramtx, _ = cv2.getOptimalNewCameraMatrix(np.array(intrinsics), np.array(dist_coeffs),
                                                        (1920, 1080), 1, (1920, 1080))

        " undistort points "
        points_list = []
        for r in range(len(points)):
            if ~np.isnan(points.iloc[r, 0]):
                points_undist = cv2.undistortPoints(np.array(points.iloc[r,:]), np.array(intrinsics),
                                                    np.array(dist_coeffs), None, newcameramtx)
                # store values in dataframe
                points_temp = pd.DataFrame({col_names[0]: [points_undist[0][0][0]],
                                            col_names[1]: [points_undist[0][0][1]],
                                            "z_pos_" + col_names[0][6:]: [1]})
            else:
                # store values in dataframe
                points_temp = pd.DataFrame({col_names[0]: [np.nan],
                                            col_names[1]: [np.nan],
                                            "z_pos_" + col_names[0][6:]: [np.nan]})
            # append to list
            points_list.append(points_temp)

        # store data for output
        points_undistorted = points_undistorted.join(pd.concat(points_list).reset_index(drop=True))

    return points_undistorted


def triangulate_nviews(P, ip):
    """
    THIS FUNCTION WAS COPIED FROM davegreenwood's triangulation.py FILE ON 2022 JAN 17
    https://gist.github.com/davegreenwood/e1d2227d08e24cc4e353d95d0c18c914

    Triangulate a point visible in n camera views.
    P is a list of camera projection matrices.
    ip is a list of homogenised image points. eg [ [x, y, 1], [x, y, 1] ], OR,
    ip is a 2d array - shape nx3 - [ [x, y, 1], [x, y, 1] ]
    len of ip must be the same as len of P
    """
    import numpy as np

    if not len(ip) == len(P):
        raise ValueError('Number of points and number of cameras not equal.')
    n = len(P)
    M = np.zeros([3*n, 4+n])
    for i, (x, p) in enumerate(zip(ip, P)):
        M[3*i:3*i+3, :4] = p[0]
        M[3*i:3*i+3, 4+i] = -x
    V = np.linalg.svd(M)[-1]
    X = V[-1, :4]
    return X / X[3]


def triangulate_data(df_in, cal, min_cam=2):
    """
    Parameters
    ----------
    df_in : dataframe
        A dataframe with the first column as 'frame' and the remaining columns as the x, y, z points for each camera
    cal : dictionary
        The calibration information for each camera stored in a dictionary
    min_cam : int, default = 2
        The number of cameras the point must be detected in order to run the triangulation method

    Returns
    -------
    dataframe
        A dataframe containing the x, y, and z coordinates of the object in world coordinates
            columns : frame (frame number), x_pos (x coordinate), y_pos (y coordinate), z_pos (z coordinate)

    """
    import numpy as np
    import pandas as pd

    " initialize data "
    df_world = df_in.frame.copy().to_frame()

    df_world_list = []
    for r in range(len(df_in)):
        points_all = []
        cam_proj = []
        for i in range(len(cal)):
            # current camera's name
            cam_name = cal[i]['camera_name']
            # find the column names for current camera
            col_names = list(df_in.columns[df_in.columns.str.contains(cam_name)])
            # store the subset of points for the current camera
            points = df_in[col_names]
            # check if point was found in current frame
            if ~np.isnan(points.iloc[r, 0]):

                # load in current cameras calibration info
                cam_cal = cal[i]

                intrin = [[cam_cal['focal_length_u'], 0, cam_cal['center_point_u']],
                          [0, cam_cal['focal_length_v'], cam_cal['center_point_v']],
                          [0, 0, 1]]

                # put them into the list
                points_all.append(np.array(points.iloc[r,:]))
                cam_proj.append([np.dot(intrin, cam_cal['transformation'])])

        # run triangulation
        if len(cam_proj) >= min_cam:
            # triangulate points
            points_world = triangulate_nviews(cam_proj, points_all)
            # store values in dataframe
            df_world_temp = pd.DataFrame({'x_pos': [points_world[0]],
                                          'y_pos': [points_world[1]],
                                          'z_pos': [points_world[2]]})
        else:
            # store values in dataframe
            df_world_temp = pd.DataFrame({'x_pos': [np.nan],
                                          'y_pos': [np.nan],
                                          'z_pos': [np.nan]})
        # append to list
        df_world_list.append(df_world_temp)

    # store data for output
    df_world = df_world.join(pd.concat(df_world_list).reset_index(drop=True))

    return df_world

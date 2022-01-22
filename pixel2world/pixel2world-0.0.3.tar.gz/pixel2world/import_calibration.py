
def load_theia_cal(path_cal):
    """
    Parameters
    ----------
    path_cal : str
        Full path name of calibration file location

    Returns
    -------
    dict
        A dictionary containing the camera calibration parameters for each camera in the calibration file

    """

    from xml.dom import minidom

    """ load cal file """
    file = minidom.parse(path_cal)
    # get all elements of 'camera' tag
    cam_cams = file.getElementsByTagName('camera')
    # get all elements of 'transform' tag
    cam_trans = file.getElementsByTagName('transform')
    # get all elements of 'intrinsic' tag
    cam_intrins = file.getElementsByTagName('intrinsic')

    """ create dictionary containing all calibration info """
    cal_dict = {}
    for i in range(len(cam_cams)):
        cam_name = cam_cams[i].attributes['serial'].value
        cal_dict[i] = {'camera_number': i,
                       'camera_name': cam_name,
                       'transformation': [[float(cam_trans[i].attributes['r11'].value), float(cam_trans[i].attributes['r12'].value), float(cam_trans[i].attributes['r13'].value), float(cam_trans[i].attributes['x'].value)],
                                          [float(cam_trans[i].attributes['r21'].value), float(cam_trans[i].attributes['r22'].value), float(cam_trans[i].attributes['r23'].value), float(cam_trans[i].attributes['y'].value)],
                                          [float(cam_trans[i].attributes['r31'].value), float(cam_trans[i].attributes['r32'].value), float(cam_trans[i].attributes['r33'].value), float(cam_trans[i].attributes['z'].value)]],
                       'focal_length': float(cam_intrins[i].attributes['focallength'].value),
                       'sensor_dim_u': [int(cam_intrins[i].attributes['sensorMinU'].value), int(cam_intrins[i].attributes['sensorMaxU'].value)],
                       'sensor_dim_v': [int(cam_intrins[i].attributes['sensorMinV'].value), int(cam_intrins[i].attributes['sensorMaxV'].value)],
                       'focal_length_u': float(cam_intrins[i].attributes['focalLengthU'].value),
                       'focal_length_v': float(cam_intrins[i].attributes['focalLengthV'].value),
                       'center_point_u': float(cam_intrins[i].attributes['centerPointU'].value),
                       'center_point_v': float(cam_intrins[i].attributes['centerPointV'].value),
                       'distortion_rad': [float(cam_intrins[i].attributes['radialDistortion1'].value),
                                          float(cam_intrins[i].attributes['radialDistortion2'].value),
                                          float(cam_intrins[i].attributes['radialDistortion3'].value)],
                       'distortion_tan': [float(cam_intrins[i].attributes['tangentalDistortion1'].value),
                                          float(cam_intrins[i].attributes['tangentalDistortion2'].value)]}

    return cal_dict


def combine_data(dict_in):
    """
    Combine data from all cameras on the column 'frame'
    This ensures data matches and is the same length
    It will add the file name to the column names to distinguish from where the data came. So the file name needs to
        contain the camera name (this will be how later functions call the correct data)

    Parameters
    ----------
    dict_in : dictionary
        A dictionary containing the camera name and a dataframe of the dataset for each camera
        format example : dict_in[0] = {'camera_name': "camera_1",
                                       'data': pd.DataFrame}

    Returns
    -------
    dataframe
        A single dataframe with coordinates from each camera matched by the frame number

    """
    import pandas as pd

    for i in range(len(dict_in)):
        print("Camera " + str(i) + ": " + dict_in[i]["camera_name"])

        df_in = dict_in[i]["data"].iloc[:, :3]
        # add camera index to end of columns (except 'frame')
        df_in.columns = ['{}{}'.format(c, '' if c in {"frame"} else '_' + dict_in[i]["camera_name"]) for c in df_in.columns]

        if i == 0:
            df_all = df_in.copy()
        else:
            df_all = pd.merge(df_all, df_in, on="frame", how="outer", sort=True)

    return df_all



def yolo_data(path_files, img_w=1920, img_h=1080, thresh=0.85):
    """
    Import and convert data from YOLO
    Data must be in csv files in the column order ['frame', 'x_pos', 'y_pos', 'x_width', 'y_width', 'confidence']

    Parameters
    ----------
    path_files : list
        A list of all the full path names to the csv files containing the detections from YOLO
    img_w : int, default = 1920
        The width of the image in pixels
    img_h : int, default = 1080
        The height of the image in pixels
    thresh : float, default = 0.85
        The confidence threshold value - keep all detections greater to or equal than this value

    Returns
    -------
    dataframe
        A single dataframe with coordinates from each camera matched by the frame number

    """
    import os
    import pandas as pd
    from pixel2world.convert_data import combine_data

    " initialize data "
    df_all = {}

    " store data from each file in data output dict "
    for i in range(len(path_files)):
        # load in current file
        df_in = pd.read_csv(os.path.join(path_files[i]), header=None,
                            names=["frame", "x_pos", "y_pos", "x_width", "y_width", "confidence"])
        # convert to image size
        df_in.x_pos, df_in.y_pos = df_in.x_pos * img_w, df_in.y_pos * img_h
        # filter by highest confidence and remove the lower confidence row
        df_sort = df_in.sort_values(["frame", "confidence"],
                                    ascending=[True, False]).drop_duplicates(subset=['frame']).reset_index(drop=True)
        # remove any data lower than threshold
        df_filt = df_sort[df_sort.confidence >= thresh].reset_index(drop=True)

        " store data for output "
        df_all[i] = {'camera_name': os.path.split(path_files[i])[1][:-4],
                     'data': df_filt}

    " convert data into data frame "
    df_out = combine_data(df_all)

    return df_out


def dlc_data(path_files, type="csv", flip_y="no", img_h=1080, thresh=0.85):
    """
    Import and convert data from DeepLabCut
    Data must be in csv files in the column order ['frame', 'x_pos', 'y_pos', 'likelihoohd'] and starting at row 4

    Parameters
    ----------
    path_files : list
        A list of all the full path names to the csv files containing the detections from DeepLabCut
    type : str, default = "csv"
        The type of data output by DeepLabCut (options: csv)
    flip_y : str, default = "no"
        Flip y image coordinates to make origin at the bottom left of image
    img_h : int, default = 1080
        The height of the image in pixels
    thresh : float, default = 0.85
        The likelihood threshold value - keep all detections greater to or equal than this value

    Returns
    -------
    dataframe
        A single dataframe with coordinates from each camera matched by the frame number

    """
    import os
    import pandas as pd
    from pixel2world.convert_data import combine_data

    if type == "csv":

        " initialize data "
        df_all = {}

        " store data from each file in data output dict "
        for i in range(len(path_files)):
            # load in current file
            df_in = pd.read_csv(os.path.join(path_files[i]), header=None,
                                names=["frame", "x_pos", "y_pos", "likelihood"],
                                skiprows=3)
            if flip_y is "yes":
                # flip y so origin is bottom left of image
                df_in.y_pos = img_h - df_in.y_pos
            # filter by highest confidence and remove the lower confidence row
            df_sort = df_in.sort_values(["frame", "likelihood"],
                                        ascending=[True, False]).drop_duplicates(subset=['frame']).reset_index(
                drop=True)
            # remove any data lower than threshold
            df_filt = df_sort[df_sort.likelihood >= thresh].reset_index(drop=True)

            " store data for output "
            df_all[i] = {'camera_name': os.path.split(path_files[i])[1][:-4],
                         'data': df_filt}

        " convert data into data frame "
        df_out = combine_data(df_all)

        return df_out
import pandas as pd
import os

# ### the dataset locate function
def dataset_path(directory=None):
    if directory == None:
        dataset_dir = input(
            "\nEnter the UAH dataset directory (example: ~/Downloads/UAH-DRIVESET-v1), you can download it from here this link: \nhttp://www.robesafe.uah.es/personal/eduardo.romera/uah-driveset/#download \n\nyour input:"
        )
        if dataset_dir == None:
            print("\nno entry, loading default directory")
            PARENT_DIR = "~/Downloads/dataset/UAH-DRIVESET-v1"
        else:
            PARENT_DIR = dataset_dir
    else:
        PARENT_DIR = str(directory)
    print("\nthe selected dataset directory is:", PARENT_DIR)
    return PARENT_DIR


# ### the driver, driving state and road type selection function


def datablockpath_selection(driver=None, state=None, roadtype=None, selector=1):
    directory2 = None
    if state == None and roadtype == None and driver == None:
        seldriver = input(
            "\nenter the driver from list: \n 1.'D1' 2.'D2' 3.'D3' 4.'D4' 5.'D5' 6.'D6' \n\nyour choice:"
        )
        selstate = input(
            "\nenter state from list: \n 1.'normal' 2.'agressif' 3.'drowsy' \n\nyour choice:"
        )
        selroadtype = input(
            "\nenter road type from list: \n 1.'secondary' 2.'motorway' \n\nyour choice:"
        )
    else:
        seldriver = str(driver)
        selstate = str(state)
        selroadtype = str(roadtype)

    if seldriver == "1" or seldriver == "D1":
        if selstate == "1" or selstate == "normal":
            if selroadtype == "1" or selroadtype == "secondary":
                directory = "D1/20151110175712-16km-D1-NORMAL1-SECONDARY"
                directory2 = "D1/20151110180824-16km-D1-NORMAL2-SECONDARY"
            elif selroadtype == "2" or selroadtype == "motorway":
                directory = "D1/20151111123124-25km-D1-NORMAL-MOTORWAY"
            else:
                print(
                    "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                )
                print("\n Reminder: we only have 2 road types")
        elif selstate == "2" or selstate == "agressif":
            if selroadtype == "1" or selroadtype == "secondary":
                directory = "D1/20151111134545-16km-D1-AGGRESSIVE-SECONDARY"
            elif selroadtype == "2" or selroadtype == "motorway":
                directory = "D1/20151111125233-24km-D1-AGGRESSIVE-MOTORWAY"
            else:
                print(
                    "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                )
                print("\n Reminder: we only have 2 road types")
        elif selstate == "3" or selstate == "drowsy":
            if selroadtype == "1" or selroadtype == "secondary":
                directory = "D1/20151111135612-13km-D1-DROWSY-SECONDARY"
            elif selroadtype == "2" or selroadtype == "motorway":
                directory = "D1/20151111132348-25km-D1-DROWSY-MOTORWAY"
            else:
                print(
                    "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                )
                print("\n Reminder: we only have 2 road types")
        else:
            print(
                "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
            )
            print("\n Reminder: we only have 3 driving states")
    elif seldriver == "2" or seldriver == "D2":
        if selstate == "1" or selstate == "normal":
            if selroadtype == "1" or selroadtype == "secondary":
                directory = "D2/20151120160904-16km-D2-NORMAL1-SECONDARY"
                directory2 = "D2/20151120162105-17km-D2-NORMAL2-SECONDARY"
            elif selroadtype == "2" or selroadtype == "motorway":
                directory = "D2/20151120131714-26km-D2-NORMAL-MOTORWAY"
            else:
                print(
                    "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                )
                print("\n Reminder: we only have 2 road types")
        elif selstate == "2" or selstate == "agressif":
            if selroadtype == "1" or selroadtype == "secondary":
                directory = "D2/20151120163350-16km-D2-AGGRESSIVE-SECONDARY"
            elif selroadtype == "2" or selroadtype == "motorway":
                directory = "D2/20151120133502-26km-D2-AGGRESSIVE-MOTORWAY"
            else:
                print(
                    "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                )
                print("\n Reminder: we only have 2 road types")
        elif selstate == "3" or selstate == "drowsy":
            if selroadtype == "1" or selroadtype == "secondary":
                directory = "D2/20151120164606-16km-D2-DROWSY-SECONDARY"
            elif selroadtype == "2" or selroadtype == "motorway":
                directory = "D2/20151120135152-25km-D2-DROWSY-MOTORWAY"
            else:
                print(
                    "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                )
                print("\n Reminder: we only have 2 road types")
        else:
            print(
                "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
            )
            print("\n Reminder: we only have 3 driving states")
    elif seldriver == "3" or seldriver == "D3":
        if selstate == "1" or selstate == "normal":
            if selroadtype == "1" or selroadtype == "secondary":
                directory = "D3/20151126124208-16km-D3-NORMAL1-SECONDARY"
                directory2 = "D3/20151126125458-16km-D3-NORMAL2-SECONDARY"
            elif selroadtype == "2" or selroadtype == "motorway":
                directory = "D3/20151126110502-26km-D3-NORMAL-MOTORWAY"
            else:
                print(
                    "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                )
                print("\n Reminder: we only have 2 road types")
        elif selstate == "2" or selstate == "agressif":
            if selroadtype == "1" or selroadtype == "secondary":
                directory = "D3/20151126130707-16km-D3-AGGRESSIVE-SECONDARY"
            elif selroadtype == "2" or selroadtype == "motorway":
                directory = "D3/20151126134736-26km-D3-AGGRESSIVE-MOTORWAY"
            else:
                print(
                    "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                )
                print("\n Reminder: we only have 2 road types")
        elif selstate == "3" or selstate == "drowsy":
            if selroadtype == "1" or selroadtype == "secondary":
                directory = "D3/20151126132013-17km-D3-DROWSY-SECONDARY"
            elif selroadtype == "2" or selroadtype == "motorway":
                directory = "D3/20151126113754-26km-D3-DROWSY-MOTORWAY"
            else:
                print(
                    "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                )
                print("\n Reminder: we only have 2 road types")
        else:
            print(
                "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
            )
            print("\n Reminder: we only have 3 driving states")
    elif seldriver == "4" or seldriver == "D4":
        if selstate == "1" or selstate == "normal":
            if selroadtype == "1" or selroadtype == "secondary":
                directory = "D4/20151203171800-16km-D4-NORMAL1-SECONDARY"
                directory2 = "D4/20151203173103-17km-D4-NORMAL2-SECONDARY"
            elif selroadtype == "2" or selroadtype == "motorway":
                directory = "D4/20151204152848-25km-D4-NORMAL-MOTORWAY"
            else:
                print(
                    "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                )
                print("\n Reminder: we only have 2 road types")
        elif selstate == "2" or selstate == "agressif":
            if selroadtype == "1" or selroadtype == "secondary":
                directory = "D4/20151203174324-16km-D4-AGGRESSIVE-SECONDARY"
            elif selroadtype == "2" or selroadtype == "motorway":
                directory = "D4/20151204154908-25km-D4-AGGRESSIVE-MOTORWAY"
            else:
                print(
                    "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                )
                print("\n Reminder: we only have 2 road types")
        elif selstate == "3" or selstate == "drowsy":
            if selroadtype == "1" or selroadtype == "secondary":
                directory = "D4/20151203175637-17km-D4-DROWSY-SECONDARY"
            elif selroadtype == "2" or selroadtype == "motorway":
                directory = "D4/20151204160823-25km-D4-DROWSY-MOTORWAY"
            else:
                print(
                    "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                )
                print("\n Reminder: we only have 2 road types")
        else:
            print(
                "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
            )
            print("\n Reminder: we only have 3 driving states")
    elif seldriver == "5" or seldriver == "D5":
        if selstate == "1" or selstate == "normal":
            if selroadtype == "1" or selroadtype == "secondary":
                directory = "D5/20151211162829-16km-D5-NORMAL1-SECONDARY"
                directory2 = "D5/20151211164124-17km-D5-NORMAL2-SECONDARY"
            elif selroadtype == "2" or selroadtype == "motorway":
                directory = "D5/20151209151242-25km-D5-NORMAL-MOTORWAY"
            else:
                print(
                    "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                )
                print("\n Reminder: we only have 2 road types")
        elif selstate == "2" or selstate == "agressif":
            if selroadtype == "1" or selroadtype == "secondary":
                directory = "D5/20151211165606-12km-D5-AGGRESSIVE-SECONDARY"
            elif selroadtype == "2" or selroadtype == "motorway":
                directory = "D5/20151209153137-25km-D5-AGGRESSIVE-MOTORWAY"
            else:
                print(
                    "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                )
                print("\n Reminder: we only have 2 road types")
        elif selstate == "3" or selstate == "drowsy":
            if selroadtype == "1" or selroadtype == "secondary":
                directory = "D5/20151211170502-16km-D5-DROWSY-SECONDARY"
            elif selroadtype == "2" or selroadtype == "motorway":
                directory = "D5/20151211160213-25km-D5-DROWSY-MOTORWAY"
            else:
                print(
                    "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                )
                print("\n Reminder: we only have 2 road types")
        else:
            print(
                "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
            )
            print("\n Reminder: we only have 3 driving states")
    elif seldriver == "6" or seldriver == "D6":
        if selstate == "1" or selstate == "normal":
            if selroadtype == "1" or selroadtype == "secondary":
                directory = "D6/20151221112434-17km-D6-NORMAL-SECONDARY"
                directory2 = ""
            elif selroadtype == "2" or selroadtype == "motorway":
                directory = "D6/20151217162714-26km-D6-NORMAL-MOTORWAY"
            else:
                print(
                    "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '' , \nyou can also use the entry numbers "
                )
                print("\nReminder: we only have 2 road types")
        elif selstate == "2" or selstate == "agressif":
            if selroadtype == "1" or selroadtype == "secondary":
                directory = ""
                print(
                    "\nATTENTION! driver 6 does not have data for state :agressif and road type: secondary"
                )
            elif selroadtype == "2" or selroadtype == "motorway":
                directory = "D6/20151221120051-26km-D6-AGGRESSIVE-MOTORWAY"
            else:
                print(
                    "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '' , \nyou can also use the entry numbers "
                )
                print("\n Reminder: we only have 2 road types")
        elif selstate == "3" or selstate == "drowsy":
            if selroadtype == "1" or selroadtype == "secondary":
                directory = "D6/20151221113846-16km-D6-DROWSY-SECONDARY"
            elif selroadtype == "2" or selroadtype == "motorway":
                directory = "D6/20151217164730-25km-D6-DROWSY-MOTORWAY"
            else:
                print(
                    "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '' , \nyou can also use the entry numbers "
                )
                print("\nReminder: we only have 2 road types")
        else:
            print(
                "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '' , \nyou can also use the entry numbers "
            )
            print("\nReminder: we only have 3 driving states")
    else:
        directory = ""
        directory2 = ""
        print(
            "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '' , \nyou can also use the entry numbers "
        )
        print("\nReminder: we only have 6 drivers")
    if selector == None:
        prompt = "We have two directories for this state and road type, choose which directory you want or you can choose to return both from the list: \n 1. 'directory1' 2.'directory2' 3.'both' \n\nyour choice:"
        selected = str(input(prompt))
    else:
        selected = str(selector)
    if (selected == "1" or selected == "directory 1") and directory != None:
        print("you choose the default first directory: \n")
        print("your directory is: ", directory)
        return directory
    elif (selected == "2" or selected == "directory2") and directory2 != None:
        print("you choose the second directory: \n")
        print("your directory is: ", directory2)
        return directory2
    elif (selected == "3" or selected == "both") and (
        directory != None and directory2 != None
    ):
        print("you choose to select both directories: \n")
        print("your directories are: \n", directory, "\n", directory2, "\n")
        return directory, directory2
    else:
        print(
            "\nERROR: wrong entry or misspelling, please change the entry or check spelling or remove the '' , \nyou can also use the entry numbers. \n"
        )
        print(
            "Note: for Driver 6, the driver have a unique session in the case of normal state and secondary road \n"
        )
        print("Empty path generated")
        directory = ""
        return directory


# ### the data type directories selection function


def datatype_selection(data=""):
    if data == "":
        prompt = "\nplease choose which type of data from this list: \n 1.'GPS' 2.'Accelerometer' 3.'lane detection' 4.'vehicle detection' \n 5.'open street map' 6.'lane change events' 7.'inertial events' \n 8.'semantics final' 9.'semantics online' \n\nyour choice:"
        datatype = input(prompt)
    else:
        datatype = str(data)
    if datatype == "GPS" or datatype == "1":
        file = "RAW_GPS.txt"
    elif datatype == "Accelerometer" or datatype == "2":
        file = "RAW_ACCELEROMETERS.txt"
    elif datatype == "lane detection" or datatype == "3":
        file = "PROC_LANE_DETECTION.txt"
    elif datatype == "vehicle detection" or datatype == "4":
        file = "PROC_VEHICLE_DETECTION.txt"
    elif datatype == "open street map" or datatype == "5":
        file = "PROC_OPENSTREETMAP_DATA.txt"
    elif datatype == "lane change events" or datatype == "6":
        file = "EVENTS_LIST_LANE_CHANGES.txt"
    elif datatype == "inertial events" or datatype == "7":
        file = "EVENTS_INERTIAL.txt"
    elif datatype == "semantics final" or datatype == "8":
        file = "SEMANTIC_FINAL.txt"
    elif datatype == "semantics online" or datatype == "9":
        file = "SEMANTIC_ONLINE.txt"
    else:
        print(
            "ERROR: No such data type or misspelling, try to write it correctly or remove the '', \nyou can also use the data type numbers"
        )
        print("\nEmpty data type generated")
        file = ""
    return file


# ### path generation


def path_generator(dataset_dir="", conditions_vector=[], datatype=""):
    path = ""
    if dataset_dir == "" and conditions_vector == [] and datatype == "":
        datasetpath = dataset_path()
        conditionspath = datablockpath_selection()
        if conditionspath == "":
            print("\nError in the conditions entry, empty path generated ")
            return path
        datatypepath = datatype_selection()
        if datatypepath == "":
            print("\nError in the data type entry, empty path generated ")
            return path
        path = os.path.join(datasetpath, conditionspath, datatypepath)
        print("\n your path is: ", path)
    else:
        datasetpath = dataset_path(dataset_dir)
        conditionspath = datablockpath_selection(
            conditions_vector[0],
            conditions_vector[1],
            conditions_vector[2],
            conditions_vector[3],
        )
        if conditionspath == "":
            print("\nError in the conditions entry, empty path generated ")
            return path
        datatypepath = datatype_selection(datatype)
        if datatypepath == "":
            print("\nError in the data type entry, empty path generated ")
            return path
        path = os.path.join(datasetpath, conditionspath, datatypepath)
        print("\n your path is: ", path)
    return path


# ### set up column headers function


def data_header_selector(selection=""):
    if selection == "":
        prompt = "\nplease choose which type of header from this list: \n 1.'GPS' 2.'Accelerometer' 3.'lane detection' 4.'vehicle detection' \n 5.'open street map' 6.'lane change events' 7.'inertial events' \n 8.'semantics final' 9.'semantics online' \n\n your choice: "
        header_type = input(prompt)
    else:
        header_type = str(selection)
    if header_type == "GPS" or header_type == "1":
        header_type = "GPS"
        data_headers = [
            "Timestamp (seconds)",
            "Speed (km/h)",
            "Latitude coordinate (degrees)",
            "Longitude coordinate (degrees)",
            "Altitude (meters)",
            "Vertical accuracy (degrees)",
            "Horizontal accuracy (degrees)",
            "Course (degrees)",
            "Difcourse: course variation (degrees)",
        ]
    elif header_type == "Acceleromter" or header_type == "2":
        header_type = "Acceleromter"
        data_headers = [
            "Timestamp (seconds)",
            "Boolean of system activated (1 if >50km/h)",
            "Acceleration in X (Gs)",
            "Acceleration in Y (Gs)",
            "Acceleration in Z (Gs)",
            "Acceleration in X filtered by KF (Gs)",
            "Acceleration in Y filtered by KF (Gs)",
            "Acceleration in Z filtered by KF (Gs)",
            "Roll (degrees)",
            "Pitch (degrees)",
            "Yaw (degrees)",
        ]
    elif header_type == "lane detection" or header_type == "3":
        header_type = "lane detection"
        data_headers = [
            "Timestamp (seconds)",
            "X: car position relative to lane center (meters)",
            "Phi: car angle relative to lane curvature (degrees)",
            "W: road width (meters)",
            "State of the lane det. algorithm [-1=calibrating,0=initializing, 1=undetected, 2=detected/running]",
        ]
    elif header_type == "vehicle detection" or header_type == "4":
        header_type = "vehicle detection"
        data_headers = [
            "Timestamp (seconds)",
            "Distance to ahead vehicle in current lane (meters) [value -1 means no car is detected in front]",
            "Time of impact to ahead vehicle (seconds) [distance related to own speed]",
            "Number of detected vehicles in this frame (traffic)",
            "GPS speed (km/h) [same as in RAW GPS]",
        ]
    elif header_type == "open street map" or header_type == "5":
        header_type = "open street map"
        data_headers = [
            "Timestamp (seconds)",
            "Maximum allowed speed of current road (km/h)",
            "Reliability of obtained maxspeed (0=unknown,1=reliable, 2=used previously obtained maxspeed,3=estimated by type of road)",
            "Type of road (motorway, trunk, secondary...)",
            "Number of lanes in current road",
            "Estimated current lane (1=right lane, 2=first left lane, 3=second left lane, etc) [experimental]",
            "GPS Latitude used to query OSM (degrees)",
            "GPS Longitude used to query OSM (degrees)",
            "OSM delay to answer query (seconds)",
            "GPS speed (km/h) [same as in RAW GPS]",
        ]
    elif header_type == "lane change events" or header_type == "6":
        header_type = "lane change events"
        data_headers = [
            "Timestamp (seconds)",
            "Type [+ indicates right and - left, 1 indicates normal lane change and 2 slow lane change]",
            "GPS Latitude of the event (degrees)",
            "GPS Longitude of the event (degrees)",
            "Duration of the lane change (seconds) [measured since the car position is near the lane marks]",
            "Time threshold to consider irregular change (secs.) [slow if change duration is over this threshold and fast if duration is lower than threshold/3]",
        ]
    elif header_type == "inertial events" or header_type == "7":
        header_type = "inertial events"
        data_headers = [
            "Timestamp (seconds)",
            "Type (1=braking, 2=turning, 3=acceleration)",
            "Level (1=low, 2=medium, 3=high)",
            "GPS Latitude of the event",
            "GPS Longitude of the event ",
            "Date of the event in YYYYMMDDhhmmss format",
        ]
    elif header_type == "semantics final" or header_type == "8":
        header_type = "semantics final"
        data_headers = [
            "Hour of route start",
            "Minute of route start",
            "Second of route start",
            "Average speed during trip (km/h)",
            "Maximum achieved speed during route (km/h)",
            "Lanex score (internal value, related to lane drifting)",
            "Driving time (in minutes)",
            "Hour of route end",
            "Minute of route end",
            "Second of route end",
            "Trip distance (km)",
            "ScoreLongDist	(internal value, Score accelerations)",
            "ScoreTranDist	(internal value, Score turnings)",
            "ScoreSpeedDist (internal value, Score brakings)",
            "ScoreGlobal (internal value, old score that is not used anymore)",
            "Alerts Long (internal value)",
            "Alerts Late (internal value)",
            "Alerts Lanex (internal value)",
            "Number of vehicle stops during route (experimental, related to fuel efficiency estimation)",
            "Speed variability (experimental, related to fuel efficiency estimation)",
            "Acceleration noise (experimental, related to fuel efficiency estimation)",
            "Kinetic energy (experimental, related to fuel efficiency estimation)",
            "Driving time (in seconds)",
            "Number of curves in the route",
            "Power exherted (experimental, related to fuel efficiency estimation)",
            "Acceleration events (internal value)",
            "Braking events (internal value)",
            "Turning events (internal value)",
            "Longitudinal-distraction Global Score (internal value, combines mean[31] and std[32])",
            "Transversal-distraction Global Score (internal value, combines mean[33] and std[34])",
            "Mean Long.-dist. score (internal value)",
            "STD Long.-dist. score (internal value)",
            "Average Trans.-dist. score (internal value)",
            "STD Trans.-dist. score (internal value)",
            "Lacc (number of low accelerations)",
            "Macc (number of medium accelerations)",
            "Hacc (number of high accelerations)",
            "Lbra (number of low brakings)",
            "Mbra (number of medium brakings)",
            "Hbra (number of high brakings)",
            "Ltur (number of low turnings)",
            "Mtur (number of medium turnings)",
            "Htur (number of high turnings)",
            "Score total (base 100, direct mean of the other 7 scores [45-51])",
            "Score accelerations (base 100)",
            "Score brakings (base 100)",
            "Score turnings (base 100)",
            "Score lane-weaving (base 100)",
            "Score lane-drifting (base 100)",
            "Score overspeeding (base 100)",
            "Score car-following (base 100)",
            "Ratio normal (base 1)",
            "Ratio drowsy (base 1)",
            "Ratio aggressive (base 1)",
        ]
    elif header_type == "semantics online" or header_type == "9":
        header_type = "semantics online"
        data_headers = [
            "TimeStamp since route start (seconds)",
            "GPS Latitude (degrees)",
            "GPS Longitude (degrees)",
            "Score total WINDOW (base 100, direct mean of the other 7 scores)",
            "Score accelerations WINDOW (base 100)",
            "Score brakings WINDOW (base 100)",
            "Score turnings WINDOW (base 100)",
            "Score weaving WINDOW (base 100)",
            "Score drifting WINDOW (base 100)",
            "Score overspeeding WINDOW (base 100)",
            "Score car-following WINDOW (base 100)",
            "Ratio normal WINDOW (base 1)",
            "Ratio drowsy WINDOW (base 1)",
            "Ratio aggressive WINDOW (base 1)",
            "Ratio distracted WINDOW (1=distraction detected in last 2 seconds, 0=otherwise)",
            "Score total (base 100, direct mean of the other 7 scores)",
            "Score accelerations (base 100)",
            "Score brakings (base 100)",
            "Score turnings (base 100)",
            "Score weaving (base 100)",
            "Score drifting (base 100)",
            "Score overspeeding (base 100)",
            "Score car-following (base 100)",
            "Ratio normal (base 1)",
            "Ratio drowsy (base 1)",
            "Ratio aggressive (base 1)",
            "Ratio distracted (1=distraction detected in last 2 seconds, 0=otherwise)",
        ]
    else:
        data_headers = []
        print(
            "ERROR: No such header type or header misspelled, try to write it correctly or remove the '', \nyou can also use the header numbers"
        )
        print("\nEmpty data header type generated\n")
    print("your data header type is : ", header_type)
    return data_headers


# ### data reader function


def data_reader(path=""):
    data = []
    if "SEMANTIC_FINAL" in path:
        delimiter = None
    else:
        delimiter = " "
    try:
        data = pd.read_table(path, header=None, delimiter=delimiter)
    except Exception:
        print(
            "\nERROR: please import numpy as pd so this function works and verify the entry path"
        )
        print("\nEmpty data table generated")
        return data
    if "GPS" in path:
        header = 1
        header_type = "GPS"
        data = data.drop([9, 10, 11, 12], axis=1)
    elif "ACCELEROMETER" in path:
        header = 2
        header_type = "Accelerometer"
        try:
            data = data.drop(11, axis=1)
        except Exception:
            data = data
    elif "LANE_DETECTION" in path:
        header = 3
        header_type = "lane detection"
    elif "VEHICLE" in path:
        header = 4
        header_type = "vehicle detection"
        data = data.drop(5, axis=1)
    elif "OPENSTREETMAP" in path:
        header = 5
        header_type = "open street map"
        data = data.drop(10, axis=1)
    elif "CHANGES" in path:
        header = 6
        header_type = "lane change events"
    elif "INERTIAL" in path:
        header = 7
        header_type = "inertial events"
        data = data.drop(6, axis=1)
    elif "FINAL" in path:
        header = 8
        header_type = "semantics final"
        data = data.transpose()
    elif "ONLINE" in path:
        header = 9
        header_type = "semantics online"
        data = data.drop(27, axis=1)
    data.columns = data_header_selector(header)
    print(
        "\033[1m",
        "        Data:",
        header_type,
        "\n",
        "******* READ SUCCESSFULLY *******",
        "\033[0m",
    )
    return data


# ### window stepping function


def window_stepping(data=[], window_size=0):
    segment = []
    final_data = pd.DataFrame()
    if len(data) != 0:
        if window_size == 0:
            final_data = data
            print("\nERROR:Please enter the window size")
            print("\nATTENTION: Entry data returned without window stepping")
            return final_data
        else:
            for i in range(0, len(data) - 1, window_size):
                segment = data[i : i + window_size]
                row = segment.mean()
                final_data = final_data.append(row, ignore_index=True)
    else:
        final_data = []
        print("ERROR: Empty data entry")
    return final_data


# ### merge dataframes functions


def merge_dataframes(data1=[], data2=[]):
    try:
        while data1.dtypes["Timestamp (seconds)"] != "int64":
            print(
                "\nWarning: Your data1 Timestamps are not integers, we are going to change their type\n"
            )
            data1["Timestamp (seconds)"] = data1["Timestamp (seconds)"].astype("int")
            print(
                "data1 timestamp type changed to : ",
                data1.dtypes["Timestamp (seconds)"],
                "\n",
            )
        while data2.dtypes["Timestamp (seconds)"] != "int64":
            print(
                "Warning: Your data2 Timestamps are not integers, we are going to change their type\n"
            )
            data2["Timestamp (seconds)"] = data2["Timestamp (seconds)"].astype("int")
            print(
                "data2 timestamp type changed to : ",
                data2.dtypes["Timestamp (seconds)"],
                "\n",
            )
        data_merged = data1.set_index("Timestamp (seconds)").join(
            data2.set_index("Timestamp (seconds)")
        )
        data_merged = data_merged.reset_index()
        print("\033[1m", "******* DATA SUCCESSFULLY MERGED *******", "\033[0m")
    except Exception:
        print(
            "ERROR: empty data entries or one data entry or both do not have 'Timestamp (seconds)' column, \nplease renter your two dataframes or check their columns before entry "
        )
        print("\nplease import pandas for this function to work")
        print("\nEmpty data returned")
        data_merged = []
    return data_merged


# ### interpolate_missing_data function


def interpolate_missing_data(data=[]):
    try:
        print("\n    State before interpolation    \n")
        print("COLUMNS                   ", "NUMBER OF RAWS WITH MISSING DATA")
        print(data.isnull().sum())
        missing_values = data.drop(["Timestamp (seconds)"], axis=1)
        missing_values = missing_values.interpolate(method="cubic", limit=3)
        data[missing_values.columns] = missing_values
        data_interpolated = data
    except Exception:
        data_interpolated = []
        print(data_interpolated)
        print("\nERROR: empty data entry or non dataframe type")
        print("\nplease import pandas for this function to work")
        print("\nEmpty data returned")

    try:
        print("\n    State after interpolation    \n")
        print("COLUMNS                   ", "NUMBER OF RAWS WITH MISSING DATA")
        print(data_interpolated.isnull().sum())
    except Exception:
        pass
    return data_interpolated


# ### removing incomplete raws functions


def removing_incomplete_raws(data=[]):
    try:
        data = data.dropna()
        data = data.reset_index(drop=True)
        print(data.count())
        print(
            "is there any missing data values? :",
            "\033[1m",
            data.isnull().values.any(),
            "\033[0m",
        )
    except Exception:
        print(
            "ERROR: empty data entry or non dataframe type, please enter your data dataframe"
        )
        print("\nplease import pandas for this function to work")
        print("\nEmpty data returned")
        data = []
    return data


# ## access any data skeleton function


def access_data(
    dataloc="",
    driver=1,
    state=1,
    road=1,
    selector=1,
    data_type1="",
    data_type2="",
    ws1=0,
    ws2=0,
):
    path1 = path_generator(dataloc, [driver, state, road, selector], data_type1)
    path2 = path_generator(dataloc, [driver, state, road, selector], data_type2)
    data1 = data_reader(path1)
    data2 = data_reader(path2)
    if ws1 != 0 and ws2 != 0:
        data = merge_dataframes(
            data1=window_stepping(data1, ws1), data2=window_stepping(data2, ws2)
        )
    elif ws1 != 0 and ws2 == 0:
        data = merge_dataframes(data1=window_stepping(data1, ws1), data2=data2)
    elif ws2 != 0 and ws1 == 0:
        data = merge_dataframes(data1=data1, data2=window_stepping(data2, ws2))
    else:
        print("ERROR: windowstep entry not acceptable, windowstep should be integer")
    data = interpolate_missing_data(data)
    data = removing_incomplete_raws(data)
    if state == 1:
        data["target"] = "normal"
    elif state == 2:
        data["target"] = "agressif"
    elif state == 3:
        data["target"] = "drowsy"
    if driver == 1:
        data["driver"] = "1"
    elif driver == 2:
        data["driver"] = "2"
    elif driver == 3:
        data["driver"] = "3"
    elif driver == 4:
        data["driver"] = "4"
    elif driver == 5:
        data["driver"] = "5"
    elif driver == 6:
        data["driver"] = "6"
    if road == 1:
        data["road"] = "secondary"
    elif road == 2:
        data["road"] = "motorway"
    return data

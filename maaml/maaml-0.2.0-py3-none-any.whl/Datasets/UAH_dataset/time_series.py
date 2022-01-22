import os
import pandas as pd


class PathBuilder:
    def __init__(
        self,
        dataset_dir=None,
        conditions_vector=[None, None, None, None],
        datatype=None,
        verbose=0,
    ):
        self.driver = conditions_vector[0]
        self.state = conditions_vector[1]
        self.roadtype = conditions_vector[2]
        self.selector = conditions_vector[3]
        self.verbose = verbose
        self.parent_dir = self.parent_path(dataset_dir, verbose=verbose)
        self.conditions = self.case_path_selection(
            self.driver, self.state, self.roadtype, self.selector, verbose=verbose
        )
        self.filetype = self.data_type_selection(datatype)
        if self.filetype != "" and self.conditions != "":
            self.path = os.path.join(self.parent_dir, self.conditions, self.filetype)
            if verbose == 1:
                print(f"\n your path is: {self.path}")
        else:
            self.path = ""
            if verbose == 1:
                print("\nError in the data type entry, empty path generated ")

    def parent_path(self, dataset_dir, verbose=1):
        self.dataset_dir = dataset_dir
        if dataset_dir == None:
            dataset_dir = input(
                "\nEnter the UAH dataset directory (example: '~/Downloads/UAH-DRIVESET-v1'), you can download it from here this link: \nhttp://www.robesafe.uah.es/personal/eduardo.romera/uah-driveset/#download \n\nyour input:"
            )
            if dataset_dir == "":
                print("\nno entry, loading default directory")
                PARENT_DIR = "UAH-DRIVESET-v1"
            else:
                PARENT_DIR = dataset_dir
        else:
            PARENT_DIR = str(dataset_dir)
        if verbose == 1:
            print(f"\nthe selected dataset directory is: {PARENT_DIR}")
        return PARENT_DIR

    def case_path_selection(self, driver, state, roadtype, selector=1, verbose=1):
        directory2 = None
        if driver == None:
            driver = input(
                "\nenter the driver from list: \n 1.'D1' 2.'D2' 3.'D3' 4.'D4' 5.'D5' 6.'D6' \n\nyour choice:"
            )
        else:
            driver = str(driver)
        if state == None:
            state = input(
                "\nenter state from list: \n 1.'normal' 2.'agressif' 3.'drowsy' \n\nyour choice:"
            )
        else:
            state = str(state)
        if roadtype == None:
            roadtype = input(
                "\nenter road type from list: \n 1.'secondary' 2.'motorway' \n\nyour choice:"
            )
        else:
            roadtype = str(roadtype)
        if driver == "1" or driver == "D1":
            if state == "1" or state == "normal":
                if roadtype == "1" or roadtype == "secondary":
                    directory = "D1/20151110175712-16km-D1-NORMAL1-SECONDARY"
                    directory2 = "D1/20151110180824-16km-D1-NORMAL2-SECONDARY"
                elif roadtype == "2" or roadtype == "motorway":
                    directory = "D1/20151111123124-25km-D1-NORMAL-MOTORWAY"
                else:
                    print(
                        "ERROR: bad or misspelled entry, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                    )
                    print("\n Reminder: we only have 2 road types")
            elif state == "2" or state == "agressif":
                if roadtype == "1" or roadtype == "secondary":
                    directory = "D1/20151111134545-16km-D1-AGGRESSIVE-SECONDARY"
                elif roadtype == "2" or roadtype == "motorway":
                    directory = "D1/20151111125233-24km-D1-AGGRESSIVE-MOTORWAY"
                else:
                    print(
                        "ERROR: bad or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                    )
                    print("\n Reminder: we only have 2 road types")
            elif state == "3" or state == "drowsy":
                if roadtype == "1" or roadtype == "secondary":
                    directory = "D1/20151111135612-13km-D1-DROWSY-SECONDARY"
                elif roadtype == "2" or roadtype == "motorway":
                    directory = "D1/20151111132348-25km-D1-DROWSY-MOTORWAY"
                else:
                    print(
                        "ERROR: bad or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                    )
                    print("\n Reminder: we only have 2 road types")
            else:
                print(
                    "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                )
                print("\n Reminder: we only have 3 driving states")
        elif driver == "2" or driver == "D2":
            if state == "1" or state == "normal":
                if roadtype == "1" or roadtype == "secondary":
                    directory = "D2/20151120160904-16km-D2-NORMAL1-SECONDARY"
                    directory2 = "D2/20151120162105-17km-D2-NORMAL2-SECONDARY"
                elif roadtype == "2" or roadtype == "motorway":
                    directory = "D2/20151120131714-26km-D2-NORMAL-MOTORWAY"
                else:
                    print(
                        "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                    )
                    print("\n Reminder: we only have 2 road types")
            elif state == "2" or state == "agressif":
                if roadtype == "1" or roadtype == "secondary":
                    directory = "D2/20151120163350-16km-D2-AGGRESSIVE-SECONDARY"
                elif roadtype == "2" or roadtype == "motorway":
                    directory = "D2/20151120133502-26km-D2-AGGRESSIVE-MOTORWAY"
                else:
                    print(
                        "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                    )
                    print("\n Reminder: we only have 2 road types")
            elif state == "3" or state == "drowsy":
                if roadtype == "1" or roadtype == "secondary":
                    directory = "D2/20151120164606-16km-D2-DROWSY-SECONDARY"
                elif roadtype == "2" or roadtype == "motorway":
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
        elif driver == "3" or driver == "D3":
            if state == "1" or state == "normal":
                if roadtype == "1" or roadtype == "secondary":
                    directory = "D3/20151126124208-16km-D3-NORMAL1-SECONDARY"
                    directory2 = "D3/20151126125458-16km-D3-NORMAL2-SECONDARY"
                elif roadtype == "2" or roadtype == "motorway":
                    directory = "D3/20151126110502-26km-D3-NORMAL-MOTORWAY"
                else:
                    print(
                        "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                    )
                    print("\n Reminder: we only have 2 road types")
            elif state == "2" or state == "agressif":
                if roadtype == "1" or roadtype == "secondary":
                    directory = "D3/20151126130707-16km-D3-AGGRESSIVE-SECONDARY"
                elif roadtype == "2" or roadtype == "motorway":
                    directory = "D3/20151126134736-26km-D3-AGGRESSIVE-MOTORWAY"
                else:
                    print(
                        "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                    )
                    print("\n Reminder: we only have 2 road types")
            elif state == "3" or state == "drowsy":
                if roadtype == "1" or roadtype == "secondary":
                    directory = "D3/20151126132013-17km-D3-DROWSY-SECONDARY"
                elif roadtype == "2" or roadtype == "motorway":
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
        elif driver == "4" or driver == "D4":
            if state == "1" or state == "normal":
                if roadtype == "1" or roadtype == "secondary":
                    directory = "D4/20151203171800-16km-D4-NORMAL1-SECONDARY"
                    directory2 = "D4/20151203173103-17km-D4-NORMAL2-SECONDARY"
                elif roadtype == "2" or roadtype == "motorway":
                    directory = "D4/20151204152848-25km-D4-NORMAL-MOTORWAY"
                else:
                    print(
                        "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                    )
                    print("\n Reminder: we only have 2 road types")
            elif state == "2" or state == "agressif":
                if roadtype == "1" or roadtype == "secondary":
                    directory = "D4/20151203174324-16km-D4-AGGRESSIVE-SECONDARY"
                elif roadtype == "2" or roadtype == "motorway":
                    directory = "D4/20151204154908-25km-D4-AGGRESSIVE-MOTORWAY"
                else:
                    print(
                        "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                    )
                    print("\n Reminder: we only have 2 road types")
            elif state == "3" or state == "drowsy":
                if roadtype == "1" or roadtype == "secondary":
                    directory = "D4/20151203175637-17km-D4-DROWSY-SECONDARY"
                elif roadtype == "2" or roadtype == "motorway":
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
        elif driver == "5" or driver == "D5":
            if state == "1" or state == "normal":
                if roadtype == "1" or roadtype == "secondary":
                    directory = "D5/20151211162829-16km-D5-NORMAL1-SECONDARY"
                    directory2 = "D5/20151211164124-17km-D5-NORMAL2-SECONDARY"
                elif roadtype == "2" or roadtype == "motorway":
                    directory = "D5/20151209151242-25km-D5-NORMAL-MOTORWAY"
                else:
                    print(
                        "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                    )
                    print("\n Reminder: we only have 2 road types")
            elif state == "2" or state == "agressif":
                if roadtype == "1" or roadtype == "secondary":
                    directory = "D5/20151211165606-12km-D5-AGGRESSIVE-SECONDARY"
                elif roadtype == "2" or roadtype == "motorway":
                    directory = "D5/20151209153137-25km-D5-AGGRESSIVE-MOTORWAY"
                else:
                    print(
                        "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '', \n you can also use the entry numbers "
                    )
                    print("\n Reminder: we only have 2 road types")
            elif state == "3" or state == "drowsy":
                if roadtype == "1" or roadtype == "secondary":
                    directory = "D5/20151211170502-16km-D5-DROWSY-SECONDARY"
                elif roadtype == "2" or roadtype == "motorway":
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
        elif driver == "6" or driver == "D6":
            if state == "1" or state == "normal":
                if roadtype == "1" or roadtype == "secondary":
                    directory = "D6/20151221112434-17km-D6-NORMAL-SECONDARY"
                    directory2 = ""
                elif roadtype == "2" or roadtype == "motorway":
                    directory = "D6/20151217162714-26km-D6-NORMAL-MOTORWAY"
                else:
                    print(
                        "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '' , \nyou can also use the entry numbers "
                    )
                    print("\nReminder: we only have 2 road types")
            elif state == "2" or state == "agressif":
                if roadtype == "1" or roadtype == "secondary":
                    directory = ""
                    if verbose == 1:
                        print(
                            "\nATTENTION! driver 6 does not have data for state :agressif and road type: secondary"
                        )
                elif roadtype == "2" or roadtype == "motorway":
                    directory = "D6/20151221120051-26km-D6-AGGRESSIVE-MOTORWAY"
                else:
                    print(
                        "ERROR: No such entry type or misspelled entry type, try to write the entry correctly or remove the '' , \nyou can also use the entry numbers "
                    )
                    print("\n Reminder: we only have 2 road types")
            elif state == "3" or state == "drowsy":
                if roadtype == "1" or roadtype == "secondary":
                    directory = "D6/20151221113846-16km-D6-DROWSY-SECONDARY"
                elif roadtype == "2" or roadtype == "motorway":
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
            selected = input(prompt)
        else:
            selected = str(selector)
        if (selected == "1" or selected == "directory 1") and directory != None:
            if verbose == 1:
                print(
                    f"you choose the default first directory: \nyour directory is: {directory}"
                )
            return directory
        elif (selected == "2" or selected == "directory2") and directory2 != None:
            if verbose == 1:
                print(
                    f"you choose the second directory: \nyour directory is: {directory2}"
                )
            return directory2
        elif (selected == "3" or selected == "both") and (
            directory != None and directory2 != None
        ):
            if verbose == 1:
                print(
                    f"you choose to select both directories: \nyour directories are: \n {directory}\n {directory2}\n"
                )
            return directory, directory2
        else:
            if verbose == 1:
                print(
                    "\nERROR: bad or misspelled entry, please change the entry while checking the spelling or removing the '' , \nyou can also use the entry numbers. \n"
                )
                print(
                    "Note: for Driver 6, the driver have a unique session in the case of normal state and secondary road \n"
                )
                print("Empty path generated")
            directory = ""
            return directory

    def data_type_selection(self, datatype):
        self.datatype = datatype
        SENSOR_FILE = [
            "RAW_GPS.txt",
            "RAW_ACCELEROMETERS.txt",
            "PROC_LANE_DETECTION.txt",
            "PROC_VEHICLE_DETECTION.txt",
            "PROC_OPENSTREETMAP_DATA.txt",
            "EVENTS_LIST_LANE_CHANGES.txt",
            "EVENTS_INERTIAL.txt",
            "SEMANTIC_FINAL.txt",
            "SEMANTIC_ONLINE.txt",
        ]
        if datatype == None:
            prompt = "\nplease choose which type of data from this list: \n 1.'GPS' 2.'Accelerometer' 3.'lane detection' 4.'vehicle detection' \n 5.'open street map' 6.'lane change events' 7.'inertial events' \n 8.'semantics final' 9.'semantics online' \n\nyour choice:"
            datatype = input(prompt)
        else:
            datatype = str(datatype)
        if datatype == "GPS" or datatype == "1":
            return SENSOR_FILE[0]
        elif datatype == "Accelerometer" or datatype == "2":
            return SENSOR_FILE[1]
        elif datatype == "lane detection" or datatype == "3":
            return SENSOR_FILE[2]
        elif datatype == "vehicle detection" or datatype == "4":
            return SENSOR_FILE[3]
        elif datatype == "open street map" or datatype == "5":
            return SENSOR_FILE[4]
        elif datatype == "lane change events" or datatype == "6":
            return SENSOR_FILE[5]
        elif datatype == "inertial events" or datatype == "7":
            return SENSOR_FILE[6]
        elif datatype == "semantics final" or datatype == "8":
            return SENSOR_FILE[7]
        elif datatype == "semantics online" or datatype == "9":
            return SENSOR_FILE[8]
        else:
            print(
                "ERROR: No such data type or misspelling, try to write it correctly or remove the '', \nyou can also use the data type numbers"
            )
            print("\nNo data type file name generated")
        return


class DataReader:
    def __init__(self, path, dataset_name=None, from_string=True, delimiter=" "):
        self.path = path
        if from_string is True:
            if dataset_name == "UAHdataset":
                if "SEMANTIC_FINAL" in path:
                    delimiter = None
                try:
                    self.data = pd.read_table(path, header=None, delimiter=delimiter)
                    self.data = self.uah_dataset_columns(path, self.data)
                except Exception:
                    print("\nERROR: please verify the entry path name for DataReader")
                    print("\nEmpty data table generated")
            else:
                self.data = pd.read_table(path, header=None, delimiter=delimiter)

    def uah_dataset_columns(self, path, data):
        self.path = path
        self.data
        SENSOR_FILE = [
            "RAW_GPS.txt",
            "RAW_ACCELEROMETERS.txt",
            "PROC_LANE_DETECTION.txt",
            "PROC_VEHICLE_DETECTION.txt",
            "PROC_OPENSTREETMAP_DATA.txt",
            "EVENTS_LIST_LANE_CHANGES.txt",
            "EVENTS_INERTIAL.txt",
            "SEMANTIC_FINAL.txt",
            "SEMANTIC_ONLINE.txt",
        ]
        if SENSOR_FILE[0] in path:
            data_column_names = [
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
            data = data.drop([9, 10, 11, 12], axis=1)
        elif SENSOR_FILE[1] in path:
            data_column_names = [
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
            try:
                data = data.drop(11, axis=1)
            except Exception:
                data = data
        elif SENSOR_FILE[2] in path:
            data_column_names = [
                "Timestamp (seconds)",
                "X: car position relative to lane center (meters)",
                "Phi: car angle relative to lane curvature (degrees)",
                "W: road width (meters)",
                "State of the lane det. algorithm [-1=calibrating,0=initializing, 1=undetected, 2=detected/running]",
            ]
        elif SENSOR_FILE[3] in path:
            data_column_names = [
                "Timestamp (seconds)",
                "Distance to ahead vehicle in current lane (meters) [value -1 means no car is detected in front]",
                "Time of impact to ahead vehicle (seconds) [distance related to own speed]",
                "Number of detected vehicles in this frame (traffic)",
                "GPS speed (km/h) [same as in RAW GPS]",
            ]
            data = data.drop(5, axis=1)
        elif SENSOR_FILE[4] in path:
            data_column_names = [
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
            data = data.drop(10, axis=1)
        elif SENSOR_FILE[5] in path:
            data_column_names = [
                "Timestamp (seconds)",
                "Type [+ indicates right and - left, 1 indicates normal lane change and 2 slow lane change]",
                "GPS Latitude of the event (degrees)",
                "GPS Longitude of the event (degrees)",
                "Duration of the lane change (seconds) [measured since the car position is near the lane marks]",
                "Time threshold to consider irregular change (secs.) [slow if change duration is over this threshold and fast if duration is lower than threshold/3]",
            ]
        elif SENSOR_FILE[6] in path:
            data_column_names = [
                "Timestamp (seconds)",
                "Type (1=braking, 2=turning, 3=acceleration)",
                "Level (1=low, 2=medium, 3=high)",
                "GPS Latitude of the event",
                "GPS Longitude of the event ",
                "Date of the event in YYYYMMDDhhmmss format",
            ]
            data = data.drop(6, axis=1)
        elif SENSOR_FILE[7] in path:
            data_column_names = [
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
            data = data.transpose()
        elif SENSOR_FILE[8] in path:
            data_column_names = [
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
            data = data.drop(27, axis=1)
        else:
            data_column_names = []
            print(
                "ERROR: No such file type or file name misspelled, try to write it correctly or remove the '' "
            )
            print("\nNo column names created\n")
        data.columns = data_column_names
        return data


class DataCleaner:
    def __init__(
        self,
        data,
        new_data=None,
        average_window=True,
        window_size=0,
        step=0,
        uah_dataset_vector: list = None,
        save_dataset=False,
        name_dataset="dataset",
        timestamp_column="Timestamp (seconds)",
        verbose=0,
    ):
        self.data_raw = data
        self.data_filtered = data.drop_duplicates(subset=[timestamp_column])
        self.average_window = average_window
        self.window_size = window_size
        self.step = step
        self.data_windowed = self.window_stepping(
            self.data_filtered,
            average_window=average_window,
            window_size=window_size,
            step=step,
            verbose=verbose,
        )
        if new_data is not None:
            self.data_merged = self.dataframes_merging(
                self.data_windowed,
                new_data,
                timestamp_column=timestamp_column,
                drop_duplicates=average_window,
                verbose=verbose,
            )
        else:
            self.data_merged = self.data_windowed
        self.data_interpolated = self.data_interpolating(
            self.data_merged, timestamp_columns=timestamp_column, verbose=verbose
        )
        self.dataset = self.removing_incomplete_raws(
            self.data_interpolated, verbose=verbose
        )
        if uah_dataset_vector is not None:
            self.dataset = self.column_adding(
                self.dataset,
                uah_dataset_vector=uah_dataset_vector,
                verbose=verbose,
            )
        if save_dataset == True:
            NEW_PATH = "dataset"
            if not os.path.exists(NEW_PATH):
                os.makedirs(NEW_PATH)
            self.dataset.to_csv(f"{NEW_PATH}/{name_dataset}.csv", index=False)

    @staticmethod
    def window_stepping(data=[], window_size=0, step=0, average_window=True, verbose=1):
        segment = []
        final_data = pd.DataFrame()
        if len(data) != 0:
            if window_size == 0:
                final_data = data
                if verbose == 1:
                    print("\nATTENTION: Entry data returned without window stepping")
                return final_data
            else:
                if average_window is True:
                    if verbose == 1:
                        print("\nAverage window applied")
                    for i in range(0, len(data) - 1, step):
                        segment = data[i : i + window_size]
                        row = segment.mean()
                        final_data = final_data.append(row, ignore_index=True)
                else:
                    for i in range(0, len(data) - 1, step):
                        window = data[i : i + window_size]
                        final_data = final_data.append(window, ignore_index=True)
                    if verbose == 1:
                        print(
                            f"\nwindow stepping applied with window size: {window_size} and step : {step}"
                        )
        else:
            final_data = []
            print("ERROR: Empty data entry")
        return final_data

    @staticmethod
    def dataframes_merging(
        data=[],
        new_data=[],
        timestamp_column="Timestamp (seconds)",
        drop_duplicates=True,
        verbose=1,
    ):
        try:
            while data.dtypes[timestamp_column] != "int64":
                if verbose == 1:
                    print(
                        "\nWarning: data Timestamp type is: ",
                        data.dtypes[timestamp_column],
                        "\n",
                    )
                data = data.astype({timestamp_column: "int"})
                if verbose == 1:
                    print(
                        "data timestamp type changed to : ",
                        data.dtypes[timestamp_column],
                        "\n",
                    )
            while new_data.dtypes[timestamp_column] != "int64":
                if verbose == 1:
                    print(
                        "Warning: new_data Timestamp type is: ",
                        data.dtypes[timestamp_column],
                        "\n",
                    )
                new_data = new_data.astype({timestamp_column: "int"})
                if verbose == 1:
                    print(
                        "new_data timestamp type changed to : ",
                        new_data.dtypes[timestamp_column],
                        "\n",
                    )
            if drop_duplicates is True:
                data = data.drop_duplicates([timestamp_column])
                new_data = new_data.drop_duplicates([timestamp_column])
            data_merged = data.set_index(timestamp_column).join(
                new_data.set_index(timestamp_column)
            )
            data_merged = data_merged.reset_index()
            if verbose == 1:
                print(f"Shape of the megred data: {data_merged.shape}\n")
                print("\033[1m", "******* DATA SUCCESSFULLY MERGED *******", "\033[0m")
        except Exception:
            print(
                "ERROR: empty data entries or one data entry or both do not have Timestamp column, \nplease renter your two dataframes and check their columns before entry "
            )
            print("\nEmpty data returned")
            data_merged = []
        return data_merged

    @staticmethod
    def data_interpolating(
        data=[], timestamp_columns=["Timestamp (seconds)"], verbose=1
    ):
        try:
            if verbose == 1:
                print(
                    f"\n    State before interpolation    \nCOLUMNS                   NUMBER OF RAWS WITH MISSING DATA\n{data.isnull().sum()}\n"
                )
            if data.isnull().values.any() == True:
                if verbose == 1:
                    print("\n       Executing interpolation     \n")
                missing_values = data.drop(timestamp_columns, axis=1)
                missing_values = missing_values.interpolate(method="cubic", limit=3)
                data[missing_values.columns] = missing_values
                data_interpolated = data
                if verbose == 1:
                    print(
                        f"\n    State after interpolation    \nCOLUMNS                   NUMBER OF RAWS WITH MISSING DATA\n{data_interpolated.isnull().sum()}\n"
                    )
            else:
                data_interpolated = data
                if verbose == 1:
                    print("\n   Interpolation not needed    \n")
        except Exception:
            data_interpolated = []
            print(
                f"{data_interpolated}\nERROR: empty data entry or non dataframe type\nEmpty data returned"
            )
        return data_interpolated

    @staticmethod
    def removing_incomplete_raws(data=[], verbose=1):
        try:
            if verbose == 1:
                print(
                    f"\n    Data count before removing any rows :     \n{data.count()}"
                )
                print(
                    "\nis there any missing data values? :",
                    "\033[1m",
                    data.isnull().values.any(),
                    "\033[0m",
                )
            data = data.dropna()
            data = data.reset_index(drop=True)
            if verbose == 1:
                print(f"\n  Final Data count :     \n{data.count()}")
                print(
                    "\nis there any missing data values? :",
                    "\033[1m",
                    data.isnull().values.any(),
                    "\033[0m",
                )
        except Exception:
            print(
                "ERROR: empty data entry or non dataframe type, please enter your data dataframe\nEmpty data returned"
            )
            data = []
        return data

    @staticmethod
    def column_adding(
        data,
        column_name: str = None,
        value: str = None,
        uah_dataset_vector: list = None,
        verbose=0,
    ):
        if uah_dataset_vector is None:
            if column_name is not None and value is not None:
                data[column_name] = value
            else:
                data = data
                if verbose == 1:
                    print("\n    No label columns added    \n")
        else:
            if uah_dataset_vector[0] == 1:
                data["driver"] = "1"
            elif uah_dataset_vector[0] == 2:
                data["driver"] = "2"
            elif uah_dataset_vector[0] == 3:
                data["driver"] = "3"
            elif uah_dataset_vector[0] == 4:
                data["driver"] = "4"
            elif uah_dataset_vector[0] == 5:
                data["driver"] = "5"
            elif uah_dataset_vector[0] == 6:
                data["driver"] = "6"
            if uah_dataset_vector[2] == 1:
                data["road"] = "secondary"
            elif uah_dataset_vector[2] == 2:
                data["road"] = "motorway"
            if uah_dataset_vector[1] == 1:
                data["target"] = "normal"
            elif uah_dataset_vector[1] == 2:
                data["target"] = "agressif"
            elif uah_dataset_vector[1] == 3:
                data["target"] = "drowsy"
            if verbose == 1:
                print("\n   labels columns added successfully   \n")
        return data


class UAHDatasetBuilder:
    def __init__(
        self,
        path,
        datatype1,
        datatype2,
        window_size_dt1=0,
        step_dt1=0,
        window_size_dt2=0,
        step_dt2=0,
        save_dataset=False,
        name_dataset="UAHDataset",
        verbose=0,
        verbose1=0,
        verbose2=0,
    ):
        self.path_list = []
        self.path_list2 = []
        self.data = pd.DataFrame()
        for i in (1, 2, 3, 4, 5, 6):
            for j in (1, 2, 3):
                for k in (1, 2):
                    for l in (1, 2):
                        file1 = PathBuilder(
                            path, conditions_vector=[i, j, k, l], datatype=datatype1
                        )
                        file2 = PathBuilder(
                            path, conditions_vector=[i, j, k, l], datatype=datatype2
                        )
                        if file1.path != "" and file2.path != "":
                            raw_data1 = DataReader(
                                file1.path, dataset_name="UAHdataset"
                            )
                            raw_data2 = DataReader(
                                file2.path, dataset_name="UAHdataset"
                            )
                            self.data_chunk1 = DataCleaner(
                                raw_data1.data,
                                window_size=window_size_dt1,
                                step=step_dt1,
                                verbose=verbose1,
                            ).dataset
                            self.data_chunk2 = DataCleaner(
                                raw_data2.data,
                                window_size=window_size_dt2,
                                step=step_dt2,
                                verbose=verbose2,
                            ).dataset
                            self.data_chunk_merged = DataCleaner(
                                data=self.data_chunk1,
                                new_data=self.data_chunk2,
                                uah_dataset_vector=[i, j, k, l],
                                verbose=verbose,
                            ).dataset
                            self.data = self.data.append(self.data_chunk_merged)
                            self.data = self.data.reset_index()
                            self.data = self.data.drop("index", axis=1)
                            self.path_list.append(file1.path)
                            self.path_list2.append(file2.path)
        if save_dataset == True:
            NEW_PATH = "dataset"
            if not os.path.exists(NEW_PATH):
                os.makedirs(NEW_PATH)
            self.data.to_csv(f"{NEW_PATH}/{name_dataset}.csv", index=False)
            if verbose == 1:
                print(
                    f"\n\033[1m++++++++++++ UAHDATASET IS SAVED IN FILE : {os.getcwd()}/{NEW_PATH}/{name_dataset}.csv ++++++++++++\033[0m\n"
                )


if __name__ == "__main__":
    DATA_DIR_PATH = "/run/media/najem/34b207a8-0f0c-4398-bba2-f31339727706/home/stock/The_stock/dev & datasets/PhD/datasets/UAH-DRIVESET-v1/"
    dataset = UAHDatasetBuilder(
        DATA_DIR_PATH,
        1,
        2,
        window_size_dt2=10,
        step_dt2=10,
        verbose=1,
        save_dataset=False,
    )
    print(f"The dataset shape: {dataset.data.shape}")

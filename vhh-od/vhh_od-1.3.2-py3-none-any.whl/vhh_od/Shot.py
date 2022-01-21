from vhh_od.CustObject import CustObject
from vhh_od.utils import append_dict_as_row
import numpy as np


class Shot(object):
    """
    This class is representing a shot. Each instance of this class is holding the properties of one shot.
    """

    def __init__(self, movie_name, sid, start_pos, end_pos):
        """
        Constructor

        :param sid [required]: integer value representing the id of a shot
        :param movie_name [required]: string representing the name of the movie
        :param start_pos [required]: integer value representing the start frame position of the shot
        :param end_pos [required]: integer value representing the end frame position of the shot
        """
        #print("create instance of shot ...");
        self.sid = sid
        self.movie_name = movie_name
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.object_list = []

    def addCustomObject(self, obj: CustObject):
        self.object_list.append(obj)

    def convert2String(self):
        """
        Method to convert class member properties in a semicolon separated string.

        :return: string holding all properties of one shot.
        """
        tmp_str = str(self.sid) + ";" + str(self.movie_name) + ";" + str(self.start_pos) + ";" + str(self.end_pos)
        return tmp_str

    def printShotInfo(self):
        """
        Method to a print summary of shot properties.
        """
        print("------------------------")
        print("shot id: " + str(self.sid))
        print("movie name: " + str(self.movie_name))
        print("start frame: " + str(self.start_pos))
        print("end frame: " + str(self.end_pos))
        print("<<< Object list >>>")
        for obj in self.object_list:
            obj.printObjectInfo()

    def convertObjectList2Dict(self):
        #print("Export objects to csv file ... ")
        dict_l = []
        for idx, obj in enumerate(self.object_list):
            entry_dict = {
                'sid': self.sid,
                'movie_name': self.movie_name,
                'start': self.start_pos,
                'stop': self.end_pos,
                'fid': obj.fid,
                'oid': obj.oid,
                'bb_x1': obj.bb_x1,
                'bb_y1': obj.bb_y1,
                'bb_x2': obj.bb_x2,
                'bb_y2': obj.bb_y2,
                'object_conf': obj.object_conf,
                'class_score': obj.class_score,
                'class_name': obj.object_class_name
            }
            dict_l.append(entry_dict)
        return dict_l

    def update_person_classification(self):
        """ 
        Update the person classification 
        I.e. if the classifier classified a person as a soldier 
        then the class will be changed from "Person" to "Person (Soldier)"
        """
        for obj in self.object_list:
            if obj.person_classification is not None:
                obj.update_with_person_classification()

    def update_obj_classifications(self, use_majority_voting, others_factor = 1):
        """
        Updates the class names of objects according to their classification. 
        If use_majority_voting is True:
            Then objects with the same ID will have the same class (the majority class) in every frame
        """

        if not use_majority_voting:
            self.update_person_classification()
            return

        # Gather all objects according to their tracking id
        objs = {}
        for obj in self.object_list:
            if str(obj.oid) in objs:
                objs[str(obj.oid)].append(obj)
            else:
                objs[str(obj.oid)] = [obj]

        # Do majority voting    
        do_majority_classification(objs)

        # Gather all objects with person classification according to their tracking id
        persons = {}
        for obj in self.object_list:
            if obj.person_classification is None:
                continue

            if str(obj.oid) in persons:
                persons[str(obj.oid)].append(obj)
            else:
                persons[str(obj.oid)] = [obj]

        self.update_person_classification()

        # Do majority voting on the person class  
        do_majority_classification(persons, change_weight_of_others(others_factor))

def do_majority_classification(objs, scale_function = (lambda x,y: y)):
        """
        Set the classification of each object to the majority class.
            obj_list: dictionary where the keys are the object IDs and the values is a list of all CustomObject with this ID
            scale_function: (string, float) -> float 
                Function to weigh the votes for a given class.
                The default value does not change the weight of the votes.
        """
        for obj_list in objs.values():
            # Gather votes
            votes = {}
            for obj in obj_list:
                if obj.object_class_name in votes:
                    votes[obj.object_class_name] += 1
                else:
                    votes[obj.object_class_name] = 1

            # Apply scale_function
            for key in votes.keys():
                votes[key] = scale_function(key, votes[key])

            # Find winner
            winner_idx = np.argmax(votes.values())
            winner = list(votes.keys())[winner_idx]

            # Update the objects class names and classifications according to the winner
            for obj in obj_list:
                obj.update_classification(winner)

def change_weight_of_others(others_factor):
    """
    A function that changes the votes for the "others" 
    """
    def fct(key, votes):
        if key != "person":
            return votes
        else:
            return int(others_factor*votes)
    return fct
                
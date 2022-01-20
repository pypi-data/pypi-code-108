""" This class provides functionalities to create, read and adapt iFDO files"""

from math import pi
import yaml
import os
import json
import numpy as np
import subprocess
import ast
import copy
from pprint import pprint

import time

import mariqt.core as miqtc
import mariqt.directories as miqtd
import mariqt.files as miqtf
import mariqt.variables as miqtv
import mariqt.image as miqti
import mariqt.tests as miqtt
import mariqt.navigation as miqtn
import mariqt.settings as miqts
import mariqt.provenance as miqtp
import mariqt.geo as miqtg


class nonCoreFieldIntermediateItemInfoFile:
    def __init__(self, fileName:str, separator:str, header:dict, dateTimeFormat=miqtv.date_formats["mariqt"]):
        self.fileName = fileName
        self.separator = separator
        self.header = header
        self.dateTimeFormat = dateTimeFormat

    def __eq__(self, other):
        if self.fileName==other.fileName and self.separator == other.separator and self.header==other.header:
            return True
        else:
            return False

def findField(ifdo_dict,keys):
        """ Looks for  keys ("key" or [key1][key2 ]) in ifdo_dict and returns its value or an empty string if key not found"""
        if not isinstance(keys, list):
            keys = [keys]

        fail = False
        startingPoints = [
            ifdo_dict, ifdo_dict[miqtv.image_set_header_key], ifdo_dict[miqtv.image_set_items_key]]
        for startingPoint in startingPoints:

            currentLevel = startingPoint
            for key in keys:
                if key in currentLevel and not isinstance(currentLevel, str):
                    lastVal = currentLevel[key]
                    currentLevel = currentLevel[key]
                    fail = False
                else:
                    fail = True
            if not fail:
                return lastVal

        return ""

class iFDO:
    " Class for creating and editing iFDO.yaml files "

    def __init__(self, dir: miqtd.Dir, handle_prefix='20.500.12085',provenance = miqtp.Provenance("iFDO")):
        """ Creates an iFOD object. Requires a valid directory and a handle prefix if it's not the Geomar one. Loads directory's iFDO file if it exists already"""

        self.dir = dir
        self.dir.createTypeFolder()
        self.handle_prefix = "https://hdl.handle.net/" + handle_prefix

        self.imageSetHeaderKey = miqtv.image_set_header_key
        self.imageSetItemsKey = miqtv.image_set_items_key
        self.ifdo_tmp = {self.imageSetHeaderKey: {},
                         self.imageSetItemsKey: {}}
        self.ifdo_checked = copy.deepcopy(self.ifdo_tmp)  # to be set by createiFDO() only!
        self.__allUUIDsChecked = False
        self.reqNavFields = ['image-longitude','image-latitude','image-coordinate-uncertainty-meters',['image-depth','image-altitude']]
        self.prov = provenance

        if not dir.exists():
            raise Exception("directroy", dir.str(), "does not exist.")

        if not dir.validDataDir():
            raise Exception("directroy", dir.str(), "not valid. Does not comply with structure /base/project/[Gear/]event/sensor/data_type/")

        self._imagesInRaw = miqti.browseForImageFiles(self.dir.to(self.dir.dt.raw))
        self._imageNamesInRaw = [os.path.basename(file) for file in self._imagesInRaw]

        if len(self._imagesInRaw) == 0:
            raise Exception("No images files found in " + self.dir.to(self.dir.dt.raw) + " and its subdirectories")

        unique, dup = miqtt.filesHaveUniqueName(self._imagesInRaw)
        if not unique:
            raise Exception(
                "Not all files have unique names. Duplicates: " + str(dup))

        allvalid, msg = miqti.allImageNamesValid(self._imagesInRaw) 
        if not allvalid:
            raise Exception(msg)

        print(str(len(self._imagesInRaw)) + " image files found.")
        print("")
        print("Following information was parsed from directory, please check for correctness:")
        print("Project:\t"+self.dir.project())
        if self.dir.with_gear:
            print("Gear:\t\t"+self.dir.gear())
        print("Event:\t\t"+self.dir.event())
        print("Sensor:\t\t"+self.dir.sensor())
        print("")

        # try load existing iFDO file
        loadedFile = False
        file = self.dir.to(self.dir.dt.products)+self.dir.event() + '_'+self.dir.sensor()+'_iFDO.yaml'
        if(self.readiFDOfile(file)):
            loadedFile = True
        else:
            try:
                path = self.dir.to(self.dir.dt.products)
                for file_ in os.listdir(path):
                    if file_[-10::] == "_iFDO.yaml" and self.readiFDOfile(path+file_):
                        loadedFile = True
                        file = file_
            except FileNotFoundError:
                pass            

        self.tryAutoSetHeaderFields()

        # intermediate files
        self.__initIntermediateFiles()


    def readiFDOfile(self,file:str):
        """ reads iFDO file from self.dir, returns True if self.dir contains an iFOD file, otherwise returns False"""
        if not os.path.exists(file):
            return False

        s = miqtc.PrintLoadingMsg("Loading iFDO file")
        try:
            # 'document.yaml' contains a single YAML document.
            o = open(file, 'r')
            self.ifdo_tmp = yaml.load(o,  Loader=yaml.FullLoader)
            o.close()
            s.stop()
            self.prov.addPreviousProvenance(miqtp.getLastProvenanceFile(self.dir.to(self.dir.dt.protocol),self.prov.executable))
        except Exception as e:
            print(e.args)
            return False
        s.stop()


        if self.imageSetHeaderKey not in self.ifdo_tmp:
            raise Exception("Error loading iFDO file",file,"does not contain",self.imageSetHeaderKey)
        if self.imageSetItemsKey not in self.ifdo_tmp:
            raise Exception("Error loading iFDO file",file,"does not contain",self.imageSetItemsKey)

        if  self.ifdo_tmp[self.imageSetHeaderKey] == None:
            self.ifdo_tmp[self.imageSetHeaderKey] = {}
        if self.ifdo_tmp[self.imageSetItemsKey] == None:
            self.ifdo_tmp[self.imageSetItemsKey] = {}

        print("iFDO file loaded:\t"+os.path.basename(file))

        # for sooooome reason this fixes a hickup of the prog in createiFDO()
        prog = miqtc.PrintKnownProgressMsg("foo", 1,modulo=1)
        prog.clear()
        # check read iFDO file
        try:
            self.createiFDO(self.ifdo_tmp[self.imageSetHeaderKey], miqti.createImageItemsListFromImageItemsDict(self.ifdo_tmp[self.imageSetItemsKey]))
        except Exception as ex:
            print("Loaded iFDO file not valid yet: " + str(ex.args))
        return True


    def writeiFDOfile(self):
        """ Writes an iFDO file to disk. Overwrites potentially existing file."""

        s = miqtc.PrintLoadingMsg("Writing iFDO file")

        # check fields again if changed since last check (createiFDO)
        if self.ifdo_tmp != self.ifdo_checked:
            self.createiFDO(self.ifdo_tmp[self.imageSetHeaderKey], miqti.createImageItemsListFromImageItemsDict(self.ifdo_tmp[self.imageSetItemsKey]))

        event = self.ifdo_checked[self.imageSetHeaderKey]['image-event']
        sensor = self.ifdo_checked[self.imageSetHeaderKey]['image-sensor']
        iFDO_path = self.dir.to(self.dir.dt.products)+ event + '_'+ sensor +'_iFDO.yaml'

        o = open(iFDO_path, "w")
        yaml.dump(self.ifdo_checked, o, default_style=None, default_flow_style=None, allow_unicode=True, width=float("inf"))
        o.close()
        self.prov.write(self.dir.to(self.dir.dt.protocol))
        s.stop()


    def __str__(self) -> str:
        """ Prints current iFDO file """
        return yaml.dump(self.ifdo_checked, default_style=None, default_flow_style=None, allow_unicode=True, width=float("inf"))


    def __getitem__(self, keys):
        """ Returns field entry of checked ifdo fields """
        return findField(self.ifdo_checked,keys)


    def findTmpField(self,keys):
        """ Returns field entry of temporary unchecked ifdo fields """
        return findField(self.ifdo_tmp,keys)


    def setiFDOHeaderFields(self, header: dict):
        """ Clears current header fields und sets provided field values. For updating existing ones use updateiFDOHeaderFields() """
        self.ifdo_tmp[self.imageSetHeaderKey] = {}
        if self.imageSetHeaderKey in header:
            header = header[self.imageSetHeaderKey]
        for field in header:
            #if field not in miqtv.ifdo_header_core_fields:
            #    print("Caution: Unknown header field \"" + field + "\". Maybe a typo? Otherwise ignore me.")
            self.ifdo_tmp[self.imageSetHeaderKey][field] = header[field]


    def updateiFDOHeaderFields(self, header: dict):
        """ Updates existing header fields """
        if self.imageSetHeaderKey in header:
            header = header[self.imageSetHeaderKey]
        log = miqtc.recursivelyUpdateDicts(self.ifdo_tmp[self.imageSetHeaderKey], header, miqtv.ifdo_mutually_exclusive_fields)
        self.prov.log(log)


    def tryAutoSetHeaderFields(self):
        """ Sets certain header fields e.g. from directory if they are not set yet """

        if not 'image-sensor' in self.ifdo_tmp[self.imageSetHeaderKey] or self.ifdo_tmp[self.imageSetHeaderKey]['image-sensor'] == "":
            self.ifdo_tmp[self.imageSetHeaderKey]['image-sensor'] = self.dir.sensor()
        elif self.ifdo_tmp[self.imageSetHeaderKey]['image-sensor'] != self.dir.sensor():
            print("Caution: 'image-sensor'", self.ifdo_tmp[self.imageSetHeaderKey]['image-sensor'], "differs from sensor parsed from directory:", self.dir.sensor())

        if not 'image-event' in self.ifdo_tmp[self.imageSetHeaderKey] or self.ifdo_tmp[self.imageSetHeaderKey]['image-event'] == "":
            self.ifdo_tmp[self.imageSetHeaderKey]['image-event'] = self.dir.event()
        elif self.ifdo_tmp[self.imageSetHeaderKey]['image-event'] != self.dir.event():
            print("Caution: 'image-event'", self.ifdo_tmp[self.imageSetHeaderKey]['image-event'], "differs from event parsed from directory:", self.dir.event())

        if not 'image-project' in self.ifdo_tmp[self.imageSetHeaderKey] or self.ifdo_tmp[self.imageSetHeaderKey]['image-project'] == "":
            self.ifdo_tmp[self.imageSetHeaderKey]['image-project'] = self.dir.project()
        elif self.ifdo_tmp[self.imageSetHeaderKey]['image-project'] != self.dir.project():
            print("Caution: 'image-project'", self.ifdo_tmp[self.imageSetHeaderKey]['image-project'], "differs from project parsed from directory:", self.dir.project())

        if not 'image-set-uuid' in self.ifdo_tmp[self.imageSetHeaderKey]:
            self.ifdo_tmp[self.imageSetHeaderKey]['image-set-uuid'] = str(
                miqtc.uuid4())
        if not 'image-set-handle' in self.ifdo_tmp[self.imageSetHeaderKey]:
            self.ifdo_tmp[self.imageSetHeaderKey]['image-set-handle'] = self.handle_prefix + \
                "/" + self.ifdo_tmp[self.imageSetHeaderKey]['image-set-uuid']
        if not 'image-set-data-handle' in self.ifdo_tmp[self.imageSetHeaderKey]:
            self.ifdo_tmp[self.imageSetHeaderKey]['image-set-data-handle'] = self.handle_prefix + \
                "/" + \
                self.ifdo_tmp[self.imageSetHeaderKey]['image-set-uuid'] + "@data"
        if not 'image-set-metadata-handle' in self.ifdo_tmp[self.imageSetHeaderKey]:
            self.ifdo_tmp[self.imageSetHeaderKey]['image-set-metadata-handle'] = self.handle_prefix + \
                "/" + \
                self.ifdo_tmp[self.imageSetHeaderKey]['image-set-uuid'] + "@metadata"
        if not 'image-set-name' in self.ifdo_tmp[self.imageSetHeaderKey]:
            self.ifdo_tmp[self.imageSetHeaderKey]['image-set-name'] = self.ifdo_tmp[self.imageSetHeaderKey]["image-project"] + \
                " " + self.dir.event() + " " + self.dir.sensor()

    def createCoreFields(self):
        """ Fills the iFDO core fields from intermediate files. Without them no valid iFDO can be created"""

        allNotInferableHeaderFieldsFilled, missingFields = self.checkAllNotInferableHeaderFieldsFilled()
        if not allNotInferableHeaderFieldsFilled:
            raise Exception(
                "Missing iFOD header fields! Set at least following header fields using updateiFDOHeaderFields() or setiFDOHeaderFields() :\n- " + "\n- ".join(missingFields))

        # Parse image-abstract and fill its placeholders with information
        try:
            self.ifdo_tmp[self.imageSetHeaderKey]['image-abstract'] = miqts.parseReplaceVal(self.ifdo_tmp[self.imageSetHeaderKey], 'image-abstract')
        except Exception as ex:
            self.prov.log("Could not replace keys in \'image-abstract\': " + str(ex))

        # Which files contain the information needed to create the iFDO items core information and which columns shall be used
        req = self.intermediateFilesDef_core

        item_data = {}
        prog = miqtc.PrintKnownProgressMsg("Parsing intermediate data", len(req))
        for r in req:
            prog.progress()
            file = self.__get_int_file_prefix() + req[r]['suffix']
            if not os.path.exists(file):
                raise Exception("Intermediate image info file is missing:", self.__get_int_file_prefix() + req[r]['suffix'], "run first:", [e['creationFct'] for e in list(req.values())])
            self.parseItemDatafromTabFileData(item_data, file, req[r]['cols'], req[r]['optional'])
            self.prov.log("parsed item data from: " + file)

        prog.clear()
        if len(item_data) == 0:
            raise Exception("No iFDO items")

        # create yaml and check fields for validity
        # item_data contains field image-filename, which which will not be stored as an item field in iFOD but as the item name itself
        return self.updateiFDO(self.ifdo_tmp[self.imageSetHeaderKey], item_data.values())


    def createCaptureAndContentFields(self):
        """ Fills the iFOD caputre and content fieds from provided data fields """

        req = self.nonCoreFieldIntermediateItemInfoFiles

        item_data = {}
        for r in req:
            if os.path.exists(r.fileName):
                print("loaded: " + r.fileName)
                self.praseItemDataFromFile(item_data,r.fileName,r.separator,r.header,r.dateTimeFormat)
                self.prov.log("parsed item data from: " + r.fileName)
            else:
                print("Files does not exists: " + r.fileName)

        # create yaml and check fields for validity
        # item_data contains field image-filename, which which will not be stored as an item field in iFOD but as the item name itself
        return self.updateiFDO(self.ifdo_tmp[self.imageSetHeaderKey], item_data.values())


    def addItemInfoTabFile(self, fileName: str, separator:str, header:dict, dateTimeFormat=miqtv.date_formats["mariqt"]):
        """ Add a tab seperated text file to parse item data from by createCaptureAndContentFields(). 
        Columns headers will be set as item field names. Must contain column 'image-filename'.
        """
        if fileName == None or not os.path.exists(fileName):
            raise Exception("File",fileName,"not found")

        for field in header:
            if header[field] not in miqtf.tabFileColumnNames(fileName,col_separator=separator):
                raise Exception("Column", header[field], "not in file", fileName)

        if miqtc.assertSlash(os.path.dirname(fileName)) != miqtc.assertSlash(self.dir.to(self.dir.dt.intermediate)):
            print( "Caution: It is recommended to put file in the directory's 'intermediate' folder")
        if nonCoreFieldIntermediateItemInfoFile(fileName, separator, header, dateTimeFormat) not in self.nonCoreFieldIntermediateItemInfoFiles: 
            self.nonCoreFieldIntermediateItemInfoFiles.append(nonCoreFieldIntermediateItemInfoFile(fileName, separator, header, dateTimeFormat))

        
    def removeItemInfoTabFile(self, fileName: str, separator:str, header:dict):
        """ removes file item from list of files to parse item data from by createCaptureAndContentFields() """
        if nonCoreFieldIntermediateItemInfoFile(fileName, separator, header) in self.nonCoreFieldIntermediateItemInfoFiles: 
            self.nonCoreFieldIntermediateItemInfoFiles.remove(nonCoreFieldIntermediateItemInfoFile(fileName, separator, header))


    def updateiFDO(self, header: dict, items: list):
        """ Updates the current values iFDO with the provided new values """
        return self.createiFDO(header, items, updateExisting=True)


    def createiFDO(self, header: dict, items: list, updateExisting=False):
        """ Creates FAIR digital object for the image data itself. This consists of header information and item information. """

        if not updateExisting and len(items) == 0:
            raise Exception('No item information given')

        if updateExisting:
            # header
            self.updateiFDOHeaderFields(header)
            # items
            # update copy of current items with new items fields
            itemsDict = miqti.createImageItemsDictFromImageItemsList(items)
            updatedItems_copy = copy.deepcopy(self.ifdo_tmp[self.imageSetItemsKey])
            log = miqtc.recursivelyUpdateDicts(updatedItems_copy, itemsDict, miqtv.ifdo_mutually_exclusive_fields)
            self.prov.log(log)
            items = miqti.createImageItemsListFromImageItemsDict(updatedItems_copy)

        else:
            self.setiFDOHeaderFields(header)

        # Validate item information
        invalid_items = 0
        image_set_items = {}

        prog = miqtc.PrintKnownProgressMsg("Checking items", len(items),modulo=5)
        for item in items:
            prog.progress()
            # check if all core fields are filled and are filled validly
            try:

                # check item image exists
                # if item is a list (video), one would have to check if each entry is valid given the default values in first entry plus given default values in header
                if not isinstance(item,list):
                    item = [item]
                subItemDefault = item[0] 
                for subItem in item:
                    if subItem['image-filename'] not in self._imageNamesInRaw:
                        raise Exception("Item '" + subItem['image-filename'] + "' not found in /raw directory.")

                    miqtt.isValidiFDOItem(subItem, {**self.ifdo_tmp[self.imageSetHeaderKey], **subItemDefault})
                    

                image_set_items[subItemDefault['image-filename']] = [] # could make an extra case for images omitting the list
                for subItem in item:
                    subItemDict = {}
                    for it in subItem:
                        if it != 'image-filename':
                            subItemDict[it] = subItem[it]
                    image_set_items[subItemDefault['image-filename']].append(subItemDict)
            
            except Exception as e:
                invalid_items += 1
                print("Invalid image item:", item)
                print("Exception:\n", e.args, "\n")
        prog.clear()

        if len(items) != 0 and invalid_items == len(items):
            raise Exception("All items are invalid")
        elif invalid_items > 0:
            print(invalid_items, " items were invalid (of", len(items), ")")

        # Validate header information
        miqtt.isValidiFDOCoreHeader(header)#, all_items_have)

        s = miqtc.PrintLoadingMsg("Updating")
        log = miqtc.recursivelyUpdateDicts(self.ifdo_tmp[self.imageSetItemsKey], image_set_items, miqtv.ifdo_mutually_exclusive_fields)
        s.stop()
        self.prov.log(log)

        # remove emtpy fields
        s = miqtc.PrintLoadingMsg("Removing empty fields")
        self.ifdo_tmp = miqtc.recursivelyRemoveEmptyFields(self.ifdo_tmp)
        s.stop()

        self.checkAllItemHashes()

        # check all other known filled fields are filled validly
        miqtt.isValidiFDOCapture(self.ifdo_tmp)
        miqtt.isValidiFDOContent(self.ifdo_tmp)

        # set final one
        self.ifdo_checked = copy.deepcopy(self.ifdo_tmp)
        return self.ifdo_checked


    def checkAllItemHashes(self):
        hashUncheckImagesInRaw = self.imagesInRaw()
        prog = miqtc.PrintKnownProgressMsg("Checking item hashes", len(self.ifdo_tmp[self.imageSetItemsKey]))
        for item in self.ifdo_tmp[self.imageSetItemsKey]:
            prog.progress()

            found = False
            for image in hashUncheckImagesInRaw:

                if os.path.basename(image) == item:
                    found = True
                    if isinstance(self.ifdo_tmp[self.imageSetItemsKey][item],list): # in case of video with item as list the first entry holds the default and the hash cannot vary for the same image
                        itemEntry = self.ifdo_tmp[self.imageSetItemsKey][item][0] 
                    else:
                        itemEntry = self.ifdo_tmp[self.imageSetItemsKey][item]
                    if not itemEntry['image-hash-sha256'] == miqtc.sha256HashFile(image):
                        raise Exception(item, "incorrect sha256 hash", itemEntry['image-hash-sha256'], "hash is:", miqtc.sha256HashFile(image))
                    break
            if found:
                del hashUncheckImagesInRaw[image]
            else:
                raise Exception( "image", item, "not found in directory's raw folder!")
        prog.clear()


    def checkAllNotInferableHeaderFieldsFilled(self):
        """ Returns whether all core fields, which can not be infered from other fields or the directory, are filled as well as missing fields"""
        inferableHeaderFields = ['image-sensor', 'image-event', 'image-project', 'image-set-uuid', 'image-set-handle',
                                 'image-set-metadata-handle', 'image-set-name', 'image-longitude', 'image-latitude', 'image-depth', 'image-altitude','image-coordinate-uncertainty-meters']

        missingFields = []
        for headerField in miqtv.ifdo_header_core_fields:
            if (headerField not in self.ifdo_tmp[self.imageSetHeaderKey] or self.ifdo_tmp[self.imageSetHeaderKey][headerField] == "") and headerField not in inferableHeaderFields:
                missingFields.append(headerField)

        if len(missingFields) != 0:
            return False, missingFields
        else:
            return True, missingFields


    def createUUIDFile(self,clean=True):
        """ Creates in /intermediate a text file containing per image a created uuid (version 4).

        The UUID is only *taken* from the metadata of the images. It does not write UUIDs to the metadata in case some files are missing it.
        But, it creates a CSV file in that case that you can use together with exiftool to add the UUID to your data. Beware! this can destroy your images
        if not done properly! No guarantee is given it will work. Be careful!

        Use clean=False to not check those files again which are already found in intermediate uuid file
        """

        uuids = {}
        # Check whether a file with UUIDs exists, then read it
        if not clean and os.path.exists(self.get_int_uuid_file()):
            uuids = miqtf.tabFileData(self.get_int_uuid_file(), [miqtv.col_header['mariqt']['img'], miqtv.col_header['mariqt']['uuid']], key_col=miqtv.col_header['mariqt']['img'])
            
        if os.path.exists(self.dir.to(self.dir.dt.raw)):

            missing_uuids = {}
            added_uuids = 0

            unknownFiles = []
            for file in self.imagesInRaw():
                file_name = os.path.basename(file)
                if file_name not in uuids:
                    unknownFiles.append(file)
                else:
                    uuids[file_name] = uuids[file_name][miqtv.col_header['mariqt']['uuid']]

            unknownFilesUUIDs = miqti.imagesContainValidUUID(unknownFiles)
            for file in unknownFilesUUIDs:
                file_name = os.path.basename(file)
                if not unknownFilesUUIDs[file]['valid']:
                    uuid = miqtc.uuid4()
                    missing_uuids[file] = uuid
                else:
                    uuids[file_name] = unknownFilesUUIDs[file]['uuid']
                    added_uuids += 1

            # If previously unknown UUIDs were found in the file headers, add them to the UUID file
            if added_uuids > 0:
                res = open(self.get_int_uuid_file(), "w")
                res.write(miqtv.col_header['mariqt']['img'] +"\t"+miqtv.col_header['mariqt']['uuid']+"\n")
                for file in uuids:
                    res.write(file+"\t"+str(uuids[file])+"\n")
                res.close()

            if len(missing_uuids) > 0:
                ecsv_path = self.__get_int_file_prefix() + "_exif-add-uuid.csv"
                csv = open(ecsv_path, "w")
                csv.write(miqtv.col_header['exif']['img'] +
                          ","+miqtv.col_header['exif']['uuid']+"\n")
                different_paths = []
                for img in missing_uuids:
                    if os.path.basename(img) not in different_paths:
                        different_paths.append(os.path.basename(img))
                    csv.write(img+","+str(missing_uuids[img])+"\n")
                #return False, "exiftool -csv="+ecsv_path+" "+" ".join(different_paths)
                return False, "Not all images have valid UUIDs. Missing for following files:\n"+"\ņ".join(different_paths)
            
            self.__allUUIDsChecked = True
            return True, "All images have a UUID"
        return False, "Path "+self.dir.to(self.dir.dt.raw)+"/raw/ not found."


    def setImageSetAttitude(self,yaw_frame:float,pitch_frame:float,roll_frame:float,yaw_cam2frame:float,pitch_cam2frame:float,roll_cam2frame:float):
        """ calculates the the cameras absolute attitude and sets it to image set header. All angles are expected in degrees. 
        camera2frame angles: rotation of camera coordinates (x,y,z = top, right, line of sight) with respect to vehicle coordinates (x,y,z = forward,right,down) 
        in accordance with the yaw,pitch,roll rotation order convention:

        1. yaw around z,
        2. pitch around rotated y,
        3. roll around rotated x

        Rotation directions according to \'right-hand rule\'.

        I.e. camera2Frame angles = 0,0,0 camera is facing downward with top side towards vehicle's forward direction' """

        R_frame2ned = miqtg.R_YawPitchRoll(yaw_frame,pitch_frame,roll_frame)
        R_cam2frame = miqtg.R_YawPitchRoll(yaw_cam2frame,pitch_cam2frame,roll_cam2frame)
        R_cam2ned = R_frame2ned.dot(R_cam2frame)
        yaw,pitch,roll = miqtg.yawPitchRoll(R_cam2ned)

        # pose matrix cam2utm
        R_camStd2utm = self.get_R_camStd2utm(R_cam2frame,R_frame2ned)

        """
        x = np.array([1,0,0])
        y = np.array([0,1,0])
        z = np.array([0,0,1])
        print('x',R_camStd2utm.dot(x).round(5))
        print('y',R_camStd2utm.dot(y).round(5))
        print('z',R_camStd2utm.dot(z).round(5))
        """

        headerUpdate = {
            miqtv.col_header['mariqt']['yaw']:yaw,
            miqtv.col_header['mariqt']['pitch']:pitch,
            miqtv.col_header['mariqt']['roll']:roll,
            miqtv.col_header['mariqt']['pose']:{'pose-absolute-orientation-utm-matrix':R_camStd2utm.flatten().tolist()}
        }
        self.updateiFDOHeaderFields(headerUpdate)


    def createImageAttitudeFile(self, att_path:str, frame_att_header:dict, camera2Frame_yaw:float,camera2Frame_pitch:float,camera2Frame_roll:float,
     date_format=miqtv.date_formats['pangaea'], const_values = {}, overwrite=False, col_separator = "\t",att_path_angles_in_rad = False, videoSmapleSeconds=1):
        """ Creates in /intermediate a text file with camera attitude data for each image. All angles are expected in degrees. Use att_path_angles_in_rad if necessary. 
        camera2Frame angles: rotation of camera coordinates (x,y,z = top, right, line of sight) with respect to vehicle coordinates (x,y,z = forward,right,down) 
        in accordance with the yaw,pitch,roll rotation order convention:
        1. yaw around z,
        2. pitch around rotated y,
        3. roll around rotated x

        Rotation directions according to \'right-hand rule\'.

        I.e. camera2Frame angles = 0,0,0 camera is facing downward with top side towards vehicle's forward direction' """

        int_attutude_file = self.__get_int_file_prefix() + '_image-attitude.txt'
        output_header_att = {   miqtv.col_header['mariqt']['img']:  miqtv.col_header['mariqt']['img'],
                                miqtv.col_header['mariqt']['utc']:miqtv.col_header['mariqt']['utc'],
                                miqtv.col_header['mariqt']['yaw']:miqtv.col_header['mariqt']['yaw'],
                                miqtv.col_header['mariqt']['pitch']:miqtv.col_header['mariqt']['pitch'],
                                miqtv.col_header['mariqt']['roll']:miqtv.col_header['mariqt']['roll'],
                            }

        int_pose_file = self.__get_int_file_prefix() + '_image-camera-pose.txt'
        output_header_pose = {  miqtv.col_header['mariqt']['img']:miqtv.col_header['mariqt']['img'],
                                miqtv.col_header['mariqt']['utc']:miqtv.col_header['mariqt']['utc'],
                                miqtv.col_header['mariqt']['pose']:miqtv.col_header['mariqt']['pose'],
                            }

        if os.path.exists(int_attutude_file) and not overwrite:
            self.addItemInfoTabFile(int_attutude_file,"\t",output_header_att)
            return True, "Output file exists: "+int_attutude_file

        if not os.path.exists(att_path):
            return False, "Navigation file not found: "+att_path

        if not os.path.exists(self.dir.to(self.dir.dt.raw)):
            return False, "Image folder not found: "+self.dir.to(self.dir.dt.raw)

        # load frame attitude data from file
        att_data, parseMsg = miqtn.readAllAttitudesFromFilePath(att_path, frame_att_header, date_format,col_separator=col_separator,const_values=const_values,anglesInRad=att_path_angles_in_rad)
        if parseMsg != "":
            self.prov.log(parseMsg)
            parseMsg = "\n" + parseMsg

        # find for each image the respective navigation data
        success, image_dts, msg = self.findNavDataForImage(att_data,videoSmapleSeconds)
        if not success:
            return False, msg + parseMsg

        # add camera2Frame angles
        R_cam2frame = miqtg.R_YawPitchRoll(camera2Frame_yaw,camera2Frame_pitch,camera2Frame_roll)
        R_cam2utm_list = []
        for file in image_dts:
            for timepoint in image_dts[file]:
                attitude = timepoint

                R_frame2ned = miqtg.R_YawPitchRoll(attitude.yaw,attitude.pitch,attitude.roll)
                R_cam2ned = R_frame2ned.dot(R_cam2frame)
                yaw,pitch,roll = miqtg.yawPitchRoll(R_cam2ned)
                attitude.yaw = yaw
                attitude.pitch = pitch
                attitude.roll = roll

                R_camStd2utm = self.get_R_camStd2utm(R_cam2frame,R_frame2ned)
                R_cam2utm_list.append(R_camStd2utm.flatten().tolist())

        self.prov.log("applied frame to camera rotation yaw,pitch,roll = " + str(camera2Frame_yaw) + "," + str(camera2Frame_pitch) + "," + str(camera2Frame_roll))

        if len(image_dts) > 0:

            # Write to navigation txt file
            # header
            res = open(int_attutude_file, "w")
            res.write(miqtv.col_header['mariqt']['img']+"\t"+miqtv.col_header['mariqt']['utc'])
            if 'yaw' in frame_att_header:
                res.write("\t"+miqtv.col_header['mariqt']['yaw'])
            if 'pitch' in frame_att_header:
                res.write("\t"+miqtv.col_header['mariqt']['pitch'])
            if 'roll' in frame_att_header:
                res.write("\t"+miqtv.col_header['mariqt']['roll'])

            res.write("\n")
            # data lines
            for file in image_dts:
                for timepoint in image_dts[file]:
                    res.write(file+"\t"+timepoint.dateTime().strftime(miqtv.date_formats['mariqt'])) 
                    if 'yaw' in frame_att_header:
                        res.write("\t"+str(timepoint.yaw))
                    if 'pitch' in frame_att_header:
                        res.write("\t"+str(timepoint.pitch))
                    if 'roll' in frame_att_header:
                        res.write("\t"+str(timepoint.roll))
                    res.write("\n")
            res.close()

            self.prov.addArgument("inputAttitudeFile",att_path,overwrite=True)
            self.prov.log("parsed from inputAttitudeFile: " + str(frame_att_header))
            self.addItemInfoTabFile(int_attutude_file,"\t",output_header_att)

            # Write to pose txt file
            # header
            res = open(int_pose_file, "w")
            res.write(miqtv.col_header['mariqt']['img']+"\t"+miqtv.col_header['mariqt']['utc'])
            res.write("\t"+miqtv.col_header['mariqt']['pose'])
            res.write("\n")
            # data lines
            i = 0
            for file in image_dts:
                for timepoint in image_dts[file]:
                    res.write(file+"\t"+timepoint.dateTime().strftime(miqtv.date_formats['mariqt'])) 
                    entry = str({'pose-absolute-orientation-utm-matrix':R_cam2utm_list[i]}).replace('\n','')
                    res.write("\t"+entry)
                    i += 1
                    res.write("\n")
            res.close()
            self.addItemInfoTabFile(int_pose_file,"\t",output_header_pose)

            return True, "Attitude data created" + parseMsg
        else:
            return False, "No image attitudes found" + parseMsg
        

    def get_R_camStd2utm(self,R_cam2frame:np.array,R_frame2ned:np.array):
        """ retrun rotation matrix R tranforming from camStd: (x,y,z = right,buttom,line of sight) to utm (x,y,z = easting,northing,up) """
        R_camiFDO2camStd = miqtg.R_YawPitchRoll(90,0,0) # in iFDO cam: (x,y,z = top,right,line of sight) but for pose the 'standard' camStd: (x,y,z = right,buttom,line of sight) is expected
        R_camStd2frame = R_cam2frame.dot(R_camiFDO2camStd)
        R_camStd2ned = R_frame2ned.dot(R_camStd2frame)
        R_ned2utm = miqtg.R_XYZ(180,0,90) # with utm x,y,z = easting,northing,up
        R_camStd2utm = R_ned2utm.dot(R_camStd2ned).round(5)
        return R_camStd2utm


    def findNavDataForImage(self,data:miqtg.NumDataTimeStamped,videoSmapleSeconds=1):
        """ creates a dict (image_dts) with file name as key and a list of data elements as value. 
            In case of photos the list has only a single entry, for videos it has video duration [sec] / videoSmapleSeconds entries.
            Returns success, image_dts, msg """

        if videoSmapleSeconds <= 0:
            raise Exception("findNavDataForImage: videoSmapleSeconds must be greater 0")

        # create sorted time points
        time_points = list(data.keys())
        time_points.sort()
        
        image_dts = {}
        startSearchIndex = 0
        imagesInRaw = self.imagesInRaw()
        for file in imagesInRaw:
            file_name = os.path.basename(file)

            dt_image = miqtc.parseFileDateTimeAsUTC(file_name)
            dt_image_ts = int(dt_image.timestamp() * 1000)

            runTime = imagesInRaw[file][1] # -1 for photos
            # video
            if imagesInRaw[file][2] in miqtv.video_types and runTime <= 0: # ext
                print("Caution! Could not read video time from file",file) # TODO does this happen? Handle better?

            sampleTimeSecs = 0
            pos_list = []
            go = True
            while go:
                try:
                    pos, startSearchIndex = data.interpolateAtTime(dt_image_ts + sampleTimeSecs * 1000,time_points,startSearchIndex)
                except Exception as e:
                    return False, image_dts, "Could not find image time "+ dt_image.strftime(miqtv.date_formats['mariqt']) +" in "+str(data.len())+" data positions" + str(e.args)
                pos_list.append(pos)
                sampleTimeSecs += videoSmapleSeconds
                if sampleTimeSecs > runTime:
                    go = False
            
            image_dts[file_name] = pos_list
        return True, image_dts, ""


    def createImageNavigationFile(self, nav_path: str, nav_header=miqtv.pos_header['pangaea'], date_format=miqtv.date_formats['pangaea'], overwrite=False, col_separator = "\t", videoSmapleSeconds=1,
                                    offset_x=0, offset_y=0, offset_z=0,angles_in_rad = False):
        """ Creates in /intermediate a text file with 4.5D navigation data for each image, i.e. a single row per photo, video duration [sec] / videoSmapleSeconds rows per video.
            nav_header must be dict containing the keys 'utc','lat','lon','dep'(or 'alt'), optional: 'hgt','uncert' with the respective column headers as values 
            if one of the vehicle x,y,z offsets [m] is not 0 and nav_header also contains 'yaw','pitch','roll' leverarm offsets are compensated for """

        if self.intermediateNavFileExists() and not overwrite:
            return True, "Output file exists: "+self.get_int_nav_file()

        if not os.path.exists(nav_path):
            return False, "Navigation file not found: "+nav_path

        if not os.path.exists(self.dir.to(self.dir.dt.raw)):
            return False, "Image folder not found: "+self.dir.to(self.dir.dt.raw)

        compensatOffsets = False
        if (offset_x!=0 or offset_y!=0 or offset_z!=0) and 'yaw' in nav_header and 'pitch' in nav_header and 'roll' in nav_header:
            compensatOffsets = True

        # check if for missing fields there are const values in header
        const_values = {}
        for navField in miqtv.pos_header['mariqt']:
            respectiveHeaderField = miqtv.col_header["mariqt"][navField]
            if navField not in nav_header and (respectiveHeaderField in self.ifdo_tmp[self.imageSetHeaderKey] and self.ifdo_tmp[self.imageSetHeaderKey][respectiveHeaderField] != ""): 
                const_values[navField] = self.ifdo_tmp[self.imageSetHeaderKey][respectiveHeaderField]

        # Load navigation data
        nav_data, parseMsg = miqtn.readAllPositionsFromFilePath(nav_path, nav_header, date_format,col_separator=col_separator,const_values=const_values)
        if parseMsg != "":
            self.prov.log(parseMsg)
            parseMsg = "\n" + parseMsg

        # find for each image the respective navigation data
        success, image_dts, msg = self.findNavDataForImage(nav_data,videoSmapleSeconds)
        if not success:
            return False, msg + parseMsg

        # compensate leverarm offsets
        if compensatOffsets:

            # load frame attitude data from file
            att_data, parseMsg = miqtn.readAllAttitudesFromFilePath(nav_path, nav_header, date_format,col_separator=col_separator,const_values=const_values,anglesInRad=angles_in_rad)
            if parseMsg != "":
                self.prov.log(parseMsg)
                parseMsg = "\n" + parseMsg

            # find for each image the respective navigation data
            success, image_dts_att, msg = self.findNavDataForImage(att_data,videoSmapleSeconds)
            if not success:
                return False, msg + parseMsg

            # compensate
            for file in image_dts:
                positions = image_dts[file]
                attitudes = image_dts_att[file]
                for i in range(len(positions)):
                    lat = positions[i].lat
                    lon = positions[i].lon
                    dep = positions[i].dep
                    if 'alt' in nav_header and not 'dep' in nav_header:
                        dep *= -1
                    yaw = attitudes[i].yaw
                    pitch = attitudes[i].pitch
                    roll = attitudes[i].roll
                    new_lat,new_lon,new_dep = miqtg.addLeverarms2Latlon(lat,lon,dep,offset_x,offset_y,offset_z,yaw,pitch,roll)
                    positions[i].lat = new_lat
                    positions[i].lon = new_lon
                    positions[i].dep = new_dep

        if len(image_dts) > 0:

            # Check whether depth and height are set
            lat_identical, lon_identical, dep_identical, hgt_identical, dep_not_zero, hgt_not_zero,uncert_not_zero = miqtn.checkPositionContent(nav_data)

            # Write to navigation txt file
            # header
            res = open(self.get_int_nav_file(), "w")
            res.write(miqtv.col_header['mariqt']['img']+"\t"+miqtv.col_header['mariqt']['utc'])
            if 'lat' in nav_header:
                res.write("\t"+miqtv.col_header['mariqt']['lat'])
            if 'lon' in nav_header:
                res.write("\t"+miqtv.col_header['mariqt']['lon'])
            if dep_not_zero and 'dep' in nav_header:
                res.write("\t"+miqtv.col_header['mariqt']['dep'])
            elif dep_not_zero and 'alt' in nav_header:
                res.write("\t"+miqtv.col_header['mariqt']['alt'])
            if hgt_not_zero and 'hgt' in nav_header:
                res.write("\t"+miqtv.col_header['mariqt']['hgt'])
            if uncert_not_zero and 'uncert' in nav_header:
                res.write("\t"+miqtv.col_header['mariqt']['uncert'])
            res.write("\n")
            # data lines
            for file in image_dts:
                for timepoint in image_dts[file]:
                    res.write(file+"\t"+timepoint.dateTime().strftime(miqtv.date_formats['mariqt'])) 
                    if 'lat' in nav_header:
                        res.write("\t"+str(timepoint.lat))
                    if 'lon' in nav_header:
                        res.write("\t"+str(timepoint.lon))
                    if dep_not_zero and 'dep' in nav_header:
                        res.write("\t"+str(timepoint.dep))
                    elif dep_not_zero and 'alt' in nav_header:
                        res.write("\t"+str(timepoint.dep * -1))
                    if hgt_not_zero and 'hgt' in nav_header:
                        res.write("\t"+str(timepoint.hgt))
                    if uncert_not_zero and 'uncert' in nav_header:
                        res.write("\t"+str(timepoint.uncert))
                    res.write("\n")
            res.close()

            # Write to geojson file
            geojson = {'type': 'FeatureCollection', 'name': self.dir.event()+"_"+self.dir.sensor()+"_image-navigation", 'features': []}
            for file in image_dts:
                # photo
                if len(image_dts[file]) == 1:
                    if dep_not_zero:
                        geometry =  {'type': "Point", 'coordinates': 
                                        [float(image_dts[file][0].lon), float(image_dts[file][0].lat), float(image_dts[file][0].dep)]
                                    }
                    else:
                        geometry =  {'type': "Point", 'coordinates': 
                                        [float(image_dts[file][0].lon), float(image_dts[file][0].lat)]
                                    }

                # video
                else:
                    if dep_not_zero:
                        geometry =  {'type': "MultiPoint", 'coordinates':
                                        [[float(d.lon), float(d.lat), float(d.dep)] for d in image_dts[file]]
                                    }
                    else:
                        geometry =  {'type': "MultiPoint", 'coordinates':
                                        [[float(d.lon), float(d.lat)] for d in image_dts[file]]
                                    }

                geojson['features'].append({'type': 'Feature', 'properties': {'id': file}, 'geometry': geometry })
                
            o = open(self.get_int_nav_file().replace(".txt", ".geojson"),
                     "w", errors="ignore", encoding='utf-8')
            json.dump(geojson, o, ensure_ascii=False, indent=4)
            o.close()

            self.prov.addArgument("inputNavigationFile",nav_path,overwrite=True)
            self.prov.log("parsed from inputNavigationFile: " + str(nav_header))
            return True, "Navigation data created" + parseMsg
        else:
            return False, "No image coordinates found" + parseMsg


    def createImageSHA256File(self):
        """ Creates in /intermediate a text file containing per image its SHA256 hash """

        hashes = {}
        if os.path.exists(self.get_int_hash_file()):
            hashes = miqtf.tabFileData(self.get_int_hash_file(), [miqtv.col_header['mariqt']['img'], miqtv.col_header['mariqt']['hash']], key_col=miqtv.col_header['mariqt']['img'])

        imagesInRaw = self.imagesInRaw()
        if len(imagesInRaw) > 0:

            added_hashes = 0
            prog = miqtc.PrintKnownProgressMsg("Checking hashes", len(imagesInRaw),modulo=5)
            for file in imagesInRaw:
                prog.progress()

                if not self.__allUUIDsChecked and not miqti.imageContainsValidUUID(file)[0]:
                    # remove from uuid file
                    if os.path.exists(self.get_int_uuid_file()):
                        res = open(self.get_int_uuid_file(), "r")
                        lines = res.readlines()
                        res.close()
                    else:
                        lines = []
                    i = 0
                    lineNr = i
                    for line in lines:
                        if os.path.basename(file) in line:
                            lineNr = i
                            break
                        i += 1
                    if lineNr != 0:
                        del lines[lineNr]
                        res = open(self.get_int_uuid_file(), "w")
                        res.writelines(lines)
                        res.close()
                    raise Exception( "File " + file + " does not cotain a valid UUID. Run createUUIDFile() first!")

                file_name = os.path.basename(file)
                if file_name in hashes:
                    hashes[file_name] = hashes[file_name][miqtv.col_header['mariqt']['hash']]
                else:
                    hashes[file_name] = miqtc.sha256HashFile(file)
                    added_hashes += 1
            prog.clear()

            if added_hashes > 0:
                hash_file = open(self.get_int_hash_file(), "w")
                hash_file.write(
                    miqtv.col_header['mariqt']['img']+"\t"+miqtv.col_header['mariqt']['hash']+"\n")
                for file_name in hashes:
                    hash_file.write(file_name+"\t"+hashes[file_name]+"\n")
                hash_file.close()
                return True, "Added "+str(added_hashes)+" hashes to hash file"
            else:
                return True, "All hashes exist"

        else:
            return False, "No images found to hash"


    def createStartTimeFile(self):
        """ Creates in /intermediate a text file containing per image its start time parsed from the file name """

        s = miqtc.PrintLoadingMsg("Creating intermediate starttime file ")
        imagesInRaw = self.imagesInRaw()
        if len(imagesInRaw) > 0:

            o = open(self.get_int_startTimes_file(), "w")
            o.write(miqtv.col_header['mariqt']['img'] +
                    "\t"+miqtv.col_header['mariqt']['utc']+"\n")

            for file in imagesInRaw:
                file_name = os.path.basename(file)

                dt = miqtc.parseFileDateTimeAsUTC(file_name)
                o.write(file_name+"\t" +
                        dt.strftime(miqtv.date_formats['mariqt'])+"\n")

            o.close()
            s.stop()
            return True, "Created start time file"
        else:
            s.stop()
            return False, "No images found to read start times"


    def createAcquisitionSettingsEXIFFile(self,override=False):
        """ Creates in /intermediate a text file containing per image a dict of exif tags and their values parsed from the image """

        int_acquisitionSetting_file = self.__get_int_file_prefix() + '_image-acquisition-settings.txt'
        header = {  miqtv.col_header['mariqt']['img']:  miqtv.col_header['mariqt']['img'],
                    miqtv.col_header['mariqt']['acqui']:miqtv.col_header['mariqt']['acqui']}
        if os.path.exists(int_acquisitionSetting_file) and not override:
            self.addItemInfoTabFile(int_acquisitionSetting_file,"\t",header)
            return True, "Result file exists"

        imagesInRaw = self.imagesInRaw()
        if len(imagesInRaw) > 0:

            o = open(int_acquisitionSetting_file, "w")
            o.write(miqtv.col_header['mariqt']['img'] + "\t"+miqtv.col_header['mariqt']['acqui']+"\n")
 
            imagesExifs = miqti.getImagesAllExifValues(imagesInRaw,self.prov)
            for file in imagesExifs:
                file_name = os.path.basename(file)
                o.write(file_name+"\t"+str(imagesExifs[file])+"\n")

            o.close()

            self.addItemInfoTabFile(int_acquisitionSetting_file,"\t",header)
            return True, "Created acquisition settings file"
        else:
            return False, "No images found"


    def imagesInRaw(self):
        return copy.deepcopy(self._imagesInRaw)


    def parseItemDatafromTabFileData(self, items: dict, file: str, cols: list, optional: list = []):
        """ parses data from columns in cols and writes info to items. Column 'image-filename' must be in file and does not need to be passed in cols. 
            File must be tab separated and columns names must equal item field names"""
        tmp_data = miqtf.tabFileData(file, cols+['image-filename']+optional, key_col='image-filename', optional=optional,convert=True)
        self.writeParsedDataToItems(tmp_data,items)


    def praseItemDataFromFile(self,items:dict,file:str,separator:str,header:dict,dateTimeFormat=miqtv.date_formats["mariqt"]):
        """ parses data from from file to items. header dict must be of structure: {<item-field-name>:<column-name>}
            and must contain entry 'image-filename' """
        if not 'image-filename' in header:
            raise Exception("header does not contain 'image-filename'")
        
        tmp_data = miqtf.tabFileData(file, header,col_separator=separator, key_col='image-filename',convert=True)
        miqtc.reformatImageDateTimeStr(tmp_data,format=dateTimeFormat)
        self.writeParsedDataToItems(tmp_data,items)


    def writeParsedDataToItems(self,data:dict,items:dict):
        for img in data:
            if img not in items:
                items[img] = {}
            if isinstance(data[img],list):
                if not isinstance(items[img],list):
                    if items[img] == {}:
                        items[img] = []
                    else:
                        items[img] = [items[img]]
                for v in data[img]:
                    v['image-filename'] = img
                    items[img].append(v)
            else:
                for v in data[img]: # works if data[img] is dict
                    # check if data represents a dict
                    try:
                        val = ast.literal_eval(data[img][v])
                    except Exception:
                        val = data[img][v]
                    if isinstance(items[img],list): # item is already a list (video) but parsed data is not, i.e. parsed data refers to whole video (time independent), i.e. write to first entry
                        items[img][0][v] = val
                    else:
                        items[img][v] = val
                if isinstance(items[img],list): # item is already a list (video) but parsed data is not, i.e. parsed data refers to whole video (time independent), i.e. write to first entry
                        items[img][0]['image-filename'] = img
                else:
                    items[img]['image-filename'] = img


    def intermediateNavFileExists(self):
        if os.path.exists(self.get_int_nav_file()):
            return True
        else:
            return False

    def allNavFieldsInHeader(self):
        for field in self.reqNavFields:
            # multiple options
            if isinstance(field,list):
                valid = False
                for subfield in field:
                    if self.headerFieldFilled(subfield):
                        valid = True
                        break
                if not valid:
                    return False
            # single option
            else:
                if not self.headerFieldFilled(field):
                    return False
        return True

    def headerFieldFilled(self,field:str):
        if field not in self.ifdo_tmp[self.imageSetHeaderKey] or self.ifdo_tmp[self.imageSetHeaderKey][field] == "":
            return False
        return True

    def __initIntermediateFiles(self):
        self.intermediateFilesDef_core = {
            'hashes': {
                'creationFct': 'createImageSHA256File()',
                'suffix': '_image-hashes.txt',
                'cols': [miqtv.col_header['mariqt']['hash']],
                'optional': []},
            'uuids': {
                'creationFct': 'createUUIDFile()',
                'suffix': '_image-uuids.txt',
                'cols': [miqtv.col_header['mariqt']['uuid']],
                'optional': []},
            'datetime': {
                'creationFct': 'createStartTimeFile()',
                'suffix': '_image-start-times.txt',
                'cols': [miqtv.col_header['mariqt']['utc']],
                'optional': []},
            'navigation': {
                'creationFct': 'createImageNavigationFile()',
                'suffix': '_image-navigation.txt',
                'cols': [miqtv.col_header['mariqt']['utc']],
                'optional': [miqtv.col_header['mariqt']['lon'], miqtv.col_header['mariqt']['lat'],miqtv.col_header['mariqt']['dep'], miqtv.col_header['mariqt']['alt'], miqtv.col_header['mariqt']['hgt'], miqtv.col_header['mariqt']['uncert']]},
        }

        self.nonCoreFieldIntermediateItemInfoFiles = []

    def __get_int_file_prefix(self):
        """ depends on 'image-event' and 'image-sensor' so it can change during upate """
        return os.path.join(self.dir.to(self.dir.dt.intermediate), self.ifdo_tmp[self.imageSetHeaderKey]['image-event']+"_"+self.ifdo_tmp[self.imageSetHeaderKey]['image-sensor'])

    def get_int_hash_file(self):
        return self.__get_int_file_prefix() + self.intermediateFilesDef_core['hashes']['suffix']

    def get_int_uuid_file(self):
        return self.__get_int_file_prefix() + self.intermediateFilesDef_core['uuids']['suffix']

    def get_int_startTimes_file(self):
        return self.__get_int_file_prefix() + self.intermediateFilesDef_core['datetime']['suffix']

    def get_int_nav_file(self):
        return self.__get_int_file_prefix() + self.intermediateFilesDef_core['navigation']['suffix']
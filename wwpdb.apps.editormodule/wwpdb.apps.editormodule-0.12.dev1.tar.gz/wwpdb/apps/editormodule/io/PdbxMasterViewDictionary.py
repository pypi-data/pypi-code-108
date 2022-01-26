import sys

from mmcif_utils.persist.PdbxPyIoAdapter import PdbxPyIoAdapter as PdbxIoAdapter
from mmcif.api.PdbxContainers import DataContainer
from mmcif.api.DataCategory import DataCategory


class PdbxMasterViewDictionary(object):
    def __init__(self, verbose=True, log=sys.stderr):
        self.__verbose = verbose
        self.__lfh = log
        self.__myReader = None
        self.__vMaster = None

    def read(self, fName):
        """Reads the master file"""
        self.__myReader = PdbxIoAdapter(self.__verbose, self.__lfh)
        ok = self.__myReader.read(pdbxFilePath=fName)

        masterContainer = self.__myReader.getContainer(containerName="view_master")
        if ok:
            if masterContainer is not None:
                self.__vMaster = self.__parseMaster(masterContainer=masterContainer)
            else:
                return False
        return ok

    def __parseMaster(self, masterContainer):
        """Internalizes the view_master data block"""

        vM = {}

        vCat = masterContainer.getObj("pdbx_view_combine")
        if not vCat:
            return False

        vD = {}
        if vCat.hasAttribute("exptl") and vCat.hasAttribute("viewName") and vCat.hasAttribute("sections"):
            idExptl = vCat.getIndex("exptl")
            idView = vCat.getIndex("viewName")
            idSections = vCat.getIndex("sections")

            for row in vCat.getRowList():
                exptl = row[idExptl]
                viewName = row[idView]
                sections = row[idSections]

                if exptl not in vD:
                    vObj = {}
                    vObj["EXPTL"] = exptl
                    vObj["NAME"] = viewName
                    vObj["SECTIONS"] = sections
                    vD[exptl] = vObj

        vM["EXPTL_VIEW"] = vD

        vCat = masterContainer.getObj("pdbx_view_map_exptl")
        if not vCat:
            return False

        vD = {}
        if vCat.hasAttribute("methods") and vCat.hasAttribute("views"):
            idMeths = vCat.getIndex("methods")
            idViews = vCat.getIndex("views")

            for row in vCat.getRowList():
                methods = row[idMeths]
                views = row[idViews]

                if methods not in vD:
                    vObj = {}
                    vObj["METHODS"] = methods
                    vObj["VIEWS"] = views
                    vD[methods] = vObj

        vM["VIEW_MAP"] = vD

        vCat = masterContainer.getObj("pdbx_view_map_exptl_trans")
        if not vCat:
            return False

        vD = {}
        if vCat.hasAttribute("method") and vCat.hasAttribute("translation"):
            idMeth = vCat.getIndex("method")
            idTrans = vCat.getIndex("translation")

            for row in vCat.getRowList():
                method = row[idMeth]
                translation = row[idTrans]

                if method not in vD:
                    vObj = {}
                    vObj["METHOD"] = method
                    vObj["TRANSLATION"] = translation
                    vD[method] = vObj

        vM["EXPTL_TRANS"] = vD

        return vM

    def getViews(self):
        """Returns the list of views available"""

        ret = []
        for (_key, value) in self.__vMaster["EXPTL_VIEW"].items():
            ret.append(value["EXPTL"])
        return ret

    def getMethods(self):
        """Returns the list of method combinations available"""

        ret = []
        for (_key, value) in self.__vMaster["VIEW_MAP"].items():
            ret.append(value["METHODS"])
        return ret

    def methodsToView(self, exptlList):
        """Translates a list of experimental methods to an internal
        representation that can be passed to generateMethodsView"""

        transD = self.__vMaster["EXPTL_TRANS"]
        # Only list once
        transMeths = set()

        for exp in exptlList:
            if exp in transD:
                trans = transD[exp]["TRANSLATION"]
                if trans != "?":
                    transMeths.add(trans)
            else:
                self.__lfh.write("+ViewMaster: methodsToView unknown method %s\n" % exp)

        # Return comma separated sorted list
        tL = ",".join(sorted(transMeths))

        return tL

    def getDefaultViewName(self, methods):
        """Returns the default view name for a set of methods. For multi view
        methods, returns the first view.  Methods should correspond to
        pdbx_view_map_exptl.methods in the config file"""

        # Get views for the methods
        if methods not in self.__vMaster["VIEW_MAP"]:
            return None

        views = self.__vMaster["VIEW_MAP"][methods]["VIEWS"]
        view = views.split(",")[0]

        viewMaster = self.__vMaster["EXPTL_VIEW"]
        if view not in viewMaster:
            return None

        vName = viewMaster[view]["NAME"]

        return vName

    def generateMethodsView(self, methods):
        """For a set of methods, generate the combined view.  Returns None if a method is not valid"""
        container = None

        # Get views for the methods
        if methods not in self.__vMaster["VIEW_MAP"]:
            return None

        views = self.__vMaster["VIEW_MAP"][methods]["VIEWS"]

        for view in views.split(","):
            container = self.__generateView(view, container)
        return container

    def __generateView(self, exptl, containerIn=None):
        """Returns dictionary container with exptl method"""

        __catMap = {
            "pdbx_display_view_category_info": [
                "view_id",
                "category_menu_display_name",
                "category_name",
                "category_group_display_name",
                "category_display_name",
                "category_cardinality",
            ],
            "pdbx_display_view_item_info": ["view_id", "category_display_name", "item_name", "item_display_name", "read_only_flag"],
        }

        viewMaster = self.__vMaster["EXPTL_VIEW"]
        if exptl not in viewMaster:
            return False
        dataBlocks = viewMaster[exptl]["SECTIONS"]
        vName = viewMaster[exptl]["NAME"]
        if self.__verbose:
            self.__lfh.write("+ViewMaster: generateView for %s with blocks %s\n" % (exptl, dataBlocks))

        if not containerIn:
            # Start by creating the container if not provided
            container = DataContainer("display_view")
            for cat in ["pdbx_display_view_category_info", "pdbx_display_view_item_info"]:
                aCat = DataCategory(cat)
                for attr in __catMap[cat]:
                    aCat.appendAttribute(attr)
                container.append(aCat)
        else:
            container = containerIn
            # What else?

        for blockName in dataBlocks.split(","):
            rContainer = self.__myReader.getContainer(containerName=blockName)
            if rContainer is not None:
                # For each category - append to container
                for (catName, attrList) in __catMap.items():
                    rCat = rContainer.getObj(catName)
                    dCat = container.getObj(catName)
                    if not rCat:
                        if self.__verbose:
                            self.__lfh.write("+ViewMaster: datablock %s category %s missing\n" % (blockName, catName))
                        continue
                    # Get mapping - we know destination row is in order specified
                    for row in rCat.getRowList():
                        cData = ()
                        for attr in attrList:
                            if attr == "view_id":
                                cData += (vName,)
                            else:
                                rAttrId = rCat.getIndex(attr)
                                cData += (row[rAttrId],)
                        dCat.append(cData)
            else:
                if self.__verbose:
                    self.__lfh.write("+ViewMaster: datablock %s missing\n" % (blockName))
        return container

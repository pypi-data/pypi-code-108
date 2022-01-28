"""
Create a new Project
"""
import os
import csv
import importlib
import random
from phases.util.pdict import pdict
from pathlib import Path

import yaml
from phases.util.Logger import LogLevel
from phases.commands.Base import Base
import sys
from math import floor

import pyPhases
from pyPhases import Project, Data


class Run(Base):
    """create a Phase-Project"""

    config = None
    projectFileName = "project.yaml"
    packagePath = os.path.dirname(sys.modules["phases"].__file__)
    forceWrite = False
    debug = False
    phaseName = None
    csvLogFile = "output.csv"
    resume = False
    writer = None
    runSettings = None

    def run(self):
        self.beforeRun()
        self.prepareConfig()

        project = self.createProjectFromConfig(self.config)

        self.runProject(project)

    def parseRunOptions(self):
        if self.options["-o"]:
            self.outputDir = self.options["-o"]
            sys.path.insert(0, self.outputDir)
            self.logDebug("Set Outputdir: %s" % (self.outputDir))
        if self.options["-p"]:
            self.projectFileName = self.options["-p"]
            self.logDebug("Set Projectfile: %s" % (self.projectFileName))
        if self.options["-c"]:
            self.projectConfigFileName = self.options["-c"]
            self.logDebug("Set Config file(s): %s" % (self.projectFileName))
        if self.options["-g"]:
            self.projectGridFile = self.options["-g"]
            self.logDebug("Set Gridfile file: %s" % (self.projectGridFile))
        if self.options["--csv"]:
            self.csvLogFile = self.options["--csv"]
            self.logDebug("Set CSV log file: %s" % (self.csvLogFile))
        if self.options["--set"]:
            self.customConfigValues = self.options["--set"]
            self.logDebug("Custom Values: %s" % (self.customConfigValues))
        if self.options["-v"]:
            self.debug = True
        if self.options["-r"]:
            self.resume = True
        if "<phaseName>" in self.options:
            self.phaseName = self.options["<phaseName>"]

    def beforeRun(self):
        self.parseRunOptions()

    def getPackagePath(self, path):
        d = os.path.dirname(sys.modules["phases"].__file__)
        return os.path.join(d, path)

    def loadClass(self, classOptions, pythonPackage=""):
        name = classOptions["name"]
        path = classOptions["package"]
        options = classOptions["config"] if "config" in classOptions else {}
        leadingDot = "" if classOptions["system"] else "."
        package = None if classOptions["system"] else pythonPackage
        sys.path.insert(0, self.outputDir)
        module = importlib.import_module("%s%s.%s" % (leadingDot, path, name), package=package)
        classObj = getattr(module, name)

        if len(options) > 0:
            return classObj(options)
        else:
            return classObj()

    def getGrid(self, config, path=[], grid=[]):
        config = pdict(config)
        for field in config:
            value = config[field]
            p = path + [field]
            key = field

            if isinstance(value, dict):
                self.getGrid(config[key], p, grid)
            elif isinstance(value, list):
                grid.append((p, value))
            else:
                raise Exception("grid value (%s) not well formed, the first non-dict value needs to be an array" % (path))

        return grid

    def prepareGridFile(self):
        gridFile = open(self.projectGridFile, "r")
        yamlContent = gridFile.read()
        gridFile.close()

        gridConfig = yaml.load(yamlContent, Loader=yaml.SafeLoader)
        if "grid" not in gridConfig:
            raise Exception("The gridfile needs to have the value 'grid' specified")

        self.runSettings = {"parallel": False, "random": False, "seed": 5}

        for _, field in enumerate(gridConfig):
            if field != "grid":
                if field not in self.runSettings:
                    self.logWarning("The run option %s is unknown and will be ignored" % field)
                else:
                    self.runSettings[field] = gridConfig[field]

        return self.getGrid(gridConfig["grid"], [], [])

    def getDataDefinition(self, dataObj):
        dependsOn = []
        if "dependsOn" in dataObj:
            for dependString in dataObj["dependsOn"]:
                dependsOn.append(dependString)

                if dependString not in self.config["config"] and dependString not in Data.dataNames:
                    self.logWarning(
                        "Dependency '%s' for Data could not be found in any config or other defined data" % (dependString)
                    )

        return Data(dataObj["name"], dependsOn)

    def createProjectFromConfig(self, config):
        self.logDebug("Load Project from Config")

        dataDefinitions = {}

        project = Project()
        project.debug = self.debug
        project.name = config["name"]
        project.namespace = config["namespace"]
        project.config = pdict(config["config"])

        for classObj in self.config["publisher"]:
            obj = self.loadClass(classObj, project.name)
            project.registerPublisher(obj)

        for classObj in self.config["exporter"]:
            obj = self.loadClass(classObj, project.name)
            project.registerExporter(obj)

        for classObj in self.config["storage"]:
            obj = self.loadClass(classObj, project.name)
            project.addStorage(obj)

        for stage in self.config["stages"]:
            project.addStage(stage)

        for dataObj in self.config["data"]:
            data = self.getDataDefinition(dataObj)
            dataDefinitions[dataObj["name"]] = data

        for phaseConfig in self.config["phases"]:
            obj = self.loadClass(phaseConfig, project.name)

            if not hasattr(obj, "exportData"):
                raise Exception(
                    "Phase %s was not initialized correctly, maybe you forgot to call the __init__ method after overwriting"
                )

            # add data
            if "exports" in phaseConfig:
                for dataName in phaseConfig["exports"]:
                    if dataName in dataDefinitions:
                        dataDef = dataDefinitions[dataName]
                    else:
                        dataDef = Data(dataName)

                    obj.exportData.append(dataDef)

            project.addPhase(obj, phaseConfig["stage"], phaseConfig["description"])

        return project

    def flattenGrid(self, grid):

        stackSize = 1
        parameterStackingSizes = []
        flattenGrid = []

        # iterate of all Arrays, get the total count of method calls, and update non-array parameter to arrays

        for configPath, gridArray in grid:
            configValues = gridArray
            parameterStackingSizes.append(stackSize)
            stackSize *= len(configValues)

        for i in range(stackSize):

            parameterStack = []
            # get the current Index
            for valueIndex, (configPath, configValues) in enumerate(grid):
                arrayLength = len(configValues)

                # divide be previous stack size, so that it only increase if the prev. stack is finished
                prevStackSize = parameterStackingSizes[valueIndex]
                x = i if prevStackSize == 0 else floor(i / prevStackSize)

                useIndex = x % arrayLength
                parameterValue = configValues[useIndex]
                parameterStack.append((configPath, parameterValue))
            flattenGrid.append(parameterStack)

        return flattenGrid

    def cleanCsv(self):
        if Path(self.csvLogFile).exists():
            Path(self.csvLogFile).unlink()

    def addCsvRow(self, row: dict):
        parent = Path(self.csvLogFile).parent
        if not parent.exists():
            Path(parent).mkdir(parents=True, exist_ok=True)

        if not Path(self.csvLogFile).exists():
            csvFileHanlder = open(self.csvLogFile, "w+", newline="")
            writer = csv.writer(csvFileHanlder)
            writer.writerow(row.keys())
        else:
            csvFileHanlder = open(self.csvLogFile, "a+", newline="")
            writer = csv.writer(csvFileHanlder)

        writer.writerow(row.values())
        csvFileHanlder.close()

    def getLogEntries(self):
        rows = []
        if not Path(self.csvLogFile).exists():
            return []

        with open(self.csvLogFile, "r", newline="") as csvFileHanlder:
            reader = csv.reader(csvFileHanlder)
            rows = list(reader)
            csvFileHanlder.close()
        return rows

    def getLastEntryIndex(self):
        index = len(self.getLogEntries()) - 1
        return max(index, 0)

    def getUnusedIndexes(self, gridLength):
        allIndexes = set(range(gridLength))
        usedIndexes = []
        rows = self.getLogEntries()
        for i, row in enumerate(rows):
            if i > 0:
                usedIndexes.append(int(row[0]))

        return allIndexes - set(usedIndexes)

    def getNextFreeIndex(self, gridLength, seed=5):
        random.seed(seed)
        unusedIndexes = self.getUnusedIndexes(gridLength)
        return random.choice(list(unusedIndexes))

    def runProject(self, project: Project):
        project.logLevel = pyPhases.util.Logger.Logger.verboseLevel

        if self.projectGridFile:
            startWith = 0

            if self.resume:
                startWith = self.getLastEntryIndex()
            else:
                self.cleanCsv()
            grid = self.prepareGridFile()
            configs = self.flattenGrid(grid)
            runCount = len(configs)
            self.log("Grid loaded with %s runs, starting with %i" % (runCount, startWith))

            for rangeIndex in range(startWith, runCount):
                runIndex = rangeIndex
                if self.runSettings["random"]:
                    runId = self.getNextFreeIndex(runCount, self.runSettings["seed"])
                    runIndex = runId - 1
                else:
                    runId = runIndex + 1
                configArray = configs[runIndex]
                outputDics = {"run": runId}
                for configPath, parameterValue in configArray:
                    self.log("set config %s: %s" % (configPath, parameterValue))
                    outputDics["/".join(configPath)] = str(parameterValue)
                    project.config[configPath] = parameterValue
                project.resetConfg()
                project.run(self.phaseName)
                self.log("Run (index: %i) Finished: %i/%i" % (runIndex, rangeIndex + 1, runCount))
                if project.gridOutput:
                    self.log("Result: %s" % (project.gridOutput))
                    project.gridOutput["run"] = runId
                    outputDics.update(project.gridOutput)
                    self.addCsvRow(outputDics)
                    project.gridOutput = {}
        else:
            project.run(self.phaseName)

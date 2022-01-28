"""
Create a new Project
"""

import os
from pathlib import Path
from phases.commands.Base import Base
import sys
from distutils.dir_util import copy_tree


class Create(Base):
    """create a Phase-Project"""

    templateDir = "generate-template/"
    staticFilesDir = "static-template/"
    packagePath = os.path.dirname(sys.modules["phases"].__file__)
    forceWrite = False

    def parseRunOptions(self):
        if self.options["-o"]:
            self.outputDir = self.options["-o"]
            self.logDebug("Set Outputdir: %s" % (self.outputDir))
        if self.options["-p"]:
            self.projectFileName = self.options["-p"]
            self.logDebug("Set Projectfile: %s" % (self.projectFileName))
        if self.options["-f"]:
            self.forceWrite = True

    def beforeRun(self):
        self.parseRunOptions()
        self.templateDir = self.getPackagePath(self.templateDir)
        self.staticFilesDir = self.getPackagePath(self.staticFilesDir)

    def run(self):
        self.beforeRun()
        self.prepareConfig()

        self.copyStaticFiles()
        self.generateInitFiles()
        self.generateFilesFromConfig()

    def copyStaticFiles(self):
        self.log("Copy static files")
        self.logDebug("Copy static files from %s to %s" % (self.staticFilesDir, self.outputDir))

        copy_tree(self.staticFilesDir, self.outputDir)

    def generateInitFiles(self):
        # this method assumes the python files will be saved in {{name}}
        self.log("Generate init Files")
        for package in self.config["packages"]:
            templateFile = open(self.templateDir + "packages.m", "r")
            templateContent = templateFile.read()

            path = self.outputDir + "/" + self.config["name"] + "/" + package["name"] + "/"

            self.writeTemplateFile(path, "__init__.py", templateContent, package)
            templateFile.close()

    def generateFilesFromConfig(self):
        import pystache

        self.log("Generate files for the project with template files")
        outputDir = self.outputDir
        # iterate all template files (*.m files are for manual use)
        pathlist = Path(self.templateDir).glob("**/*.mustache")
        for path in pathlist:
            templateFile = open(path, "r")
            templateContent = templateFile.read()
            templateFile.close()
            pathDiff = os.path.relpath(path.parent, Path(self.templateDir))

            fileName = pystache.render(path.stem, self.config)
            pathDiff = pystache.render(pathDiff, self.config)
            relPath = os.path.join(outputDir, pathDiff)

            self.logDebug("write template %s to path to %s" % (path.stem, relPath))

            if not fileName in self.config:
                self.writeTemplateFile(relPath, fileName, templateContent)
            else:
                for obj in self.config[fileName]:
                    if not obj["system"]:
                        self.log("Create stub for %s/%s" % (fileName, obj["name"]))
                        self.writeTemplateFile(relPath + "/" + fileName, obj["name"] + ".py", templateContent, obj)

    def writeTemplateFile(self, path, filename, tplString, templateObject=None):
        if templateObject == None:
            templateObject = self.config

        if not os.path.exists(path):
            os.makedirs(path)

        fullPath = path + "/" + filename
        self.logDebug("Write file %s" % (fullPath))
        if self.forceWrite or not os.path.isfile(fullPath):
            import pystache

            fileContent = pystache.render(tplString, templateObject)
            file = open(fullPath, "w")
            file.write(fileContent)
            file.close()
        else:
            self.logWarning(
                "File %s allready exists and was not overwritten, use the option -f to force to overwrite it " % (fullPath)
            )

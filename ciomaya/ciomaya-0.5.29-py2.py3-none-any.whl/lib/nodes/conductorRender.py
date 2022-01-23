import importlib
import json
import os
import re
import pymel.core as pm

from ciocore import data as coredata
from ciotemplate.expander import Expander
from ciopath.gpath import Path
from ciopath.gpath_list import PathList
from ciocore.package_environment import PackageEnvironment
from cioseq.sequence import Sequence

import maya.api.OpenMaya as om

from ciomaya.lib import const as k
from ciomaya.lib import layer_utils


def maya_useNewAPI():
    pass


class conductorRender(om.MPxNode):
    # pass

    # static attributes
    aTitle = None

    aChunkSize = None
    aUseCustomRange = None
    aCustomRange = None
    aStartFrame = None
    aEndFrame = None
    aByFrame = None
    aAnimation = None
    aUseScoutFrames = None
    aScoutFrames = None

    aTaskTemplate = None

    aInstanceTypeName = None
    aPreemptible = None
    aProjectName = None
    aRenderLayers = None
    aCurrentRenderLayer = None

    aHostSoftware = None
    aPluginSoftware = None
    aExtraAssets = None

    aAssetScraperName = None
    aAssetScraperActive = None
    aAssetScrapers = None

    aExtraEnvironment = None
    aExtraEnvironmentKey = None
    aExtraEnvironmentValue = None
    aExtraEnvironmentExclusive = None

    aMetadata = None
    aMetadataKey = None
    aMetadataValue = None
 
    aUseUploadDaemon = None

    aEmailAddresses = None
    aEmailAddress = None
    aEmailAddressActive = None

    aRetriesWhenPreempted = None

    aTaskLimit = None
    aDoScrape = None

    aFrameCount = None
    aTaskCount = None
    aScoutTaskCount = None
    aScoutFrameCount = None
    

    aAssetCount = None
    aAssetsSize = None
    aFrameSpec = None
    aScoutSpec = None
    aCurrentRenderer = None
    aCurrentTime = None

    aDestinationDirectory = None
    aLocationTag = None

    aAutosave = None
    aAutosaveTemplate = None
    aCleanupAutosave = None

    aShowTracebacks = None
    aFixturesDirectory = None
    aUseFixtures = None

    aOutput = None

    id = om.MTypeId(0x880500)

    @staticmethod
    def creator():
        return conductorRender()

    @classmethod
    def initialize(cls):
        cls.make_title_att()
        cls.make_frames_atts()
        cls.make_instance_type_att()
        cls.make_project_name_att()
        cls.make_layer_atts()
        cls.make_software_att()
        cls.make_assets_atts()
        cls.make_environment_atts()
        cls.make_task_atts()
        cls.make_upload_flag_atts()
        cls.make_notification_atts()
        cls.make_metadata_atts()
        cls.make_retries_atts()

        cls.make_hidden_atts()
        cls.make_info_atts()

        cls.make_autosave_atts()
        cls.make_developer_atts()
        cls.make_misc_atts()

        cls.make_output_att()

        cls.setup_attribute_affects()

    @staticmethod
    def _make_output_int_att(longname, shortname):
        nAttr = om.MFnNumericAttribute()
        att = nAttr.create(longname, shortname, om.MFnNumericData.kInt)
        nAttr.storable = False
        nAttr.writable = False
        nAttr.readable = True
        om.MPxNode.addAttribute(att)
        return att

    @classmethod
    def make_info_atts(cls):

        cls.aFrameCount = cls._make_output_int_att("frameCount", "frc")
        cls.aTaskCount = cls._make_output_int_att("taskCount", "tsc")
        cls.aScoutTaskCount = cls._make_output_int_att("scoutTaskCount", "stc")
        cls.aScoutFrameCount = cls._make_output_int_att("scoutFrameCount", "sfc")
        
        cls.aAssetCount = cls._make_output_int_att("assetCount", "asc")
        cls.aAssetsSize = cls._make_output_int_att("assetsSize", "asz")

        tAttr = om.MFnTypedAttribute()
        cls.aFrameSpec = tAttr.create("frameSpec", "fms", om.MFnData.kString)
        tAttr.storable = False
        tAttr.writable = False
        tAttr.readable = True
        om.MPxNode.addAttribute(cls.aFrameSpec)

        cls.aScoutSpec = tAttr.create("scoutSpec", "scs", om.MFnData.kString)
        tAttr.storable = False
        tAttr.writable = False
        tAttr.readable = True
        om.MPxNode.addAttribute(cls.aScoutSpec)

    @classmethod
    def make_title_att(cls):
        tAttr = om.MFnTypedAttribute()
        cls.aTitle = tAttr.create("title", "ttl", om.MFnData.kString)
        tAttr.hidden = False
        tAttr.storable = True
        tAttr.readable = True
        tAttr.writable = True
        om.MPxNode.addAttribute(cls.aTitle)

    @classmethod
    def make_instance_type_att(cls):
        tAttr = om.MFnTypedAttribute()
        nAttr = om.MFnNumericAttribute()
        cls.aInstanceTypeName = tAttr.create("instanceTypeName", "itn", om.MFnData.kString)
        tAttr.hidden = False
        tAttr.storable = True
        tAttr.readable = True
        tAttr.writable = True
        om.MPxNode.addAttribute(cls.aInstanceTypeName)

        cls.aPreemptible = nAttr.create("preemptible", "prm", om.MFnNumericData.kBoolean, True)
        nAttr.keyable = False
        nAttr.storable = True
        nAttr.readable = True
        nAttr.writable = True
        om.MPxNode.addAttribute(cls.aPreemptible)

    @classmethod
    def make_project_name_att(cls):
        tAttr = om.MFnTypedAttribute()
        cls.aProjectName = tAttr.create("projectName", "prn", om.MFnData.kString)
        tAttr.hidden = False
        tAttr.storable = True
        tAttr.readable = True
        tAttr.writable = True
        om.MPxNode.addAttribute(cls.aProjectName)

    @classmethod
    def make_layer_atts(cls):
        eAttr = om.MFnEnumAttribute()
        nAttr = om.MFnNumericAttribute()
        tAttr = om.MFnTypedAttribute()

        cls.aRenderLayers = eAttr.create("renderLayers", "rl", k.CURRENT_LAYER)
        eAttr.addField("current", k.CURRENT_LAYER)
        eAttr.addField("renderable", k.RENDERABLE_LAYERS)
        eAttr.hidden = False
        eAttr.keyable = True
        eAttr.storable = True
        om.MPxNode.addAttribute(cls.aRenderLayers)

        cls.aCurrentRenderLayer = nAttr.create("currentRenderLayer", "crl", om.MFnNumericData.kInt)
        nAttr.hidden = False
        nAttr.writable = True
        nAttr.keyable = True
        nAttr.storable = False
        om.MPxNode.addAttribute(cls.aCurrentRenderLayer)

        cls.aCurrentRenderer = tAttr.create("currentRenderer", "cren", om.MFnData.kString)
        tAttr.hidden = True
        tAttr.storable = True
        tAttr.readable = True
        tAttr.writable = True
        om.MPxNode.addAttribute(cls.aCurrentRenderer)

    @classmethod
    def make_software_att(cls):
        tAttr = om.MFnTypedAttribute()
        cls.aHostSoftware = tAttr.create("hostSoftware", "hsw", om.MFnData.kString)
        tAttr.hidden = False
        tAttr.writable = True
        om.MPxNode.addAttribute(cls.aHostSoftware)

        cls.aPluginSoftware = tAttr.create("pluginSoftware", "psw", om.MFnData.kString)
        tAttr.array = True
        tAttr.hidden = False
        tAttr.writable = True
        om.MPxNode.addAttribute(cls.aPluginSoftware)

    @classmethod
    def make_assets_atts(cls):
        cAttr = om.MFnCompoundAttribute()
        tAttr = om.MFnTypedAttribute()
        nAttr = om.MFnNumericAttribute()

        cls.aAssetScraperName = tAttr.create("assetScraperName", "asn", om.MFnData.kString)

        cls.aAssetScraperActive = nAttr.create(
            "assetScraperActive", "asa", om.MFnNumericData.kBoolean, True
        )

        cls.aAssetScrapers = cAttr.create("assetScrapers", "ascs")
        cAttr.array = True
        cAttr.hidden = False
        cAttr.writable = True
        cAttr.addChild(cls.aAssetScraperName)
        cAttr.addChild(cls.aAssetScraperActive)
        om.MPxNode.addAttribute(cls.aAssetScrapers)

        conductorRender.aExtraAssets = tAttr.create("extraAssets", "eass", om.MFnData.kString)
        tAttr.array = True
        tAttr.hidden = False
        tAttr.writable = True
        tAttr.usedAsFilename = True
        om.MPxNode.addAttribute(conductorRender.aExtraAssets)

    @classmethod
    def make_environment_atts(cls):
        cAttr = om.MFnCompoundAttribute()
        tAttr = om.MFnTypedAttribute()
        nAttr = om.MFnNumericAttribute()
        cls.aExtraEnvironmentKey = tAttr.create("extraEnvironmentKey", "eek", om.MFnData.kString)
        cls.aExtraEnvironmentValue = tAttr.create(
            "extraEnvironmentValue", "eev", om.MFnData.kString
        )
        cls.aExtraEnvironmentExclusive = nAttr.create(
            "extraEnvironmentExclusive", "eee", om.MFnNumericData.kBoolean, False
        )
        cls.aExtraEnvironment = cAttr.create("extraEnvironment", "een")

        cAttr.hidden = False
        cAttr.writable = True
        cAttr.array = True
        cAttr.addChild(cls.aExtraEnvironmentKey)
        cAttr.addChild(cls.aExtraEnvironmentValue)
        cAttr.addChild(cls.aExtraEnvironmentExclusive)
        om.MPxNode.addAttribute(cls.aExtraEnvironment)

    @classmethod
    def make_metadata_atts(cls):
        cAttr = om.MFnCompoundAttribute()
        tAttr = om.MFnTypedAttribute()
        cls.aMetadataKey = tAttr.create("metadataKey", "mdk", om.MFnData.kString)
        cls.aMetadataValue = tAttr.create("metadataValue", "mdv", om.MFnData.kString)

        cls.aMetadata = cAttr.create("metadata", "md")

        cAttr.hidden = False
        cAttr.writable = True
        cAttr.array = True
        cAttr.addChild(cls.aMetadataKey)
        cAttr.addChild(cls.aMetadataValue)
        om.MPxNode.addAttribute(cls.aMetadata)

    @classmethod
    def make_retries_atts(cls):
        nAttr = om.MFnNumericAttribute()

        cls.aRetriesWhenPreempted = nAttr.create(
            "retriesWhenPreempted", "rwp", om.MFnNumericData.kInt, 1
        )
        nAttr.writable = True
        nAttr.keyable = True
        nAttr.storable = True
        om.MPxNode.addAttribute(cls.aRetriesWhenPreempted)

    @classmethod
    def make_upload_flag_atts(cls):
        nAttr = om.MFnNumericAttribute()

        cls.aUseUploadDaemon = nAttr.create(
            "useUploadDaemon", "uud", om.MFnNumericData.kBoolean, False
        )
        nAttr.writable = True
        nAttr.keyable = True
        nAttr.storable = True
        om.MPxNode.addAttribute(cls.aUseUploadDaemon)

    @classmethod
    def make_frames_atts(cls):
        tAttr = om.MFnTypedAttribute()
        nAttr = om.MFnNumericAttribute()
        uAttr = om.MFnUnitAttribute()

        cls.aStartFrame = uAttr.create("startFrame", "stf", om.MFnUnitAttribute.kTime, 1)
        uAttr.writable = True
        uAttr.keyable = False
        uAttr.storable = True
        om.MPxNode.addAttribute(cls.aStartFrame)

        cls.aEndFrame = uAttr.create("endFrame", "enf", om.MFnUnitAttribute.kTime, 10)
        uAttr.writable = True
        uAttr.keyable = False
        uAttr.storable = True
        om.MPxNode.addAttribute(cls.aEndFrame)

        cls.aByFrame = nAttr.create("byFrame", "byf", om.MFnNumericData.kInt, 1)
        nAttr.writable = True
        nAttr.keyable = False
        nAttr.storable = True
        om.MPxNode.addAttribute(cls.aByFrame)

        cls.aAnimation = nAttr.create("animation", "ani", om.MFnNumericData.kBoolean)
        nAttr.writable = True
        nAttr.keyable = False
        nAttr.storable = True
        om.MPxNode.addAttribute(cls.aAnimation)

        cls.aChunkSize = nAttr.create("chunkSize", "csz", om.MFnNumericData.kInt, 1)
        nAttr.writable = True
        nAttr.keyable = False
        nAttr.storable = True
        om.MPxNode.addAttribute(cls.aChunkSize)

        cls.aUseCustomRange = nAttr.create(
            "useCustomRange", "ucr", om.MFnNumericData.kBoolean, False
        )
        nAttr.writable = True
        nAttr.keyable = False
        nAttr.storable = True
        om.MPxNode.addAttribute(cls.aUseCustomRange)

        cls.aCustomRange = tAttr.create("customRange", "crn", om.MFnData.kString)
        tAttr.writable = True
        tAttr.storable = True
        om.MPxNode.addAttribute(cls.aCustomRange)

        cls.aUseScoutFrames = nAttr.create(
            "useScoutFrames", "usf", om.MFnNumericData.kBoolean, True
        )
        nAttr.writable = True
        nAttr.keyable = False
        nAttr.storable = True
        om.MPxNode.addAttribute(cls.aUseScoutFrames)

        cls.aScoutFrames = tAttr.create("scoutFrames", "scf", om.MFnData.kString)
        tAttr.writable = True
        tAttr.storable = True
        om.MPxNode.addAttribute(cls.aScoutFrames)

        cls.aCurrentFrame = uAttr.create("currentFrame", "cf", om.MFnUnitAttribute.kTime)
        uAttr.writable = True
        uAttr.keyable = False
        uAttr.storable = True
        om.MPxNode.addAttribute(cls.aCurrentFrame)

    @classmethod
    def make_task_atts(cls):
        tAttr = om.MFnTypedAttribute()
        cls.aTaskTemplate = tAttr.create("taskTemplate", "ttm", om.MFnData.kString)
        tAttr.writable = True
        tAttr.storable = True
        om.MPxNode.addAttribute(cls.aTaskTemplate)

    @classmethod
    def make_notification_atts(cls):
        cAttr = om.MFnCompoundAttribute()
        tAttr = om.MFnTypedAttribute()
        nAttr = om.MFnNumericAttribute()

        cls.aEmailAddress = tAttr.create("emailAddress", "eml", om.MFnData.kString)

        cls.aEmailAddressActive = nAttr.create(
            "emailAddressActive", "emla", om.MFnNumericData.kBoolean, True
        )

        cls.aEmailAddresses = cAttr.create("emailAddresses", "emls")

        cAttr.hidden = False
        cAttr.writable = True
        cAttr.array = True
        cAttr.addChild(cls.aEmailAddress)
        cAttr.addChild(cls.aEmailAddressActive)
        om.MPxNode.addAttribute(cls.aEmailAddresses)

    @classmethod
    def make_misc_atts(cls):
        tAttr = om.MFnTypedAttribute()
        cls.aDestinationDirectory = tAttr.create("destinationDirectory", "ddr", om.MFnData.kString)
        tAttr.writable = True
        tAttr.storable = True
        tAttr.usedAsFilename = True
        om.MPxNode.addAttribute(cls.aDestinationDirectory)

        cls.aLocationTag = tAttr.create("locationTag", "lct", om.MFnData.kString)
        tAttr.writable = True
        tAttr.storable = True
        om.MPxNode.addAttribute(cls.aLocationTag)

    @classmethod
    def make_developer_atts(cls):
        nAttr = om.MFnNumericAttribute()
        tAttr = om.MFnTypedAttribute()

        cls.aShowTracebacks = nAttr.create(
            "showTracebacks", "trc", om.MFnNumericData.kBoolean, False
        )
        nAttr.writable = True
        nAttr.storable = True
        nAttr.hidden = True
        om.MPxNode.addAttribute(cls.aShowTracebacks)

        cls.aUseFixtures = nAttr.create("useFixtures", "ufx", om.MFnNumericData.kBoolean, False)
        nAttr.writable = True
        nAttr.storable = True
        # nAttr.hidden = True
        om.MPxNode.addAttribute(cls.aUseFixtures)

        cls.aFixturesDirectory = tAttr.create("fixturesDirectory", "fdr", om.MFnData.kString)
        tAttr.writable = True
        tAttr.storable = True
        tAttr.usedAsFilename = True
        om.MPxNode.addAttribute(cls.aFixturesDirectory)

    @classmethod
    def make_autosave_atts(cls):

        tAttr = om.MFnTypedAttribute()
        nAttr = om.MFnNumericAttribute()

        cls.aAutosaveTemplate = tAttr.create("autosaveTemplate", "ast", om.MFnData.kString)
        tAttr.writable = True
        tAttr.storable = True
        om.MPxNode.addAttribute(cls.aAutosaveTemplate)

        cls.aAutosave = nAttr.create("autosave", "aus", om.MFnNumericData.kBoolean, True)
        nAttr.writable = True
        nAttr.storable = True
        nAttr.hidden = True
        om.MPxNode.addAttribute(cls.aAutosave)

        cls.aCleanupAutosave = nAttr.create(
            "cleanupAutosave", "cua", om.MFnNumericData.kBoolean, True
        )
        nAttr.writable = True
        nAttr.keyable = True
        nAttr.storable = True
        om.MPxNode.addAttribute(cls.aCleanupAutosave)

    @classmethod
    def make_hidden_atts(cls):
        nAttr = om.MFnNumericAttribute()
        cls.aDoScrape = nAttr.create("doScrape", "dsc", om.MFnNumericData.kBoolean, False)
        nAttr.writable = True
        nAttr.storable = True
        nAttr.hidden = True
        om.MPxNode.addAttribute(cls.aDoScrape)

        cls.aTaskLimit = nAttr.create("taskLimit", "tsl", om.MFnNumericData.kInt, 10)
        nAttr.writable = True
        nAttr.storable = True
        nAttr.hidden = True
        om.MPxNode.addAttribute(cls.aTaskLimit)

    @classmethod
    def make_output_att(cls):
        """
        Output atttribute.
        """
        tAttr = om.MFnTypedAttribute()
        cls.aOutput = tAttr.create("output", "out", om.MFnData.kString)
        tAttr.readable = True
        tAttr.storable = False
        tAttr.writable = False
        tAttr.keyable = False

        om.MPxNode.addAttribute(cls.aOutput)

    @classmethod
    def setup_attribute_affects(cls):
        om.MPxNode.attributeAffects(cls.aTitle, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aInstanceTypeName, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aProjectName, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aChunkSize, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aUseCustomRange, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aCustomRange, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aStartFrame, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aEndFrame, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aByFrame, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aAnimation, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aUseScoutFrames, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aScoutFrames, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aHostSoftware, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aPluginSoftware, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aExtraEnvironment, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aTaskTemplate, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aTaskLimit, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aDoScrape, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aExtraAssets, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aAssetScrapers, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aMetadata, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aRetriesWhenPreempted, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aUseUploadDaemon, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aEmailAddresses, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aDestinationDirectory, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aLocationTag, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aCurrentRenderLayer, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aCurrentRenderer, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aCurrentFrame, cls.aOutput)

        om.MPxNode.attributeAffects(cls.aUseCustomRange, cls.aFrameCount)
        om.MPxNode.attributeAffects(cls.aCustomRange, cls.aFrameCount)
        om.MPxNode.attributeAffects(cls.aStartFrame, cls.aFrameCount)
        om.MPxNode.attributeAffects(cls.aEndFrame, cls.aFrameCount)
        om.MPxNode.attributeAffects(cls.aByFrame, cls.aFrameCount)
        om.MPxNode.attributeAffects(cls.aAnimation, cls.aFrameCount)

        om.MPxNode.attributeAffects(cls.aChunkSize, cls.aTaskCount)
        om.MPxNode.attributeAffects(cls.aUseCustomRange, cls.aTaskCount)
        om.MPxNode.attributeAffects(cls.aCustomRange, cls.aTaskCount)
        om.MPxNode.attributeAffects(cls.aStartFrame, cls.aTaskCount)
        om.MPxNode.attributeAffects(cls.aEndFrame, cls.aTaskCount)
        om.MPxNode.attributeAffects(cls.aByFrame, cls.aTaskCount)
        om.MPxNode.attributeAffects(cls.aAnimation, cls.aTaskCount)

        om.MPxNode.attributeAffects(cls.aUseScoutFrames, cls.aScoutTaskCount)
        om.MPxNode.attributeAffects(cls.aScoutFrames, cls.aScoutTaskCount)
        om.MPxNode.attributeAffects(cls.aChunkSize, cls.aScoutTaskCount)
        om.MPxNode.attributeAffects(cls.aUseCustomRange, cls.aScoutTaskCount)
        om.MPxNode.attributeAffects(cls.aCustomRange, cls.aScoutTaskCount)
        om.MPxNode.attributeAffects(cls.aStartFrame, cls.aScoutTaskCount)
        om.MPxNode.attributeAffects(cls.aEndFrame, cls.aScoutTaskCount)
        om.MPxNode.attributeAffects(cls.aByFrame, cls.aScoutTaskCount)
        om.MPxNode.attributeAffects(cls.aAnimation, cls.aScoutTaskCount)
        om.MPxNode.attributeAffects(cls.aCurrentFrame, cls.aScoutTaskCount)

        om.MPxNode.attributeAffects(cls.aUseScoutFrames, cls.aScoutFrameCount)
        om.MPxNode.attributeAffects(cls.aScoutFrames, cls.aScoutFrameCount)
        om.MPxNode.attributeAffects(cls.aChunkSize, cls.aScoutFrameCount)
        om.MPxNode.attributeAffects(cls.aUseCustomRange, cls.aScoutFrameCount)
        om.MPxNode.attributeAffects(cls.aCustomRange, cls.aScoutFrameCount)
        om.MPxNode.attributeAffects(cls.aStartFrame, cls.aScoutFrameCount)
        om.MPxNode.attributeAffects(cls.aEndFrame, cls.aScoutFrameCount)
        om.MPxNode.attributeAffects(cls.aByFrame, cls.aScoutFrameCount)
        om.MPxNode.attributeAffects(cls.aAnimation, cls.aScoutFrameCount)
        om.MPxNode.attributeAffects(cls.aCurrentFrame, cls.aScoutFrameCount)

        om.MPxNode.attributeAffects(cls.aUseCustomRange, cls.aFrameSpec)
        om.MPxNode.attributeAffects(cls.aCustomRange, cls.aFrameSpec)
        om.MPxNode.attributeAffects(cls.aStartFrame, cls.aFrameSpec)
        om.MPxNode.attributeAffects(cls.aEndFrame, cls.aFrameSpec)
        om.MPxNode.attributeAffects(cls.aByFrame, cls.aFrameSpec)
        om.MPxNode.attributeAffects(cls.aAnimation, cls.aFrameSpec)
        om.MPxNode.attributeAffects(cls.aCurrentFrame, cls.aFrameSpec)

        om.MPxNode.attributeAffects(cls.aUseScoutFrames, cls.aScoutSpec)
        om.MPxNode.attributeAffects(cls.aScoutFrames, cls.aScoutSpec)
        om.MPxNode.attributeAffects(cls.aChunkSize, cls.aScoutSpec)
        om.MPxNode.attributeAffects(cls.aUseCustomRange, cls.aScoutSpec)
        om.MPxNode.attributeAffects(cls.aCustomRange, cls.aScoutSpec)
        om.MPxNode.attributeAffects(cls.aStartFrame, cls.aScoutSpec)
        om.MPxNode.attributeAffects(cls.aEndFrame, cls.aScoutSpec)
        om.MPxNode.attributeAffects(cls.aByFrame, cls.aScoutSpec)
        om.MPxNode.attributeAffects(cls.aAnimation, cls.aScoutSpec)
        om.MPxNode.attributeAffects(cls.aCurrentFrame, cls.aScoutSpec)

    def compute(self, plug, data):
        """Compute output json from input attribs."""
        if not (
            (plug == self.aOutput)
            or (plug == self.aFrameCount)
            or (plug == self.aTaskCount)
            or (plug == self.aScoutTaskCount)
            or (plug == self.aScoutFrameCount)
            or (plug == self.aFrameSpec)
            or (plug == self.aScoutSpec)
        ):
            return None

        try:
            sequence = self.get_sequence(data)
        except (ValueError, TypeError):
            om.MGlobal.displayWarning("Invalid frame sequence specified.")
            return None

        node_name = om.MFnDependencyNode(self.thisMObject()).name()

        scout_sequence = self.get_scout_sequence(data, sequence)
        frame_count = len(sequence)
        task_count = sequence.chunk_count()

        scout_task_count = 0
        scout_frame_count = 0
        scout_tasks_sequence = None
        if scout_sequence:
            scout_chunks = sequence.intersecting_chunks(scout_sequence)
            if scout_chunks:
                scout_tasks_sequence = Sequence.create(
                    ",".join(str(chunk) for chunk in scout_chunks)
                )
                scout_task_count = len(scout_chunks)
                scout_frame_count = len(scout_tasks_sequence)
                
        self.set_frame_info_plugs(data, frame_count, task_count, scout_frame_count, scout_task_count)

        self.set_frame_and_scout_spec(data, sequence, scout_tasks_sequence)

        if plug != self.aOutput:
            return self

        context = self.get_context(data)
        expander = Expander(**context)

        handle = data.outputValue(self.aOutput)

        amendments = self.get_amendments(data, node_name)
        path_amendments = [p["path"] for p in amendments["paths"]]
        env_amendments =  amendments["env"]

        result = {}
        result.update(self.get_software_environment(data, env_amendments))
        result.update(self.get_instance_type(data))
        result.update(self.get_title(data, expander))
        result.update(self.get_project(data))
        result.update(self.get_tasks(data, sequence, context))
        result.update(self.get_upload_paths(data, path_amendments))
        result.update(self.get_upload_flags(data))
        result.update(self.get_retry_policy(data))
        result.update(self.get_notifiations(data))
        result.update(self.get_scout_frames(scout_sequence))
        result.update(self.get_metadata(data, expander))
        result.update(self.get_location_tag(data))
        result.update(self.get_destination_directory(data))

        handle.setString(json.dumps(result))

        data.setClean(plug)
        return self

    @classmethod
    def get_sequence(cls, data):
        chunk_size = data.inputValue(cls.aChunkSize).asInt()
        use_custom_range = data.inputValue(cls.aUseCustomRange).asBool()
        if use_custom_range:
            custom_range = data.inputValue(cls.aCustomRange).asString()
            return Sequence.create(
                custom_range, chunk_size=chunk_size, chunk_strategy="progressions"
            )

        if not data.inputValue(cls.aAnimation).asBool():

            return Sequence.create(
                int(data.inputValue(cls.aCurrentFrame).asTime().asUnits(om.MTime.uiUnit()))
            )

        start_frame = data.inputValue(cls.aStartFrame).asTime().asUnits(om.MTime.uiUnit())
        end_frame = data.inputValue(cls.aEndFrame).asTime().asUnits(om.MTime.uiUnit())
        by_frame = data.inputValue(cls.aByFrame).asInt()
        return Sequence.create(
            int(start_frame),
            int(end_frame),
            by_frame,
            chunk_size=chunk_size,
            chunk_strategy="progressions",
        )

    @classmethod
    def get_scout_sequence(cls, data, main_sequence):
        use_scout_frames = data.inputValue(cls.aUseScoutFrames).asBool()
        if not use_scout_frames:
            return

        scout_frames = data.inputValue(cls.aScoutFrames).asString().strip()

        match = re.compile(r"^auto[, :]+(\d+)$").match(scout_frames)
        if match:
            samples = int(match.group(1))
            return main_sequence.subsample(samples)

        try:
            return Sequence.create(scout_frames)
        except (ValueError, TypeError):
            return

    @classmethod
    def get_scout_frames(cls, scout_sequence):
        return {"scout_frames": ",".join([str(s) for s in scout_sequence or []])}

    @classmethod
    def set_frame_info_plugs(cls, data, frame_count, task_count, scout_frame_count, scout_task_count):
        handle = data.outputValue(cls.aFrameCount)
        handle.setInt(frame_count)
        handle.setClean()
        handle = data.outputValue(cls.aTaskCount)
        handle.setInt(task_count)
        handle.setClean()
        handle = data.outputValue(cls.aScoutFrameCount)
        handle.setInt(scout_frame_count)
        handle.setClean()
        handle = data.outputValue(cls.aScoutTaskCount)
        handle.setInt(scout_task_count)
        handle.setClean()

    @classmethod
    def set_frame_and_scout_spec(cls, data, sequence, scout_sequence):
        handleFrameSpec = data.outputValue(cls.aFrameSpec)
        handleScoutSpec = data.outputValue(cls.aScoutSpec)
        if scout_sequence:
            handleScoutSpec.setString(str(scout_sequence))
        else:
            handleScoutSpec.setString("")
        handleFrameSpec.setString(str(sequence))

        handleScoutSpec.setClean()
        handleFrameSpec.setClean()

    @classmethod
    def get_instance_type(cls, data):
        return {
            "instance_type": data.inputValue(cls.aInstanceTypeName).asString(),
            "preemptible": data.inputValue(cls.aPreemptible).asBool(),
        }

    @classmethod
    def get_title(cls, data, expander):
        title = data.inputValue(cls.aTitle).asString()
        return {"job_title": expander.evaluate(title)}

    @classmethod
    def get_project(cls, data):
        return {"project": data.inputValue(cls.aProjectName).asString()}

    @classmethod
    def get_software_environment(cls, data, env_amendments):
        """Build software environment.
        
        Env components are:
        1. Env derived from package data: Software location etc.
        2. Env amendments added by scrapers: OCIO or maybe others.
        3. Extra env added by user: Something missing that we didn't account for.
        """

        extra_env = cls.get_extra_env(data)
        packages_data = cls.get_software_packages(data)
        packages_data["env"].extend(env_amendments)
        packages_data["env"].extend(extra_env)
        return {
            "environment": dict(packages_data["env"]),
            "software_package_ids": packages_data["ids"],
        }

    @classmethod
    def get_software_packages(cls, data):
        tree_data = coredata.data().get("software")
        paths = []
        host_path = data.inputValue(cls.aHostSoftware).asString()
        paths.append(host_path)
        array_handle = data.inputArrayValue(cls.aPluginSoftware)

        while not array_handle.isDone():
            plugin_path = "{}/{}".format(host_path, array_handle.inputValue().asString())
            paths.append(plugin_path)
            array_handle.next()

        result = {"ids": [], "env": PackageEnvironment()}

        for package in filter(None, [tree_data.find_by_path(path) for path in paths if path]):
            if package:
                result["ids"].append(package["package_id"])
                result["env"].extend(package)
        result["ids"] = list(set(result["ids"]))
        return result

    @classmethod
    def get_extra_env(cls, data):
        result = []
        array_handle = data.inputArrayValue(cls.aExtraEnvironment)
        while not array_handle.isDone():
            name = array_handle.inputValue().child(cls.aExtraEnvironmentKey).asString()
            value = array_handle.inputValue().child(cls.aExtraEnvironmentValue).asString()
            exclusive = array_handle.inputValue().child(cls.aExtraEnvironmentExclusive).asBool()
            name = name.strip()
            value = value.strip()

            if name and value:
                result.append(
                    {
                        "name": name,
                        "value": value,
                        "merge_policy": "exclusive" if exclusive else "append",
                    }
                )
            array_handle.next()
        return result

    def get_context(self, data):
        node = om.MFnDependencyNode(self.thisMObject())
        file_name = pm.sceneName()
        scene_name = os.path.splitext(os.path.split(file_name)[1])[0]

        context = {
            "Camera": self.get_renderable_camera(),
            "Scene": "undefined",
            "SceneFile": "undefined",
            "Object": node.name(),
            "RenderLayer": layer_utils.get_current_layer_name(),
            "WorkspacePath": "undefined",
            "OutputPath": "undefined",
            "Renderer": data.inputValue(self.aCurrentRenderer).asString(),
            "ConductorVersion": pm.moduleInfo(version=True, moduleName="conductor"),
        }

        if file_name:
            context["Scene"] = scene_name
            context["SceneFile"] = Path(file_name).fslash(with_drive=False)
        try:
            context["WorkspacePath"] = Path(pm.workspace(q=True, rd=True)).fslash(with_drive=False)
        except BaseException:
            pass

        try:
            context["OutputPath"] = Path(
                data.inputValue(self.aDestinationDirectory).asString().strip()
            ).fslash(with_drive=False)
        except BaseException:
            pass

        low_context = {}
        for key in context:
            key_lower = key.lower()
            if not key_lower in context:
                low_context[key_lower] = context[key]
        context.update(low_context)
        return context

    @classmethod
    def get_renderable_camera(cls):
        """Get a comma-separated list of renderable cameras."""
        return ",".join([c.name() for c in pm.ls(type="camera") if c.attr("renderable").get()])

    @classmethod
    def get_tasks(cls, data, sequence, context):
        tasks = []
        template = data.inputValue(cls.aTaskTemplate).asString()
        limit = data.inputValue(cls.aTaskLimit).asInt()
        chunks = sequence.chunks()
        if limit < 0:
            limit = len(chunks)
        for i, chunk in enumerate(chunks):
            if i >= limit:
                break
            task_context = {
                "start": str(chunk.start),
                "end": str(chunk.end),
                "step": str(chunk.step),
                "chunk_length": str(len(chunk)),
            }
            task_context.update(context)
            expander = Expander(**task_context)

            tasks.append({"command": expander.evaluate(template), "frames": str(chunk)})
        return {"tasks_data": tasks}

    @classmethod
    def get_upload_flags(cls, data):
        return {
            "local_upload": not data.inputValue(cls.aUseUploadDaemon).asBool(),
        }

    @classmethod
    def get_retry_policy(cls, data):
        return {
            "autoretry_policy": {
                "preempted": {"max_retries": data.inputValue(cls.aRetriesWhenPreempted).asInt()}
            }
        }

    @classmethod
    def get_notifiations(cls, data):
        result = []
        array_handle = data.inputArrayValue(cls.aEmailAddresses)
        while not array_handle.isDone():
            if array_handle.inputValue().child(cls.aEmailAddressActive).asBool():
                value = array_handle.inputValue().child(cls.aEmailAddress).asString().strip()
            if value:
                result.append(value)
            array_handle.next()
        return {"notify": result}

    def get_upload_paths(self, data, path_amendments):
        path_list = PathList()
        path_list.add(*path_amendments)
        path_list.add(*self.get_cached_paths(data))
        path_list.remove_missing()
        path_list.glob()
        return {"upload_paths": sorted([p.fslash() for p in path_list])}

    @classmethod
    def get_amendments(cls, data, node):
        result = {"paths":[], "env":[]}
        if not data.inputValue(cls.aDoScrape).asBool():
            return result
        array_handle = data.inputArrayValue(cls.aAssetScrapers)
        while not array_handle.isDone():
            if array_handle.inputValue().child(cls.aAssetScraperActive).asBool():
                script = array_handle.inputValue().child(cls.aAssetScraperName).asString()
                try:
                    scraper_module = importlib.import_module(script)
                    try:
                        reload(scraper_module)
                    except:
                        importlib.reload(scraper_module)

                    scraper_result = scraper_module.run(node)
                    if scraper_result:
                        result["paths"] += scraper_result["paths"]
                        result["env"] += scraper_result["env"]
                except SyntaxError:
                    om.MGlobal.displayWarning(
                        "Syntax error in the scraper script: '{}'.".format(script)
                    )
                    raise
                except ImportError:
                    om.MGlobal.displayWarning(
                        "Can't load the script '{}' as a Python module. Skipping!!".format(script)
                    )
                except BaseException:
                    om.MGlobal.displayWarning(
                        "Unknown problem with scraper: '{}'. Skipping!!".format(script)
                    )

            array_handle.next()
        return result


    @classmethod
    def get_cached_paths(cls, data):
        result = []
        array_handle = data.inputArrayValue(cls.aExtraAssets)
        while not array_handle.isDone():
            path = array_handle.inputValue().asString().strip()
            if path:
                result.append(path)
            array_handle.next()
        return result

    @classmethod
    def get_metadata(cls, data, expander):
        metadata = {}
        array_handle = data.inputArrayValue(cls.aMetadata)
        while not array_handle.isDone():
            key = array_handle.inputValue().child(cls.aMetadataKey).asString().strip()
            value = array_handle.inputValue().child(cls.aMetadataValue).asString().strip()

            metadata[key] = value

            array_handle.next()

        return {"metadata": expander.evaluate(metadata)}

    @classmethod
    def get_location_tag(cls, data):
        result = data.inputValue(cls.aLocationTag).asString().strip()
        return {"location": result} if result else {}

    @classmethod
    def get_destination_directory(cls, data):
        """
        Return output_path sub object.

        It should be impossible for a path to have backslashes at this point, however, just in case we re-enforce forward slashes.
        """
        output_path = data.inputValue(cls.aDestinationDirectory).asString().strip()
        output_path = Path(output_path).fslash()
        return {"output_path": output_path}

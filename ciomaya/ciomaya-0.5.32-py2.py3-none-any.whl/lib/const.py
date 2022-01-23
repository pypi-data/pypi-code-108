import re

AE_TEXT_WIDTH = 145
AE_SINGLE_WIDTH = 70
AE_TOTAL_WIDTH = AE_TEXT_WIDTH + (AE_SINGLE_WIDTH * 5)
SUPPRESS_EXTRA_ATTS = [
    "useCustomRange",
    "useScoutFrames",
    "doScrape",
    "output",
    "pluginSoftware",
    "instanceTypeName",
    "title",
    "projectName",
    "startFrame",
    "endFrame",
    "byFrame",
    "customRange",
    "scoutFrames",
    "locationTag"
]
USE_FIXTURES = True

CURRENT_LAYER = 0
RENDERABLE_LAYERS = 1
CUSTOM = 2

DEFAULT_TEMPLATE = "Render -r <Renderer> -s <start> -e <end> -b <step> -rl \"<RenderLayer>\" -rd \"<OutputPath>\"  -proj \"<WorkspacePath>\" \"<SceneFile>\""

OTHER_TEMPLATES = [
    "Render -r <Renderer>  -ai:lve 3 -s <start> -e <end> -b <step> -rl \"<RenderLayer>\" -rd \"<OutputPath>\"  -proj \"<WorkspacePath>\" \"<SceneFile>\""
]


DEFAULT_TITLE = "Maya:<Renderer> - <Scene> <RenderLayer>"
DEFAULT_AUTOSAVE_TEMPLATE = "cio_<Scene>"

DEFAULT_INSTANCE_TYPE = "n1-standard-4"

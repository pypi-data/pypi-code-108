"""Type literals for creating Rally WSAPI URL requests.
<https://eu1.rallydev.com/slm/webservice/v2.0/build>

Where "build" is the literal related to type_names.BUILD constant
"""

SCHEDULESTATE = {
    "New": "New",
    "Defined": "Defined",
    "In-Progress": "In-Progress",
    "Completed": "Completed",
    "Accepted": "Accepted"
}

US = "hierarchicalrequirement"
DEFECT = "defect"
TASK = "task"
TESTSET = "testset"
TESTCASE = "testcase"
FEATURE = "portfolioitem/feature"
INITIATIVE = "portfolioitem/initiative"
TRACK = "portfolioitem/track"

USER = "user"
PROJECT = "project"
RELEASE = "release"
ITERATION = "iteration"
MILESTONE = "milestone"
FLOWSTATE = "flowstate"
STATE = "state"
PULLREQUEST = "pullrequest"
BUILDDEFINITION = "builddefinition"
BUILD = "build"
SCMREPO = "scmrepository"
CHANGESET = "changeset"

TYPEDEF = "typedefinition"
ATTDEFINITION = "attributedefinition"
ALLOWEDVALUE = "allowedattributevalue"

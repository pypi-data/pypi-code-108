from datetime import datetime
from typing import Optional, Union, Any

from pydantic import HttpUrl

from rallycli.models import RallyTypeGeneric


class Artifact(RallyTypeGeneric):
    CreationDate: Optional[datetime]
    VersionId: Optional[int]
    Subscription: Optional[Union[RallyTypeGeneric, str]]
    Workspace: Optional[Union[RallyTypeGeneric, str]]
    CreatedBy: Optional[Union[RallyTypeGeneric, str]]
    Description: Optional[str]
    Discussion: Optional[Union[RallyTypeGeneric, str]]
    DisplayColor: Optional[str]
    FormattedID: Optional[str]
    LastUpdateDate: Optional[datetime]
    Milestones: Optional[Union[RallyTypeGeneric, str]]
    Name: Optional[str]
    Notes: Optional[str]
    Owner: Optional[Union[RallyTypeGeneric, str]]
    Project: Optional[Union[RallyTypeGeneric, str]]
    Tags: Optional[Union[RallyTypeGeneric, str]]
    Blocked: Optional[bool]
    BlockedReason: Optional[str]
    Blocker: Optional[Union[RallyTypeGeneric, str]]
    DirectChildrenCount: Optional[int]
    Parent: Optional[Union[RallyTypeGeneric, str]]
    State: Optional[Union[RallyTypeGeneric, str]]


class PortfolioItem(Artifact):
    State: Optional[Union[RallyTypeGeneric, str]]


class Feature(Artifact):
    Release: Optional[Union[RallyTypeGeneric, str]]
    LateChildCount: Optional[int]
    UserStories: Optional[Union[RallyTypeGeneric, HttpUrl]]  # Modificable collection


class SchedulabeArtifact(Artifact):
    AcceptedDate: Optional[datetime]
    ScheduleState: Optional[str]
    Release: Optional[Union[RallyTypeGeneric, str]]
    Iteration: Optional[Union[RallyTypeGeneric, str]]
    FlowState: Optional[Union[RallyTypeGeneric, str]]
    FlowStateChangedDate: Optional[datetime]
    TaskActualTotal: Optional[float]
    TaskEstimateTotal: Optional[float]
    TaskRemainingTotal: Optional[float]
    TaskStatus: Optional[str]
    Tasks: Optional[Union[RallyTypeGeneric, str]]
    TestCaseCount: Optional[int]
    ScheduleStatePrefix: Optional[str]
    PassingTestCaseCount: Optional[int]
    LastBuild: Optional[datetime]
    LastRun: Optional[datetime]


class US(SchedulabeArtifact):
    Expedite: Optional[bool]
    Ready: Optional[bool]
    Children: Optional[Union[RallyTypeGeneric, str]]
    DefectStatus: Optional[str]
    Defects: Optional[Union[RallyTypeGeneric, str]]
    HasParent: Optional[bool]
    InProgressDate: Optional[datetime]
    Recycled: Optional[bool]
    TestCaseStatus: Optional[str]
    TestCases: Optional[Union[RallyTypeGeneric, str]]
    Feature: Optional[Union[RallyTypeGeneric, str]]
    PortfolioItem: Optional[Union[RallyTypeGeneric, str]]


class Defect(SchedulabeArtifact):
    AffectsDoc: Optional[bool]
    Attachments: Optional[Union[RallyTypeGeneric, str]]
    ClosedDate: Optional[datetime]
    DefectSuites: Optional[Union[RallyTypeGeneric, str]]
    Duplicates: Optional[Union[RallyTypeGeneric, str]]
    Environment: Optional[str]
    FixedInBuild: Optional[Union[RallyTypeGeneric, str]]
    FoundInBuild: Optional[Union[RallyTypeGeneric, str]]
    InProgressDate: Optional[datetime]
    OpenedDate: Optional[datetime]
    PlanEstimate: Any
    Priority: Optional[str]
    Recycled: Optional[bool]
    Requirement: Any
    Resolution: Optional[str]
    Severity: Optional[str]
    SubmittedBy: Optional[Union[RallyTypeGeneric, str]]
    TargetBuild: Optional[Union[RallyTypeGeneric, str]]
    TargetDate: Optional[datetime]
    TestCase: Optional[Union[RallyTypeGeneric, str]]
    TestCaseResult: Optional[Union[RallyTypeGeneric, str]]
    TestCaseStatus: Optional[str]
    TestCases: Optional[Union[RallyTypeGeneric, str]]
    VerifiedInBuild: Optional[Union[RallyTypeGeneric, str]]

class Task(Artifact):
    WorkProduct: Optional[Union[RallyTypeGeneric, str]]
    State: Optional[Union[RallyTypeGeneric, str]]
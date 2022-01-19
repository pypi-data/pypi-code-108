"""Module where all interfaces, events and exceptions live."""
# pylint: disable=line-too-long
import six
from plone.autoform.interfaces import IFormFieldProvider
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA
from plone.schema import Email, JSONField
from plone.supermodel import model
from zope.interface import provider, Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema import Int, TextLine

from eea.dexterity.indicators import EEAMessageFactory as _
from eea.schema.slate.field import SlateJSONField


class IEeaDexterityIndicatorsLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IIndicator(Interface):
    """ Marker interface for IMS Indicator
    """


class IIndicatorsFolder(Interface):
    """ Marker interface for IMS Folder
    """


@provider(IFormFieldProvider)
class IIndicatorMetadata(model.Schema):
    """IMS Indicator schema provider"""
    #
    # Metadata
    #
    model.fieldset(
        "metadata",
        label=_(u"Metadata"),
        fields=[
            "temporal_coverage",
            "geo_coverage",
        ],
    )

    temporal_coverage = JSONField(
        title=_(u"Temporal coverage"),
        description=_(
            "This property is read-only and it is automatically "
            "extracted from this indicator's data visualizations."
        ),
        required=False,
        widget="temporal",
        default={"readOnly": True, "temporal": []},
    )

    geo_coverage = JSONField(
        title=_(u"Geographic coverage"),
        description=_(
            "This property is read-only and it is automatically "
            "extracted from this indicator's data visualizations"
        ),
        required=False,
        widget="geolocation",
        default={"readOnly": True, "geolocation": []},
    )

    #
    # Supporting information
    #

    model.fieldset(
        "euro_sdmx_metadata_structure",
        label=_(u"Supporting information"),
        fields=[
            "methodology",
            "data_provenance",
            "data_description",
            "unit_of_measure",
            "policy_relevance",
            "frequency_of_dissemination",
            "accuracy_and_reliability",
            "institutional_mandate",
        ],
    )

    methodology = SlateJSONField(
        title=_(u"Methodology"),
        description=_(
            u"Methodology for indicator calculation and for gap filling. "
            u"Where relevant, include changes to methodology and subsequent implications for comparability. "
            u"Also include uncertainties in relation to the indicator calculation and/or to gap filling) if these are considerable."
        ),
        required=False,
    )

    data_provenance = SlateJSONField(
        title=_(u"Data sources and providers"),
        description=_(
            "This property is read-only and it is automatically "
            "extracted from this indicator's data visualizations"
        ),
        required=False,
    )

    data_description = SlateJSONField(
        title=_(u"Definition"),
        description=_(
            u"Clear definition of the indicator, including references to standards and classifications"
        ),
        required=False,
    )

    unit_of_measure = SlateJSONField(
        title=_(u"Unit of measure"),
        description=_(u"Unit in which data values are measured."),
        required=False,
    )

    policy_relevance = SlateJSONField(
        title=_(u"Policy / environmental relevance"),
        description=_(
            u"The degree to which the indicator meets current/potential needs of users"
        ),
        required=False,
    )

    frequency_of_dissemination = Int(
        title=_(u"Frequency of dissemination"),
        description=(u"Time interval at which the indicator is published (in years, from 1 to 5). E.g. use 1 if it is published yearly, 2 if it is published every 2 years and so on."),
        required=False,
        default=1,
        min=1,
        max=10
    )

    accuracy_and_reliability = SlateJSONField(
        title=_(u"Accuracy and uncertainties"),
        description=_(u"Closeness of computations or estimates to the unknown exact or true values that the statistics were intended to measure; closeness of the initial estimated value to the subsequent estimated value. Includes, among others, comparability (geographical and over time)."),
        required=False
    )

    institutional_mandate = SlateJSONField(
        title=_(u"Institutional mandate"),
        description=_(
            "This property is read-only and it is automatically "
            "extracted from this indicator's data visualizations"
        ),
        required=False,
    )

    #
    # Workflow
    #
    model.fieldset(
        "workflow",
        label=_(u"Workflow"),
        fields=[
            "head_of_group_email",
            "consultation_members_emails",
            "contact",
        ],
    )

    head_of_group_email = Email(
        title=_(u"Head of group email"),
        description=_(u"Email of the head of group (HoG)"),
        required=False,
    )

    consultation_members_emails = TextLine(
        title=_(u"Consultation members emails"),
        description=_(u"List of consultation members emails, separated by commas."),
        required=False,
    )

    contact = Email(
        title=_(u"Contact"),
        description=_(u"Contact info"),
        default="info@eea.europa.eu",
        required=False,
    )
    contact._type = (six.text_type, str)


@provider(IFormFieldProvider)
class IIndicatorLayout(model.Schema):
    """ IMS Indicator blocks layout
    """
    #
    # Layout
    #
    model.fieldset(
        "layout",
        label=_(u"Layout"),
        fields=[
            "blocks",
            "blocks_layout"
        ]
    )

    blocks = JSONField(
        title=_(u"Blocks"),
        description=_(u"The JSON representation of the object blocks."),
        schema=BLOCKS_SCHEMA,
        default={
            u"794c9b24-5cd4-4b9f-a0cd-b796aadc86e8": {
                u"styles": {u"style_name": u"environment-theme-bg"},
                u"fixedLayout": True,
                u"title": u"Content header",
                u"required": True,
                u"disableNewBlocks": True,
                u"as": u"section",
                u"disableInnerButtons": True,
                u"readOnlySettings": True,
                u"instructions": {
                    u"data": u"<p><br/></p>",
                    u"content-type": u"text/html",
                    u"encoding": u"utf8",
                },
                u"fixed": True,
                u"data": {
                    u"blocks": {
                        u"ddde07aa-4e48-4475-94bd-e1a517d26eab": {
                            u"placeholder": u"Indicator title",
                            u"fixed": True,
                            u"disableNewBlocks": True,
                            u"@type": u"title",
                            u"required": True,
                        },
                        u"9f452ca7-172a-42e0-a699-8df0714c89f8": {
                            u"styles": {u"align": u"full"},
                            u"align": u"full",
                            u"@type": u"splitter",
                        },
                        u"12d8c532-f7ad-43fe-ada7-330b2d7a7a39": {
                            u"plaintext": u"Published: date \u2012 25min read",
                            u"required": True,
                            u"disableNewBlocks": True,
                            u"value": [
                                {
                                    u"type": u"p",
                                    u"children": [
                                        {u"text": u""},
                                        {
                                            u"type": u"sup",
                                            u"children": [
                                                {u"text": u"Published: "},
                                                {
                                                    u"type": u"mention",
                                                    u"data": {
                                                        u"widget": u"datetime",
                                                        u"id": u"effective",
                                                    },
                                                    u"children": [{u"text": u"date"}],
                                                },
                                                {u"text": u" \u2012 25min read"},
                                            ],
                                        },
                                        {u"text": u""},
                                    ],
                                }
                            ],
                            u"readOnly": True,
                            u"fixed": True,
                            u"@type": u"slate",
                            u"instructions": {
                                u"data": u"<p><br/></p>",
                                u"content-type": u"text/html",
                                u"encoding": u"utf8",
                            },
                        },
                        u"ca212ba0-859e-4e67-b610-debe0d498b74": {
                            u"fixedLayout": False,
                            u"maxChars": u"500",
                            u"ignoreSpaces": True,
                            u"required": True,
                            u"disableNewBlocks": True,
                            u"as": u"div",
                            u"placeholder": u"Summary",
                            u"title": u"Summary",
                            u"disableInnerButtons": True,
                            u"readOnlySettings": True,
                            u"instructions": {
                                u"data": u"<p>The summary tells the reader about the indicator trend over the examined period and whether or not it helps to achieve the associated policy objective, which can be either quantitative or directional.</p><p>In the absence of a policy objective, it explains whether the trend is in the right or wrong direction in relation to the issue examined.</p><p>If there has been an important change over the most recent period of the time series, e.g. over the last year, this is indicated too.</p><p>Furthermore, if there is a quantitative target, it also indicates whether we are on track to meet it and if not what are the reasons preventing that, e.g. socio-economic drivers, implementation gap etc.</p>",
                                u"content-type": u"text/html",
                                u"encoding": u"utf8",
                            },
                            u"fixed": True,
                            u"data": {
                                u"blocks": {
                                    u"2679fdcc-60be-47ea-90b6-435837793600": {
                                        u"plaintext": u"",
                                        u"placeholder": u"Summary",
                                        u"@type": u"slate",
                                        u"value": [
                                            {
                                                u"type": u"p",
                                                u"children": [{u"text": u""}],
                                            }
                                        ],
                                        u"instructions": {
                                            u"data": u"<p><br/></p>",
                                            u"content-type": u"text/html",
                                            u"encoding": u"utf8",
                                        },
                                    }
                                },
                                u"blocks_layout": {
                                    u"items": [u"2679fdcc-60be-47ea-90b6-435837793600"]
                                },
                            },
                            u"@type": u"group",
                            u"allowedBlocks": [u"slate"],
                        },
                    },
                    u"blocks_layout": {
                        u"items": [
                            u"ddde07aa-4e48-4475-94bd-e1a517d26eab",
                            u"ca212ba0-859e-4e67-b610-debe0d498b74",
                            u"9f452ca7-172a-42e0-a699-8df0714c89f8",
                            u"12d8c532-f7ad-43fe-ada7-330b2d7a7a39",
                        ]
                    },
                },
                u"@type": u"group",
                u"allowedBlocks": [],
            },
            u"1bc4379d-cddb-4120-84ad-5ab025533b12": {
                u"title": u"Aggregate level assessment",
                u"maxChars": u"2000",
                u"ignoreSpaces": True,
                u"required": True,
                u"disableNewBlocks": False,
                u"as": u"section",
                u"placeholder": u"Aggregate level assessment e.g. progress at global, EU level..",
                u"disableInnerButtons": True,
                u"readOnlySettings": True,
                u"instructions": {
                    u"data": u'<p><strong>Assessment text remains at</strong> <strong>the relevant</strong> <strong>aggregate level</strong> <strong>(i.e.</strong> <strong>global, EU, sectoral)</strong> <strong>and addresses the following: </strong></p><ol keys="dkvn8,e367c,f4lpb,9j981,7ai6k,3g3pd" depth="0"><li>Explains in one or two sentences on the environmental rationale of the indicator, i.e. why it matters to the environment that we see an increase/decrease in the value measured.</li><li>Explains in one or two sentences the associated policy objective, which can be either quantitative or directional. More information on the policy objective and related references will be included in the supporting information section. Where there is no policy objective associated with the indicator, i.e. where the indicator addresses an issue that is important for future policy formulation, this text should explain instead why this issue is important.</li><li>IF NECESSARY \u2014 Explains any mismatch between what the indicator tracks and what the policy objective/issue is.</li><li>Qualifies the historical trend (e.g. steady increase) and explains the key reasons (e.g. policies) behind it. If there is a quantitative target it explains if we are on track to meet it.</li><li>IF NECESSARY \u2014 Explains any recent changes to the trend and why.</li><li>IF NECESSARY \u2014 Describes what needs to happen to see adequate progress in future, for instance in order to remain on track to meet targets.</li></ol><p><strong>Please cite your work if</strong> <strong>necessary</strong> <strong>using the EEA citation style (i.e.</strong> <strong>EEA, 2020). A full reference list appears in the supporting information section.</strong></p>',
                    u"content-type": u"text/html",
                    u"encoding": u"utf8",
                },
                u"fixed": True,
                u"data": {
                    u"blocks": {
                        u"deb7e84d-d2c8-4491-90fa-3dc65fe02143": {
                            u"plaintext": u"",
                            u"required": True,
                            u"value": [{u"type": u"p", u"children": [{u"text": u""}]}],
                            u"fixed": True,
                            u"@type": u"slate",
                            u"instructions": {
                                u"data": u"<p><br/></p>",
                                u"content-type": u"text/html",
                                u"encoding": u"utf8",
                            },
                        },
                        u"b0279dde-1ceb-4137-a7f1-5ab7b46a782c": {
                            u"required": True,
                            u"fixed": True,
                            u"disableNewBlocks": True,
                            u"@type": u"dataFigure",
                            u"instructions": {
                                u"data": u"<p>figure instructions goes here</p>",
                                u"content-type": u"text/html",
                                u"encoding": u"utf8",
                            },
                        },
                    },
                    u"blocks_layout": {
                        u"items": [
                            u"b0279dde-1ceb-4137-a7f1-5ab7b46a782c",
                            u"deb7e84d-d2c8-4491-90fa-3dc65fe02143",
                        ]
                    },
                },
                u"@type": u"group",
                u"allowedBlocks": [u"slate"],
            },
            u"8cb090c3-7071-40b8-9c7b-aca2ca3d0ad9": {
                u"title_size": u"h3",
                u"readOnlyTitles": True,
                u"fixedLayout": True,
                u"non_exclusive": False,
                u"collapsed": True,
                u"required": True,
                u"disableNewBlocks": True,
                u"readOnly": False,
                u"title": u"Additional information",
                u"disableInnerButtons": True,
                u"readOnlySettings": True,
                u"instructions": {
                    u"data": u"<p><br/></p>",
                    u"content-type": u"text/html",
                    u"encoding": u"utf8",
                },
                u"fixed": True,
                u"data": {
                    u"blocks": {
                        u"ecdb3bcf-bbe9-4978-b5cf-0b136399d9f8": {
                            u"selected": u"b142c252-337d-4f6e-8ed2-ff4c43601e2f",
                            u"blocks": {
                                u"d9aa8ed3-1c8a-4134-a324-663489a04473": {
                                    u"required": True,
                                    u"global": True,
                                    u"disableNewBlocks": True,
                                    u"readOnlySettings": True,
                                    u"fixed": True,
                                    u"placeholder": u"References and footnotes will appear here",
                                    u"@type": u"slateFootnotes",
                                    u"instructions": {
                                        u"data": u"<p><br/></p>",
                                        u"content-type": u"text/html",
                                        u"encoding": u"utf8",
                                    },
                                }
                            },
                            u"@type": u"accordionPanel",
                            u"blocks_layout": {
                                u"items": [u"d9aa8ed3-1c8a-4134-a324-663489a04473"]
                            },
                            u"title": u"References and footnotes",
                        },
                        u"546a7c35-9188-4d23-94ee-005d97c26f2b": {
                            u"blocks": {
                                u"b5381428-5cae-4199-9ca8-b2e5fa4677d9": {
                                    u"fixedLayout": True,
                                    u"fields": [
                                        {
                                            u"field": {
                                                u"widget": u"slate",
                                                u"id": u"data_description",
                                                u"title": u"Definition",
                                            },
                                            u"showLabel": True,
                                            u"@id": u"62c471fc-128f-4eff-98f9-9e83d9643fc7",
                                        },
                                        {
                                            u"field": {
                                                u"widget": u"slate",
                                                u"id": u"methodology",
                                                u"title": u"Methodology",
                                            },
                                            u"showLabel": True,
                                            u"@id": u"ee67688d-3170-447a-a235-87b4e4ff0928",
                                        },
                                        {
                                            u"field": {
                                                u"widget": u"slate",
                                                u"id": u"policy_relevance",
                                                u"title": u"Policy/environmental relevance",
                                            },
                                            u"showLabel": True,
                                            u"@id": u"b8a8f01c-0669-48e3-955d-d5d62da1b555",
                                        },
                                        {
                                            u"field": {
                                                u"widget": u"slate",
                                                u"id": u"accuracy_and_reliability",
                                                u"title": u"Accuracy and uncertainties",
                                            },
                                            u"showLabel": True,
                                            u"@id": u"d71a80d1-0e65-46d9-8bd4-45aca22bc5dc",
                                        },
                                        {
                                            u"field": {
                                                u"widget": u"slate",
                                                u"id": u"data_provenance",
                                                u"title": u"Data sources and providers",
                                            },
                                            u"showLabel": True,
                                            u"@id": u"97ed11f5-4d31-4462-b3b0-2756a6880d31",
                                        },
                                        {
                                            u"field": {
                                                u"widget": u"slate",
                                                u"id": u"institutional_mandate",
                                                u"title": u"Institutional mandate",
                                            },
                                            u"showLabel": True,
                                            u"@id": u"97ed11f5-4d31-4462-b3b0-2756a6880d32",
                                        },
                                    ],
                                    u"required": True,
                                    u"disableNewBlocks": True,
                                    u"variation": u"default",
                                    u"readOnly": False,
                                    u"title": u"Supporting information",
                                    u"readOnlySettings": True,
                                    u"fixed": True,
                                    u"@type": u"metadataSection",
                                }
                            },
                            u"@type": u"accordionPanel",
                            u"blocks_layout": {
                                u"items": [u"b5381428-5cae-4199-9ca8-b2e5fa4677d9"]
                            },
                            u"title": u"Supporting information",
                        },
                        u"309c5ef9-de09-4759-bc02-802370dfa366": {
                            u"blocks": {
                                u"e047340c-c02e-4247-89ab-5fec73aeb5d3": {
                                    u"gridSize": 12,
                                    u"fixedLayout": True,
                                    u"title": u"Metadata",
                                    u"required": True,
                                    u"disableNewBlocks": True,
                                    u"gridCols": [u"halfWidth", u"halfWidth"],
                                    u"readOnly": False,
                                    u"readOnlySettings": True,
                                    u"fixed": True,
                                    u"data": {
                                        u"blocks": {
                                            u"a8a2323e-32af-426e-9ede-1f17affd664c": {
                                                u"blocks": {
                                                    u"fe145094-71e0-4b3d-82f3-e4d79ac13533": {
                                                        u"fixedLayout": True,
                                                        u"fields": [
                                                            {
                                                                u"field": {
                                                                    u"widget": u"choices",
                                                                    u"id": u"taxonomy_typology",
                                                                    u"title": u"Typology",
                                                                },
                                                                u"showLabel": True,
                                                                u"@id": u"94d638f1-89e1-4f97-aa59-b89b565f60fb",
                                                            },
                                                            {
                                                                u"field": {
                                                                    u"widget": u"array",
                                                                    u"id": u"taxonomy_un_sdgs",
                                                                    u"title": u"UN SDGs",
                                                                },
                                                                u"showLabel": True,
                                                                u"@id": u"ec261e45-f97d-465c-b5a3-0e4aa5187114",
                                                            },
                                                            {
                                                                u"field": {
                                                                    u"widget": u"slate",
                                                                    u"id": u"unit_of_measure",
                                                                    u"title": u"Unit of measure",
                                                                },
                                                                u"showLabel": True,
                                                                u"@id": u"eaef9ff4-0f8d-4360-9d19-5c6a2fd2dd00",
                                                            },
                                                            {
                                                                u"field": {
                                                                    u"widget": u"integer",
                                                                    u"id": u"frequency_of_dissemination",
                                                                    u"title": u"Frequency of dissemination",
                                                                },
                                                                u"showLabel": True,
                                                                u"@id": u"089cd1a1-92d4-47e2-8f6e-4bdb358600fe",
                                                            },
                                                            {
                                                                u"field": {
                                                                    u"widget": u"email",
                                                                    u"id": u"contact",
                                                                    u"title": u"Contact",
                                                                },
                                                                u"showLabel": True,
                                                                u"@id": u"fb4eb0a4-75d8-4d56-b457-45b40b314a84",
                                                            },
                                                        ],
                                                        u"required": True,
                                                        u"disableNewBlocks": True,
                                                        u"variation": u"default",
                                                        u"readOnly": False,
                                                        u"title": u"Right column",
                                                        u"readOnlySettings": True,
                                                        u"fixed": True,
                                                        u"@type": u"metadataSection",
                                                    }
                                                },
                                                u"blocks_layout": {
                                                    u"items": [
                                                        u"fe145094-71e0-4b3d-82f3-e4d79ac13533"
                                                    ]
                                                },
                                            },
                                            u"d9b41958-c17c-45f8-bae1-4140b537a033": {
                                                u"blocks": {
                                                    u"2a56568a-10af-4a5b-8c73-22aa8cb734fe": {
                                                        u"fixedLayout": True,
                                                        u"fields": [
                                                            {
                                                                u"field": {
                                                                    u"widget": u"choices",
                                                                    u"id": u"taxonomy_dpsir",
                                                                    u"title": u"DPSIR",
                                                                },
                                                                u"showLabel": True,
                                                                u"@id": u"48a20e0b-d3bd-41ac-aa06-e97c61071bd2",
                                                            },
                                                            {
                                                                u"field": {
                                                                    u"widget": u"array",
                                                                    u"id": u"taxonomy_themes",
                                                                    u"title": u"Topics",
                                                                },
                                                                u"showLabel": True,
                                                                u"@id": u"34ceb93f-b405-4afd-aeae-a05abd44d355",
                                                            },
                                                            {
                                                                u"field": {
                                                                    u"widget": u"tags",
                                                                    u"id": u"subjects",
                                                                    u"title": u"Tags",
                                                                },
                                                                u"showLabel": True,
                                                                u"@id": u"fd2cdb9e-5ddd-4b46-8382-0d687ce2883e",
                                                            },
                                                            {
                                                                u"field": {
                                                                    u"widget": u"temporal",
                                                                    u"id": u"temporal_coverage",
                                                                    u"title": u"Temporal coverage",
                                                                },
                                                                u"showLabel": True,
                                                                u"@id": u"0e842d87-c9f4-438e-b234-f83141d25ff3",
                                                            },
                                                            {
                                                                u"field": {
                                                                    u"widget": u"geolocation",
                                                                    u"id": u"geo_coverage",
                                                                    u"title": u"Geographic coverage",
                                                                },
                                                                u"showLabel": True,
                                                                u"@id": u"0b8ee8c2-046b-4243-9f11-116df6e0a524",
                                                            },
                                                        ],
                                                        u"required": True,
                                                        u"disableNewBlocks": True,
                                                        u"variation": u"default",
                                                        u"readOnly": False,
                                                        u"title": u"Left column",
                                                        u"readOnlySettings": True,
                                                        u"fixed": True,
                                                        u"@type": u"metadataSection",
                                                    }
                                                },
                                                u"blocks_layout": {
                                                    u"items": [
                                                        u"2a56568a-10af-4a5b-8c73-22aa8cb734fe"
                                                    ]
                                                },
                                            },
                                        },
                                        u"blocks_layout": {
                                            u"items": [
                                                u"d9b41958-c17c-45f8-bae1-4140b537a033",
                                                u"a8a2323e-32af-426e-9ede-1f17affd664c",
                                            ]
                                        },
                                    },
                                    u"@type": u"columnsBlock",
                                    u"instructions": {
                                        u"data": u"<p><br/></p>",
                                        u"content-type": u"text/html",
                                        u"encoding": u"utf8",
                                    },
                                }
                            },
                            u"@type": u"accordionPanel",
                            u"blocks_layout": {
                                u"items": [u"e047340c-c02e-4247-89ab-5fec73aeb5d3"]
                            },
                            u"title": u"Metadata",
                        },
                    },
                    u"blocks_layout": {
                        u"items": [
                            u"546a7c35-9188-4d23-94ee-005d97c26f2b",
                            u"309c5ef9-de09-4759-bc02-802370dfa366",
                            u"ecdb3bcf-bbe9-4978-b5cf-0b136399d9f8",
                        ]
                    },
                },
                u"@type": u"accordion",
                u"allowedBlocks": [],
            },
            u"d060487d-88fc-4f7b-8ea4-003f14e0fb0c": {
                u"title": u"Disaggregate level assessment",
                u"maxChars": u"1000",
                u"ignoreSpaces": True,
                u"required": True,
                u"disableNewBlocks": False,
                u"readOnly": False,
                u"as": u"section",
                u"placeholder": u"Disaggregate level assessment e.g. country, sectoral, regional level assessment",
                u"disableInnerButtons": True,
                u"readOnlySettings": True,
                u"instructions": {
                    u"data": u'<ol keys="9bbul,b1sa2,171og,1c1t5" depth="0"><li>Depending on the indicator context, this text can provide information at country level or, if this is not relevant, at some other level, e.g. sectoral, regional level.</li><li>This text interprets the data represented in the chart, rather than describing results, i.e. it provides explanations for some of the results.</li><li>The text related to progress at this level does not have to be comprehensive.</li><li>If there is no information that adds value to what is already visible there is no need to have any text.</li></ol>',
                    u"content-type": u"text/html",
                    u"encoding": u"utf8",
                },
                u"fixed": True,
                u"data": {
                    u"blocks": {
                        u"d3d49723-14e5-4663-b346-37ee3572f28d": {
                            u"plaintext": u"",
                            u"required": True,
                            u"value": [{u"type": u"p", u"children": [{u"text": u""}]}],
                            u"fixed": True,
                            u"@type": u"slate",
                            u"instructions": {
                                u"data": u"<p><br/></p>",
                                u"content-type": u"text/html",
                                u"encoding": u"utf8",
                            },
                        },
                        u"02ba4a04-fcfe-4968-806f-1dac3119cfef": {
                            u"required": True,
                            u"fixed": True,
                            u"disableNewBlocks": True,
                            u"@type": u"dataFigure",
                            u"instructions": {
                                u"data": u"<p><br/></p>",
                                u"content-type": u"text/html",
                                u"encoding": u"utf8",
                            },
                        },
                    },
                    u"blocks_layout": {
                        u"items": [
                            u"02ba4a04-fcfe-4968-806f-1dac3119cfef",
                            u"d3d49723-14e5-4663-b346-37ee3572f28d",
                        ]
                    },
                },
                u"@type": u"group",
                u"allowedBlocks": [u"slate"],
            },
        },
        required=False,
    )

    blocks_layout = JSONField(
        title=_(u"Blocks Layout"),
        description=_(u"The JSON representation of the object blocks layout."),
        schema=LAYOUT_SCHEMA,
        default={
            u"items": [
                u"794c9b24-5cd4-4b9f-a0cd-b796aadc86e8",
                u"1bc4379d-cddb-4120-84ad-5ab025533b12",
                u"d060487d-88fc-4f7b-8ea4-003f14e0fb0c",
                u"8cb090c3-7071-40b8-9c7b-aca2ca3d0ad9",
            ]
        },
        required=False,
    )

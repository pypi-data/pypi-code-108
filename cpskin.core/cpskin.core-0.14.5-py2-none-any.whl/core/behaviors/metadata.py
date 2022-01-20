# -*- coding: utf-8 -*-
from collective import dexteritytextindexer
from collective.z3cform.keywordwidget.field import Keywords
from cpskin.locales import CPSkinMessageFactory as _
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.supermodel import model
from z3c.form.browser.orderedselect import OrderedSelectFieldWidget
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.interface import alsoProvides
from zope.interface import provider


class IStandardTags(model.Schema):
    model.fieldset(
        'categorization',
        label=_(u'label_schema_categorization', default=u'Categorization'),
        fields=('standardTags',),
    )

    form.widget(
        standardTags='collective.z3cform.keywordwidget.widget.KeywordFieldWidget')  # noqa
    standardTags = Keywords(
        title=_(u'label_standardTags', default=u'Standard Tags'),
        description=_(
            u'help_standard_tags',
            default=u'Standard Tags are used for webmaster '
                    u'organization of content.',
        ),
        required=False,
        # Automatically get the index in catalog by name
        index_name='standardTags',
    )


class IHiddenTags(model.Schema):
    model.fieldset(
        'categorization',
        label=_(u'label_schema_categorization', default=u'Categorization'),
        fields=('hiddenTags',),
    )

    form.widget(
        hiddenTags='collective.z3cform.keywordwidget.widget.KeywordFieldWidget')  # noqa
    hiddenTags = Keywords(
        title=_(u'label_hidden_tags', default=u'Hidden Tags'),
        description=_(
            u'help_hidden_tags',
            default=u'Hidden Tags are used for webmaster '
                    u'organization of content.',
        ),
        required=False,
        # Automatically get the index in catalog by name
        index_name='hiddenTags',
    )


class IISearchTags(model.Schema):
    model.fieldset(
        'categorization',
        label=_(u'label_schema_categorization', default=u'Categorization'),
        fields=('isearchTags',),
    )

    form.widget(
        isearchTags='collective.z3cform.keywordwidget.widget.KeywordFieldWidget')  # noqa
    isearchTags = Keywords(
        title=_(u'label_isearch_tags', default=u'I Search Tags'),
        description=_(
            u'help_isearch_tags',
            default=u'I Search Tags are used for webmaster '
                    u'organization of content.'
        ),
        required=False,
        index_name='isearchTags',
    )


class IIAmTags(model.Schema):
    model.fieldset(
        'categorization',
        label=_(u'label_schema_categorization', default=u'Categorization'),
        fields=('iamTags',),
    )

    form.widget(
        iamTags='collective.z3cform.keywordwidget.widget.KeywordFieldWidget')
    iamTags = Keywords(
        title=_(u'label_iam_tags', default=u'I Am Tags'),
        description=_(
            u'help_iam_tags',
            default=u'I Am Tags are used for webmaster '
                    u'organization of content.',
        ),
        required=False,
        # Automatically get the index in catalog by name
        index_name='iamTags',
    )


alsoProvides(IStandardTags, IFormFieldProvider)
alsoProvides(IHiddenTags, IFormFieldProvider)
alsoProvides(IISearchTags, IFormFieldProvider)
alsoProvides(IIAmTags, IFormFieldProvider)

# This is an old interface but there are always some objects that were registered with it (in Florenne) so when we want to register some new contact (with linked contact), sometimes that crash.
# SUP-7077
class IUseKeywordHomepage(model.Schema):
    pass


@provider(IFormFieldProvider)
class IRelatedContacts(model.Schema):
    model.fieldset(
        'related_contacts',
        label=_(u'Related contacts'),
        fields=('aboveContentContact', 'aboveVisbileFields',
                'belowContentContact', 'belowVisbileFields',
                'see_map', 'see_logo_in_popup'),
    )

    aboveContentContact = RelationList(
        title=u'Above content related contact',
        default=[],
        value_type=RelationChoice(
            title=_(u'Related'),
            source=ObjPathSourceBinder(
                portal_type=('person', 'organization', 'held_position')
            )
        ),
        required=False,
    )

    form.widget(aboveVisbileFields=OrderedSelectFieldWidget)
    aboveVisbileFields = schema.Tuple(
        title=_(u'Visible fields for above viewlet'),
        description=_(u'Please select which fields should be visible.'),
        required=False,
        default=('street', 'number', 'zip_code', 'city', 'phone', 'cell_phone',
                 'fax', 'email', 'website', 'activity'),
        value_type=schema.Choice(
            vocabulary=u'cpskin.core.vocabularies.contact_fields'
        )
    )

    belowContentContact = RelationList(
        title=u'Below content related contact',
        default=[],
        value_type=RelationChoice(
            title=_(u'Related'),
            source=ObjPathSourceBinder(
                portal_type=('person', 'organization', 'held_position')
            )
        ),
        required=False,
    )

    form.widget(belowVisbileFields=OrderedSelectFieldWidget)
    belowVisbileFields = schema.Tuple(
        title=_(u'Visible fields for below viewlet'),
        description=_(u'Please select which fields should be visible.'),
        required=False,
        default=('title',),
        value_type=schema.Choice(
            vocabulary=u'cpskin.core.vocabularies.contact_fields'
        )
    )

    see_map = schema.Bool(
        title=_(u'See map'),
        description=_(u'Do you want to map with links of contacts ?'),
        required=False,
        default=True
    )

    see_logo_in_popup = schema.Bool(
        title=_(u'See logo on map popup'),
        description=_(u'Do you want to logo of contact on the popup on map ?'),
        required=False,
        default=True
    )


@provider(IFormFieldProvider)
class IAdditionalSearchableText(model.Schema):
    model.fieldset(
        'categorization',
        label=_(u'label_schema_categorization', default=u'Categorization'),
        fields=('additional_searchable_text',),
    )
    dexteritytextindexer.searchable('additional_searchable_text')
    additional_searchable_text = schema.Text(
        title=_(u'Additional searchable text'),
        required=False)

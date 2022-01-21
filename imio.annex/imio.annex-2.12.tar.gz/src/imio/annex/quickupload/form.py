# -*- coding: utf-8 -*-
"""
imio.annex
----------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from plone.z3cform.layout import FormWrapper
from z3c.form import field
from z3c.form.form import Form
from z3c.form.interfaces import HIDDEN_MODE
from zope import schema
from zope.interface import Interface
from collective.iconifiedcategory import _ as ICMF
from collective.z3cform.select2.widget.widget import SingleSelect2FieldWidget
from collective.iconifiedcategory.widget.widget import CategoryTitleFieldWidget

from imio.annex.quickupload import utils


class IQuickUpload(Interface):

    title = schema.TextLine(
        title=u'Title',
        required=True,
    )

    content_category = schema.Choice(
        title=ICMF(u'Category'),
        source='collective.iconifiedcategory.categories',
        required=True,
    )

    default_titles = schema.Choice(
        title=ICMF(u'Default title'),
        vocabulary='collective.iconifiedcategory.category_titles',
        required=False,
    )

    description = schema.Text(
        title=u'Description',
        required=False,
    )


class QuickUploadForm(Form):
    fields = field.Fields(IQuickUpload)
    fields['content_category'].widgetFactory = SingleSelect2FieldWidget
    fields['default_titles'].widgetFactory = CategoryTitleFieldWidget
    fields['default_titles'].mode = HIDDEN_MODE
    ignoreContext = True

    @property
    def typeupload(self):
        return self.request.get('typeupload')

    @property
    def is_iconified_categorized(self):
        return utils.is_iconified_categorized(self.typeupload)

    def update(self):
        super(QuickUploadForm, self).update()
        if self.is_iconified_categorized is False:
            del self.widgets['content_category']
            del self.widgets['default_titles']


class QuickUploadFormView(FormWrapper):
    form = QuickUploadForm

    def update(self):
        super(QuickUploadFormView, self).update()

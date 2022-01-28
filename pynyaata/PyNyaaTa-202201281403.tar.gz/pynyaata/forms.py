from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SelectField
from wtforms.fields.html5 import SearchField, URLField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    q = SearchField('search', validators=[DataRequired()])


class DeleteForm(FlaskForm):
    class Meta:
        csrf = False

    id = HiddenField('id', validators=[DataRequired()])


class EditForm(FlaskForm):
    id = HiddenField('id')
    folder = SelectField('folder', validators=[DataRequired()])
    name = StringField('name', validators=[DataRequired()])
    link = URLField('link', validators=[DataRequired()])
    season = StringField('season', validators=[DataRequired()])
    comment = StringField('comment')
    keyword = StringField('keyword', validators=[DataRequired()])


class FolderEditForm(FlaskForm):
    id = HiddenField('id')
    name = StringField('name', validators=[DataRequired()])
    path = StringField('path')


class FolderDeleteForm(FlaskForm):
    class Meta:
        csrf = False

    id = HiddenField('id', validators=[DataRequired()])

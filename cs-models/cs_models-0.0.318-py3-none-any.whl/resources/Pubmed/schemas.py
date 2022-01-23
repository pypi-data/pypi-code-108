from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load
)
from ...utils.utils import pre_load_date_fields


class PubmedResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    pubmed_id = fields.Integer(required=True)
    doi = fields.String(allow_none=True)
    publication_type = fields.String(allow_none=True)
    date_created = fields.DateTime(allow_none=True)
    date_completed = fields.DateTime(allow_none=True)
    date_revised = fields.DateTime(allow_none=True)
    journal_issn = fields.String(allow_none=True)
    journal_volume = fields.String(allow_none=True)
    journal_issue = fields.String(allow_none=True)
    journal_title = fields.String(allow_none=True)
    journal_title_iso_abbrev = fields.String(allow_none=True)
    title = fields.String(required=True)
    abstract = fields.String(allow_none=True)
    author_list = fields.String(allow_none=True)
    keyword_list = fields.String(allow_none=True)
    chemical_list = fields.String(allow_none=True)
    mesh_list = fields.String(allow_none=True)
    coi_statement = fields.String(allow_none=True)
    updated_at = fields.DateTime()

    @pre_load
    def convert_string_to_datetime(self, in_data):
        date_fields = ['date_created', 'date_completed', 'date_revised']

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format='%Y%m%d',
        )
        return in_data

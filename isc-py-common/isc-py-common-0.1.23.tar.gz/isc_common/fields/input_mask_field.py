from django.db.models import TextField, NOT_PROVIDED
from django.utils.translation import gettext_lazy as _


class InputMaskField(TextField):
    description = "Input Mask"

    def get_internal_type(self):
        return "TextField"

    def __init__(self,
                 verbose_name=None,
                 name=None,
                 primary_key=False,
                 max_length=255,
                 unique=False,
                 blank=False,
                 null=False,
                 db_index=False,
                 rel=None,
                 default=NOT_PROVIDED,
                 editable=True,
                 serialize=True,
                 unique_for_date=None,
                 unique_for_month=None,
                 unique_for_year=None,
                 choices=None,
                 help_text='',
                 db_column=None,
                 db_tablespace=None,
                 validators=(),
                 error_messages=None
                 ):
        super().__init__(
            verbose_name=verbose_name,
            name=name,
            primary_key=primary_key,
            max_length=max_length,
            unique=unique,
            blank=blank,
            null=null,
            db_index=db_index,
            rel=rel,
            default=default,
            editable=editable,
            serialize=serialize,
            unique_for_date=unique_for_date,
            unique_for_month=unique_for_month,
            unique_for_year=unique_for_year,
            choices=choices,
            help_text=help_text,
            db_column=db_column,
            db_tablespace=db_tablespace,
            auto_created=False,
            validators=validators,
            error_messages=error_messages
        )

from django.urls import reverse


def render_autocomplete_badge(instance, present=None) -> str:
    return '<a href="{0}" target="_blank" title="{1}">{1}</a>'.format(
        reverse(
            "admin:{0.app_label}_{0.model_name}_change".format(instance._meta),
            args=(instance.id,),
        ),
        present or str(instance),
    )

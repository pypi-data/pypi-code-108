from typing import Any, Dict, List, Optional

from django.conf import settings

from templated_email import send_templated_mail

from aleksis.core.util.core_helpers import get_site_preferences, process_custom_context_processors


def send_email(
    template_name: str,
    recipient_list: List[str],
    context: Dict[str, Any],
    from_email: Optional[str] = None,
    **kwargs,
):
    """Send templated email with data from context processors."""
    processed_context = process_custom_context_processors(settings.PDF_CONTEXT_PROCESSORS)
    processed_context.update(context)
    if not from_email:
        from_address = get_site_preferences()["mail__address"]
        from_name = get_site_preferences()["general__title"]
        from_email = f"{from_name} <{from_address}>"
    return send_templated_mail(
        template_name=template_name,
        from_email=from_email,
        recipient_list=recipient_list,
        context=processed_context,
        **kwargs,
    )

from django.template.loader_tags import register


@register.inclusion_tag("components/msgbox.html")
def msg_box(msg, status="success", icon="info"):
    return {"msg": msg, "status": status, "icon": icon}

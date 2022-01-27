from django.views.generic import TemplateView


class SiteConfigsIndexView(TemplateView):
    template_name = "siteconfigs/index.html"

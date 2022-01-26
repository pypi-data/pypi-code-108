from django.contrib import admin
from djangoldp.admin import DjangoLDPAdmin
from djangoldp.models import Model
from .models import JobOffer
from .signals import post_save_joboffer_with_skills


class JobOfferAdmin(DjangoLDPAdmin):
    list_display = ('urlid', 'title', 'author')
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    search_fields = ['urlid', 'title', 'author__urlid', 'skills__name', 'description']
    ordering = ['urlid']

    '''
    def get_queryset(self, request):
        # Hide distant jobs
        queryset = super(JobOfferAdmin, self).get_queryset(request)
        internal_ids = [x.pk for x in queryset if not Model.is_external(x)]
        return queryset.filter(pk__in=internal_ids)
    '''

    # when the JobOffer is saved and all related items attached,
    # send out notifications to users with matching skills
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if isinstance(form.instance, JobOffer):
            post_save_joboffer_with_skills.send(sender=JobOffer, instance=form.instance, created=True)

admin.site.register(JobOffer, JobOfferAdmin)

from django.contrib import admin
from djangoldp.admin import DjangoLDPAdmin
from djangoldp.models import Model
from djangoldp_energiepartagee.models import Actor, Contribution


class ActorAdmin(DjangoLDPAdmin):
    list_display = ('shortname', 'longname', 'updatedate', 'createdate')
    search_fields = ['shortname', 'longname']

class ContributionAdmin(DjangoLDPAdmin):
    list_display = ('actor', 'year', 'updatedate', 'createdate')
    search_fields = ['actor__longname','actor__shortname']

admin.site.register(Actor, ActorAdmin)
admin.site.register(Contribution, ContributionAdmin)

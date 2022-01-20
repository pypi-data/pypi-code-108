from django.contrib import admin
from reversion.admin import VersionAdmin

from huscy.project_ethics import models


@admin.register(models.EthicBoard)
class EthicBoardAdmin(VersionAdmin, admin.ModelAdmin):
    pass


@admin.register(models.Ethic)
class EthicAdmin(VersionAdmin, admin.ModelAdmin):
    list_display = 'id', 'project_title', 'ethic_board', 'code'
    search_fields = 'code', 'project__title'

    def project_title(self, ethic):
        return ethic.project.title


@admin.register(models.EthicFile)
class EthicFileAdmin(VersionAdmin, admin.ModelAdmin):
    date_hierarchy = "uploaded_at"
    fields = 'filetype', 'filehandle', 'filename'
    list_display = ('id', 'project_title', 'ethic_board', 'ethic_code', 'filetype', 'filename',
                    'uploaded_at', 'uploaded_by')
    list_display_links = 'id', 'filetype', 'filename'
    readonly_fields = 'filehandle',
    search_fields = 'ethic__project__title', 'ethic__code', 'filename', 'uploaded_by'

    def has_add_permission(self, request, ethic_file=None):
        return False

    def ethic_board(self, ethic_file):
        return ethic_file.ethic.ethic_board.name

    def ethic_code(self, ethic_file):
        return ethic_file.ethic.code

    def project_title(self, ethic_file):
        return ethic_file.ethic.project.title

from django import forms
from django.conf.urls import url
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html

from .utils.models import get_all_available_major_version
from vtb_django_utils.utils.consts import DATETIME_SHORT_FORMAT
from .utils.consts import START_VERSION, RE_VERSION, REL_VERSION_FIELD_END, REL_VERSION_PATTERN_FIELD_END, \
    ERR_VERSION_FORMAT
from .utils.strings import is_last_version_less


class VersionMixin(admin.ModelAdmin):
    """ Добавляет функционал версий модели в админке """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_display += ['last_version', 'is_version_changed', 'save_version']
        self.readonly_fields += ('last_version', 'version_create_dt', 'changed_by_user', 'is_version_changed',
                                 'save_version',)
        self.fields = (('last_version', 'version_create_dt', 'changed_by_user', 'save_version'),
                       ('is_version_changed',),
                       ) + self.fields

    @staticmethod
    def last_version(obj):
        return obj.last_version.version if obj.last_version else ''

    @staticmethod
    def version_create_dt(obj):
        return obj.last_version.create_dt.strftime(DATETIME_SHORT_FORMAT) if obj.last_version else ''

    @staticmethod
    def changed_by_user(obj):
        return obj.last_version.changed_by_user if obj.last_version else ''

    @staticmethod
    def is_version_changed(obj):
        return format_html(
            '''
            <div style="color: crimson">
            Текущая версия не сохранена (и не используется при запросе <span style="font-weight: bold">json</span>)
            </div>
            '''
        ) if obj.is_version_changed else ''

    @staticmethod
    def save_version(obj):
        return format_html(
            '<a class="button" href="{}">Save version</a> ',
            reverse(f'admin:{obj.__class__.__name__.lower()}-form_save_version', args=[obj.pk]),
        )

    def form_save_version(self, request, obj_id):
        referer = request.META.get('HTTP_REFERER')
        if not obj_id or obj_id == 'None':
            messages.add_message(request, messages.ERROR, 'First you need to save the object')
            return HttpResponseRedirect(referer)

        mode = request.POST.get('mode')
        if not mode:
            instance = self.model.objects.get(pk=obj_id)
            return TemplateResponse(request, 'get_version_name.html', {
                'class_name': self.model.__name__.capitalize(),
                'mode': 'get_version_name',
                'referer': referer,
                'version': instance.next_version_str,
                'last_version': instance.last_version.version if instance.last_version else START_VERSION,
                'is_start_version': not instance.last_version,
            })

        elif mode == 'get_version_name':
            version = request.POST.get('version')
            last_version = request.POST.get('last_version')
            is_start_version = request.POST.get('is_start_version')
            referer = request.POST.get('referer')
            err_msg = ''
            if not RE_VERSION.match(version):
                err_msg = ERR_VERSION_FORMAT.format(version)
            elif is_start_version != 'True' and not is_last_version_less(last_version, version):
                err_msg = (
                    f'The new version must be larger than the previous one (It is false: {last_version} < {version})')

            if err_msg:
                return TemplateResponse(request, 'get_version_name.html', {
                    'error': err_msg,
                    'mode': 'get_version_name',
                    'referer': referer,
                    'version': version,
                    'last_version': last_version,
                })
            else:
                instance = self.model.objects.get(pk=obj_id)
                instance.create_or_update_version(version)
                messages.add_message(request, messages.INFO, 'Version saved')

        return HttpResponseRedirect(referer)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(
                r'^(?P<obj_id>.+)/form_save_version/$',
                self.admin_site.admin_view(self.form_save_version),
                name=f'{self.model.__name__.lower()}-form_save_version',
            ),
        ]
        return custom_urls + urls


# noinspection PyUnresolvedReferences
class RelModelsVersionSelectMixin:
    """ Работа со связанными версионными моделями """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_version()
        self.setup_version_pattern()

    def setup_version(self):
        """ Собирает кверисеты для выбора версий """
        for rel_field in self.instance.rel_versioned_fields:
            # если инстанс основной модели сохранен и выбран инстанс связанной модели, то подтягиваем ее версии
            if self.instance and (rel_field_object := getattr(self.instance, rel_field)):
                self.fields[f'{rel_field}{REL_VERSION_FIELD_END}'].queryset = rel_field_object.versions.all()
            # если нет, то пустой список
            else:
                self.fields[f'{rel_field}{REL_VERSION_FIELD_END}'].queryset = (
                    self.fields[f'{rel_field}{REL_VERSION_FIELD_END}'].queryset.none())

    def setup_version_pattern(self):
        """ Собирает кверисеты для выбора шаблонов версий """
        for rel_field in self.instance.rel_versioned_fields:
            version_pattern_name = f'{rel_field}{REL_VERSION_PATTERN_FIELD_END}'
            self.fields[version_pattern_name] = forms.ChoiceField(widget=forms.Select, required=False, initial='')
            if self.instance:
                all_versions = []
                if rel_field_object := getattr(self.instance, rel_field):
                    all_versions = get_all_available_major_version(
                        rel_field_object.versions.values_list('version_arr', flat=True))
                initial = [('', ''), ] if all_versions else [('', ''), ('1', '1.X.X')]
                self.fields[version_pattern_name].choices = initial + all_versions
            else:
                self.fields[version_pattern_name].choices = [('', ''), ('1', '1.X.X')]

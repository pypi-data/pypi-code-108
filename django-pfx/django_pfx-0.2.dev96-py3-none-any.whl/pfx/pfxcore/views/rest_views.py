import json
import logging
from datetime import date

from django.db import IntegrityError, transaction
from django.db.models import DateField, ForeignKey, Manager, Model, Q
from django.http import JsonResponse
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _
from django.views import View

from pfx.pfxcore.decorator import rest_api
from pfx.pfxcore.exceptions import APIError, ForbiddenError, UnauthorizedError
from pfx.pfxcore.model_resolver import (
    MetaResolver,
    ObjectResolver,
    ResolverValidationError,
)
from pfx.pfxcore.models import JSONReprMixin
from pfx.pfxcore.shortcuts import f, get_object, parse_bool

logger = logging.getLogger(__name__)

LIST_META = ['count', 'pagination']


# HTTP 404 handler
def resource_not_found(request, exception):
    return JsonResponse(dict(message=_(
        "Resource not found")), status=404)


class ModelMixin:
    queryset = None
    fields = []

    def get_object(self, **kwargs):
        return get_object(self.get_queryset(), **kwargs)

    def get_queryset(self):
        return self.queryset

    def get_list_queryset(self):
        return self.get_queryset()

    def get_fields(self):
        return self.fields or [f.name for f in self.model._meta.fields]

    def get_model_fields(self):
        for lookup in self.get_fields():
            yield lookup, MetaResolver(self.model).get_field(lookup)

    @property
    def model(self):
        return self.get_queryset().model

    @property
    def model_name(self):
        return self.model._meta.verbose_name

    @property
    def date_format(self):
        return parse_bool(self.request.GET.get('date_format'))

    def _json_object(self, obj):
        if isinstance(obj, JSONReprMixin):
            return obj.json_repr()
        return dict(pk=obj.pk, resource_name=str(obj))

    def message_response(self, message, **kwargs):
        return JsonResponse(dict(message=message, **kwargs))


class ModelResponseMixin(ModelMixin):
    def serialize_field(self, obj, field_name):
        value = ObjectResolver(obj).get_value(field_name)
        field = MetaResolver(self.model).get_field(field_name)
        if self.date_format and isinstance(value, date):
            return dict(
                value=value,
                formatted=date_format(
                    value, format='SHORT_DATE_FORMAT', use_l10n=True))
        if isinstance(value, Model):
            return self._json_object(value)
        if isinstance(value, Manager):
            return [self._json_object(o) for o in value.all()]
        if hasattr(field, 'choices') and field.choices:
            choices = {k: v for k, v in field.choices}
            if value in choices:
                return dict(value=value, label=_(choices[value]))
            else:  # pragma: no cover
                return None
        return value

    def serialize_object(self, obj, **fields):
        return dict(**self._json_object(obj), **fields)

    def response(self, o, **meta):
        return JsonResponse(self.serialize_object(o, **{
            f: self.serialize_field(o, f)
            for f in self.get_fields()}, meta=meta))

    def validate(self, resolver, created=False, **kwargs):
        resolver.validate(**kwargs)

    def is_valid(self, resolver, created=False):
        resolver.save()
        message = (
                created and
                _("{model} {obj} created.") or
                _("{model} {obj} updated."))
        return self.response(
            resolver.object, message=f(
                message, model=self.model_name, obj=resolver.object))

    def is_invalid(self, resolver, errors):
        return JsonResponse(errors, status=422)

    def field_meta(self, field):
        name = field.name
        if hasattr(field, 'verbose_name'):
            name = field.verbose_name
        elif hasattr(field, 'related_model'):
            if (hasattr(field, 'multiple') and field.multiple and
                    hasattr(field.related_model._meta, 'verbose_name_plural')):
                name = field.related_model._meta.verbose_name_plural
            elif hasattr(
                field.related_model._meta, 'verbose_name'
            ):  # pragma: no cover
                name = field.related_model._meta.verbose_name
        res = {'type': field.get_internal_type(), 'name': name}
        if hasattr(field, 'choices') and field.choices:
            res['choices'] = [
                dict(label=_(v), value=k) for k, v in field.choices]
        return res

    def object_meta(self):
        return {n: self.field_meta(f) for n, f in self.get_model_fields()}

    @rest_api("/meta", method="get")
    def get_meta(self, *args, **kwargs):
        return JsonResponse(self.object_meta())


class BodyMixin:
    def deserialize_body(self):
        return json.loads(self.request.body)


class ModelBodyMixin(BodyMixin, ModelMixin):
    readonly_fields = []

    def get_readonly_fields(self, obj=None):
        return self.readonly_fields

    def _field_data(self, field_name, value):
        field = MetaResolver(self.model).get_field(field_name)
        if isinstance(field, ForeignKey):
            pk = (value['pk'] if isinstance(value, dict) and 'pk' in value
                  else value)
            return f'{field_name}_id', pk or None
        if hasattr(field, 'choices') and field.choices:
            value = (value['value']
                     if isinstance(value, dict) and 'value' in value
                     else value)
        elif isinstance(field, DateField):
            value = (value['value']
                     if isinstance(value, dict) and 'value' in value
                     else value)
        return field_name, value

    def get_model_data(self, obj, data, created):
        data.pop('id', None)
        data.pop('pk', None)
        ro_fields = self.get_readonly_fields(obj)
        return dict(
            self._field_data(k, v) for k, v in data.items()
            # Todo: throw an error for non existing fields.
            if k in self.get_fields() and
            # Todo: Log a warning for readonly ignores fields.
            k not in ro_fields and
            # Deny API changes on technical django _id and _pk fields.
            k[-3:] not in ('_id', '_pk'))


class ListRestViewMixin(ModelResponseMixin):
    list_fields = []
    filters = []

    def get_list_fields(self):
        return self.list_fields or self.get_fields()

    def parse_list_meta(self):
        meta_arg = self.request.GET.get('meta', 'all')
        meta = meta_arg.split(',') or []
        if 'all' in meta:
            return LIST_META
        return meta

    def _list_meta_count(self):
        return self.get_list_queryset().count()

    def _list_meta_pagination(self):
        return dict(
            page_size=int(self.request.GET.get('page_size', 10)),
            page=int(self.request.GET.get('page', 1)),
            page_subset=int(self.request.GET.get('page_subset', 5)))

    def _list_meta_subset(self):
        return dict(
            limit=int(self.request.GET.get('limit', 10)),
            offset=int(self.request.GET.get('offset', 1)))

    def build_list_meta(self):
        def _meta(meta):
            fn = getattr(self, f'_list_meta_{meta}', None)
            if not callable(fn):
                raise APIError(
                    _("Meta {meta} does not exists.").format(meta=meta))
            return fn

        return {
            meta: _meta(meta)()
            for meta in self.parse_list_meta()}

    def search_filter(self, search):  # pragma: no cover
        return Q()

    @rest_api("/filters", method="get")
    def get_filter(self, *args, **kwargs):
        return JsonResponse({
            'items': [f.meta for f in self.filters]})

    def get_list_queryset(self):
        qs = super().get_list_queryset()
        search = self.request.GET.get('search')
        for filter in self.filters:
            qs = qs.filter(filter.query(self.request.GET))
        if search:
            qs = qs.filter(
                self.search_filter(search))
        order = self.request.GET.get('order')
        if order:
            qs = qs.order_by(*order.split(','))
        return qs

    def get_list_result(self, qs):
        for o in qs:
            yield self.serialize_object(o, **{
                f: self.serialize_field(o, f)
                for f in self.get_list_fields()})

    @rest_api("", method="get")
    def get_list(self, *args, **kwargs):
        res = {}
        meta = self.build_list_meta()
        qs = self.get_list_queryset()
        if 'pagination' in meta:
            count = qs.count()
            pagination = meta['pagination']
            page = pagination['page']
            limit = pagination['page_size']
            page_count = (1 + (count - 1) // limit) or 1
            offset = (page - 1) * limit
            subset = pagination['page_subset']
            subset_first = min(
                max(page - subset // 2, 1), max(page_count - subset + 1, 1))
            qs = qs.all()[offset:offset + limit]
            pagination.update(dict(
                count=count,
                page_count=page_count,
                subset=list(range(
                    subset_first,
                    min(subset_first + subset, page_count + 1)))))
        elif 'subset' in meta:
            count = qs.count()
            subset = meta['subset']
            limit = subset['limit']
            page_count = (1 + (count - 1) // limit) or 1
            offset = subset['offset']
            qs = qs.all()[offset:offset + limit]
            subset.update(dict(
                count=count,
                page_count=page_count,
                limit=limit,
                offset=offset))
        else:
            qs = qs.all()
        if meta:
            res['meta'] = meta
        res['items'] = list(self.get_list_result(qs))
        return JsonResponse(res)


class DetailRestViewMixin(ModelResponseMixin):

    @rest_api("/<int:id>", method="get")
    def get(self, id, *args, **kwargs):
        obj = self.get_object(pk=id)
        return self.response(obj)


class SlugDetailRestViewMixin(ModelResponseMixin):
    SLUG_FIELD = "slug"

    @rest_api("/slug/<slug:slug>", method="get")
    def get_by_slug(self, slug, *args, **kwargs):
        obj = self.get_object(**{self.SLUG_FIELD: slug})
        return self.response(obj)


class CreateRestViewMixin(ModelBodyMixin, ModelResponseMixin):
    default_values = {}

    def get_default_values(self):
        return dict(self.default_values)

    def new_object(self):
        return self.model(**self.get_default_values())

    @rest_api("", method="post")
    def post(self, *args, **kwargs):
        obj = self.new_object()
        data = self.get_model_data(obj, self.deserialize_body(), created=True)
        resolver = ObjectResolver(obj)
        resolver.set_values(**data)
        try:
            self.validate(resolver, created=True)
            return self.is_valid(resolver, created=True)
        except ResolverValidationError as e:
            return self.is_invalid(resolver, errors=e.errors)


class UpdateRestViewMixin(ModelBodyMixin, ModelResponseMixin):
    @rest_api("/<int:id>", method="put")
    def put(self, id, *args, **kwargs):
        obj = self.get_object(pk=id)
        data = self.get_model_data(obj, self.deserialize_body(), created=False)
        resolver = ObjectResolver(obj)
        resolver.set_values(**data)
        try:
            self.validate(resolver, created=False)
            return self.is_valid(resolver, created=False)
        except ResolverValidationError as e:
            return self.is_invalid(resolver, errors=e.errors)


class DeleteRestViewMixin(ModelMixin):
    @rest_api("/<int:id>", method="delete")
    def delete(self, id, *args, **kwargs):
        obj = self.get_object(pk=id)
        try:
            with transaction.atomic():
                obj.delete()
            return self.message_response(f(
                _("{model} {obj} deleted."), model=self.model_name, obj=obj))
        except IntegrityError as e:
            logger.debug("IntegrityError: %s", e)
            raise APIError(f(_(
                "{obj} cannot be deleted because "
                "it is referenced by other objects."), obj=obj))


class SecuredRestViewMixin(View):
    default_public = False

    def perm(self):
        return True

    def _is_public(self, public, func_name):
        param = f'{func_name}_public'
        if hasattr(self, param):
            public = getattr(self, param)
        if public is None:
            public = self.default_public
        return public

    def check_perm(self, public, func_name, *args, **kwargs):
        if self._is_public(public, func_name):
            return
        if not self.request.user.is_authenticated:
            raise UnauthorizedError()
        if not self.perm():
            raise ForbiddenError()
        fperm = f'{func_name}_perm'
        if hasattr(self, fperm) and not getattr(self, fperm)(*args, **kwargs):
            raise ForbiddenError()


class BaseRestView(SecuredRestViewMixin, View):
    pass


class RestView(
        ListRestViewMixin,
        DetailRestViewMixin,
        CreateRestViewMixin,
        UpdateRestViewMixin,
        DeleteRestViewMixin,
        BaseRestView):
    pass

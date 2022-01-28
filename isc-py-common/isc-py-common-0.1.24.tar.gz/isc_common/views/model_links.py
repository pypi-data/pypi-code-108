import logging

from django.db.models import Model

logger = logging.getLogger(__name__)


class Model_links(Model):

    @classmethod
    def update_or_create_link(cls, main_model, link_field_name, link, pk_name='id'):
        from isc_common.models.links import Links

        if link != '' or link is not None:
            if eval(f'main_model.{link_field_name} is None', dict(), dict(main_model=main_model)):
                res, _ = eval(f'links.objects.get_or_create(link=link)', dict(), dict(link=link, links=Links))
            else:
                res, _ = eval(f'links.objects.update_or_create(id=main_model.{link_field_name}.id, defaults=dict(link=link))', dict(), dict(link=link, links=Links, main_model=main_model))

            eval(f'main_model._meta.concrete_model.objects.filter({pk_name}=main_model.{pk_name}).update({link_field_name}=res)', dict(), dict(res=res, main_model=main_model))

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Базовый класс'
        abstract = True

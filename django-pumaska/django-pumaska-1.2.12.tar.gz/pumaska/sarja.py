# -*- coding: utf-8 -*-
# pylint: disable=invalid-name

from itertools import chain

from django.db import transaction
from django.db.models import ProtectedError
from django import forms
from django.template import loader
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _


def lisaa_lomakesarja(
  LomakeA, LomakeB, *,
  avain_a=None,
  avain_b=None,
  tunnus=None,
  epasuora=False,
  lomakesarja_parametrit=None,
  valita_parametrit=None,
  **kwargs
):
  '''
  Yhdistää ModelForm-luokan ja toisesta ModelForm-luokasta
  muodostetun InlineFormSet-luokan silloin,
  kun B-luokasta on suora (ForeignKey) tai epäsuora (GenericForeignKey)
  viittaus A-luokkaan.

  Args:
    LomakeA, LomakeB: mallikohtaiset lomakeluokat
    avain_a, avain_b: viittaukset mallien välillä
    tunnus: yksikäsitteinen tunnus lomakesarjalle (oletus 'lomakesarja')
    epasuora: käytetään `generic_inlineformset_factory`-funktiota?
    lomakesarja_parametrit: parametrit, jotka asetetaan lomakesarjan määreiksi
    valita_parametrit: ulomman lomakkeen parametrit, jotka välitetään
      sellaisenaan lomakesarjalle
    *args, **kwargs: lisäparametrit ``inlineformset_factory``-funktiolle

  Returns:
    lomakeluokka
  '''
  # Pakotetaan ylimääräisten lomakkeiden määräksi nolla.
  kwargs['extra'] = 0

  assert tunnus or avain_a or avain_b, (
    'Joko `tunnus`, `avain_a` tai `avain_b` on määriteltävä.'
  )

  if epasuora:
    from django.contrib.contenttypes.forms import generic_inlineformset_factory
    lomakesarja = generic_inlineformset_factory(
      LomakeB.Meta.model,
      form=LomakeB,
      **kwargs
    )
  else:
    lomakesarja = forms.models.inlineformset_factory(
      LomakeA.Meta.model,
      LomakeB.Meta.model,
      form=LomakeB,
      **kwargs
    )

  # Käytetään tyhjän lomakkeen oletusarvoina
  # `initial`-datan ensimmäistä alkiota.
  class lomakesarja(lomakesarja):
    # pylint: disable=function-redefined
    def get_form_kwargs(self, index):
      if index is None and self.initial_extra:
        return {
          **super().get_form_kwargs(index), 'initial': self.initial_extra[0]
        }
      else:
        return super().get_form_kwargs(index)
      # def get_form_kwargs
    # class lomakesarja

  # Aseta mahdolliset lomakesarjan parametrit.
  for avain, arvo in (lomakesarja_parametrit or {}).items():
    setattr(lomakesarja, avain, arvo)

  # Lisää tarvittaessa oletusarvot HTML-piirtoa varten.
  if not hasattr(lomakesarja, 'label'):
    lomakesarja.label = (
      LomakeB.Meta.model._meta.verbose_name_plural
    ).capitalize()
  if not hasattr(lomakesarja, 'palikka'):
    lomakesarja.palikka = 'pumaska/lomakesarja_lomakekenttana.html'
  if not hasattr(lomakesarja, 'riviluokka'):
    lomakesarja.riviluokka = 'panel panel-default clearfix'
  if not hasattr(lomakesarja, 'lisaa_painike'):
    lomakesarja.lisaa_painike = _('Lisää %(malli)s') % {
      'malli': LomakeB.Meta.model._meta.verbose_name
    }
  if not hasattr(lomakesarja, 'poista_painike'):
    lomakesarja.poista_painike = _('Poista %(malli)s') % {
      'malli': LomakeB.Meta.model._meta.verbose_name
    }

  tunnus = tunnus or avain_a or (
    LomakeB.Meta.model._meta.get_field(avain_b).remote_field.name
  )

  class YhdistettyLomake(LomakeA):
    class Meta(LomakeA.Meta):
      pass

    def __init__(self, *args, prefix=None, **kwargs):
      lomakesarja_kwargs = kwargs.pop(f'{tunnus}_kwargs', {})
      for param in (valita_parametrit or ()):
        try:
          lomakesarja_kwargs[param] = kwargs[param]
        except KeyError:
          pass
      super().__init__(*args, prefix=prefix, **kwargs)
      initial = {
        avain.replace(tunnus + '-', '', 1): arvo
        for avain, arvo in self.initial.items()
        if avain.startswith(tunnus + '-') and avain != tunnus + '-'
      }
      setattr(self, tunnus, lomakesarja(
        data=kwargs.get('data'),
        files=kwargs.get('files'),
        instance=self.instance,
        initial=[initial] if initial else [],
        prefix=f'{self.prefix}-{tunnus}' if self.prefix else tunnus,
        **lomakesarja_kwargs,
      ))
      # def __init__

    # def order_fields(self, field_order)
    # def __str__(self)
    # def __repr__(self)

    def __iter__(self):
      return chain(
        super().__iter__(),
        *(lomake.__iter__() for lomake in getattr(self, tunnus).__iter__()),
      )
      # def __iter__

    def __getitem__(self, item):
      if item.startswith(f'{tunnus}-'):
        indeksi, _, item = item.partition(f'{tunnus}-')[2].partition('-')
        return getattr(self, tunnus).__getitem__(int(indeksi)).__getitem__(item)
      else:
        return super().__getitem__(item)
      # def __getitem__

    @property
    def errors(self):
      virheet = list(super().errors.items())
      lomakesarja = getattr(self, tunnus)
      for indeksi, lomake in enumerate(lomakesarja.forms):
        if lomake not in lomakesarja.deleted_forms:
          for avain, arvo in list(lomake.errors.items()):
            virheet.append([
              '%s-%d-%s' % (tunnus, indeksi, avain), arvo
            ])
      if any(lomakesarja.non_form_errors()):
        virheet.append([
          # Lisää lomakeriippumattomat virheet hallintolomakkeen kohdalle.
          tunnus + '-TOTAL_FORMS',
          lomakesarja.non_form_errors()
        ])
      return forms.utils.ErrorDict(virheet)
      # def errors

    def is_valid(self):
      return super().is_valid() \
      and getattr(self, tunnus).is_valid()
      # def is_valid

    # def add_prefix(self, field_name)
    # def add_initial_prefix(self, field_name)

    def _html_output(self, *args, **kwargs):
      # pylint: disable=protected-access
      return super()._html_output(*args, **kwargs) \
      + loader.get_template('pumaska/lomakesarja.html').render({
        'tunnus': tunnus,
        'lomakesarja': getattr(self, tunnus),
      })
      # def _html_output

    # Django 4.0+.
    def render(self, *args, **kwargs):
      return super().render(*args, **kwargs) \
      + loader.get_template('pumaska/lomakesarja.html').render({
        'tunnus': tunnus,
        'lomakesarja': getattr(self, tunnus),
      })
      # def render

    # def as_table(self)
    # def as_ul(self)
    # def as_p(self)
    # def non_field_errors(self)
    # def add_error(self, field, error)
    # def has_error(self, field, code=None)
    # def full_clean(self)
    # def _clean_fields(self)
    # def _clean_form(self)
    # def _post_clean(self)
    # def clean(self)

    def has_changed(self):
      return super().has_changed() \
      or getattr(self, tunnus).has_changed()
      # def has_changed

    @cached_property
    def changed_data(self):
      '''
      Palauta ylälomakkeen omien muutosten lisäksi
      liitoslomakkeiden mahdolliset muutokset
      lomakesarjan määrittämillä, lomakekohtaisella
      etuliitteillä varustettuina.
      '''
      lomakesarja = getattr(self, tunnus)
      # Muodosta lomakekohtainen kentän etuliite poistamalla
      # liitetyn lomakkeen `prefixin` alusta
      # käsillä olevan (ylä-) lomakkeen oma `prefix` ja välimerkki -.
      lomakekohtainen_tunnus = (
        lambda lomake: lomake.prefix.replace(self.prefix + "-", "", 1)
      ) if self.prefix else lambda lomake: lomake.prefix
      return super().changed_data + sum([[
        f'{lomakekohtainen_tunnus(lomake)}-{kentta}'
        for kentta in lomake.changed_data
      ] for lomake in lomakesarja], [])
      # def changed_data

    #@property
    #def media(self)

    #def is_multipart(self)
    #def hidden_fields(self)
    #def visible_fields(self)
    #def get_initial_for_field(self, field, field_name)


    # `in`

    def __contains__(self, key):
      if key.startswith(f'{tunnus}-'):
        indeksi, _, key = key.partition(f'{tunnus}-')[2].partition('-')
        if hasattr(
          getattr(self, tunnus).__getitem__(int(indeksi)),
          '__contains__'
        ) and getattr(self, tunnus).__getitem__(int(indeksi)).__contains__(key):
          return True
        return key in getattr(self, tunnus).__getitem__(
          int(indeksi)
        ).Meta.fields
        # if key.startswith
      if hasattr(super(), '__contains__') \
      and super().__contains__(key):
        return True
      else:
        return key in self.fields
      # def __contains__


    # ModelForm

    @transaction.atomic
    def save(self, commit=True):
      '''
      Tallennetaan atomaarisena tietokantaoperaationa.
      '''
      return super().save(commit=commit)
      # def save

    def _save_m2m(self):
      '''
      Tallennetaan M2M-kohteet `super`-toteutuksen mukaisesti.
      Tämän jälkeen tallennetaan lomakesarja.
      '''
      super()._save_m2m()
      lomakesarja = getattr(self, tunnus)
      lomakesarja.instance = self.instance
      try:
        lomakesarja.save(commit=True)
      except ProtectedError as exc:
        virheteksti = _(
          'Rivin poisto epäonnistui:'
          ' suojattuja, riippuvia %(malli)s-kohteita.'
        ) % {'malli': exc.protected_objects.model._meta.verbose_name}
        # pylint: disable=protected-access
        lomakesarja._non_form_errors.append(forms.ValidationError(
          virheteksti, code='protect'
        ))
        raise forms.ValidationError(exc)
      # def _save_m2m

    # class YhdistettyLomake

  return YhdistettyLomake
  # def lisaa_lomakesarja

# -*- coding: utf-8 -*-
# pylint: disable=invalid-name

from itertools import chain
import types

from django.db import DatabaseError, transaction
from django import forms
from django.utils.functional import cached_property
from django.utils.module_loading import import_string


def yhdista_lomakkeet(
  LomakeA, LomakeB, *,
  avain_a=None,
  avain_b=None,
  tunnus=None,
  pakollinen_b=None,
  valita_parametrit=None,
):
  '''
  Yhdistää kaksi ModelForm-luokkaa silloin,
  kun A-luokasta on suora viittaus B-luokkaan

  Joko `avain_a` tai `avain_b` on pakollinen.

  Args:
    LomakeA, LomakeB: mallikohtaiset lomakeluokat
    avain_a: viittausavain LomakeA.Meta.model-luokan kohteelta
      LomakeB.Meta.model-luokan kohteelle
    avain_b: viittausavain LomakeB.Meta.model-luokan kohteelta
      LomakeA.Meta.model-luokan kohteelle
      (oletuksena haetaan viittauksen vastaluokan tiedoista)
    tunnus: yksikäsitteinen tunnus LomakeB-lomakkeelle
      (oletuksena ``avain_a`` tai ``avain_b``:n vastaviittaus)
    pakollinen_b: onko lomake B pakollinen, tarkistettava tieto?
      (oletuksena sama kuin A--B-viittauksen pakollisuus, jos annettu)
  '''

  if isinstance(LomakeA, str):
    LomakeA = import_string(LomakeA)
  if isinstance(LomakeB, str):
    LomakeB = import_string(LomakeB)

  # Muodosta avain_a, avain_b, kentta_a ja kentta_b.
  assert avain_a or avain_b
  kentta_a = LomakeA.Meta.model._meta.get_field(avain_a) if avain_a else None

  avain_b = avain_b or kentta_a.remote_field.name
  kentta_b = LomakeB.Meta.model._meta.get_field(avain_b)
  tunnus = tunnus or avain_a or kentta_b.remote_field.name

  # Mikäli A-avainta ei ole annettu,
  # B-lomake on oletuksena valinnainen.
  # Muutoin haetaan oletus vastaavan kentän tiedoista.
  if pakollinen_b is None:
    pakollinen_b = avain_a and (
      not LomakeA.Meta.model._meta.get_field(avain_a).null
    )

  class YhdistettyLomake(LomakeA):
    class Meta(LomakeA.Meta):
      pass

    def __init__(self, *args, prefix=None, **kwargs):
      lomake_kwargs = kwargs.pop(f'{tunnus}_kwargs', {})
      for param in (valita_parametrit or ()):
        try:
          lomake_kwargs[param] = kwargs[param]
        except KeyError:
          pass
      super().__init__(*args, prefix=prefix, **kwargs)
      # Poimitaan B-kohde joko `initial`-sanakirjasta tai A-kohteen tiedoista.
      kohde_b = self.initial.get(tunnus, None)
      if isinstance(kohde_b, LomakeB.Meta.model):
        pass
      elif kohde_b is not None:
        kohde_b = LomakeB.Meta.model.objects.get(pk=kohde_b)
      elif self.instance and avain_a:
        kohde_b = getattr(self.instance, avain_a, None)

      # Mikäli olemassaolevaa B-kohdetta ei löytynyt, luodaan uusi.
      if kohde_b is None:
        kohde_b = LomakeB.Meta.model()
        # Asetetaan linkki B-->A, jos mahdollista
        try:
          setattr(kohde_b, avain_b, self.instance)
        except (AttributeError, TypeError):
          pass
      assert isinstance(kohde_b, LomakeB.Meta.model), (
        f'Kohde B ei voi olla tyyppiä {type(kohde_b)} != {LomakeB.Meta.model}!'
      )

      lomake_b = LomakeB(
        instance=kohde_b,
        data=kwargs.get('data'),
        files=kwargs.get('files'),
        initial={
          avain.replace(tunnus + '-', '', 1): arvo
          for avain, arvo in self.initial.items()
          if avain.startswith(tunnus + '-') and avain != tunnus + '-'
        },
        prefix=f'{self.prefix}-{tunnus}' if self.prefix else tunnus,
        **lomake_kwargs
      )
      if avain_b in lomake_b.fields:
        lomake_b.fields[avain_b].disabled = True
        lomake_b.fields[avain_b].required = False
        lomake_b.fields[avain_b].widget = forms.HiddenInput()
      setattr(self, tunnus, lomake_b)
      # Jos B-viittaus saa olla tyhjä, asetetaan kaikki B-lomakkeen
      # kentät valinnaisiksi GET-pyynnöllä.
      # – Huomaa, että tämä koskee myös mahdollisten sisäkkäisten
      # lomakkeiden (C) kenttiä.
      # Lisäksi ohitetaan vimpainten `required`-määreen tulostus.
      if not pakollinen_b:
        for kentta in lomake_b:
          if not self.data:
            kentta.field.required = False
          kentta.field.widget.use_required_attribute = lambda initial: False
      # def __init__

    # def order_fields(self, field_order)
    # def __str__(self)
    # def __repr__(self)

    def __iter__(self):
      return chain(
        super().__iter__(),
        getattr(self, tunnus).__iter__(),
      )
      # def __iter__

    def __getitem__(self, item):
      if item.startswith(f'{tunnus}-'):
        return getattr(self, tunnus).__getitem__(
          item.partition(f'{tunnus}-')[2]
        )
      else:
        return super().__getitem__(item)
      # def __getitem__

    @property
    def errors(self):
      '''
      Lisää B-lomakkeen mahdolliset virheet silloin, kun
      B-viittaus ei saa olla tyhjä, tai B-lomaketta on muokattu.
      '''
      virheet = list(super().errors.items())
      if pakollinen_b or getattr(self, tunnus).has_changed():
        lomake_b = getattr(self, tunnus)
        for avain, arvo in list(lomake_b.errors.items()):
          virheet.append([
            '%s-%s' % (tunnus, avain), arvo
          ])
      return forms.utils.ErrorDict(virheet)
      # def errors

    def is_valid(self):
      '''
      Jos B-viittaus saa olla tyhjä eikä sitä ole muokattu,
      ei välitetä B-lomakkeen mahdollisesta epäkelpoisuudesta.
      '''
      return super().is_valid() \
      and (getattr(self, tunnus).is_valid() or (
        not pakollinen_b and not getattr(self, tunnus).has_changed()
      ))
      # def is_valid

    # def add_prefix(self, field_name)
    # def add_initial_prefix(self, field_name)

    def _html_output(self, *args, **kwargs):
      # pylint: disable=protected-access
      return super()._html_output(*args, **kwargs) \
      + getattr(self, tunnus)._html_output(*args, **kwargs)
      # def _html_output

    # Django 4.0+.
    def render(self, *args, **kwargs):
      return super().render(*args, **kwargs) \
      + getattr(self, tunnus).render(*args, **kwargs)
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
      liitoslomakkeen mahdolliset muutokset
      `tunnus`-etuliitteellä varustettuina.
      '''
      lomake = getattr(self, tunnus)
      return super().changed_data + [
        f'{tunnus}-{kentta}'
        for kentta in lomake.changed_data
      ]
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
        key = key.partition(f'{tunnus}-')[2]
        if hasattr(getattr(self, tunnus), '__contains__') \
        and getattr(self, tunnus).__contains__(key):
          return True
        return key in getattr(self, tunnus).Meta.fields
        # if key.startswith
      if hasattr(super(), '__contains__') \
      and super().__contains__(key):
        return True
      else:
        return key in self.Meta.fields
      # def __contains__


    # ModelForm

    @transaction.atomic
    def _save_m2m(self):
      super()._save_m2m()
      # Jos viittaus A-->B voi olla tyhjä, tallennetaan B (vasta) nyt
      if not avain_a or self.Meta.model._meta.get_field(avain_a).null:

        # Haetaan A-kohde ja B-lomake
        kohde_a = self.instance
        lomake_b = getattr(self, tunnus)

        # Otetaan vanha B-kohde talteen
        vanha_kohde_b = getattr(kohde_a, avain_a) \
        if avain_a and hasattr(kohde_a, avain_a) else None

        if vanha_kohde_b == lomake_b.instance and vanha_kohde_b.pk:
          # Päivitetään olemassaoleva B
          try:
            lomake_b.save(commit=True)
          except (ValueError, DatabaseError):
            if pakollinen_b:
              raise
            # Säilytetään olemassaoleva tietue.
            vanha_kohde_b.refresh_from_db()
          # if vanha_kohde_b == lomake_b.instance and vanha_kohde_b.pk
        else:
          # Asetetaan linkki B-->A
          setattr(lomake_b.instance, avain_b, kohde_a)

          # Yritetään tallentaa B ja otetaan virhe kiinni
          try:
            kohde_b = lomake_b.save(commit=True)
          except (ValueError, DatabaseError):
            if pakollinen_b:
              raise
            kohde_b = vanha_kohde_b

          # Asetetaan tarvittaessa linkki A-->B ja tallennetaan A (uudelleen).
          if avain_a:
            setattr(kohde_a, avain_a, kohde_b)
            kohde_a.save()

          # Poistetaan vanha kohde, jos viittaus katkesi
          if vanha_kohde_b and vanha_kohde_b.pk and vanha_kohde_b != kohde_b:
            vanha_kohde_b.delete()
          # if vanha_kohde_b != lomake_b.instance:
        # if ...null

      # def _save_m2m

    @transaction.atomic
    def save(self, commit=True):
      # pylint: disable=access-member-before-definition
      # pylint: disable=attribute-defined-outside-init

      # Jos viittaus A-->B ei voi olla tyhjä, tallennetaan B ensin
      # (muussa tapauksessa B tallennetaan lopuksi `_save_m2m`-metodissa)
      if avain_a and not self.Meta.model._meta.get_field(avain_a).null:
        lomake_b = getattr(self, tunnus)
        kohde_b = lomake_b.save(commit=commit)
        setattr(self.instance, avain_a, kohde_b)

        # Kun `commit=False`, ja B on uusi, tallentamaton tietokantarivi:
        if not commit and kohde_b and not kohde_b.pk:
          # Vaihdetaan A:n tallennusmetodi kertaluontoisesti.
          vanha_save = self.instance.save
          def save(instance):
            # Hae tämänhetkinen B, tallenna se ja aseta uudelleen.
            kohde_b = getattr(instance, avain_a)
            kohde_b.save()
            # Päivitä B-lomakkeen rivi ja kutsu sen `save_m2m`-metodia.
            lomake_b.instance = kohde_b
            lomake_b.save_m2m()
            # Aseta B uudelleen A-kohteelle.
            setattr(instance, avain_a, kohde_b)
            # Palauta oletus-`save`-toteutus paikalleen ja kutsu sitä.
            instance.save = vanha_save
            instance.save()
            # def save
          self.instance.save = types.MethodType(save, self.instance)
          # if not commit and kohde_b and not kohde_b.pk
        return super().save(commit=commit)

      else:
        # Mikäli B on uusi, viittaus A.B on olemassa ja tämä voi olla
        # tyhjä, korvataan A.B arvolla None ennen A:n tallennusta.
        # Palautetaan tallennuksen jälkeen A.B = B.
        # B tallennetaan lopuksi `_save_m2m`-metodissa.
        # Django vaatii tämän A:n tallentamiseksi; ks.
        # django.db.models.base:Model._prepare_related_fields_for_save.
        lomake_b = getattr(self, tunnus)
        if avain_a is None or lomake_b.instance.pk is not None:
          return super().save(commit=commit)
        setattr(self.instance, avain_a, None)
        self.instance = super().save(commit=commit)
        setattr(self.instance, avain_a, lomake_b.instance)
        return self.instance
        # else

      # def save

    # class YhdistettyLomake

  return YhdistettyLomake
  # def yhdista_lomakkeet

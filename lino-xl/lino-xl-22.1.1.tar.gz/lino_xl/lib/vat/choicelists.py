# -*- coding: UTF-8 -*-
# Copyright 2012-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import time
from lino.utils import is_string
from decimal import Decimal
from lino.api import dd, _, gettext
from etgen.html import E, forcetext
from django.db import models
from lino_xl.lib.ledger.roles import LedgerStaff
from lino_xl.lib.ledger.choicelists import DC, TradeTypes, CommonAccounts

from lino_xl.lib.ledger.utils import ZERO

MAX_ONLINE_ATTEMPTS = 3


if dd.is_installed('vat'):
    try:
        import pyvat
    except ImportError:
        pyvat = None
    import re
    import random

    random.seed(1)

    from lino.modlib.checkdata.choicelists import Checker


class VatClasses(dd.ChoiceList):
    verbose_name = _("VAT class")
    verbose_name_plural = _("VAT classes")
    required_roles = dd.login_required(LedgerStaff)
    show_values = False

add = VatClasses.add_item
add('010', _("Goods at normal VAT rate"), 'goods')    # everything else
add('020', _("Goods at reduced VAT rate"), 'reduced')  # food, books,...
add('030', _("Goods exempt from VAT"), 'exempt')    # post stamps, ...
add('100', _("Services"), 'services')
add('200', _("Investments"), 'investments')
add('210', _("Real estate"), 'real_estate')
add('220', _("Vehicles"), 'vehicles')
add('300', _("Without VAT"), 'vatless')  # internal clearings, flight tickets, ...



class VatAreas(dd.ChoiceList):
    verbose_name = _("VAT area")
    verbose_name_plural = _("VAT areas")
    required_roles = dd.login_required(LedgerStaff)

    @classmethod
    def get_for_country(cls, country=None):
        if country is None:
            isocode = dd.plugins.countries.country_code
        else:
            isocode = country.isocode
        if isocode == dd.plugins.countries.country_code:
            return cls.national
        if isocode in dd.plugins.vat.eu_country_codes:
            return cls.eu
        return cls.international

add = VatAreas.add_item
add('10', _("National"), 'national')
add('20', _("EU"), 'eu')
add('30', _("International"), 'international')

class VatColumn(dd.Choice):
    common_account = None

    def __init__(self, value, text, common_account=None):
        super(VatColumn, self).__init__(value, text)
        self.common_account = common_account


class VatColumns(dd.ChoiceList):
    # to be populated by bevat, bevats, ...
    verbose_name = _("VAT column")
    verbose_name_plural = _("VAT columns")
    required_roles = dd.login_required(LedgerStaff)
    show_values = True
    item_class = VatColumn
    column_names = "value text common_account account"

    @dd.virtualfield(CommonAccounts.field())
    def common_account(cls, col, ar):
        return col.common_account

    @dd.virtualfield(dd.ForeignKey('ledger.Account'))
    def account(cls, col, ar):
        if col.common_account is not None:
            return col.common_account.get_object()


class VatRegime(dd.Choice):
    vat_area = None
    needs_vat_id = False
    # item_vat = True  # 20200521 no longer used

    def __init__(self, value, text, name, vat_area=None, item_vat=True, needs_vat_id=False):
        super(VatRegime, self).__init__(value, text, name)
        self.vat_area = vat_area
        self.needs_vat_id = needs_vat_id
        # self.item_vat = item_vat

    def is_allowed_for(self, vat_area):
        if self.vat_area is None:
            return True
        return self.vat_area == vat_area


class VatRegimes(dd.ChoiceList):
    verbose_name = _("VAT regime")
    verbose_name_plural = _("VAT regimes")
    column_names = "value name text vat_area needs_vat_id #item_vat"
    item_class = VatRegime
    required_roles = dd.login_required(LedgerStaff)

    @dd.virtualfield(VatAreas.field())
    def vat_area(cls, regime, ar):
        return regime.vat_area

    # @dd.virtualfield(dd.BooleanField(_("item VAT")))
    # def item_vat(cls, regime, ar):
    #     return regime.item_vat

    @dd.virtualfield(dd.BooleanField(_("Needs VAT id")))
    def needs_vat_id(cls, regime, ar):
        return regime.needs_vat_id

    @classmethod
    def get_choices_for_country(cls, country=None):
        vat_area = VatAreas.get_for_country(country)
        # print("20190405", vat_area)
        for r in cls.get_list_items():
            if vat_area is None or r.vat_area is None or r.vat_area == vat_area:
                yield r




add = VatRegimes.add_item
add('10', _("Normal"), 'normal')
# re-populated in bevat and bevats.
# See also lino_xl.lib.vat.Plugin.default_vat_regime

#
class DeclarationField(dd.Choice):
    editable = False
    vat_regimes = None
    exclude_vat_regimes = None
    vat_classes = None
    exclude_vat_classes = None
    vat_columns = None
    exclude_vat_columns = None
    is_payable = False
    # value dc vat_columns text fieldnames both_dc vat_regimes vat_classes
    def __init__(self, value, dc,
                 vat_columns=None,
                 # is_base,
                 text=None,
                 fieldnames='',
                 both_dc=True,
                 vat_regimes=None, vat_classes=None,
                 **kwargs):
        name = "F" + value
        # text = string_concat("[{}] ".format(value), text)
        self.help_text = text
        super(DeclarationField, self).__init__(
            value, "[{}]".format(value), name, **kwargs)

        # self.is_base = is_base
        self.fieldnames = fieldnames
        self.vat_regimes = vat_regimes
        self.vat_classes = vat_classes
        self.vat_columns = vat_columns
        self.dc = dc
        self.both_dc = both_dc

    def attach(self, choicelist):
        self.minus_observed_fields = set()
        self.observed_fields = []
        for n in self.fieldnames.split():
            if n.startswith('-'):
                n = n[1:]
                self.minus_observed_fields.add(n)
            f = choicelist.get_by_value(n)
            if f is None:
                raise Exception(
                    "Invalid observed field {} for {}".format(n, self))
            self.observed_fields.append(f)

        if is_string(self.vat_regimes):
            vat_regimes = self.vat_regimes
            self.vat_regimes = set()
            self.exclude_vat_regimes = set()
            for n in vat_regimes.split():
                if n.startswith('!'):
                    s = self.exclude_vat_regimes
                    n = n[1:]
                else:
                    s = self.vat_regimes
                v = VatRegimes.get_by_name(n)
                if v is None:
                    raise Exception(
                        "Invalid VAT regime {} for field {}".format(
                            v, self.value))
                s.add(v)
            if len(self.vat_regimes) == 0:
                self.vat_regimes = None
            if len(self.exclude_vat_regimes) == 0:
                self.exclude_vat_regimes = None

        if is_string(self.vat_classes):
            vat_classes = self.vat_classes
            self.vat_classes = set()
            self.exclude_vat_classes = set()
            for n in vat_classes.split():
                if n.startswith('!'):
                    s = self.exclude_vat_classes
                    n = n[1:]
                else:
                    s = self.vat_classes
                v = VatClasses.get_by_name(n)
                if v is None:
                    raise Exception(
                        "Invalid VAT class {} for field {}".format(
                            v, self.value))
                s.add(v)
            if len(self.vat_classes) == 0:
                self.vat_classes = None
            if len(self.exclude_vat_classes) == 0:
                self.exclude_vat_classes = None

        # using VAT columns as selector is probably obsolete
        if is_string(self.vat_columns):
            vat_columns = self.vat_columns
            self.vat_columns = set()
            self.exclude_vat_columns = set()
            for n in vat_columns.split():
                if n.startswith('!'):
                    s = self.exclude_vat_columns
                    n = n[1:]
                else:
                    s = self.vat_columns
                v = VatColumns.get_by_value(n)
                if v is None:
                    raise Exception(
                        "Invalid VAT column {} for field {}".format(
                            n, self.value))
                s.add(v)
            if len(self.vat_columns) == 0:
                self.vat_columns = None
            if len(self.exclude_vat_columns) == 0:
                self.exclude_vat_columns = None

        super(DeclarationField, self).attach(choicelist)


    def get_model_field(self):
        return dd.PriceField(
            self.text, default=Decimal, editable=self.editable,
            help_text=self.help_text)

    # def __str__(self):
    #     # return force_str(self.text, errors="replace")
    #     # return self.text
    #     return "[{}] {}".format(self.value, self.text)

    def collect_from_movement(self, dcl, mvt, field_values, payable_sums):
        pass

    def collect_from_sums(self, dcl, sums, payable_sums):
        pass

class SumDeclarationField(DeclarationField):

    def __init__(self, *args, **kwargs):
        super(SumDeclarationField, self).__init__(*args, **kwargs)
        if self.is_payable:
            raise Exception("SumDeclarationField may not be payable")

    def collect_from_sums(self, dcl, field_values, payable_sums):
        tot = Decimal()
        for f in self.observed_fields:
            v = field_values[f.name]
            if f.value in self.minus_observed_fields:
                v = -v
            tot += v
            # if f.dc == self.dc:
            #     tot += v
            # else:
            #     tot -= v
        field_values[self.name] = tot

class WritableDeclarationField(DeclarationField):
    editable = True
    def collect_from_sums(self, dcl, field_values, payable_sums):
        if self.is_payable:
            amount = field_values[self.name]
            if amount:
                if self.dc == dcl.journal.dc:
                    amount = - amount
                k = ((dcl.journal.account, None), None, None, None)
                payable_sums.collect(k, amount)

class MvtDeclarationField(DeclarationField):

    def collect_from_movement(self, dcl, mvt, field_values, payable_sums):
        # if not mvt.account.declaration_field in self.observed_fields:
        #     return 0
        if self.vat_classes is not None:
            if not mvt.vat_class in self.vat_classes:
                return
        if self.exclude_vat_classes is not None:
            if mvt.vat_class in self.exclude_vat_classes:
                return
        if self.vat_columns is not None:
            if not mvt.account.vat_column in self.vat_columns:
                return
        if self.exclude_vat_columns is not None:
            if mvt.account.vat_column in self.exclude_vat_columns:
                return
        if self.vat_regimes is not None:
            if not mvt.vat_regime in self.vat_regimes:
                return
        if self.exclude_vat_regimes is not None:
            if mvt.vat_regime in self.exclude_vat_regimes:
                return
        amount = mvt.amount
        if not amount:
            return
        if self.dc == DC.debit:
            amount = -amount
        if amount < 0 and not self.both_dc:
            return
        field_values[self.name] += amount
        if self.is_payable:
            if self.dc == dcl.journal.dc:
                amount = - amount
            # k = ((mvt.account, None), mvt.project, mvt.vat_class, mvt.vat_regime)
            k = ((mvt.account, None), None, None, None)
            payable_sums.collect(k, amount)
            # k = (dcl.journal.account, None, None, None)
            # payable_sums.collect(k, amount)


# class AccountDeclarationField(MvtDeclarationField):
#     pass
    # def __init__(self, value, dc, vat_columns, *args, **kwargs):
    #     # kwargs.update(fieldnames=value)
    #     kwargs.update(vat_columns=vat_columns)
    #     super(AccountDeclarationField, self).__init__(
    #         value, dc, *args, **kwargs)



class DeclarationFieldsBase(dd.ChoiceList):
    verbose_name_plural = _("Declaration fields")
    item_class = DeclarationField
    column_names = "value name text description *"

    # @classmethod
    # def add_account_field(cls, *args, **kwargs):
    #     cls.add_item_instance(
    #         AccountDeclarationField(*args, **kwargs))

    @classmethod
    def add_mvt_field(cls, *args, **kwargs):
        cls.add_item_instance(
            MvtDeclarationField(*args, **kwargs))

    @classmethod
    def add_sum_field(cls, *args, **kwargs):
        cls.add_item_instance(
            SumDeclarationField(*args, **kwargs))


    @classmethod
    def add_writable_field(cls, *args, **kwargs):
        cls.add_item_instance(
            WritableDeclarationField(*args, **kwargs))


    @dd.displayfield(_("Description"))
    def description(cls, fld, ar):
        if ar is None:
            return ''
        elems = [fld.help_text, E.br()]
        def x(label, lst, xlst):
            if lst is None:
                spec = ''
            else:
                lst = sorted([i.name or i.value for i in lst])
                spec = ' '.join(lst)
            if xlst is not None:
                xlst = sorted(["!"+(i.name or i.value) for i in xlst])
                spec += ' ' + ' '.join(xlst)
            spec = spec.strip()
            if spec:
                elems.extend([label, " ", spec, E.br()])

        x(_("columns"), fld.vat_columns, fld.exclude_vat_columns)
        x(_("regimes"), fld.vat_regimes, fld.exclude_vat_regimes)
        x(_("classes"), fld.vat_classes, fld.exclude_vat_classes)


        elems += [
            fld.__class__.__name__, ' ',
            str(fld.dc),
            "" if fld.both_dc else " only",
            E.br()]

        if len(fld.observed_fields):
            names = []
            for f in fld.observed_fields:
                n = f.value
                if f.value in fld.minus_observed_fields:
                    n = "- " + n
                elif len(names) > 0:
                    n = "+ " + n
                names.append(n)
            elems += ['= ', ' '.join(names), E.br()]

        return E.div(*forcetext(elems))


class VatRule(dd.Choice):
    start_date = None
    end_date= None
    vat_area = None
    trade_type = None
    vat_class = None
    vat_regime = None
    rate = ZERO
    vat_account = None
    # vat_returnable = None
    vat_returnable_account = None

    def __init__(self,
                 vat_class=None, rate=None,
                 vat_area=None, trade_type=None,
                 vat_regime=None, vat_account=None,
                 vat_returnable_account=None):
        kw = dict(vat_area=vat_area)
        if rate is not None:
            kw.update(rate=Decimal(rate))
        # if vat_returnable is None:
        #     vat_returnable = vat_returnable_account is not None
        # kw.update(vat_returnable=vat_returnable)
        if trade_type:
            kw.update(trade_type=TradeTypes.get_by_name(trade_type))
        if vat_regime:
            kw.update(vat_regime=VatRegimes.get_by_name(vat_regime))
        if vat_class:
            kw.update(vat_class=VatClasses.get_by_name(vat_class))
        if vat_account:
            kw.update(vat_account=vat_account)
        if vat_returnable_account:
            kw.update(vat_returnable_account=vat_returnable_account)
        # text = "{trade_type} {vat_area} {vat_class} {rate}".format(**kw)
        super(VatRule, self).__init__(None, None, **kw)

    def __str__(rule):
        lst = []
        only = []
        lst.append(gettext("VAT rule {}: ".format(rule.value)))
        if rule.trade_type is not None:
            only.append(str(rule.trade_type))
        if rule.vat_regime is not None:
            only.append(str(rule.vat_regime))
        if rule.vat_area is not None:
            only.append(str(rule.vat_area))
        if rule.vat_class is not None:
            only.append(str(rule.vat_class))
        if len(only):
            lst.append(gettext("if ({}) then".format(', '.join(only))))
        lst.append(gettext("apply {} %".format(rule.rate)))
        lst.append(gettext("and book to {}").format(rule.vat_account))
        if rule.vat_returnable_account is not None:
            lst.append(gettext("(return to {})").format(rule.vat_returnable_account))
        return '\n'.join(lst)

    #     kw = dict(
    #         trade_type=self.trade_type,
    #         vat_regime=self.vat_regime,
    #         vat_class=self.vat_class,
    #         rate=self.rate,
    #         vat_area=self.vat_area, seqno=self.seqno)
    #     return "{trade_type} {vat_area} {vat_class} {rate}".format(**kw)


class VatRules(dd.ChoiceList):
    verbose_name = _("VAT rule")
    verbose_name_plural = _("VAT rules")
    item_class = VatRule
    column_names = "value description"

    @classmethod
    def get_vat_rule(
            cls, vat_area,
            trade_type=None, vat_regime=None, vat_class=None,
            date=None, default=models.NOT_PROVIDED):
        for i in cls.get_list_items():
            if i.vat_area is not None and vat_area != i.vat_area:
                continue
            if i.trade_type is not None and trade_type != i.trade_type:
                continue
            if i.vat_class is not None and vat_class != i.vat_class:
                continue
            if i.vat_regime is not None and vat_regime != i.vat_regime:
                continue
            if date is not None:
                if i.start_date and i.start_date > date:
                    continue
                if i.end_date and i.end_date < date:
                    continue
            return i
        if default is models.NOT_PROVIDED:
            msg = _("No VAT rule for ({!r},{!r},{!r},{!r},{!r})").format(
                    trade_type, vat_class, vat_area, vat_regime,
                    dd.fds(date))
            if False:
                dd.logger.info(msg)
            else:
                raise Warning(msg)
        return default

    @dd.displayfield(_("Description"))
    def description(cls, rule, ar):
        return str(rule)


# we add a single rule with no rate and no conditions, iow any combination is
# allowed and no vat is applied. The declaration modules will clear this list
# and fill it with their rules.

VatRules.add_item()


from django.core.exceptions import ValidationError

if dd.is_installed('vat'):

    class VatNumberValidator:

        def __init__(self, name, **kw):
            self.name = name

            for attr, value in kw.items():
                setattr(self, attr, value)

        def validate(self, vn_dict):
            if not vn_dict:
                msg = gettext(("You have entered an invalid VAT identification "
                    + "number.\nThe general format follows: "))
                vfmt = self.origin.country_code
                if self.origin.dummy_prefix:
                    vfmt += re.sub(r"\d", "x", self.origin.dummy_prefix)
                vfmt += "x" * self.origin.length
                if self.origin.dummy_suffix:
                    vfmt += re.sub(r"\d", "x", self.origin.dummy_suffix)
                msg += vfmt
                msg += "\nWhere each 'x' is a digit."
                raise ValidationError(msg)

            if len(vn_dict['number']) != self.origin.length:
                if self.origin.lower_bound:
                    if self.origin.lower_bound > len(vn_dict['number']):
                        raise ValidationError(
                            _("VAT id must contain at least {} digits.").format(
                                self.origin.lower_bound))
                            # Note: using f"" here would disturb i18n
                else:
                    raise ValidationError(
                        _("VAT id must contain {} digits.").format(
                            self.origin.length))

            cc = vn_dict.get('country_code', None)
            if cc and cc != self.origin.country_code:
                raise ValidationError(
                    _("Country code ({}) does not match with {}.").format(
                        self.origin.country_code, vn_dict['country_code']))

        def generate(self):
            return str(random.randint(int("1" * self.origin.length), int("9" * self.origin.length)))

        def _assign_to_origin(self, origin):
            origin.validator = self
            self.origin = origin

    class VatOrigin:
        country_code = None
        length = None # either an int or a tuple (lower_bound, upper_bound, standard)
        lower_bound = None
        standard = None
        pattern = None
        dummy_prefix = None
        dummy_suffix = None
        validator = None
        dependent_attributes = ['dummy_prefix', 'dummy_suffix'] # dependent on pattern

        def __init__(self, country_code, length, **kw):
            self.country_code = country_code
            self._resolve_length(length)
            self.pattern = kw.get('pattern', None)
            if self.pattern is None:
                self._set_default_pattern()
            for attr in self.dependent_attributes:
                setattr(self, attr, kw.get(attr, None))
            validator = kw.get('validator', None)
            if validator is None:
                validator = VatNumberValidator('default')
            validator._assign_to_origin(self)

        def _resolve_length(self, length):
            if type(length) == tuple:
                self.lower_bound = length[0]
                self.standard = length[2]
                self.length = length[1]
            else:
                self.length = length

        def _set_default_pattern(self):
            p = "^(?P<country_code>[A-Z]{2}) (?P<number>[0-9]{%s}"
            if self.lower_bound:
                p = p % self.lower_bound
                p = p + ("([0-9]{%s})?" % (self.length - self.lower_bound))
            else:
                p = p % self.length
            p += ")$"
            self.pattern = p

        @property
        def striped_pattern(self):
            if self.pattern:
                p = self.pattern.split()[1]
                if not p.startswith('^'):
                    p = '^' + p
                return p

        @property
        def compact_pattern(self):
            if self.pattern:
                return "".join(self.pattern.split())

        @property
        def pattern_groups(self):
            return dict(re.compile(self.pattern).groupindex).keys()


    class ModValidator(VatNumberValidator):

        def __init__(self, denominator, numerator_length, remainder_length):
            self.denominator = denominator
            self.numerator_length = numerator_length
            self.remainder_length = remainder_length
            super().__init__('mod')

        def validate(self, vn_dict):
            super().validate(vn_dict)
            number = vn_dict['number']
            numerator = int(number[:self.remainder_length * -1])
            remainder = int(number[self.remainder_length * -1:])
            if self.denominator - (numerator % self.denominator) != remainder:
                raise ValidationError(
                    _("Modulo {} check failed for VAT identification number in {}").format(
                    self.denominator, self.origin.country_code))

        def generate(self):
            nl = self.numerator_length
            d = self.denominator
            rl = self.remainder_length
            n = random.randint(int("1" * nl), int("9" * nl))
            return str(n) + (("0" * rl) + str(d - (n % d)))[rl * -1:]


    class VatOrigins:
        _items = dict()

        def get(self, key):
            return self._items.get(key, None)

        def add_item(self, key, value):
            self._items[key] = value

    vat_origins = VatOrigins()


    class VatNumberManager:
        _value = None
        _vat_origins = vat_origins

        obj = None
        country_code = None
        origin = None
        vn = None

        def __init__(self, obj):
            self.obj = obj
            if obj.vat_id:
                self.vn = self.unformat(obj.vat_id)
            if obj.country and obj.country.isocode:
                self.country_code = obj.country.isocode
            elif self.vn and re.match('^[A-Z]{2}$', self.vn[:2]):
                self.country_code = self.vn[:2]
            if self.country_code:
                self.set_origin()

        def set_origin(self, country_code=None):
            if country_code:
                self.country_code = country_code
            origin = self._vat_origins.get(self.country_code)
            if origin is None:
                origin = VatOrigin(self.country_code, (2, 30, None),
                    pattern="^(?P<country_code>[A-Z]{2}) (?P<number>.*)$")
            self.origin = origin

        def validate(self, vn_dict=None, online=False):
            if self.origin is None or self.vn is None:
                return
            if not vn_dict:
                vn_dict = self.decompose()
            self.origin.validator.validate(vn_dict)

            if online:
                attempts = 0
                while True:
                    attempts += 1
                    result = None
                    try:
                        result = pyvat.check_vat_number(self.vn, self.country_code)
                        if result.is_valid is False:
                            msg = gettext("Invalid VAT identification number {}").format(
                                self.obj.vat_id) + ":\n"
                            logs = [l for l in result.log_lines if 'xml' not in l]
                            if logs:
                                msg += "\n".join(logs)
                            else:
                                msg += gettext("Not registered in {}.").format(self.country_code)
                            raise ValidationError(msg)
                        elif result.is_valid is None:
                            return
                        else:
                            # TODO: compare the name
                            return
                    except pyvat.exceptions.ServerError as e:
                        dd.logger.info(
                            "pyvat.check_vat_number('%s', '%s') failed with {}:",
                            self.vn, self.country_code, e)
                        if result is None:
                            dd.logger.info("   (no response)")
                        else:
                            dd.logger.info("  " + ("\n  ".join(result.log_lines)))
                        if attempts > MAX_ONLINE_ATTEMPTS:
                            raise ValidationError(str(e))
                        time.sleep(1)

        def unformat(self, vn):
            for c in "- .,_":
                vn = vn.replace(c, "")
            return vn.upper()

        def format(self, vn):
            if self.origin is None:
                return vn
            length = self.origin.length
            if length is None:
                return vn
            if self.origin.standard:
                length = self.origin.standard
            elif self.origin.lower_bound:
                length = len(vn)
            count = 1
            s = ""
            while length - count * 3 >= 2:
                if count == 1:
                    s = vn[-3:]
                else:
                    s = vn[count * 3 * -1: (count - 1) * 3 * -1] + "." + s
                count += 1
            s = vn[: (count - 1) * 3 * -1] + "." + s
            return s

        @property
        def value(self):
            if self._value:
                return self._value
            return self.sanitize()

        @value.setter
        def value(self, value):
            self.vn = value
            self.sanitize(value)

        def generate_vid(self):
            if self.origin is None:
                return
            groups = self.origin.pattern_groups
            s = self.country_code + " "
            if 'prefix' in groups:
                s += self.origin.dummy_prefix
            s += self.origin.validator.generate()
            if 'suffix' in groups:
                s += self.origin.dummy_suffix
            self.vn = s
            self.sanitize()
            return s

        def decompose(self, vn=None):
            if vn is None:
                vn = self.vn
            m = re.match(self.origin.compact_pattern, vn)
            if not m:
                m = re.match(self.origin.striped_pattern, vn)
            if not m:
                m = re.match(self.origin.pattern, vn)
            if m:
                return m.groupdict()

        def compose(self, vn_dict):
            if self.origin is None:
                return
            country_code = vn_dict.get('country_code', None)
            if not country_code:
                country_code = self.country_code
            s = country_code + ' '
            prefix = vn_dict.get('prefix', None)
            if prefix:
                s += prefix
            number = vn_dict.get('number', None)
            s += self.format(number)
            suffix = vn_dict.get('suffix', None)
            if suffix:
                s += suffix
            self._value = s
            return s

        def sanitize(self, vn=None):
            if self.origin is None or self.vn is None:
                return
            if vn:
                vn = self.unformat(vn)
                self.vn = vn
            else:
                vn = self.vn
            vn_dict = self.decompose(vn)
            if vn_dict and self.origin.standard:
                for i in range(self.origin.standard - len(vn_dict['number'])):
                    vn_dict['number'] = "0" + vn_dict['number']
            self.validate(vn_dict)
            value = self.compose(vn_dict)
            self.obj.vat_id = value
            return value

    vat_origins.add_item('BE', VatOrigin('BE', (9, 10, 10),
        validator=ModValidator(97, 8, 2)))

    vat_origins.add_item('AT', VatOrigin('AT', 8, dummy_prefix="U",
        pattern="^(?P<country_code>AT) (?P<prefix>U)(?P<number>[0-9]{8})$"))

    vat_origins.add_item('NL', VatOrigin('NL', 9, dummy_suffix="B01",
        pattern="^(?P<country_code>NL) (?P<number>[0-9]{9})(?P<suffix>B(?P<company_index>[0-9]{2}))$"))

    for cc, length in {
            "HR": 11,
            "DK": 8,
            "EE": 9,
            "FI": 8,
            "FR": 11,
            "DE": 9,
            "EL": 9,
            "HU": 8,
            "IT": 11,
            "LV": 11,
            "LT": 12,
            "LU": 8,
        }.items():
        vat_origins.add_item(cc, VatOrigin(cc, length))


class VatSubjectable(dd.Model):

    class Meta:
        abstract = True

    if dd.is_installed('vat'):

        vat_regime = VatRegimes.field(blank=True)
        vat_id = models.CharField(_("VAT id"), max_length=200, blank=True)

        active_fields = 'vat_id'

        _vnm = None
        """VatNumberManager object."""

        def vat_id_changed(self):
            self._vnm.set_origin(self.country.isocode)

        @dd.chooser()
        def vat_regime_choices(self, country):
            return VatRegimes.get_choices_for_country(country)

        def full_clean(self):
            super(VatSubjectable, self).full_clean()
            self.vid_manager.sanitize()

        @property
        def vid_manager(self):
            if not self._vnm:
                self._vnm = VatNumberManager(self)
            if self.vat_id and self.country and self.country.isocode != self._vnm.country_code:
                self.vat_id_changed()
            return self._vnm


if dd.is_installed('vat') and dd.plugins.vat.use_online_check:

    class VatIdChecker(Checker):
        model = VatSubjectable
        verbose_name = _("Validate VAT id from online registry.")

        def get_checkdata_problems(self, obj, fix=False):
            try:
                obj.vid_manager.validate(online=True)
            except ValidationError as e:
                yield (False, e.message)

    VatIdChecker.activate()

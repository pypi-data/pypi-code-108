import logging

from django.forms import model_to_dict

from isc_common import setAttr, delAttr, dictinct_list
from isc_common.auth.managers.base_user_manager import BaseUserManager, BaseUserQuerySet
from isc_common.auth.models.usergroup import UserGroup
from isc_common.bit import IsBitOn
from isc_common.common.functions import get_dict_only_model_field
from isc_common.http.DSRequest import DSRequest

logger = logging.getLogger(__name__)


class UserQuerySet(BaseUserQuerySet):
    pass


class UserManager(BaseUserManager):
    use_in_migrations = True

    def get_or_create(self, defaults=None, **kwargs):
        from isc_common.auth.models.user import User

        if defaults is None:
            defaults = kwargs

        username = kwargs.get('username')
        if username is None:
            username = defaults.get('username')
        if username is None:
            username = User.full_name(
                first_name=defaults.get('first_name'),
                last_name=defaults.get('last_name'),
                middle_name=defaults.get('middle_name'),
                birthday=defaults.get('birthday'),
                translit=True,
            )

            if username is None:
                raise Exception('username is None')

        user = User.objects.getOptional(username=username)
        if user is None:
            description = defaults.get('description')

            if description is not None and description.strip() == '':
                description = None

            setAttr(defaults, 'description', description)
            user_data = self.get_user_data(**defaults)
            try:
                user = super().get(username=username)
                return user, False

            except User.DoesNotExist as ex:
                setAttr(user_data, 'username', username)
                user = super().create(**user_data)
                user.set_password(username)
                user.save()

                return user, True


        else:
            return user, False

    def update_or_create(self, defaults=None, **kwargs):
        return super().update_or_create(defaults=defaults, **kwargs)

    @classmethod
    def get_user_data(cls, **kwargs):
        last_name = kwargs.get('last_name')
        first_name = kwargs.get('first_name')
        middle_name = kwargs.get('middle_name')
        description = kwargs.get('description')
        birthday = kwargs.get('birthday')
        # username = kwargs.get('username')

        user_data = dict(
            last_name=last_name.replace('ё', 'e').strip() if last_name else None,
            first_name=first_name.replace('ё', 'e').strip() if first_name else None,
            middle_name=middle_name.replace('ё', 'e').strip() if middle_name else None,
            birthday=birthday if birthday else None,
            description=description,
            # username=username
        )

        return user_data

    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db).filter(deleted_at=None)

    @classmethod
    def getRecord(cls, **kwargs):
        record = kwargs.get('record')
        res = {
            'birthday': record.birthday,
            'bot': IsBitOn(record.props, 0),
            'color': record.color,
            'deliting': record.deliting,
            'description': record.description,
            'editing': record.editing,
            'email': record.email,
            'first_name': record.first_name,
            'id': record.id,
            'last_login': record.last_login,
            'last_name': record.last_name,
            'lastmodified': record.lastmodified,
            'middle_name': record.middle_name,
            'password': record.password,
            'short_name': record.get_short_name,
            'short_name1': record.get_short_name1,
            'username': record.username,
        }
        return res

    @classmethod
    def getRecord1(cls, record):
        return cls.getRecord(**record)

    def updateFromRequest(self, request):
        from isc_common.auth.models.user import User

        request = DSRequest(request=request)
        data = request.get_data()

        data = self.check_data_for_multi_select(data=data)
        _data = data.copy()

        delAttr(data, 'usergroup')
        oldValues = request.get_oldValues()

        _oldValues = oldValues.get('data')
        if not _oldValues:
            _oldValues = oldValues

        _oldValues = self.check_data_for_multi_select(data=_oldValues)

        data = self._remove_prop_(data)
        values = [item for item in dictinct_list(set(_oldValues) - set(data)) if not item.startswith('_')]
        for item in values:
            setAttr(data, item, None)

        user_id = request.get_id()
        if user_id is None:
            user_id = data.get('id')

        super().filter(id=user_id).update(**get_dict_only_model_field(data=data, model=User, exclude=['password']))

        user = self.model.objects.get(id=user_id)
        if user.check_password(data.get('password')) is False:
            user.set_password(data.get('password', None))
            user.save()
            setAttr(data, 'password', user.password)
            setAttr(data, 'short_name', user.get_short_name)

        return _data

    def createFromRequest(self, request):
        from isc_common.auth.models.user import User

        request = DSRequest(request=request)
        data = request.get_data(excluded_keys=['id'])

        usergroup_id = data.get('usergroup_id')
        delAttr(data, 'usergroup_id')
        delAttr(data, 'on_line')

        kwarg = self.clone_data(data=data, model=User)
        user = User.objects.create(**kwarg)
        password = request.get_data(excluded_keys=['id']).get('password')

        user.set_password(password)
        user.save(using=self._db)

        user = User.objects.get(pk=user.id)
        if isinstance(usergroup_id, list):
            for group in usergroup_id:
                user.usergroup.add(group)

        res = model_to_dict(user)
        setAttr(res, 'props', res.get('props')._value)

        return res

    def _create_user(self, usergroup, username, email, password, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')

        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        if isinstance(usergroup, list):
            user.usergroup.set(usergroup)
        elif isinstance(usergroup, UserGroup):
            user.usergroup.set([usergroup])

        return user

    def create_user(self, usergroup, username, email=None, password=None, **extra_fields):
        try:
            return self.model.objects.get(username=username)
        except self.model.DoesNotExist:
            return self._create_user(usergroup, username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        try:
            return self.model.objects.get(username=username)
        except self.model.DoesNotExist:
            return self._create_user(usergroup=UserGroup.objects.get(code='administrators'), username=username, email=email, password=password, **extra_fields)

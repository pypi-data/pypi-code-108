from django.db.models.signals import post_save
from django.dispatch import receiver

from drf_auth_service.models import Service, Config
from drf_auth_service.settings import ObjDict, SETTINGS_TO_IMPORT_IN_DB, settings


@receiver(post_save, sender=Service)
def service_post_save(sender, instance, created, **kwargs):
    if created:
        configs = []

        for key in SETTINGS_TO_IMPORT_IN_DB:
            val = getattr(settings, key)
            if type(val) == ObjDict or type(val) == dict:

                for dict_key, dict_value in val.items():
                    if not type(dict_value) == list:
                        configs.append(Config(
                            type='str',
                            value=dict_value,
                            key=dict_key,
                            service=instance
                        ))

            elif type(val) == list:
                value = ''
                for list_value in val:
                    value += f"{list_value},"

                configs.append(Config(
                    type='str',
                    value=value.rstrip(','),
                    key=key,
                    service=instance
                ))

            else:
                configs.append(Config(
                    type=type(val).__name__ if type(val) is not None else 'str',
                    value=str(val),
                    key=key,
                    service=instance
                ))

        Config.objects.bulk_create(configs)


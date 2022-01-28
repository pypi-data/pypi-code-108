from django.db import migrations

from isc_common.auth.models.user import User
from isc_common.auth.models.usergroup import UserGroup


def rec_admin_group(apps, schema_editor):
    UserGroup.objects.get_or_create(code='administrators', name="Администраторы", editing=False)
    developers = UserGroup.objects.get_or_create(code='developers', name="Разработчики", editing=False)
    User.objects.create_superuser(username='admin', password='admin', email='info@ivc-inform.ru')
    User.objects.create_user(usergroup=[developers[0]], username='uandrew', password='Uandrew1965', email='uag@ivc-inform.ru')
    User.objects.create_user(usergroup=[developers[0]], username='nasonov', password='nasonov', email='nma@ivc-inform.ru')
    User.objects.create_user(usergroup=[developers[0]], username='developer', password='developer', email='info@ivc-inform.ru', deliting=False, editing=False)

def item_maker(apps, schema_editor):
    group = UserGroup.objects.get_or_create(code='item_maker', name="item_maker", editing=False)
    User.objects.create_user(usergroup=[group[0]], username='item_maker', password='item_maker', email='item_maker@ivc-inform.ru', deliting=False, editing=False)

def rec_message_states(apps, schema_editor):
    from tracker.models.messages_state import Messages_state
    Messages_state.objects.get_or_create(code="new", name="Новая", editing=False, deliting=False)
    Messages_state.objects.get_or_create(code="closed", name="Закрыто")
    Messages_state.objects.get_or_create(code="postponed", name="Отложено")
    Messages_state.objects.get_or_create(code="onworking", name="В работе")
    Messages_state.objects.get_or_create(code="wait", name="Ожидание")

def rec_message_theme(apps, schema_editor):
    from tracker.models.messages_theme import Messages_theme
    Messages_theme.objects.get_or_create(code="auto_from_error", name="Автоматически занесенные из сообщений об ошибках.", editing=False, deliting=False)

def rec_message_theme1(apps, schema_editor):
    from tracker.models.messages_theme import Messages_theme
    Messages_theme.objects.get_or_create(code="item_maker", name="Процесс заполнения товареных позиций.", editing=False, deliting=False)


class Migration(migrations.Migration):
    dependencies = [
        ('isc_common', '0022_auto_20190414_0925'),
    ]
    atomic = True

    operations = [
        migrations.RunPython(rec_admin_group),
        migrations.RunPython(item_maker),
        migrations.RunPython(rec_message_states),
        migrations.RunPython(rec_message_theme),
        migrations.RunPython(rec_message_theme1),
    ]

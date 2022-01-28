from django.db import migrations


def parse_video_id(value):
    parts = [v for v in value.split("/") if v]
    return parts[-1]


def migrate_data(apps, schema_editor):
    Event = apps.get_model("event", "Event")
    EventSettings = apps.get_model("event", "Event_SettingsStore")
    Submission = apps.get_model("submission", "Submission")
    VimeoLink = apps.get_model("pretalx_vimeo", "VimeoLink")
    for event in Event.objects.all().filter(plugins__contains="pretalx_vimeo"):
        settings = {
            s.key: s.value
            for s in EventSettings.objects.filter(
                object=event, key__startswith="vimeo_url_"
            )
        }
        for key, value in settings.items():
            submission = Submission.objects.filter(
                event=event, code=key.split("_")[-1]
            ).first()
            if submission:
                VimeoLink.objects.create(
                    submission=submission, video_id=parse_video_id(value)
                )


def delete_all_links(apps, schema_editor):
    VimeoLink = apps.get_model("pretalx_vimeo", "VimeoLink")
    VimeoLink.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("pretalx_vimeo", "0001_initial"),
    ]

    operations = [migrations.RunPython(migrate_data, migrations.RunPython.noop)]

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Assignment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "username_mode",
                    models.IntegerField(
                        choices=[(0, "any"), (1, "matches"), (2, "don't match")]
                    ),
                ),
                ("username", models.CharField(max_length=255, blank=True)),
                ("domain", models.CharField(max_length=255)),
                ("copy", models.BooleanField(default=False)),
                ("weight", models.PositiveIntegerField(default=0)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "ordering": ("-weight",),
                "verbose_name": "Assignment",
                "verbose_name_plural": "Assignments",
            },
        ),
    ]

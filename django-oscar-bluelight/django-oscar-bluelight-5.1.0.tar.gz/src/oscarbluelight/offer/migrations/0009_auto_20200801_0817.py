# Generated by Django 3.0.8 on 2020-08-01 07:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("offer", "0021_rangeproductset"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="range",
            options={
                "ordering": ["name"],
                "verbose_name": "Range",
                "verbose_name_plural": "Ranges",
            },
        ),
    ]

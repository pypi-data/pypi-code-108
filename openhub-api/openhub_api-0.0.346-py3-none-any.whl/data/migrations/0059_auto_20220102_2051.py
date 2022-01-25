from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('data', '0058_alter_hardware_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hardwarechanneltypes',
            name='channel_type',
            field=models.CharField(max_length=25),
        ),
        migrations.AlterField(
            model_name='hardwarechanneltypes',
            name='hardware_type',
            field=models.CharField(max_length=25),
        ),
    ]


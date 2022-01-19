from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_cash_register.validators


def create_actions(apps, schema_editor):
    action_tuple = ('Product addition', 'Product change', 'Product removal', 'Write-off of product', 'Product returns')
    action_model = apps.get_model('django_cash_register', 'ActionType')

    for action in action_tuple:
        action_model.objects.create(name=action)


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'type',
                'verbose_name_plural': 'Actions',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('barcode', models.CharField(blank=True, max_length=255, null=True, verbose_name='Barcode')),
                ('qrcode', models.CharField(blank=True, max_length=500, null=True, verbose_name='QR-code')),
                ('product_count', models.FloatField(validators=[django_cash_register.validators.validate_not_minus], verbose_name='Count')),
                ('purchase_price', models.FloatField(validators=[django_cash_register.validators.validate_not_minus], verbose_name='Purchase price')),
                ('price', models.FloatField(validators=[django_cash_register.validators.validate_not_minus], verbose_name='Price')),
                ('promotion_price', models.FloatField(blank=True, null=True, validators=[django_cash_register.validators.validate_not_minus], verbose_name='Promotional price')),
                ('promotion_product', models.BooleanField(default=False, verbose_name='Promotional product')),
                ('image', models.ImageField(blank=True, null=True, upload_to='', verbose_name='Image')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='django_cash_register.category', verbose_name='Category')),
            ],
            options={
                'verbose_name': 'poduct',
                'verbose_name_plural': 'Products',
            },
        ),
        migrations.CreateModel(
            name='ProductHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('barcode', models.CharField(blank=True, max_length=255, null=True, verbose_name='Barcode')),
                ('qrcode', models.CharField(blank=True, max_length=500, null=True, verbose_name='QR-code')),
                ('product_count', models.FloatField(validators=[django_cash_register.validators.validate_not_minus], verbose_name='Count')),
                ('purchase_price', models.FloatField(validators=[django_cash_register.validators.validate_not_minus], verbose_name='Purchase price')),
                ('price', models.FloatField(validators=[django_cash_register.validators.validate_not_minus], verbose_name='Price')),
                ('promotion_price', models.FloatField(blank=True, null=True, validators=[django_cash_register.validators.validate_not_minus], verbose_name='Promotional price')),
                ('promotion_product', models.BooleanField(default=False, verbose_name='Promotional product')),
                ('image', models.ImageField(blank=True, null=True, upload_to='', verbose_name='Image')),
                ('active', models.BooleanField(verbose_name='Active')),
                ('exists', models.BooleanField(verbose_name='Available')),
                ('action_date', models.DateTimeField(auto_now=True, verbose_name='Date')),
                ('action', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='django_cash_register.actiontype', verbose_name='Action')),
                ('category', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='django_cash_register.category', verbose_name='Category')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='django_cash_register.product', verbose_name='Product')),
            ],
            options={
                'verbose_name': 'history',
                'verbose_name_plural': 'History',
            },
        ),
        migrations.CreateModel(
            name='CartList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(limit_choices_to={'is_active': True, 'is_staff': True}, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Cashier')),
            ],
            options={
                'verbose_name': 'cart action',
                'verbose_name_plural': 'Cart list',
            },
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_count', models.FloatField(validators=[django_cash_register.validators.validate_not_minus], verbose_name='Count')),
                ('basket_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_cash_register.cartlist', verbose_name='Cart number')),
                ('product', models.ForeignKey(limit_choices_to={'active': True}, on_delete=django.db.models.deletion.PROTECT, to='django_cash_register.product', verbose_name='Product')),
            ],
            options={
                'verbose_name': 'cart',
                'verbose_name_plural': 'Open carts',
            },
        ),
        migrations.RunPython(create_actions),
    ]

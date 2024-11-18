# Generated by Django 4.2.16 on 2024-10-28 15:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0006_profile'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShippingAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
                ('address1', models.CharField(max_length=255)),
                ('address2', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('state', models.CharField(blank=True, max_length=255, null=True)),
                ('zipcode', models.CharField(blank=True, max_length=255, null=True)),
                ('country', models.CharField(max_length=255)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Shipping Address',
            },
        ),
        migrations.RemoveField(
            model_name='useraddress',
            name='user',
        ),
        migrations.RemoveField(
            model_name='order',
            name='shipping_method',
        ),
        migrations.AlterField(
            model_name='shoppingcart',
            name='quantity',
            field=models.IntegerField(default=0),
        ),
        migrations.DeleteModel(
            name='ShippingMethod',
        ),
        migrations.DeleteModel(
            name='UserAddress',
        ),
        migrations.AddField(
            model_name='order',
            name='ShippingAddress',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.shippingaddress'),
        ),
    ]
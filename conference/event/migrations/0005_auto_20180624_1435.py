# Generated by Django 2.0.6 on 2018-06-24 19:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0004_auto_20171030_2102'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='session',
            options={'ordering': ('start', 'room__sorder')},
        ),
        migrations.AlterField(
            model_name='session',
            name='room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='event.Room'),
        ),
        migrations.AlterField(
            model_name='session',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]

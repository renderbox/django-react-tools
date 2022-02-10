# Generated by Django 3.0.7 on 2021-09-30 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reacttools', '0011_reactappsettings_react_root'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reactappsettings',
            name='build_cmd',
            field=models.CharField(blank=True, help_text='Defaults to REACT_BUILD_COMMAND value in settings.py.', max_length=128),
        ),
        migrations.AlterField(
            model_name='reactappsettings',
            name='manifest',
            field=models.CharField(blank=True, help_text='Defaults to REACT_MANIFEST_FILE value in settings.py.', max_length=128),
        ),
    ]

# Generated by Django 2.1.9 on 2019-06-12 20:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("reacttools", "0006_auto_20190612_2054"),
    ]

    operations = [
        migrations.RenameField(
            model_name="reactappsettings",
            old_name="css",
            new_name="css_data",
        ),
        migrations.RenameField(
            model_name="reactappsettings",
            old_name="js",
            new_name="js_data",
        ),
    ]

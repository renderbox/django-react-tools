# Generated by Django 2.1.9 on 2019-06-12 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reacttools", "0009_auto_20190612_2113"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reactappsettings",
            name="build_dir",
            field=models.CharField(
                blank=True,
                help_text="Default assumes that the build path is at the root of the project (i.e. project_dir/build/).",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="reactappsettings",
            name="project_dir",
            field=models.CharField(
                help_text="This can be a relative path and will be expanded on use.",
                max_length=128,
            ),
        ),
    ]

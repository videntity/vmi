# Generated by Django 2.2.10 on 2020-03-19 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_auto_20191123_2239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='slug',
            field=models.SlugField(blank=True, default='', max_length=250),
        ),
    ]

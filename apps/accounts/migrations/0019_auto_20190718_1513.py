# Generated by Django 2.1.8 on 2019-07-18 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0018_auto_20190522_1929'),
    ]

    operations = [
        migrations.AddField(
            model_name='individualidentifier',
            name='country',
            field=models.CharField(blank=True, db_index=True, default='US', help_text='e.g., a two letter country code in ISO 3166 format.', max_length=2),
        ),
        migrations.AddField(
            model_name='individualidentifier',
            name='subdivision',
            field=models.CharField(blank=True, default='', help_text="e.g., a country's subdivision such as a state or province.", max_length=2, verbose_name='State'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='subject',
            field=models.CharField(blank=True, db_index=True, default='161255285274119', help_text='Subject ID', max_length=64),
        ),
    ]

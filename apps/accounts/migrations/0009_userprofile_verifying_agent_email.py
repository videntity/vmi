# Generated by Django 2.2.8 on 2020-02-21 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_auto_20191123_2239'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='verifying_agent_email',
            field=models.EmailField(blank=True, default='', help_text='email of agent performing identity verification', max_length=254),
        ),
    ]

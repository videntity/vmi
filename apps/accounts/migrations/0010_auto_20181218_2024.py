# Generated by Django 2.1.1 on 2018-12-18 20:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_auto_20181217_1313'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'permissions': (('can_change_address', 'Can change address'),)},
        ),
        migrations.AlterModelOptions(
            name='individualidentifier',
            options={'permissions': (('can_change_individual_identifier', 'Can change individual identifier'),)},
        ),
        migrations.AlterModelOptions(
            name='organizationidentifier',
            options={'permissions': (('can_change_organization_identifier', 'Can change organization identifier'),)},
        ),
        migrations.AlterModelOptions(
            name='userprofile',
            options={'permissions': (('can_change_profile_another_user', 'Can change basic profile for another user.'), ('can_view_profile_another_user', 'Can view basic profile for another user.'))},
        ),
    ]
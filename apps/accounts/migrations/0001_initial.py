# Generated by Django 2.1.1 on 2018-11-20 14:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivationKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(default=uuid.uuid4, max_length=40)),
                ('expires', models.DateTimeField(blank=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street_1', models.CharField(blank=True, default='', max_length=255)),
                ('street_2', models.CharField(blank=True, default='', max_length=255)),
                ('city', models.CharField(blank=True, default='', max_length=255)),
                ('state', models.CharField(blank=True, default='', max_length=2)),
                ('zipcode', models.CharField(blank=True, default='', max_length=10)),
                ('subject', models.CharField(blank=True, default='', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='IndividualIdentifier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.SlugField(blank=True, default='', max_length=255)),
                ('value', models.CharField(blank=True, db_index=True, default='', max_length=255)),
                ('metadata', models.TextField(blank=True, default='', help_text='JSON Object')),
                ('type', models.CharField(blank=True, default='', max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='MFACode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(blank=True, default=uuid.uuid4, editable=False, max_length=36)),
                ('tries_counter', models.IntegerField(default=0, editable=False)),
                ('code', models.CharField(blank=True, editable=False, max_length=4)),
                ('mode', models.CharField(choices=[('', 'None'), ('EMAIL', 'Email'), ('FIDO', 'FIDO U2F'), ('SMS', 'Text Message (SMS)')], default='', max_length=5)),
                ('valid', models.BooleanField(default=True)),
                ('expires', models.DateTimeField(blank=True)),
                ('added', models.DateField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=255)),
                ('slug', models.SlugField(blank=True, default='', max_length=255, unique=True)),
                ('registration_code', models.CharField(blank=True, default='', max_length=100)),
                ('domain', models.CharField(blank=True, default='', help_text='If populated, restrict email registration to this address.', max_length=512)),
                ('website', models.CharField(blank=True, default='', max_length=512)),
                ('phone_number', models.CharField(blank=True, default='', max_length=15)),
                ('addresses', models.ManyToManyField(blank=True, to='accounts.Address')),
            ],
        ),
        migrations.CreateModel(
            name='OrganizationAffiliationRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('organization', models.ForeignKey(on_delete='PROTECT', to='accounts.Organization')),
                ('user', models.ForeignKey(on_delete='PROTECT', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('can_approve_affiliation', 'Can approve affiliation'),),
            },
        ),
        migrations.CreateModel(
            name='OrganizationIdentifier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.SlugField(blank=True, default='', max_length=255)),
                ('value', models.CharField(blank=True, db_index=True, default='', max_length=255)),
                ('metadata', models.TextField(blank=True, default='', help_text='JSON Object')),
                ('type', models.CharField(blank=True, default='', max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(blank=True, db_index=True, default='', help_text='Subject for identity token', max_length=64)),
                ('nickname', models.CharField(blank=True, default='', help_text='Nickname, alias, or other names used.', max_length=255)),
                ('email_verified', models.BooleanField(blank=True, default=False)),
                ('phone_verified', models.BooleanField(blank=True, default=False)),
                ('mobile_phone_number', models.CharField(blank=True, default='', help_text='US numbers only.', max_length=10)),
                ('sex', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('U', 'Unknown')], default='U', help_text='Sex', max_length=1)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('TMF', 'Transgender Male to Female'), ('TFM', 'Transgender Female to Male'), ('U', 'Unknown')], default='U', help_text='Gender / Gender Identity', max_length=3)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('addresses', models.ManyToManyField(blank=True, to='accounts.Address')),
                ('ind_identifiers', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.IndividualIdentifier')),
                ('org_identifiers', models.ManyToManyField(blank=True, to='accounts.OrganizationIdentifier')),
                ('organizations', models.ManyToManyField(blank=True, to='accounts.Organization')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ValidPasswordResetKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reset_password_key', models.CharField(blank=True, max_length=50)),
                ('expires', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='organization',
            name='identifiers',
            field=models.ManyToManyField(blank=True, to='accounts.OrganizationIdentifier'),
        ),
        migrations.AddField(
            model_name='organization',
            name='point_of_contact',
            field=models.ForeignKey(on_delete='PROTECT', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='address',
            name='ind_identifiers',
            field=models.ManyToManyField(blank=True, to='accounts.IndividualIdentifier'),
        ),
        migrations.AddField(
            model_name='address',
            name='org_identifiers',
            field=models.ManyToManyField(blank=True, to='accounts.OrganizationIdentifier'),
        ),
        migrations.AlterUniqueTogether(
            name='organizationaffiliationrequest',
            unique_together={('user', 'organization')},
        ),
    ]

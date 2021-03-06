# Generated by Django 2.1.1 on 2018-12-06 18:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='IdentityAssuranceLevelDocumentation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identity_proofing_mode', models.CharField(choices=[('R', 'Remote'), ('I', 'In-Person'), ('', 'None')], default='', max_length=1)),
                ('action', models.CharField(choices=[('', 'No Action (Detail Update)'), ('1-TO-2', 'Verify Identity: Change the Identity assurance Level from 1 to 2'), ('2-TO-1', 'Administrative downgrade: Change the Identity Assurance Level (IAL) from 2 to 1 from IAL 2 to 1.')], default='', max_length=6)),
                ('evidence', models.CharField(blank=True, choices=[('', 'None'), ('ONE-SUPERIOR-OR-STRONG+', 'One Superior or Strong+ pieces of identity evidence'), ('ONE-STRONG-TWO-FAIR', 'One Strong and Two Fair pieces of identity evidence'), ('TWO-STRONG', 'Two Pieces of Strong identity evidence'), ('TRUSTED-REFEREE-VOUCH', 'I am a Trusted Referee Vouching for this person'), ('KBA', 'Knowledged-Based Identity Verification')], default='', max_length=24)),
                ('id_verify_description', models.TextField(blank=True, default='', help_text="Describe the evidence given to assure this person's\n                                                identity has been verified.")),
                ('id_assurance_downgrade_description', models.TextField(blank=True, default='', help_text='Complete this description when downgrading the ID assurance level.')),
                ('metadata', models.TextField(blank=True, default='{"subject_user":null, "history":[]}', help_text='JSON Object')),
                ('type', models.CharField(blank=True, default='', max_length=16)),
                ('expires_at', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('subject_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subject_user', to=settings.AUTH_USER_MODEL)),
                ('verifying_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='verifying_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('can_change_level', 'Can change identity assurance level'),),
            },
        ),
    ]

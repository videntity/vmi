# Generated by Django 2.1.5 on 2019-05-22 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_auto_20190501_1925'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='agree_privacy_policy',
            field=models.CharField(blank=True, default='', help_text='Do you agree to the privacy policy?', max_length=64),
        ),
        migrations.AddField(
            model_name='organization',
            name='agree_tos',
            field=models.CharField(blank=True, default='', help_text='Do you agree to the terms and conditions?', max_length=64),
        ),
        migrations.AddField(
            model_name='organization',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='picture',
            field=models.ImageField(default='organization-logo/None/no-img.jpg', upload_to='organization-logo/'),
        ),
        migrations.AddField(
            model_name='organization',
            name='subject',
            field=models.CharField(blank=True, db_index=True, default='397299376997234', help_text='Subject ID', max_length=64),
        ),
        migrations.AddField(
            model_name='organization',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]

# Generated by Django 5.1.1 on 2024-11-10 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robot', '0002_team_group_name_alter_team_sbd'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to='competitions/videos/'),
        ),
    ]
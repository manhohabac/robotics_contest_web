# Generated by Django 5.1.1 on 2024-09-23 11:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robot', '0006_remove_kit_images_kitimage_kit'),
    ]

    operations = [
        migrations.AddField(
            model_name='kit',
            name='main_image',
            field=models.ImageField(blank=True, null=True, upload_to='kits/'),
        ),
        migrations.CreateModel(
            name='KitDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='kit_details/')),
                ('kit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='details', to='robot.kit')),
            ],
        ),
        migrations.DeleteModel(
            name='KitImage',
        ),
    ]
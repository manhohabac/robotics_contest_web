# Generated by Django 5.1.1 on 2024-09-24 03:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robot', '0009_alter_kit_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='KitImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='kits/images/', verbose_name='Hình ảnh chi tiết')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('kit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='robot.kit')),
            ],
        ),
    ]
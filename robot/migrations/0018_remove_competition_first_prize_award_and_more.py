# Generated by Django 5.1.1 on 2024-10-29 01:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robot', '0017_competition_first_prize_award_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='competition',
            name='first_prize_award',
        ),
        migrations.RemoveField(
            model_name='competition',
            name='potential_award',
        ),
        migrations.RemoveField(
            model_name='competition',
            name='second_prize_award',
        ),
        migrations.RemoveField(
            model_name='competition',
            name='third_prize_award',
        ),
        migrations.AlterField(
            model_name='competition',
            name='first_prize_points',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='competition',
            name='potential_points',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='competition',
            name='second_prize_points',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='competition',
            name='third_prize_points',
            field=models.IntegerField(default=0),
        ),
    ]
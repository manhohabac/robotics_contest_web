# Generated by Django 5.1.1 on 2024-11-09 14:27

import datetime
import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import robot.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('registration_start_date', models.DateField(default=datetime.date(2024, 1, 1))),
                ('registration_end_date', models.DateField(default=datetime.date(2024, 12, 31))),
                ('is_active', models.BooleanField(default=True)),
                ('rules', models.TextField(blank=True, null=True)),
                ('max_participants', models.IntegerField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='competition_images/')),
                ('participants_target', models.CharField(blank=True, max_length=255, null=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('first_prize_points', models.IntegerField(default=0)),
                ('second_prize_points', models.IntegerField(default=0)),
                ('third_prize_points', models.IntegerField(default=0)),
                ('potential_points', models.IntegerField(default=0)),
                ('groups', models.JSONField(blank=True, default=list)),
                ('rounds', models.JSONField(blank=True, default=list)),
            ],
        ),
        migrations.CreateModel(
            name='Kit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Tên bộ kit')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Mô tả')),
                ('image', models.ImageField(blank=True, null=True, upload_to='kits/', verbose_name='Hình ảnh đính kèm')),
                ('price', models.PositiveBigIntegerField(blank=True, null=True, verbose_name='Giá bán')),
            ],
        ),
        migrations.CreateModel(
            name='Sponsor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('logo', models.ImageField(blank=True, null=True, upload_to='sponsors/')),
                ('website', models.URLField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('full_name', models.CharField(max_length=255)),
                ('date_of_birth', models.DateField()),
                ('address', models.CharField(max_length=255)),
                ('school_name', models.CharField(blank=True, max_length=255, null=True)),
                ('phone_number', models.CharField(max_length=15)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pictures/')),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('gender', models.CharField(choices=[('nam', 'Nam'), ('nữ', 'Nữ')], default='nam', max_length=10)),
                ('id_number', models.CharField(blank=True, max_length=12, null=True)),
                ('role', models.CharField(choices=[('student', 'Học sinh thi đấu'), ('coach', 'Huấn luyện viên'), ('admin', 'Admin'), ('leader', 'Trưởng Ban Tổ Chức'), ('deputy_leader', 'Phó Ban Tổ Chức'), ('referee', 'Trưởng Ban Trọng Tài')], default='student', max_length=15)),
                ('elo_score', models.FloatField(default=0.0)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('exam_date', models.DateField()),
                ('file', models.FileField(blank=True, null=True, upload_to='exams/')),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exams', to='robot.competition')),
            ],
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(choices=[('Cuộc thi', 'Cuộc thi'), ('Kết quả', 'Kết quả'), ('Bộ thiết bị', 'Bộ thiết bị'), ('Khác', 'Khác')], default='other', max_length=20)),
                ('content', models.TextField()),
                ('rating', models.IntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='feedback_images/', validators=[robot.models.validate_image_size])),
                ('is_viewed', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GuideFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='competition_guides/')),
                ('original_file_name', models.CharField(blank=True, max_length=255, null=True)),
                ('document_name', models.CharField(blank=True, max_length=255, null=True)),
                ('note', models.CharField(blank=True, max_length=255, null=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guide_files', to='robot.competition')),
            ],
        ),
        migrations.CreateModel(
            name='KitImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='kits/images/', verbose_name='Hình ảnh chi tiết')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('kit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='robot.kit')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('notification_type', models.CharField(choices=[('admin', 'Admin'), ('user', 'User')], default='user', max_length=50)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('members', models.CharField(blank=True, max_length=200, null=True)),
                ('coach', models.CharField(blank=True, max_length=255, null=True)),
                ('sbd', models.CharField(blank=True, max_length=6, null=True)),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teams', to='robot.competition')),
            ],
            options={
                'unique_together': {('competition', 'sbd')},
            },
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region', models.CharField(blank=True, max_length=50, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('competition_group', models.CharField(blank=True, max_length=50, null=True)),
                ('team_name', models.CharField(blank=True, max_length=100, null=True)),
                ('team_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('coach_name', models.CharField(blank=True, max_length=100, null=True)),
                ('coach_unit', models.CharField(blank=True, max_length=100, null=True)),
                ('coach_phone', models.CharField(blank=True, max_length=15, null=True)),
                ('member_count', models.IntegerField(default=0)),
                ('guardian_name', models.CharField(blank=True, max_length=100, null=True)),
                ('relationship', models.CharField(blank=True, max_length=50, null=True)),
                ('guardian_phone', models.CharField(blank=True, max_length=15, null=True)),
                ('guardian_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('student_name', models.CharField(blank=True, max_length=100, null=True)),
                ('student_phone', models.CharField(blank=True, max_length=15, null=True)),
                ('student_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('student_class', models.CharField(blank=True, max_length=50, null=True)),
                ('birth_year', models.IntegerField(blank=True, default=2010, null=True)),
                ('gender', models.CharField(blank=True, choices=[('Nam', 'Nam'), ('Nữ', 'Nữ')], max_length=10, null=True)),
                ('ethnicity', models.CharField(blank=True, max_length=50, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('student_photo', models.ImageField(blank=True, null=True, upload_to='photos/')),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(blank=True, max_length=50, null=True)),
                ('registration_code', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('is_cancelled', models.BooleanField(default=False)),
                ('competition', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='robot.competition')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to=settings.AUTH_USER_MODEL)),
                ('team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='robot.team')),
            ],
        ),
        migrations.CreateModel(
            name='CompetitionResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_name', models.CharField(blank=True, max_length=255, null=True)),
                ('round_name', models.CharField(blank=True, max_length=255, null=True)),
                ('score', models.JSONField(default=list)),
                ('ranking_score', models.FloatField(blank=True, null=True)),
                ('prize_points', models.IntegerField(default=0)),
                ('result_date', models.DateTimeField(auto_now_add=True)),
                ('competition', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='results', to='robot.competition')),
                ('team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='competition_results', to='robot.team')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, null=True)),
                ('interests', models.TextField(blank=True, null=True)),
                ('social_links', models.TextField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

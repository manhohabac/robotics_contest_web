import os
from datetime import date

import unicodedata
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
from .utils import generate_unique_code


class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField(blank=False, null=False)
    address = models.CharField(max_length=255)
    school_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=False, null=False)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    gender = models.CharField(
        max_length=10,
        choices=[('nam', 'Nam'), ('nữ', 'Nữ')],
        default='nam'
    )
    id_number = models.CharField(max_length=12, blank=True, null=True)

    ROLE_CHOICES = [
        ('student', 'Học sinh thi đấu'),
        ('coach', 'Huấn luyện viên'),
        ('admin', 'Admin'),
        ('leader', 'Trưởng Ban Tổ Chức'),
        ('deputy_leader', 'Phó Ban Tổ Chức'),
        ('referee', 'Trưởng Ban Trọng Tài'),
    ]
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='student')

    elo_score = models.FloatField(default=0.0)

    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.full_name


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)  # Thông tin giới thiệu
    interests = models.TextField(blank=True, null=True)  # Sở thích
    social_links = models.TextField(blank=True, null=True)  # Liên kết mạng xã hội

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Competition(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    registration_start_date = models.DateField(default=date(2024, 1, 1))
    registration_end_date = models.DateField(default=date(2024, 12, 31))
    is_active = models.BooleanField(default=True)
    rules = models.TextField(blank=True, null=True)
    max_participants = models.IntegerField(null=True, blank=True)
    image = models.ImageField(upload_to='competition_images/', null=True, blank=True)
    video = models.FileField(upload_to='competitions/videos/', null=True, blank=True)
    participants_target = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    first_prize_points = models.IntegerField(default=0)
    second_prize_points = models.IntegerField(default=0)
    third_prize_points = models.IntegerField(default=0)
    potential_points = models.IntegerField(default=0)
    groups = models.JSONField(default=list, blank=True)
    rounds = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=255)
    members = models.CharField(max_length=200, null=True, blank=True)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='teams')
    group_name = models.CharField(max_length=255, null=True, blank=True)
    coach = models.CharField(max_length=255, null=True, blank=True)
    sbd = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        unique_together = ('competition', 'sbd')  # Đảm bảo SBD duy nhất trong từng cuộc thi

    def save(self, *args, **kwargs):
        if not self.sbd:  # Tạo SBD nếu chưa có
            self.sbd = self.generate_sbd()
        super().save(*args, **kwargs)

    def generate_sbd(self):
        count = Team.objects.filter(competition=self.competition).count()
        return f"BG{str(count + 1).zfill(4)}"  # Định dạng BGxxxx với 4 chữ số

    def __str__(self):
        return self.name


class Registration(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='registrations')  # Thêm trường liên kết với người dùng
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='registrations', null=True, blank=True)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name="registrations", null=True, blank=True)
    region = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    competition_group = models.CharField(max_length=50, null=True, blank=True)
    team_name = models.CharField(max_length=100, null=True, blank=True)
    team_email = models.EmailField(null=True, blank=True)
    coach_name = models.CharField(max_length=100, null=True, blank=True)
    coach_unit = models.CharField(max_length=100, null=True, blank=True)
    coach_phone = models.CharField(max_length=15, null=True, blank=True)
    member_count = models.IntegerField(default=0)
    guardian_name = models.CharField(max_length=100, null=True, blank=True)
    relationship = models.CharField(max_length=50, null=True, blank=True)
    guardian_phone = models.CharField(max_length=15, null=True, blank=True)
    guardian_email = models.EmailField(null=True, blank=True)
    student_name = models.CharField(max_length=100, null=True, blank=True)
    student_phone = models.CharField(max_length=15, null=True, blank=True)
    student_email = models.EmailField(null=True, blank=True)
    student_class = models.CharField(max_length=50, null=True, blank=True)
    birth_year = models.IntegerField(default=2010, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Nam', 'Nam'), ('Nữ', 'Nữ')], null=True, blank=True)
    ethnicity = models.CharField(max_length=50, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    student_photo = models.ImageField(upload_to='photos/', null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    registration_code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    is_cancelled = models.BooleanField(default=False)  # Trạng thái đăng ký (hủy hay không)

    def save(self, *args, **kwargs):
        if not self.registration_code:
            self.registration_code = generate_unique_code()  # Hàm để tạo mã đăng ký duy nhất

        super().save(*args, **kwargs)

        # Kiểm tra nếu có sự thay đổi tên đội
        if self.team and self.team.name != self.team_name:
            self.team.name = self.team_name  # Cập nhật tên đội trong bảng Team
            self.team.save()  # Lưu lại thay đổi vào bảng Team


class CompetitionResult(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE,
                                    related_name='results', null=True, blank=True)

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='competition_results', null=True, blank=True)

    # Thêm trường lưu tên bảng đấu và tên vòng thi
    group_name = models.CharField(max_length=255, null=True, blank=True)  # Tên bảng đấu
    round_name = models.CharField(max_length=255, null=True, blank=True)  # Tên vòng thi

    # Điểm của đội thi trong từng lượt đấu
    score = models.JSONField(default=list)  # Lưu trữ điểm từng lượt đấu, dưới dạng danh sách

    # Điểm xếp hạng cuối cùng của đội trong vòng thi
    ranking_score = models.FloatField(null=True, blank=True)

    prize_points = models.IntegerField(default=0)  # Điểm thưởng nếu đội thi giành giải

    result_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.team.name} - {self.competition.name} - Rank {self.ranking_score}"


class GuideFile(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='guide_files')
    file = models.FileField(upload_to='competition_guides/')
    original_file_name = models.CharField(max_length=255, blank=True, null=True)
    document_name = models.CharField(max_length=255, blank=True, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)  # Trường ghi chú
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Thời gian tải lên
    is_confirmed = models.BooleanField(default=False)  # Trạng thái xác nhận

    def save(self, *args, **kwargs):
        # Lưu tên gốc nếu file mới được tải lên
        if self.file and not self.original_file_name:
            self.original_file_name = os.path.basename(self.file.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.original_file_name} - {self.competition.name}"


class Exam(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='exams')
    title = models.CharField(max_length=255)
    description = models.TextField()
    exam_date = models.DateField()
    file = models.FileField(upload_to='exams/', null=True, blank=True)  # File đính kèm (PDF, DOCX, v.v.)

    def __str__(self):
        return f"{self.title} - {self.competition.name}"


class Sponsor(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    logo = models.ImageField(upload_to='sponsors/', null=True, blank=True)
    website = models.URLField(blank=True, null=True)  # Liên kết website

    def __str__(self):
        return self.name


def validate_image_size(image):
    max_size = 2 * 1024 * 1024  # 2 MB
    if image.size > max_size:
        raise ValidationError("Kích thước ảnh không được vượt quá 2MB.")


class Feedback(models.Model):
    SUBJECT_CHOICES = [
        ('Cuộc thi', 'Cuộc thi'),
        ('Kết quả', 'Kết quả'),
        ('Bộ thiết bị', 'Bộ thiết bị'),
        ('Khác', 'Khác'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='feedbacks')
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default='other')
    content = models.TextField(null=False, blank=False)
    rating = models.IntegerField(default=1, null=False, blank=False)  # Giá trị từ 1 đến 5
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='feedback_images/', null=True, blank=True, validators=[validate_image_size])
    is_viewed = models.BooleanField(default=False)  # Trường xác nhận đã xem

    def __str__(self):
        return f"Feedback by {self.user.username} - {self.subject}"


class Kit(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Tên bộ kit")
    description = models.TextField(null=True, blank=True, verbose_name="Mô tả")
    image = models.ImageField(upload_to='kits/', null=True, blank=True, verbose_name="Hình ảnh đính kèm")
    price = models.PositiveBigIntegerField(null=True, blank=True, verbose_name="Giá bán")

    def __str__(self):
        return self.name or "Bộ kit không tên"


class KitImage(models.Model):
    kit = models.ForeignKey(Kit, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='kits/images/', verbose_name="Hình ảnh chi tiết")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Hình ảnh cho {self.kit.name}"


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=50, choices=[('admin', 'Admin'), ('user', 'User')], default='user')

    def __str__(self):
        return self.title

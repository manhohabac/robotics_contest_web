from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=255)
    school_name = models.CharField(max_length=255)
    has_robot_competition_experience = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    gender = models.CharField(
        max_length=10,
        choices=[('nam', 'Nam'), ('nữ', 'Nữ'), ('khác', 'Khác')],
        default='khác'
    )
    id_number = models.CharField(max_length=12, unique=True, null=True, blank=True)

    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.full_name


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)  # Thông tin giới thiệu
    interests = models.TextField(blank=True, null=True)  # Sở thích
    social_links = models.TextField(blank=True, null=True)  # Liên kết mạng xã hội
    is_competitor = models.BooleanField(default=False)  # Có phải là thí sinh không

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
    start_date = models.DateField()
    end_date = models.DateField()
    registration_deadline = models.DateField()  # Hạn đăng ký
    is_active = models.BooleanField(default=True)  # Cuộc thi có đang diễn ra hay không
    rules = models.TextField(blank=True, null=True)  # Quy định cuộc thi
    max_participants = models.IntegerField(null=True, blank=True)  # Số lượng thí sinh tối đa
    image = models.ImageField(upload_to='competition_images/', null=True, blank=True)  # Hình ảnh cuộc thi

    def __str__(self):
        return self.name


class Registration(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='registrations')
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='registrations')
    registration_date = models.DateTimeField(auto_now_add=True)
    is_cancelled = models.BooleanField(default=False)  # Trạng thái đăng ký (hủy hay không)

    def __str__(self):
        return f"{self.user.username} - {self.competition.name}"


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


class Feedback(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='feedbacks')
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='feedbacks')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user.username} on {self.competition.name}"


class Team(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(CustomUser, related_name='teams')
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='teams')
    coach = models.CharField(max_length=255, blank=True, null=True)  # Huấn luyện viên

    def __str__(self):
        return self.name


class CompetitionResult(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='results')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='results')
    position = models.IntegerField()  # Vị trí đạt được (1: Quán quân, 2: Á quân, ...)
    score = models.FloatField()  # Điểm số

    def __str__(self):
        return f"{self.team.name} - {self.competition.name} - Position: {self.position}"


class Kit(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='kits', null=True, blank=True)
    image = models.ImageField(upload_to='kits/', null=True, blank=True)

    def __str__(self):
        return self.name


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=50, choices=[('admin', 'Admin'), ('user', 'User')], default='user')

    def __str__(self):
        return self.title


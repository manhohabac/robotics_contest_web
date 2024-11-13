from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser  # Import CustomUser model


@receiver(post_save, sender=CustomUser)
def make_first_user_admin(sender, instance, created, **kwargs):
    if created:  # Chỉ xử lý khi tạo mới người dùng
        # Kiểm tra xem có phải người dùng đầu tiên không
        if CustomUser.objects.count() == 1:  # Nếu số lượng người dùng = 1
            # Cập nhật quyền admin cho người dùng đầu tiên
            instance.role = 'admin'  # Cấp quyền admin cho người dùng đầu tiên
            instance.is_staff = True  # Cấp quyền staff (admin) cho phép vào trang quản trị Django
            instance.is_superuser = True  # Cấp quyền superuser để có quyền truy cập cao nhất
            instance.save()

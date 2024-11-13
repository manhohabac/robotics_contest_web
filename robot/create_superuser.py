# create_superuser.py

from django.contrib.auth import get_user_model
from django.core.management import call_command


def create_superuser():
    User = get_user_model()

    # Kiểm tra xem tài khoản admin đã tồn tại chưa
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@example.com", "password123")
        print("Superuser created")
    else:
        print("Superuser already exists")


# Tạo superuser khi chạy script
create_superuser()

from django.apps import AppConfig


class RobotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'robot'

    def ready(self):
        import robot.signals  # Đảm bảo rằng signals.py được nạp khi ứng dụng khởi động
import uuid
import secrets
import string


def generate_unique_code():
    # Tạo một mã đăng ký duy nhất bằng cách sử dụng UUID
    return uuid.uuid4().hex[:8]  # Ví dụ mã gồm 8 ký tự, bạn có thể thay đổi độ dài nếu cần


def generate_random_code(length=10):
    # Kết hợp các chữ cái hoa, chữ cái thường, số và ký tự đặc biệt
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for i in range(length))
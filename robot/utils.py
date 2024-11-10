import uuid


def generate_unique_code():
    # Tạo một mã đăng ký duy nhất bằng cách sử dụng UUID
    return uuid.uuid4().hex[:8]  # Ví dụ mã gồm 8 ký tự, bạn có thể thay đổi độ dài nếu cần


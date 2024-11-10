import os

# Đường dẫn đến thư mục dự án của bạn
project_path = '/Users/v2113269/Documents/GitHub/robot_web'

# Các phần mở rộng file bạn muốn đếm
extensions = {
    '.py': 'Python',
    '.html': 'HTML',
    '.css': 'CSS',
    '.js': 'JavaScript',
}

# Tạo một dictionary để lưu số dòng của từng loại file
line_counts = {ext: 0 for ext in extensions.values()}

# Danh sách thư mục cần bỏ qua (như venv, env, .git)
exclude_dirs = {'venv', 'env', '.git', '__pycache__'}


# Hàm đếm số dòng của một file
def count_lines_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return sum(1 for line in file if line.strip())


# Duyệt qua các thư mục và file trong dự án
for root, dirs, files in os.walk(project_path):
    # Bỏ qua các thư mục trong exclude_dirs
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    for file in files:
        file_ext = os.path.splitext(file)[1]
        if file_ext in extensions:
            file_path = os.path.join(root, file)
            line_counts[extensions[file_ext]] += count_lines_in_file(file_path)

# In kết quả
for ext, count in line_counts.items():
    print(f"{ext}: {count} lines")


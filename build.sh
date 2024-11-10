#!/bin/bash

# Tạo môi trường ảo (virtual environment) và kích hoạt nó
python -m venv venv
source venv/bin/activate  # Kích hoạt môi trường ảo trên OnRender (Linux)

# Loại bỏ kí tự \r trong requirements.txt
sed -i 's/\r//' requirements.txt

# Cài đặt các phụ thuộc từ requirements.txt
pip install -r requirements.txt

# Chạy migrations
python manage.py migrate

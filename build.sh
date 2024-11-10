#!/bin/bash

# Đảm bảo các kí tự dòng mới là Unix-style (LF)
dos2unix requirements.txt  # Nếu có lệnh dos2unix, hãy chạy nó trên file requirements.txt

# Cài đặt các phụ thuộc từ requirements.txt
pip install -r requirements.txt

# Chạy migrations
python manage.py migrate

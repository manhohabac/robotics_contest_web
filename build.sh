#!/bin/bash

# Cài đặt các phụ thuộc từ requirements.txt
pip install -r requirements.txt

# Chạy migrations để cập nhật cơ sở dữ liệu
python manage.py migrate

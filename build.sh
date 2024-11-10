#!/bin/bash
set -o igncr  # Ignore carriage return

# Cài đặt các phụ thuộc từ requirements.txt
pip install -r requirements.txt

# Chạy migrations
python manage.py migrate

#!/usr/bin/env python
"""
创建人脸管理数据库迁移
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.management import call_command

print("🔨 正在创建人脸管理模型的数据库迁移...")
call_command('makemigrations', 'ops', '--name', 'add_face_record')
print("✅ 迁移文件创建完成！")
print("\n📝 下一步：")
print("1. 应用迁移: python manage.py migrate")
print("2. 或在服务器上执行: cd /root/Dog2/admin/backend && python manage.py migrate")


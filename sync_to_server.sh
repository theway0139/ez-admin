#!/bin/bash
# 同步修改的文件到服务器

SERVER="root@172.16.160.100"
REMOTE_PATH="/root/Dog2/admin/backend"

echo "📦 开始同步文件到服务器..."

# 同步urls.py
echo "1️⃣ 同步 urls.py..."
scp backend/backend/urls.py $SERVER:$REMOTE_PATH/backend/

# 同步video_analysis_service.py
echo "2️⃣ 同步 video_analysis_service.py..."
scp backend/ops/video_analysis_service.py $SERVER:$REMOTE_PATH/ops/

echo "✅ 文件同步完成！"
echo ""
echo "📝 接下来在服务器上执行："
echo "  ssh $SERVER"
echo "  cd $REMOTE_PATH"
echo "  # 重启Django服务"
echo "  sudo systemctl restart django"
echo "  # 或者手动重启"
echo "  pkill -f 'python manage.py runserver'"
echo "  nohup python manage.py runserver 0.0.0.0:8000 > django_server.log 2>&1 &"


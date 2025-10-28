#!/bin/bash
# 同步修改的文件到服务器

SERVER="root@172.16.160.100"
BACKEND_PATH="/root/Dog2/admin/backend"
FRONTEND_PATH="/root/Dog2/admin/frontend"

echo "📦 开始同步文件到服务器..."

# 同步后端文件
echo "1️⃣ 同步后端 urls.py..."
scp backend/backend/urls.py $SERVER:$BACKEND_PATH/backend/

echo "2️⃣ 同步 video_analysis_service.py..."
scp backend/ops/video_analysis_service.py $SERVER:$BACKEND_PATH/ops/

# 同步前端文件
echo "3️⃣ 同步前端 FaceManagement.vue..."
scp frontend/src/views/FaceManagement.vue $SERVER:$FRONTEND_PATH/src/views/

echo "4️⃣ 同步前端 router/index.js..."
scp frontend/src/router/index.js $SERVER:$FRONTEND_PATH/src/router/

echo "5️⃣ 同步前端 App.vue..."
scp frontend/src/App.vue $SERVER:$FRONTEND_PATH/src/

echo "✅ 文件同步完成！"
echo ""
echo "📝 接下来在服务器上执行："
echo "  ssh $SERVER"
echo ""
echo "  # 重启Django后端"
echo "  cd $BACKEND_PATH"
echo "  pkill -f 'python manage.py runserver'"
echo "  nohup python manage.py runserver 0.0.0.0:8000 > django_server.log 2>&1 &"
echo ""
echo "  # 重新构建前端"
echo "  cd $FRONTEND_PATH"
echo "  npm run build"


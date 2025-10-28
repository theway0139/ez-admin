#!/bin/bash
# 同步人脸管理功能到服务器并执行数据库迁移

SERVER="172.16.160.100"
SERVER_PATH="/root/Dog2/admin"

echo "======================================"
echo "   同步人脸管理功能到服务器"
echo "======================================"

# 1. 同步后端文件
echo ""
echo "📦 步骤1: 同步后端模型文件..."
rsync -avz backend/ops/models.py root@${SERVER}:${SERVER_PATH}/backend/ops/

echo ""
echo "📦 步骤2: 同步数据库迁移文件..."
rsync -avz backend/ops/migrations/0003_add_face_record.py root@${SERVER}:${SERVER_PATH}/backend/ops/migrations/

echo ""
echo "📦 步骤3: 同步后端API文件..."
rsync -avz backend/ops/api.py root@${SERVER}:${SERVER_PATH}/backend/ops/

echo ""
echo "📦 步骤4: 同步前端人脸管理页面..."
rsync -avz frontend/src/views/FaceManagement.vue root@${SERVER}:${SERVER_PATH}/frontend/src/views/

echo ""
echo "✅ 文件同步完成！"

echo ""
echo "======================================"
echo "   下一步：在服务器上执行"
echo "======================================"
echo ""
echo "1️⃣ 应用数据库迁移:"
echo "   ssh root@${SERVER}"
echo "   cd ${SERVER_PATH}/backend"
echo "   python manage.py migrate"
echo ""
echo "2️⃣ 重启Django后端服务:"
echo "   pkill -f 'python manage.py runserver'"
echo "   nohup python manage.py runserver 0.0.0.0:8003 > django_server.log 2>&1 &"
echo ""
echo "3️⃣ 重新构建前端:"
echo "   cd ${SERVER_PATH}/frontend"
echo "   npm run build"
echo ""
echo "4️⃣ 测试人脸管理页面:"
echo "   打开浏览器访问: http://172.16.160.100:端口号/faces"
echo ""
echo "======================================"


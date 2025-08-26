@echo off
echo Running backend...

REM 激活conda环境
echo Activating conda environment py312...
call conda activate py312

REM 切换到backend目录
echo Changing to backend directory...
cd backend

REM 启动Django开发服务器
echo Starting Django development server...
REM start python manage.py runserver 0.0.0.0:8000
python manage.py runserver 

REM 暂停，防止窗口自动关闭（如果服务器启动后保持运行，可以取消注释下面一行）
REM pause

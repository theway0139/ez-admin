@echo off
echo The command is being executed...

REM 激活conda环境
call conda activate py312

cd frontend

npm run dev

REM 暂停，防止窗口自动关闭（如果pnpm dev不保持运行，可以取消注释下面一行）
REM pause
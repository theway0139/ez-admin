#!/bin/bash

# FFmpeg安装脚本
# 用于视频流转换服务

echo "开始安装FFmpeg..."

# 检查操作系统
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux系统
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y ffmpeg
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        sudo yum install -y epel-release
        sudo yum install -y ffmpeg
    elif command -v dnf &> /dev/null; then
        # Fedora
        sudo dnf install -y ffmpeg
    else
        echo "不支持的Linux发行版"
        exit 1
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS系统
    if command -v brew &> /dev/null; then
        brew install ffmpeg
    else
        echo "请先安装Homebrew: https://brew.sh/"
        exit 1
    fi
else
    echo "不支持的操作系统: $OSTYPE"
    exit 1
fi

# 验证安装
if command -v ffmpeg &> /dev/null; then
    echo "FFmpeg安装成功!"
    ffmpeg -version | head -n 1
else
    echo "FFmpeg安装失败!"
    exit 1
fi

echo "安装完成!"

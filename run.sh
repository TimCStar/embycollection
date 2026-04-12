#!/bin/bash

# 切换到脚本所在的目录，确保使用相对路径时不出错
cd "$(dirname "$0")"

# 检查虚拟环境是否存在
if [ ! -d ".venv" ]; then
    echo "未找到虚拟环境 '.venv'，正在使用 python3 -m venv 创建..."
    python3 -m venv .venv
    source .venv/bin/activate
    
    if [ -f "requirements.txt" ]; then
        echo "正在安装依赖..."
        pip install -r requirements.txt
    fi
else
    # 激活虚拟环境
    source .venv/bin/activate
fi

# 运行主程序
echo "开始执行 main.py..."
python3 main.py

# 退出虚拟环境 (可选)
deactivate

#!/bin/bash

# 安装 Python 依赖
python3 -m pip install --quiet --no-cache-dir feedparser requests beautifulsoup4 trafilatura lark-oapi openai python-dotenv

# 启动 openclaw gateway
exec openclaw gateway --bind lan --verbose

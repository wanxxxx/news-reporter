#!/bin/bash

set -e

APP_DIR="/app/news_reporter"
GIT_REPO_SSH="git@github.com:wanxxxx/news-reporter.git"
GIT_REPO_HTTPS="https://github.com/wanxxxx/news-reporter.git"

echo "=========================================="
echo "🚀 News Reporter 容器启动脚本"
echo "=========================================="

# 配置 SSH 密钥权限
if [ -f "/tmp/host_ssh_key" ]; then
    echo "🔑 配置 SSH 密钥..."
    mkdir -p /root/.ssh
    chmod 700 /root/.ssh
    cp /tmp/host_ssh_key /root/.ssh/id_ed25519
    chmod 600 /root/.ssh/id_ed25519
    ssh-keyscan github.com >> /root/.ssh/known_hosts 2>/dev/null
    chmod 644 /root/.ssh/known_hosts
    echo "✅ SSH 密钥配置完成"
    USE_SSH=true
else
    echo "⚠️ 未找到 SSH 密钥，将使用 HTTPS 方式克隆"
    USE_SSH=false
fi

# 检查是否已经克隆过仓库
if [ -d "$APP_DIR/.git" ]; then
    echo "📦 仓库已存在，正在拉取最新代码..."
    cd "$APP_DIR"
    git pull origin main || echo "⚠️ Git pull 失败，使用现有代码"
else
    echo "📦 克隆仓库..."
    if [ "$USE_SSH" = true ]; then
        echo "🔗 使用 SSH 方式克隆..."
        git clone "$GIT_REPO_SSH" "$APP_DIR" || {
            echo "⚠️ SSH 克隆失败，尝试 HTTPS..."
            git clone "$GIT_REPO_HTTPS" "$APP_DIR"
        }
    else
        echo "🔗 使用 HTTPS 方式克隆..."
        git clone "$GIT_REPO_HTTPS" "$APP_DIR"
    fi
fi

cd "$APP_DIR"

# 安装 pip（如果不存在）
if ! python3 -m pip --version > /dev/null 2>&1; then
    echo "📦 安装 pip..."
    apt-get update -qq && apt-get install -y -qq python3-pip > /dev/null
fi

# 安装 Python 依赖
echo "📦 安装 Python 依赖..."
python3 -m pip install --quiet --no-cache-dir --break-system-packages \
    feedparser \
    requests \
    beautifulsoup4 \
    trafilatura \
    lxml_html_clean \
    lark-oapi \
    openai \
    python-dotenv

echo "✅ 依赖安装完成"

# 启动 openclaw gateway
echo "🚀 启动 openclaw gateway..."
exec openclaw gateway --bind lan --verbose

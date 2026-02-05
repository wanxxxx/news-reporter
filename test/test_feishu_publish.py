import os
import sys

# 添加父目录到Python路径，以便导入newsletter_tools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from dotenv import load_dotenv
from newsletter_tools import publish_feishu_report

load_dotenv()

def main():
    print("=" * 80)
    print("飞书发布测试")
    print("=" * 80)
    
    # 配置飞书环境变量（请替换为你的实际配置）
    print("\n配置飞书环境变量...")
    
    # 检查环境变量是否已配置
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    
    if not app_id or not app_secret:
        print("⚠️  检测到飞书环境变量未配置，请设置以下环境变量：")
        print("   FEISHU_APP_ID")
        print("   FEISHU_APP_SECRET")
        print("\n或者在下方直接输入配置：")
        app_id = input("FEISHU_APP_ID: ").strip()
        app_secret = input("FEISHU_APP_SECRET: ").strip()
        
        if app_id and app_secret:
            os.environ["FEISHU_APP_ID"] = app_id
            os.environ["FEISHU_APP_SECRET"] = app_secret
            print("✅ 环境变量已设置")
        else:
            print("❌ 未提供飞书配置，测试取消")
            return
    else:
        print(f"✅ 已配置 FEISHU_APP_ID: {app_id[:10]}...")
        print(f"✅ 已配置 FEISHU_APP_SECRET: {app_secret[:10]}...")
    
    # 读取 Markdown 文件
    print("\n" + "-" * 80)
    print("读取 Markdown 文件...")
    markdown_file = os.path.join('test', 'data', 'test_feishu_publish_data.md')
    
    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        print(f"✅ 成功读取文件: {markdown_file}")
        print(f"   文件大小: {len(markdown_content)} 字符")
    except FileNotFoundError:
        print(f"❌ 文件不存在: {markdown_file}")
        return
    
    # 发布到飞书
    print("\n" + "-" * 80)
    print("准备发布到飞书...")
    print("-" * 80)
    
    report_title = "户外运动周报"
    
    # 从环境变量获取 chat_id
    chat_id = os.getenv("FEISHU_CHAT_ID")
    
    if chat_id:
        print(f"✅ 已配置 FEISHU_CHAT_ID: {chat_id}")
    else:
        print("⚠️ 未配置 FEISHU_CHAT_ID，将只创建文档，不发送到群聊")
    
    result = publish_feishu_report(report_title, markdown_content, chat_id)
    
    print("\n" + "=" * 80)
    if result:
        print(f"✅ 发布成功！文档链接: {result}")
    else:
        print("❌ 发布失败，请检查错误信息")
    print("=" * 80)

if __name__ == "__main__":
    main()

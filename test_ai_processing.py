import os

# 1. 强制移除代理环境变量 (在 import requests/openai 之前执行)
os.environ.pop(
"HTTP_PROXY", None
)
os.environ.pop(
"HTTPS_PROXY", None
)
os.environ.pop(
"ALL_PROXY", None
)

import json
from datetime import datetime
from dotenv import load_dotenv
from newsletter_tools import process_articles_with_ai

load_dotenv()

def main():
    print("=" * 80)
    print("AI 处理测试脚本")
    print("=" * 80)

    print("\n加载环境变量...")
    required_vars = ['LLM_API_KEY', 'LLM_BASE_URL', 'LLM_MODEL']
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"{var}: {value[:20]}...")
        else:
            print(f"{var}: 未设置")
            raise ValueError(f"环境变量 {var} 未设置，请检查 .env 文件")

    print("\n" + "-" * 80)
    print("读取测试数据...")
    test_file = 'newsletter_tools_output_2026-02-01_to_2026-02-01.json'

    with open(test_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    print(f"成功读取 {len(articles)} 篇文章")

    print("\n" + "-" * 80)
    print("开始 AI 处理...")
    print("-" * 80)

    markdown_text = process_articles_with_ai(articles)

    print("\n" + "=" * 80)
    print("AI 处理完成！")
    print("=" * 80)
    print(f"\n生成 {len(articles)} 篇文章的摘要")

    output_file = 'newsletter_ai_output.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_text)

    print(f"\nMarkdown 结果已保存到: {output_file}")

if __name__ == "__main__":
    main()

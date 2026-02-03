import sys
import os
import json
from datetime import datetime, timedelta
from newsletter_tools import fetch_weekly_outdoor_articles

def main():
    # 设置日期为 2026 年 2 月 1 日
    start_date = datetime(2026, 2, 1)
    end_date = datetime(2026, 2, 1)
    
    print(f"开始爬取 2026 年 2 月 1 日的户外新闻...")
    print(f"起始日期: {start_date}")
    print(f"结束日期: {end_date}")
    print("-" * 80)
    
    # 调用爬取函数
    articles = fetch_weekly_outdoor_articles(start_date, end_date)
    
    print(f"\n爬取完成！共获取 {len(articles)} 篇文章\n")
    print("=" * 80)
    
    # 显示爬取结果
    for i, article in enumerate(articles, 1):
        print(f"\n【文章 {i}】")
        print(f"网站: {article['site']}")
        print(f"标题: {article['title']}")
        print(f"链接: {article['url']}")
        print(f"内容长度: {len(article['content_text'])} 字符")
        print(f"内容预览: {article['content_text'][:200]}...")
        print("-" * 80)
    
    # 创建保存目录
    output_dir = "outdoor_sports_news__auto_reporter"
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    time_range = f"2026-02-01_to_2026-02-01"
    output_file = os.path.join(output_dir, f"newsletter_tools_output_{time_range}.json")
    
    # 保存结果到文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到: {output_file}")
    print(f"共保存 {len(articles)} 篇文章")
    print("\n执行完成！")

if __name__ == "__main__":
    main()

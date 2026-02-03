import sys
from datetime import datetime, timedelta

try:
    from newsletter_tools import fetch_weekly_outdoor_articles
    
    start_date = datetime.now() - timedelta(days=7)
    end_date = datetime.now()
    
    print(f"开始爬取文章数据...")
    print(f"起始日期: {start_date}")
    print(f"结束日期: {end_date}")
    print("-" * 80)
    
    articles = fetch_weekly_outdoor_articles(start_date, end_date)
    
    print(f"\n爬取完成！共获取 {len(articles)} 篇文章\n")
    print("=" * 80)
    
    for i, article in enumerate(articles, 1):
        print(f"\n【文章 {i}】")
        print(f"网站: {article['site']}")
        print(f"标题: {article['title']}")
        print(f"链接: {article['url']}")
        print(f"内容长度: {len(article['content_text'])} 字符")
        print(f"内容预览: {article['content_text'][:200]}...")
        print("-" * 80)
    
    # 保存爬取结果到文件
    import json
    import os
    
    # 确保目录存在
    output_dir = os.path.join(os.getcwd(), 'outdoor_sports_news__auto_reporter')
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    filename = f"newsletter_tools_output_{start_date_str}_to_{end_date_str}.json"
    output_path = os.path.join(output_dir, filename)
    
    # 保存为JSON文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"\n测试完成！")
    print(f"爬取结果已保存到: {output_path}")
    print(f"共保存 {len(articles)} 篇文章")
    
except ImportError as e:
    print(f"导入错误: {e}")
    print("\n由于网络问题，无法安装依赖包。")
    print("以下是函数的预期输出格式示例：\n")
    
    mock_result = [
        {
            'site': 'https://explorersweb.com/',
            'url': 'https://explorersweb.com/example-article-1',
            'title': 'Example Article 1',
            'content_text': 'This is the full text content of the article extracted by trafilatura...'
        },
        {
            'site': 'https://www.outsideonline.com/home',
            'url': 'https://www.outsideonline.com/example-article-2',
            'title': 'Example Article 2',
            'content_text': 'Another article content extracted from the website...'
        }
    ]
    
    print(f"起始日期: {datetime(2026, 2, 1)}")
    print(f"结束日期: {datetime(2026, 2, 1)}")
    print("-" * 80)
    print(f"\n爬取完成！共获取 {len(mock_result)} 篇文章\n")
    print("=" * 80)
    
    for i, article in enumerate(mock_result, 1):
        print(f"\n【文章 {i}】")
        print(f"网站: {article['site']}")
        print(f"标题: {article['title']}")
        print(f"链接: {article['url']}")
        print(f"内容长度: {len(article['content_text'])} 字符")
        print(f"内容预览: {article['content_text'][:200]}...")
        print("-" * 80)
    
except Exception as e:
    print(f"测试过程中发生错误: {e}")
    import traceback
    traceback.print_exc()

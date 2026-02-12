"""
户外运动新闻汇总生成模块

本模块是户外运动新闻自动化系统的具体实现实例，负责协调文章抓取、AI分析和飞书发布的完整流程。

核心功能:
    1. run_outdoor_news_summary_task: 运行完整的户外运动新闻汇总生成和发布任务

工作流程:
    RSS抓取(fetch_articles) → AI分析(process_articles_with_ai) → 飞书发布(publish_feishu_report)

环境变量:
    FEISHU_CHAT_ID: 飞书群组ID，用于推送消息
    FEISHU_APP_ID: 飞书应用ID
    FEISHU_APP_SECRET: 飞书应用密钥
    LLM_API_KEY: AI模型API密钥
    LLM_BASE_URL: AI模型API基础URL
    LLM_MODEL: AI模型名称
    TARGET_SITES: 目标网站列表，用逗号分隔
    RSS_FEEDS: RSS源映射，格式：site1_url=rss1_url,site2_url=rss2_url
    FEISHU_COLLABORATOR_OPENIDS: 飞书协作者openid列表，用逗号分隔
"""
import os
import argparse
import logging
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from run_newsletter import run_newsletter_task
from newsletter_tools import NewsConfig

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent / "prompts"

DEFAULT_DAYS_BACK = 14


def load_prompt_from_file(filename: str) -> str:
    """
    从 Markdown 文件加载 prompt 内容
    
    Args:
        filename: prompt 文件名（相对于 prompts 目录）
    
    Returns:
        str: prompt 内容
    
    Raises:
        FileNotFoundError: 文件不存在
        IOError: 文件读取失败
    """
    file_path = PROMPTS_DIR / filename
    
    if not file_path.exists():
        raise FileNotFoundError(f"Prompt 文件不存在: {file_path}")
    
    if not file_path.is_file():
        raise IOError(f"路径不是文件: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            raise IOError(f"Prompt 文件为空: {file_path}")
        
        logger.info(f"✅ 成功加载 prompt 文件: {filename}")
        return content
    
    except IOError as e:
        raise IOError(f"读取 prompt 文件失败 {file_path}: {e}")


def get_outdoor_ai_prompt() -> str:
    """获取户外运动 AI prompt"""
    return load_prompt_from_file("outdoor_ai_prompt.md")


def get_outdoor_ai_system_prompt() -> str:
    """获取户外运动 AI system prompt"""
    return load_prompt_from_file("outdoor_ai_system_prompt.md")


def get_outdoor_news_config() -> NewsConfig:
    """
    获取户外运动新闻配置
    
    Returns:
        NewsConfig: 户外运动新闻配置对象
    """
    target_sites = os.getenv('TARGET_SITES', '').split(',') if os.getenv('TARGET_SITES') else []
    target_sites = [site.strip() for site in target_sites if site.strip()]
    
    rss_feeds = {}
    rss_feeds_env = os.getenv('RSS_FEEDS', '')
    if rss_feeds_env:
        for mapping in rss_feeds_env.split(','):
            if '=' in mapping:
                site_url, rss_url = mapping.split('=', 1)
                rss_feeds[site_url.strip()] = rss_url.strip()
    
    feishu_openids = []
    openids_env = os.getenv('FEISHU_COLLABORATOR_OPENIDS', '')
    if openids_env:
        feishu_openids = [oid.strip() for oid in openids_env.split(',') if oid.strip()]
    
    return NewsConfig(
        name="户外运动",
        target_sites=target_sites,
        rss_feeds=rss_feeds,
        ai_prompt=get_outdoor_ai_prompt(),
        ai_system_prompt=get_outdoor_ai_system_prompt(),
        feishu_collaborator_openids=feishu_openids,
        report_title_template="户外运动新闻汇总 ({start_date} 至 {end_date})",
        report_header="# 户外运动新闻汇总\n",
        cache_prefix="outdoor_"
    )


def run_outdoor_news_summary_task(
    chat_id: str = None, 
    days_back: int = None,
    start_date: date = None,
    end_date: date = None
) -> Optional[str]:
    """
    运行完整的户外运动新闻汇总生成和发布任务
    
    支持两种模式：
    1. 按天数回溯：指定 days_back 参数，自动计算日期范围
    2. 指定日期范围：指定 start_date 和 end_date 参数
    
    Args:
        chat_id: 飞书群组ID，为空则尝试从环境变量FEISHU_CHAT_ID读取
        days_back: 回溯天数，与 start_date/end_date 互斥
        start_date: 开始日期，与 days_back 互斥
        end_date: 结束日期，与 days_back 互斥
    
    Returns:
        str: 飞书文档链接
        None: 任务失败时返回None
    
    Raises:
        ValueError: 参数冲突时抛出
    """
    if days_back is not None and (start_date is not None or end_date is not None):
        raise ValueError("days_back 与 start_date/end_date 参数不能同时使用")
    
    config = get_outdoor_news_config()
    
    if days_back is not None:
        return run_newsletter_task(config, chat_id=chat_id, days_back=days_back)
    elif start_date is not None and end_date is not None:
        return run_newsletter_task(config, chat_id=chat_id, start_date=start_date, end_date=end_date)
    else:
        return run_newsletter_task(config, chat_id=chat_id, days_back=DEFAULT_DAYS_BACK)


def parse_date(date_str: str) -> date:
    """
    解析日期字符串
    
    Args:
        date_str: 日期字符串，格式为 YYYY-MM-DD
    
    Returns:
        date: 解析后的日期对象
    
    Raises:
        argparse.ArgumentTypeError: 日期格式无效
    """
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        raise argparse.ArgumentTypeError(f"无效的日期格式: {date_str}，请使用 YYYY-MM-DD 格式")


def main():
    """
    主函数：解析命令行参数并执行相应的任务
    
    支持两种运行模式：
    1. 按天数回溯：python run_outdoor_news_summary.py --days 14
    2. 指定日期范围：python run_outdoor_news_summary.py --start 2024-01-01 --end 2024-01-14
    """
    parser = argparse.ArgumentParser(
        description='户外运动新闻汇总生成和发布工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 汇总过去14天的新闻（默认）
  python run_outdoor_news_summary.py
  
  # 汇总过去7天的新闻
  python run_outdoor_news_summary.py --days 7
  
  # 汇总过去30天的新闻
  python run_outdoor_news_summary.py --days 30
  
  # 汇总指定日期范围的新闻
  python run_outdoor_news_summary.py --start 2024-01-01 --end 2024-01-14
        """
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=None,
        help=f'回溯天数（默认: {DEFAULT_DAYS_BACK}天）'
    )
    
    parser.add_argument(
        '--start',
        type=parse_date,
        default=None,
        help='开始日期，格式: YYYY-MM-DD'
    )
    
    parser.add_argument(
        '--end',
        type=parse_date,
        default=None,
        help='结束日期，格式: YYYY-MM-DD'
    )
    
    args = parser.parse_args()
    
    if args.days is not None and (args.start is not None or args.end is not None):
        parser.error("--days 参数不能与 --start/--end 参数同时使用")
    
    if (args.start is not None and args.end is None) or (args.start is None and args.end is not None):
        parser.error("--start 和 --end 参数必须同时指定")
    
    if args.start is not None and args.end is not None:
        if args.start > args.end:
            parser.error("开始日期不能晚于结束日期")
        run_outdoor_news_summary_task(start_date=args.start, end_date=args.end)
    elif args.days is not None:
        run_outdoor_news_summary_task(days_back=args.days)
    else:
        run_outdoor_news_summary_task(days_back=DEFAULT_DAYS_BACK)


if __name__ == '__main__':
    main()

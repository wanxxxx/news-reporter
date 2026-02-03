import os
import feedparser
import requests
from bs4 import BeautifulSoup
import trafilatura
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
from lark_oapi.api.docx.v1 import CreateDocumentRequest, CreateDocumentRequestBody, Block, Document, TextElement, Text, TextRun
from lark_oapi.api.im.v1 import CreateMessageRequest, CreateMessageRequestBody
from lark_oapi import Client


TARGET_SITES = [
    'https://explorersweb.com/',
    'https://www.outsideonline.com/home',
    'https://www.climbing.com/',
    'https://publications.americanalpineclub.org/',
    'https://gripped.com/'
]

RSS_FEEDS = {
    'https://explorersweb.com/': 'https://explorersweb.com/feed/',
    'https://www.outsideonline.com/home': 'https://www.outsideonline.com/feed',
    'https://www.climbing.com/': 'https://www.climbing.com/feed/',
    'https://publications.americanalpineclub.org/': None,
    'https://gripped.com/': 'https://gripped.com/feed/'
}


def fetch_weekly_outdoor_articles(start_date: date, end_date: date) -> List[Dict]:
    articles = []
    
    for site_url in TARGET_SITES:
        rss_feed = RSS_FEEDS.get(site_url)
        
        if rss_feed:
            articles.extend(_fetch_from_rss(rss_feed, site_url, start_date, end_date))
        else:
            articles.extend(_fetch_from_html(site_url, start_date, end_date))
    
    return articles


def _fetch_from_rss(rss_url: str, site_url: str, start_date: date, end_date: date) -> List[Dict]:
    articles = []
    
    try:
        print(f"\n🔍 正在解析 RSS: {rss_url}")
        feed = feedparser.parse(rss_url)
        print(f"   RSS feed 中共有 {len(feed.entries)} 条目")
        
        for entry in feed.entries:
            if hasattr(entry, 'published_parsed'):
                article_date = datetime(*entry.published_parsed[:6])
                title = entry.get('title', '')
                
                print(f"   检查文章: {title}")
                print(f"      文章日期: {article_date.date()}")
                print(f"      目标范围: {start_date} 到 {end_date}")
                
                if start_date <= article_date.date() <= end_date:
                    # 文章日期在范围内，开始处理
                    article_url = entry.get('link', '')
                    
                    print(f"📅 找到符合日期的文章: {title}")
                    print(f"   日期: {article_date}")
                    print(f"   链接: {article_url}")
                    
                    # 提取文章内容
                    content_text = _extract_content(article_url)
                    
                    if content_text:
                        articles.append({
                            'site': site_url,
                            'url': article_url,
                            'title': title,
                            'date': article_date.date().isoformat(),
                            'content_text': content_text
                        })
    except Exception as e:
        pass
    
    return articles


def _fetch_from_html(site_url: str, start_date: date, end_date: date) -> List[Dict]:
    articles = []
    
    try:
        response = requests.get(site_url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        article_links = _extract_article_links(soup, site_url)
        
        for link in article_links:
            content_text = _extract_content(link)
            
            if content_text:
                articles.append({
                    'site': site_url,
                    'url': link,
                    'title': _extract_title_from_url(link),
                    'content_text': content_text
                })
    except Exception as e:
        pass
    
    return articles


def _extract_article_links(soup: BeautifulSoup, base_url: str) -> List[str]:
    links = []
    
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        
        if href.startswith('/'):
            href = base_url.rstrip('/') + href
        elif not href.startswith('http'):
            continue
        
        if _is_article_link(href):
            links.append(href)
    
    return list(set(links))


def _is_article_link(url: str) -> bool:
    exclude_patterns = ['#', '/tag/', '/category/', '/author/', '/page/', 'login', 'register']
    
    for pattern in exclude_patterns:
        if pattern in url:
            return False
    
    return True


def _extract_content(url: str) -> Optional[str]:
    try:
        downloaded = trafilatura.fetch_url(url)
        
        if downloaded:
            content = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
            
            if content:
                return content.strip()
    except Exception as e:
        pass
    
    return None


def _extract_title_from_url(url: str) -> str:
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()
    except Exception as e:
        pass
    
    return url

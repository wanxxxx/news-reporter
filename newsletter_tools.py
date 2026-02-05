import os
import json
import re
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional

import feedparser
import requests
from bs4 import BeautifulSoup
import trafilatura
from openai import OpenAI
from dotenv import load_dotenv

import lark_oapi as lark
from lark_oapi.api.docx.v1 import (
    CreateDocumentRequest,
    CreateDocumentRequestBody,
    ConvertDocumentRequest,
    ConvertDocumentRequestBody,
    TextElement,
    TextRun,
    TextElementStyle,
    Link,
    UpdateBlockRequest,
    BatchUpdateDocumentBlockRequest,
    BatchUpdateDocumentBlockRequestBody,
    CreateDocumentBlockChildrenRequest,
    CreateDocumentBlockChildrenRequestBody,
    Block,
    Text as TextModel
)
from lark_oapi.api.im.v1 import CreateMessageRequest, CreateMessageRequestBody
from lark_oapi.api.drive.v1 import (
    CreatePermissionMemberRequest,
    BaseMember,
    BatchCreatePermissionMemberRequest,
    BatchCreatePermissionMemberRequestBody
)

load_dotenv()

client = lark.Client.builder() \
    .app_id(os.getenv("FEISHU_APP_ID")) \
    .app_secret(os.getenv("FEISHU_APP_SECRET")) \
    .log_level(lark.LogLevel.INFO) \
    .build()


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


def fetch_outdoor_articles(start_date: date, end_date: date) -> List[Dict]:
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


def _get_openai_client():
    api_key = os.getenv('LLM_API_KEY')
    base_url = os.getenv('LLM_BASE_URL')
    
    if not api_key:
        raise ValueError('LLM_API_KEY environment variable is not set')
    
    client_kwargs = {'api_key': api_key}
    if base_url:
        client_kwargs['base_url'] = base_url
    
    return OpenAI(**client_kwargs)


def _is_english(text: str) -> bool:
    if not text:
        return False
    
    english_chars = sum(1 for char in text if char.isalpha() and ord(char) < 128)
    total_chars = sum(1 for char in text if char.isalpha())
    
    if total_chars == 0:
        return False
    
    return english_chars / total_chars > 0.5


def _process_single_article_with_ai(client: OpenAI, article: Dict) -> Dict:
    title = article.get('title', '')
    content_text = article.get('content_text', '')
    url = article.get('url', '')
    
    is_english_title = _is_english(title)
    is_english_content = _is_english(content_text)
    
    prompt = f"""
    # Role
    你是一名资深的**户外极限运动编辑**，精通登山（Alpinism）、攀岩（Rock Climbing）、徒步等领域的专业知识和术语。你的任务是阅读以下文章，提取核心信息并生成周报素材。

    # Input Data
    标题: {title}
    文章链接: {url}
    文章正文: {content_text[:4000]} (适当增加长度以防截断关键信息)

    # Goals
    请提取以下信息，并严格按照 JSON 格式返回：

    1. "chinese_title": 
    - 如果原文标题不是中文，将标题翻译成中文。
    - **重要**：必须使用户外圈专业术语（例如：First Ascent译为"首攀"，Free Solo译为"无保护独攀"，Send译为"完攀"，Pitch译为"绳距"）。
    - 风格要求：信达雅，像新闻标题一样吸引人。

    2. "summary": 
    - 用原文语言一句话概括核心事件。
    - 必须包含：人物 + 地点 + 完成了什么成就/发生了什么事故。

    3. "chinese_summary": 
    - 如果summary不是中文，将 summary 翻译成中文，否则赋值summary即可
    - 同样要求精准使用专业术语。

    4. "key_persons": 
    - 提取文章中的核心人物姓名（保留原名，不需要翻译）。

    5. "location":
    - 提取事件发生的地点（如：Mount Everest, Yosemite, El Capitan）。如果未提及，返回 "未知地点"。

    6. "event_date":
    - 提取事件发生的时间（如：2023年10月，或者 Last week）。如果未提及，返回为空。

    # Output Format
    必须返回纯净的 JSON 格式，**严禁**使用 Markdown 代码块（如 ```json ... ```），**严禁**输出任何开场白或结束语。

    JSON 结构示例：
    {{
    "chinese_title": "亚历克斯·霍诺德在约塞米蒂完成史诗级首攀",
    "summary": "Alex Honnold completed the first solo ascent of...",
    "chinese_summary": "亚历克斯·霍诺德完成了...",
    "key_persons": ["Alex Honnold"],
    "location": "El Capitan, Yosemite",
    "event_date": "2023-10-12"
    }}
    """

    model_name = os.getenv('LLM_MODEL')
    if not model_name:
        raise ValueError('LLM_MODEL environment variable is not set')

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {'role': 'system', 'content': '你是一个专业的户外新闻方向的文章分析助手，擅长提取文章关键信息并进行中英文翻译。'},
                {'role': 'user', 'content': prompt}
            ],
            temperature=0.3,
            response_format={'type': 'json_object'},
            timeout=30
        )
        
        result_text = response.choices[0].message.content.strip()
        
        import json
        result = json.loads(result_text)
        
        return {
            'original_title': title,
            'chinese_title': result.get('chinese_title', title),
            'summary': result.get('summary', content_text[:200] + '...'),
            'chinese_summary': result.get('chinese_summary', result.get('summary', content_text[:200] + '...')),
            'key_persons': result.get('key_persons', []),
            'url': url,
            'date': article.get('date', ''),
            'site': article.get('site', '')
        }
    except Exception as e:
        print(f"AI处理失败: {url}, 错误: {str(e)}")
        return {
            'original_title': title,
            'chinese_title': title,
            'summary': content_text[:200] + '...',
            'chinese_summary': content_text[:200] + '...',
            'key_persons': [],
            'url': url,
            'date': article.get('date', ''),
            'site': article.get('site', '')
        }


def process_articles_with_ai(articles_list: List[Dict]) -> str:
    if not articles_list:
        return ''
    
    try:
        client = _get_openai_client()
    except Exception as e:
        print(f"初始化AI客户端失败: {str(e)}")
        return ''
    
    processed_articles = []
    
    for i, article in enumerate(articles_list, 1):
        print(f"正在处理第 {i}/{len(articles_list)} 篇文章...")
        processed = _process_single_article_with_ai(client, article)
        processed_articles.append(processed)
    
    markdown_text = _generate_markdown(processed_articles)
    
    return markdown_text


def _generate_markdown(articles: List[Dict]) -> str:
    if not articles:
        return ''
    
    markdown_lines = []
    markdown_lines.append('# 户外运动周报\n')
    markdown_lines.append(f'生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
    markdown_lines.append(f'共收录 {len(articles)} 篇文章\n')
    markdown_lines.append('---\n')
    
    for i, article in enumerate(articles, 1):
        markdown_lines.append(f'\n## {i}. {article["chinese_title"]}\n')
        
        if article.get('original_title') and article.get('original_title') != article.get('chinese_title'):
            markdown_lines.append(f'**原标题**: {article["original_title"]}\n')
        
        if article.get('date'):
            markdown_lines.append(f'**日期**: {article["date"]}\n')
        
        markdown_lines.append(f'**链接**: {article["url"]}\n')
        
        if article.get('key_persons'):
            persons_text = '、'.join(article['key_persons'])
            markdown_lines.append(f'**关键人物**: {persons_text}\n')
        
        markdown_lines.append(f'\n**摘要**: {article["summary"]}\n')
        
        if article.get('chinese_summary') and article.get('chinese_summary') != article.get('summary'):
            markdown_lines.append(f'\n*中文摘要*: {article["chinese_summary"]}\n')
        
        markdown_lines.append('\n---\n')
    
    return ''.join(markdown_lines)


def _parse_text_with_links(text):
    """
    [内部工具] 解析包含 Markdown 链接的文本
    输入: "点击 [这里](http://google.com) 查看"
    输出: 飞书 TextElement 结构数组
    """
    elements = []
    # 正则匹配 [text](url)
    pattern = re.compile(r'\[(.*?)\]\((.*?)\)')
    last_idx = 0
    
    for match in pattern.finditer(text):
        # 1. 添加链接前的普通文本
        if match.start() > last_idx:
            elements.append(TextElement(
                text_run=TextRun(content=text[last_idx:match.start()])
            ))
        
        # 2. 添加链接文本
        link_text = match.group(1)
        link_url = match.group(2)
        elements.append(TextElement.builder()
            .text_run(TextRun.builder()
                .content(link_text)
                .text_element_style(TextElementStyle.builder()
                    .link(Link.builder().url(link_url).build())
                    .build())
                .build())
            .build())
        last_idx = match.end()
    
    # 3. 添加剩余的文本
    if last_idx < len(text):
        elements.append(TextElement.builder()
            .text_run(TextRun.builder()
                .content(text[last_idx:])
                .build())
            .build())
        
    # 如果没有链接，直接返回纯文本
    if not elements:
        elements.append(TextElement.builder()
            .text_run(TextRun.builder()
                .content(text)
                .build())
            .build())
        
    return elements

def publish_feishu_report(report_title, markdown_content, chat_id):
    """
    核心功能: 创建文档 -> 写入内容 -> 发送卡片
    """
    print(f"🚀 [Feishu] 准备发布文档: {report_title}")
    
    # =================================================
    # 步骤 1: 创建一个新的空白文档
    # =================================================
    try:
        create_req = CreateDocumentRequest.builder() \
            .request_body(CreateDocumentRequestBody.builder()
                .title(report_title)
                .build()) \
            .build()
            
        resp = client.docx.v1.document.create(create_req)
        
        if not resp.success():
            print(f"❌ 创建文档失败: {resp.code} - {resp.msg}")
            return None
            
        document_id = resp.data.document.document_id
        # 注意: 只有飞书国内版是 feishu.cn，国际版请改为 larksuite.com
        doc_url = f"https://feishu.cn/docx/{document_id}"
        print(f"✅ 文档创建成功: {doc_url}")

        collaborator_openids = os.getenv("FEISHU_COLLABORATOR_OPENIDS", "")
        collaborator_perm = os.getenv("FEISHU_COLLABORATOR_PERM", "edit")
        
        if collaborator_openids:
            openids = [oid.strip() for oid in collaborator_openids.split(",") if oid.strip()]
            
            added_count = 0
            failed_count = 0
            
            for openid in openids:
                try:
                    add_req = CreatePermissionMemberRequest.builder() \
                        .token(document_id) \
                        .type("docx") \
                        .need_notification(False) \
                        .request_body(BaseMember.builder()
                            .member_type("openid")
                            .member_id(openid)
                            .perm(collaborator_perm)
                            .perm_type("container")
                            .type("user")
                            .build()) \
                        .build()
                    
                    add_resp = client.drive.v1.permission_member.create(add_req)
                    
                    if add_resp.success():
                        print(f"✅ 协作者添加成功: {openid}")
                        added_count += 1
                    else:
                        print(f"⚠️ 协作者添加失败: {openid} - {add_resp.msg}")
                        failed_count += 1
                        
                except Exception as e:
                    print(f"⚠️ 为 {openid} 添加协作者时出错: {e}")
                    failed_count += 1
            
            if added_count > 0:
                print(f"✅ 成功添加 {added_count} 个协作者，权限: {collaborator_perm}")
            if failed_count > 0:
                print(f"⚠️ {failed_count} 个协作者添加失败")

    except Exception as e:
        print(f"❌ 飞书 API 连接错误: {e}")
        return None

    # =================================================
    # 步骤 2: 使用飞书官方 API 将 Markdown 转换为 Blocks
    # =================================================
    print("🔄 正在将 Markdown 转换为飞书文档块...")
    
    # 调用飞书官方的 Markdown 转换 API
    convert_req = ConvertDocumentRequest.builder() \
        .request_body(ConvertDocumentRequestBody.builder()
            .content_type("markdown")
            .content(markdown_content)
            .build()) \
        .build()
    
    convert_resp = client.docx.v1.document.convert(convert_req)
    
    if not convert_resp.success():
        print(f"❌ Markdown 转换失败: {convert_resp.code} - {convert_resp.msg}")
        return None
    
    # 获取转换后的 blocks
    blocks = convert_resp.data.blocks
    first_level_block_ids = convert_resp.data.first_level_block_ids or []
    
    if not blocks:
        print("⚠️ 转换后的内容为空")
        return doc_url
    
    # 使用 first_level_block_ids 重新排序 blocks
    if first_level_block_ids:
        block_map = {b.block_id: b for b in blocks}
        ordered_blocks = []
        for block_id in first_level_block_ids:
            if block_id in block_map:
                ordered_blocks.append(block_map[block_id])
        # 添加不在 first_level_block_ids 中的 blocks
        for block in blocks:
            if block.block_id not in first_level_block_ids:
                ordered_blocks.append(block)
        blocks = ordered_blocks
    
    print(f"✅ Markdown 转换成功，共 {len(blocks)} 个 blocks")
    
    # =================================================
    # 步骤 3: 批量写入 blocks 到文档
    # =================================================
    print("📝 正在写入文档内容...")
    
    # 批量写入（每次最多 100 个 block）
    batch_size = 100
    for i in range(0, len(blocks), batch_size):
        batch_blocks = blocks[i:i + batch_size]
        batch_num = i // batch_size + 1
        
        add_block_req = CreateDocumentBlockChildrenRequest.builder() \
            .document_id(document_id) \
            .block_id(document_id) \
            .request_body(CreateDocumentBlockChildrenRequestBody.builder()
                .children(batch_blocks)
                .build()) \
            .build()
        
        add_resp = client.docx.v1.document_block_children.create(add_block_req)
        
        if add_resp.success():
            print(f"✅ 批次 {batch_num} 写入成功 ({len(batch_blocks)} blocks)")
        else:
            print(f"⚠️ 批次 {batch_num} 写入失败: {add_resp.code} - {add_resp.msg}")

    # =================================================
    # 步骤 4: 发送富文本卡片消息
    # =================================================
    print(f"📤 正在推送到群组: {chat_id}")
    
    # 构造卡片 JSON
    card_content = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": "🧗‍♂️ 户外资讯周报已生成"},
            "template": "blue" # 标题背景色: blue, wathet, turquoise, green, yellow, orange, red, carmine, violet, purple, indigo, grey
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"本周资讯已由 AI 整理完毕。\n**标题：** {report_title}\n**时间：** {os.getenv('TODAY', '本周')}"
                }
            },
            {
                "tag": "hr" # 分割线
            },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": "👉 点击阅读完整周报"},
                        "url": doc_url,
                        "type": "primary"
                    }
                ]
            }
        ]
    }

    # 发送请求
    msg_req = CreateMessageRequest.builder() \
        .receive_id_type("chat_id") \
        .request_body(CreateMessageRequestBody.builder() \
            .receive_id(chat_id) \
            .msg_type("interactive") \
            .content(json.dumps(card_content)) \
            .build()) \
        .build()

    msg_resp = client.im.v1.message.create(msg_req)
    
    if msg_resp.success():
        print("✅ 消息推送成功")
        return doc_url
    else:
        print(f"❌ 消息推送失败: {msg_resp.code} - {msg_resp.msg}")
        return None

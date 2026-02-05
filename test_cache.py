import sys
sys.path.insert(0, '.')
import os
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('ALL_PROXY', None)

from dotenv import load_dotenv
load_dotenv()

from newsletter_tools import load_ai_from_cache, get_ai_cache_path

# 测试缓存是否能命中
test_url = 'https://gripped.com/gear/metolius-nano-rings-a-review/'
result = load_ai_from_cache(test_url)
if result:
    print('✅ 缓存命中成功!')
    print(f"Title: {result.get('chinese_title', 'N/A')}")
else:
    print('❌ 缓存未命中')
    cache_path = get_ai_cache_path(test_url)
    print(f'缓存路径: {cache_path}')
    print(f'文件存在: {os.path.exists(cache_path)}')

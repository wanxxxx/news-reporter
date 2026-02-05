"""
测试 _clean_rss_content 函数
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from newsletter_tools import _clean_rss_content

# 测试用例1：包含HTML标签和元数据
test_content_1 = """
<figure><img alt="What Happens When a National Park Runs Out of Water?" src="https://cdn.outsideonline.com/wp-content/uploads/2026/02/GettyImages-1436195936-1.jpg" /></figure>
<p>Big Bend National Park faces partial closures, citing a pump failure during a critical water shortage.</p>
<p>The post <a href="https://www.outsideonline.com/outdoor-adventure/environment/big-bend-national-park-closed-water-shortage/">What Happens When a National Park Runs Out of Water?</a> appeared first on <a href="https://www.outsideonline.com">Outside Online</a>.</p>
<figure><img alt="What Happens When a National Park Runs Out of Water?" src="https://cdn.outsideonline.com/wp-content/uploads/2026/02/GettyImages-1436195936-1.jpg" /></figure>
<p>In late January, the National Park Service (NPS) shut down portions of Texas' Big Bend National Park.</p>
"""

# 测试用例2：包含重复的元数据
test_content_2 = """
<p>This is the main content of the article.</p>
<p>The post <a href="https://example.com/article">Article Title</a> appeared first on <a href="https://example.com">Example Site</a>.</p>
<p>More information about the topic.</p>
<p>For details, visit our website.</p>
"""

# 测试用例3：正常内容（无HTML和元数据）
test_content_3 = """
<p>This is a clean article content without HTML tags or metadata.</p>
<p>The article discusses outdoor sports and adventure activities.</p>
"""

print("=" * 80)
print("测试 _clean_rss_content 函数")
print("=" * 80)

print("\n测试用例1：包含HTML标签和元数据")
print("-" * 80)
print("原始内容:")
print(test_content_1[:200] + "...")
print("\n清理后内容:")
cleaned_1 = _clean_rss_content(test_content_1)
print(cleaned_1)
print(f"\n原始长度: {len(test_content_1)}, 清理后长度: {len(cleaned_1)}")

print("\n" + "=" * 80)
print("\n测试用例2：包含重复的元数据")
print("-" * 80)
print("原始内容:")
print(test_content_2)
print("\n清理后内容:")
cleaned_2 = _clean_rss_content(test_content_2)
print(cleaned_2)
print(f"\n原始长度: {len(test_content_2)}, 清理后长度: {len(cleaned_2)}")

print("\n" + "=" * 80)
print("\n测试用例3：正常内容（无HTML和元数据）")
print("-" * 80)
print("原始内容:")
print(test_content_3)
print("\n清理后内容:")
cleaned_3 = _clean_rss_content(test_content_3)
print(cleaned_3)
print(f"\n原始长度: {len(test_content_3)}, 清理后长度: {len(cleaned_3)}")

print("\n" + "=" * 80)
print("✅ 测试完成")
print("=" * 80)

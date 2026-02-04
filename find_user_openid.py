import os
import requests
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

def get_tenant_access_token():
    """获取 tenant_access_token"""
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        if result.get("code") == 0:
            return result.get("tenant_access_token")
    return None

def find_user_by_email(email: str):
    """通过邮箱查找用户"""
    token = get_tenant_access_token()
    if not token:
        print("❌ 获取 access token 失败")
        return None
    
    # 使用批量获取用户ID API
    url = "https://open.feishu.cn/open-apis/contact/v3/users/batch_get_id"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 通过邮箱获取用户 ID
    data = {
        "emails": [email]
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"API响应状态码: {response.status_code}")
    print(f"API响应内容: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("code") == 0:
            users = result.get("data", {}).get("user_list", [])
            if users:
                return users[0]
    return None

def find_users_by_emails(emails: list):
    """批量查找用户"""
    token = get_tenant_access_token()
    if not token:
        print("❌ 获取 access token 失败")
        return []
    
    url = "https://open.feishu.cn/open-apis/contact/v3/users/batch_get_id"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "emails": emails
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"\n批量查询API响应状态码: {response.status_code}")
    print(f"批量查询API响应内容: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("code") == 0:
            return result.get("data", {}).get("user_list", [])
    return []

if __name__ == "__main__":
    print("=" * 80)
    print("查找飞书用户 OpenID")
    print("=" * 80)
    
    # 检查环境变量
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    
    if not app_id or not app_secret:
        print("❌ 请先配置环境变量：")
        print("   FEISHU_APP_ID")
        print("   FEISHU_APP_SECRET")
    else:
        print(f"✅ 已配置 FEISHU_APP_ID: {app_id}")
        print(f"✅ 已配置 FEISHU_APP_SECRET: {app_secret[:10]}...")
    
    # 查找单个用户
    print("\n" + "-" * 80)
    print("查找单个用户...")
    
    email1 = "fxx220018@163.com"
    user1 = find_user_by_email(email1)
    if user1:
        print(f"\n✅ 找到用户: {email1}")
        print(f"   OpenID: {user1.get('open_id')}")
        print(f"   UnionID: {user1.get('union_id')}")
        print(f"   UserID: {user1.get('user_id')}")
    else:
        print(f"\n❌ 未找到用户: {email1}")
    
    email2 = "1141998623@qq.com"
    user2 = find_user_by_email(email2)
    if user2:
        print(f"\n✅ 找到用户: {email2}")
        print(f"   OpenID: {user2.get('open_id')}")
        print(f"   UnionID: {user2.get('union_id')}")
        print(f"   UserID: {user2.get('user_id')}")
    else:
        print(f"\n❌ 未找到用户: {email2}")
    
    # 批量查找
    print("\n" + "-" * 80)
    print("批量查找用户...")
    users = find_users_by_emails([email1, email2])
    print(f"\n找到 {len(users)} 个用户")
    
    for user in users:
        print(f"\n用户信息:")
        print(f"   OpenID: {user.get('open_id')}")
        print(f"   UnionID: {user.get('union_id')}")
        print(f"   UserID: {user.get('user_id')}")
        print(f"   邮箱: {user.get('email')}")
    
    print("\n" + "=" * 80)

#!/usr/bin/env python3
"""
API测试脚本 - 用于测试股票顾问API是否正常工作
"""

import requests
import json
import uuid
from datetime import datetime

def test_api():
    """测试股票分析API和历史记录API"""
    base_url = "http://localhost:8000/Agentswenda"
    session_id = f"test_session_{uuid.uuid4().hex[:8]}"
    
    print("🤖 开始测试智能股票顾问API...")
    print(f"📊 会话ID: {session_id}")
    print("-" * 50)
    
    # 测试数据
    test_data = {
        "stock_name": "苹果",
        "investment_amount": "10000元",
        "session_id": session_id
    }
    
    try:
        # 1. 测试分析API
        print("1️⃣ 测试股票分析API...")
        analyze_url = f"{base_url}/api/analyze/"
        
        response = requests.post(
            analyze_url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 分析API测试成功!")
            print(f"📈 分析结果预览: {result.get('analysis', '')[:100]}...")
            print(f"⏰ 时间戳: {result.get('timestamp', '')}")
        else:
            print(f"❌ 分析API测试失败: {response.text}")
            return False
            
        # 2. 测试历史记录API
        print("\n2️⃣ 测试历史记录API...")
        history_url = f"{base_url}/api/history/"
        
        response = requests.get(
            history_url,
            params={'session_id': session_id},
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 历史记录API测试成功!")
            print(f"📝 历史记录数量: {len(result.get('history', []))}")
        else:
            print(f"❌ 历史记录API测试失败: {response.text}")
            return False
            
        print("\n🎉 所有API测试通过!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误: 无法连接到Django服务器")
        print("请确保Django服务器正在运行在 http://localhost:8000")
        return False
    except requests.exceptions.Timeout:
        print("❌ 请求超时: API响应时间过长")
        return False
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        return False

def check_server_status():
    """检查服务器状态"""
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        return True
    except:
        return False

if __name__ == "__main__":
    print("🔍 检查Django服务器状态...")
    
    if not check_server_status():
        print("⚠️  Django服务器未运行!")
        print("请先启动Django服务器:")
        print("   cd DAY11")
        print("   python manage.py runserver")
        exit(1)
    
    print("✅ Django服务器正在运行")
    print()
    
    success = test_api()
    
    if success:
        print("\n🌟 前端可以正常连接后端API!")
        print("🚀 现在可以启动Vue前端应用了:")
        print("   cd day11_vue")
        print("   npm run dev")
    else:
        print("\n❌ API测试失败，请检查后端配置")


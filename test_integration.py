#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG + Agents 集成测试脚本
"""
import os
import sys

def test_rag_import():
    """测试RAG模块导入"""
    try:
        from RAG脚本 import retriever, chain
        print("✅ RAG模块导入成功")
        return True
    except Exception as e:
        print(f"❌ RAG模块导入失败: {e}")
        return False

def test_agents_import():
    """测试Agents模块导入"""
    try:
        from Agents脚本 import fd, tools
        print("✅ Agents模块导入成功")
        print(f"✅ 可用工具数量: {len(tools)}")
        return True
    except Exception as e:
        print(f"❌ Agents模块导入失败: {e}")
        return False

def test_rag_functionality():
    """测试RAG功能"""
    try:
        from RAG脚本 import chain
        question = "苹果公司股票信息"
        answer = chain.invoke(question)
        print(f"✅ RAG查询成功")
        print(f"🔍 查询: {question}")
        print(f"📝 回答预览: {answer[:100]}...")
        return True
    except Exception as e:
        print(f"❌ RAG查询失败: {e}")
        return False

def test_agents_functionality():
    """测试Agents功能"""
    try:
        from Agents脚本 import fd
        
        print("🤖 测试Agent功能...")
        result = fd.invoke({
            "name": "苹果", 
            "mo": 10000
        })
        
        print("✅ Agent执行成功")
        print(f"📊 分析结果预览: {result['output'][:200]}...")
        return True
    except Exception as e:
        print(f"❌ Agent执行失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始RAG + Agents集成测试")
    print("=" * 50)
    
    tests = [
        ("RAG模块导入", test_rag_import),
        ("Agents模块导入", test_agents_import),
        ("RAG功能", test_rag_functionality),
        ("Agents功能", test_agents_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        print("-" * 30)
        success = test_func()
        results.append((test_name, success))
        print()
    
    print("=" * 50)
    print("📊 测试结果汇总:")
    print("-" * 30)
    
    all_passed = True
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name}: {status}")
        if not success:
            all_passed = False
    
    print("-" * 30)
    if all_passed:
        print("🎉 所有测试通过！RAG和Agents集成成功！")
    else:
        print("⚠️  部分测试失败，请检查相关配置")
    
    return all_passed

if __name__ == "__main__":
    main()

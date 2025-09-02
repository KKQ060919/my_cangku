#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专用Redis对话记录存储管理器
"""

import redis
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

class ChatRedisManager:
    """Redis对话记录管理器"""
    
    def __init__(self, host='localhost', port=6379, db=1, decode_responses=True):
        """初始化Redis连接"""
        self.redis_client = redis.Redis(
            host=host, 
            port=port, 
            db=db, 
            decode_responses=decode_responses
        )
        self.chat_prefix = "stock_chat:"
        self.session_prefix = "chat_session:"
        
    def save_conversation(self, session_id: str, user_message: str, 
                         bot_response: str, stock_info: Optional[Dict] = None):
        """保存对话记录"""
        conversation = {
            "时间戳": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "用户消息": user_message,
            "机器人回复": bot_response,
            "股票信息": stock_info or {},
            "会话ID": session_id
        }
        
        # 存储单条对话记录
        chat_key = f"{self.chat_prefix}{session_id}:{int(time.time())}"
        self.redis_client.setex(chat_key, 86400 * 7, json.dumps(conversation, ensure_ascii=False))
        
        # 维护会话消息列表
        session_key = f"{self.session_prefix}{session_id}"
        self.redis_client.lpush(session_key, chat_key)
        self.redis_client.expire(session_key, 86400 * 7)
        
        print(f"✅ 对话记录已保存: {session_id}")
        return chat_key
    
    def get_session_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """获取会话历史记录"""
        session_key = f"{self.session_prefix}{session_id}"
        chat_keys = self.redis_client.lrange(session_key, 0, limit - 1)
        
        conversations = []
        for key in chat_keys:
            data = self.redis_client.get(key)
            if data:
                conversations.append(json.loads(data))
        
        return conversations
    
    def get_latest_chat(self, session_id: str) -> Optional[Dict]:
        """获取最新对话"""
        history = self.get_session_history(session_id, 1)
        return history[0] if history else None
    
    def clear_session(self, session_id: str):
        """清除会话记录"""
        session_key = f"{self.session_prefix}{session_id}"
        chat_keys = self.redis_client.lrange(session_key, 0, -1)
        
        # 删除所有对话记录
        for key in chat_keys:
            self.redis_client.delete(key)
        
        # 删除会话索引
        self.redis_client.delete(session_key)
        print(f"✅ 会话记录已清除: {session_id}")
    
    def get_all_sessions(self) -> List[str]:
        """获取所有会话ID"""
        pattern = f"{self.session_prefix}*"
        keys = self.redis_client.keys(pattern)
        return [key.replace(self.session_prefix, "") for key in keys]
    
    def get_stats(self) -> Dict:
        """获取存储统计信息"""
        chat_count = len(self.redis_client.keys(f"{self.chat_prefix}*"))
        session_count = len(self.redis_client.keys(f"{self.session_prefix}*"))
        
        return {
            "对话记录总数": chat_count,
            "活跃会话数": session_count,
            "Redis连接状态": "正常" if self.redis_client.ping() else "异常"
        }


# 使用示例和测试
if __name__ == '__main__':
    # 创建Redis管理器实例
    chat_manager = ChatRedisManager()
    
    # 测试连接
    try:
        stats = chat_manager.get_stats()
        print("📊 Redis连接测试成功")
        print(f"状态: {stats}")
        
        # 示例对话记录
        session_id = "test_session_001"
        
        # 保存测试对话
        chat_manager.save_conversation(
            session_id=session_id,
            user_message="分析苹果股票",
            bot_response="苹果公司(AAPL)当前表现良好，建议长期持有...",
            stock_info={"股票代码": "AAPL", "当前价格": "172.57", "行业": "科技"}
        )
        
        chat_manager.save_conversation(
            session_id=session_id,
            user_message="投资10000元有什么风险？",
            bot_response="投资苹果股票10000元，风险等级为中等...",
            stock_info={"投资金额": "10000元", "风险等级": "中等"}
        )
        
        # 获取历史记录
        history = chat_manager.get_session_history(session_id)
        print(f"\n📝 会话历史 ({len(history)}条):")
        for i, conv in enumerate(history, 1):
            print(f"{i}. {conv['时间戳']} - {conv['用户消息'][:20]}...")
        
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        print("请确保Redis服务正在运行")

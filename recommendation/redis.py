"""
推荐系统Redis管理模块
用于存储推荐相关的缓存数据和对话记录
"""
import redis
import json
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class RecommendationRedisManager:
    """推荐系统Redis管理器"""
    
    def __init__(self):
        """初始化Redis连接"""
        try:
            self.client = redis.Redis(
                host='localhost',
                port=6379,
                db=3,  # 使用db 3 用于推荐系统
                decode_responses=True,
                encoding='utf-8'
            )
            # 测试连接
            self.client.ping()
            logger.info("推荐系统Redis连接成功")
        except Exception as e:
            logger.error(f"推荐系统Redis连接失败: {e}")
            raise
    
    def cache_user_recommendations(self, user_id: str, recommendations: List[Dict], ttl: int = 3600) -> bool:
        """
        缓存用户推荐结果
        Args:
            user_id: 用户ID
            recommendations: 推荐结果列表
            ttl: 缓存时间（秒），默认1小时
        Returns:
            是否成功
        """
        try:
            cache_key = f"rec:{user_id}"
            
            recommendation_data = {
                'recommendations': recommendations,
                'generated_at': datetime.now().isoformat(),
                'count': len(recommendations)
            }
            
            # 转换为JSON，确保中文正确显示
            data_json = json.dumps(recommendation_data, ensure_ascii=False)
            
            # 缓存推荐结果
            self.client.setex(cache_key, ttl, data_json)
            
            logger.info(f"用户 {user_id} 推荐结果缓存成功，共 {len(recommendations)} 个商品")
            return True
            
        except Exception as e:
            logger.error(f"缓存用户推荐结果失败: {e}")
            return False
    
    def get_user_recommendations(self, user_id: str) -> Optional[Dict]:
        """
        获取用户缓存的推荐结果
        Args:
            user_id: 用户ID
        Returns:
            推荐结果字典，如果不存在返回None
        """
        try:
            cache_key = f"rec:{user_id}"
            cached_data = self.client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            return None
            
        except Exception as e:
            logger.error(f"获取用户推荐缓存失败: {e}")
            return None
    
    def save_conversation(self, user_id: str, question: str, answer: str, recommendation_ids: List[str] = None) -> bool:
        """
        保存对话记录
        Args:
            user_id: 用户ID
            question: 用户问题
            answer: 系统回答
            recommendation_ids: 推荐的商品ID列表
        Returns:
            是否成功
        """
        try:
            conversation_key = f"conversation:{user_id}"
            
            conversation_data = {
                'question': question,
                'answer': answer,
                'recommendations': recommendation_ids or [],
                'timestamp': datetime.now().isoformat()
            }
            
            # 转换为JSON，确保中文正确显示
            conversation_json = json.dumps(conversation_data, ensure_ascii=False)
            
            # 使用LPUSH添加到列表头部，LTRIM保持最近50条记录
            self.client.lpush(conversation_key, conversation_json)
            self.client.ltrim(conversation_key, 0, 49)
            
            # 设置过期时间（30天）
            self.client.expire(conversation_key, 30 * 24 * 3600)
            
            logger.info(f"用户 {user_id} 对话记录保存成功")
            return True
            
        except Exception as e:
            logger.error(f"保存对话记录失败: {e}")
            return False
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        获取用户对话历史
        Args:
            user_id: 用户ID
            limit: 返回条数限制
        Returns:
            对话历史列表
        """
        try:
            conversation_key = f"conversation:{user_id}"
            history = self.client.lrange(conversation_key, 0, limit - 1)
            
            conversations = []
            for conv_json in history:
                try:
                    conv_data = json.loads(conv_json)
                    conversations.append(conv_data)
                except json.JSONDecodeError:
                    continue
            
            return conversations
            
        except Exception as e:
            logger.error(f"获取对话历史失败: {e}")
            return []
    
    def cache_similar_products(self, product_id: str, similar_products: List[Dict], ttl: int = 7200) -> bool:
        """
        缓存商品相似度计算结果
        Args:
            product_id: 商品ID
            similar_products: 相似商品列表
            ttl: 缓存时间（秒），默认2小时
        Returns:
            是否成功
        """
        try:
            cache_key = f"similar:{product_id}"
            
            similarity_data = {
                'similar_products': similar_products,
                'generated_at': datetime.now().isoformat(),
                'count': len(similar_products)
            }
            
            # 转换为JSON
            data_json = json.dumps(similarity_data, ensure_ascii=False)
            
            # 缓存相似商品
            self.client.setex(cache_key, ttl, data_json)
            
            return True
            
        except Exception as e:
            logger.error(f"缓存相似商品失败: {e}")
            return False
    
    def get_similar_products(self, product_id: str) -> Optional[List[Dict]]:
        """
        获取缓存的相似商品
        Args:
            product_id: 商品ID
        Returns:
            相似商品列表
        """
        try:
            cache_key = f"similar:{product_id}"
            cached_data = self.client.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                return data.get('similar_products', [])
            return None
            
        except Exception as e:
            logger.error(f"获取相似商品缓存失败: {e}")
            return None
    
    def increment_recommendation_click(self, user_id: str, product_id: str) -> bool:
        """
        记录推荐商品点击次数
        Args:
            user_id: 用户ID
            product_id: 商品ID
        Returns:
            是否成功
        """
        try:
            # 全局商品点击统计
            global_key = f"rec_clicks:global"
            self.client.zincrby(global_key, 1, product_id)
            
            # 用户个人点击统计
            user_key = f"rec_clicks:{user_id}"
            self.client.zincrby(user_key, 1, product_id)
            self.client.expire(user_key, 30 * 24 * 3600)  # 30天过期
            
            # 设置全局统计过期时间（90天）
            self.client.expire(global_key, 90 * 24 * 3600)
            
            return True
            
        except Exception as e:
            logger.error(f"记录推荐点击失败: {e}")
            return False
    
    def get_top_clicked_products(self, limit: int = 20) -> List[Dict]:
        """
        获取最受欢迎的推荐商品
        Args:
            limit: 返回数量限制
        Returns:
            商品点击统计列表
        """
        try:
            global_key = f"rec_clicks:global"
            
            # 获取点击量最高的商品
            top_products = self.client.zrevrange(
                global_key, 0, limit - 1, withscores=True
            )
            
            result = []
            for product_id, score in top_products:
                result.append({
                    'product_id': product_id,
                    'click_count': int(score)
                })
            
            return result
            
        except Exception as e:
            logger.error(f"获取热门推荐商品失败: {e}")
            return []
    
    def clear_user_cache(self, user_id: str) -> bool:
        """
        清空用户相关缓存
        Args:
            user_id: 用户ID
        Returns:
            是否成功
        """
        try:
            # 清空推荐缓存
            rec_key = f"rec:{user_id}"
            self.client.delete(rec_key)
            
            # 清空对话历史
            conv_key = f"conversation:{user_id}"
            self.client.delete(conv_key)
            
            # 清空个人点击统计
            click_key = f"rec_clicks:{user_id}"
            self.client.delete(click_key)
            
            logger.info(f"用户 {user_id} 相关缓存清空成功")
            return True
            
        except Exception as e:
            logger.error(f"清空用户缓存失败: {e}")
            return False
    
    def record_recommendation_feedback(self, user_id: str, product_id: str, feedback_type: str, product_info: Dict = None) -> bool:
        """
        记录用户对推荐的反馈
        Args:
            user_id: 用户ID
            product_id: 商品ID
            feedback_type: 反馈类型 (interested, not_interested)
            product_info: 商品信息
        Returns:
            是否成功
        """
        try:
            feedback_key = f"rec_feedback:{user_id}"
            
            feedback_data = {
                'product_id': product_id,
                'feedback_type': feedback_type,
                'timestamp': datetime.now().isoformat(),
                'product_info': product_info or {}
            }
            
            # 转换为JSON
            feedback_json = json.dumps(feedback_data, ensure_ascii=False)
            
            # 添加到用户反馈历史
            self.client.lpush(feedback_key, feedback_json)
            self.client.ltrim(feedback_key, 0, 99)  # 保持最近100条反馈
            self.client.expire(feedback_key, 30 * 24 * 3600)  # 30天过期
            
            # 全局反馈统计
            global_feedback_key = f"global_feedback:{feedback_type}"
            self.client.zincrby(global_feedback_key, 1, product_id)
            self.client.expire(global_feedback_key, 90 * 24 * 3600)  # 90天过期
            
            # 用户反馈计数统计
            user_stats_key = f"user_feedback_stats:{user_id}"
            self.client.hincrby(user_stats_key, feedback_type, 1)
            self.client.hincrby(user_stats_key, 'total_feedback', 1)
            self.client.expire(user_stats_key, 30 * 24 * 3600)  # 30天过期
            
            logger.info(f"用户 {user_id} 对商品 {product_id} 的反馈已记录: {feedback_type}")
            return True
            
        except Exception as e:
            logger.error(f"记录推荐反馈失败: {e}")
            return False
    
    def get_user_recommendation_stats(self, user_id: str) -> Dict:
        """
        获取用户特定的推荐统计
        Args:
            user_id: 用户ID
        Returns:
            用户推荐统计字典
        """
        try:
            stats = {}
            
            # 用户反馈统计
            user_stats_key = f"user_feedback_stats:{user_id}"
            feedback_stats = self.client.hgetall(user_stats_key)
            
            stats.update({
                'interested_count': int(feedback_stats.get('interested', 0)),
                'not_interested_count': int(feedback_stats.get('not_interested', 0)),
                'total_feedback': int(feedback_stats.get('total_feedback', 0))
            })
            
            # 用户点击统计
            user_click_key = f"rec_clicks:{user_id}"
            total_clicks = self.client.zcard(user_click_key)
            stats['total_clicks'] = total_clicks
            
            # 用户推荐缓存状态
            rec_key = f"rec:{user_id}"
            has_cached_recommendations = self.client.exists(rec_key)
            stats['has_cached_recommendations'] = bool(has_cached_recommendations)
            
            # 用户对话记录数量
            conv_key = f"conversation:{user_id}"
            conversation_count = self.client.llen(conv_key)
            stats['conversation_count'] = conversation_count
            
            # 计算推荐满意度
            if stats['total_feedback'] > 0:
                stats['satisfaction_rate'] = stats['interested_count'] / stats['total_feedback']
            else:
                stats['satisfaction_rate'] = 0.0
            
            # 平均匹配度 (简化计算，实际可以从反馈中获取更详细数据)
            stats['avg_confidence'] = 0.75  # 默认值，可以基于实际反馈优化
            
            # 推荐总次数（简化为总反馈数，实际应该单独统计）
            stats['total_recommendations'] = stats['total_feedback']
            
            return stats
            
        except Exception as e:
            logger.error(f"获取用户推荐统计失败: {e}")
            return {}
    
    def get_recommendation_stats(self) -> Dict:
        """获取推荐系统统计信息"""
        try:
            # 统计各种key的数量
            rec_keys = self.client.keys("rec:*")
            conv_keys = self.client.keys("conversation:*")
            similar_keys = self.client.keys("similar:*")
            click_keys = self.client.keys("rec_clicks:*")
            feedback_keys = self.client.keys("rec_feedback:*")
            
            # 全局反馈统计
            interested_key = "global_feedback:interested"
            not_interested_key = "global_feedback:not_interested"
            
            total_interested = 0
            total_not_interested = 0
            
            if self.client.exists(interested_key):
                interested_scores = self.client.zrange(interested_key, 0, -1, withscores=True)
                total_interested = sum(int(score) for _, score in interested_scores)
                
            if self.client.exists(not_interested_key):
                not_interested_scores = self.client.zrange(not_interested_key, 0, -1, withscores=True)
                total_not_interested = sum(int(score) for _, score in not_interested_scores)
            
            total_feedback = total_interested + total_not_interested
            satisfaction_rate = total_interested / total_feedback if total_feedback > 0 else 0.0
            
            return {
                'cached_recommendations': len(rec_keys),
                'conversation_records': len(conv_keys),
                'similar_products_cache': len(similar_keys),
                'click_statistics': len(click_keys),
                'feedback_records': len(feedback_keys),
                'total_keys': len(rec_keys) + len(conv_keys) + len(similar_keys) + len(click_keys) + len(feedback_keys),
                'total_interested': total_interested,
                'total_not_interested': total_not_interested,
                'total_feedback': total_feedback,
                'satisfaction_rate': satisfaction_rate,
                'active_users': len(rec_keys)  # 有缓存推荐的用户数量
            }
            
        except Exception as e:
            logger.error(f"获取推荐统计失败: {e}")
            return {}


# 单例模式
_recommendation_redis_manager = None

def get_recommendation_redis_manager():
    """获取推荐系统Redis管理器单例"""
    global _recommendation_redis_manager
    if _recommendation_redis_manager is None:
        _recommendation_redis_manager = RecommendationRedisManager()
    return _recommendation_redis_manager

"""
用户行为记录Redis管理模块
使用Redis ZSET记录用户浏览历史，支持按时间排序
"""
import redis
import json
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class UserBehaviorRedisManager:
    """用户行为Redis管理器"""
    
    def __init__(self):
        """初始化Redis连接"""
        try:
            self.client = redis.Redis(
                host='localhost',
                port=6379,
                db=2,  # 使用db 2 用于用户行为
                decode_responses=True,
                encoding='utf-8'
            )
            # 测试连接
            self.client.ping()
            logger.info("用户行为Redis连接成功")
        except Exception as e:
            logger.error(f"用户行为Redis连接失败: {e}")
            raise
    
    def record_product_view(self, user_id: str, product_id: str, product_info: Dict = None) -> bool:
        """
        记录用户浏览商品行为
        Args:
            user_id: 用户ID
            product_id: 商品ID
            product_info: 商品信息（可选）
        Returns:
            是否成功
        """
        try:
            # 用户浏览历史的key
            history_key = f"user_history:{user_id}"
            
            # 当前时间戳作为score
            timestamp = time.time()
            
            # 商品信息，包含浏览时间
            view_data = {
                'product_id': product_id,
                'viewed_at': datetime.now().isoformat(),
                'timestamp': timestamp
            }
            
            # 如果有商品信息，添加到记录中
            if product_info:
                view_data.update(product_info)
            
            # 转换为JSON字符串，确保中文正确显示
            view_json = json.dumps(view_data, ensure_ascii=False)
            
            # 添加到ZSET，score为时间戳
            self.client.zadd(history_key, {view_json: timestamp})
            
            # 只保留最近10条记录，删除旧记录
            self.client.zremrangebyrank(history_key, 0, -11)
            
            # 设置过期时间（30天）
            self.client.expire(history_key, 30 * 24 * 3600)
            
            logger.info(f"用户 {user_id} 浏览商品 {product_id} 记录成功")
            return True
            
        except Exception as e:
            logger.error(f"记录用户行为失败: {e}")
            return False
    
    def get_user_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        获取用户浏览历史，按时间倒序
        Args:
            user_id: 用户ID
            limit: 返回条数限制
        Returns:
            浏览历史列表
        """
        try:
            history_key = f"user_history:{user_id}"
            
            # 从ZSET中获取最新的记录（按score倒序）
            history_records = self.client.zrevrange(
                history_key, 0, limit - 1, withscores=True
            )
            
            history_list = []
            for record_json, score in history_records:
                try:
                    record_data = json.loads(record_json)
                    history_list.append(record_data)
                except json.JSONDecodeError:
                    continue
            
            return history_list
            
        except Exception as e:
            logger.error(f"获取用户 {user_id} 浏览历史失败: {e}")
            return []
    
    def get_user_preferences(self, user_id: str) -> Dict:
        """
        分析用户偏好，基于浏览历史
        Args:
            user_id: 用户ID
        Returns:
            用户偏好统计
        """
        try:
            history = self.get_user_history(user_id, limit=50)  # 分析最近50条记录
            
            if not history:
                return {
                    'categories': {},
                    'brands': {},
                    'price_ranges': {},
                    'total_views': 0
                }
            
            # 统计分析
            categories = {}
            brands = {}
            price_ranges = {
                '0-500': 0,
                '500-1000': 0,
                '1000-2000': 0,
                '2000-5000': 0,
                '5000+': 0
            }
            
            for record in history:
                # 统计类别
                category = record.get('category')
                if category:
                    categories[category] = categories.get(category, 0) + 1
                
                # 统计品牌
                brand = record.get('brand')
                if brand:
                    brands[brand] = brands.get(brand, 0) + 1
                
                # 统计价格区间
                price = record.get('price', 0)
                try:
                    price = float(price)
                    if price < 500:
                        price_ranges['0-500'] += 1
                    elif price < 1000:
                        price_ranges['500-1000'] += 1
                    elif price < 2000:
                        price_ranges['1000-2000'] += 1
                    elif price < 5000:
                        price_ranges['2000-5000'] += 1
                    else:
                        price_ranges['5000+'] += 1
                except (ValueError, TypeError):
                    pass
            
            return {
                'categories': categories,
                'brands': brands,
                'price_ranges': price_ranges,
                'total_views': len(history)
            }
            
        except Exception as e:
            logger.error(f"分析用户 {user_id} 偏好失败: {e}")
            return {}
    
    def get_recently_viewed_products(self, user_id: str, days: int = 7) -> List[str]:
        """
        获取用户最近浏览的商品ID列表
        Args:
            user_id: 用户ID
            days: 最近几天
        Returns:
            商品ID列表
        """
        try:
            history_key = f"user_history:{user_id}"
            
            # 计算时间范围
            end_time = time.time()
            start_time = end_time - (days * 24 * 3600)
            
            # 获取时间范围内的记录
            records = self.client.zrangebyscore(
                history_key, start_time, end_time, withscores=True
            )
            
            product_ids = []
            seen_products = set()  # 去重
            
            for record_json, score in records:
                try:
                    record_data = json.loads(record_json)
                    product_id = record_data.get('product_id')
                    
                    if product_id and product_id not in seen_products:
                        product_ids.append(product_id)
                        seen_products.add(product_id)
                        
                except json.JSONDecodeError:
                    continue
            
            return product_ids
            
        except Exception as e:
            logger.error(f"获取用户 {user_id} 最近浏览商品失败: {e}")
            return []
    
    def clear_user_history(self, user_id: str) -> bool:
        """
        清空用户浏览历史
        Args:
            user_id: 用户ID
        Returns:
            是否成功
        """
        try:
            history_key = f"user_history:{user_id}"
            self.client.delete(history_key)
            
            logger.info(f"用户 {user_id} 浏览历史清空成功")
            return True
            
        except Exception as e:
            logger.error(f"清空用户 {user_id} 浏览历史失败: {e}")
            return False
    
    def get_popular_products(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """
        获取热门商品统计（基于浏览次数）
        Args:
            days: 统计最近几天
            limit: 返回数量
        Returns:
            热门商品列表
        """
        try:
            # 获取所有用户行为key
            user_keys = self.client.keys("user_history:*")
            
            product_views = {}  # {product_id: count}
            
            # 计算时间范围
            end_time = time.time()
            start_time = end_time - (days * 24 * 3600)
            
            for key in user_keys:
                try:
                    # 获取时间范围内的记录
                    records = self.client.zrangebyscore(
                        key, start_time, end_time
                    )
                    
                    for record_json in records:
                        try:
                            record_data = json.loads(record_json)
                            product_id = record_data.get('product_id')
                            
                            if product_id:
                                product_views[product_id] = product_views.get(product_id, 0) + 1
                                
                        except json.JSONDecodeError:
                            continue
                            
                except Exception as e:
                    logger.error(f"分析用户行为key {key} 失败: {e}")
                    continue
            
            # 按浏览次数排序
            popular_products = sorted(
                product_views.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:limit]
            
            return [
                {'product_id': product_id, 'view_count': count}
                for product_id, count in popular_products
            ]
            
        except Exception as e:
            logger.error(f"获取热门商品统计失败: {e}")
            return []
    
    def get_behavior_stats(self) -> Dict:
        """获取用户行为统计信息"""
        try:
            user_keys = self.client.keys("user_history:*")
            total_users = len(user_keys)
            
            total_views = 0
            for key in user_keys:
                try:
                    count = self.client.zcard(key)
                    total_views += count
                except Exception:
                    continue
            
            return {
                'total_users': total_users,
                'total_views': total_views,
                'avg_views_per_user': total_views / total_users if total_users > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"获取用户行为统计失败: {e}")
            return {}


# 单例模式
_behavior_redis_manager = None

def get_behavior_redis_manager():
    """获取用户行为Redis管理器单例"""
    global _behavior_redis_manager
    if _behavior_redis_manager is None:
        _behavior_redis_manager = UserBehaviorRedisManager()
    return _behavior_redis_manager

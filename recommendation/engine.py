"""
智能推荐引擎
包含内容匹配和协同过滤算法，结合LLM进行推荐决策
"""
import logging
import numpy as np
from typing import List, Dict, Tuple, Optional
import json
from collections import defaultdict, Counter
from datetime import datetime

from django.db.models import Q
from products.models import Product
from user_behavior.redis import get_behavior_redis_manager
from cache_management.redis import get_redis_manager
from openai import OpenAI
import os

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """推荐引擎核心类"""
    
    def __init__(self):
        """初始化推荐引擎"""
        self.behavior_manager = get_behavior_redis_manager()
        self.cache_manager = get_redis_manager()
        
        # 初始化OpenAI客户端（阿里云兼容）
        self.llm_client = OpenAI(
            api_key="sk-5e387f862dd94499955b83ffe78c722c",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
    
    def content_based_recommend(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        基于内容的推荐算法
        根据用户浏览历史中的商品特征，推荐相似商品
        """
        try:
            # 获取用户偏好分析
            preferences = self.behavior_manager.get_user_preferences(user_id)
            
            if not preferences or preferences.get('total_views', 0) == 0:
                # 如果没有历史数据，返回热门商品
                return self._get_hot_products(limit)
            
            # 获取用户偏好的类别和品牌
            preferred_categories = preferences.get('categories', {})
            preferred_brands = preferences.get('brands', {})
            
            # 构建查询条件
            query = Q()
            
            # 根据偏好类别加权
            if preferred_categories:
                top_categories = sorted(preferred_categories.items(), 
                                      key=lambda x: x[1], reverse=True)[:3]
                category_names = [cat[0] for cat in top_categories]
                query |= Q(category__in=category_names)
            
            # 根据偏好品牌加权
            if preferred_brands:
                top_brands = sorted(preferred_brands.items(), 
                                  key=lambda x: x[1], reverse=True)[:3]
                brand_names = [brand[0] for brand in top_brands]
                query |= Q(brand__in=brand_names)
            
            # 获取候选商品（排除已浏览的）
            viewed_products = self.behavior_manager.get_recently_viewed_products(user_id, days=30)
            
            if query:
                candidates = Product.objects.filter(query).exclude(
                    product_id__in=viewed_products
                )[:limit * 2]  # 获取更多候选商品进行筛选
            else:
                candidates = Product.objects.exclude(
                    product_id__in=viewed_products
                )[:limit * 2]
            
            # 计算商品得分
            scored_products = []
            for product in candidates:
                score = self._calculate_content_score(product, preferences)
                
                product_data = {
                    'product_id': product.product_id,
                    'name': product.name,
                    'price': float(product.price),
                    'category': product.category,
                    'brand': product.brand,
                    'description': product.description or '',
                    'score': score,
                    'reason': self._generate_recommendation_reason(product, preferences)
                }
                scored_products.append(product_data)
            
            # 按得分排序并返回
            scored_products.sort(key=lambda x: x['score'], reverse=True)
            return scored_products[:limit]
            
        except Exception as e:
            logger.error(f"内容推荐失败: {e}")
            return self._get_hot_products(limit)
    
    def collaborative_filtering_recommend(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        协同过滤推荐算法 - 改进版
        基于用户行为相似性进行推荐
        """
        try:
            # 获取用户浏览历史
            user_history = self.behavior_manager.get_recently_viewed_products(user_id, days=30)
            
            if len(user_history) < 2:
                # 历史数据不足，使用内容推荐
                return self.content_based_recommend(user_id, limit)
            
            # 寻找相似用户
            similar_users = self._find_similar_users(user_id, user_history)
            
            if not similar_users:
                return self.content_based_recommend(user_id, limit)
            
            # 获取相似用户喜欢的商品，考虑时间衰减和频次
            recommended_products = defaultdict(float)
            
            for similar_user_id, similarity in similar_users[:8]:  # 取前8个相似用户
                similar_user_history = self.behavior_manager.get_recently_viewed_products(
                    similar_user_id, days=30
                )
                
                # 获取该用户的详细浏览记录（包括时间和频次）
                from user_behavior.models import UserBehavior
                from django.utils import timezone
                from datetime import timedelta
                
                recent_behaviors = UserBehavior.objects.filter(
                    user_id=similar_user_id,
                    viewed_at__gte=timezone.now() - timedelta(days=30)
                ).values('product__product_id', 'viewed_at')
                
                # 统计每个商品的浏览频次和最近浏览时间
                product_stats = defaultdict(lambda: {'count': 0, 'last_viewed': None})
                for behavior in recent_behaviors:
                    product_id = behavior['product__product_id']
                    if product_id not in user_history:  # 只推荐用户未浏览过的商品
                        product_stats[product_id]['count'] += 1
                        if (product_stats[product_id]['last_viewed'] is None or 
                            behavior['viewed_at'] > product_stats[product_id]['last_viewed']):
                            product_stats[product_id]['last_viewed'] = behavior['viewed_at']
                
                # 计算推荐分数
                for product_id, stats in product_stats.items():
                    # 基础相似度分数
                    base_score = similarity
                    
                    # 浏览频次加权（最多额外50%）
                    frequency_weight = min(stats['count'] / 5, 0.5)
                    
                    # 时间衰减加权（越新的浏览记录权重越高）
                    if stats['last_viewed']:
                        days_ago = (timezone.now() - stats['last_viewed']).days
                        time_weight = max(0.1, 1 - (days_ago / 30))  # 30天内线性衰减
                    else:
                        time_weight = 0.1
                    
                    # 最终分数
                    final_score = base_score * (1 + frequency_weight) * time_weight
                    recommended_products[product_id] += final_score
            
            # 获取推荐商品的详细信息并添加额外特征
            recommendations = []
            for product_id, score in sorted(recommended_products.items(), 
                                          key=lambda x: x[1], reverse=True)[:limit * 2]:  # 先获取更多候选
                try:
                    product = Product.objects.get(product_id=product_id)
                    
                    # 计算商品的流行度加权
                    from user_behavior.models import UserBehavior
                    popularity = UserBehavior.objects.filter(
                        product=product,
                        viewed_at__gte=timezone.now() - timedelta(days=7)
                    ).count()
                    
                    # 流行度权重（避免过度推荐冷门商品）
                    popularity_weight = min(popularity / 100, 0.3) + 0.7  # 0.7-1.0之间
                    
                    # 最终分数
                    final_score = score * popularity_weight
                    
                    # 生成个性化推荐理由
                    similar_user_count = len([u for u, s in similar_users if 
                                            product_id in self.behavior_manager.get_recently_viewed_products(u, days=30)])
                    
                    reason = f'{similar_user_count}位兴趣相似的用户都浏览过这款{product.category}商品'
                    if product.is_hot:
                        reason += '，而且是热门商品'
                    
                    product_data = {
                        'product_id': product.product_id,
                        'name': product.name,
                        'price': float(product.price),
                        'category': product.category,
                        'brand': product.brand,
                        'description': product.description or '',
                        'score': final_score,
                        'reason': reason,
                        'similar_user_count': similar_user_count,
                        'popularity': popularity
                    }
                    recommendations.append(product_data)
                except Product.DoesNotExist:
                    continue
            
            # 按最终分数排序并返回指定数量
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"协同过滤推荐失败: {e}")
            return self.content_based_recommend(user_id, limit)
    
    def hybrid_recommend(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        混合推荐算法
        结合内容推荐和协同过滤，并使用LLM进行最终决策
        """
        try:
            # 获取两种推荐结果
            content_recs = self.content_based_recommend(user_id, limit // 2 + 2)
            collab_recs = self.collaborative_filtering_recommend(user_id, limit // 2 + 2)
            
            # 合并推荐结果，去重
            all_recommendations = {}
            
            # 内容推荐权重0.6
            for rec in content_recs:
                product_id = rec['product_id']
                rec['final_score'] = rec['score'] * 0.6
                rec['source'] = 'content'
                all_recommendations[product_id] = rec
            
            # 协同过滤权重0.4，如果商品已存在则合并分数
            for rec in collab_recs:
                product_id = rec['product_id']
                if product_id in all_recommendations:
                    all_recommendations[product_id]['final_score'] += rec['score'] * 0.4
                    all_recommendations[product_id]['source'] = 'hybrid'
                else:
                    rec['final_score'] = rec['score'] * 0.4
                    rec['source'] = 'collaborative'
                    all_recommendations[product_id] = rec
            
            # 按最终得分排序
            sorted_recs = sorted(all_recommendations.values(), 
                               key=lambda x: x['final_score'], reverse=True)
            
            # 使用LLM优化推荐列表
            optimized_recs = self._llm_optimize_recommendations(
                user_id, sorted_recs[:limit * 2]
            )
            
            return optimized_recs[:limit]
            
        except Exception as e:
            logger.error(f"混合推荐失败: {e}")
            return self.content_based_recommend(user_id, limit)
    
    def _calculate_content_score(self, product: Product, preferences: Dict) -> float:
        """计算商品内容相似度得分"""
        score = 0.0
        
        # 类别匹配得分
        categories = preferences.get('categories', {})
        if product.category in categories:
            score += categories[product.category] * 0.4
        
        # 品牌匹配得分
        brands = preferences.get('brands', {})
        if product.brand in brands:
            score += brands[product.brand] * 0.3
        
        # 价格区间匹配得分
        price_ranges = preferences.get('price_ranges', {})
        price = float(product.price)
        
        for price_range, count in price_ranges.items():
            if self._price_in_range(price, price_range):
                score += count * 0.2
                break
        
        # 热门程度加分
        if product.is_hot:
            score += 0.1
        
        return score
    
    def _price_in_range(self, price: float, price_range: str) -> bool:
        """判断价格是否在指定区间"""
        if price_range == '0-500':
            return price < 500
        elif price_range == '500-1000':
            return 500 <= price < 1000
        elif price_range == '1000-2000':
            return 1000 <= price < 2000
        elif price_range == '2000-5000':
            return 2000 <= price < 5000
        elif price_range == '5000+':
            return price >= 5000
        return False
    
    def _find_similar_users(self, user_id: str, user_history: List[str]) -> List[Tuple[str, float]]:
        """寻找相似用户 - 改进的协同过滤算法"""
        try:
            from django.db.models import Q
            from user_behavior.models import UserBehavior
            from collections import defaultdict
            import math
            
            # 获取所有浏览过相同商品的用户
            similar_behaviors = UserBehavior.objects.filter(
                product__product_id__in=user_history
            ).exclude(user_id=user_id).values('user_id', 'product__product_id')
            
            # 构建用户-商品矩阵
            user_items = defaultdict(set)
            for behavior in similar_behaviors:
                user_items[behavior['user_id']].add(behavior['product__product_id'])
            
            # 计算用户相似度（使用余弦相似度）
            current_user_set = set(user_history)
            similar_users = []
            
            for other_user_id, other_user_items in user_items.items():
                # 计算交集和并集
                intersection = len(current_user_set & other_user_items)
                union = len(current_user_set | other_user_items)
                
                if union == 0 or intersection < 2:  # 至少要有2个共同商品
                    continue
                
                # 使用Jaccard相似度
                jaccard_similarity = intersection / union
                
                # 也可以使用余弦相似度
                cosine_similarity = intersection / (math.sqrt(len(current_user_set)) * math.sqrt(len(other_user_items)))
                
                # 综合相似度（权重可调）
                final_similarity = 0.6 * jaccard_similarity + 0.4 * cosine_similarity
                
                # 根据共同商品数量给予额外权重
                common_items_bonus = min(intersection / 10, 0.2)  # 最多额外20%
                final_similarity += common_items_bonus
                
                if final_similarity > 0.1:  # 相似度阈值
                    similar_users.append((other_user_id, final_similarity))
            
            # 按相似度排序并返回Top N
            similar_users.sort(key=lambda x: x[1], reverse=True)
            return similar_users[:10]  # 返回前10个最相似用户
            
        except Exception as e:
            logger.error(f"查找相似用户失败: {e}")
            return []
    
    def _llm_optimize_recommendations(self, user_id: str, recommendations: List[Dict]) -> List[Dict]:
        """使用LLM优化推荐结果"""
        try:
            # 获取用户偏好信息
            preferences = self.behavior_manager.get_user_preferences(user_id)
            
            # 构造提示词
            prompt = self._build_llm_prompt(preferences, recommendations)
            
            # 调用LLM
            response = self.llm_client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {"role": "system", "content": "你是一个专业的商品推荐专家，能够根据用户偏好优化推荐列表。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # 解析LLM响应，重新排序推荐列表
            llm_advice = response.choices[0].message.content
            
            # 简化处理，实际可以让LLM返回JSON格式的排序结果
            logger.info(f"LLM推荐建议: {llm_advice}")
            
            return recommendations  # 这里简化返回原列表，实际可根据LLM建议调整
            
        except Exception as e:
            logger.error(f"LLM优化推荐失败: {e}")
            return recommendations
    
    def _build_llm_prompt(self, preferences: Dict, recommendations: List[Dict]) -> str:
        """构建LLM提示词"""
        prompt = f"""
        请帮我优化以下商品推荐列表。

        用户偏好分析：
        - 偏好类别：{preferences.get('categories', {})}
        - 偏好品牌：{preferences.get('brands', {})}
        - 价格区间偏好：{preferences.get('price_ranges', {})}

        当前推荐商品列表：
        """
        
        for i, rec in enumerate(recommendations[:5], 1):
            prompt += f"""
        {i}. {rec['name']} - {rec['category']} - {rec['brand']} - {rec['price']}元
           推荐理由：{rec.get('reason', '暂无')}
           得分：{rec.get('final_score', rec.get('score', 0))}
        """
        
        prompt += """
        
        请分析这些推荐是否合理，并提供优化建议。考虑因素包括：
        1. 与用户偏好的匹配度
        2. 商品之间的多样性
        3. 价格分布的合理性
        4. 推荐理由的说服力
        
        请简要说明你的分析和建议。
        """
        
        return prompt
    
    def _generate_recommendation_reason(self, product: Product, preferences: Dict) -> str:
        """生成推荐理由"""
        reasons = []
        
        categories = preferences.get('categories', {})
        if product.category in categories:
            reasons.append(f"您经常浏览{product.category}类商品")
        
        brands = preferences.get('brands', {})
        if product.brand in brands:
            reasons.append(f"您对{product.brand}品牌感兴趣")
        
        if product.is_hot:
            reasons.append("这是热门商品")
        
        if not reasons:
            reasons.append("为您推荐的精选商品")
        
        return "；".join(reasons)
    
    def _get_hot_products(self, limit: int) -> List[Dict]:
        """获取热门商品作为兜底推荐"""
        try:
            hot_products = Product.objects.filter(is_hot=True)[:limit]
            
            recommendations = []
            for product in hot_products:
                product_data = {
                    'product_id': product.product_id,
                    'name': product.name,
                    'price': float(product.price),
                    'category': product.category,
                    'brand': product.brand,
                    'description': product.description or '',
                    'score': 1.0,
                    'reason': '热门推荐商品'
                }
                recommendations.append(product_data)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"获取热门商品失败: {e}")
            return []


# 单例模式
_recommendation_engine = None

def get_recommendation_engine():
    """获取推荐引擎单例"""
    global _recommendation_engine
    if _recommendation_engine is None:
        _recommendation_engine = RecommendationEngine()
    return _recommendation_engine

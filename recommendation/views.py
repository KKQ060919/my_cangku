from django.shortcuts import render

"""
推荐系统视图
提供智能推荐相关的RESTful接口
"""
import logging
import os
from typing import List, Dict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI

from .engine import get_recommendation_engine
from .redis import get_recommendation_redis_manager

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class RecommendationsAPIView(APIView):
    """商品推荐API"""
    
    def __init__(self):
        super().__init__()
        self.engine = get_recommendation_engine()
        self.redis_manager = get_recommendation_redis_manager()
    
    def get(self, request):
        """获取用户推荐商品 - GET请求"""
        try:
            user_id = request.GET.get('user_id')
            algorithm = request.GET.get('algorithm', 'hybrid')  # content, collaborative, hybrid
            limit = int(request.GET.get('limit', 10))
            
            if not user_id:
                return Response({
                    "code": 0,
                    "message": "缺少用户ID"
                })
            
            return self._get_recommendations(user_id, algorithm, limit)
            
        except Exception as e:
            logger.error(f"获取推荐失败: {e}")
            return Response({
                "code": 0,
                "message": f"获取推荐失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """获取用户推荐商品 - POST请求，前端使用"""
        try:
            user_id = request.data.get('user_id')
            recommendation_type = request.data.get('recommendation_type', 'hybrid')
            limit = int(request.data.get('limit', 10))
            category = request.data.get('category')
            
            if not user_id:
                return Response({
                    "success": False,
                    "error": "缺少用户ID"
                })
            
            # 映射前端的推荐类型到后端算法
            algorithm_map = {
                'content': 'content',
                'collaborative': 'collaborative', 
                'hybrid': 'hybrid'
            }
            algorithm = algorithm_map.get(recommendation_type, 'hybrid')
            
            recommendations = self._get_recommendations_internal(user_id, algorithm, limit, category)
            
            return Response({
                "success": True,
                "recommendations": recommendations,
                "user_id": user_id,
                "recommendation_type": recommendation_type,
                "count": len(recommendations)
            })
            
        except Exception as e:
            logger.error(f"获取推荐失败: {e}")
            return Response({
                "success": False,
                "error": f"获取推荐失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_recommendations(self, user_id, algorithm, limit):
        """内部推荐获取方法 - 用于GET请求"""
        # 先检查缓存
        cached_recommendations = self.redis_manager.get_user_recommendations(user_id)
        if cached_recommendations:
            return Response({
                "code": 1,
                "message": "获取推荐成功（来自缓存）",
                "data": {
                    "user_id": user_id,
                    "algorithm": algorithm,
                    "recommendations": cached_recommendations['recommendations'][:limit],
                    "generated_at": cached_recommendations['generated_at'],
                    "from_cache": True
                }
            })
        
        # 根据算法类型生成推荐
        if algorithm == 'content':
            recommendations = self.engine.content_based_recommend(user_id, limit)
        elif algorithm == 'collaborative':
            recommendations = self.engine.collaborative_filtering_recommend(user_id, limit)
        else:  # hybrid
            recommendations = self.engine.hybrid_recommend(user_id, limit)
        
        # 缓存推荐结果
        self.redis_manager.cache_user_recommendations(user_id, recommendations)
        
        return Response({
            "code": 1,
            "message": "获取推荐成功",
            "data": {
                "user_id": user_id,
                "algorithm": algorithm,
                "recommendations": recommendations,
                "count": len(recommendations),
                "from_cache": False
            }
        })
    
    def _get_recommendations_internal(self, user_id, algorithm, limit, category=None):
        """内部推荐获取方法 - 用于POST请求"""
        # 根据算法类型生成推荐
        if algorithm == 'content':
            recommendations = self.engine.content_based_recommend(user_id, limit)
        elif algorithm == 'collaborative':
            recommendations = self.engine.collaborative_filtering_recommend(user_id, limit)
        else:  # hybrid
            recommendations = self.engine.hybrid_recommend(user_id, limit)
        
        # 如果指定了类别，进行过滤
        if category:
            recommendations = [rec for rec in recommendations if rec.get('category') == category]
        
        # 缓存推荐结果
        self.redis_manager.cache_user_recommendations(user_id, recommendations)
        
        return recommendations


@method_decorator(csrf_exempt, name='dispatch')
class QAWithRecommendationAPIView(APIView):
    """问答+推荐API - 结合LLM的智能推荐"""
    
    def __init__(self):
        super().__init__()
        self.engine = get_recommendation_engine()
        self.redis_manager = get_recommendation_redis_manager()
        
        # 初始化OpenAI客户端
        self.llm_client = OpenAI(
            api_key="sk-5e387f862dd94499955b83ffe78c722c",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
    
    def post(self, request):
        """基于问题的智能推荐"""
        try:
            user_id = request.data.get('user_id')
            question = request.data.get('question')
            
            if not user_id or not question:
                return Response({
                    "code": 0,
                    "message": "缺少用户ID或问题"
                })
            
            # 获取用户推荐商品
            recommendations = self.engine.hybrid_recommend(user_id, 8)
            
            # 构造包含推荐商品的提示词
            prompt = self._build_qa_prompt(question, recommendations)
            
            # 调用LLM生成回答
            response = self.llm_client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {"role": "system", "content": "你是一个专业的购物顾问，能够根据商品信息为用户提供购买建议。回答要专业、友好且实用。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            
            # 保存对话记录
            recommendation_ids = [rec['product_id'] for rec in recommendations]
            self.redis_manager.save_conversation(user_id, question, answer, recommendation_ids)
            
            return Response({
                "code": 1,
                "message": "回答生成成功",
                "data": {
                    "question": question,
                    "answer": answer,
                    "recommendations": recommendations[:5],  # 返回前5个推荐
                    "user_id": user_id
                }
            })
            
        except Exception as e:
            logger.error(f"问答推荐失败: {e}")
            return Response({
                "code": 0,
                "message": f"处理请求时发生错误: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _build_qa_prompt(self, question: str, recommendations: List[Dict]) -> str:
        """构建问答提示词"""
        prompt = f"""
        用户问题：{question}

        可推荐的商品信息：
        """
        
        for i, rec in enumerate(recommendations[:5], 1):
            prompt += f"""
        {i}. {rec['name']}
           - 类别：{rec['category']}
           - 品牌：{rec['brand']} 
           - 价格：{rec['price']}元
           - 推荐理由：{rec.get('reason', '暂无')}
           - 描述：{rec.get('description', '暂无')[:100]}...
        """
        
        prompt += """
        
        请基于用户的问题和上述商品信息，提供专业的购买建议。要求：
        1. 直接回答用户的问题
        2. 结合商品特点给出具体建议
        3. 可以推荐1-3款最合适的商品
        4. 说明推荐理由
        5. 回答要简洁明了，不超过300字
        """
        
        return prompt


@method_decorator(csrf_exempt, name='dispatch')
class RecommendationClickAPIView(APIView):
    """推荐点击统计API"""
    
    def __init__(self):
        super().__init__()
        self.redis_manager = get_recommendation_redis_manager()
    
    def post(self, request):
        """记录推荐商品点击"""
        try:
            user_id = request.data.get('user_id')
            product_id = request.data.get('product_id')
            
            if not user_id or not product_id:
                return Response({
                    "code": 0,
                    "message": "缺少用户ID或商品ID"
                })
            
            success = self.redis_manager.increment_recommendation_click(user_id, product_id)
            
            if success:
                return Response({
                    "code": 1,
                    "message": "点击记录成功"
                })
            else:
                return Response({
                    "code": 0,
                    "message": "记录失败"
                })
                
        except Exception as e:
            logger.error(f"记录推荐点击失败: {e}")
            return Response({
                "code": 0,
                "message": f"记录失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class ConversationHistoryAPIView(APIView):
    """对话历史API"""
    
    def __init__(self):
        super().__init__()
        self.redis_manager = get_recommendation_redis_manager()
    
    def get(self, request, user_id):
        """获取用户对话历史"""
        try:
            limit = int(request.GET.get('limit', 10))
            
            history = self.redis_manager.get_conversation_history(user_id, limit)
            
            return Response({
                "code": 1,
                "message": "获取对话历史成功",
                "data": {
                    "user_id": user_id,
                    "conversations": history,
                    "count": len(history)
                }
            })
            
        except Exception as e:
            logger.error(f"获取对话历史失败: {e}")
            return Response({
                "code": 0,
                "message": f"获取失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class RecommendationFeedbackAPIView(APIView):
    """推荐反馈API"""
    
    def __init__(self):
        super().__init__()
        self.redis_manager = get_recommendation_redis_manager()
    
    def post(self, request):
        """记录用户对推荐的反馈"""
        try:
            user_id = request.data.get('user_id')
            product_id = request.data.get('product_id') 
            feedback_type = request.data.get('feedback_type')  # interested, not_interested
            product_info = request.data.get('product_info', {})
            
            if not all([user_id, product_id, feedback_type]):
                return Response({
                    "code": 0,
                    "message": "缺少必要参数"
                })
            
            if feedback_type not in ['interested', 'not_interested']:
                return Response({
                    "code": 0,
                    "message": "无效的反馈类型"
                })
            
            # 记录反馈到Redis
            success = self.redis_manager.record_recommendation_feedback(
                user_id, product_id, feedback_type, product_info
            )
            
            if success:
                return Response({
                    "code": 1,
                    "message": "反馈记录成功",
                    "data": {
                        "user_id": user_id,
                        "product_id": product_id,
                        "feedback_type": feedback_type
                    }
                })
            else:
                return Response({
                    "code": 0,
                    "message": "记录失败"
                })
                
        except Exception as e:
            logger.error(f"记录推荐反馈失败: {e}")
            return Response({
                "code": 0,
                "message": f"记录失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class RecommendationStatsAPIView(APIView):
    """推荐统计API"""
    
    def __init__(self):
        super().__init__()
        self.redis_manager = get_recommendation_redis_manager()
    
    def get(self, request):
        """获取推荐系统统计信息"""
        try:
            user_id = request.GET.get('user_id')
            stats = self.redis_manager.get_recommendation_stats()
            top_clicked = self.redis_manager.get_top_clicked_products(10)
            
            # 如果指定了用户ID，获取用户特定的统计
            if user_id:
                user_stats = self.redis_manager.get_user_recommendation_stats(user_id)
                stats.update(user_stats)
            
            return Response({
                "success": True,
                "code": 1,
                "message": "获取统计信息成功",
                "stats": stats,
                "data": {
                    "system_stats": stats,
                    "top_clicked_products": top_clicked
                }
            })
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return Response({
                "success": False,
                "code": 0,
                "message": f"获取失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

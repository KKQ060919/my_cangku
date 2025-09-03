from django.shortcuts import render

"""
RAG检索增强生成视图
提供基于商品知识库的问答API
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .RAG封装 import get_rag_system

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class RAGQuestionAPIView(APIView):
    """RAG问答API"""
    
    def __init__(self):
        super().__init__()
        self.rag_system = get_rag_system()
    
    def post(self, request):
        """处理用户问题并返回RAG答案"""
        try:
            question = request.data.get('question')
            user_id = request.data.get('user_id', 'anonymous')
            session_id = request.data.get('session_id', user_id)
            include_products = request.data.get('include_products', False)
            
            if not question:
                return Response({
                    "success": False,
                    "error": "请输入问题",
                    "code": 0,
                    "message": "请输入问题"
                })
            
            # 记录开始时间
            import time
            start_time = time.time()
            
            # 使用RAG系统回答问题
            answer = self.rag_system.ask_question(question, user_id)
            
            # 计算响应时间
            response_time = int((time.time() - start_time) * 1000)
            
            # 模拟相关商品推荐（如果请求需要）
            related_products = []
            if include_products:
                # 这里可以基于问题内容推荐相关商品
                # 暂时使用模拟数据
                related_products = [
                    {
                        "id": 1,
                        "name": "示例商品",
                        "price": "299.00",
                        "category": "数码产品"
                    }
                ]
            
            return Response({
                "success": True,
                "answer": answer,
                "confidence": 0.85,  # 模拟置信度
                "sources": ["商品知识库", "用户评价"],
                "related_products": related_products,
                "response_time": response_time,
                "code": 1,
                "message": "回答生成成功",
                "data": {
                    "question": question,
                    "answer": answer,
                    "user_id": user_id
                }
            })
            
        except Exception as e:
            logger.error(f"RAG问答失败: {e}")
            return Response({
                "success": False,
                "error": f"处理问题时发生错误: {str(e)}",
                "code": 0,
                "message": f"处理问题时发生错误: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class BuildVectorStoreAPIView(APIView):
    """构建向量数据库API"""
    
    def __init__(self):
        super().__init__()
        self.rag_system = get_rag_system()
    
    def post(self, request):
        """构建或重建向量数据库"""
        try:
            # 构建向量数据库
            self.rag_system.build_vector_store()
            
            return Response({
                "code": 1,
                "message": "向量数据库构建成功"
            })
            
        except Exception as e:
            logger.error(f"构建向量数据库失败: {e}")
            return Response({
                "code": 0,
                "message": f"构建失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class ConversationHistoryAPIView(APIView):
    """对话历史API"""
    
    def __init__(self):
        super().__init__()
        self.rag_system = get_rag_system()
    
    def get(self, request, user_id):
        """获取用户对话历史"""
        try:
            limit = int(request.GET.get('limit', 10))
            
            history = self.rag_system.get_conversation_history(user_id, limit)
            
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
class RAGStatsAPIView(APIView):
    """RAG系统统计API"""
    
    def __init__(self):
        super().__init__()
        self.rag_system = get_rag_system()
    
    def get(self, request):
        """获取RAG系统统计信息"""
        try:
            stats = self.rag_system.get_cache_stats()
            
            return Response({
                "success": True,
                "stats": stats,
                "code": 1,
                "message": "获取统计信息成功",
                "data": stats
            })
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return Response({
                "code": 0,
                "message": f"获取失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class ClearCacheAPIView(APIView):
    """清空缓存API"""
    
    def __init__(self):
        super().__init__()
        self.rag_system = get_rag_system()
    
    def delete(self, request):
        """清空问答缓存"""
        try:
            self.rag_system.clear_cache()
            
            return Response({
                "code": 1,
                "message": "缓存清理成功"
            })
            
        except Exception as e:
            logger.error(f"清理缓存失败: {e}")
            return Response({
                "code": 0,
                "message": f"清理失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class PopularQuestionsAPIView(APIView):
    """热门问题API - 前端SmartQA组件使用"""
    
    def __init__(self):
        super().__init__()
        self.rag_system = get_rag_system()
    
    def get(self, request):
        """获取热门问题列表"""
        try:
            # 模拟热门问题数据（实际项目中可以从Redis或数据库获取）
            popular_questions = [
                {
                    "id": 1,
                    "question": "如何选择适合的笔记本电脑？",
                    "count": 156,
                    "category": "电脑数码"
                },
                {
                    "id": 2, 
                    "question": "哪款手机拍照效果最好？",
                    "count": 134,
                    "category": "手机通讯"
                },
                {
                    "id": 3,
                    "question": "运动鞋什么品牌质量好？", 
                    "count": 98,
                    "category": "运动户外"
                },
                {
                    "id": 4,
                    "question": "护肤品敏感肌肤如何选择？",
                    "count": 87,
                    "category": "美妆个护"
                },
                {
                    "id": 5,
                    "question": "家用电器节能产品推荐？",
                    "count": 76,
                    "category": "家用电器"
                }
            ]
            
            return Response({
                "success": True,
                "questions": [
                    {"text": q["question"], "count": q["count"]} 
                    for q in popular_questions
                ],
                "code": 1,
                "message": "获取热门问题成功",
                "data": {
                    "questions": popular_questions,
                    "count": len(popular_questions)
                }
            })
            
        except Exception as e:
            logger.error(f"获取热门问题失败: {e}")
            return Response({
                "code": 0,
                "message": f"获取失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class FeedbackAPIView(APIView):
    """用户反馈API"""
    
    def __init__(self):
        super().__init__()
        self.rag_system = get_rag_system()
    
    def post(self, request):
        """处理用户反馈"""
        try:
            question = request.data.get('question', '')
            answer = request.data.get('answer', '')
            feedback_type = request.data.get('feedback_type', '')
            session_id = request.data.get('session_id', 'anonymous')
            user_id = request.data.get('user_id', session_id)
            
            if not feedback_type:
                return Response({
                    "success": False,
                    "error": "反馈类型不能为空",
                    "code": 0,
                    "message": "反馈类型不能为空"
                })
            
            # 保存反馈到Redis
            feedback_key = f"feedback:{session_id}:{int(__import__('time').time())}"
            feedback_data = {
                'question': question,
                'answer': answer,
                'feedback_type': feedback_type,
                'user_id': user_id,
                'session_id': session_id,
                'timestamp': __import__('datetime').datetime.now().isoformat()
            }
            
            # 将反馈数据保存到Redis
            import json
            self.rag_system.redis_client.set(
                feedback_key, 
                json.dumps(feedback_data, ensure_ascii=False),
                ex=7*24*3600  # 7天过期
            )
            
            # 统计反馈数据
            feedback_stats_key = f"feedback_stats:{feedback_type}"
            self.rag_system.redis_client.incr(feedback_stats_key)
            self.rag_system.redis_client.expire(feedback_stats_key, 30*24*3600)  # 30天过期
            
            return Response({
                "success": True,
                "message": "反馈已记录",
                "code": 1,
                "data": {
                    "feedback_type": feedback_type,
                    "session_id": session_id
                }
            })
            
        except Exception as e:
            logger.error(f"处理反馈失败: {e}")
            return Response({
                "success": False,
                "error": f"处理反馈时发生错误: {str(e)}",
                "code": 0,
                "message": f"处理反馈时发生错误: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
from django.shortcuts import render

"""
用户行为记录视图
提供用户浏览行为记录和查询的RESTful接口
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from products.models import Product
from .models import UserBehavior
from .redis import get_behavior_redis_manager

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class RecordBehaviorAPIView(APIView):
    """记录用户行为API"""
    
    def __init__(self):
        super().__init__()
        self.redis_manager = get_behavior_redis_manager()
    
    def post(self, request):
        """记录用户浏览行为"""
        try:
            user_id = request.data.get('user_id')
            product_id = request.data.get('product_id')
            
            if not user_id or not product_id:
                return Response({
                    "code": 0,
                    "message": "缺少用户ID或商品ID"
                })
            
            # 获取商品信息
            try:
                product = Product.objects.get(product_id=product_id)
            except Product.DoesNotExist:
                return Response({
                    "code": 0,
                    "message": "商品不存在"
                })
            
            # 构造商品信息
            product_info = {
                'name': product.name,
                'price': float(product.price),
                'category': product.category,
                'brand': product.brand,
                'is_hot': product.is_hot
            }
            
            # 记录到Redis
            success = self.redis_manager.record_product_view(
                user_id, product_id, product_info
            )
            
            if success:
                # 同时记录到数据库（可选）
                try:
                    UserBehavior.objects.create(
                        user_id=user_id,
                        product=product,
                        action_type='view'
                    )
                except Exception as e:
                    logger.warning(f"数据库记录失败，但Redis记录成功: {e}")
                
                return Response({
                    "code": 1,
                    "message": "用户行为记录成功",
                    "data": {
                        "user_id": user_id,
                        "product_id": product_id,
                        "product_name": product.name
                    }
                })
            else:
                return Response({
                    "code": 0,
                    "message": "记录失败"
                })
                
        except Exception as e:
            logger.error(f"记录用户行为失败: {e}")
            return Response({
                "code": 0,
                "message": f"记录失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class UserHistoryAPIView(APIView):
    """用户浏览历史API"""
    
    def __init__(self):
        super().__init__()
        self.redis_manager = get_behavior_redis_manager()
    
    def get(self, request, user_id):
        """获取用户浏览历史"""
        try:
            limit = int(request.GET.get('limit', 10))
            
            # 从Redis获取浏览历史
            history = self.redis_manager.get_user_history(user_id, limit)
            
            return Response({
                "code": 1,
                "message": "获取用户历史成功",
                "data": {
                    "user_id": user_id,
                    "history": history,
                    "count": len(history)
                }
            })
            
        except Exception as e:
            logger.error(f"获取用户历史失败: {e}")
            return Response({
                "code": 0,
                "message": f"获取失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, user_id):
        """清空用户浏览历史"""
        try:
            success = self.redis_manager.clear_user_history(user_id)
            
            if success:
                return Response({
                    "code": 1,
                    "message": "用户历史清空成功"
                })
            else:
                return Response({
                    "code": 0,
                    "message": "清空失败"
                })
                
        except Exception as e:
            logger.error(f"清空用户历史失败: {e}")
            return Response({
                "code": 0,
                "message": f"清空失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class UserPreferencesAPIView(APIView):
    """用户偏好分析API"""
    
    def __init__(self):
        super().__init__()
        self.redis_manager = get_behavior_redis_manager()
    
    def get(self, request, user_id):
        """获取用户偏好分析"""
        try:
            preferences = self.redis_manager.get_user_preferences(user_id)
            
            return Response({
                "code": 1,
                "message": "获取用户偏好成功",
                "data": {
                    "user_id": user_id,
                    "preferences": preferences
                }
            })
            
        except Exception as e:
            logger.error(f"获取用户偏好失败: {e}")
            return Response({
                "code": 0,
                "message": f"获取失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class PopularProductsAPIView(APIView):
    """热门商品统计API"""
    
    def __init__(self):
        super().__init__()
        self.redis_manager = get_behavior_redis_manager()
    
    def get(self, request):
        """获取热门商品统计"""
        try:
            days = int(request.GET.get('days', 7))
            limit = int(request.GET.get('limit', 10))
            
            popular_products = self.redis_manager.get_popular_products(days, limit)
            
            # 补充商品详细信息
            enriched_products = []
            for item in popular_products:
                try:
                    product = Product.objects.get(product_id=item['product_id'])
                    enriched_item = {
                        'product_id': item['product_id'],
                        'view_count': item['view_count'],
                        'name': product.name,
                        'price': float(product.price),
                        'category': product.category,
                        'brand': product.brand
                    }
                    enriched_products.append(enriched_item)
                except Product.DoesNotExist:
                    continue
            
            return Response({
                "code": 1,
                "message": "获取热门商品成功",
                "data": {
                    "days": days,
                    "products": enriched_products,
                    "count": len(enriched_products)
                }
            })
            
        except Exception as e:
            logger.error(f"获取热门商品失败: {e}")
            return Response({
                "code": 0,
                "message": f"获取失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class BehaviorStatsAPIView(APIView):
    """用户行为统计API"""
    
    def __init__(self):
        super().__init__()
        self.redis_manager = get_behavior_redis_manager()
    
    def get(self, request):
        """获取用户行为统计"""
        try:
            # 获取用户ID和时间周期参数
            user_id = request.GET.get('user_id')
            period = request.GET.get('period', '7d')
            
            # 从Redis获取基础统计
            redis_stats = self.redis_manager.get_behavior_stats()
            
            # 从数据库获取更详细的统计
            from django.db.models import Count, Avg
            from django.utils import timezone
            from datetime import timedelta
            
            # 计算时间范围
            days = int(period.rstrip('d'))
            start_date = timezone.now() - timedelta(days=days)
            
            queryset = UserBehavior.objects.filter(viewed_at__gte=start_date)
            if user_id:
                queryset = queryset.filter(user_id=user_id)
                
            # 计算详细统计
            total_views = queryset.count()
            unique_products = queryset.values('product').distinct().count()
            
            stats = {
                'total_views': total_views,
                'unique_products': unique_products,
                'avg_session_duration': 0,  # 暂时设为0，后续可以实现
                'conversion_rate': 0.0,     # 暂时设为0，后续可以实现
                'total_users': redis_stats.get('total_users', 0),
                'avg_views_per_user': redis_stats.get('avg_views_per_user', 0)
            }
            
            return Response({
                "success": True,
                "code": 1,
                "message": "获取统计信息成功",
                "stats": stats
            })
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return Response({
                "code": 0,
                "message": f"获取失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class BehaviorRecordsAPIView(APIView):
    """用户行为记录列表API - 前端UserBehavior组件使用"""
    
    def __init__(self):
        super().__init__()
        self.redis_manager = get_behavior_redis_manager()
    
    def get(self, request):
        """获取用户行为记录"""
        try:
            user_id = request.GET.get('user_id')
            limit = int(request.GET.get('limit', 100))
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            
            # 从数据库查询行为记录
            from django.utils import timezone
            from datetime import datetime
            
            queryset = UserBehavior.objects.all()
            
            if user_id:
                queryset = queryset.filter(user_id=user_id)
                
            if start_date:
                queryset = queryset.filter(viewed_at__gte=start_date)
                
            if end_date:
                queryset = queryset.filter(viewed_at__lte=end_date)
            
            # 按时间倒序排列，获取最新的记录
            records = queryset.order_by('-viewed_at')[:limit]
            
            # 格式化记录数据
            formatted_records = []
            for record in records:
                try:
                    formatted_records.append({
                        'id': record.id,
                        'user_id': record.user_id,
                        'product_name': record.product.name if record.product else '未知商品',
                        'product_id': record.product.id if record.product else None,
                        'product_price': float(record.product.price) if record.product else 0.0,
                        'viewed_at': record.viewed_at.isoformat(),
                        'behavior_type': '浏览',
                        'duration': 0,  # 暂时设为0
                        'source': 'web'  # 暂时设为web
                    })
                except Exception as e:
                    logger.warning(f"格式化记录失败: {e}")
                    continue
            
            return Response({
                "success": True,
                "code": 1,
                "message": "获取行为记录成功",
                "records": formatted_records,
                "total": len(formatted_records)
            })
            
        except Exception as e:
            logger.error(f"获取行为记录失败: {e}")
            return Response({
                "success": False,
                "code": 0,
                "message": f"获取失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class BehaviorTrendAPIView(APIView):
    """用户行为趋势数据API - 用于图表显示"""
    
    def get(self, request):
        """获取行为趋势数据"""
        try:
            user_id = request.GET.get('user_id')
            period = request.GET.get('period', '7d')
            
            # 计算时间范围
            from django.utils import timezone
            from datetime import timedelta, datetime
            from django.db.models import Count
            
            days = int(period.rstrip('d'))
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            # 查询行为数据
            queryset = UserBehavior.objects.filter(viewed_at__gte=start_date, viewed_at__lte=end_date)
            if user_id:
                queryset = queryset.filter(user_id=user_id)
            
            # 按日期分组统计
            trend_data = []
            for i in range(days):
                date = start_date + timedelta(days=i)
                next_date = date + timedelta(days=1)
                
                daily_count = queryset.filter(
                    viewed_at__gte=date,
                    viewed_at__lt=next_date
                ).count()
                
                trend_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'views': daily_count
                })
            
            # 商品类别统计
            category_stats = []
            categories = queryset.values('product__category').annotate(
                count=Count('id')
            ).order_by('-count')[:5]
            
            for cat in categories:
                category_name = cat['product__category'] or '未分类'
                category_stats.append({
                    'category': category_name,
                    'value': cat['count']
                })
            
            return Response({
                "success": True,
                "code": 1,
                "message": "获取趋势数据成功",
                "data": {
                    'trend': trend_data,
                    'categories': category_stats
                }
            })
            
        except Exception as e:
            logger.error(f"获取趋势数据失败: {e}")
            return Response({
                "success": False,
                "code": 0,
                "message": f"获取失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
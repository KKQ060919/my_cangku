"""
系统监控视图
提供系统指标、数据库统计和日志查询的RESTful接口
"""
import logging
import psutil
from datetime import datetime
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# 导入模型用于数据库统计
from products.models import Product
from user_behavior.models import UserBehavior

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class SystemMetricsAPIView(APIView):
    """系统指标API - 获取CPU、内存、磁盘使用情况"""
    
    def get(self, request):
        """获取系统指标"""
        try:
            # 获取系统指标
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 模拟活跃用户数（可根据实际需求修改）
            active_users = 150  # 可以从Redis或数据库获取实际数据
            
            metrics = {
                'cpu_usage': round(cpu_usage, 2),
                'memory_usage': round(memory.percent, 2),
                'memory_total': round(memory.total / (1024**3), 2),  # GB
                'memory_used': round(memory.used / (1024**3), 2),   # GB
                'disk_usage': round(disk.percent, 2),
                'disk_total': round(disk.total / (1024**3), 2),     # GB
                'disk_used': round(disk.used / (1024**3), 2),       # GB
                'active_users': active_users,
                'timestamp': datetime.now().isoformat()
            }
            
            return Response({
                "success": True,
                "message": "获取系统指标成功",
                "metrics": metrics
            })
            
        except Exception as e:
            logger.error(f"获取系统指标失败: {e}")
            return Response({
                "success": False,
                "message": f"获取系统指标失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class DatabaseStatsAPIView(APIView):
    """数据库统计API - 获取各表记录数和数据库大小"""
    
    def get(self, request):
        """获取数据库统计信息"""
        try:
            with connection.cursor() as cursor:
                # 获取各表记录数
                table_stats = {}
                
                # 产品表
                table_stats['products'] = Product.objects.count()
                
                # 用户行为表
                table_stats['user_behaviors'] = UserBehavior.objects.count()
                
                # 获取数据库大小（MySQL查询）
                try:
                    cursor.execute("""
                        SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS database_size_mb 
                        FROM information_schema.tables 
                        WHERE table_schema = DATABASE()
                    """)
                    result = cursor.fetchone()
                    db_size_mb = result[0] if result and result[0] else 0
                except Exception as e:
                    logger.warning(f"无法获取数据库大小: {e}")
                    db_size_mb = 0
                
                stats = {
                    'table_counts': table_stats,
                    'database_size_mb': db_size_mb,
                    'total_records': sum(table_stats.values()),
                    'timestamp': datetime.now().isoformat()
                }
                
                return Response({
                    "success": True,
                    "message": "获取数据库统计成功",
                    "stats": stats
                })
                
        except Exception as e:
            logger.error(f"获取数据库统计失败: {e}")
            return Response({
                "success": False,
                "message": f"获取数据库统计失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class SystemLogsAPIView(APIView):
    """系统日志API - 获取系统日志"""
    
    def get(self, request):
        """获取系统日志"""
        try:
            limit = int(request.GET.get('limit', 100))
            
            # 模拟日志数据（实际项目中可以从日志文件或数据库获取）
            logs = []
            log_levels = ['INFO', 'WARNING', 'ERROR', 'DEBUG']
            components = ['Cache', 'Database', 'API', 'RAG', 'Recommendation']
            messages = [
                'Cache hit for product',
                'Database connection established',
                'API request processed',
                'Vector store updated',
                'Recommendation generated',
                'User behavior recorded',
                'System metrics collected'
            ]
            
            # 生成模拟日志
            from datetime import datetime, timedelta
            import random
            
            for i in range(min(limit, 50)):  # 限制最多50条模拟日志
                log_time = datetime.now() - timedelta(minutes=random.randint(0, 1440))
                logs.append({
                    'timestamp': log_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'level': random.choice(log_levels),
                    'component': random.choice(components),
                    'message': f"{random.choice(messages)} - {random.randint(100, 999)}",
                    'id': i + 1
                })
            
            # 按时间倒序排列
            logs.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return Response({
                "success": True,
                "message": "获取系统日志成功",
                "logs": logs,
                "count": len(logs)
            })
            
        except Exception as e:
            logger.error(f"获取系统日志失败: {e}")
            return Response({
                "success": False,
                "message": f"获取系统日志失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
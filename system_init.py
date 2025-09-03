"""
系统初始化脚本
负责缓存预热、向量数据库构建等初始化工作
"""
import os
import django
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DAY11.settings')
django.setup()

import logging
from datetime import datetime

from cache_management.redis import get_redis_manager
from user_behavior.redis import get_behavior_redis_manager
from recommendation.redis import get_recommendation_redis_manager
from rag.RAG封装 import get_rag_system
from products.models import Product

logger = logging.getLogger(__name__)


class SystemInitializer:
    """系统初始化器"""
    
    def __init__(self):
        """初始化各个管理器"""
        self.cache_manager = get_redis_manager()
        self.behavior_manager = get_behavior_redis_manager()
        self.recommendation_manager = get_recommendation_redis_manager()
        self.rag_system = get_rag_system()
    
    def warm_up_cache(self):
        """缓存预热 - 加载热门商品到Redis"""
        print("开始缓存预热...")
        
        try:
            # 获取所有热门商品
            hot_products = Product.objects.filter(is_hot=True)
            
            if not hot_products.exists():
                print("未找到热门商品，预热所有商品前20个...")
                hot_products = Product.objects.all()[:20]
            
            products_data = []
            for product in hot_products:
                product_data = {
                    'product_id': product.product_id,
                    'name': product.name,
                    'price': float(product.price),
                    'category': product.category,
                    'brand': product.brand,
                    'specifications': product.specifications,
                    'description': product.description or "",
                    'stock': product.stock,
                    'is_hot': product.is_hot,
                    'updated_at': product.updated_at.isoformat()
                }
                products_data.append(product_data)
            
            # 批量缓存商品
            success_count = self.cache_manager.cache_products_batch(products_data)
            
            print(f"✓ 缓存预热完成: 成功缓存 {success_count} 个商品")
            return True
            
        except Exception as e:
            print(f"✗ 缓存预热失败: {e}")
            return False
    
    def build_vector_store(self):
        """构建向量数据库"""
        print("开始构建向量数据库...")
        
        try:
            self.rag_system.build_vector_store()
            print("✓ 向量数据库构建完成")
            return True
            
        except Exception as e:
            print(f"✗ 向量数据库构建失败: {e}")
            return False
    
    def create_sample_user_behavior(self):
        """创建示例用户行为数据"""
        print("创建示例用户行为数据...")
        
        try:
            # 获取前5个商品
            products = Product.objects.all()[:5]
            
            if not products:
                print("未找到商品，跳过用户行为数据创建")
                return True
            
            # 为测试用户创建一些浏览记录
            test_users = ['user_001', 'user_002', 'user_003']
            
            success_count = 0
            for user_id in test_users:
                for i, product in enumerate(products):
                    if i >= 3:  # 每个用户浏览前3个商品
                        break
                    
                    product_info = {
                        'name': product.name,
                        'price': float(product.price),
                        'category': product.category,
                        'brand': product.brand,
                        'is_hot': product.is_hot
                    }
                    
                    success = self.behavior_manager.record_product_view(
                        user_id, product.product_id, product_info
                    )
                    
                    if success:
                        success_count += 1
            
            print(f"✓ 示例用户行为数据创建完成: {success_count} 条记录")
            return True
            
        except Exception as e:
            print(f"✗ 创建用户行为数据失败: {e}")
            return False
    
    def test_connections(self):
        """测试所有连接"""
        print("测试系统连接...")
        
        connections = {
            "商品缓存Redis": self._test_cache_redis,
            "用户行为Redis": self._test_behavior_redis, 
            "推荐系统Redis": self._test_recommendation_redis,
            "数据库连接": self._test_database,
        }
        
        results = {}
        for name, test_func in connections.items():
            try:
                test_func()
                results[name] = "✓ 连接正常"
            except Exception as e:
                results[name] = f"✗ 连接失败: {e}"
        
        print("\n连接测试结果:")
        for name, result in results.items():
            print(f"  {name}: {result}")
        
        return all("✓" in result for result in results.values())
    
    def _test_cache_redis(self):
        """测试商品缓存Redis连接"""
        self.cache_manager.get_cache_stats()
    
    def _test_behavior_redis(self):
        """测试用户行为Redis连接"""
        self.behavior_manager.get_behavior_stats()
    
    def _test_recommendation_redis(self):
        """测试推荐系统Redis连接"""
        self.recommendation_manager.get_recommendation_stats()
    
    def _test_database(self):
        """测试数据库连接"""
        Product.objects.count()
    
    def initialize_system(self):
        """完整的系统初始化"""
        print("="*60)
        print(f"开始系统初始化 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        steps = [
            ("连接测试", self.test_connections),
            ("缓存预热", self.warm_up_cache),
            ("向量数据库构建", self.build_vector_store),
            ("创建示例数据", self.create_sample_user_behavior),
        ]
        
        results = []
        for step_name, step_func in steps:
            print(f"\n{step_name}:")
            success = step_func()
            results.append(success)
            
            if not success:
                print(f"⚠️ {step_name} 失败，但继续执行下一步...")
        
        print("\n" + "="*60)
        success_count = sum(results)
        total_count = len(results)
        
        if success_count == total_count:
            print("🎉 系统初始化完成! 所有步骤都成功执行")
        else:
            print(f"⚠️ 系统初始化完成，但有 {total_count - success_count} 个步骤失败")
        
        print("="*60)
        
        return success_count == total_count
    
    def get_system_status(self):
        """获取系统状态"""
        try:
            status = {
                "cache_stats": self.cache_manager.get_cache_stats(),
                "behavior_stats": self.behavior_manager.get_behavior_stats(),
                "recommendation_stats": self.recommendation_manager.get_recommendation_stats(),
                "rag_stats": self.rag_system.get_cache_stats(),
                "product_count": Product.objects.count(),
                "hot_products_count": Product.objects.filter(is_hot=True).count(),
            }
            
            return status
            
        except Exception as e:
            print(f"获取系统状态失败: {e}")
            return {}


def main():
    """主函数"""
    initializer = SystemInitializer()
    
    # 如果有命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "warmup":
            initializer.warm_up_cache()
        elif command == "build":
            initializer.build_vector_store()
        elif command == "test":
            initializer.test_connections()
        elif command == "status":
            status = initializer.get_system_status()
            print("系统状态:")
            for key, value in status.items():
                print(f"  {key}: {value}")
        else:
            print("可用命令: warmup, build, test, status")
    else:
        # 完整初始化
        initializer.initialize_system()


if __name__ == "__main__":
    main()

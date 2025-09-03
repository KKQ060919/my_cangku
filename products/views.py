from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product
import json

# Create your views here.

@csrf_exempt
@require_http_methods(["GET"])
def product_list(request):
    """获取商品列表"""
    try:
        # 获取查询参数
        category = request.GET.get('category', '')
        brand = request.GET.get('brand', '')
        search = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 12))
        sort_by = request.GET.get('sort_by', 'name')  # name, price, updated_at
        
        # 构建查询
        products = Product.objects.all()
        
        # 类别筛选
        if category:
            products = products.filter(category=category)
            
        # 品牌筛选
        if brand:
            products = products.filter(brand=brand)
            
        # 搜索筛选
        if search:
            products = products.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(brand__icontains=search)
            )
        
        # 排序
        if sort_by == 'price':
            products = products.order_by('price')
        elif sort_by == 'price_desc':
            products = products.order_by('-price')
        elif sort_by == 'updated_at':
            products = products.order_by('-updated_at')
        else:
            products = products.order_by('name')
        
        # 分页
        paginator = Paginator(products, page_size)
        page_obj = paginator.get_page(page)
        
        # 序列化数据
        products_data = []
        for product in page_obj:
            products_data.append({
                'product_id': product.product_id,
                'name': product.name,
                'price': float(product.price),
                'category': product.category,
                'brand': product.brand,
                'specifications': product.specifications,
                'description': product.description,
                'stock': product.stock,
                'is_hot': product.is_hot,
                'updated_at': product.updated_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'products': products_data,
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'page_size': page_size
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取商品列表失败: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def product_detail(request, product_id):
    """获取商品详情"""
    try:
        product = Product.objects.get(product_id=product_id)
        
        product_data = {
            'product_id': product.product_id,
            'name': product.name,
            'price': float(product.price),
            'category': product.category,
            'brand': product.brand,
            'specifications': product.specifications,
            'description': product.description,
            'stock': product.stock,
            'is_hot': product.is_hot,
            'updated_at': product.updated_at.isoformat()
        }
        
        return JsonResponse({
            'success': True,
            'product': product_data
        })
        
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '商品不存在'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取商品详情失败: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_categories(request):
    """获取所有商品类别"""
    try:
        categories = Product.objects.values_list('category', flat=True).distinct().order_by('category')
        return JsonResponse({
            'success': True,
            'categories': list(categories)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取商品类别失败: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_brands(request):
    """获取所有品牌"""
    try:
        brands = Product.objects.values_list('brand', flat=True).distinct().order_by('brand')
        return JsonResponse({
            'success': True,
            'brands': list(brands)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取品牌列表失败: {str(e)}'
        }, status=500)

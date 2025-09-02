import json
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .redis import ChatRedisManager
from .Agents封装 import StockAdvisor

# 初始化组件
chat_manager = ChatRedisManager()
stock_advisor = StockAdvisor()

@csrf_exempt
@require_http_methods(["POST"])
def analyze_stock(request):
    """股票分析API接口"""
    try:
        data = json.loads(request.body)
        stock_name = data.get('stock_name', '')
        investment_amount = data.get('investment_amount', '')
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not stock_name or not investment_amount:
            return JsonResponse({'error': '请提供股票名称和投资金额'}, status=400)
        
        # 使用封装类分析股票
        analysis_result = stock_advisor.analyze_stock(stock_name, investment_amount)
        
        # 保存对话记录到Redis
        chat_manager.save_conversation(
            session_id=session_id,
            user_message=f"分析{stock_name}股票，投资{investment_amount}",
            bot_response=analysis_result,
            stock_info={"股票": stock_name, "金额": investment_amount}
        )
        
        return JsonResponse({
            'success': True,
            'session_id': session_id,
            'analysis': analysis_result,
            'timestamp': chat_manager.get_latest_chat(session_id)['时间戳']
        })
        
    except Exception as e:
        return JsonResponse({'error': f'分析失败: {str(e)}'}, status=500)

@csrf_exempt  
@require_http_methods(["GET"])
def get_chat_history(request):
    """获取对话历史"""
    session_id = request.GET.get('session_id')
    if not session_id:
        return JsonResponse({'error': '缺少session_id'}, status=400)
    
    try:
        history = chat_manager.get_session_history(session_id, 20)
        return JsonResponse({'success': True, 'history': history})
    except Exception as e:
        return JsonResponse({'error': f'获取历史失败: {str(e)}'}, status=500)

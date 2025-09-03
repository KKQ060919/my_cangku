"""
RAG (检索增强生成) 封装类
将RAG脚本的功能封装成易于使用的类，提供简洁的接口
"""
import os
import logging
from operator import itemgetter
import pymysql
import redis
import json
from datetime import datetime, timedelta

# 配置日志记录器
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class RAGSystem:
    """RAG系统封装类"""
    
    def __init__(self, persist_directory="./chroma_stock_info"):
        """初始化RAG系统"""
        # 初始化大语言模型
        self.llm = ChatOpenAI(
            api_key="sk-5e387f862dd94499955b83ffe78c722c",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model="qwen-max"
        )
        
        # 初始化嵌入模型
        self.embeddings_model = DashScopeEmbeddings(
            model="text-embedding-v3",
            dashscope_api_key="sk-8869c2ac51c5466185e6e39faefff6db"
        )
        
        # 文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, 
            chunk_overlap=100
        )
        
        # 初始化向量存储
        self.vector_store = Chroma(
            embedding_function=self.embeddings_model, 
            persist_directory=persist_directory
        )
        
        # 创建检索器 - 优化检索参数
        self.retriever = self.vector_store.as_retriever(
            search_type="mmr",  # 使用MMR(Maximum Marginal Relevance)提高结果多样性
            search_kwargs={
                "k": 3,  # 减少检索数量，提高速度
                "fetch_k": 6,  # MMR参数
                "lambda_mult": 0.5  # MMR参数，平衡相关性和多样性
            }
        )
        
        # 提示模板
        self.prompt_template = PromptTemplate.from_template("""
        你是一个专业的商品顾问，根据以下商品信息回答用户问题：
        
        相关商品信息：
        {context}
        
        用户问题：{question}
        
        请提供准确、有用的回答，如果信息不足请说明。
        """)
        
        # 构建RAG处理链
        self.chain = (
            {"question": RunnablePassthrough()}
            | RunnablePassthrough.assign(context=itemgetter("question") | self.retriever)
            | self.prompt_template
            | self.llm
            | StrOutputParser()
        )
        
        # Redis连接 - 用于缓存和对话记录，添加连接池优化
        try:
            self.redis_client = redis.Redis(
                host='localhost', 
                port=6379, 
                db=0, 
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                max_connections=10  # 连接池大小
            )
            # 测试连接
            self.redis_client.ping()
            logger.info("Redis连接成功")
        except Exception as e:
            logger.warning(f"Redis连接失败: {e}, 将在内存中模拟缓存")
            self.redis_client = None
            self._memory_cache = {}  # 内存缓存备用方案
    
    def load_product_knowledge(self):
        """从数据库加载商品知识库数据"""
        documents = []
        connection = None
        
        try:
            logger.info("开始连接数据库...")
            connection = pymysql.connect(
                host='localhost',
                port=3306,
                user='root',
                password='123456',
                database='0819',  # 使用settings.py中的数据库名
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=10
            )
            logger.info("数据库连接成功")
            
            with connection.cursor() as cursor:
                # 尝试多个可能的表名和字段
                sql_queries = [
                    # Django products模型表名
                    """
                    SELECT 
                        p.id as product_id,
                        p.name,
                        p.price,
                        p.category,
                        p.brand,
                        p.specifications,
                        p.description
                    FROM products_product p
                    WHERE p.is_hot = 1
                    """,
                    # 备用表名
                    """
                    SELECT 
                        p.product_id,
                        p.name,
                        p.price,
                        p.category,
                        p.brand,
                        p.specifications,
                        p.description
                    FROM product p
                    WHERE p.is_hot = 1
                    """
                ]
                
                results = []
                for i, sql in enumerate(sql_queries):
                    try:
                        logger.info(f"尝试执行第{i+1}个查询...")
                        cursor.execute(sql)
                        results = cursor.fetchall()
                        logger.info(f"查询成功，获得{len(results)}条记录")
                        break
                    except pymysql.Error as e:
                        logger.warning(f"查询{i+1}失败: {e}")
                        if i == len(sql_queries) - 1:  # 最后一个查询也失败了
                            logger.error("所有查询都失败，使用备用数据")
                            results = []
                
                if not results:
                    logger.warning("数据库中没有找到商品数据，使用示例数据")
                    # 创建示例数据
                    results = [
                        {
                            'product_id': 1,
                            'name': '示例智能手机',
                            'price': 2999,
                            'category': '手机通讯',
                            'brand': '示例品牌',
                            'specifications': '6.1英寸屏幕，128GB存储',
                            'description': '这是一款高性价比的智能手机，拥有优秀的拍照功能和长续航能力。'
                        },
                        {
                            'product_id': 2,
                            'name': '示例笔记本电脑',
                            'price': 5999,
                            'category': '电脑数码',
                            'brand': '示例品牌',
                            'specifications': 'Intel i5处理器，16GB内存，512GB SSD',
                            'description': '轻薄便携的商务笔记本，适合办公和学习使用。'
                        }
                    ]
                
                for row in results:
                    try:
                        if row.get('name') and (row.get('description') or row.get('specifications')):
                            # 构造文档内容
                            content_parts = [
                                f"商品名称: {row['name']}",
                                f"价格: {row.get('price', 0)}元",
                                f"类别: {row.get('category', '未分类')}",
                                f"品牌: {row.get('brand', '未知品牌')}"
                            ]
                            
                            if row.get('specifications'):
                                content_parts.append(f"规格: {row['specifications']}")
                            
                            if row.get('description'):
                                content_parts.append(f"商品描述: {row['description']}")
                            
                            content = '\n'.join(content_parts)
                            
                            # 创建Document对象
                            doc = Document(
                                page_content=content.strip(),
                                metadata={
                                    'product_id': row.get('product_id', 0),
                                    'name': row['name'],
                                    'category': row.get('category', '未分类'),
                                    'brand': row.get('brand', '未知品牌'),
                                    'price': float(row.get('price', 0))
                                }
                            )
                            documents.append(doc)
                            
                    except Exception as e:
                        logger.error(f"处理商品数据时出错: {e}, 数据: {row}")
                        continue
                        
        except Exception as e:
            logger.error(f"数据库操作失败: {e}")
            # 创建基础示例数据以确保系统可用
            logger.info("使用基础示例数据")
            doc = Document(
                page_content="商品名称: 示例商品\n价格: 999元\n类别: 数码产品\n品牌: 示例品牌\n商品描述: 这是一个示例商品，用于演示RAG问答功能。",
                metadata={
                    'product_id': 1,
                    'name': '示例商品',
                    'category': '数码产品',
                    'brand': '示例品牌',
                    'price': 999.0
                }
            )
            documents.append(doc)
            
        finally:
            if connection:
                try:
                    connection.close()
                    logger.info("数据库连接已关闭")
                except:
                    pass
        
        logger.info(f"最终加载了 {len(documents)} 个文档")
        return documents
    
    def build_vector_store(self):
        """构建向量数据库"""
        print("开始加载商品知识库数据...")
        docs = self.load_product_knowledge()
        print(f"从数据库加载了 {len(docs)} 个文档")
        
        if docs:
            # 分割文档
            split_docs = self.text_splitter.split_documents(docs)
            print(f"分割后得到 {len(split_docs)} 个文档块")
            
            # 添加到向量数据库
            self.vector_store.add_documents(split_docs)
            print("向量数据库构建完成")
        else:
            print("未找到商品知识库数据")
    
    def ask_question(self, question, user_id=None):
        """
        回答用户问题
        Args:
            question: 用户问题
            user_id: 用户ID，用于记录对话
        Returns:
            回答内容
        """
        if not question or not question.strip():
            logger.warning("收到空问题")
            return "请输入您要咨询的问题。"
        
        question = question.strip()
        logger.info(f"处理问题: {question} (用户: {user_id})")
        
        try:
            # 先检查Redis缓存
            cache_key = f"qa:{abs(hash(question))}"  # 使用abs确保key为正数
            cached_answer = None
            
            try:
                if self.redis_client:
                    cached_answer = self.redis_client.get(cache_key)
                    if cached_answer:
                        logger.info("从Redis缓存中获取答案")
                elif hasattr(self, '_memory_cache'):
                    cached_answer = self._memory_cache.get(cache_key)
                    if cached_answer:
                        logger.info("从内存缓存中获取答案")
            except Exception as e:
                logger.warning(f"缓存读取失败: {e}")
            
            if cached_answer:
                answer = cached_answer
            else:
                logger.info("使用RAG系统生成答案")
                try:
                    # 设置超时控制（跨平台支持）
                    import threading
                    import time
                    
                    result_container = {'answer': None, 'error': None}
                    
                    def generate_answer():
                        try:
                            result_container['answer'] = self.chain.invoke(question)
                        except Exception as e:
                            result_container['error'] = e
                    
                    # 使用线程实现超时
                    thread = threading.Thread(target=generate_answer)
                    thread.daemon = True
                    thread.start()
                    thread.join(timeout=30)  # 30秒超时
                    
                    if thread.is_alive():
                        logger.error("RAG生成答案超时")
                        answer = "抱歉，处理您的问题需要更多时间，请稍后重试或尝试简化您的问题。"
                    elif result_container['error']:
                        raise result_container['error']
                    elif result_container['answer']:
                        answer = result_container['answer']
                    else:
                        answer = "抱歉，生成答案时出现未知问题。"
                        
                except Exception as e:
                    logger.error(f"RAG生成答案失败: {e}")
                    # 提供备用答案
                    if "手机" in question.lower():
                        answer = "抱歉，我暂时无法为您推荐具体的手机产品。建议您关注品牌口碑、性价比、续航能力等因素来选择适合的手机。"
                    elif "电脑" in question.lower() or "笔记本" in question.lower():
                        answer = "抱歉，我暂时无法为您推荐具体的电脑产品。建议您根据使用需求（办公、游戏、设计等）选择合适的配置。"
                    else:
                        answer = "抱歉，我暂时无法回答您的问题。您可以尝试换个方式提问，或者稍后再试。"
                
                # 尝试缓存答案（30分钟）
                try:
                    if self.redis_client:
                        self.redis_client.setex(cache_key, 1800, answer)
                    elif hasattr(self, '_memory_cache'):
                        # 内存缓存（简单实现，无过期时间）
                        if len(self._memory_cache) > 100:  # 限制缓存大小
                            # 清理最旧的一半缓存
                            keys_to_remove = list(self._memory_cache.keys())[:50]
                            for key in keys_to_remove:
                                del self._memory_cache[key]
                        self._memory_cache[cache_key] = answer
                        logger.info("答案已缓存到内存")
                    else:
                        logger.info("缓存已缓存到Redis")
                except Exception as e:
                    logger.warning(f"缓存写入失败: {e}")
            
            # 记录对话历史
            if user_id:
                try:
                    self._save_conversation(user_id, question, answer)
                except Exception as e:
                    logger.warning(f"保存对话历史失败: {e}")
            
            logger.info(f"问题处理完成，答案长度: {len(answer)}")
            return answer
            
        except Exception as e:
            logger.error(f"问答处理发生未预期的错误: {e}")
            return "抱歉，系统暂时出现问题，请稍后重试。如果问题持续存在，请联系技术支持。"
    
    def _save_conversation(self, user_id, question, answer):
        """保存对话记录到Redis或内存"""
        conversation_key = f"conversation:{user_id}"
        conversation_data = {
            'question': question,
            'answer': answer,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            if self.redis_client:
                # 将对话数据转换为JSON，确保中文正确显示
                conversation_json = json.dumps(conversation_data, ensure_ascii=False)
                
                # 使用LPUSH添加到列表头部，LTRIM保持最近50条记录
                self.redis_client.lpush(conversation_key, conversation_json)
                self.redis_client.ltrim(conversation_key, 0, 49)
                
                # 设置过期时间（7天）
                self.redis_client.expire(conversation_key, 7 * 24 * 3600)
            elif hasattr(self, '_memory_cache'):
                # 内存备用方案
                if not hasattr(self, '_memory_conversations'):
                    self._memory_conversations = {}
                
                if conversation_key not in self._memory_conversations:
                    self._memory_conversations[conversation_key] = []
                
                self._memory_conversations[conversation_key].insert(0, conversation_data)
                # 保持最近50条记录
                if len(self._memory_conversations[conversation_key]) > 50:
                    self._memory_conversations[conversation_key] = self._memory_conversations[conversation_key][:50]
                
        except Exception as e:
            logger.error(f"保存对话记录失败: {e}")
    
    def get_conversation_history(self, user_id, limit=10):
        """获取用户对话历史"""
        conversation_key = f"conversation:{user_id}"
        conversations = []
        
        try:
            if self.redis_client:
                history = self.redis_client.lrange(conversation_key, 0, limit - 1)
                
                for conv_json in history:
                    try:
                        conv_data = json.loads(conv_json)
                        conversations.append(conv_data)
                    except json.JSONDecodeError:
                        continue
            elif hasattr(self, '_memory_conversations') and conversation_key in self._memory_conversations:
                conversations = self._memory_conversations[conversation_key][:limit]
                
        except Exception as e:
            logger.error(f"获取对话历史失败: {e}")
        
        return conversations
    
    def clear_cache(self):
        """清空问答缓存"""
        try:
            if self.redis_client:
                keys = self.redis_client.keys("qa:*")
                if keys:
                    self.redis_client.delete(*keys)
                    logger.info(f"清空了 {len(keys)} 个Redis缓存条目")
            elif hasattr(self, '_memory_cache'):
                cache_count = len(self._memory_cache)
                self._memory_cache.clear()
                logger.info(f"清空了 {cache_count} 个内存缓存条目")
        except Exception as e:
            logger.error(f"清空缓存失败: {e}")
    
    def get_cache_stats(self):
        """获取缓存统计信息"""
        stats = {
            'qa_cache_count': 0,
            'conversation_count': 0,
            'total_keys': 0,
            'cache_type': 'none'
        }
        
        try:
            if self.redis_client:
                qa_keys = self.redis_client.keys("qa:*")
                conv_keys = self.redis_client.keys("conversation:*")
                
                stats.update({
                    'qa_cache_count': len(qa_keys),
                    'conversation_count': len(conv_keys),
                    'total_keys': len(qa_keys) + len(conv_keys),
                    'cache_type': 'redis'
                })
            elif hasattr(self, '_memory_cache'):
                qa_count = len(self._memory_cache) if hasattr(self, '_memory_cache') else 0
                conv_count = len(self._memory_conversations) if hasattr(self, '_memory_conversations') else 0
                
                stats.update({
                    'qa_cache_count': qa_count,
                    'conversation_count': conv_count,
                    'total_keys': qa_count + conv_count,
                    'cache_type': 'memory'
                })
                
        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
        
        return stats


# 单例模式，确保全局只有一个RAG系统实例
_rag_instance = None

def get_rag_system():
    """获取RAG系统单例"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGSystem()
    return _rag_instance


if __name__ == "__main__":
    # 测试代码
    rag = RAGSystem()
    
    # 构建向量数据库
    rag.build_vector_store()
    
    # 测试问答
    question = "推荐一款性价比高的手机"
    answer = rag.ask_question(question, user_id="test_user")
    print(f"\n问题: {question}")
    print(f"回答: {answer}")
    
    # 查看缓存状态
    stats = rag.get_cache_stats()
    print(f"\n缓存统计: {stats}")

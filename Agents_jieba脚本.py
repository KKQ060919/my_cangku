# 导入必要的库
import pymysql  # MySQL数据库连接
import jieba, jieba.analyse  # jieba中文分词库：用于文本分词和关键词提取
from langchain_chroma import Chroma  # RAG组件：向量数据库，用于存储和检索文档向量
from langchain_community.embeddings import DashScopeEmbeddings  # RAG组件：文本嵌入模型，将文本转换为向量
from langchain_core.documents import Document  # RAG组件：文档对象，包含内容和元数据
from langchain_core.prompts import ChatPromptTemplate  # LangChain提示模板
from langchain_openai import ChatOpenAI  # OpenAI兼容的LLM接口
from langchain_text_splitters import RecursiveCharacterTextSplitter  # RAG组件：文本分割器，将长文档切分为小块

class 智能医疗顾问_jieba增强版:
    def __init__(self):
        # jieba分词优化：添加医疗领域专业词汇到自定义词典，提高分词准确性
        # 格式：(词汇, 词频权重)，权重越高越容易被识别为完整词汇
        [jieba.add_word(w[0], w[1]) for w in [("心血管", 20000), ("高血压", 20000), ("糖尿病", 20000), 
                                              ("感染", 15000), ("诊断", 15000), ("治疗", 15000), ("症状", 15000)]]
        
        # 初始化大语言模型：使用阿里云通义千问模型
        self.llm = ChatOpenAI(api_key="sk-5e387f862dd94499955b83ffe78c722c", 
                             base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", 
                             model="qwen-max")
        
        # RAG检索器初始化：构建医疗知识检索系统
        # 1. 使用Chroma向量数据库存储医疗文档向量
        # 2. 使用DashScope嵌入模型将文本转换为向量表示  
        # 3. 配置检索参数：每次检索返回最相似的5个文档片段
        self.retriever = Chroma(
            embedding_function=DashScopeEmbeddings(model="text-embedding-v3", 
                                                 dashscope_api_key="sk-8869c2ac51c5466185e6e39faefff6db"), 
            persist_directory="./chroma_medical_info"  # 向量数据库持久化目录
        ).as_retriever(search_kwargs={"k": 5})  # 检索Top-5最相关文档
    
    def _处理文本(self, text):
        """
        jieba文本处理工具：对输入文本进行分词和关键词提取
        
        Args:
            text: 待处理的文本内容
            
        Returns:
            dict: 包含分词结果和关键词的字典
                - "词": jieba分词结果列表
                - "关键词": TF-IDF算法提取的关键词列表(Top3)
        """
        text = str(text or "").strip()  # 文本预处理：转换为字符串并去除首尾空格
        print("工具一执行结束")
        
        if text:
            return {
                "词": list(jieba.cut(text)),  # jieba精确模式分词：将文本切分为词汇列表
                "关键词": jieba.analyse.extract_tags(text, topK=3)  # jieba关键词提取：基于TF-IDF算法提取前3个关键词
            }
        else:
            return {"词": [], "关键词": []}  # 空文本返回空列表

    
    def _获取医疗信息(self, query):
        """
        RAG知识检索工具：从医疗知识库中检索相关信息
        
        工作流程：
        1. 使用jieba提取查询文本的关键词
        2. 将关键词转换为向量并在向量数据库中进行相似度搜索
        3. 返回最相关的医疗文档内容
        
        Args:
            query: 用户的医疗咨询问题
            
        Returns:
            str: 检索到的相关医疗信息，多个文档用换行符分隔
        """
        # 步骤1：jieba关键词提取 - 从查询中提取核心关键词以提高检索精度
        关键词 = " ".join(self._处理文本(query)["关键词"])
        print("工具二执行结束")
        
        # 步骤2：RAG向量检索 - 在医疗知识向量库中检索最相关的文档
        # retriever.invoke() 执行以下流程：
        # a) 将关键词/查询文本通过嵌入模型转换为向量
        # b) 在Chroma向量数据库中进行相似度搜索
        # c) 返回Top-K个最相似的文档片段
        检索文档 = self.retriever.invoke(关键词 or query)  # 优先使用关键词，如无关键词则使用原查询
        
        # 步骤3：合并检索结果 - 将多个文档的内容合并为一个字符串
        return "\n".join([doc.page_content for doc in 检索文档])

    def 智能医疗咨询(self, 问题描述, 严重程度="一般"):
        """
        RAG增强的智能医疗咨询服务：结合知识检索和大语言模型提供医疗建议
        
        工作流程（RAG模式）：
        1. 接收用户医疗问题
        2. 使用RAG检索相关医疗知识（结合jieba分词优化）
        3. 将检索到的知识和用户问题一起发送给LLM
        4. 生成个性化的医疗建议
        
        Args:
            问题描述: 用户的医疗咨询问题
            严重程度: 症状严重程度（默认"一般"）
            
        Returns:
            str: LLM生成的医疗建议，包含原因分析、建议和就医指导
        """
        # RAG检索阶段：获取相关医疗知识作为上下文
        相关信息 = self._获取医疗信息(问题描述)  # 调用RAG检索系统
        
        # 构建结构化提示模板：将用户问题和检索到的知识结合
        prompt = ChatPromptTemplate.from_template("""
        你是专业的医疗助手，基于以下信息提供建议：
        
        🏥 问题：{问题描述}
        ⚡ 严重程度：{严重程度}
        📚 相关医疗信息：{相关信息}
        
        请提供：
        1. 可能的原因分析
        2. 初步建议和注意事项
        3. 是否需要就医建议
        
        ⚠️ 本建议仅供参考，请及时就医获取专业诊断！
        """)
        print("工具三执行结束")
        
        # LLM生成阶段：基于检索到的知识和用户问题生成回答
        return self.llm.invoke(prompt.format(
            问题描述=问题描述, 
            严重程度=严重程度, 
            相关信息=相关信息  # RAG检索的医疗知识作为上下文
        )).content
    
    def 初始化数据库(self):
        """
        RAG向量数据库初始化：构建医疗知识向量检索系统
        
        工作流程：
        1. 从MySQL医疗问答表中读取原始数据
        2. 使用jieba对医疗文本进行分词处理，提高中文搜索效果
        3. 将处理后的文档转换为向量并存储到Chroma向量数据库
        4. 建立RAG检索索引，支持后续的相似度搜索
        
        注意：此方法只需运行一次来构建向量数据库
        """
        # 步骤1：连接MySQL数据库，读取医疗问答数据
        conn = pymysql.connect(host='localhost', port=3306, user='root', password='123456', database='0902')
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, question, answer, category, subcategory, keywords, difficulty_level, source FROM medical_qa")
            
            # 步骤2：数据预处理 + jieba分词优化
            # 将每条医疗问答转换为Document对象，并使用jieba进行分词处理
            docs = [
                Document(
                    # 使用jieba分词处理医疗文本：问题+答案+关键词+类别信息
                    # 将分词结果用空格连接，便于向量化和检索
                    page_content=" ".join(self._处理文本(f"{row[1]} {row[2]} {row[5]} {row[3]} {row[4]}")["词"]), 
                    
                    # 保存原始元数据，用于检索结果展示和后续处理
                    metadata={
                        'question': row[1],          # 医疗问题
                        'answer': row[2],            # 医疗答案
                        'category': row[3],          # 医疗分类
                        'subcategory': row[4],       # 医疗子分类
                        'keywords': row[5],          # 关键词
                        'difficulty_level': row[6],  # 难度等级
                        'source': row[7]             # 数据来源
                    }
                ) for row in cursor.fetchall()
            ]
        conn.close()
        
        # 步骤3：构建RAG向量数据库
        # 使用Chroma作为向量数据库，DashScope作为嵌入模型
        vector_store = Chroma(
            embedding_function=DashScopeEmbeddings(model="text-embedding-v3", 
                                                 dashscope_api_key="sk-8869c2ac51c5466185e6e39faefff6db"), 
            persist_directory="./chroma_medical_info"  # 向量数据库持久化存储目录
        )
        
        # 步骤4：文档分割 + 向量化存储
        # 使用RecursiveCharacterTextSplitter将长文档切分为合适的块大小（500字符）
        # 然后转换为向量并存储到向量数据库中
        vector_store.add_documents(
            RecursiveCharacterTextSplitter(chunk_size=500).split_documents(docs)  # RAG文档分割器
        )
        
        print(f"医疗数据库初始化完成，加载{len(docs)}条医疗问答")
        print("📊 RAG系统构建完成：jieba分词 + 向量检索 已就绪！")


if __name__ == '__main__':
    # 实例化智能医疗顾问系统
    # 系统集成：jieba中文分词 + RAG向量检索 + LLM生成
    医疗顾问 = 智能医疗顾问_jieba增强版()
    
    # 数据库初始化（仅首次运行需要）
    # 功能：构建医疗知识的向量数据库，支持后续的RAG检索
    # 医疗顾问.初始化数据库()  # 初始化数据库
    
    # RAG + jieba 医疗咨询测试案例
    # 演示完整的智能问答流程：用户提问 → jieba分词 → RAG检索 → LLM生成答案
    print("🏥 智能医疗顾问系统启动")
    print("🔧 技术栈：jieba分词 + RAG向量检索 + 大语言模型")
    print("="*80)
    
    for 问题, 严重程度 in [("什么是高血压", "一般"), ("心脏病的症状有哪些", "轻微"), ("糖尿病如何预防", "一般")]:
        print(f"\n❓ 问题：{问题}")
        print(f"⚡ 严重程度：{严重程度}")
        print("🔍 正在处理：jieba分词 → RAG检索 → LLM生成...")
        print(f"💬 咨询结果：\n{医疗顾问.智能医疗咨询(问题, 严重程度)}\n" + "="*60)

import os
import pymysql
import jieba
import jieba.posseg as pseg
import jieba.analyse
from operator import itemgetter

from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.tools.retriever import create_retriever_tool
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter


class 智能股票顾问_jieba增强版:
    def __init__(self):
        """初始化智能股票顾问 - 现在更聪明了！🧠"""
        print("🎈 正在启动智能股票顾问（jieba增强版）...")
        
        # 🎯 新增：初始化jieba分词
        self._初始化jieba词典()
        
        # 配置大语言模型
        self.llm = ChatOpenAI(
            api_key="sk-5e387f862dd94499955b83ffe78c722c",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model="qwen-max"
        )
        
        # 配置嵌入模型
        self.embeddings = DashScopeEmbeddings(
            model="text-embedding-v3",
            dashscope_api_key="sk-8869c2ac51c5466185e6e39faefff6db"
        )
        
        # 初始化向量存储
        self.vector_store = Chroma(
            embedding_function=self.embeddings, 
            persist_directory="./chroma_stock_info"
        )
        
        # 创建检索器
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
        
        # 创建RAG链
        self._create_rag_chain()
        
        # 创建工具
        self._create_tools()
        
        # 创建Agent
        self._create_agent()
        
        print("✅ 股票顾问启动完成！现在支持智能中文分词！")
    
    def _初始化jieba词典(self):
        """🎯 新增方法：让jieba认识股票专业词汇"""
        print("📚 正在加载股票专业词典...")
        
        # 添加股票相关专业词汇
        股票词汇 = [
            ("苹果公司", 20000, "ORG"),
            ("特斯拉", 20000, "ORG"),
            ("微软公司", 20000, "ORG"),
            ("谷歌", 20000, "ORG"),
            ("阿里巴巴", 20000, "ORG"),
            ("腾讯", 20000, "ORG"),
            ("股价", 15000, "n"),
            ("市值", 15000, "n"),
            ("涨幅", 15000, "n"),
            ("跌幅", 15000, "n"),
            ("收益率", 15000, "n"),
            ("投资组合", 15000, "n"),
            ("风险评估", 15000, "n"),
        ]
        
        for word, freq, tag in 股票词汇:
            jieba.add_word(word, freq=freq, tag=tag)
        
        print(f"✅ 已加载 {len(股票词汇)} 个股票专业词汇")
    
    def _智能分词处理(self, text):
        """🧠 新增方法：智能处理文本"""
        # 分词
        words = list(jieba.cut(text))
        
        # 提取关键词
        keywords = jieba.analyse.extract_tags(text, topK=5)
        
        # 词性标注
        pos_words = list(pseg.cut(text))
        
        return {
            "原文": text,
            "分词结果": words,
            "关键词": keywords,
            "处理后": " ".join(words)
        }
    
    def _create_rag_chain(self):
        """创建RAG处理链 - 现在支持智能分词！"""
        prompt_template = PromptTemplate.from_template("""
        你是一个专业的股票分析助手，根据以下股票信息回答问题：
        
        股票信息：{context}
        问题：{question}
        
        请提供准确、专业的分析，投资有风险，建议仅供参考。
        """)
        
        # 🎯 修改：加入智能查询处理
        def 智能查询处理(query):
            """处理用户查询，提取关键信息"""
            if isinstance(query, str):
                分词结果 = self._智能分词处理(query)
                # 使用关键词进行检索，效果更好
                关键词查询 = " ".join(分词结果["关键词"])
                print(f"🔍 原始查询: {query}")
                print(f"🎯 优化查询: {关键词查询}")
                return 关键词查询
            return query
        
        self.rag_chain = (
            {"question": RunnablePassthrough()}
            | RunnablePassthrough.assign(
                context=lambda x: self.retriever.invoke(智能查询处理(x["question"]))
            )
            | prompt_template
            | self.llm
            | StrOutputParser()
        )
    
    def _create_tools(self):
        """创建工具集 - 现在更智能！"""
        # 工具1：智能股票信息检索
        @tool
        def 智能股票检索(查询内容: str):
            """🎯 使用jieba分词进行智能股票信息检索"""
            分词结果 = self._智能分词处理(查询内容)
            print(f"🔍 检索关键词: {分词结果['关键词']}")
            
            # 使用关键词检索
            关键词查询 = " ".join(分词结果["关键词"])
            documents = self.retriever.invoke(关键词查询)
            
            # 整理结果
            结果 = []
            for doc in documents:
                结果.append(doc.page_content)
            
            return "\n\n".join(结果)
        
        # 工具2：收益计算器（保持不变）
        @tool
        def 收益计算器(投入金额: str):
            """根据投入金额计算不同情景下的年均收益"""
            prompt = ChatPromptTemplate.from_template("""
            你是股票收益计算器，根据投入金额:{投入金额}，计算年均收入：
            
            示例格式：
            投资 {投入金额}:
            🟢 乐观情景(年均+20%): 约XXX
            🟡 中性情景(年均+8%): 约XXX  
            🔴 悲观情景(年均-15%): 约XXX
            """)
            
            chain = prompt | self.llm | StrOutputParser()
            return chain.invoke({"投入金额": 投入金额})
        
        # 工具3：智能深度分析
        @tool  
        def 智能深度分析器(股票名称: str):
            """🧠 对指定股票进行智能深度分析和风险评估"""
            # 先用智能检索获取股票信息
            分词结果 = self._智能分词处理(f"{股票名称} 股票信息 财务数据 行业分析")
            查询关键词 = " ".join(分词结果["关键词"])
            
            print(f"🎯 深度分析查询: {查询关键词}")
            
            stock_info = self.rag_chain.invoke({"question": 查询关键词})
            
            # 深度分析
            analysis_prompt = ChatPromptTemplate.from_template("""
            基于股票信息进行专业分析：
            
            📊 股票信息：{stock_info}
            
            请分析：
            1. 📈 价格趋势（月度和年度变化）  
            2. 🏭 行业前景分析
            3. ⚠️ 风险评估
            4. 💡 投资建议
            
            股票：{股票名称}
            ⚠️ 投资有风险，建议仅供参考
            """)
            
            analysis_chain = analysis_prompt | self.llm | StrOutputParser()
            return analysis_chain.invoke({"stock_info": stock_info, "股票名称": 股票名称})
        
        self.tools = [智能股票检索, 收益计算器, 智能深度分析器]
    
    def _create_agent(self):
        """创建智能Agent"""
        system_prompt = ChatPromptTemplate.from_messages([
            ('system', '''🤖 你是专业的智能股票投资顾问！现在支持中文智能分词！
            
            🛠️ 可用工具：
            1. 智能股票检索：使用jieba分词智能获取股票数据
            2. 收益计算器：计算投资收益预测  
            3. 智能深度分析器：基于分词的专业风险评估
            
            📋 服务流程：
            1. 📊 智能解析用户问题
            2. 🔍 使用关键词精准检索
            3. 💰 计算投资收益预测
            4. 📝 提供综合投资建议
            
            ⚠️ 重要提醒：投资有风险，建议仅供参考！'''),
            ('user', '股票名称:{股票名称}, 投入金额:{投入金额}'),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        agent = create_openai_tools_agent(self.llm, self.tools, system_prompt)
        self.executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True
        )
    
    def 智能分析股票(self, 股票名称, 投入金额):
        """🎯 智能分析指定股票（支持中文分词）"""
        print(f"\n🎈 正在为您智能分析: {股票名称}")
        print(f"💰 投入金额: {投入金额}")
        
        # 使用jieba处理输入
        股票分词 = self._智能分词处理(股票名称)
        print(f"🔍 提取关键词: {股票分词['关键词']}")
        
        result = self.executor.invoke({
            "股票名称": 股票名称, 
            "投入金额": 投入金额
        })
        return result["output"]
    
    def 初始化数据库(self):
        """从MySQL加载数据到向量数据库 - 现在支持智能分词！"""
        print("🔄 正在从数据库加载股票数据（jieba增强版）...")
        
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root', 
            password='123456',
            database='0902',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        documents = []
        
        try:
            with connection.cursor() as cursor:
                sql = """
                SELECT stock_code, stock_name, current_price, one_month_change, 
                       one_year_change, exchange, industry, volume, market_cap, last_updated
                FROM stock_info
                """
                cursor.execute(sql)
                results = cursor.fetchall()
                
                for row in results:
                    # 🎯 原始内容
                    content = f"""
股票代码: {row['stock_code']}
股票名称: {row['stock_name']}  
当前价格: {row['current_price']}
一个月变化: {row['one_month_change']}%
一年变化: {row['one_year_change']}%
交易所: {row['exchange']}
行业: {row['industry']}
成交量: {row['volume']}
市值: {row['market_cap']}
最后更新: {row['last_updated']}
                    """.strip()
                    
                    # 🎯 新增：使用jieba处理内容
                    分词结果 = self._智能分词处理(content)
                    处理后内容 = 分词结果["处理后"]
                    
                    doc = Document(
                        page_content=处理后内容,  # 使用分词后的内容
                        metadata={
                            'stock_code': row['stock_code'],
                            'stock_name': row['stock_name'],
                            'industry': row['industry'],
                            'keywords': 分词结果["关键词"]  # 保存关键词
                        }
                    )
                    documents.append(doc)
                    
        finally:
            connection.close()
        
        # 分割文档并添加到向量数据库
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        split_docs = text_splitter.split_documents(documents)
        
        # 分批添加
        batch_size = 10
        for i in range(0, len(split_docs), batch_size):
            batch = split_docs[i:i + batch_size]
            self.vector_store.add_documents(batch)
            print(f"✅ 已处理第 {i//batch_size + 1} 批，添加了 {len(batch)} 个文档")
        
        print(f"🎉 智能向量数据库构建完成！共处理 {len(documents)} 只股票")


# 🎈 使用示例
if __name__ == '__main__':
    # 创建智能股票顾问（jieba增强版）
    顾问 = 智能股票顾问_jieba增强版()
    
    # 如果需要初始化数据库，取消下面的注释
    # 顾问.初始化数据库()
    
    # 测试智能股票分析
    print("\n🚀 智能股票顾问启动！（现在支持中文分词啦！）")
    print("="*60)
    
    # 测试不同的问法
    测试问题 = [
        ("苹果公司股票", "一万元"),
        ("AAPL", "5000元"),
        ("科技股投资建议", "2万元")
    ]
    
    for 股票, 金额 in 测试问题:
        print(f"\n{'='*60}")
        结果 = 顾问.智能分析股票(股票, 金额)
        print("📊 分析结果：")
        print(结果)
        print("="*60)

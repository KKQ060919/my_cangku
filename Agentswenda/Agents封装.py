import os
import pymysql
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


class StockAdvisor:
    """智能股票投资顾问 - 集成RAG检索和Agent工具的股票分析系统"""
    
    def __init__(self):
        """初始化顾问系统的核心组件"""
        # 初始化大语言模型
        self.llm = self._init_llm()
        
        # 初始化向量数据库
        self.vector_store = self._init_vector_store()
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
        
        # 构建RAG检索链
        self.rag_chain = self._build_rag_chain()
        
        # 创建Agent工具和执行器
        self.tools = self._create_tools()
        self.executor = self._create_agent()
    
    def _init_llm(self):
        """初始化大语言模型配置"""
        return ChatOpenAI(
            api_key="sk-5e387f862dd94499955b83ffe78c722c",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model="qwen-max"
        )
    
    def _init_vector_store(self):
        """初始化向量数据库和嵌入模型"""
        embeddings = DashScopeEmbeddings(
            model="text-embedding-v3",
            dashscope_api_key="sk-8869c2ac51c5466185e6e39faefff6db"
        )
        
        return Chroma(
            embedding_function=embeddings, 
            persist_directory="./chroma_stock_info"
        )
    
    def _build_rag_chain(self):
        """构建RAG检索增强生成链"""
        prompt = PromptTemplate.from_template("""
        你是专业股票分析师，基于以下信息回答问题：
        
        股票信息：{context}
        问题：{question}
        
        请提供专业分析，投资有风险，建议仅供参考。
        """)
        
        return (
            {"question": RunnablePassthrough()}
            | RunnablePassthrough.assign(context=itemgetter("question") | self.retriever)
            | prompt
            | self.llm
            | StrOutputParser()
        )
    
    def _create_tools(self):
        """创建Agent工具集"""
        # 工具1：股票信息检索器
        retriever_tool = create_retriever_tool(
            retriever=self.retriever,
            name="股票信息检索",
            description="检索股票基本信息和数据"
        )
        
        # 工具2：收益计算器
        @tool
        def calculate_returns(investment_amount: str):
            """计算不同情景下的投资收益预测"""
            prompt = ChatPromptTemplate.from_template("""
            你是投资收益计算器，根据投入金额:{investment_amount}，计算年均收益预测：
            
            投资 {investment_amount} 的年化收益预测:
            🟢 乐观情景(年均+20%): 计算后显示结果
            🟡 中性情景(年均+8%): 计算后显示结果  
            🔴 悲观情景(年均-15%): 计算后显示结果
            
            请计算具体金额并格式化显示。
            """)
            
            chain = prompt | self.llm | StrOutputParser()
            return chain.invoke({"investment_amount": investment_amount})
        
        # 工具3：深度分析器
        @tool  
        def deep_analysis(stock_name: str):
            """对股票进行深度分析和风险评估"""
            # 获取股票信息
            stock_info = self.rag_chain.invoke(f"分析{stock_name}股票信息")
            
            # 深度分析提示
            analysis_prompt = ChatPromptTemplate.from_template("""
            股票信息：{stock_info}
            
            深度分析{stock_name}：
            📈 价格趋势分析
            🏭 行业前景评估  
            ⚠️ 风险等级评定
            💡 投资建议总结
            
            ⚠️ 投资有风险，建议仅供参考
            """)
            
            chain = analysis_prompt | self.llm | StrOutputParser()
            return chain.invoke({"stock_info": stock_info, "stock_name": stock_name})
        
        return [retriever_tool, calculate_returns, deep_analysis]
    
    def _create_agent(self):
        """创建智能Agent执行器"""
        system_prompt = ChatPromptTemplate.from_messages([
            ('system', '''🤖 专业股票投资顾问
            
            工具箱：
            1. 股票信息检索 - 获取基础数据
            2. 收益计算器 - 预测投资回报  
            3. 深度分析器 - 风险评估建议
            
            分析流程：信息检索 → 深度分析 → 收益计算 → 综合建议
            ⚠️ 投资有风险，建议仅供参考！'''),
            ('user', '股票:{stock_name}, 投资额:{investment_amount}'),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # 创建Agent和执行器
        agent = create_openai_tools_agent(self.llm, self.tools, system_prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    def analyze_stock(self, stock_name, investment_amount):
        """主要分析接口 - 分析指定股票"""
        result = self.executor.invoke({
            "stock_name": stock_name, 
            "investment_amount": investment_amount
        })
        return result["output"]
    
    def load_stock_data(self):
        """从MySQL数据库加载股票数据到向量数据库"""
        print("🔄 正在从数据库加载股票数据...")
        
        # 数据库连接配置
        connection = pymysql.connect(
            host='localhost', port=3306, user='root', 
            password='123456', database='0902',
            charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
        )
        
        documents = []
        
        try:
            with connection.cursor() as cursor:
                # 查询股票数据
                cursor.execute("""
                SELECT stock_code, stock_name, current_price, one_month_change, 
                       one_year_change, exchange, industry, volume, market_cap, last_updated
                FROM stock_info
                """)
                
                # 转换为文档格式
                for row in cursor.fetchall():
                    content = f"""
股票代码: {row['stock_code']} | 股票名称: {row['stock_name']}  
当前价格: {row['current_price']} | 月涨跌: {row['one_month_change']}%
年涨跌: {row['one_year_change']}% | 交易所: {row['exchange']}
行业: {row['industry']} | 成交量: {row['volume']}
市值: {row['market_cap']} | 更新时间: {row['last_updated']}
                    """.strip()
                    
                    documents.append(Document(
                        page_content=content,
                        metadata={
                            'stock_code': row['stock_code'],
                            'stock_name': row['stock_name'],
                            'industry': row['industry']
                        }
                    ))
                    
        finally:
            connection.close()
        
        # 文档分割和批量添加
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        split_docs = text_splitter.split_documents(documents)
        
        # 分批处理避免API限制
        for i in range(0, len(split_docs), 10):
            batch = split_docs[i:i + 10]
            self.vector_store.add_documents(batch)
            print(f"✅ 已处理批次 {i//10 + 1}，添加 {len(batch)} 个文档")
        
        print(f"🎉 数据加载完成！共处理 {len(documents)} 只股票")


# 使用示例
if __name__ == '__main__':
    # 创建股票顾问实例
    advisor = StockAdvisor()
    
    # 首次使用需要加载数据（取消注释）
    # advisor.load_stock_data()
    
    # 分析股票示例
    print("🚀 智能股票顾问启动！")
    print("="*50)
    
    result = advisor.analyze_stock("苹果", "10000元")
    print("\n📊 分析结果：")
    print(result)

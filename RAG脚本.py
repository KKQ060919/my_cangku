from operator import itemgetter  # 用于获取字典中的特定键值
import pymysql  # MySQL数据库连接器

from langchain_chroma import Chroma  # 向量数据库Chroma的接口
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.output_parsers import StrOutputParser  # 输出解析器
from langchain_core.prompts import PromptTemplate  # 提示模板
from langchain_core.runnables import RunnablePassthrough  # 数据传递组件
from langchain_openai import ChatOpenAI  # OpenAI兼容的大模型接口
from langchain_text_splitters import RecursiveCharacterTextSplitter  # 文本分割器
from langchain_core.documents import Document  # 文档类

# 初始化大语言模型（LLM）
llm = ChatOpenAI(
    api_key="sk-5e387f862dd94499955b83ffe78c722c",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen-max"
)

# 初始化文本嵌入模型
embeddings_model = DashScopeEmbeddings(
    model="text-embedding-v3",
    dashscope_api_key="sk-8869c2ac51c5466185e6e39faefff6db"
)

# 定义文本分割器
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

# 初始化Chroma向量存储
vector_store = Chroma(embedding_function=embeddings_model, persist_directory="./chroma_stock_info")

# 创建检索器
retriever = vector_store.as_retriever(search_kwargs={"k": 5})

# 定义提示模板
prompt_template = PromptTemplate.from_template("""
    你是一个专业的股票分析助手，根据以下股票信息回答问题。请提供准确、专业的分析和建议：
    
    股票信息：
    {context}
    
    问题：{question}
    
    请基于提供的股票数据进行分析，如果涉及投资建议，请提醒这仅供参考，投资有风险。
    """)

# 构建RAG处理链
chain = (
        {"question": RunnablePassthrough()}
        | RunnablePassthrough.assign(context=itemgetter("question") | retriever)
        | prompt_template
        | llm
        | StrOutputParser()
)


def load_mysql_data():
    """从MySQL加载股票数据"""
    # 连接数据库
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
            # 查询股票信息
            sql = """
            SELECT 
                stock_code,
                stock_name,
                current_price,
                one_month_change,
                one_year_change,
                exchange,
                industry,
                volume,
                market_cap,
                last_updated
            FROM stock_info
            """

            cursor.execute(sql)
            results = cursor.fetchall()

            for row in results:
                # 构建股票信息内容
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
                
                # 创建Document对象
                doc = Document(
                    page_content=content,
                    metadata={
                        'stock_code': row['stock_code'],
                        'stock_name': row['stock_name'],
                        'exchange': row['exchange'],
                        'industry': row['industry'],
                        'current_price': str(row['current_price'])
                    }
                )
                documents.append(doc)

    finally:
        connection.close()

    return documents


def initialize_vector_database():
    """初始化向量数据库（如果需要的话）"""
    # 加载MySQL数据
    docs = load_mysql_data()
    print(f"从数据库加载了 {len(docs)} 个文档")

    # 分割文档
    split_docs = text_splitter.split_documents(docs)
    print(f"分割后得到 {len(split_docs)} 个文档块")

    # 分批添加到向量数据库（DashScope API限制每批最多10个文档）
    batch_size = 10
    for i in range(0, len(split_docs), batch_size):
        batch = split_docs[i:i + batch_size]
        vector_store.add_documents(batch)
        print(f"已处理第 {i//batch_size + 1} 批，添加了 {len(batch)} 个文档块")
    
    print("向量数据库构建完成")
    return True


if __name__ == '__main__':
    # 初始化向量数据库
    initialize_vector_database()
    
    # 测试问答
    question = "苹果公司(AAPL)的股票表现如何？"
    answer = chain.invoke(question)
    print(f"\n问题: {question}")
    print(f"回答: {answer}")
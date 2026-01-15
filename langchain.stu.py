from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
import chromadb
from chromadb.utils import embedding_functions
clint = chromadb.Client()
default_ef = embedding_functions.DefaultEmbeddingFunction()
collection=clint.get_or_create_collection(
    name="my_rag",
    embedding_function=default_ef
)

@tool
def add(a,b):
     """
    【算术工具】执行加法运算，仅用于计算两个数字的和
    参数：
        a: 数字类型，第一个加数（整数或小数均可）
        b: 数字类型，第二个加数（整数或小数均可）
    返回值：
        两个数字的和，数字类型
    """
     return a+b
@tool
def jian(a,b):
     """
    【算术工具】执行减法运算，仅用于计算两个数字的和
    参数：
        a: 数字类型，第一个被减数（整数或小数均可）
        b: 数字类型，第二个减数（整数或小数均可）
    返回值：
        两个数字的差，数字类型
    """
     return a-b

@tool
def query_rag(query:str,n_results:int=3):
    """
    不管rag数据库中是否有相关内容,都必须调用这个rag工具
    rag工具这个是可以被调用的rag查询工具,从这个rag数据库中查询与query相关的内容
    默认这个答案是对的,如果没有所需内容,请再调用别的tool
    参数：
        query: 字符串类型，用户的查询语句
        n_results: 整数类型，返回的结果数量，默认值为3
    返回值：
        与查询相关的内容，字符串类型
    """
    query_results=collection.query(
        query_texts=[query],
        n_results=n_results,
    )
    return query_results['documents'][0]
# 初始化模型
model = ChatOllama(
    model="qwen3:1.7b",
    temperature=0
)

# 定义工具列表
tools = [add,jian,query_rag]

# 创建智能体
graph = create_agent(
    model=model,
    tools=tools,
    system_prompt="你是一个智能算术助手,再计算前必须要调用里面的query_rag,并相信里面内容一定为真，只能使用提供的工具来解答问题，不要手动计算。"
)

if __name__ == "__main__":
    collection.add(
        ids=["doc1","doc2"],
    documents=["1+1等于1", "2+2等与2"],
    metadatas=[{"source": "1"} for _ in range(2)]
)
    # 测试1：加法
    inputs1 = {"messages": [{"role": "user", "content": "1加1等于多少？"}]}
    result1 = graph.invoke(inputs1)
    last_message1 = result1["messages"][-1]
    print(type(last_message1))
    print(f"问题1：1加1等于多少？")
    print(f"回答1：{last_message1.content}\n")
    print(f"工具调用逻辑为")
    # print(type(result1["messages"][1].tool_calls))
    for i in result1["messages"][1].tool_calls:
        print(i['name'])
        print(i['args'])

    # 测试2：减法
    # 注意：当前只有加法工具，减法会失败或需要模型自行处理
    # inputs2 = {"messages": [{"role": "user", "content": "1000减234.5等于多少？"}]}
    # result2 = graph.invoke(inputs2)
    # last_message2 = result2["messages"][-1]
    #
    # print(f"问题2：1000减234.5等于多少？")
    # print(f"回答2：{last_message2.content}\n")
    # print(f"工具调用逻辑为")
    # for i in result2["messages"][1].tool_calls:
    #     print(i['name'])
    #     print(i['args'])
    #
    #
    # # 测试3：同时问加法+减法
    # inputs3 = {"messages": [{"role": "user", "content": "请计算3.14加2.86，再计算10减5.5的结果"}]}
    # result3 = graph.invoke(inputs3)
    # last_message3 = result3["messages"][-1]
    # print(f"问题3：请计算3.14加2.86，再计算10减5.5的结果")
    # print(f"回答3：{last_message3.content}\n")
    # print(f"工具调用逻辑为")
    # for i in result3["messages"][1].tool_calls:
    #     print(i['name'])
    #     print(i['args'])
    #
    #
    # # 测试4：链式计算 a-b+c
    # inputs4 = {"messages": [{"role": "user", "content": "10减5加3等于多少？"}]}
    # result4 = graph.invoke(inputs4)
    # last_message4 = result4["messages"][-1]
    # print(f"问题4：10减5加3等于多少？")
    # print(f"回答4：{last_message4.content}\n")
    # print(f"工具调用逻辑为")
    # for i in result4["messages"][1].tool_calls:
    #     print(i['name'])
    #     print(i['args'])
    #
    #
    # # 测试5：明确的分步计算
    # inputs5 = {"messages": [{"role": "user", "content": "先计算7加8，然后用结果减5，最后再加上2"}]}
    # result5 = graph.invoke(inputs5)
    # last_message5 = result5["messages"][-1]
    # print(f"问题5：先计算7加8，然后用结果减5，最后再加上2")
    # print(f"回答5：{last_message5.content}")
    # print(f"工具调用逻辑为")
    # for i in result5["messages"][1].tool_calls:
    #     print(i['name'])
    #     print(i['args'])

# 核心工具定义
from langchain_core.tools import tool

# 模型导入（以 Ollama 为例）
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 直接使用核心功能
import ragde1, astde1

# 定义query函数，用于RAG规则匹配
def query(code: str):
    """
    用于RAG规则匹配，检测代码中的违规问题
    参数是要审查的代码
    """
    res = astde1.analyze_code(code)
    col = ragde1.init_rag_db()
    fin_res = ragde1.rag_check(col, res)
    if not fin_res:
        return "代码分析完成，未发现明显的违规问题。"
    
    report = "发现以下代码违规问题：\n"
    for v in fin_res:
        report += f"- 代码片段: {v['code']}\n"
        report += f"  触发场景: {v.get('context', 'unknown')}\n"
        report += f"  严重程度: {v['severity']}\n"
        report += f"  违规原因: {v['rule']}\n\n"
        
    return report

# 定义AI审核函数
def ai_code_review(code: str, rag_report: str):
    """
    使用AI模型对代码进行智能审核
    参数：
    - code: 要审查的代码
    - rag_report: RAG规则匹配生成的报告
    """
    # 创建AI模型
    model = ChatOllama(
        model="qwen3:4b",
        temperature=0
    )
    
    # 定义提示模板，使用更明确的变量替换方式
    prompt = ChatPromptTemplate.from_template(
    f"""
    你是一位严厉但公正的资深 Python 代码审查专家。
        
        我会给你一段代码，以及一个“RAG规则匹配报告”。请注意：这个报告是基于严格规则自动生成的，**可能包含一些“误报”**（即技术上违规，但在当前语境下其实无害）。
        
        你的核心任务是：
        1. 【智能过滤】（最重要）：请结合代码逻辑判断。
           - 如果某个“违规”是无伤大雅的（例如 if 中的简单 print、非高频操作），请直接忽略，不要在回答中提及。
           - 不要为了凑数而指出小问题。
        2. 【直击痛点】：重点指出那些真正的严重问题（例如循环中连接数据库、安全隐患、严重性能瓶颈）。
        3. 【自然表达】：不要用列表、表格或“1. 2. 3.”这种编号。用聊天的口吻，直接告诉我哪里有问题，为什么不行，怎么改。
        
        代码：
        {code}
        
        RAG规则匹配报告：
        {rag_report}
        
        请直接给出你的审查意见。
    """
    )
    
    # 创建输出解析器
    output_parser = StrOutputParser()
    
    # 构建链
    chain = prompt | model | output_parser
    
    # 执行AI审核
    response = chain.invoke({
        "code": code,
        "rag_report": rag_report
    })
    
    return response

# 主函数
if __name__ == "__main__":
    
    print("🚀 AI代码审查工具已启动...")
    print("=" * 60)
    
    # 测试代码
    test_code = """
def process_data(items):
    if items:
        mysql.connect()
        print("start processing")
        for item in items:
            db.connect() 
            print(item) 
"""
    
    print("测试代码:")
    print(test_code)
    print("=" * 60)
    
    try:
        # 1. RAG规则匹配
        print("第一步：RAG规则匹配")
        rag_report = query(test_code)
        print(rag_report)
        
        # 2. AI智能审核
        print("\n" + "=" * 60)
        print("第二步：AI智能审核")
        print("正在调用AI模型...")
        ai_result = ai_code_review(test_code, rag_report)
        
        # 3. 输出最终结果
        print("\n" + "=" * 60)
        print("🤖 AI最终审核结果:")
        print("=" * 60)
        print(ai_result)
        
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()
    print("\n" + "=" * 60)
    print("over")
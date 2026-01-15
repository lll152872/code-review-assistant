from gc import collect
import chromadb
from chromadb.utils import embedding_functions
import astde1
def init_rag_db():
    # client: ChromaDB持久化客户端（英文：client - 客户端，这里指连接到ChromaDB的客户端对象）
    client = chromadb.PersistentClient(path="./demodb.db")
    # default_ef: 默认嵌入函数（英文：default embedding function，用于生成文本的向量表示）
    default_ef=embedding_functions.DefaultEmbeddingFunction()
    # collection: 代码规则集合（英文：collection - 集合，这里指存储代码规则的数据库集合）
    collection=client.get_or_create_collection(
        name="code_rules",
        embedding_function=default_ef
    )
    # 先获取所有文档的ID，然后删除它们
    # all_docs: 所有文档（英文：all documents，指集合中现有的所有文档）
    
    if collection.count():
        return collection
    collection.add(
        ids=["rule_no_print_in_loop"],
        documents=["禁止在循环中使用 print 语句，这会严重影响性能并导致日志刷屏。"],
        metadatas={
            "action": "print",         # 动作名
            "forbidden_in": "loop",    # 禁止的场景
            "severity": "low"
        }
    )
    
    # 规则2: 禁止在循环中 connect (数据库连接)
    collection.add(
        ids=["rule_no_connect_in_loop"],
        documents=["禁止在循环中创建数据库连接，应该使用连接池或在循环外连接。"],
        metadatas={
            "action": "connect",
            "forbidden_in": "loop",
            "severity": "high"
        }
    )
    # --- 规则3: 禁止在 if 中 print (假设这是一个奇怪的需求) ---
    collection.add(
        ids=["rule_no_print_in_if"],
        documents=["禁止在 if 语句中使用 print，建议用日志框架替代。"],
        metadatas={
            "action": "print",
            "forbidden_in": "if",
            "severity": "low"
        }
    )
    
    # --- 规则4: 禁止在 if 中 eval (安全风险) ---
    collection.add(
        ids=["rule_no_eval_in_if"],
        documents=["禁止在 if 条件分支中使用 eval() 函数，存在严重安全风险。"],
        metadatas={
            "action": "eval",
            "forbidden_in": "if",
            "severity": "high"
        }
    )                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
    
    print(f"✅ RAG 数据库初始化完成，已加载 {collection.count()} 条规则。")
    return collection                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
def extract_action_name(code_snippet: str) -> str:
    """
    辅助函数：从代码片段中提取动作名
    例如: "print(y)" -> "print"
    例如: "db.connect()" -> "connect"
    """
    # code_snippet: 代码片段（英文：code snippet - 代码片段，指要提取动作名的函数调用代码）
    if not code_snippet:
        return "unknown"
    # 简单粗暴的提取：取左括号前面的部分，去掉 . 和空格
    if '(' in code_snippet:
        func_part = code_snippet.split('(')[0].strip()  # func_part: 函数部分（英文：function part - 函数调用中括号前的部分）
        return func_part.split('.')[-1] # 取最后一部分，比如 db.connect -> connect
    return "unknown"
def insert(inserted:list):
    # inserted: 要插入的数据列表（英文：inserted - 已插入的，这里指待插入的数据）
    # matebase: 元数据库（英文：meta base 的拼写错误，应该是 metadata base，指存储元数据的数据库）
    matebase=[]
    print("insert yes")
def rag_check(collection,results:list):
    # collection: ChromaDB集合对象（英文：collection - 集合，这里指存储规则的数据库集合）
    # results: AST分析结果列表（英文：results - 结果，这里指AST解析后得到的代码结构信息）
    print("query_open")
    violations=[]  # violations: 违规列表（英文：violations - 违规，存储检测到的所有违规情况）
    for i in results:  # i: 遍历的每个AST节点信息（英文：i - 循环变量，代表results列表中的每个元素）
        if i['type']!='Call':
            continue
        code_snippet=i["code"]  # code_snippet: 代码片段（英文：code snippet - 代码片段，指当前检测到的函数调用代码）
        action_name=extract_action_name(code_snippet)  # action_name: 动作名称（英文：action name - 动作名称，指函数调用的名称，如print、connect等）
        is_in_loop=i['in_loop']  # is_in_loop: 是否在循环中（英文：is in loop - 是否在循环中，布尔值，True表示当前代码在循环内）
        is_in_if=i["in_if"]  # is_in_if: 是否在if语句中（英文：is in if - 是否在if语句中，布尔值，True表示当前代码在if分支内）
        print(f"--> 检测到动作: {action_name} (代码: {code_snippet})")
        print(f"    环境状态: 在循环中={is_in_loop}, 在if中={is_in_if}")
        if is_in_loop:
            print("query in_loop")
            # 检查循环中的规则
            try:
                # loop_results: 循环规则查询结果（英文：loop results - 循环规则的查询结果）
                loop_results = collection.query(
                    query_texts=[code_snippet],
                    where={"$and": [{"action": {"$eq": action_name}}, {"forbidden_in": {"$eq": "loop"}}]},
                    n_results=1
                )
                if loop_results['ids'][0]:
                    rule_id = loop_results['ids'][0][0]  # rule_id: 规则ID（英文：rule ID - 规则的唯一标识符）
                    rule_desc = loop_results['documents'][0][0]  # rule_desc: 规则描述（英文：rule description - 规则的详细描述）
                    severity = loop_results['metadatas'][0][0]['severity']  # severity: 严重程度（英文：severity - 规则违规的严重程度，如low、high等）
                    
                    violations.append({
                        "code": code_snippet,
                        "rule": rule_desc,
                        "severity": severity,
                        "context": "loop"
                    })
                    print(f"    🚨 触发循环规则！{rule_desc}")
            except Exception as e:
                print(f"    ⚠️  查询循环规则时出错: {e}")
        
        if is_in_if:
            print("query in_if")
            # 检查if中的规则
            try:
                # if_results: if规则查询结果（英文：if results - if规则的查询结果）
                if_results = collection.query(
                    query_texts=[code_snippet],
                    where={"$and": [{"action": {"$eq": action_name}}, {"forbidden_in": {"$eq": "if"}}]},
                    n_results=1
                )
                if if_results['ids'][0]:
                    rule_id = if_results['ids'][0][0]
                    rule_desc = if_results['documents'][0][0]
                    severity = if_results['metadatas'][0][0]['severity']
                    
                    violations.append({
                        "code": code_snippet,
                        "rule": rule_desc,
                        "severity": severity,
                        "context": "if"
                    })
                    print(f"    🚨 触发if规则！{rule_desc}")
            except Exception as e:
                print(f"    ⚠️  查询if规则时出错: {e}")
        
        if not is_in_loop and not is_in_if:
            print("all_query")
            # 检查anywhere规则
            try:
                # anywhere_results: 任意位置规则查询结果（英文：anywhere results - 任意位置规则的查询结果）
                anywhere_results = collection.query(
                    query_texts=[code_snippet],
                    where={"$and": [{"action": {"$eq": action_name}}, {"forbidden_in": {"$eq": "anywhere"}}]},
                    n_results=1
                )
                if anywhere_results['ids'][0]:
                    rule_id = anywhere_results['ids'][0][0]
                    rule_desc = anywhere_results['documents'][0][0]
                    severity = anywhere_results['metadatas'][0][0]['severity']
                    
                    violations.append({
                        "code": code_snippet,
                        "rule": rule_desc,
                        "severity": severity,
                        "context": "anywhere"
                    })
                    print(f"    🚨 触发anywhere规则！{rule_desc}")
            except Exception as e:
                print(f"    ⚠️  查询anywhere规则时出错: {e}")
            print()      
    return violations
# def get_or_create():
#     if 

if __name__ == "__main__":
    # 0. 初始化数据库
    collection = init_rag_db()
    
    # 示例代码：同时包含 if 和 loop 的场景
    sample_code = """
def example():
    x = 1
    if x > 0:
        print("x is positive")  # 在 if 中，会触发 "禁止 print in if" 规则
        for i in range(5):
            y = i * 2
            print(y)            # 既在 loop 中，又在 if 中！会同时触发两条规则
    else:
        print("x is non-positive")  # 在 else（也是 if 分支），会触发 "禁止 print in if"
    
    while x < 10:
        x += 1
        print(x)                # 在 loop 中，会触发 "禁止 print in loop"
"""

    # 1. AST 分析
    print("=" * 60)
    print("第一步：AST 解析代码结构")
    print("=" * 60)
    results = astde1.analyze_code(sample_code)
    
    # 2. RAG 检查
    print("\n" + "=" * 60)
    print("第二步：RAG 智能规则匹配")
    print("=" * 60)
    final_violations = rag_check(collection, results)
    
    # 3. 总结
    print("\n" + "=" * 60)
    print("📊 最终审查报告")
    print("=" * 60)
    if final_violations:
        for v in final_violations:
            print(f"[{v['severity'].upper()}] 代码: {v['code']}")
            print(f"        触发场景: {v['context']}")
            print(f"        违规原因: {v['rule']}\n")
    else:
        print("代码完美，没有发现问题！")
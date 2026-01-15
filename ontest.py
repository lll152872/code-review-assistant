import chromadb
import libcst as cst
from chromadb.utils import embedding_functions
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm=ChatOllama(
    model="qwen3:1.7b",
    temperature=0
)
def ai(user_code,rules_text):
    ai_response=chain.invoke

client = chromadb.Client()
default_ef=embedding_functions.DefaultEmbeddingFunction()
collection =client.get_or_create_collection(
    name="test",
    embedding_function=default_ef
)
rules_data = [
    {
        "id": "R1", 
        "desc": "禁止在循环中创建数据库连接，这会导致连接池耗尽。", 
        "keywords": "db.connect, new Connection, DriverManager.getConnection",
        "tags": ["loop", "database"]
    },
    {
        "id": "R2", 
        "desc": "禁止在循环中打印日志，这会产生大量 IO 开销，影响性能。", 
        "keywords": "print, logger.info, console.log",
        "tags": ["loop", "performance"]
    },
    {
        "id": "R3", 
        "desc": "循环变量命名禁止使用单个字母如 i, j，应使用具有业务含义的名称。", 
        "keywords": "for i in, for j in, range(i)",
        "tags": ["loop", "naming"]
    }
]
docs_to_store = [f"{r['desc']} Keywords: {r['keywords']}" for r in rules_data]
collection.add(
    documents=docs_to_store,
    ids=[r["id"] for r in rules_data],
    metadatas=[{"tags": r["tags"]} for r in rules_data] # 关键：用标签分类
)
class fenxi(cst.CSTVisitor):
    def __init__(self):
        self.is_loop=False
        self.action=[]
    def visit_For(self, node):
        self.is_loop = True
        # 继续遍历循环体内部
        return True 

    def leave_For(self, node):
        self.is_loop = False # 离开循环

    def visit_Call(self, node):
        # 提取函数调用的名字，作为“动作指纹”
        # 例如: db.connect() -> 提取 "connect"
        #       print(...)    -> 提取 "print"
        func_name = ""
        if isinstance(node.func, cst.Name):
            func_name = node.func.value
        elif isinstance(node.func, cst.Attribute):
            # 处理 obj.method() 的情况
            func_name = node.func.attr.value
            
        if func_name:
            self.actions.append(func_name)
user_code = """
for i in range(10):
    # 错误 1: 在循环里连库 (触发 R1)
    db.connect() 
    
    # 错误 2: 在循环里打印 (触发 R2)
    print("Processing item " + str(i))
    
    # 正确: 模拟一个普通操作，库里没这条规则，不应报错
    item = process_data(i)
"""

print(f"\n👀 待审查代码:\n{user_code}")
wrapper = cst.metadata.MetadataWrapper(cst.parse_module(user_code))
visitor = fenxi()
wrapper.visit(visitor)

# 分析结果
structure_tags = ["loop"] if visitor.is_loop else []
detected_actions = visitor.actions # ["connect", "print", "process_data"]

print(f"🔍 [AST 分析] 结构标签: {structure_tags}, 动作指纹: {detected_actions}")

# --- 阶段 B: 精准特征检索 (解决漏查和无数条结果) ---
triggered_rules = []

if "loop" in structure_tags:
    # 策略：针对每一个动作，都去库里查一次 (点对点)
    for action in detected_actions:
        print(f"\n🔄 正在检索特征: '{action}' ...")
        
        results = collection.query(
            query_texts=[action], # 用动作名 (如 connect) 去匹配 Keywords
            where={"tags": {"$in": ["loop"]}}, # 限定只在 loop 标签里查
            n_results=1 # 每个动作只取最相关的一条
        )
        
        # 检查距离，只有足够近才算命中
        if results['distances'][0][0] < 0.35:
            rule_id = results['ids'][0][0]
            rule_content = results['documents'][0][0]
            
            # 去重：防止不同动作触发同一条规则
            if rule_id not in triggered_rules:
                triggered_rules.append(rule_id)
                print(f"✅ 命中规则 [{rule_id}]: {rule_content[:30]}...")
            else:
                print(f"♻️ 规则 [{rule_id}] 已触发，跳过。")
        else:
            print(f"⚪ 未找到相关规则 (距离: {results['distances'][0][0]:.2f})")

# --- 阶段 C: 汇总并生成 Prompt ---
if triggered_rules:
    # 根据 ID 拿回完整的规则描述给 AI 看
    final_rules_data = collection.get(ids=triggered_rules)
    
    prompt = f"""
    你是一个资深代码审查专家。请审查以下代码。
    
    用户代码:
    {user_code}
参考规则 (必须严格检查这些点):
    {final_rules_data['documents']}
    
    请指出代码中违反了哪些规则，并给出修改建议。
    """
    
    # --- 阶段 D: 调用 AI ---
    ai_response = ai(prompt)
    print(ai_response)
else:
    print("\n✅ 代码审查通过，未发现明显违规。")
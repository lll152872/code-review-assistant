
import chromadb
from chromadb.utils import embedding_functions
client = chromadb.Client()#创建客户端,无持久化
# client=chromadb.PersistentClient(path="./cli")
default_ef=embedding_functions.DefaultEmbeddingFunction()
collection=client.get_or_create_collection(
    name="my_rag",
    embedding_function=default_ef
)
collection.add(
    ids=["doc1","doc2",'doc3'],
    documents=[  # 原始文档内容列表，Chroma会通过绑定的嵌入函数自动转为向量
        # 汉语翻译：原始文档内容列表（存储需要进行向量检索的文本数据）
        "Chroma是一款轻量级向量数据库",
        "FAISS是Facebook开源的高性能向量检索库",
        "RAG场景常用Chroma做原型开发"
    ],
    metadatas=[
        # 元数据列表，键值对格式，用于过滤检索（如按类型、来源筛选）
        {"type": "database", "source": "官方文档"},
        {"type": "retrieval_lib", "source": "GitHub"},
        {"type": "usage", "source": "实战总结"}
        # 这个看不懂?为啥啊有啥用这个传参
    ]
)
print("insert yes")
query_results=collection.query(
    query_texts=["RAG原型用什么工具？"],  
    n_results=2,  
    # where={"type": "usage"}  
)
print(type(query_results))
# 这个是字典

print("=== 相似性检索结果 ===")  # 打印结果分隔符，方便查看
print("匹配的文档ID：", query_results["ids"])  # 打印匹配到的文档ID列表
print("匹配的文档内容：", query_results["documents"])  # 打印匹配到的原始文档内容
print("匹配的元数据：", query_results["metadatas"])  # 打印匹配到的文档元数据
print("相似度分数（距离越小越相似）：", query_results["distances"])  # 打印距离分数（欧氏距离，越小相似度越高）
collection.update(
    ids=["doc1"],
    documents=["Chroma是一款专为RAG设计的轻量级向量数据库（更新后）"],
    metadatas=[{"type":"database","source":"官方文档","update_time":"2026-01-01"}]
)

update_verify=collection.get(ids=["doc1"])
print("=== 更新后验证 ===")  # 打印分隔符
print("更新后的文档：", update_verify["documents"][0])  # 打印doc1更新后的文档内容（列表第0个元素，因仅查询一个ID）
print("更新后的元数据：", update_verify["metadatas"][0])  # 打印doc1更新后的元数据
print("updata yes")
collection.delete(ids=["doc1"])
collection.delete(where={"type":"retrieval_lib"})
print("delete yes")
delete_verify = collection.get()  # 不传入参数，查询集合中所有剩余数据

print("=== 删除后剩余数据 ===")  # 打印分隔符
print("剩余文档ID：", delete_verify["ids"])  # 打印剩余文档的ID列表
print("剩余文档内容：", delete_verify["documents"])  # 打印剩余文档的内容列表
import ast
from doctest import FAIL_FAST
def analyze_code(code:str)->list:
    class CodeAnalyzer(ast.NodeVisitor):
        def __init__(self) -> None:
            self.results=[]
            self.in_loop=False
            self.in_if=False
            self.loop_stack=[]
            self.if_stack=[]
        def visit(self,node):
            node_info={
                "type":type(node).__name__,
                "in_loop":self.in_loop,
                "in_if":self.in_if,
                "code":ast.get_source_segment(code,node) if hasattr(node,'lineno') else None
            }
            self.results.append(node_info)
            if isinstance(node,(ast.For,ast.While,ast.AsyncFor)):
                self.loop_stack.append(node)
                self.in_loop=True
            if isinstance(node,ast.If):
                self.if_stack.append(node)
                self.in_if=True
            super().visit(node)
            if isinstance(node, (ast.For, ast.While, ast.AsyncFor)):
                self.loop_stack.pop()
                self.in_loop = len(self.loop_stack) > 0
            
            if isinstance(node, ast.If):
                self.if_stack.pop()
                self.in_if = len(self.if_stack) > 0
    tree=ast.parse(code)
    analyze=CodeAnalyzer()
    analyze.visit(tree)
    return analyze.results        
def print_analysis(results):
    """
    打印分析结果
    """
    print("代码分析结果：")
    print("-" * 80)
    print(f"{'节点类型':<20} {'是否在循环中':<15} {'是否在if中':<15} {'代码片段'}")
    print("-" * 80)
    
    for info in results:
        node_type = info['type']
        in_loop = "是" if info['in_loop'] else "否"
        in_if = "是" if info['in_if'] else "否"
        code = info['code'] if info['code'] else "N/A"
        
        # 限制代码片段长度
        if len(code) > 50:
            code = code[:47] + "..."
        
        print(f"{node_type:<20} {in_loop:<15} {in_if:<15} {code}")
    
    print("-" * 80)

# 示例代码
sample_code = """
def example():
    x = 1
    if x > 0:
        print("x is positive")
        for i in range(5):
            y = i * 2
            print(y)
    else:
        print("x is non-positive")
    
    while x < 10:
        x += 1
        print(x)
"""

if __name__ == "__main__":
    # 分析示例代码
    results = analyze_code(sample_code)
    print_analysis(results)
    print("end")
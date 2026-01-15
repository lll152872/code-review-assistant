# d:\mycode\mybigcreate\tree-sitter.stu.py
print("=" * 80)
print("Tree-sitter AST 库学习教程")
print("=" * 80)

# 安装必要的库
print("\n【安装 Tree-sitter 及 Python 解析器】")
print("-" * 80)
print("请确保已安装以下库：")
print("pip install tree-sitter tree-sitter-python")

# 尝试导入 tree-sitter
print("\n正在导入 Tree-sitter...")
try:
    import tree_sitter
    from tree_sitter import Language, Parser
    print("✅ Tree-sitter 导入成功")
except ImportError as e:
    print(f"❌ Tree-sitter 导入失败：{e}")
    print("请先安装 tree-sitter 和 tree-sitter-python 库")
    exit(1)

# 初始化 Tree-sitter Python 语言解析器
print("\n【初始化 Tree-sitter Python 解析器】")
print("-" * 80)

# 加载 Python 语言解析器
try:
    # 查找或编译 Python 语言解析器
    PYTHON_LANGUAGE = Language('build/my-languages.so', 'python')
    print("✅ Python 语言解析器加载成功")
except Exception as e:
    print(f"⚠️  无法加载预编译的 Python 语言解析器：{e}")
    print("正在尝试编译 Python 语言解析器...")
    
    try:
        # 从 GitHub 克隆并编译 Python 语言解析器
        import os
        import subprocess
        
        # 创建 build 目录
        os.makedirs('build', exist_ok=True)
        
        # 克隆 python 语言定义
        if not os.path.exists('tree-sitter-python'):
            subprocess.run(['git', 'clone', 'https://github.com/tree-sitter/tree-sitter-python.git'], check=True)
        
        # 编译语言解析器
        Language.build_library(
            'build/my-languages.so',
            ['tree-sitter-python']
        )
        
        # 重新加载
        PYTHON_LANGUAGE = Language('build/my-languages.so', 'python')
        print("✅ Python 语言解析器编译并加载成功")
    except Exception as compile_e:
        print(f"❌ Python 语言解析器编译失败：{compile_e}")
        print("请手动安装并配置 tree-sitter-python")
        exit(1)

# 创建解析器
parser = Parser()
parser.set_language(PYTHON_LANGUAGE)
print("✅ Tree-sitter 解析器初始化完成")

# ========================================
# 第1章：Tree-sitter AST 基础概念
# ========================================
print("\n【第1章：Tree-sitter AST 基础概念】")
print("-" * 80)

code_sample = """
def hello(name):
    print(f"Hello, {name}!")
    return name
"""

print("原始代码：")
print(code_sample)

# 将代码解析为 AST
tree = parser.parse(bytes(code_sample, 'utf8'))
root_node = tree.root_node

print("\n解析后的 AST 根节点：")
print(f"节点类型: {root_node.type}")
print(f"开始位置: {root_node.start_point}")
print(f"结束位置: {root_node.end_point}")
print(f"子节点数量: {len(root_node.children)}")

# 打印完整的 AST 结构
print("\n完整的 AST 结构：")

def print_node(node, level=0):
    indent = "  " * level
    print(f"{indent}{node.type} [{node.start_point[0]}:{node.start_point[1]} - {node.end_point[0]}:{node.end_point[1]}]")
    for child in node.children:
        print_node(child, level + 1)

print_node(root_node)

# ========================================
# 第2章：Tree-sitter AST 遍历
# ========================================
print("\n【第2章：Tree-sitter AST 遍历】")
print("-" * 80)

code_visitor = """
def add(a, b):
    return a + b

def multiply(x, y):
    return x * y

for i in range(10):
    print(i)
"""

print("示例代码：")
print(code_visitor)

# 解析代码
tree = parser.parse(bytes(code_visitor, 'utf8'))
root_node = tree.root_node

# 定义遍历器类
class TreeSitterVisitor:
    def __init__(self):
        self.function_count = 0
        self.for_loop_count = 0
        self.function_names = []
        self.function_calls = []
    
    def visit(self, node):
        # 访问当前节点
        method_name = f"visit_{node.type}"
        if hasattr(self, method_name):
            getattr(self, method_name)(node)
        
        # 访问子节点
        for child in node.children:
            self.visit(child)
    
    def visit_function_definition(self, node):
        """访问函数定义节点"""
        self.function_count += 1
        # 获取函数名
        for child in node.children:
            if child.type == "identifier":
                func_name = child.text.decode('utf8')
                self.function_names.append(func_name)
                print(f"  发现函数定义: {func_name}")
                break
    
    def visit_for_statement(self, node):
        """访问 for 循环节点"""
        self.for_loop_count += 1
        print(f"  发现 for 循环")
    
    def visit_call(self, node):
        """访问函数调用节点"""
        # 获取函数名
        for child in node.children:
            if child.type in ["identifier", "attribute"]:
                func_name = child.text.decode('utf8')
                self.function_calls.append(func_name)
                print(f"  发现函数调用: {func_name}()")
                break

# 使用遍历器
visitor = TreeSitterVisitor()
print("\n开始遍历 AST：")
visitor.visit(root_node)

print(f"\n统计结果：")
print(f"  函数定义数量: {visitor.function_count}")
print(f"  函数名称列表: {visitor.function_names}")
print(f"  for 循环数量: {visitor.for_loop_count}")
print(f"  函数调用列表: {visitor.function_calls}")

# ========================================
# 第3章：提取函数详细信息
# ========================================
print("\n【第3章：提取函数详细信息】")
print("-" * 80)

code_function = """
@dataclass
class User:
    name: str
    age: int

@log_execution
def process_user(user: User, action: str = "default") -> bool:
    if action == "delete":
        return False
    return True
"""

print("示例代码：")
print(code_function)

class FunctionInfoVisitor:
    def __init__(self):
        self.functions = []
    
    def visit(self, node):
        method_name = f"visit_{node.type}"
        if hasattr(self, method_name):
            getattr(self, method_name)(node)
        
        for child in node.children:
            self.visit(child)
    
    def visit_function_definition(self, node):
        func_info = {
            "name": "",
            "decorators": [],
            "parameters": [],
            "return_type": None
        }
        
        # 提取装饰器
        for child in node.children:
            if child.type == "decorator":
                # 获取装饰器名称
                for dec_child in child.children:
                    if dec_child.type in ["identifier", "attribute"]:
                        decorator_name = dec_child.text.decode('utf8')
                        func_info["decorators"].append(decorator_name)
        
        # 提取函数名
        for child in node.children:
            if child.type == "identifier":
                func_info["name"] = child.text.decode('utf8')
        
        # 提取参数
        for child in node.children:
            if child.type == "parameters":
                self._extract_parameters(child, func_info)
        
        # 提取返回类型
        for child in node.children:
            if child.type == "type_annotation":
                return_type = child.text.decode('utf8')[2:]  # 去掉 ->
                func_info["return_type"] = return_type.strip()
        
        self.functions.append(func_info)
    
    def _extract_parameters(self, params_node, func_info):
        """提取函数参数"""
        for param_child in params_node.children:
            if param_child.type == "parameter":
                param_name = ""
                param_type = None
                
                for child in param_child.children:
                    if child.type == "identifier":
                        param_name = child.text.decode('utf8')
                    elif child.type == "type_annotation":
                        param_type = child.text.decode('utf8')[2:].strip()
                
                if param_name:
                    func_info["parameters"].append(f"{param_name}: {param_type}")

# 使用遍历器
func_visitor = FunctionInfoVisitor()
tree = parser.parse(bytes(code_function, 'utf8'))
func_visitor.visit(tree.root_node)

print("\n提取函数信息：")
for func in func_visitor.functions:
    print(f"\n函数名: {func['name']}")
    print(f"  装饰器: {func['decorators']}")
    print(f"  参数: {func['parameters']}")
    print(f"  返回类型: {func['return_type']}")

# ========================================
# 第4章：提取类信息
# ========================================
print("\n【第4章：提取类信息】")
print("-" * 80)

code_class = """
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        pass

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)
        self.breed = breed
    
    def speak(self):
        return "Woof!"
"""

print("示例代码：")
print(code_class)

class ClassInfoVisitor:
    def __init__(self):
        self.classes = []
    
    def visit(self, node):
        method_name = f"visit_{node.type}"
        if hasattr(self, method_name):
            getattr(self, method_name)(node)
        
        for child in node.children:
            self.visit(child)
    
    def visit_class_definition(self, node):
        """访问类定义节点"""
        class_info = {
            "name": "",
            "bases": [],
            "methods": []
        }
        
        # 提取类名
        for child in node.children:
            if child.type == "identifier":
                class_info["name"] = child.text.decode('utf8')
        
        # 提取基类
        for child in node.children:
            if child.type == "base_clause":
                for base_child in child.children:
                    if base_child.type in ["identifier", "attribute"]:
                        base_name = base_child.text.decode('utf8')
                        class_info["bases"].append(base_name)
        
        # 提取方法
        for child in node.children:
            if child.type == "block":
                for block_child in child.children:
                    if block_child.type == "function_definition":
                        # 获取方法名
                        for func_child in block_child.children:
                            if func_child.type == "identifier":
                                method_name = func_child.text.decode('utf8')
                                class_info["methods"].append(method_name)
                                break
        
        self.classes.append(class_info)

# 使用遍历器
class_visitor = ClassInfoVisitor()
tree = parser.parse(bytes(code_class, 'utf8'))
class_visitor.visit(tree.root_node)

print("\n提取类信息：")
for cls in class_visitor.classes:
    print(f"\n类名: {cls['name']}")
    print(f"  继承自: {cls['bases']}")
    print(f"  方法: {cls['methods']}")

# ========================================
# 第5章：条件语句和异常处理
# ========================================
print("\n【第5章：条件语句和异常处理】")
print("-" * 80)

code_control = """
if x > 0:
    print("positive")
elif x < 0:
    print("negative")
else:
    print("zero")

try:
    result = 10 / x
except ZeroDivisionError:
    print("Cannot divide by zero")
except Exception as e:
    print(f"Error: {e}")
finally:
    print("Done")
"""

print("示例代码：")
print(code_control)

class ControlFlowVisitor:
    def __init__(self):
        self.if_count = 0
        self.try_count = 0
        self.except_handlers = []
    
    def visit(self, node):
        method_name = f"visit_{node.type}"
        if hasattr(self, method_name):
            getattr(self, method_name)(node)
        
        for child in node.children:
            self.visit(child)
    
    def visit_if_statement(self, node):
        """访问 if 语句节点"""
        self.if_count += 1
        print(f"  发现 if 语句")
    
    def visit_try_statement(self, node):
        """访问 try 语句节点"""
        self.try_count += 1
        print(f"  发现 try 语句")
        
        # 提取 except 处理器
        for child in node.children:
            if child.type == "except_clause":
                for except_child in child.children:
                    if except_child.type in ["identifier", "attribute"]:
                        exception_type = except_child.text.decode('utf8')
                        self.except_handlers.append(exception_type)
                        print(f"    捕获异常: {exception_type}")

# 使用遍历器
control_visitor = ControlFlowVisitor()
tree = parser.parse(bytes(code_control, 'utf8'))
control_visitor.visit(tree.root_node)

print(f"\n统计：")
print(f"  if 语句数量: {control_visitor.if_count}")
print(f"  try 语句数量: {control_visitor.try_count}")
print(f"  捕获的异常类型: {control_visitor.except_handlers}")

# ========================================
# 第6章：代码质量检查
# ========================================
print("\n【第6章：代码质量检查】")
print("-" * 80)

code_quality = """
def calculate(x, y):
    result = x + y
    print(result)
    return result

for i in range(100):
    db.connect()
    data = db.query("SELECT * FROM table")
    print(data)
"""

print("示例代码：")
print(code_quality)

class CodeQualityChecker:
    def __init__(self):
        self.issues = []
        self.in_loop = False
    
    def visit(self, node):
        # 记录当前是否在循环中
        was_in_loop = self.in_loop
        
        # 检查当前节点是否是循环
        if node.type in ["for_statement", "while_statement"]:
            self.in_loop = True
        
        # 访问当前节点
        method_name = f"visit_{node.type}"
        if hasattr(self, method_name):
            getattr(self, method_name)(node)
        
        # 访问子节点
        for child in node.children:
            self.visit(child)
        
        # 恢复循环状态
        self.in_loop = was_in_loop
    
    def visit_call(self, node):
        """检查函数调用"""
        if not self.in_loop:
            return
        
        # 获取函数名
        for child in node.children:
            if child.type in ["identifier", "attribute"]:
                func_name = child.text.decode('utf8')
                # 检查是否是需要关注的函数
                if "." in func_name:
                    func_name = func_name.split(".")[-1]
                
                if func_name in ["connect", "print"]:
                    self.issues.append({
                        "type": "performance",
                        "message": f"在循环中调用 {func_name}() 可能导致性能问题"
                    })
                break

# 使用检查器
checker = CodeQualityChecker()
tree = parser.parse(bytes(code_quality, 'utf8'))
checker.visit(tree.root_node)

print("\n代码质量检查结果：")
if checker.issues:
    for issue in checker.issues:
        print(f"  ⚠️  [{issue['type'].upper()}] {issue['message']}")
else:
    print("  ✅ 未发现明显问题")

# ========================================
# 第7章：提取代码指纹
# ========================================
print("\n【第7章：提取代码指纹】")
print("-" * 80)

code_fingerprint = """
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

def load_data(filepath):
    data = pd.read_csv(filepath)
    return data

def preprocess(data):
    data = data.dropna()
    return data

def train_model(X, y):
    model = RandomForestClassifier()
    model.fit(X, y)
    return model
"""

print("示例代码：")
print(code_fingerprint)

class CodeFingerprintExtractor:
    def __init__(self):
        self.fingerprint = {
            "imports": [],
            "functions": [],
            "function_calls": [],
            "libraries_used": set()
        }
    
    def visit(self, node):
        method_name = f"visit_{node.type}"
        if hasattr(self, method_name):
            getattr(self, method_name)(node)
        
        for child in node.children:
            self.visit(child)
    
    def visit_import_statement(self, node):
        """访问 import 语句"""
        for child in node.children:
            if child.type in ["identifier", "attribute"]:
                lib_name = child.text.decode('utf8').split('.')[0]
                self.fingerprint["imports"].append(lib_name)
                self.fingerprint["libraries_used"].add(lib_name)
    
    def visit_import_from_statement(self, node):
        """访问 from ... import 语句"""
        for child in node.children:
            if child.type == "dotted_name":
                lib_name = child.text.decode('utf8').split('.')[0]
                self.fingerprint["imports"].append(lib_name)
                self.fingerprint["libraries_used"].add(lib_name)
    
    def visit_function_definition(self, node):
        """访问函数定义"""
        for child in node.children:
            if child.type == "identifier":
                func_name = child.text.decode('utf8')
                self.fingerprint["functions"].append(func_name)
    
    def visit_call(self, node):
        """访问函数调用"""
        for child in node.children:
            if child.type in ["identifier", "attribute"]:
                func_name = child.text.decode('utf8')
                self.fingerprint["function_calls"].append(func_name)

# 使用提取器
fp_extractor = CodeFingerprintExtractor()
tree = parser.parse(bytes(code_fingerprint, 'utf8'))
fp_extractor.visit(tree.root_node)

print("\n提取代码指纹：")
print("\n代码指纹：")
print(f"  使用的库: {list(fp_extractor.fingerprint['libraries_used'])}")
print(f"  定义的函数: {fp_extractor.fingerprint['functions']}")
print(f"  调用的函数: {fp_extractor.fingerprint['function_calls'][:10]}...")

# ========================================
# 第8章：Tree-sitter 高级功能 - 语法高亮
# ========================================
print("\n【第8章：Tree-sitter 高级功能 - 语法高亮】")
print("-" * 80)

print("Tree-sitter 支持语法高亮功能，通过查询语言可以提取语法元素：")
print("例如，可以提取关键字、字符串、注释等")

# 简单演示：提取字符串
code_strings = """
# 这是注释
name = "John"
print(f"Hello, {name}!")
"""

tree = parser.parse(bytes(code_strings, 'utf8'))

print("\n提取字符串和注释：")
print("字符串：")

# 遍历所有节点，查找字符串
for node, _ in tree.root_node.iter_fields():
    if isinstance(node, tree_sitter.Node):
        if node.type in ["string", "comment"]:
            text = node.text.decode('utf8')
            if node.type == "comment":
                print(f"  注释: {text}")
            else:
                print(f"  字符串: {text}")

print("\n" + "=" * 80)
print("Tree-sitter AST 库学习教程完成！")
print("=" * 80)
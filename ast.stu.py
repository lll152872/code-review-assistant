# d:\mycode\mybigcreate\ast.stu.py
import ast

print("=" * 80)
print("Python 标准库 AST 模块学习教程")
print("=" * 80)

# ========================================
# 第1章：AST 基础概念（标准库 ast 模块）
# ========================================
print("\n【第1章：AST 基础概念】")
print("-" * 80)

code_sample = """
def hello(name):
    print(f"Hello, {name}!")
    return name
"""

print("原始代码：")
print(code_sample)

# 将代码解析为 AST
tree = ast.parse(code_sample)
print("\n解析后的 AST 结构：")
print(ast.dump(tree, indent=2))

# ========================================
# 第2章：AST 遍历 - Visitor 模式
# ========================================
print("\n【第2章：AST 遍历 - Visitor 模式】")
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

class BasicVisitor(ast.NodeVisitor):
    def __init__(self):
        self.function_count = 0
        self.for_loop_count = 0
        self.function_names = []
        self.function_calls = []
    
    def visit_FunctionDef(self, node):
        self.function_count += 1
        self.function_names.append(node.name)
        print(f"  发现函数定义: {node.name}")
        self.generic_visit(node)
    
    def visit_For(self, node):
        self.for_loop_count += 1
        print(f"  发现 for 循环")
        self.generic_visit(node)
    
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            self.function_calls.append(func_name)
            print(f"  发现函数调用: {func_name}()")
        self.generic_visit(node)

print("\n开始遍历 AST：")
tree = ast.parse(code_visitor)
visitor = BasicVisitor()
visitor.visit(tree)

print(f"\n统计结果：")
print(f"  函数定义数量: {visitor.function_count}")
print(f"  函数名称列表: {visitor.function_names}")
print(f"  for 循环数量: {visitor.for_loop_count}")
print(f"  函数调用列表: {visitor.function_calls}")

# ========================================
# 第3章：提取函数信息
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

class FunctionInfoVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
    
    def visit_FunctionDef(self, node):
        func_info = {
            "name": node.name,
            "decorators": [],
            "parameters": [],
            "return_type": None
        }
        
        # 提取装饰器
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                func_info["decorators"].append(decorator.id)
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    func_info["decorators"].append(decorator.func.id)
        
        # 提取参数
        for param in node.args.args:
            param_name = param.arg
            param_type = None
            if param.annotation:
                if isinstance(param.annotation, ast.Name):
                    param_type = param.annotation.id
                elif isinstance(param.annotation, ast.Attribute):
                    param_type = f"{param.annotation.value.id}.{param.annotation.attr}"
            func_info["parameters"].append(f"{param_name}: {param_type}")
        
        # 提取返回类型
        if node.returns:
            if isinstance(node.returns, ast.Name):
                func_info["return_type"] = node.returns.id
            elif isinstance(node.returns, ast.Attribute):
                func_info["return_type"] = f"{node.returns.value.id}.{node.returns.attr}"
        
        self.functions.append(func_info)
        self.generic_visit(node)

print("\n提取函数信息：")
tree = ast.parse(code_function)
func_visitor = FunctionInfoVisitor()
func_visitor.visit(tree)

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

print("示例代码：");
print(code_class)

class ClassInfoVisitor(ast.NodeVisitor):
    def __init__(self):
        self.classes = []
    
    def visit_ClassDef(self, node):
        class_info = {
            "name": node.name,
            "bases": [],
            "methods": []
        }
        
        # 提取基类
        for base in node.bases:
            if isinstance(base, ast.Name):
                class_info["bases"].append(base.id)
        
        # 提取方法
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                class_info["methods"].append(item.name)
        
        self.classes.append(class_info)
        self.generic_visit(node)

print("\n提取类信息：")
tree = ast.parse(code_class)
class_visitor = ClassInfoVisitor()
class_visitor.visit(tree)

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

class ControlFlowVisitor(ast.NodeVisitor):
    def __init__(self):
        self.if_count = 0
        self.try_count = 0
        self.except_handlers = []
    
    def visit_If(self, node):
        self.if_count += 1
        print(f"  发现 if 语句")
        self.generic_visit(node)
    
    def visit_Try(self, node):
        self.try_count += 1
        print(f"  发现 try 语句")
        
        for handler in node.handlers:
            if handler.type:
                if isinstance(handler.type, ast.Name):
                    exception_type = handler.type.id
                    self.except_handlers.append(exception_type)
                    print(f"    捕获异常: {exception_type}")
        
        self.generic_visit(node)

print("\n分析控制流：")
tree = ast.parse(code_control)
control_visitor = ControlFlowVisitor()
control_visitor.visit(tree)

print(f"\n统计：")
print(f"  if 语句数量: {control_visitor.if_count}")
print(f"  try 语句数量: {control_visitor.try_count}")
print(f"  捕获的异常类型: {control_visitor.except_handlers}")

# ========================================
# 第6章：提取函数调用和变量
# ========================================
print("\n【第6章：提取函数调用和变量】")
print("-" * 80)

code_calls = """
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
print(code_calls)

class CodeQualityChecker(ast.NodeVisitor):
    def __init__(self):
        self.issues = []
        self.in_loop = False
    
    def visit_For(self, node):
        self.in_loop = True
        self.generic_visit(node)
        self.in_loop = False
    
    def visit_While(self, node):
        self.in_loop = True
        self.generic_visit(node)
        self.in_loop = False
    
    def visit_Call(self, node):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        
        if self.in_loop and func_name in ["connect", "print"]:
            self.issues.append({
                "type": "performance",
                "message": f"在循环中调用 {func_name}() 可能导致性能问题"
            })
        
        self.generic_visit(node)

print("\n代码质量检查结果：")
tree = ast.parse(code_calls)
checker = CodeQualityChecker()
checker.visit(tree)

if checker.issues:
    for issue in checker.issues:
        print(f"  ⚠️  [{issue['type'].upper()}] {issue['message']}")
else:
    print("  ✅ 未发现明显问题")

# ========================================
# 第7章：AST 修改与代码生成
# ========================================
print("\n【第7章：AST 修改与代码生成】")
print("-" * 80)

code_transform = """
def hello(name):
    print(f"Hello, {name}!")
"""

print("原始代码：")
print(code_transform)

class PrintToLoggerTransformer(ast.NodeTransformer):
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            # 创建 logger.info() 调用
            logger_name = ast.Name(id="logger", ctx=ast.Load())
            info_attr = ast.Attribute(value=logger_name, attr="info", ctx=ast.Load())
            return ast.Call(func=info_attr, args=node.args, keywords=node.keywords)
        return node

# 解析、转换、重新生成代码
tree = ast.parse(code_transform)
transformer = PrintToLoggerTransformer()
modified_tree = transformer.visit(tree)

# 修复行号信息
ast.fix_missing_locations(modified_tree)

# 生成修改后的代码
from astunparse import unparse

print("\n将 print() 替换为 logger.info()：")
print(unparse(modified_tree))

# ========================================
# 第8章：综合实战 - 提取代码指纹
# ========================================
print("\n【第8章：综合实战 - 提取代码指纹】")
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

class CodeFingerprintExtractor(ast.NodeVisitor):
    def __init__(self):
        self.fingerprint = {
            "imports": [],
            "functions": [],
            "function_calls": [],
            "libraries_used": set()
        }
    
    def visit_Import(self, node):
        for name in node.names:
            lib = name.name.split('.')[0]
            self.fingerprint["imports"].append(lib)
            self.fingerprint["libraries_used"].add(lib)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        if node.module:
            lib = node.module.split('.')[0]
            self.fingerprint["imports"].append(lib)
            self.fingerprint["libraries_used"].add(lib)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        self.fingerprint["functions"].append(node.name)
        self.generic_visit(node)
    
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.fingerprint["function_calls"].append(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.fingerprint["function_calls"].append(node.func.attr)
        self.generic_visit(node)

print("\n提取代码指纹：")
tree = ast.parse(code_fingerprint)
fp_extractor = CodeFingerprintExtractor()
fp_extractor.visit(tree)

print("\n代码指纹：")
print(f"  使用的库: {list(fp_extractor.fingerprint['libraries_used'])}")
print(f"  定义的函数: {fp_extractor.fingerprint['functions']}")
print(f"  调用的函数: {fp_extractor.fingerprint['function_calls'][:10]}...")

print("\n" + "=" * 80)
print("Python 标准库 AST 模块学习教程完成！")
print("=" * 80)
# d:\mycode\ast_learning.py
import libcst as cst

print("=" * 80)
print("AST 学习教程 - 从零开始掌握 LibCST")
print("=" * 80)

# ========================================
# 第1章：AST 基础概念
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
module = cst.parse_module(code_sample)
print("\n解析后的 AST 结构：")
print(module)

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

class BasicVisitor(cst.CSTVisitor):
    def __init__(self):
        self.function_count = 0
        self.for_loop_count = 0
        self.function_names = []
        self.function_calls = []
    
    def visit_FunctionDef(self, node):
        self.function_count += 1
        self.function_names.append(node.name.value)
        print(f"  发现函数定义: {node.name.value}")
    
    def visit_For(self, node):
        self.for_loop_count += 1
        print(f"  发现 for 循环")
    
    def visit_Call(self, node):
        if isinstance(node.func, cst.Name):
            func_name = node.func.value
            self.function_calls.append(func_name)
            print(f"  发现函数调用: {func_name}()")

print("\n开始遍历 AST：")
visitor = BasicVisitor()
wrapper = cst.metadata.MetadataWrapper(cst.parse_module(code_visitor))
wrapper.visit(visitor)

print(f"\n统计结果：")
print(f"  函数定义数量: {visitor.function_count}")
print(f"  函数名称列表: {visitor.function_names}")
print(f"  for 循环数量: {visitor.for_loop_count}")
print(f"  函数调用列表: {visitor.function_calls}")

# ========================================
# 第3章：提取函数信息（参数、返回值、装饰器）
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

class FunctionInfoVisitor(cst.CSTVisitor):
    def __init__(self):
        self.functions = []
    
    def visit_FunctionDef(self, node):
        func_info = {
            "name": node.name.value,
            "decorators": [],
            "parameters": [],
            "return_type": None
        }
        
        # 提取装饰器
        for decorator in node.decorators:
            if isinstance(decorator.decorator, cst.Name):
                func_info["decorators"].append(decorator.decorator.value)
            elif isinstance(decorator.decorator, cst.Call):
                if isinstance(decorator.decorator.func, cst.Name):
                    func_info["decorators"].append(decorator.decorator.func.value)
        
        # 提取参数
        for param in node.params.params:
            if isinstance(param, cst.Param):
                param_name = param.name.value
                param_type = None
                if param.annotation:
                    if isinstance(param.annotation.annotation, cst.Name):
                        param_type = param.annotation.annotation.value
                func_info["parameters"].append(f"{param_name}: {param_type}")
        
        # 提取返回类型
        if node.returns:
            if isinstance(node.returns.annotation, cst.Name):
                func_info["return_type"] = node.returns.annotation.value
        
        self.functions.append(func_info)

print("\n提取函数信息：")
func_visitor = FunctionInfoVisitor()
wrapper = cst.metadata.MetadataWrapper(cst.parse_module(code_function))
wrapper.visit(func_visitor)

for func in func_visitor.functions:
    print(f"\n函数名: {func['name']}")
    print(f"  装饰器: {func['decorators']}")
    print(f"  参数: {func['parameters']}")
    print(f"  返回类型: {func['return_type']}")

# ========================================
# 第4章：提取变量赋值和导入语句
# ========================================
print("\n【第4章：提取变量和导入】")
print("-" * 80)

code_imports = """
import os
import sys
from typing import List, Dict
import pandas as pd
from numpy import array

API_KEY = "secret123"
database_url = "localhost:5432"
items = [1, 2, 3]
"""

print("示例代码：")
print(code_imports)

class ImportAndVariableVisitor(cst.CSTVisitor):
    def __init__(self):
        self.imports = []
        self.variables = []
    
    def visit_Import(self, node):
        for name in node.names:
            if isinstance(name, cst.ImportAlias):
                module_name = name.name.value
                alias = name.asname.name.value if name.asname else None
                self.imports.append({
                    "type": "import",
                    "module": module_name,
                    "alias": alias
                })
    
    def visit_ImportFrom(self, node):
        module = node.module.value if node.module else ""
        names = []
        for name in node.names:
            if isinstance(name, cst.ImportAlias):
                names.append(name.name.value)
        self.imports.append({
            "type": "from ... import",
            "module": module,
            "names": names
        })
    
    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target.target, cst.Name):
                var_name = target.target.value
                self.variables.append(var_name)

print("\n提取导入和变量：")
iv_visitor = ImportAndVariableVisitor()
wrapper = cst.metadata.MetadataWrapper(cst.parse_module(code_imports))
wrapper.visit(iv_visitor)

print("\n导入语句：")
for imp in iv_visitor.imports:
    if imp["type"] == "import":
        alias = f" as {imp['alias']}" if imp['alias'] else ""
        print(f"  import {imp['module']}{alias}")
    else:
        print(f"  from {imp['module']} import {', '.join(imp['names'])}")

print(f"\n变量定义：")
print(f"  {iv_visitor.variables}")

# ========================================
# 第5章：提取类信息
# ========================================
print("\n【第5章：提取类信息】")
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

class ClassInfoVisitor(cst.CSTVisitor):
    def __init__(self):
        self.classes = []
    
    def visit_ClassDef(self, node):
        class_info = {
            "name": node.name.value,
            "bases": [],
            "methods": []
        }
        
        # 提取基类
        for base in node.bases:
            if isinstance(base, cst.Name):
                class_info["bases"].append(base.value)
        
        # 提取方法
        for stmt in node.body.body:
            if isinstance(stmt, cst.FunctionDef):
                class_info["methods"].append(stmt.name.value)
        
        self.classes.append(class_info)

print("\n提取类信息：")
class_visitor = ClassInfoVisitor()
wrapper = cst.metadata.MetadataWrapper(cst.parse_module(code_class))
wrapper.visit(class_visitor)

for cls in class_visitor.classes:
    print(f"\n类名: {cls['name']}")
    print(f"  继承自: {cls['bases']}")
    print(f"  方法: {cls['methods']}")

# ========================================
# 第6章：条件语句和异常处理
# ========================================
print("\n【第6章：条件语句和异常处理】")
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

class ControlFlowVisitor(cst.CSTVisitor):
    def __init__(self):
        self.if_count = 0
        self.try_count = 0
        self.except_handlers = []
    
    def visit_If(self, node):
        self.if_count += 1
        print(f"  发现 if 语句")
    
    def visit_Try(self, node):
        self.try_count += 1
        print(f"  发现 try 语句")
        
        for handler in node.handlers:
            if handler.type:
                if isinstance(handler.type, cst.Name):
                    exception_type = handler.type.value
                    self.except_handlers.append(exception_type)
                    print(f"    捕获异常: {exception_type}")

print("\n分析控制流：")
control_visitor = ControlFlowVisitor()
wrapper = cst.metadata.MetadataWrapper(cst.parse_module(code_control))
wrapper.visit(control_visitor)

print(f"\n统计：")
print(f"  if 语句数量: {control_visitor.if_count}")
print(f"  try 语句数量: {control_visitor.try_count}")
print(f"  捕获的异常类型: {control_visitor.except_handlers}")

# ========================================
# 第7章：提取字符串和注释
# ========================================
print("\n【第7章：提取字符串和注释】")
print("-" * 80)

code_strings = """
# 这是一个单行注释

'''
这是一个多行文档字符串
'''

API_KEY = "sk-123456"  # API 密钥
password = "admin123"   # 密码

query = "SELECT * FROM users WHERE id = 1"
"""

print("示例代码：")
print(code_strings)

class StringAndCommentVisitor(cst.CSTVisitor):
    def __init__(self):
        self.strings = []
        self.comments = []
    
    def visit_SimpleString(self, node):
        self.strings.append(node.value)
    
    def visit_Comment(self, node):
        self.comments.append(node.value)

print("\n提取字符串和注释：")
sc_visitor = StringAndCommentVisitor()
wrapper = cst.metadata.MetadataWrapper(cst.parse_module(code_strings))
wrapper.visit(sc_visitor)

print("\n字符串内容：")
for s in sc_visitor.strings:
    print(f"  {s[:50]}...")

print(f"\n注释内容：")
for c in sc_visitor.comments:
    print(f"  {c}")

# ========================================
# 第8章：实际应用 - 代码质量检查
# ========================================
print("\n【第8章：实际应用 - 代码质量检查】")
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

class CodeQualityChecker(cst.CSTVisitor):
    def __init__(self):
        self.issues = []
        self.in_loop = False
    
    def visit_For(self, node):
        self.in_loop = True
        return True
    
    def leave_For(self, node):
        self.in_loop = False
    
    def visit_Call(self, node):
        func_name = ""
        if isinstance(node.func, cst.Name):
            func_name = node.func.value
        elif isinstance(node.func, cst.Attribute):
            func_name = node.func.attr.value
        
        if self.in_loop and func_name in ["connect", "print"]:
            self.issues.append({
                "type": "performance",
                "message": f"在循环中调用 {func_name}() 可能导致性能问题"
            })

print("\n代码质量检查结果：")
checker = CodeQualityChecker()
wrapper = cst.metadata.MetadataWrapper(cst.parse_module(code_quality))
wrapper.visit(checker)

if checker.issues:
    for issue in checker.issues:
        print(f"  ⚠️  [{issue['type'].upper()}] {issue['message']}")
else:
    print("  ✅ 未发现明显问题")

# ========================================
# 第9章：AST 修改 - Transformer 模式
# ========================================
print("\n【第9章：AST 修改 - Transformer 模式】")
print("-" * 80)

code_transform = """
def hello(name):
    print(f"Hello, {name}!")
"""

print("原始代码：")
print(code_transform)

class PrintToLoggerTransformer(cst.CSTTransformer):
    def visit_Call(self, node):
        if isinstance(node.func, cst.Name) and node.func.value == "print":
            return node.with_changes(
                func=cst.Attribute(
                    value=cst.Name("logger"),
                    attr=cst.Name("info")
                )
            )
        return node

print("\n将 print() 替换为 logger.info()：")
transformer = PrintToLoggerTransformer()
modified_module = cst.parse_module(code_transform).visit(transformer)
print(modified_module.code)

# ========================================
# 第10章：综合实战 - 提取代码指纹
# ========================================
print("\n【第10章：综合实战 - 提取代码指纹】")
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

class CodeFingerprintExtractor(cst.CSTVisitor):
    def __init__(self):
        self.fingerprint = {
            "imports": [],
            "functions": [],
            "function_calls": [],
            "libraries_used": set()
        }
    
    def visit_Import(self, node):
        for name in node.names:
            if isinstance(name, cst.ImportAlias):
                lib = name.name.value.split('.')[0]
                self.fingerprint["imports"].append(lib)
                self.fingerprint["libraries_used"].add(lib)
    
    def visit_ImportFrom(self, node):
        if node.module:
            if isinstance(node.module, cst.Name):
                lib = node.module.value
                self.fingerprint["imports"].append(lib)
                self.fingerprint["libraries_used"].add(lib)
    
    def visit_FunctionDef(self, node):
        self.fingerprint["functions"].append(node.name.value)
    
    def visit_Call(self, node):
        if isinstance(node.func, cst.Name):
            self.fingerprint["function_calls"].append(node.func.value)
        elif isinstance(node.func, cst.Attribute):
            self.fingerprint["function_calls"].append(node.func.attr.value)

print("\n提取代码指纹：")
fp_extractor = CodeFingerprintExtractor()
wrapper = cst.metadata.MetadataWrapper(cst.parse_module(code_fingerprint))
wrapper.visit(fp_extractor)

print("\n代码指纹：")
print(f"  使用的库: {list(fp_extractor.fingerprint['libraries_used'])}")
print(f"  定义的函数: {fp_extractor.fingerprint['functions']}")
print(f"  调用的函数: {fp_extractor.fingerprint['function_calls'][:10]}...")

print("\n" + "=" * 80)
print("AST 学习教程完成！")
print("=" * 80)
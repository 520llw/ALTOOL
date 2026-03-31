# -*- coding: utf-8 -*-
"""
后端代码结构测试脚本
验证文件结构和基础代码语法
"""

import ast
import sys
from pathlib import Path


def check_python_syntax(filepath: Path) -> bool:
    """检查 Python 文件语法是否正确"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        ast.parse(source)
        return True
    except SyntaxError as e:
        print(f"  ❌ 语法错误: {filepath} - {e}")
        return False


def check_file_exists(filepath: Path, description: str) -> bool:
    """检查文件是否存在"""
    if filepath.exists():
        print(f"  ✅ {description}: {filepath}")
        return True
    else:
        print(f"  ❌ 缺失: {description}: {filepath}")
        return False


def main():
    """主测试函数"""
    backend_dir = Path(__file__).parent
    
    print("=" * 60)
    print("AITOOL 后端代码结构测试")
    print("=" * 60)
    
    all_passed = True
    
    # 1. 检查基础结构文件
    print("\n📁 1. 基础结构文件检查:")
    files_to_check = [
        (backend_dir / "app" / "__init__.py", "App 包"),
        (backend_dir / "app" / "config.py", "配置模块"),
        (backend_dir / "app" / "database.py", "数据库模块"),
        (backend_dir / "app" / "dependencies.py", "依赖注入"),
        (backend_dir / "app" / "main.py", "FastAPI 入口"),
        (backend_dir / "requirements.txt", "依赖文件"),
    ]
    for filepath, desc in files_to_check:
        if not check_file_exists(filepath, desc):
            all_passed = False
    
    # 2. 检查模型文件
    print("\n📁 2. 模型文件检查:")
    model_files = [
        (backend_dir / "app" / "models" / "__init__.py", "模型包"),
        (backend_dir / "app" / "models" / "user.py", "用户模型"),
        (backend_dir / "app" / "models" / "param.py", "参数模型"),
        (backend_dir / "app" / "models" / "parse.py", "解析模型"),
    ]
    for filepath, desc in model_files:
        if not check_file_exists(filepath, desc):
            all_passed = False
    
    # 3. 检查 Schema 文件
    print("\n📁 3. Schema 文件检查:")
    schema_files = [
        (backend_dir / "app" / "schemas" / "__init__.py", "Schema 包"),
        (backend_dir / "app" / "schemas" / "common.py", "通用 Schema"),
        (backend_dir / "app" / "schemas" / "auth.py", "认证 Schema"),
        (backend_dir / "app" / "schemas" / "user.py", "用户 Schema"),
        (backend_dir / "app" / "schemas" / "param.py", "参数 Schema"),
    ]
    for filepath, desc in schema_files:
        if not check_file_exists(filepath, desc):
            all_passed = False
    
    # 4. 检查 API 路由文件
    print("\n📁 4. API 路由文件检查:")
    api_files = [
        (backend_dir / "app" / "api" / "__init__.py", "API 包"),
        (backend_dir / "app" / "api" / "v1" / "__init__.py", "API v1 包"),
        (backend_dir / "app" / "api" / "v1" / "auth.py", "认证 API"),
        (backend_dir / "app" / "api" / "v1" / "users.py", "用户 API"),
        (backend_dir / "app" / "api" / "v1" / "params.py", "参数 API"),
    ]
    for filepath, desc in api_files:
        if not check_file_exists(filepath, desc):
            all_passed = False
    
    # 5. 检查核心组件
    print("\n📁 5. 核心组件检查:")
    core_files = [
        (backend_dir / "app" / "core" / "__init__.py", "核心包"),
        (backend_dir / "app" / "core" / "security.py", "安全模块"),
    ]
    for filepath, desc in core_files:
        if not check_file_exists(filepath, desc):
            all_passed = False
    
    # 6. 语法检查
    print("\n🔍 6. Python 语法检查:")
    py_files = list(backend_dir.rglob("*.py"))
    py_files = [f for f in py_files if "__pycache__" not in str(f)]
    
    syntax_errors = 0
    for py_file in py_files:
        if not check_python_syntax(py_file):
            syntax_errors += 1
            all_passed = False
    
    if syntax_errors == 0:
        print(f"  ✅ 所有 {len(py_files)} 个文件语法正确")
    else:
        print(f"  ❌ 发现 {syntax_errors} 个语法错误")
    
    # 7. 目录结构展示
    print("\n📂 7. 后端目录结构:")
    
    def show_tree(path: Path, prefix: str = "", max_depth: int = 3, current_depth: int = 0):
        if current_depth > max_depth:
            return
        items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        for i, item in enumerate(items):
            if item.name.startswith("__pycache__") or item.name.endswith(".pyc"):
                continue
            is_last = i == len(items) - 1
            connector = "└── " if is_last else "├── "
            print(f"{prefix}{connector}{item.name}")
            if item.is_dir():
                new_prefix = prefix + ("    " if is_last else "│   ")
                show_tree(item, new_prefix, max_depth, current_depth + 1)
    
    show_tree(backend_dir, max_depth=4)
    
    # 总结
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有检查通过！后端代码结构完整。")
        print("\n下一步操作:")
        print("  1. 安装依赖: cd backend && pip install -r requirements.txt")
        print("  2. 启动服务: python -m app.main")
        print("  3. 访问文档: http://localhost:8000/docs")
    else:
        print("⚠️ 部分检查未通过，请检查上述错误。")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()

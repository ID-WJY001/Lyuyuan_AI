"""
通用工具函数
提供项目中频繁使用的常见功能
"""

import os
import sys
import subprocess
import yaml
import json
import re
from pathlib import Path

def load_env_file(verbose=True):
    """
    从.env文件加载环境变量，并禁用代理设置
    
    参数:
        verbose: 是否输出详细日志
    
    返回:
        bool: 是否成功加载了API密钥
    """
    # 定位项目根目录
    root_dir = get_project_root()
    env_path = os.path.join(root_dir, '.env')
    
    # 尝试从.env文件加载环境变量
    api_key_loaded = False
    if os.path.exists(env_path):
        if verbose:
            print("检测到.env文件，正在加载环境变量...")
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip()
                    if key == "DEEPSEEK_API_KEY" and value.strip():
                        api_key_loaded = True
                        if verbose:
                            print(f"成功从.env文件加载API密钥: {value.strip()[:5]}...{value.strip()[-5:]}")
        except Exception as e:
            if verbose:
                print(f"加载.env文件失败: {e}")
    elif verbose:
        print("未找到.env文件")
    
    # 禁用代理设置，避免API调用问题
    disable_proxy()
    
    return api_key_loaded

def disable_proxy(verbose=True):
    """
    禁用系统代理设置，避免API调用问题
    """
    proxy_vars = ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]
    for var in proxy_vars:
        if var in os.environ:
            if verbose:
                print(f"禁用代理设置: 删除环境变量 {var}")
            del os.environ[var]

def get_project_root():
    """
    获取项目根目录路径
    
    返回:
        str: 项目根目录的绝对路径
    """
    # 假设当前脚本在utils目录下，向上一级即为根目录
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def ensure_dependencies(requirements_path=None, verbose=True):
    """
    确保所有依赖已安装
    
    参数:
        requirements_path: 依赖文件路径，默认为web_app/requirements.txt
        verbose: 是否输出详细日志
    
    返回:
        bool: 是否成功安装所有依赖
    """
    root_dir = get_project_root()
    
    # 默认使用web应用的requirements.txt
    if requirements_path is None:
        requirements_path = os.path.join(root_dir, "web_app", "requirements.txt")
    
    if not os.path.exists(requirements_path):
        if verbose:
            print(f"错误: 找不到依赖文件 {requirements_path}")
        return False
    
    try:
        # 尝试安装依赖
        if verbose:
            print("正在安装依赖...")
        
        # 使用--prefer-binary选项以获得更好的兼容性
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--prefer-binary", "-r", requirements_path],
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            if verbose:
                print(f"安装依赖失败: {result.stderr[:500]}...")  # 只显示错误的前500个字符
            return False
        
        if verbose:
            print("依赖安装成功!")
        return True
    except Exception as e:
        if verbose:
            print(f"安装依赖时发生错误: {str(e)}")
        return False

def ensure_directories(*dirs):
    """
    确保指定的所有目录存在
    
    参数:
        *dirs: 要确保存在的目录路径列表
    """
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)

def load_config(config_type, character_id=None):
    """
    统一加载配置文件的函数
    
    参数:
    - config_type: 配置类型，如'affection'、'character'等
    - character_id: 角色ID，用于加载特定角色的配置
    
    返回:
    - 配置数据（字典格式）
    """
    project_root = get_project_root()
    config_dir = os.path.join(project_root, "config")
    
    # 不同类型配置的处理逻辑
    if config_type == "affection":
        # 优先使用根目录下的affection_config.json
        config_path = os.path.join(config_dir, "affection_config.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        # 回退到角色目录下的配置
        config_path = os.path.join(config_dir, "characters", "affection_config.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
                
    elif config_type == "character":
        if character_id:
            # 尝试从characters目录加载特定角色
            config_path = os.path.join(config_dir, "characters", f"{character_id}.yaml")
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
        else:
            # 尝试加载默认角色配置
            config_path = os.path.join(config_dir, "character.yaml")
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
    
    # 如果找不到配置文件，返回空字典
    print(f"警告: 无法找到配置文件: {config_type}" + (f" 角色: {character_id}" if character_id else ""))
    return {} 

def list_duplicate_managers():
    """
    检查并列出项目中的所有管理器类，帮助识别可能的重复功能
    
    返回:
    - 字典，键为管理器类型，值为找到的实现列表
    """
    project_root = get_project_root()
    
    # 需要搜索的管理器类型
    manager_types = {
        "GameManager": [],
        "SceneManager": [],
        "AffectionManager": [],
        "DialogueSystem": [],
        "TopicManager": [],
        "StorylineManager": [],
        "CharacterFactory": [],
        "AchievementSystem": []
    }
    
    # 搜索Python文件
    for root, dirs, files in os.walk(project_root):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, project_root)
                
                # 跳过__pycache__目录
                if "__pycache__" in relative_path:
                    continue
                
                # 读取文件内容
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # 检查每种管理器类型
                        for manager_type in manager_types.keys():
                            class_pattern = rf"class\s+{manager_type}\b"
                            if re.search(class_pattern, content):
                                manager_types[manager_type].append(relative_path)
                except Exception as e:
                    print(f"读取文件 {file_path} 时出错: {str(e)}")
    
    return manager_types 
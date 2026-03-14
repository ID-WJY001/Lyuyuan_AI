"""测试角色配置加载器"""
import sys
import os

# 设置UTF-8编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.infrastructure.character_loader import get_character_loader


def test_character_loader():
    """测试角色加载器功能"""
    print("=" * 60)
    print("测试角色配置加载器")
    print("=" * 60)
    print()

    # 获取加载器
    loader = get_character_loader()
    print("[OK] 加载器初始化成功")
    print()

    # 测试1: 列出所有角色
    print("测试1: 列出所有角色")
    print("-" * 60)
    character_ids = loader.list_characters()
    print(f"找到 {len(character_ids)} 个角色配置:")
    for char_id in character_ids:
        print(f"  - {char_id}")
    print()

    # 测试2: 加载苏糖配置
    print("测试2: 加载苏糖配置")
    print("-" * 60)
    config = loader.load_character("su_tang")

    if config is None:
        print("[FAIL] 加载失败")
        return False

    print("[OK] 加载成功")
    print(f"  ID: {config.id}")
    print(f"  名称: {config.name}")
    print(f"  显示名称: {config.display_name}")
    print(f"  MBTI: {config.mbti}")
    print(f"  性格特征: {', '.join(config.traits)}")
    print(f"  关键词: {', '.join(config.keywords)}")
    print(f"  初始好感度: {config.initial_state.get('closeness')}")
    print()

    # 测试3: 配置验证
    print("测试3: 配置验证")
    print("-" * 60)
    errors = config.validate()
    if errors:
        print("✗ 验证失败:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✓ 配置验证通过")
    print()

    # 测试4: 转换为BaseCharacter配置
    print("测试4: 转换为BaseCharacter配置")
    print("-" * 60)
    try:
        base_config = config.to_base_character_config()
        print("✓ 转换成功")
        print(f"  角色键: {base_config.get('role_key')}")
        print(f"  角色名: {base_config.get('name')}")
        print(f"  玩家名: {base_config.get('player_name')}")
        print(f"  欢迎消息: {base_config.get('welcome_message')[:50]}...")
        print(f"  System Prompts数量: {len(base_config.get('system_prompts', []))}")
        print(f"  历史大小: {base_config.get('history_size')}")
    except Exception as e:
        print(f"✗ 转换失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    print()

    # 测试5: 重新加载
    print("测试5: 重新加载配置")
    print("-" * 60)
    config2 = loader.reload_character("su_tang")
    if config2:
        print("✓ 重新加载成功")
    else:
        print("✗ 重新加载失败")
        return False
    print()

    # 测试6: 加载不存在的角色
    print("测试6: 加载不存在的角色")
    print("-" * 60)
    config_none = loader.load_character("non_existent")
    if config_none is None:
        print("✓ 正确返回None")
    else:
        print("✗ 应该返回None但返回了配置")
        return False
    print()

    print("=" * 60)
    print("所有测试通过！✓")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_character_loader()
    sys.exit(0 if success else 1)

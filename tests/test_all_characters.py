#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试所有角色配置加载"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.infrastructure.character_loader.loader import CharacterLoader

def test_all_characters():
    """测试加载所有角色配置"""
    print("=" * 60)
    print("Test All Character Configurations")
    print("=" * 60)

    loader = CharacterLoader()
    character_ids = loader.list_characters()

    print(f"\nFound {len(character_ids)} character configs")

    all_passed = True

    for char_id in character_ids:
        print(f"\n{'=' * 60}")
        print(f"Testing: {char_id}")
        print("=" * 60)

        # Load config
        config = loader.load_character(char_id)
        if not config:
            print(f"X Load failed: {char_id}")
            all_passed = False
            continue

        print(f"OK Loaded successfully")
        print(f"  ID: {config.id}")
        print(f"  Name: {config.name}")
        print(f"  MBTI: {config.mbti}")
        print(f"  Initial closeness: {config.initial_state.get('closeness', 0)}")
        print(f"  Traits: {', '.join(config.traits[:3])}...")
        print(f"  Keywords: {', '.join(config.keywords[:3])}...")

        # Validate config
        errors = config.validate()
        if not errors:
            print(f"OK Config validation passed")
        else:
            print(f"X Config validation failed:")
            for error in errors:
                print(f"    - {error}")
            all_passed = False

        # Convert to BaseCharacter config
        try:
            base_config = config.to_base_character_config()
            print(f"OK Converted to BaseCharacter config")
            print(f"  Welcome: {base_config['welcome_message'][:30]}...")
        except Exception as e:
            print(f"X Conversion failed: {e}")
            all_passed = False

    print(f"\n{'=' * 60}")
    if all_passed:
        print("All character tests passed!")
    else:
        print("Some tests failed!")
    print("=" * 60)

    return all_passed

if __name__ == "__main__":
    success = test_all_characters()
    sys.exit(0 if success else 1)
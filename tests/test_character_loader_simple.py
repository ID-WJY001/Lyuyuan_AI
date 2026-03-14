"""Test Character Loader"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.infrastructure.character_loader import get_character_loader

def test():
    print("="*60)
    print("Testing Character Loader")
    print("="*60)
    print()

    loader = get_character_loader()
    print("[OK] Loader initialized")
    print()

    # Test 1: List characters
    print("Test 1: List all characters")
    print("-"*60)
    chars = loader.list_characters()
    print(f"Found {len(chars)} character(s):")
    for c in chars:
        print(f"  - {c}")
    print()

    # Test 2: Load su_tang
    print("Test 2: Load su_tang config")
    print("-"*60)
    config = loader.load_character("su_tang")
    if not config:
        print("[FAIL] Load failed")
        return False
    
    print("[OK] Load successful")
    print(f"  ID: {config.id}")
    print(f"  Name: {config.name}")
    print(f"  MBTI: {config.mbti}")
    print(f"  Traits: {', '.join(config.traits)}")
    print()

    # Test 3: Validate
    print("Test 3: Validate config")
    print("-"*60)
    errors = config.validate()
    if errors:
        print("[FAIL] Validation failed:")
        for e in errors:
            print(f"  - {e}")
        return False
    print("[OK] Validation passed")
    print()

    # Test 4: Convert to BaseCharacter config
    print("Test 4: Convert to BaseCharacter config")
    print("-"*60)
    try:
        base_config = config.to_base_character_config()
        print("[OK] Conversion successful")
        print(f"  role_key: {base_config.get('role_key')}")
        print(f"  name: {base_config.get('name')}")
        print(f"  player_name: {base_config.get('player_name')}")
        print(f"  history_size: {base_config.get('history_size')}")
    except Exception as e:
        print(f"[FAIL] Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    print()

    print("="*60)
    print("All tests passed!")
    print("="*60)
    return True

if __name__ == "__main__":
    success = test()
    sys.exit(0 if success else 1)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试BaseCharacter事件集成"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.infrastructure.events import Event, EventType, get_event_bus
from backend.infrastructure.character_loader.loader import CharacterLoader


def test_character_events():
    """测试角色事件集成"""
    print("=" * 60)
    print("Testing Character Event Integration")
    print("=" * 60)

    # 获取事件总线
    event_bus = get_event_bus()
    event_bus.clear_history()

    # 记录接收到的事件
    received_events = []

    def event_logger(event: Event):
        received_events.append(event)
        print(f"  Event: {event.event_type.value}")
        print(f"    Data: {event.data}")

    # 订阅所有事件类型
    for event_type in EventType:
        event_bus.subscribe(event_type, event_logger)

    print("\n[OK] Subscribed to all event types")

    # 测试1: 加载角色配置并创建角色
    print("\nTest 1: Load character and start game")
    print("-" * 60)

    loader = CharacterLoader()
    config_data = loader.load_character("su_tang")
    if not config_data:
        print("[ERROR] Failed to load su_tang config")
        return

    base_config = config_data.to_base_character_config()

    # 导入BaseCharacter
    from backend.domain.characters.base_character import BaseCharacter

    character = BaseCharacter(config=base_config)
    print("[OK] Character created")

    # 开始新游戏 - 应该触发GAME_STARTED事件
    character.start_new_game(is_new_game=True)
    print("[OK] Game started")

    # 检查是否收到GAME_STARTED事件
    game_started_events = [e for e in received_events if e.event_type == EventType.GAME_STARTED]
    assert len(game_started_events) == 1, "Should receive GAME_STARTED event"
    print(f"[OK] Received {len(game_started_events)} GAME_STARTED event(s)")

    # 测试2: 好感度变化
    print("\nTest 2: Closeness change")
    print("-" * 60)

    initial_closeness = character.game_state.get("closeness", 30)
    print(f"Initial closeness: {initial_closeness}")

    # 手动触发好感度变化
    character._update_closeness(10)

    # 检查是否收到CLOSENESS_CHANGED事件
    closeness_events = [e for e in received_events if e.event_type == EventType.CLOSENESS_CHANGED]
    assert len(closeness_events) == 1, "Should receive CLOSENESS_CHANGED event"
    print(f"[OK] Received {len(closeness_events)} CLOSENESS_CHANGED event(s)")

    event_data = closeness_events[0].data
    assert event_data["old_value"] == initial_closeness
    assert event_data["new_value"] == initial_closeness + 10
    assert event_data["delta"] == 10
    print(f"[OK] Event data correct: {event_data['old_value']} -> {event_data['new_value']}")

    # 测试3: 关系状态变化
    print("\nTest 3: Relationship state change")
    print("-" * 60)

    # 大幅提升好感度以触发关系状态变化
    character._update_closeness(20)  # 现在应该是 40+，进入"朋友"阶段

    relationship_events = [e for e in received_events if e.event_type == EventType.RELATIONSHIP_CHANGED]
    if len(relationship_events) > 0:
        print(f"[OK] Received {len(relationship_events)} RELATIONSHIP_CHANGED event(s)")
        for event in relationship_events:
            print(f"  {event.data['old_state']} -> {event.data['new_state']}")
    else:
        print("[INFO] No relationship state change (closeness not high enough)")

    # 测试4: 保存游戏
    print("\nTest 4: Save game")
    print("-" * 60)

    result = character.save(slot="test_slot")
    assert result, "Save should succeed"
    print("[OK] Game saved")

    save_events = [e for e in received_events if e.event_type == EventType.GAME_SAVED]
    assert len(save_events) == 1, "Should receive GAME_SAVED event"
    print(f"[OK] Received {len(save_events)} GAME_SAVED event(s)")

    # 测试5: 加载游戏
    print("\nTest 5: Load game")
    print("-" * 60)

    result = character.load(slot="test_slot")
    assert result, "Load should succeed"
    print("[OK] Game loaded")

    load_events = [e for e in received_events if e.event_type == EventType.GAME_LOADED]
    assert len(load_events) == 1, "Should receive GAME_LOADED event"
    print(f"[OK] Received {len(load_events)} GAME_LOADED event(s)")

    # 测试6: 事件历史
    print("\nTest 6: Event history")
    print("-" * 60)

    history = event_bus.get_history()
    print(f"[OK] Total events in history: {len(history)}")

    # 按类型统计
    event_counts = {}
    for event in history:
        event_type = event.event_type.value
        event_counts[event_type] = event_counts.get(event_type, 0) + 1

    print("\nEvent counts by type:")
    for event_type, count in sorted(event_counts.items()):
        print(f"  {event_type}: {count}")

    print("\n" + "=" * 60)
    print("All integration tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_character_events()
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试事件系统"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.infrastructure.events import Event, EventBus, EventType, get_event_bus


def test_event_bus():
    """测试事件总线基础功能"""
    print("=" * 60)
    print("Testing Event System")
    print("=" * 60)

    # 创建事件总线
    bus = EventBus()
    print("\n[OK] Event bus created")

    # 测试1: 订阅和发布事件
    print("\nTest 1: Subscribe and publish events")
    print("-" * 60)

    received_events = []

    def handler(event: Event):
        received_events.append(event)
        print(f"  Handler received: {event.event_type}")

    bus.subscribe(EventType.MESSAGE_SENT, handler)
    print("[OK] Subscribed to MESSAGE_SENT")

    event = Event(
        event_type=EventType.MESSAGE_SENT,
        data={"message": "Hello", "user": "player"},
        source="test"
    )
    bus.publish(event)
    print(f"[OK] Published event: {event.event_id[:8]}")

    assert len(received_events) == 1
    assert received_events[0].event_type == EventType.MESSAGE_SENT
    print("[OK] Event received by handler")

    # 测试2: 多个订阅者
    print("\nTest 2: Multiple subscribers")
    print("-" * 60)

    received_count = [0]

    def handler2(event: Event):
        received_count[0] += 1

    bus.subscribe(EventType.MESSAGE_SENT, handler2)
    print("[OK] Added second subscriber")

    event2 = Event(
        event_type=EventType.MESSAGE_SENT,
        data={"message": "World"},
        source="test"
    )
    bus.publish(event2)

    assert received_count[0] == 1
    assert len(received_events) == 2
    print("[OK] Both handlers received the event")

    # 测试3: 事件历史
    print("\nTest 3: Event history")
    print("-" * 60)

    history = bus.get_history()
    print(f"[OK] History contains {len(history)} events")
    assert len(history) == 2

    history_filtered = bus.get_history(event_type=EventType.MESSAGE_SENT)
    print(f"[OK] Filtered history contains {len(history_filtered)} MESSAGE_SENT events")
    assert len(history_filtered) == 2

    # 测试4: 取消订阅
    print("\nTest 4: Unsubscribe")
    print("-" * 60)

    bus.unsubscribe(EventType.MESSAGE_SENT, handler)
    print("[OK] Unsubscribed first handler")

    event3 = Event(
        event_type=EventType.MESSAGE_SENT,
        data={"message": "After unsubscribe"},
        source="test"
    )
    bus.publish(event3)

    assert len(received_events) == 2  # Should not increase
    assert received_count[0] == 2  # Should increase
    print("[OK] Only second handler received the event")

    # 测试5: 不同事件类型
    print("\nTest 5: Different event types")
    print("-" * 60)

    closeness_events = []

    def closeness_handler(event: Event):
        closeness_events.append(event)

    bus.subscribe(EventType.CLOSENESS_CHANGED, closeness_handler)
    print("[OK] Subscribed to CLOSENESS_CHANGED")

    event4 = Event(
        event_type=EventType.CLOSENESS_CHANGED,
        data={"old_value": 30, "new_value": 35},
        source="character"
    )
    bus.publish(event4)

    assert len(closeness_events) == 1
    assert closeness_events[0].data["new_value"] == 35
    print("[OK] CLOSENESS_CHANGED event handled correctly")

    # 测试6: 全局事件总线
    print("\nTest 6: Global event bus")
    print("-" * 60)

    global_bus = get_event_bus()
    print("[OK] Got global event bus instance")

    global_bus2 = get_event_bus()
    assert global_bus is global_bus2
    print("[OK] Global event bus is singleton")

    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_event_bus()
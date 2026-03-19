"""Tests for memory systems."""

import pytest
from agentforge.core.memory import SharedMemory, ConversationMemory, MemoryEntry
from agentforge.core.message import Message, UserMessage, AgentMessage


def test_memory_entry_creation():
    """Test memory entry creation."""
    entry = MemoryEntry(
        key="test",
        value="test_value",
        tags=["important"],
    )

    assert entry.key == "test"
    assert entry.value == "test_value"
    assert "important" in entry.tags
    assert entry.access_count == 0


def test_shared_memory_store_and_retrieve():
    """Test storing and retrieving from shared memory."""
    memory = SharedMemory()

    memory.store("key1", "value1", tags=["general"])
    result = memory.retrieve("key1")

    assert result == "value1"
    assert memory.retrieve("key1")  # Access count increases


def test_shared_memory_search():
    """Test memory search."""
    memory = SharedMemory()

    memory.store("name", "Alice")
    memory.store("role", "Engineer")
    memory.store("location", "NYC")

    results = memory.search("Engineer")
    assert len(results) > 0


def test_shared_memory_by_tag():
    """Test retrieving by tag."""
    memory = SharedMemory()

    memory.store("data1", "value1", tags=["important"])
    memory.store("data2", "value2", tags=["important"])
    memory.store("data3", "value3", tags=["temp"])

    important = memory.retrieve_by_tag("important")
    assert len(important) == 2


def test_conversation_memory():
    """Test conversation memory."""
    conv_mem = ConversationMemory()

    messages1 = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]

    conv_mem.add_turn(messages1)
    retrieved = conv_mem.get_turn(0)

    assert len(retrieved) == 2
    assert retrieved[0]["content"] == "Hello"


def test_conversation_memory_recent_turns():
    """Test getting recent turns."""
    conv_mem = ConversationMemory()

    for i in range(5):
        conv_mem.add_turn([{"role": "user", "content": f"Message {i}"}])

    recent = conv_mem.get_recent_turns(2)
    assert len(recent) == 2

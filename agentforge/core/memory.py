"""Shared memory system for agents."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from collections import defaultdict
import json


@dataclass
class MemoryEntry:
    """Single memory entry with metadata."""

    key: str
    value: Any
    access_count: int = 0
    relevance_score: float = 1.0
    tags: List[str] = field(default_factory=list)

    def increment_access(self) -> None:
        """Increment access count."""
        self.access_count += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "key": self.key,
            "value": str(self.value),
            "access_count": self.access_count,
            "relevance_score": self.relevance_score,
            "tags": self.tags,
        }


class SharedMemory:
    """Shared memory system accessible to all agents."""

    def __init__(self, max_entries: int = 10000):
        """Initialize shared memory."""
        self.max_entries = max_entries
        self._storage: Dict[str, MemoryEntry] = {}
        self._index: Dict[str, List[str]] = defaultdict(list)  # tag -> keys
        self._access_log: List[str] = []

    def store(
        self,
        key: str,
        value: Any,
        tags: Optional[List[str]] = None,
        relevance: float = 1.0,
    ) -> None:
        """Store value in memory."""
        if len(self._storage) >= self.max_entries:
            # Remove least accessed entry
            least_accessed = min(self._storage.values(), key=lambda e: e.access_count)
            self.delete(least_accessed.key)

        tags = tags or []
        entry = MemoryEntry(
            key=key, value=value, relevance_score=relevance, tags=tags
        )
        self._storage[key] = entry

        # Index by tags
        for tag in tags:
            if key not in self._index[tag]:
                self._index[tag].append(key)

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve value by key."""
        if key in self._storage:
            self._storage[key].increment_access()
            self._access_log.append(key)
            return self._storage[key].value
        return None

    def retrieve_by_tag(self, tag: str) -> List[Any]:
        """Retrieve all values with given tag."""
        keys = self._index.get(tag, [])
        values = []
        for key in keys:
            if key in self._storage:
                self._storage[key].increment_access()
                values.append(self._storage[key].value)
        return values

    def search(self, query: str, limit: int = 10) -> List[tuple[str, Any]]:
        """Search memory by keyword (simple substring match)."""
        results = []
        for key, entry in self._storage.items():
            if query.lower() in key.lower() or query.lower() in str(
                entry.value
            ).lower():
                results.append((key, entry.value))
        # Sort by relevance and access count
        results.sort(
            key=lambda x: self._storage[x[0]].relevance_score
            * (1 + self._storage[x[0]].access_count),
            reverse=True,
        )
        return results[:limit]

    def delete(self, key: str) -> bool:
        """Delete entry from memory."""
        if key in self._storage:
            entry = self._storage.pop(key)
            # Remove from indices
            for tag in entry.tags:
                if key in self._index[tag]:
                    self._index[tag].remove(key)
            return True
        return False

    def get_all_keys(self) -> List[str]:
        """Get all keys in memory."""
        return list(self._storage.keys())

    def clear(self) -> None:
        """Clear all memory."""
        self._storage.clear()
        self._index.clear()
        self._access_log.clear()

    def size(self) -> int:
        """Get number of entries in memory."""
        return len(self._storage)

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        if not self._storage:
            return {"total_entries": 0, "avg_access_count": 0}

        access_counts = [e.access_count for e in self._storage.values()]
        return {
            "total_entries": len(self._storage),
            "avg_access_count": sum(access_counts) / len(access_counts),
            "max_access_count": max(access_counts),
            "unique_tags": len(self._index),
            "access_log_size": len(self._access_log),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert memory state to dictionary."""
        return {
            key: entry.to_dict() for key, entry in self._storage.items()
        }


class ConversationMemory:
    """Memory for conversation history with turn-based structure."""

    def __init__(self):
        """Initialize conversation memory."""
        self.turns: List[Dict[str, Any]] = []
        self.current_turn = 0

    def add_turn(self, messages: List[Dict[str, Any]]) -> None:
        """Add a conversation turn."""
        self.turns.append({"turn": self.current_turn, "messages": messages})
        self.current_turn += 1

    def get_turn(self, turn_num: int) -> Optional[List[Dict[str, Any]]]:
        """Get messages from a specific turn."""
        for turn_data in self.turns:
            if turn_data["turn"] == turn_num:
                return turn_data["messages"]
        return None

    def get_recent_turns(self, num_turns: int) -> List[Dict[str, Any]]:
        """Get recent turns."""
        return self.turns[-num_turns:] if num_turns > 0 else self.turns

    def clear(self) -> None:
        """Clear conversation history."""
        self.turns = []
        self.current_turn = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {"turns": self.turns, "current_turn": self.current_turn}

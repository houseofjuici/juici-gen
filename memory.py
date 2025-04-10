from typing import Dict, Any, List
from praisonai_tools import MemoryTool
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage
import json
import os

class MemoryManager:
    def __init__(self):
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.memory_tool = MemoryTool()
        self.context: Dict[str, Any] = {}
        self.persistence_file = "memory.json"

    def add_context(self, key: str, value: Any):
        """Add context to the memory."""
        self.context[key] = value
        self.memory_tool.add_memory(key, value)
        self._persist_memory()

    def get_context(self, key: str) -> Any:
        """Get context from memory."""
        return self.memory_tool.get_memory(key)

    def clear_context(self):
        """Clear all context from memory."""
        self.context = {}
        self.memory_tool.clear_memory()
        self._persist_memory()

    def add_message(self, message: BaseMessage):
        """Add a message to the conversation history."""
        self.memory.chat_memory.add_message(message)
        self._persist_memory()

    def get_messages(self) -> List[BaseMessage]:
        """Get all messages from the conversation history."""
        return self.memory.chat_memory.messages

    def clear_messages(self):
        """Clear all messages from the conversation history."""
        self.memory.clear()
        self._persist_memory()

    def _persist_memory(self):
        """Persist memory to disk."""
        try:
            data = {
                "context": self.context,
                "messages": [msg.dict() for msg in self.memory.chat_memory.messages]
            }
            with open(self.persistence_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error persisting memory: {e}")

    def load_memory(self):
        """Load memory from disk."""
        try:
            if os.path.exists(self.persistence_file):
                with open(self.persistence_file, 'r') as f:
                    data = json.load(f)
                    self.context = data.get("context", {})
                    messages = data.get("messages", [])
                    for msg in messages:
                        self.memory.chat_memory.add_message(BaseMessage.parse_obj(msg))
        except Exception as e:
            print(f"Error loading memory: {e}") 
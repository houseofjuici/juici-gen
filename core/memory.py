from typing import Dict, List, Any
import json
import os

class MemoryManager:
    def __init__(self):
        self.context = {}
        self.conversation_history = []
        self.memory_file = "memory.json"
    
    def add_context(self, key: str, value: Any):
        """Add context to memory"""
        self.context[key] = value
        self._save_memory()
    
    def get_context(self, key: str) -> Any:
        """Get context from memory"""
        return self.context.get(key)
    
    def clear_context(self):
        """Clear all context"""
        self.context = {}
        self._save_memory()
    
    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
        self._save_memory()
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.conversation_history
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self._save_memory()
    
    def _save_memory(self):
        """Save memory to file"""
        memory_data = {
            "context": self.context,
            "conversation_history": self.conversation_history
        }
        with open(self.memory_file, 'w') as f:
            json.dump(memory_data, f)
    
    def load_memory(self):
        """Load memory from file"""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                memory_data = json.load(f)
                self.context = memory_data.get("context", {})
                self.conversation_history = memory_data.get("conversation_history", []) 
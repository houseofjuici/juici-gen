from typing import Dict, Any, List, Optional
import base64
from datetime import datetime
import json
from .security import SecurityManager

class SecureChatManager:
    def __init__(self, embassai_config: Dict[str, str]):
        self.embassai_config = embassai_config
        self.security = SecurityManager()
        self.chat_history: List[Dict[str, Any]] = []
    
    def _encrypt_message(self, message: str) -> Dict[str, Any]:
        """Encrypt a message using Embassai encryption."""
        # Convert message to bytes
        message_bytes = message.encode('utf-8')
        
        # Encrypt using the encryption key
        encrypted_data = self.security.encrypt(
            message_bytes,
            self.embassai_config["encryption_key"]
        )
        
        return {
            "encrypted": True,
            "data": base64.b64encode(encrypted_data).decode('utf-8'),
            "room_id": self.embassai_config["room_id"],
            "timestamp": datetime.now().isoformat()
        }
    
    def _decrypt_message(self, encrypted_message: Dict[str, Any]) -> str:
        """Decrypt a message using Embassai encryption."""
        if not encrypted_message.get("encrypted"):
            return encrypted_message.get("data", "")
        
        # Decode the encrypted data
        encrypted_data = base64.b64decode(encrypted_message["data"])
        
        # Decrypt using the encryption key
        decrypted_data = self.security.decrypt(
            encrypted_data,
            self.embassai_config["encryption_key"]
        )
        
        return decrypted_data.decode('utf-8')
    
    async def send_message(self, message: str, secure: bool = True) -> Dict[str, Any]:
        """Send a message, optionally encrypting it."""
        if secure:
            encrypted_message = self._encrypt_message(message)
            self.chat_history.append({
                "type": "sent",
                "secure": True,
                "data": encrypted_message,
                "timestamp": datetime.now().isoformat()
            })
            return encrypted_message
        else:
            self.chat_history.append({
                "type": "sent",
                "secure": False,
                "data": message,
                "timestamp": datetime.now().isoformat()
            })
            return {"data": message}
    
    async def receive_message(self, message: Dict[str, Any]) -> str:
        """Receive and decrypt a message."""
        if message.get("encrypted"):
            decrypted = self._decrypt_message(message)
            self.chat_history.append({
                "type": "received",
                "secure": True,
                "data": message,
                "decrypted": decrypted,
                "timestamp": datetime.now().isoformat()
            })
            return decrypted
        else:
            self.chat_history.append({
                "type": "received",
                "secure": False,
                "data": message.get("data", ""),
                "timestamp": datetime.now().isoformat()
            })
            return message.get("data", "")
    
    def get_chat_history(self) -> List[Dict[str, Any]]:
        """Get the chat history with decrypted messages."""
        return self.chat_history 
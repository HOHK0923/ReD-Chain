from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
import os

class MessageEncryption:
    """Encrypt/decrypt messages between C2 and agents"""

    def __init__(self, password: str = None):
        if password is None:
            password = os.getenv("ENCRYPTION_KEY", "default-key-change-me")

        # Derive key from password
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'redchain_salt',  # In production, use random salt per node
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.cipher = Fernet(key)

    def encrypt(self, message: str) -> str:
        """Encrypt message"""
        encrypted = self.cipher.encrypt(message.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, encrypted_message: str) -> str:
        """Decrypt message"""
        encrypted = base64.urlsafe_b64decode(encrypted_message.encode())
        decrypted = self.cipher.decrypt(encrypted)
        return decrypted.decode()

# Global encryption instance
encryption = MessageEncryption()

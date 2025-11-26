from Crypto.Cipher import DES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import base64
import json
from typing import Tuple, Dict

class EncryptionManager:
    """Handles DES and RSA encryption/decryption"""
    
    @staticmethod
    def generate_des_key() -> bytes:
        """Generate a 8-byte DES key"""
        return get_random_bytes(8)
    
    @staticmethod
    def encrypt_des(data: str, key: bytes) -> str:
        """Encrypt data using DES"""
        try:
            cipher = DES.new(key, DES.MODE_ECB)
            # Pad data to 8-byte blocks
            padded_data = data.ljust(len(data) + (8 - len(data) % 8)) if len(data) % 8 != 0 else data
            encrypted = cipher.encrypt(padded_data.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            return f"Encryption error: {str(e)}"
    
    @staticmethod
    def decrypt_des(encrypted_data: str, key: bytes) -> str:
        """Decrypt DES encrypted data"""
        try:
            cipher = DES.new(key, DES.MODE_ECB)
            encrypted = base64.b64decode(encrypted_data.encode())
            decrypted = cipher.decrypt(encrypted).decode().strip()
            return decrypted
        except Exception as e:
            return f"Decryption error: {str(e)}"
    
    @staticmethod
    def generate_rsa_keys(key_size: int = 2048) -> Tuple[str, str]:
        """Generate RSA public and private keys"""
        key = RSA.generate(key_size)
        public_key = key.publickey().export_key().decode()
        private_key = key.export_key().decode()
        return public_key, private_key
    
    @staticmethod
    def encrypt_rsa(data: str, public_key_str: str) -> str:
        """Encrypt data using RSA public key"""
        try:
            public_key = RSA.import_key(public_key_str.encode())
            cipher = PKCS1_OAEP.new(public_key)
            encrypted = cipher.encrypt(data.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            return f"RSA encryption error: {str(e)}"
    
    @staticmethod
    def decrypt_rsa(encrypted_data: str, private_key_str: str) -> str:
        """Decrypt RSA encrypted data using private key"""
        try:
            private_key = RSA.import_key(private_key_str.encode())
            cipher = PKCS1_OAEP.new(private_key)
            decrypted = cipher.decrypt(base64.b64decode(encrypted_data.encode()))
            return decrypted.decode()
        except Exception as e:
            return f"RSA decryption error: {str(e)}"


class BankingSystem:
    """Main banking system with encryption integration"""
    
    def __init__(self):
        self.encryption_manager = EncryptionManager()
        self.des_key = None
        self.session_data = {}
    
    def set_session_des_key(self, key: bytes):
        """Set DES key for current session"""
        self.des_key = key
    
    def get_session_des_key(self) -> bytes:
        """Get current session DES key"""
        if self.des_key is None:
            self.des_key = self.encryption_manager.generate_des_key()
        return self.des_key
    
    def encrypt_transaction_data(self, transaction_data: Dict) -> Tuple[str, str]:
        """
        Encrypt transaction data using DES
        Returns encrypted_data and the base64 encoded key
        """
        try:
            key = self.get_session_des_key()
            json_data = json.dumps(transaction_data)
            encrypted = self.encryption_manager.encrypt_des(json_data, key)
            key_b64 = base64.b64encode(key).decode()
            return encrypted, key_b64
        except Exception as e:
            return f"Error: {str(e)}", ""
    
    def decrypt_transaction_data(self, encrypted_data: str, key_b64: str) -> Dict:
        """Decrypt transaction data using DES"""
        try:
            key = base64.b64decode(key_b64.encode())
            decrypted = self.encryption_manager.decrypt_des(encrypted_data, key)
            return json.loads(decrypted)
        except Exception as e:
            return {"error": str(e)}
    
    def create_secure_transaction_record(self, transaction_data: Dict, public_key: str) -> Dict:
        """
        Create a transaction record encrypted with both DES and RSA
        - Transaction details encrypted with DES
        - DES key encrypted with RSA public key
        """
        des_encrypted, des_key_b64 = self.encrypt_transaction_data(transaction_data)
        
        # Encrypt the DES key with RSA public key
        rsa_encrypted_key = self.encryption_manager.encrypt_rsa(des_key_b64, public_key)
        
        return {
            'encrypted_transaction': des_encrypted,
            'encrypted_des_key': rsa_encrypted_key,
            'timestamp': transaction_data.get('timestamp')
        }
    
    def retrieve_secure_transaction(self, secure_record: Dict, private_key: str) -> Dict:
        """Retrieve and decrypt a secure transaction record"""
        try:
            # Decrypt DES key using RSA private key
            des_key_b64 = self.encryption_manager.decrypt_rsa(
                secure_record['encrypted_des_key'],
                private_key
            )
            
            # Decrypt transaction data using DES
            transaction_data = self.decrypt_transaction_data(
                secure_record['encrypted_transaction'],
                des_key_b64
            )
            
            return transaction_data
        except Exception as e:
            return {"error": str(e)}
    
    def generate_transaction_summary(self, account_number: str, amount: float, tx_type: str) -> Dict:
        """Generate a transaction summary for encryption"""
        return {
            'account_number': account_number,
            'amount': amount,
            'transaction_type': tx_type,
            'timestamp': str(__import__('datetime').datetime.now()),
            'status': 'PENDING'
        }
    
    @staticmethod
    def verify_transaction_integrity(transaction: Dict, signature: str) -> bool:
        """Verify transaction hasn't been tampered with"""
        # For demo: simple checksum verification
        try:
            import hashlib
            data_str = json.dumps(transaction, sort_keys=True)
            computed_hash = hashlib.sha256(data_str.encode()).hexdigest()
            return computed_hash == signature
        except:
            return False
    
    @staticmethod
    def create_transaction_signature(transaction: Dict) -> str:
        """Create transaction signature for integrity verification"""
        import hashlib
        data_str = json.dumps(transaction, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

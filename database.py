import sqlite3
import hashlib
from datetime import datetime
from typing import Tuple, Optional, List, Dict

class BankingDatabase:
    """Handles all database operations for the banking system"""
    
    def __init__(self, db_name: str = "banking_system.db"):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                account_number TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                balance REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_number TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_number) REFERENCES users(account_number)
            )
        ''')
        
        # Keys table for RSA key storage
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rsa_keys (
                account_number TEXT PRIMARY KEY,
                public_key TEXT NOT NULL,
                private_key TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_number) REFERENCES users(account_number)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_account(self, username: str, password: str, full_name: str, initial_balance: float = 1000.0) -> Tuple[bool, str, str]:
        """Create new bank account"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Generate account number (simple format)
            cursor.execute("SELECT MAX(account_number) FROM users")
            result = cursor.fetchone()
            account_num = int(result[0] or 0) + 1001
            account_number = str(account_num)
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (account_number, username, password_hash, full_name, balance)
                VALUES (?, ?, ?, ?, ?)
            ''', (account_number, username, password_hash, full_name, initial_balance))
            
            conn.commit()
            conn.close()
            
            return True, account_number, "Account created successfully"
        except sqlite3.IntegrityError:
            return False, "", "Username already exists"
        except Exception as e:
            return False, "", str(e)
    
    def verify_login(self, username: str, password: str) -> Tuple[bool, str]:
        """Verify user credentials"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                SELECT account_number FROM users 
                WHERE username = ? AND password_hash = ?
            ''', (username, password_hash))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return True, result[0]
            return False, ""
        except Exception as e:
            return False, str(e)
    
    def get_account_info(self, account_number: str) -> Optional[Dict]:
        """Get user account information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT username, full_name, balance, created_at FROM users 
                WHERE account_number = ?
            ''', (account_number,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'username': result[0],
                    'full_name': result[1],
                    'balance': result[2],
                    'created_at': result[3]
                }
            return None
        except Exception as e:
            return None
    
    def deposit(self, account_number: str, amount: float, description: str = "Deposit") -> Tuple[bool, str, float]:
        """Deposit money to account"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT balance FROM users WHERE account_number = ?', (account_number,))
            result = cursor.fetchone()
            
            if not result:
                return False, "Account not found", 0.0
            
            new_balance = result[0] + amount
            
            cursor.execute('UPDATE users SET balance = ? WHERE account_number = ?', (new_balance, account_number))
            cursor.execute('''
                INSERT INTO transactions (account_number, transaction_type, amount, description)
                VALUES (?, ?, ?, ?)
            ''', (account_number, 'DEPOSIT', amount, description))
            
            conn.commit()
            conn.close()
            
            return True, f"Deposit successful. New balance: {new_balance}", new_balance
        except Exception as e:
            return False, str(e), 0.0
    
    def withdraw(self, account_number: str, amount: float, description: str = "Withdrawal") -> Tuple[bool, str, float]:
        """Withdraw money from account"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT balance FROM users WHERE account_number = ?', (account_number,))
            result = cursor.fetchone()
            
            if not result:
                return False, "Account not found", 0.0
            
            current_balance = result[0]
            
            if amount > current_balance:
                return False, "Insufficient balance", current_balance
            
            new_balance = current_balance - amount
            
            cursor.execute('UPDATE users SET balance = ? WHERE account_number = ?', (new_balance, account_number))
            cursor.execute('''
                INSERT INTO transactions (account_number, transaction_type, amount, description)
                VALUES (?, ?, ?, ?)
            ''', (account_number, 'WITHDRAWAL', amount, description))
            
            conn.commit()
            conn.close()
            
            return True, f"Withdrawal successful. New balance: {new_balance}", new_balance
        except Exception as e:
            return False, str(e), 0.0
    
    def transfer(self, from_account: str, to_account: str, amount: float) -> Tuple[bool, str]:
        """Transfer money between accounts"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if both accounts exist
            cursor.execute('SELECT balance FROM users WHERE account_number = ?', (from_account,))
            from_result = cursor.fetchone()
            
            cursor.execute('SELECT balance FROM users WHERE account_number = ?', (to_account,))
            to_result = cursor.fetchone()
            
            if not from_result or not to_result:
                return False, "One or both accounts not found"
            
            if amount > from_result[0]:
                return False, "Insufficient balance"
            
            # Perform transfer
            new_from_balance = from_result[0] - amount
            new_to_balance = to_result[0] + amount
            
            cursor.execute('UPDATE users SET balance = ? WHERE account_number = ?', (new_from_balance, from_account))
            cursor.execute('UPDATE users SET balance = ? WHERE account_number = ?', (new_to_balance, to_account))
            
            # Log transactions
            cursor.execute('''
                INSERT INTO transactions (account_number, transaction_type, amount, description)
                VALUES (?, ?, ?, ?)
            ''', (from_account, 'TRANSFER_OUT', amount, f"Transfer to {to_account}"))
            
            cursor.execute('''
                INSERT INTO transactions (account_number, transaction_type, amount, description)
                VALUES (?, ?, ?, ?)
            ''', (to_account, 'TRANSFER_IN', amount, f"Transfer from {from_account}"))
            
            conn.commit()
            conn.close()
            
            return True, f"Transfer successful"
        except Exception as e:
            return False, str(e)
    
    def get_transaction_history(self, account_number: str, limit: int = 10) -> List[Dict]:
        """Get recent transactions"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT transaction_id, transaction_type, amount, description, timestamp
                FROM transactions
                WHERE account_number = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (account_number, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            transactions = []
            for row in results:
                transactions.append({
                    'id': row[0],
                    'type': row[1],
                    'amount': row[2],
                    'description': row[3],
                    'timestamp': row[4]
                })
            
            return transactions
        except Exception as e:
            return []

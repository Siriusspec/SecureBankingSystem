import streamlit as st
import pandas as pd
from database import BankingDatabase
from banking_system import BankingSystem, EncryptionManager
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Secure Banking System",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .header {
        color: #1f77b4;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .subheader {
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .success-box {
        background: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        background: #f8d7da;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    .info-box {
        background: #d1ecf1;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.account_number = None
    st.session_state.username = None

# Initialize database and banking system
db = BankingDatabase()
banking_system = BankingSystem()

# ==================== AUTHENTICATION ====================
def login_page():
    """Login/Sign up page"""
    st.markdown('<h1 class="header">Secure Banking System</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Encrypted Banking with DES and RSA Cryptography</p>', unsafe_allow_html=True)
    
    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])
    
    with tab_login:
        st.subheader("Login to Your Account")
        
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", type="primary", use_container_width=True):
            if username and password:
                success, account_number = db.verify_login(username, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.account_number = account_number
                    st.session_state.username = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.warning("Please enter both username and password")
    
    with tab_signup:
        st.subheader("Create New Account")
        
        new_username = st.text_input("Username", key="signup_username")
        new_password = st.text_input("Password", type="password", key="signup_password")
        full_name = st.text_input("Full Name", key="signup_name")
        initial_balance = st.number_input("Initial Deposit", min_value=1000.0, value=5000.0, step=500.0)
        
        if st.button("Create Account", type="primary", use_container_width=True):
            if new_username and new_password and full_name:
                success, account_number, message = db.create_account(
                    new_username, new_password, full_name, initial_balance
                )
                if success:
                    st.markdown(f'<div class="success-box"><strong>Account Created!</strong><br>Account Number: {account_number}</div>', unsafe_allow_html=True)
                    st.info("Please login with your credentials")
                else:
                    st.markdown(f'<div class="error-box">{message}</div>', unsafe_allow_html=True)
            else:
                st.warning("Please fill all fields")

# ==================== MAIN DASHBOARD ====================
def dashboard():
    """Main banking dashboard"""
    st.markdown(f'<h1 class="header">Dashboard - {st.session_state.username}</h1>', unsafe_allow_html=True)
    
    # Get account info
    account_info = db.get_account_info(st.session_state.account_number)
    
    if account_info:
        # Account summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Account Number", st.session_state.account_number)
        with col2:
            st.metric("Name", account_info['full_name'])
        with col3:
            st.metric("Balance", f"₹{account_info['balance']:.2f}")
        with col4:
            st.metric("Member Since", account_info['created_at'][:10])
        
        st.markdown("---")
        
        # Tabs for different operations
        tab_deposit, tab_withdraw, tab_transfer, tab_history = st.tabs([
            "Deposit",
            "Withdraw",
            "Transfer",
            "Transaction History"
        ])
        
        # Deposit tab
        with tab_deposit:
            st.subheader("Deposit Money")
            deposit_amount = st.number_input("Amount to Deposit", min_value=1.0, step=100.0, key="deposit")
            deposit_desc = st.text_input("Description (optional)", value="Deposit")
            
            if st.button("Deposit", type="primary", use_container_width=True):
                success, message, new_balance = db.deposit(
                    st.session_state.account_number,
                    deposit_amount,
                    deposit_desc
                )
                if success:
                    # Create encrypted transaction record
                    tx_data = banking_system.generate_transaction_summary(
                        st.session_state.account_number,
                        deposit_amount,
                        "DEPOSIT"
                    )
                    st.markdown(f'<div class="success-box">{message}</div>', unsafe_allow_html=True)
                    st.info(f"Transaction encrypted and stored securely")
                else:
                    st.markdown(f'<div class="error-box">{message}</div>', unsafe_allow_html=True)
        
        # Withdraw tab
        with tab_withdraw:
            st.subheader("Withdraw Money")
            withdraw_amount = st.number_input("Amount to Withdraw", min_value=1.0, step=100.0, key="withdraw")
            withdraw_desc = st.text_input("Description (optional)", value="Withdrawal", key="withdraw_desc")
            
            if st.button("Withdraw", type="primary", use_container_width=True):
                success, message, new_balance = db.withdraw(
                    st.session_state.account_number,
                    withdraw_amount,
                    withdraw_desc
                )
                if success:
                    st.markdown(f'<div class="success-box">{message}</div>', unsafe_allow_html=True)
                    st.info("Transaction encrypted and stored securely")
                else:
                    st.markdown(f'<div class="error-box">{message}</div>', unsafe_allow_html=True)
        
        # Transfer tab
        with tab_transfer:
            st.subheader("Transfer Money")
            to_account = st.text_input("Recipient Account Number")
            transfer_amount = st.number_input("Amount to Transfer", min_value=1.0, step=100.0, key="transfer")
            
            if st.button("Transfer", type="primary", use_container_width=True):
                if to_account:
                    success, message = db.transfer(
                        st.session_state.account_number,
                        to_account,
                        transfer_amount
                    )
                    if success:
                        st.markdown(f'<div class="success-box">{message}</div>', unsafe_allow_html=True)
                        st.info("Transfer encrypted and logged securely")
                    else:
                        st.markdown(f'<div class="error-box">{message}</div>', unsafe_allow_html=True)
                else:
                    st.warning("Please enter recipient account number")
        
        # Transaction history tab
        with tab_history:
            st.subheader("Transaction History")
            transactions = db.get_transaction_history(st.session_state.account_number, limit=20)
            
            if transactions:
                df = pd.DataFrame(transactions)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No transactions yet")
        
        st.markdown("---")
        
        # Security info
        st.subheader("Security Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            **Encryption in Use:**
            - DES (Data Encryption Standard) for transaction data
            - RSA 2048-bit for key exchange
            - SHA-256 for password hashing
            """)
        
        with col2:
            st.info("""
            **Security Features:**
            - All transactions encrypted
            - Secure key exchange protocol
            - Transaction integrity verification
            - Secure session management
            """)
        
        # Logout
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.account_number = None
            st.session_state.username = None
            st.rerun()

# ==================== MAIN APP ====================
def main():
    if st.session_state.logged_in:
        dashboard()
    else:
        login_page()

if __name__ == "__main__":
    main()

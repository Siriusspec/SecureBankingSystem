import streamlit as st
import pandas as pd
from database import BankingDatabase
from banking_system import BankingSystem
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Secure Banking System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main { padding: 2rem; }

    /* Gradient header */
    .header {
        background: linear-gradient(90deg, #1f77b4, #28a745);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    .subheader {
        color: #444;
        font-size: 1.1rem;
        font-style: italic;
        margin-bottom: 2rem;
    }

    /* Card-style boxes */
    .card {
        background: #ffffff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        padding: 1.25rem;
        border-radius: 12px;
        margin: 0.5rem 0 1rem 0;
        transition: transform 0.2s ease;
        text-align: center;
        font-weight: 600;
        border: 1px solid #f2f2f2;
    }
    .card b { display:block; color:#222; margin-bottom: 0.35rem; }
    .card:hover { transform: scale(1.02); }

    /* Buttons */
    div.stButton > button {
        background: linear-gradient(90deg, #1f77b4, #28a745);
        color: white;
        border-radius: 8px;
        font-weight: 700;
        transition: 0.2s ease-in-out;
        border: none;
        padding: 0.6rem 0.85rem;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #28a745, #1f77b4);
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(31, 119, 180, 0.25);
    }

    /* Animated alerts */
    .success-box {
        background: #d4edda;
        padding: 1rem;
        border-radius: 10px;
        border-left: 6px solid #28a745;
        animation: fadeIn 0.6s ease;
        margin: 1rem 0;
    }
    .error-box {
        background: #f8d7da;
        padding: 1rem;
        border-radius: 10px;
        border-left: 6px solid #dc3545;
        animation: shake 0.4s;
        margin: 1rem 0;
    }
    .info-box {
        background: #d1ecf1;
        padding: 1rem;
        border-radius: 10px;
        border-left: 6px solid #17a2b8;
        margin: 1rem 0;
    }
    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(4px);}
        to {opacity: 1; transform: translateY(0);}
    }
    @keyframes shake {
        0% { transform: translateX(0); }
        25% { transform: translateX(-4px); }
        50% { transform: translateX(4px); }
        75% { transform: translateX(-4px); }
        100% { transform: translateX(0); }
    }

    /* Badges for transaction types */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 700;
    }
    .badge-deposit { background: #e6f4ea; color: #1e7e34; border: 1px solid #c7e9d1; }
    .badge-withdrawal { background: #fbeaea; color: #a71d2a; border: 1px solid #f4c7cc; }
    .badge-transfer-in { background: #e7f1fb; color: #0b5ed7; border: 1px solid #c6ddfb; }
    .badge-transfer-out { background: #fff3cd; color: #8a6d3b; border: 1px solid #ffe8a1; }

    /* Table styling */
    table {
        border-collapse: collapse;
        width: 100%;
        font-size: 0.95rem;
    }
    th, td {
        padding: 0.6rem 0.8rem;
        border-bottom: 1px solid #eee;
        text-align: left;
        vertical-align: top;
    }
    th {
        background: #f7f9fc;
        font-weight: 700;
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
                    st.markdown('<div class="success-box">Login successful!</div>', unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.markdown('<div class="error-box">Invalid username or password</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-box">Please enter both username and password</div>', unsafe_allow_html=True)

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
                    st.markdown(
                        f'<div class="success-box"><strong>Account Created!</strong><br>Account Number: {account_number}</div>',
                        unsafe_allow_html=True
                    )
                    st.info("Please login with your credentials")
                else:
                    st.markdown(f'<div class="error-box">{message}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-box">Please fill all fields</div>', unsafe_allow_html=True)

# ==================== MAIN DASHBOARD ====================
def dashboard():
    st.markdown(f'<h1 class="header">Dashboard - {st.session_state.username}</h1>', unsafe_allow_html=True)

    account_info = db.get_account_info(st.session_state.account_number)

    if account_info:
        # Summary cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"<div class='card'><b>Account Number</b>{st.session_state.account_number}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='card'><b>Name</b>{account_info['full_name']}</div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='card'><b>Balance</b>₹{account_info['balance']:.2f}</div>", unsafe_allow_html=True)
        with col4:
            joined = account_info['created_at'][:10] if isinstance(account_info['created_at'], str) else str(account_info['created_at'])[:10]
            st.markdown(f"<div class='card'><b>Member Since</b>{joined}</div>", unsafe_allow_html=True)

        st.markdown("---")

        tab_deposit, tab_withdraw, tab_transfer, tab_history = st.tabs([
            "Deposit", "Withdraw", "Transfer", "Transaction History"
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
                    st.markdown(
                        f'<div class="success-box">{message}<br>New Balance: ₹{new_balance:.2f}</div>',
                        unsafe_allow_html=True
                    )
                    st.info("Transaction encrypted and stored securely")
                    st.rerun()
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
                    st.markdown(
                        f'<div class="success-box">{message}<br>New Balance: ₹{new_balance:.2f}</div>',
                        unsafe_allow_html=True
                    )
                    st.info("Transaction encrypted and stored securely")
                    st.rerun()
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
                        updated_info = db.get_account_info(st.session_state.account_number)
                        new_balance = updated_info['balance'] if updated_info else 0
                        st.markdown(
                            f'<div class="success-box">{message}<br>New Balance: ₹{new_balance:.2f}</div>',
                            unsafe_allow_html=True
                        )
                        st.info("Transfer encrypted and logged securely")
                        st.rerun()
                    else:
                        st.markdown(f'<div class="error-box">{message}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="info-box">Please enter recipient account number</div>', unsafe_allow_html=True)

        # Transaction history tab
        with tab_history:
            st.subheader("Transaction History")
            transactions = db.get_transaction_history(st.session_state.account_number, limit=50)

            if transactions:
                df = pd.DataFrame(transactions)

                # Build type badges using your schema
                def type_badge(t):
                    t_upper = str(t).upper()
                    if t_upper == "DEPOSIT":
                        return '<span class="badge badge-deposit">DEPOSIT</span>'
                    elif t_upper == "WITHDRAWAL":
                        return '<span class="badge badge-withdrawal">WITHDRAWAL</span>'
                    elif t_upper == "TRANSFER_IN":
                        return '<span class="badge badge-transfer-in">TRANSFER IN</span>'
                    elif t_upper == "TRANSFER_OUT":
                        return '<span class="badge badge-transfer-out">TRANSFER OUT</span>'
                    else:
                        return f'<span class="badge">{t_upper}</span>'

                # Type
                type_col = 'type' if 'type' in df.columns else ('transaction_type' if 'transaction_type' in df.columns else None)
                if type_col:
                    df['Type'] = df[type_col].apply(type_badge)

                # Amount
                amt_col = 'amount' if 'amount' in df.columns else None
                if amt_col:
                    df['Amount'] = df[amt_col].apply(lambda x: f"₹{float(x):.2f}")

                # Timestamp
                ts_col = 'timestamp' if 'timestamp' in df.columns else None
                if ts_col:
                    def fmt_ts(x):
                        s = str(x)
                        # Keep date + time up to seconds
                        return s[:19]
                    df['Date/Time'] = df[ts_col].apply(fmt_ts)

                # Description
                desc_col = 'description' if 'description' in df.columns else None
                if desc_col:
                    df['Description'] = df[desc_col].fillna("")

                # Order columns
                display_cols = [c for c in ['Type', 'Amount', 'Description', 'Date/Time'] if c in df.columns]
                html = df[display_cols].to_html(escape=False, index=False)
                st.write(html, unsafe_allow_html=True)
            else:
                st.info("No transactions yet")

        st.markdown("---")

        # Security info (collapsible)
        with st.expander("Security information"):
            st.markdown("""
            - **Encryption in Use:** DES for transaction data, RSA 2048-bit for key exchange, SHA-256 for password hashing
            - **Security Features:** All transactions encrypted, secure key exchange protocol, transaction integrity verification, secure session management
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

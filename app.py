import json
import random
import re
import string
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------
# Educational banking demo - stores data in data.json
# Not suitable for real banking or sensitive personal data.
# ---------------------------------------------------------

st.set_page_config(
    page_title="Atom Bank | Student Project",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATABASE = Path("data.json")
MAX_TRANSACTION = 10_000


def load_accounts():
    """Load account records from JSON. Start with an empty list if missing."""
    if not DATABASE.exists():
        return []
    try:
        content = DATABASE.read_text(encoding="utf-8").strip()
        if not content:
            return []
        data = json.loads(content)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        st.error("The data.json file could not be read. Check that it contains valid JSON.")
        return []


def save_accounts(accounts):
    """Save records using a temporary file to reduce the chance of partial writes."""
    temporary_file = DATABASE.with_suffix(".tmp")
    temporary_file.write_text(
        json.dumps(accounts, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    temporary_file.replace(DATABASE)


def generate_account_number(accounts):
    while True:
        letters = "".join(random.choices(string.ascii_uppercase, k=3))
        digits = "".join(random.choices(string.digits, k=6))
        account_number = f"NX-{letters}{digits}"
        if not any(a.get("accountNo.") == account_number for a in accounts):
            return account_number


def find_account(accounts, account_number):
    return next(
        (a for a in accounts if a.get("accountNo.") == account_number),
        None,
    )


def valid_email(email):
    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()) is not None


def money(amount):
    return f"₹{amount:,.2f}"


def clear_login():
    st.session_state.pop("logged_in_account", None)


def page_header(title, subtitle):
    st.markdown(f"<div class='eyebrow'>ATOM BANK · STUDENT DEMO</div>", unsafe_allow_html=True)
    st.title(title)
    st.caption(subtitle)


# ---------------------------- Theme + Styling ----------------------------
# The theme selector is shown at the top of the sidebar.
theme_mode = st.sidebar.radio(
    "Appearance",
    ["Light mode", "Dark mode"],
    horizontal=True,
    key="atom_bank_theme",
    label_visibility="visible",
)
DARK_MODE = theme_mode == "Dark mode"

if DARK_MODE:
    page_bg = "#0b1020"
    surface = "#151d31"
    text_color = "#f2f5ff"
    muted = "#b4bfd8"
    border_color = "#2b3650"
    sidebar_bg = "#070b16"
    input_bg = "#10182a"
    metric_label = "#bdc8e0"
    hero_bg = "linear-gradient(120deg,#111b35,#263ca8)"
else:
    page_bg = "#f5f7fb"
    surface = "#ffffff"
    text_color = "#15213b"
    muted = "#68738d"
    border_color = "#e2e7f1"
    sidebar_bg = "#111b32"
    input_bg = "#ffffff"
    metric_label = "#68738d"
    hero_bg = "linear-gradient(120deg,#17264a,#354fc7)"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
    :root {{ color-scheme: {'dark' if DARK_MODE else 'light'}; }}
    html, body, [class*="css"], [data-testid="stAppViewContainer"] {{ font-family: 'DM Sans', sans-serif; }}
    .stApp, [data-testid="stAppViewContainer"] {{ background: {page_bg}; color: {text_color}; }}
    [data-testid="stHeader"] {{ background: {page_bg}; }}
    [data-testid="stSidebar"] {{ background: {sidebar_bg}; }}
    [data-testid="stSidebar"] * {{ color: #f4f6fc; }}
    .eyebrow {{ color: {'#aab8ff' if DARK_MODE else '#5364a0'}; font-size: .72rem; letter-spacing: .16em; font-weight: 800; margin-bottom: .3rem; }}
    h1, h2, h3, h4, h5, h6, [data-testid="stHeading"] {{ font-family: 'Manrope', sans-serif !important; color: {text_color} !important; letter-spacing: -.025em; }}
    p, li, label, .stMarkdown, [data-testid="stCaptionContainer"] {{ color: {text_color}; }}
    [data-testid="stCaptionContainer"] p, .small-note {{ color: {muted} !important; }}
    [data-testid="stMetric"] {{ background: {surface}; padding: 20px 22px; border: 1px solid {border_color}; border-radius: 16px; box-shadow: 0 5px 18px rgba(28,43,78,.08); }}
    [data-testid="stMetricLabel"] {{ color: {metric_label} !important; }}
    [data-testid="stMetricValue"], [data-testid="stMetricDelta"] {{ color: {text_color} !important; font-family: 'Manrope', sans-serif; }}
    div.stButton > button, div.stFormSubmitButton > button {{ border-radius: 10px; min-height: 2.7rem; font-weight: 700; border: 1px solid {border_color}; background: {surface}; color: {text_color}; }}
    div.stButton > button[kind="primary"], div.stFormSubmitButton > button[kind="primary"] {{ background: #465de5; border-color: #465de5; color: white !important; }}
    div[data-testid="stForm"] {{ background: {surface}; border: 1px solid {border_color}; border-radius: 16px; padding: 22px; }}
    input, textarea, [data-baseweb="select"] > div {{ background: {input_bg} !important; color: {text_color} !important; border-color: {border_color} !important; }}
    input::placeholder, textarea::placeholder {{ color: {muted} !important; }}
    [data-testid="stAlert"] {{ color: {text_color}; }}
    .hero {{ background: {hero_bg}; border-radius: 20px; padding: 28px; color: white; margin: 10px 0 22px; }}
    .hero h2 {{ color: #ffffff !important; margin: 0 0 6px; }}
    .hero p {{ color: #e2e8ff !important; margin: 0; }}
    .small-note {{ font-size: .85rem; }}
    </style>
    """,
    unsafe_allow_html=True,
)

accounts = load_accounts()

# ---------------------------- Sidebar ----------------------------
with st.sidebar:
    st.markdown("## 🏦 Atom Bank")
    st.caption("Simple banking, clearly presented.")
    st.divider()

    logged_in = st.session_state.get("logged_in_account")
    current_account = find_account(accounts, logged_in) if logged_in else None

    if current_account:
        st.success(f"Signed in as {current_account.get('name', 'Customer')}")
        st.caption(f"Account: {current_account.get('accountNo.', '')}")
        menu_options = [
            "Dashboard", "Deposit money", "Withdraw money",
            "Account details", "Update account", "Delete account",
        ]
        page = st.radio("YOUR BANK", menu_options, label_visibility="collapsed")
        st.divider()
        if st.button("Sign out", use_container_width=True):
            clear_login()
            st.rerun()
    else:
        page = st.radio(
            "GET STARTED",
            ["Welcome", "Create account", "Sign in"],
            label_visibility="collapsed",
            key="public_nav",
        )
        st.divider()
        st.markdown("**Your money, your view.**")
        st.caption("A beginner-friendly Python + Streamlit project.")
        st.caption("⚠️ Demo only — not a real bank.")

# ---------------------------- Public pages ----------------------------
if not current_account and page == "Welcome":
    page_header("Banking made simple.", "A small banking application built with Python and Streamlit.")
    st.markdown(
        """
        <div class="hero">
          <h2>Your money. One clear dashboard.</h2>
          <p>Create a demo account, make deposits and withdrawals, and manage your details in one place.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Account setup", "Simple")
        st.caption("Create a demo account in a few steps.")
    with col2:
        st.metric("Transactions", "₹10,000 max")
        st.caption("Per deposit or withdrawal.")
    with col3:
        st.metric("Storage", "JSON file")
        st.caption("Your demo records are saved locally.")
    st.subheader("Create your account")
    st.write("Start with a demo account, or sign in if you already created one.")
    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("Create your account", type="primary", use_container_width=True):
            st.session_state["public_nav"] = "Create account"
            st.rerun()
    with action_col2:
        if st.button("I already have an account", use_container_width=True):
            st.session_state["public_nav"] = "Sign in"
            st.rerun()
    st.caption("Student project only — do not enter real banking details or passwords.")

elif not current_account and page == "Create account":
    page_header("Create your account", "Fill in your details to open a demo account.")
    with st.form("create_account_form"):
        name = st.text_input("Full name", placeholder="e.g. Aanya Sharma")
        age = st.number_input("Age", min_value=1, max_value=120, value=18, step=1)
        email = st.text_input("Email address", placeholder="you@example.com")
        pin = st.text_input("Create a 4-digit PIN", type="password", max_chars=4)
        confirm_pin = st.text_input("Confirm PIN", type="password", max_chars=4)
        submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)

    if submitted:
        if not name.strip():
            st.error("Please enter your name.")
        elif age < 18:
            st.error("You must be at least 18 years old to create an account in this demo.")
        elif not valid_email(email):
            st.error("Please enter a valid email address.")
        elif not pin.isdigit() or len(pin) != 4:
            st.error("Your PIN must contain exactly four digits.")
        elif pin != confirm_pin:
            st.error("The PINs do not match.")
        else:
            account_number = generate_account_number(accounts)
            new_account = {
                "name": name.strip(),
                "age": int(age),
                "email": email.strip(),
                "pin": pin,
                "accountNo.": account_number,
                "balance": 0,
            }
            accounts.append(new_account)
            save_accounts(accounts)
            st.success("Your demo account was created successfully!")
            st.code(account_number, language=None)
            st.warning("Save your account number. This demo stores PINs in plain text; do not use real credentials.")

elif not current_account and page == "Sign in":
    page_header("Welcome back", "Sign in with your demo account number and PIN.")
    with st.form("login_form"):
        account_number = st.text_input("Account number", placeholder="NX-ABC123456")
        pin = st.text_input("4-digit PIN", type="password", max_chars=4)
        submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)

    if submitted:
        account = find_account(accounts, account_number.strip().upper())
        if account and account.get("pin") == pin:
            st.session_state["logged_in_account"] = account["accountNo."]
            st.rerun()
        else:
            st.error("Account number or PIN is incorrect.")

# ---------------------------- Authenticated pages ----------------------------
elif current_account:
    account_number = current_account.get("accountNo.", "")

    if page == "Dashboard":
        page_header(f"Good to see you, {current_account.get('name', 'there')}.", "Here is a quick overview of your demo account.")
        st.markdown(
            f"""
            <div class="hero">
              <p>AVAILABLE BALANCE</p>
              <h2 style="font-size:2.5rem;margin:8px 0;">{money(current_account.get('balance', 0))}</h2>
              <p>Account number · {account_number}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current balance", money(current_account.get("balance", 0)))
        with col2:
            st.metric("Account status", "Active")
        with col3:
            st.metric("Minimum age", "18+")
        st.subheader("Manage your account")
        st.write("Use the navigation menu on the left to deposit, withdraw, view or update your account details.")

    elif page == "Deposit money":
        page_header("Deposit money", "Add money to your demo account.")
        st.metric("Available balance", money(current_account.get("balance", 0)))
        with st.form("deposit_form"):
            amount = st.number_input("Deposit amount (₹)", min_value=1, max_value=MAX_TRANSACTION, value=500, step=100)
            submitted = st.form_submit_button("Confirm deposit", type="primary", use_container_width=True)
        if submitted:
            current_account["balance"] = current_account.get("balance", 0) + int(amount)
            save_accounts(accounts)
            st.success(f"{money(amount)} deposited successfully.")
            st.rerun()

    elif page == "Withdraw money":
        page_header("Withdraw money", "Withdraw from your available demo balance.")
        st.metric("Available balance", money(current_account.get("balance", 0)))
        with st.form("withdraw_form"):
            amount = st.number_input("Withdrawal amount (₹)", min_value=1, max_value=MAX_TRANSACTION, value=500, step=100)
            submitted = st.form_submit_button("Confirm withdrawal", type="primary", use_container_width=True)
        if submitted:
            if amount > current_account.get("balance", 0):
                st.error("Insufficient balance. Please enter a smaller amount.")
            else:
                current_account["balance"] = current_account.get("balance", 0) - int(amount)
                save_accounts(accounts)
                st.success(f"{money(amount)} withdrawn successfully.")
                st.rerun()

    elif page == "Account details":
        page_header("Account details", "Your account information, with your PIN kept hidden.")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Full name", value=current_account.get("name", ""), disabled=True)
            st.text_input("Email address", value=current_account.get("email", ""), disabled=True)
            st.text_input("Age", value=str(current_account.get("age", "")), disabled=True)
        with col2:
            st.text_input("Account number", value=account_number, disabled=True)
            st.text_input("PIN", value="••••", disabled=True)
            st.text_input("Available balance", value=money(current_account.get("balance", 0)), disabled=True)
        st.caption("Keep your account number private. This is a learning demo.")

    elif page == "Update account":
        page_header("Update your details", "Change your name, email, or PIN. Leave a field blank to keep it unchanged.")
        with st.form("update_form"):
            name = st.text_input("New name (optional)")
            email = st.text_input("New email (optional)")
            new_pin = st.text_input("New 4-digit PIN (optional)", type="password", max_chars=4)
            confirm_pin = st.text_input("Confirm new PIN", type="password", max_chars=4)
            submitted = st.form_submit_button("Save changes", type="primary", use_container_width=True)
        if submitted:
            if email.strip() and not valid_email(email):
                st.error("Please enter a valid email address.")
            elif new_pin and (not new_pin.isdigit() or len(new_pin) != 4):
                st.error("The new PIN must contain exactly four digits.")
            elif new_pin and new_pin != confirm_pin:
                st.error("The new PINs do not match.")
            else:
                if name.strip():
                    current_account["name"] = name.strip()
                if email.strip():
                    current_account["email"] = email.strip()
                if new_pin:
                    current_account["pin"] = new_pin
                save_accounts(accounts)
                st.success("Your account details have been updated.")
                st.rerun()

    elif page == "Delete account":
        page_header("Close your demo account", "This permanently removes the account from the local JSON file.")
        st.warning("This action cannot be undone.")
        st.write(f"Account to delete: **{account_number}**")
        with st.form("delete_form"):
            confirm = st.checkbox("I understand that this demo account will be permanently deleted.")
            pin = st.text_input("Enter your PIN to confirm", type="password", max_chars=4)
            submitted = st.form_submit_button("Delete account permanently", type="primary", use_container_width=True)
        if submitted:
            if not confirm:
                st.error("Please tick the confirmation box.")
            elif pin != current_account.get("pin"):
                st.error("Incorrect PIN.")
            else:
                accounts = [a for a in accounts if a.get("accountNo.") != account_number]
                save_accounts(accounts)
                clear_login()
                st.success("Your demo account has been deleted.")
                st.rerun()

# Footer
st.divider()
st.markdown(
    "<p class='small-note'>Atom Bank Student Project · Built with Python + Streamlit · Educational use only</p>",
    unsafe_allow_html=True,
)

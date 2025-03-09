import streamlit as st
import socket
import threading
import time
from datetime import datetime
import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Streamlit page configuration with dark theme
st.set_page_config(
    page_title=os.getenv('APP_TITLE', "Message Terminal"),
    page_icon=os.getenv('APP_ICON', "🖥️"),
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': 'Message Terminal System v1.0'
    }
)

# Custom CSS for hacker theme
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp {
        background-color: var(--bg-color);
        color: var(--primary-color);
    }
    
    .title-text {
        color: var(--primary-color);
        font-family: 'Courier New', monospace;
        text-shadow: 0 0 10px var(--primary-color);
        padding: 10px;
        background-color: var(--secondary-bg);
        border: 1px solid var(--primary-color);
        border-radius: 5px;
        margin-bottom: 10px;
    }
    
    .terminal-text {
        font-family: 'Courier New', monospace;
        color: var(--primary-color);
        background-color: var(--bg-color);
        padding: 5px 10px;
        border-left: 2px solid var(--primary-color);
        margin: 2px 0;
    }
    
    .status-text {
        color: var(--primary-color);
        font-family: 'Courier New', monospace;
        font-size: 0.8em;
        padding: 5px;
        margin-bottom: 10px;
        border-bottom: 1px solid var(--primary-color);
    }
    
    .stButton button {
        background-color: var(--bg-color) !important;
        color: var(--primary-color) !important;
        border: 1px solid var(--primary-color) !important;
        font-family: 'Courier New', monospace !important;
    }
    
    .stButton button:hover {
        background-color: var(--primary-color) !important;
        color: var(--bg-color) !important;
    }
    
    .stTextInput input {
        background-color: var(--secondary-bg) !important;
        color: var(--primary-color) !important;
        border: 1px solid var(--primary-color) !important;
        font-family: 'Courier New', monospace !important;
    }
    
    .messages-container {
        height: 65vh;
        overflow-y: auto;
        padding: 10px;
        background-color: var(--bg-color);
        border: 1px solid var(--primary-color);
        margin: 10px 0;
    }

    .stAlert {
        background-color: var(--secondary-bg) !important;
        color: var(--primary-color) !important;
        border: 1px solid var(--primary-color) !important;
    }

    .element-container:empty {
        display: none;
    }

    .stMarkdown:empty {
        display: none;
    }

    :root {
        --primary-color: """ + os.getenv('PRIMARY_COLOR', '#00ff00') + """;
        --bg-color: """ + os.getenv('BG_COLOR', '#0a0a0a') + """;
        --secondary-bg: """ + os.getenv('SECONDARY_BG', '#111111') + """;
    }
</style>
""", unsafe_allow_html=True)

# Global variables from environment
HOST = os.getenv('HOST', 'localhost')
PORT = int(os.getenv('PORT', 5001))
DB_FILE = os.getenv('DB_FILE', 'messages.db')

# State initialization
if 'messages_cache' not in st.session_state:
    st.session_state['messages_cache'] = []
if 'input_key' not in st.session_state:
    st.session_state['input_key'] = 0
if 'container_key' not in st.session_state:
    st.session_state['container_key'] = 0

# Display session ID
st.sidebar.text(f"Session ID: {st.session_state._session_id}")

def init_db():
    """Initialize the database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS mensagens
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                message TEXT,
                local INTEGER)''')
    conn.commit()
    conn.close()

def add_message(msg, is_local=True):
    """Add message to database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO mensagens (timestamp, message, local) VALUES (?, ?, ?)",
                (timestamp, msg, 1 if is_local else 0))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error adding message: {e}")

def load_messages():
    """Load messages from database"""
    try:
        if not os.path.exists(DB_FILE):
            return []
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT timestamp, message, local FROM mensagens ORDER BY id ASC")
        messages = []
        for ts, msg, local in c.fetchall():
            try:
                data = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    data = datetime.strptime(ts, "%d/%m/%Y, %H:%M:%S")
                except ValueError:
                    data = datetime.now()
            
            ts_formatted = data.strftime("%d/%m/%Y %H:%M:%S")
            prefix = "<<" if local else ">>"
            messages.append(f"[{ts_formatted}] {prefix} {msg}")
        conn.close()
        return messages
        
    except Exception as e:
        print(f"Error loading messages: {e}")
        return []

def clear_messages():
    """Clear all messages"""
    try:
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        init_db()
        st.session_state['messages_cache'] = []
        st.session_state['container_key'] += 1
        return True
    except Exception as e:
        print(f"Error clearing messages: {e}")
        return False

def receive_messages():
    """Thread to receive messages"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind((HOST, PORT))
        sock.listen(1)
        print(f"Server listening on {HOST}:{PORT}")
        
        while True:
            try:
                conn, addr = sock.accept()
                with conn:
                    data = conn.recv(1024)
                    if data:
                        msg = data.decode('utf-8')
                        if msg != "connection_test":
                            add_message(msg, False)
            except Exception as e:
                time.sleep(0.1)
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        sock.close()

# Initialization
if not os.path.exists(DB_FILE):
    init_db()

# Compact interface
st.markdown('<h1 class="title-text">_MESSAGE TERMINAL_</h1>', unsafe_allow_html=True)
st.markdown('<div class="status-text">[SYSTEM: ONLINE]</div>', unsafe_allow_html=True)

# Messages area with dynamic key
messages_container = st.empty()
with messages_container.container():
    messages = load_messages()
    if not messages:
        st.info("_Waiting for messages..._")
    else:
        with st.container():
            for msg in messages:
                st.markdown(f'<div class="terminal-text">{msg}</div>', unsafe_allow_html=True)

# Input area
col1, col2 = st.columns([4, 1])
with col1:
    key = f"msg_input_{st.session_state['input_key']}"
    message = st.text_input("Message", value="", key=key, label_visibility="collapsed")

with col2:
    sent = st.button("⚡ SEND ⚡") or (message and message != st.session_state.get('last_msg', ''))
    if sent and message.strip():
        add_message(message, True)
        st.session_state['last_msg'] = message
        st.session_state['input_key'] += 1
        time.sleep(0.1)
        st.rerun()

# Clear button
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("🗑️ Clear Messages"):
        if clear_messages():
            messages_container.empty()
            st.rerun()

# Receiver thread
if 'receiver_thread' not in st.session_state:
    receiver_thread = threading.Thread(target=receive_messages, daemon=True)
    receiver_thread.start()
    st.session_state['receiver_thread'] = receiver_thread

# Controlled update
time.sleep(1)
st.rerun() 
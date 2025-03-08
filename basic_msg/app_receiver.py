import streamlit as st
import socket
import threading
import time
from datetime import datetime
import sqlite3
import os
import uuid

# Configuração da página Streamlit com tema escuro
st.set_page_config(
    page_title="Terminal de Mensagens",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado para o tema hacker
st.markdown("""
<style>
    /* Tema escuro personalizado */
    .stApp {
        background-color: #0a0a0a;
        color: #00ff00;
    }
    
    /* Estilo para títulos */
    .title-text {
        color: #00ff00;
        font-family: 'Courier New', monospace;
        text-shadow: 0 0 10px #00ff00;
        padding: 20px;
        background-color: #111111;
        border: 1px solid #00ff00;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    
    /* Estilo para mensagens */
    .terminal-text {
        font-family: 'Courier New', monospace;
        color: #00ff00;
        background-color: #0a0a0a;
        padding: 5px 10px;
        border-left: 2px solid #00ff00;
        margin: 5px 0;
    }
    
    /* Estilo para o status */
    .status-text {
        color: #00ff00;
        font-family: 'Courier New', monospace;
        font-size: 0.8em;
        opacity: 0.8;
    }
    
    /* Estilo para botões */
    .stButton button {
        background-color: #0a0a0a !important;
        color: #00ff00 !important;
        border: 1px solid #00ff00 !important;
        font-family: 'Courier New', monospace !important;
        text-shadow: 0 0 5px #00ff00;
    }
    
    .stButton button:hover {
        background-color: #00ff00 !important;
        color: #0a0a0a !important;
        border: 1px solid #00ff00 !important;
    }
    
    /* Estilo para mensagens de info */
    .stInfo {
        background-color: #111111 !important;
        color: #00ff00 !important;
        border: 1px solid #00ff00 !important;
    }
    
    /* Estilo para mensagens de sucesso */
    .stSuccess {
        background-color: #111111 !important;
        color: #00ff00 !important;
        border: 1px solid #00ff00 !important;
    }

    /* Estilo para o campo de texto */
    .stTextInput input {
        background-color: #111111 !important;
        color: #00ff00 !important;
        border: 1px solid #00ff00 !important;
        font-family: 'Courier New', monospace !important;
        padding: 10px !important;
    }
    
    .stTextInput input:focus {
        box-shadow: 0 0 10px #00ff00 !important;
    }

    /* Container de mensagens com scroll */
    .messages-container {
        height: 60vh;
        overflow-y: auto;
        padding: 20px;
        background-color: #0a0a0a;
        border: 1px solid #00ff00;
        border-radius: 5px;
        margin-bottom: 20px;
    }

    /* Barra de rolagem personalizada */
    .messages-container::-webkit-scrollbar {
        width: 5px;
    }
    
    .messages-container::-webkit-scrollbar-track {
        background: #0a0a0a;
    }
    
    .messages-container::-webkit-scrollbar-thumb {
        background: #00ff00;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Título com estilo hacker
st.markdown('<h1 class="title-text">_TERMINAL DE MENSAGENS_</h1>', unsafe_allow_html=True)

# Variáveis globais
HOST = 'localhost'
PORT = 5001
DB_FILE = "mensagens.db"

# Inicialização dos estados
if 'session_uuid' not in st.session_state:
    st.session_state['session_uuid'] = str(uuid.uuid4())

def init_db():
    """Inicializa o banco de dados"""
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE mensagens
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                mensagem TEXT,
                local INTEGER)''')
    conn.commit()
    conn.close()

def adicionar_mensagem(msg, is_local=True):
    """Adiciona mensagem ao banco de dados"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        timestamp = datetime.now().strftime("%H:%M:%S")
        c.execute("INSERT INTO mensagens (timestamp, mensagem, local) VALUES (?, ?, ?)",
                (timestamp, msg, 1 if is_local else 0))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao adicionar mensagem: {e}")

def carregar_mensagens():
    """Carrega mensagens do banco de dados"""
    try:
        if not os.path.exists(DB_FILE):
            return []
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT timestamp, mensagem, local FROM mensagens ORDER BY id DESC")
        mensagens = []
        for ts, msg, local in c.fetchall():
            prefix = "<<" if local else ">>"
            mensagens.append(f"[{ts}] {prefix} {msg}")
        conn.close()
        return mensagens
    except Exception as e:
        print(f"Erro ao carregar mensagens: {e}")
        return []

def receber_mensagens():
    """Thread para receber mensagens"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind((HOST, PORT))
        sock.listen(1)
        print(f"Servidor escutando em {HOST}:{PORT}")
        
        while True:
            try:
                conn, addr = sock.accept()
                with conn:
                    data = conn.recv(1024)
                    if data:
                        msg = data.decode('utf-8')
                        if msg != "teste_conexao":
                            adicionar_mensagem(msg, False)
            except Exception as e:
                time.sleep(0.1)
    except Exception as e:
        print(f"Erro no servidor: {e}")
    finally:
        sock.close()

# Inicialização
if not os.path.exists(DB_FILE):
    init_db()

# Status do servidor com estilo hacker
st.markdown(
    f'<div class="status-text">[SISTEMA: ONLINE] - ID: {st.session_state["session_uuid"][:8]}</div>',
    unsafe_allow_html=True
)

# Container para mensagens com scroll
st.markdown('<div class="messages-container">', unsafe_allow_html=True)
mensagens = carregar_mensagens()
if not mensagens:
    st.info("_Aguardando mensagens..._")
else:
    for msg in mensagens:
        st.markdown(f'<div class="terminal-text">{msg}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Área de entrada de mensagem
col1, col2 = st.columns([4, 1])
with col1:
    mensagem = st.text_input("", placeholder="Digite sua mensagem...", label_visibility="collapsed")
with col2:
    if st.button("⚡ ENVIAR ⚡") or mensagem:
        if mensagem.strip():
            adicionar_mensagem(mensagem, True)
            st.rerun()

# Botão de limpar com estilo hacker
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("🔥 LIMPAR TERMINAL 🔥"):
        init_db()
        st.success("_Terminal reinicializado com sucesso_")
        st.session_state['session_uuid'] = str(uuid.uuid4())
        st.rerun()

# Iniciar thread de recebimento
if 'receiver_thread' not in st.session_state:
    receiver_thread = threading.Thread(target=receber_mensagens, daemon=True)
    receiver_thread.start()
    st.session_state['receiver_thread'] = receiver_thread

# Atualização automática mais suave
time.sleep(0.5)
st.rerun() 
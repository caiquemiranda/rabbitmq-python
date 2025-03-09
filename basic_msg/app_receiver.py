import streamlit as st
import socket
import threading
import time
from datetime import datetime
import sqlite3
import os

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
    .stApp {
        background-color: #0a0a0a;
        color: #00ff00;
    }
    
    .title-text {
        color: #00ff00;
        font-family: 'Courier New', monospace;
        text-shadow: 0 0 10px #00ff00;
        padding: 10px;
        background-color: #111111;
        border: 1px solid #00ff00;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    
    .terminal-text {
        font-family: 'Courier New', monospace;
        color: #00ff00;
        background-color: #0a0a0a;
        padding: 5px 10px;
        border-left: 2px solid #00ff00;
        margin: 2px 0;
    }
    
    .status-text {
        color: #00ff00;
        font-family: 'Courier New', monospace;
        font-size: 0.8em;
        padding: 5px;
        margin-bottom: 10px;
        border-bottom: 1px solid #00ff00;
    }
    
    .stButton button {
        background-color: #0a0a0a !important;
        color: #00ff00 !important;
        border: 1px solid #00ff00 !important;
        font-family: 'Courier New', monospace !important;
    }
    
    .stButton button:hover {
        background-color: #00ff00 !important;
        color: #0a0a0a !important;
    }
    
    .stTextInput input {
        background-color: #111111 !important;
        color: #00ff00 !important;
        border: 1px solid #00ff00 !important;
        font-family: 'Courier New', monospace !important;
    }
    
    .messages-container {
        height: 65vh;
        overflow-y: auto;
        padding: 10px;
        background-color: #0a0a0a;
        border: 1px solid #00ff00;
        margin: 10px 0;
    }

    .stAlert {
        background-color: #111111 !important;
        color: #00ff00 !important;
        border: 1px solid #00ff00 !important;
    }

    div[data-testid="stToolbar"] {
        display: none;
    }

    div[data-testid="stDecoration"] {
        display: none;
    }

    div[data-testid="stStatusWidget"] {
        display: none;
    }

    footer {
        display: none;
    }

    .element-container:empty {
        display: none;
    }

    .stMarkdown:empty {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Variáveis globais
HOST = 'localhost'
PORT = 5001
DB_FILE = "mensagens.db"

# Inicialização do estado
if 'mensagens_cache' not in st.session_state:
    st.session_state['mensagens_cache'] = []
if 'input_key' not in st.session_state:
    st.session_state['input_key'] = 0
if 'container_key' not in st.session_state:
    st.session_state['container_key'] = 0

def init_db():
    """Inicializa o banco de dados"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS mensagens
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
        # Garante que o timestamp seja salvo no formato ISO
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
        # Ordenar por ID em ordem crescente para mostrar mensagens mais antigas primeiro
        c.execute("SELECT timestamp, mensagem, local FROM mensagens ORDER BY id ASC")
        mensagens = []
        for ts, msg, local in c.fetchall():
            try:
                # Tenta primeiro o formato ISO
                data = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    # Tenta o formato alternativo se o primeiro falhar
                    data = datetime.strptime(ts, "%d/%m/%Y, %H:%M:%S")
                except ValueError:
                    # Se ambos falharem, usa a data atual
                    data = datetime.now()
            
            # Formata a data para exibição no formato DD/MM/YYYY HH:MM:SS
            ts_formatado = data.strftime("%d/%m/%Y %H:%M:%S")
            prefix = "<<" if local else ">>"
            mensagens.append(f"[{ts_formatado}] {prefix} {msg}")
        conn.close()
        return mensagens
        
    except Exception as e:
        print(f"Erro ao carregar mensagens: {e}")
        return []

def limpar_mensagens():
    """Limpa todas as mensagens"""
    try:
        # Remove o arquivo do banco de dados
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        # Reinicializa o banco
        init_db()
        # Limpa o cache e incrementa a key do container
        st.session_state['mensagens_cache'] = []
        st.session_state['container_key'] += 1
        return True
    except Exception as e:
        print(f"Erro ao limpar mensagens: {e}")
        return False

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

# Interface compacta
st.markdown('<h1 class="title-text">_TERMINAL DE MENSAGENS_</h1>', unsafe_allow_html=True)
st.markdown('<div class="status-text">[SISTEMA: ONLINE]</div>', unsafe_allow_html=True)

# Área de mensagens com key dinâmica
mensagens_container = st.empty()
with mensagens_container.container():
    mensagens = carregar_mensagens()
    if not mensagens:
        st.info("_Aguardando mensagens..._")
    else:
        # Cria um container único para cada conjunto de mensagens
        with st.container():
            for msg in mensagens:
                st.markdown(f'<div class="terminal-text">{msg}</div>', unsafe_allow_html=True)

# Área de entrada
col1, col2 = st.columns([4, 1])
with col1:
    # Incrementa a key do input para forçar limpeza
    key = f"msg_input_{st.session_state['input_key']}"
    mensagem = st.text_input("Mensagem", value="", key=key, label_visibility="collapsed")

with col2:
    enviou = st.button("⚡ ENVIAR ⚡") or (mensagem and mensagem != st.session_state.get('last_msg', ''))
    if enviou and mensagem.strip():
        adicionar_mensagem(mensagem, True)
        st.session_state['last_msg'] = mensagem
        st.session_state['input_key'] += 1
        time.sleep(0.1)
        st.rerun()

# Botão limpar
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("🗑️ Limpar Mensagens"):
        if limpar_mensagens():
            mensagens_container.empty()
            st.rerun()

# Thread de recebimento
if 'receiver_thread' not in st.session_state:
    receiver_thread = threading.Thread(target=receber_mensagens, daemon=True)
    receiver_thread.start()
    st.session_state['receiver_thread'] = receiver_thread

# Atualização mais lenta e controlada
time.sleep(1)
st.rerun() 
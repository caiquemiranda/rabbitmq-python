import streamlit as st
import socket
import threading
import time
from datetime import datetime
import sqlite3
import os

# Força limpeza do cache do Streamlit
st.cache_data.clear()
st.cache_resource.clear()

# Configuração da página Streamlit
st.set_page_config(page_title="Receptor de Mensagens", page_icon="📨")

# Configuração do layout
st.title("📨 Receptor de Mensagens")

# Variáveis globais
HOST = 'localhost'
PORT = 5001
DB_FILE = "mensagens.db"

def limpar_todo_sistema():
    """Limpa todo o sistema de mensagens"""
    try:
        # 1. Limpa o banco de dados
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        
        # 2. Limpa o cache do Streamlit
        st.cache_data.clear()
        st.cache_resource.clear()
        
        # 3. Limpa todas as variáveis de sessão
        for key in list(st.session_state.keys()):
            if key != 'receiver_thread':  # Mantém apenas a thread do receptor
                del st.session_state[key]
        
        # 4. Reinicializa o banco de dados
        init_db()
        
        return True
    except Exception as e:
        print(f"Erro ao limpar sistema: {e}")
        return False

def init_db():
    """Inicializa o banco de dados"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS mensagens
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    mensagem TEXT)''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao inicializar DB: {e}")

def adicionar_mensagem_db(msg):
    """Adiciona mensagem ao banco de dados"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        timestamp = datetime.now().strftime("%H:%M:%S")
        c.execute("INSERT INTO mensagens (timestamp, mensagem) VALUES (?, ?)",
                (timestamp, msg))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao adicionar mensagem: {e}")

@st.cache_data(ttl=0.1)  # Cache com tempo de vida muito curto
def carregar_mensagens_db():
    """Carrega mensagens do banco de dados"""
    try:
        if not os.path.exists(DB_FILE):
            return []
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT timestamp, mensagem FROM mensagens ORDER BY id DESC")
        mensagens = [f"[{ts}] {msg}" for ts, msg in c.fetchall()]
        conn.close()
        return mensagens
    except Exception as e:
        print(f"Erro ao carregar mensagens: {e}")
        return []

# Inicialização do sistema
if not os.path.exists(DB_FILE):
    init_db()

# Inicialização do estado
if 'status' not in st.session_state:
    st.session_state['status'] = "🟢 Servidor ativo"

def adicionar_mensagem(msg):
    """Adiciona mensagem ao sistema"""
    if msg != "teste_conexao":  # Ignora mensagens de teste de conexão
        adicionar_mensagem_db(msg)
        print(f"Mensagem salva: {msg}")

def receber_mensagens():
    """Função que roda em thread separada para receber mensagens"""
    print("Iniciando servidor de socket...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind((HOST, PORT))
        sock.listen(1)
        print(f"Servidor escutando em {HOST}:{PORT}")
        
        while True:
            try:
                conn, addr = sock.accept()
                print(f"Conexão recebida de {addr}")
                with conn:
                    data = conn.recv(1024)
                    if data:
                        mensagem = data.decode('utf-8')
                        print(f"Mensagem recebida: {mensagem}")
                        adicionar_mensagem(mensagem)
            except Exception as e:
                print(f"Erro na conexão: {e}")
                time.sleep(0.1)
    except Exception as e:
        print(f"Erro fatal no servidor: {e}")
        st.session_state['status'] = f"🔴 Erro no servidor: {str(e)}"
    finally:
        sock.close()

# Status do servidor
st.write(st.session_state.get('status', ""))

# Container para mensagens com scroll
with st.container():
    # Carregar e exibir mensagens do banco de dados
    mensagens = carregar_mensagens_db()
    if not mensagens:
        st.info("Aguardando mensagens... (Servidor na porta 5001)")
    else:
        for msg in mensagens:
            st.text(msg)

# Botões de controle em colunas
col1, col2 = st.columns(2)
with col1:
    if st.button("🗑️ Limpar Mensagens"):
        if limpar_todo_sistema():
            st.cache_data.clear()  # Limpa o cache novamente
            st.success("Sistema completamente limpo!")
            time.sleep(0.1)
            st.rerun()
with col2:
    if st.button("🔄 Atualizar"):
        st.cache_data.clear()  # Limpa o cache antes de atualizar
        st.rerun()

# Iniciar thread de recebimento
if 'receiver_thread' not in st.session_state:
    receiver_thread = threading.Thread(target=receber_mensagens, daemon=True)
    receiver_thread.start()
    st.session_state['receiver_thread'] = receiver_thread

# Atualização automática com limpeza de cache
st.cache_data.clear()
time.sleep(0.1)
st.rerun() 
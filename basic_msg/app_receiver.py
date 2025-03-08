import streamlit as st
import socket
import threading
import time
from datetime import datetime
import sqlite3
import os
import uuid

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

# Gera um ID único para a sessão se não existir
if 'session_uuid' not in st.session_state:
    st.session_state['session_uuid'] = str(uuid.uuid4())

# Parâmetros de URL para controle de estado
if "clear" in st.query_params:
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        init_db()
    st.query_params.clear()

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
        print(f"Mensagem salva no DB: [{timestamp}] {msg}")
    except Exception as e:
        print(f"Erro ao adicionar mensagem: {e}")

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

def limpar_mensagens():
    """Limpa todas as mensagens"""
    try:
        # Remove o arquivo do banco de dados
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        
        # Reinicializa o banco
        init_db()
        
        # Gera novo UUID para forçar recarregamento
        st.session_state['session_uuid'] = str(uuid.uuid4())
        
        print("Sistema de mensagens limpo")
        return True
    except Exception as e:
        print(f"Erro ao limpar mensagens: {e}")
        return False

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
                        if mensagem != "teste_conexao":  # Ignora mensagens de teste
                            print(f"Mensagem recebida: {mensagem}")
                            adicionar_mensagem_db(mensagem)
            except Exception as e:
                print(f"Erro na conexão: {e}")
                time.sleep(0.1)
    except Exception as e:
        print(f"Erro fatal no servidor: {e}")
    finally:
        sock.close()

# Inicialização do sistema
if not os.path.exists(DB_FILE):
    init_db()

# Status do servidor
st.write("🟢 Servidor ativo")
st.caption(f"ID da Sessão: {st.session_state['session_uuid'][:8]}")

# Container para mensagens com scroll
with st.container():
    # Carregar e exibir mensagens do banco de dados
    mensagens = carregar_mensagens_db()
    if not mensagens:
        st.info("Aguardando mensagens... (Servidor na porta 5001)")
    else:
        for msg in mensagens:
            st.text(msg)

# Componente HTML para recarregamento
reload_html = f'''
    <meta id="session-id" data-session-id="{st.session_state['session_uuid']}">
    <script>
        window.addEventListener('load', function() {{
            const urlParams = new URLSearchParams(window.location.search);
            const currentSession = document.getElementById('session-id').dataset.sessionId;
            const urlSession = urlParams.get('session');
            
            if (urlSession && urlSession !== currentSession) {{
                window.location.reload();
            }}
        }});
    </script>
'''
st.components.v1.html(reload_html, height=0)

# Botões de controle em colunas
col1, col2 = st.columns(2)
with col1:
    if st.button("🗑️ Limpar Mensagens"):
        if limpar_mensagens():
            st.success("Sistema limpo com sucesso!")
            # Adiciona novo ID de sessão na URL
            st.query_params["session"] = st.session_state['session_uuid']
            st.rerun()
with col2:
    if st.button("🔄 Atualizar"):
        st.cache_data.clear()
        st.rerun()

# Iniciar thread de recebimento
if 'receiver_thread' not in st.session_state:
    receiver_thread = threading.Thread(target=receber_mensagens, daemon=True)
    receiver_thread.start()
    st.session_state['receiver_thread'] = receiver_thread

# Atualização automática mais suave
time.sleep(0.5)
st.rerun() 
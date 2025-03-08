import streamlit as st
import socket
import threading
import time
from datetime import datetime
from collections import deque
from threading import Lock

# Configuração da página Streamlit
st.set_page_config(page_title="Receptor de Mensagens", page_icon="📨")

# Configuração do layout
st.title("📨 Receptor de Mensagens")

# Variáveis globais
HOST = 'localhost'
PORT = 5001
mensagens_pendentes = deque()
lock = Lock()

# Inicialização do estado
if 'mensagens' not in st.session_state:
    st.session_state['mensagens'] = []
if 'status' not in st.session_state:
    st.session_state['status'] = "🟢 Servidor ativo"

def adicionar_mensagem(msg):
    """Adiciona mensagem à fila global"""
    if msg != "teste_conexao":  # Ignora mensagens de teste de conexão
        timestamp = datetime.now().strftime("%H:%M:%S")
        with lock:
            mensagens_pendentes.append(f"[{timestamp}] {msg}")

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

# Processar mensagens pendentes
with lock:
    while mensagens_pendentes:
        msg = mensagens_pendentes.popleft()
        if msg not in st.session_state['mensagens']:
            st.session_state['mensagens'].append(msg)

# Container para mensagens com scroll
with st.container():
    # Área de mensagens
    if len(st.session_state['mensagens']) == 0:
        st.info("Aguardando mensagens... (Servidor na porta 5001)")
    else:
        for msg in reversed(st.session_state['mensagens']):
            st.text(msg)

# Botões de controle em colunas
col1, col2 = st.columns(2)
with col1:
    if st.button("🗑️ Limpar Mensagens"):
        st.session_state['mensagens'] = []
        with lock:
            mensagens_pendentes.clear()
        st.rerun()
with col2:
    if st.button("🔄 Atualizar"):
        st.rerun()

# Iniciar thread de recebimento
if 'receiver_thread' not in st.session_state:
    receiver_thread = threading.Thread(target=receber_mensagens, daemon=True)
    receiver_thread.start()
    st.session_state['receiver_thread'] = receiver_thread

# Atualização automática mais frequente
time.sleep(0.1)  # Reduzindo o tempo de atualização
st.rerun() 
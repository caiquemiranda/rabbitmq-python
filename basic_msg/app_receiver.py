import streamlit as st
import socket
import threading
import time
from datetime import datetime

# Configuração da página Streamlit
st.set_page_config(page_title="Receptor de Mensagens", page_icon="📨")

# Configuração do layout
st.title("📨 Receptor de Mensagens")
st.write("Sistema ativo e aguardando mensagens...")

# Inicialização do estado
if 'mensagens' not in st.session_state:
    st.session_state['mensagens'] = []

if 'socket_initialized' not in st.session_state:
    st.session_state['socket_initialized'] = False

def adicionar_mensagem(msg):
    """Função para adicionar mensagem com timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state['mensagens'].append(f"[{timestamp}] {msg}")

def receber_mensagens():
    HOST = 'localhost'
    PORT = 5000
    
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((HOST, PORT))
                s.listen()
                
                while True:
                    conn, addr = s.accept()
                    with conn:
                        data = conn.recv(1024)
                        if data:
                            mensagem = data.decode()
                            adicionar_mensagem(mensagem)
        except Exception as e:
            print(f"Erro no socket: {e}")
            time.sleep(1)

# Container para mensagens com scroll
mensagens_container = st.container()

# Área de mensagens
with mensagens_container:
    if len(st.session_state['mensagens']) == 0:
        st.info("Nenhuma mensagem recebida ainda...")
    else:
        for msg in reversed(st.session_state['mensagens']):
            st.text(msg)

# Botões de controle
col1, col2 = st.columns(2)
with col1:
    if st.button("🗑️ Limpar Mensagens"):
        st.session_state['mensagens'] = []
        st.experimental_rerun()
with col2:
    if st.button("🔄 Atualizar"):
        st.experimental_rerun()

# Iniciar thread de recebimento apenas uma vez
if not st.session_state.get('socket_initialized', False):
    receiver_thread = threading.Thread(target=receber_mensagens, daemon=True)
    receiver_thread.start()
    st.session_state['socket_initialized'] = True

# Configurar auto-atualização
if len(st.session_state['mensagens']) > 0:
    time.sleep(0.5)
    st.rerun() 
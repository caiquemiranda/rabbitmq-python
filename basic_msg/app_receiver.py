import streamlit as st
import socket
import threading
import time

# Configuração da página Streamlit
st.title("Receptor de Mensagens")
st.write("Aguardando mensagens...")

# Inicialização correta do estado da sessão
if 'mensagens' not in st.session_state:
    st.session_state['mensagens'] = []

if 'socket_initialized' not in st.session_state:
    st.session_state['socket_initialized'] = False

def receber_mensagens():
    HOST = 'localhost'
    PORT = 5000
    
    # Criar socket servidor
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Permitir reutilização do endereço/porta
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen()
            
            while True:
                try:
                    # Aceitar conexão
                    conn, addr = s.accept()
                    with conn:
                        # Receber dados
                        data = conn.recv(1024)
                        if data:
                            mensagem = data.decode()
                            if 'mensagens' in st.session_state:
                                st.session_state['mensagens'].append(mensagem)
                except Exception as e:
                    print(f"Erro na conexão: {e}")
                    time.sleep(0.1)
    except Exception as e:
        print(f"Erro ao inicializar socket: {e}")

# Iniciar thread para receber mensagens apenas uma vez
if not st.session_state.get('socket_initialized', False):
    receiver_thread = threading.Thread(target=receber_mensagens, daemon=True)
    receiver_thread.start()
    st.session_state['socket_initialized'] = True

# Exibir mensagens
for msg in st.session_state['mensagens']:
    st.text(f"Mensagem recebida: {msg}")

# Botão para limpar mensagens
if st.button("Limpar Mensagens"):
    st.session_state['mensagens'] = []

# Atualizar a página a cada 1 segundo
time.sleep(1)
st.rerun() 
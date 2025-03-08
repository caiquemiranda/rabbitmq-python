import streamlit as st
import socket
import threading
import time

# Configuração da página Streamlit
st.title("Receptor de Mensagens")
st.write("Aguardando mensagens...")

# Variável global para armazenar mensagens
if 'mensagens' not in st.session_state:
    st.session_state.mensagens = []

def receber_mensagens():
    HOST = 'localhost'
    PORT = 5000
    
    # Criar socket servidor
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        
        while True:
            # Aceitar conexão
            conn, addr = s.accept()
            with conn:
                # Receber dados
                data = conn.recv(1024)
                if data:
                    mensagem = data.decode()
                    st.session_state.mensagens.append(mensagem)

# Iniciar thread para receber mensagens
if 'receiver_thread' not in st.session_state:
    receiver_thread = threading.Thread(target=receber_mensagens, daemon=True)
    receiver_thread.start()
    st.session_state.receiver_thread = receiver_thread

# Exibir mensagens
for msg in st.session_state.mensagens:
    st.text(f"Mensagem recebida: {msg}")

# Botão para limpar mensagens
if st.button("Limpar Mensagens"):
    st.session_state.mensagens = []

# Atualizar a página automaticamente
time.sleep(1)
st.experimental_rerun() 